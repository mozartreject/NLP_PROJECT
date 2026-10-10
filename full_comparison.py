"""Four-dataset, six-configuration benchmark with cached POS and resumable evidence.
Current implementations, not claimed publication-time executable equivalence.
"""
import argparse,csv,hashlib,importlib.metadata,json,logging,math,os,platform,re,sys,time,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pke,spacy,yake
from scipy.stats import ttest_rel
from replication.core import Config,extract,tokenize
ROOT=Path(__file__).resolve().parent
PKE_COMMIT='69871ffdb720b83df23684fea53ec8776fd87e63'
DATASETS={'500N-KPCrowd':('500N-KPCrowd-v1.1.zip','en',500),
 'SemEval2010':('SemEval2010.zip','en',243),'Schutz2008':('Schutz2008.zip','en',1231),'WICC':('wicc.zip','es',1640)}
METHODS=['YAKE-package','TextRank-PKE','TF-IDF-PKE','SingleRank-PKE','RAKE-local','Independent-reconstruction']
PUBLISHED={
 'SemEval2010':[[.153,.103,.123],[.101,.067,.081],[.036,.023,.028],[.035,.022,.027],[.007,.004,.005]],
 'Schutz2008':[[.217,.058,.091],[.198,.052,.082],[.100,.028,.043],[.082,.024,.037],[.013,.004,.006]],
 '500N-KPCrowd':[[.251,.063,.101],[.265,.063,.103],[.223,.060,.095],[.190,.054,.084],[.120,.038,.058]],
 'WICC':[[.050,.141,.073],[.018,.058,.027],[.026,.067,.037],[.017,.045,.024],[.004,.012,.006]]}

def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def normalize(s):return ' '.join(s.casefold().split())
def score(pred,gold,k=10):
 hits=len({normalize(p) for p in pred}&gold);p=hits/k;r=hits/len(gold)
 return p,r,2*p*r/(p+r) if p+r else 0.

def load_dataset(name,limit=0):
 filename,lang,count=DATASETS[name];archive=ROOT/'data'/filename
 with zipfile.ZipFile(archive) as z:
  names=sorted(n for n in z.namelist() if '/docsutf8/' in n and n.endswith('.txt'))
  if len(names)!=count:raise ValueError(f'{name}: expected {count} docs, found {len(names)}')
  rows=[]
  for n in names:
   goldpath=n.replace('/docsutf8/','/keys/').removesuffix('.txt')+'.key'
   gold={normalize(g) for g in z.read(goldpath).decode('utf-8-sig').splitlines() if g.strip()}
   if not gold:raise ValueError('Empty gold: '+goldpath)
   rows.append((Path(n).stem,z.read(n).decode('utf-8-sig'),gold))
 if len({r[0] for r in rows})!=count:raise ValueError('Duplicate IDs')
 return (rows[:limit] if limit else rows),hashlib.sha256(archive.read_bytes()).hexdigest(),lang

def select(model):
 # A common explicit POS-constrained 1..3-gram candidate policy for PKE baselines.
 model.ngram_selection(n=3)
 model.candidate_filtering(maximum_word_number=3,pos_blacklist=['ADP','ADV','AUX','CCONJ','DET','INTJ','NUM','PART','PRON','PUNCT','SCONJ','SYM','VERB','X','SPACE'])
 return model

def load_model(cls,parsed,lang,stop):
 model=cls();model.load_document(input=parsed,language=lang,stoplist=list(stop),normalization=None)
 return select(model)

def rake(text,stop):
 # Independent Unicode RAKE: degree including self / frequency, phrase score=sum(word scores).
 phrases=[]
 for sentence in tokenize(text):
  phrase=[]
  for token in sentence+['.']:
   word=token.casefold()
   if not token[0].isalpha() or word in stop:
    if 1<=len(phrase)<=3:phrases.append(tuple(phrase))
    phrase=[]
   else:phrase.append(word)
 freq=Counter();degree=Counter()
 for phrase in phrases:
  for word in phrase:freq[word]+=1;degree[word]+=len(phrase)
 candidates={' '.join(p):sum(degree[w]/freq[w] for w in p) for p in phrases}
 return sorted(candidates.items(),key=lambda p:(-p[1],p[0]))[:10]

def cache_parsed(rows,nlp,cache,lang,stop,name):
 cache.mkdir(parents=True,exist_ok=True);df=Counter();total_seconds=0
 for i,(ident,text,gold) in enumerate(rows):
  p=cache/(ident+'.json');begin=time.perf_counter()
  if p.exists():parsed=json.loads(p.read_text())
  else:
   doc=nlp(text);parsed=[[(t.text,t.pos_) for t in sent] for sent in doc.sents]
   dump(p,parsed)
  total_seconds+=time.perf_counter()-begin
  tf=load_model(pke.unsupervised.TfIdf,parsed,lang,stop);df.update(tf.candidates.keys())
  if (i+1)%100==0 or i+1==len(rows):print(f'{name} POS/IDF: {i+1}/{len(rows)}',flush=True)
 df['--NB_DOC--']=len(rows)
 return dict(df),total_seconds

