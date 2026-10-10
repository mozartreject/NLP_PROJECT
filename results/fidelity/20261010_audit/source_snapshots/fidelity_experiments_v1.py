"""Predeclared fidelity audit, historical executions and four-dataset interventions.
Run prepare_fidelity_sources.py first. Every experiment retains predictions locally.
"""
import argparse,csv,hashlib,importlib.metadata,json,logging,math,os,sys,time,zipfile
from collections import Counter,defaultdict
from dataclasses import asdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import spacy,yake,pke
from scipy.stats import ttest_rel
from full_comparison import ROOT,DATASETS,normalize,score,load_dataset,load_model
from replication.core import Config,extract as original_extract
from replication.fidelity_core import Policy,extract
from replication.historical import load_yake,load_rake,CACHE

SOURCE_FILES=['fidelity_experiments.py','replication/fidelity_core.py','replication/core.py','replication/historical/__init__.py','prepare_fidelity_sources.py','full_comparison.py','configs/fidelity_sources.json']
CORE_POLICIES={
 'Independent-baseline':{},
 **{'without-'+feature:{'omit':feature} for feature in ['WCase','WPosition','WFreq','WRel','WSpread']},
 'Tokenizer-segtok':{'policy':{'tokenizer':'segtok'}},
 'Tokenizer-special-chars':{'policy':{'tokenizer':'special_chars'}},
 'Author-stopwords':{'stoplist':'author'},
 'Casing-natural-log':{'policy':{'casing_log':'natural'}},
 'Position-natural-log':{'policy':{'position_log':'natural'}},
 'Frequency-nonstopwords':{'policy':{'frequency_population':'nonstop'}},
 'Relatedness-without-PLPR':{'policy':{'relatedness_plpr':False}},
 'Position-unique-sentences':{'policy':{'position_unique':True}},
 'Singleton-casing-log1p':{'policy':{'casing_singleton':'log1p'}},
 'Neighbor-window-2':{'window':2},
 'Casing-one-plus-ln':{'policy':{'casing_add_one':True}},
 'Internal-stopword-transition':{'policy':{'phrase_internal_transition':True}},
 'Plural-stripping':{'policy':{'strip_plural':True}}}

def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_rows(name,limit=0):
 if name!='SemEval2010':return load_dataset(name,limit)
 path=ROOT/'data/SemEval2010-recovered244.zip'
 with zipfile.ZipFile(path) as z:
  docs=sorted(n for n in z.namelist() if '/docsutf8/' in n and n.endswith('.txt'));assert len(docs)==244
  rows=[]
  for n in docs:
   gold={normalize(g) for g in z.read(n.replace('/docsutf8/','/keys/')[:-4]+'.key').decode('utf-8-sig').splitlines() if g.strip()}
   if not gold:
    assert Path(n).stem=='C-86','Unexpected empty gold';continue
   rows.append((Path(n).stem,z.read(n).decode('utf-8-sig'),gold))
 return rows[:limit] if limit else rows,sha(path),'en'
def holm(pvalues):
 order=np.argsort(pvalues);result=np.zeros(len(pvalues));running=0.
 for rank,index in enumerate(order):
  running=max(running,(len(order)-rank)*pvalues[index]);result[index]=min(1.,running)
 return result.tolist()
def bootstrap(diff,seed=42):
 rng=np.random.default_rng(seed);means=[]
 for _ in range(20):means.extend(diff[rng.integers(0,len(diff),size=(100,len(diff)))].mean(axis=1))
 return np.quantile(means,[.025,.975]).tolist()