def finalize(run,records,manifest):
 summary={};comparison=[];intervals=[];rng=np.random.default_rng(42)
 for dataset in manifest['datasets']:
  summary[dataset]={}
  for mi,method in enumerate(METHODS):
   group=[r for r in records if r['dataset']==dataset and r['method']==method]
   if len(group)!=manifest['datasets'][dataset]['evaluated_documents']:raise ValueError('Incomplete experiment group')
   values={k:float(np.mean([r[k] for r in group])) for k in ['precision','recall','f1','seconds','returned']}
   p,r=values['precision'],values['recall'];values['f1_of_macro_PR']=2*p*r/(p+r) if p+r else 0
   summary[dataset][method]=values
   if mi<5:
    old=PUBLISHED[dataset][mi]
    comparison.append(dict(dataset=dataset,method=method,paper_precision=old[0],paper_recall=old[1],paper_f1=old[2],our_precision=values['precision'],our_recall=values['recall'],our_f1=values['f1'],f1_delta=values['f1']-old[2]))
  base={r['document_id']:r['f1'] for r in records if r['dataset']==dataset and r['method']=='YAKE-package'}
  for method in METHODS[1:]:
   group=[r for r in records if r['dataset']==dataset and r['method']==method]
   diff=np.array([base[r['document_id']]-r['f1'] for r in group])
   samples=np.array([rng.choice(diff,len(diff),replace=True).mean() for _ in range(2000)])
   pvalue=float(ttest_rel([base[r['document_id']] for r in group],[r['f1'] for r in group]).pvalue) if np.any(diff) else 1.
   intervals.append(dict(dataset=dataset,contrast='YAKE-package minus '+method,mean_difference=float(diff.mean()),bootstrap_95=np.quantile(samples,[.025,.975]).tolist(),paired_t_p_unadjusted=pvalue))
 dump(run/'summary.json',summary);dump(run/'paired_statistics.json',intervals)
 for name,rows in [('per_document.csv',records),('paper_comparison.csv',comparison)]:
  with (run/name).open('w',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 lines=['# Expanded four-dataset comparison','',
 'Current implementations with declared preprocessing/settings; not verified publication-time equivalence.',
 'SemEval archive: 243 documents versus 244 described by the paper. Other archive counts match.',
 'F1 is mean per-document F1; top 10, casefolded exact matching. No supervised training.',
 'TF-IDF uses collection-level candidate document frequencies (transductive), with POS tagging shared across PKE methods.','']
 for dataset,values in summary.items():
  lines += ['## '+dataset,'','| Method | Paper P | Paper R | Paper F1 | Our P@10 | Our R | Our F1 | F1 delta |','|---|---:|---:|---:|---:|---:|---:|---:|']
  for mi,method in enumerate(METHODS):
   v=values[method]
   old=PUBLISHED[dataset][mi] if mi<5 else None
   prior=' | '.join(f'{x:.4f}' for x in old) if old else '— | — | —'
   delta=f"{v['f1']-old[2]:+.4f}" if old else '—'
   lines.append(f"| {method} | {prior} | {v['precision']:.4f} | {v['recall']:.4f} | {v['f1']:.4f} | {delta} |")
  lines.append('')
 lines += ['## Interpretation limits','',
 'Do not infer superiority from paper-vs-run deltas: original executable versions, tokenization, stoplists, POS taggers and exact aggregation details have not been matched.',
 'Our PKE baselines use a common POS-filtered 1–3-gram policy. TextRank window=2 and unweighted PageRank; SingleRank window=10 and weighted PageRank; damping=0.85.',
 'RAKE is a local Unicode implementation with language-specific spaCy stopwords; phrases longer than 3 are discarded before word statistics.',
 'Independent reconstruction uses the prior English stoplist for English and spaCy Spanish stopwords for WICC; it retains documented equation safeguards.',
 'Paired statistics compare our matched document outputs, not unpublished per-document outputs from the paper. T-test p-values are unadjusted exploratory values across multiple comparisons; bootstrap intervals are pointwise.',
 'Timing columns exclude shared POS preprocessing and corpus DF construction; those stage times appear in the manifest.','']
 (run/'COMPARISON_REPORT.md').write_text('\n'.join(lines))
 manifest['status']='complete';manifest['records']=len(records);dump(run/'manifest.json',manifest)
 print('COMPLETE:',run,flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=0);parser.add_argument('--resume',type=Path);parser.add_argument('--datasets',nargs='+',choices=list(DATASETS),default=list(DATASETS));args=parser.parse_args()
 if args.limit<0:parser.error('limit must be nonnegative')
 settings={'top_k':10,'max_ngram':3,'dedup_threshold':.8,'window_yake':1,'window_textrank':2,'window_singlerank':10,'normalization':'none','limit':args.limit,'datasets':args.datasets}
 hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['full_comparison.py','replication/core.py']}
 run=args.resume or ROOT/'results/expanded'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ');run.mkdir(parents=True,exist_ok=True)
 manifest={'status':'running','settings':settings,'source_sha256':hashes,'datasets':{},'pke_commit':PKE_COMMIT,'python':sys.version,'platform':platform.platform(),'packages':{p:importlib.metadata.version(p) for p in ['pke','spacy','en-core-web-sm','es-core-news-sm','yake','numpy','networkx','scikit-learn','nltk']}}
 if args.resume:
  old=json.loads((run/'manifest.json').read_text())
  if old['settings']!=settings or old['source_sha256']!=hashes:raise ValueError('Resume config/source changed')
 records=[]
 if (run/'predictions.jsonl').exists():
  for line in (run/'predictions.jsonl').read_text().splitlines():
   item=json.loads(line);records.append(item['metrics'])
 done={(r['dataset'],r['document_id'],r['method']) for r in records}
 logging.getLogger().setLevel(logging.ERROR)
 models={};started=time.perf_counter()
 dump(run/'manifest.json',manifest)
 try:
  for name in args.datasets:
   rows,digest,lang=load_dataset(name,args.limit)
   if lang not in models:
    model_name='en_core_web_sm' if lang=='en' else 'es_core_news_sm'
    nlp=spacy.load(model_name,disable=['ner','parser','lemmatizer']);nlp.add_pipe('sentencizer');nlp.max_length=3000000;models[lang]=nlp
   nlp=models[lang];stop=nlp.Defaults.stop_words
   cache_id=hashlib.sha256((digest+manifest['packages']['spacy']+str(nlp.meta['version'])+'rulesents_no_stemming').encode()).hexdigest()[:16]
   cache=ROOT/'.cache/full_pos'/cache_id
   df,prep_seconds=cache_parsed(rows,nlp,cache,lang,stop,name)
   manifest['datasets'][name]={'archive_sha256':digest,'available_documents':DATASETS[name][2],'evaluated_documents':len(rows),'language':lang,'gold_phrases_mean':float(np.mean([len(g) for _,_,g in rows])),'POS_cache_load_or_compute_seconds':prep_seconds,'candidate_df_sha256':hashlib.sha256(json.dumps(df,sort_keys=True).encode()).hexdigest()}
   dump(run/'manifest.json',manifest)
   reference=yake.KeywordExtractor(lan=lang,n=3,top=10,dedupLim=.8,dedupFunc='leve',windowsSize=1)
   with (run/'predictions.jsonl').open('a') as output:
    for i,(ident,text,gold) in enumerate(rows):
     parsed=json.loads((cache/(ident+'.json')).read_text())
     for method in METHODS:
      if (name,ident,method) in done:continue
      begin=time.perf_counter()
      if method=='YAKE-package':result=reference.extract_keywords(text)
      elif method=='RAKE-local':result=rake(text,stop)
      elif method=='Independent-reconstruction':result,trace=extract(text,Config(),stopwords=stop if lang=='es' else None,collect_trace=False)
      else:
       cls={'TextRank-PKE':pke.unsupervised.TextRank,'SingleRank-PKE':pke.unsupervised.SingleRank,'TF-IDF-PKE':pke.unsupervised.TfIdf}[method]
       model=load_model(cls,parsed,lang,stop)
       if method=='TF-IDF-PKE':model.candidate_weighting(df=df)
       else:model.candidate_weighting(window=2 if method=='TextRank-PKE' else 10,pos={'NOUN','PROPN','ADJ'})
       result=model.get_n_best(n=10,redundancy_removal=False)
      elapsed=time.perf_counter()-begin
      if any(not math.isfinite(float(v)) for p,v in result):raise ValueError('Nonfinite score')
      p,r,f=score([p for p,v in result],gold)
      record=dict(dataset=name,document_id=ident,method=method,precision=p,recall=r,f1=f,seconds=elapsed,returned=len(result))
      output.write(json.dumps({'metrics':record,'predictions':result},ensure_ascii=False)+'\n');output.flush();records.append(record);done.add((name,ident,method))
     if (i+1)%100==0 or i+1==len(rows):print(f'{name} evaluated: {i+1}/{len(rows)}',flush=True)
   print(name,'F1:',{method:round(float(np.mean([r['f1'] for r in records if r['dataset']==name and r['method']==method])),4) for method in METHODS},flush=True)
  manifest['elapsed_seconds_this_invocation']=time.perf_counter()-started
  finalize(run,records,manifest)
 except Exception as e:
  manifest.update(status='failed',error_type=type(e).__name__,error=str(e));dump(run/'manifest.json',manifest);raise

if __name__=='__main__':main()