def finalize(run,manifest):
 items=[json.loads(s) for s in (run/'predictions.jsonl').read_text().splitlines()];records=[i['metrics'] for i in items]
 assert len({(r['dataset'],r['document_id'],r['method']) for r in records})==len(records)
 summaries={};stats=[]
 for name in manifest['datasets']:
  summaries[name]={};groups=defaultdict(list)
  for r in records:
   if r['dataset']==name:groups[r['method']].append(r)
  for method,group in groups.items():
   assert len(group)==manifest['datasets'][name]['documents'],(name,method,len(group))
   summaries[name][method]={k:float(np.mean([r[k] for r in group])) for k in ['precision','recall','f1','seconds','returned']}
  # Explicit paired IDs; one paired t-test per P/R/F1 and per configuration.
  if manifest['suite']=='core':base='Independent-baseline'
  elif manifest['suite']=='history':base='YAKE-current-window1'
  else:base=None
  pairs=[]
  if base:pairs=[(base,m) for m in groups if m!=base]
  else:
   for prefix in ['TextRank','SingleRank','TF-IDF']:
    pairs += [(prefix+'-common',prefix+'-native')]
   pairs += [('TF-IDF-common','TF-IDF-no-POS')]
  for base,method in pairs:
   b={r['document_id']:r for r in groups[base]};g={r['document_id']:r for r in groups[method]};assert set(b)==set(g)
   for metric in ['precision','recall','f1']:
    diff=np.array([g[i][metric]-b[i][metric] for i in sorted(b)])
    p=float(ttest_rel([g[i][metric] for i in sorted(b)],[b[i][metric] for i in sorted(b)]).pvalue) if np.any(diff) else 1.
    stats.append({'dataset':name,'baseline':base,'variant':method,'metric':metric,'contrast':'variant minus baseline','n':len(diff),'mean_difference':float(diff.mean()),'bootstrap_95':bootstrap(diff),'paired_t_p_two_sided':p,'bootstrap_seed':42,'bootstrap_resamples':2000})
 adjusted=holm([s['paired_t_p_two_sided'] for s in stats])
 for s,p in zip(stats,adjusted):s['holm_p_family_suite']=p
 dump(run/'summary.json',summaries);dump(run/'paired_statistics.json',stats)
 with (run/'per_document.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 # Re-evaluate every saved output against input annotations independently of score().
 validated=0
 for name in manifest['datasets']:
  rows,_,_=load_rows(name,manifest['limit']);goldmap={i:g for i,t,g in rows}
  for item in items:
   r=item['metrics']
   if r['dataset']!=name:continue
   gold=goldmap[r['document_id']];pred={normalize(p) for p,s in item['predictions'][:10]};hits=len(gold&pred)
   P=hits/10;R=hits/len(gold);F=2*hits/(10+len(gold))
   assert all(abs(r[k]-v)<1e-12 for k,v in [('precision',P),('recall',R),('f1',F)])
   validated+=1
 manifest.update(status='complete',records=len(records),metrics_recomputed=validated)
 dump(run/'manifest.json',manifest)
 dump(run/'EVIDENCE_VALIDATION.json',{'unique_pairs':len(records),'metrics_recomputed':validated,'expected_records':sum(d['documents']*len(d['applicable_configurations']) for d in manifest['datasets'].values()),'top_k':10,'all_matched':True})
 print('COMPLETE',manifest['suite'],len(records),'records',run,flush=True)

def model(cls,parsed,lang,stop,native=False):
 m=cls();m.load_document(input=parsed,language=lang,stoplist=list(stop),normalization=None)
 if not native:return load_model(cls,parsed,lang,stop)
 return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--suite',choices=['core','history','baselines'],required=True);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
 if a.limit<0:ap.error('limit must be nonnegative')
 run=a.run;run.mkdir(parents=True,exist_ok=True);hashes={p:sha(ROOT/p) for p in SOURCE_FILES}
 configurations=CORE_POLICIES if a.suite=='core' else ({'YAKE-current-window1':{},'YAKE-0.3.0-window1':{},'YAKE-0.3.2-window1':{},'YAKE-0.3.0-default-window2':{},'YAKE-current-window2':{},'RAKE-2018-Smart-English':{},'RAKE-2018-KEP-stopwords':{}} if a.suite=='history' else {m:{} for m in ['TextRank-common','TextRank-native','SingleRank-common','SingleRank-native','TF-IDF-common','TF-IDF-native','TF-IDF-no-POS']})
 manifest={'suite':a.suite,'status':'running','limit':a.limit,'configurations':configurations,'source_sha256':hashes,'datasets':{},'matching':'casefold whitespace exact; unique hits / 10; average per-document F1','runtime_packages':{p:importlib.metadata.version(p) for p in ['yake','numpy','spacy','networkx','segtok','jellyfish','pke']},'dependencies_historical':'Historical source executed using current pinned runtime; original executable identity unknown','started_utc':datetime.now(timezone.utc).isoformat()}
 if (run/'manifest.json').exists():
  old=json.loads((run/'manifest.json').read_text());assert old['source_sha256']==hashes and old['limit']==a.limit and old['suite']==a.suite,'Resume source/config changed'
  manifest=old;manifest['status']='running'
 done=set()
 if (run/'predictions.jsonl').exists():
  for line in (run/'predictions.jsonl').read_text().splitlines():
   r=json.loads(line)['metrics'];key=(r['dataset'],r['document_id'],r['method']);assert key not in done;done.add(key)
 dump(run/'manifest.json',manifest);start=time.perf_counter();logging.getLogger().setLevel(logging.ERROR)
 try:
  with (run/'predictions.jsonl').open('a') as f:
   for name in DATASETS:
    rows,digest,lang=load_rows(name,a.limit);stop=spacy.lang.en.stop_words.STOP_WORDS if lang=='en' else spacy.lang.es.stop_words.STOP_WORDS
    author=yake.KeywordExtractor(lan=lang).stopword_set
    manifest['datasets'][name]={'documents':len(rows),'archive_sha256':digest,'language':lang,'applicable_configurations':[m for m in configurations if not (m=='RAKE-2018-Smart-English' and lang=='es')]};dump(run/'manifest.json',manifest)
    print(a.suite,name,'START',len(rows),flush=True)
    if a.suite=='history':
     extractors={'YAKE-current-window1':yake.KeywordExtractor(lan=lang,n=3,top=10,dedupLim=.8,dedupFunc='leve',windowsSize=1),'YAKE-current-window2':yake.KeywordExtractor(lan=lang,n=3,top=10,dedupLim=.8,dedupFunc='leve',windowsSize=2)}
     for v in ['0.3.0','0.3.2']:extractors['YAKE-'+v+'-window1']=load_yake(v)(lan=lang,n=3,top=10,dedupLim=.8,windowsSize=1)
     extractors['YAKE-0.3.0-default-window2']=load_yake('0.3.0')(lan=lang,n=3,top=10,dedupLim=.8)
     rakeclass=load_rake();rakes={'RAKE-2018-Smart-English':rakeclass(str(CACHE/'SmartStoplist.txt'),max_words_length=3),'RAKE-2018-KEP-stopwords':rakeclass(str(CACHE/f'kep_stopwords_{lang}.txt'),max_words_length=3)}
    if a.suite=='baselines':
     cached=ROOT/'.cache/full_pos'/hashlib.sha256((digest+importlib.metadata.version('spacy')+('3.7.1' if lang=='en' else '3.7.0')+'rulesents_no_stemming').encode()).hexdigest()[:16];cached.mkdir(parents=True,exist_ok=True)
     # Reuse the verified old SemEval POS inputs for unchanged shared documents.
     olddigest=sha(ROOT/'data/SemEval2010.zip') if name=='SemEval2010' else digest
     oldcache=ROOT/'.cache/full_pos'/hashlib.sha256((olddigest+importlib.metadata.version('spacy')+('3.7.1' if lang=='en' else '3.7.0')+'rulesents_no_stemming').encode()).hexdigest()[:16]
     parsedrows={};nlp=None;dfs={'common':Counter(),'native':Counter(),'no-POS':Counter()};prepstart=time.perf_counter()
     for ident,text,gold in rows:
      path=cached/(ident+'.json');oldpath=oldcache/(ident+'.json')
      if path.exists():parsed=json.loads(path.read_text())
      elif oldpath.exists():parsed=json.loads(oldpath.read_text());dump(path,parsed)
      else:
       if nlp is None:
        nlp=spacy.load('en_core_web_sm' if lang=='en' else 'es_core_news_sm',disable=['ner','parser','lemmatizer']);nlp.add_pipe('sentencizer');nlp.max_length=3000000
       doc=nlp(text);parsed=[[(t.text,t.pos_) for t in sent] for sent in doc.sents];dump(path,parsed)
      parsedrows[ident]=parsed
      for policy in dfs:
       m=model(pke.unsupervised.TfIdf,parsed,lang,stop,native=policy!='common')
       if policy=='native':m.candidate_selection(n=3)
       if policy=='no-POS':m.ngram_selection(n=3);m.candidate_filtering(maximum_word_number=3)
       dfs[policy].update(m.candidates.keys())
     for df in dfs.values():df['--NB_DOC--']=len(rows)
     manifest['datasets'][name]['shared_POS_and_DF_seconds']=time.perf_counter()-prepstart;manifest['datasets'][name]['df_sha256']={p:hashlib.sha256(json.dumps(dict(df),sort_keys=True).encode()).hexdigest() for p,df in dfs.items()};dump(run/'manifest.json',manifest)
    for i,(ident,text,gold) in enumerate(rows):
     for method,choices in configurations.items():
      if (name,ident,method) in done:continue
      # An explicitly English-only SmartStoplist is not applied to Spanish as a faithful baseline.
      if method=='RAKE-2018-Smart-English' and lang=='es':continue
      begin=time.perf_counter()
      if a.suite=='core':
       chosenstop=author if choices.get('stoplist')=='author' else stop if lang=='es' else None
       result,_=extract(text,Config(window=choices.get('window',1)),omit=choices.get('omit'),stopwords=chosenstop,collect_trace=False,policy=Policy(**choices.get('policy',{})))
       if method=='Independent-baseline':assert result==original_extract(text,Config(),stopwords=chosenstop,collect_trace=False)[0]
      elif a.suite=='history':
       if method in rakes:result=rakes[method].run(text)[:10]
       else:
        result=extractors[method].extract_keywords(text)
        if method.startswith('YAKE-0.'):result=[(phrase,float(value)) for value,phrase in result]
      else:
       prefix,policy=('TF-IDF','no-POS') if method=='TF-IDF-no-POS' else method.rsplit('-',1);native=policy!='common';cls={'TextRank':pke.unsupervised.TextRank,'SingleRank':pke.unsupervised.SingleRank,'TF-IDF':pke.unsupervised.TfIdf}[prefix]
       m=model(cls,parsedrows[ident],lang,stop,native)
       if prefix=='TextRank':
        m.candidate_weighting(window=2,pos={'NOUN','PROPN','ADJ'},top_percent=.33 if native else None)
        if native:
         m.candidate_filtering(maximum_word_number=3)
         m.weights={key:value for key,value in m.weights.items() if key in m.candidates}
       elif prefix=='SingleRank':
        if native:m.candidate_selection(pos={'NOUN','PROPN','ADJ'});m.candidate_filtering(maximum_word_number=3)
        m.candidate_weighting(window=10,pos={'NOUN','PROPN','ADJ'})
       else:
        if policy=='native':m.candidate_selection(n=3)
        elif policy=='no-POS':m.ngram_selection(n=3);m.candidate_filtering(maximum_word_number=3)
        m.candidate_weighting(df=dict(dfs[policy]))
       result=m.get_n_best(n=10,redundancy_removal=False)
      elapsed=time.perf_counter()-begin
      assert len(result)<=10 and all(math.isfinite(float(value)) for phrase,value in result)
      p,r,F=score([phrase for phrase,value in result],gold)
      row=dict(dataset=name,document_id=ident,method=method,precision=p,recall=r,f1=F,seconds=elapsed,returned=len(result))
      f.write(json.dumps({'metrics':row,'predictions':result},ensure_ascii=False,allow_nan=False)+'\n');f.flush();done.add((name,ident,method))
     if (i+1)%50==0 or i+1==len(rows):print(a.suite,name,i+1,'/',len(rows),flush=True)
    print(a.suite,name,'DONE',flush=True)
  manifest['elapsed_seconds_this_invocation']=time.perf_counter()-start
  finalize(run,manifest)
 except Exception as e:
  manifest.update(status='failed',error=repr(e));dump(run/'manifest.json',manifest);raise
if __name__=='__main__':main()
