"""Aggregate audit evidence, recheck metrics and inspect error/length effects."""
import argparse,csv,hashlib,json,re,sys,platform,importlib.metadata,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr,ttest_rel
from nltk.stem import PorterStemmer
from scripts.full_comparison import ROOT,load_dataset,normalize,PUBLISHED,METHODS
from scripts.fidelity_experiments import load_rows,bootstrap,holm,dump,sha,read_jsonl
BASE=ROOT/'results/expanded/20261009T100336_607448Z'
DATASETS=['SemEval2010','Schutz2008','500N-KPCrowd','WICC']

def lines(path):return read_jsonl(path)
def csvout(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=ROOT/'results/fidelity/20261010_audit');a=ap.parse_args();a.run=a.run.resolve()
 suites={s:json.loads((a.run/s/'manifest.json').read_text()) for s in ['core','history','baselines','recovered_cpp','semeval244_stemmed','early_releases']}
 assert all(m['status']=='complete' for m in suites.values()),'Some experiments are unfinished'
 inputs={s:lines(a.run/s/'predictions.jsonl') for s in ['core','history','baselines','recovered_cpp','early_releases']}
 original=lines(BASE/'predictions.jsonl');inputs['archived_main']=original
 summaries={s:json.loads((a.run/s/'summary.json').read_text()) for s in suites}
 datasetrows={d:load_dataset(d)[0] for d in DATASETS};gold={d:{i:g for i,t,g in rows} for d,rows in datasetrows.items()}
 validation={};allrecords={}
 sourcecheck={}
 snapshots={sha(p):str(p.relative_to(ROOT)) for p in (a.run/'source_snapshots').glob('*.py')}
 with zipfile.ZipFile(ROOT/'results/evidence.zip') as preserved:
  for rel in preserved.namelist():
   snapshots[hashlib.sha256(preserved.read(rel)).hexdigest()]='results/evidence.zip!'+rel
 scripts={'early_releases':'scripts/historical_release_sweep.py','recovered_cpp':'scripts/run_recovered_baselines.py','semeval244_stemmed':'scripts/semeval244_sensitivity.py'}
 for suite,m in suites.items():
  checked={}
  for rel,digest in m.get('source_sha256',{}).items():
   if (ROOT/rel).exists() and sha(ROOT/rel)==digest:checked[rel]={'sha256':digest,'verified_at':rel}
   else:
    assert digest in snapshots,('Missing extraction source snapshot',suite,rel)
    checked[rel]={'sha256':digest,'verified_at':snapshots[digest]}
  if suite in scripts:
   rel=scripts[suite];digest=m['script_sha256']
   if sha(ROOT/rel)==digest:location=rel
   else:
    assert digest in snapshots,('Missing runner source',suite,rel);location=snapshots[digest]
   checked[rel]={'sha256':digest,'verified_at':location}
  sourcecheck[suite]=checked
 validation['extraction_source_hashes']=sourcecheck
 for suite,items in inputs.items():
  keys=set();recomputed=0
  if suite!='archived_main':assert len(items)==suites[suite]['records'],('Record count',suite)
  for item in items:
   r=item['metrics'];d=r['dataset'];i=r['document_id'];m=r['method'];key=(d,i,m);assert key not in keys;keys.add(key)
   pred={normalize(p) for p,s in item['predictions'][:10]};g=gold[d][i];hits=len(pred&g)
   for metric,value in [('precision',hits/10),('recall',hits/len(g)),('f1',2*hits/(10+len(g)))]:assert abs(r[metric]-value)<1e-12,(suite,key,metric)
   allrecords[(suite,d,i,m)]=r;recomputed+=1
  validation[suite]={'unique_records':len(keys),'metrics_independently_recomputed':recomputed,'all_matched':True}
 # Paired inference resembling paper's test design, not reproducing its unavailable original outputs.
 comparisons=[]
 for d in DATASETS:
  ids=sorted(gold[d]);reference='YAKE-0.3.0-default-window2'
  candidates=[('recovered_cpp',m+'-recovered-modernPOS') for m in ['TextRank','SingleRank','TfIdf']]+[('history','RAKE-2018-KEP-stopwords')]
  for suite,method in candidates:
   for metric in ['precision','recall','f1']:
    ref=np.array([allrecords[('history',d,i,reference)][metric] for i in ids]);other=np.array([allrecords[(suite,d,i,method)][metric] for i in ids]);diff=ref-other
    p=float(ttest_rel(ref,other).pvalue) if np.any(diff) else 1.
    comparisons.append({'dataset':d,'reference':reference,'baseline':method,'metric':metric,'contrast':'historical YAKE minus recovered baseline','mean_difference':float(diff.mean()),'n':len(ids),'paired_t_p_two_sided':p,'bootstrap_95':bootstrap(diff),'exploratory':True})
 for row,p in zip(comparisons,holm([r['paired_t_p_two_sided'] for r in comparisons])):row['holm_p_all_48_comparisons']=p
 dump(a.run/'recovered_paired_statistics.json',comparisons)
 # Confirm archived baseline identity; all original inputs retained.
 equality={}
 for d in DATASETS:
  ids=sorted(gold[d]);independent=all(abs(allrecords[('core',d,i,'Independent-baseline')]['f1']-allrecords[('archived_main',d,i,'Independent-reconstruction')]['f1'])<1e-12 for i in ids)
  package=all(abs(allrecords[('history',d,i,'YAKE-current-window1')]['f1']-allrecords[('archived_main',d,i,'YAKE-package')]['f1'])<1e-12 for i in ids)
  equality[d]={'independent_baseline_equals_archived_metrics':independent,'current_package_equals_archived_metrics':package};assert independent and package
 # Annotation diagnostics and error slices from archived outputs, no tuning.
 annotation=[];slices=[];matching=[];stemmer=PorterStemmer()
 for d,rows in datasetrows.items():
  byid={i:(t,g) for i,t,g in rows};lengths={i:len(t.split()) for i,t,g in rows};quartiles=np.quantile(list(lengths.values()),[.25,.5,.75]);countgold=0;literal=0;long=0
  for i,text,g in rows:
   normalized=normalize(text);countgold+=len(g);long+=sum(len(p.split())>3 for p in g)
   literal+=sum(bool(re.search(r'(?<!\w)'+re.escape(p)+r'(?!\w)',normalized)) for p in g)
  annotation.append({'dataset':d,'documents':len(rows),'total_unique_gold_phrases':countgold,'gold_per_document':countgold/len(rows),'gold_over3_words':long,'literal_text_present_gold_proxy':literal,'literal_presence_definition':'Casefold whitespace text; regex Unicode word boundaries; diagnostic, not an extraction upper bound','whitespace_words_mean':float(np.mean(list(lengths.values())))})
  for method in METHODS:
   group=[item for item in original if item['metrics']['dataset']==d and item['metrics']['method']==method]
   f1=[x['metrics']['f1'] for x in group];lens=[lengths[x['metrics']['document_id']] for x in group];corr=spearmanr(lens,f1)
   slices.append({'dataset':d,'method':method,'slice':'all','documents':len(group),'mean_f1':float(np.mean(f1)),'length_f1_spearman':float(corr.statistic),'spearman_p_exploratory':float(corr.pvalue)})
   for bucket in range(4):
    selected=[x['metrics']['f1'] for x in group if int(np.searchsorted(quartiles,lengths[x['metrics']['document_id']],side='right'))==bucket]
    if selected:slices.append({'dataset':d,'method':method,'slice':'length_quartile_'+str(bucket+1),'documents':len(selected),'mean_f1':float(np.mean(selected)),'length_f1_spearman':None,'spearman_p_exploratory':None})
   for scheme in ['casefold-exact','casefold-exact-returned-budget','plural-final-s-tolerance','porter-stemmed-sensitivity']:
    scores=[]
    for item in group:
     i=item['metrics']['document_id'];pred={normalize(p) for p,s in item['predictions'][:10]};g=byid[i][1]
     if scheme=='porter-stemmed-sensitivity':
      canon=lambda p:' '.join(stemmer.stem(w) for w in p.split());pred={canon(p) for p in pred};g={canon(p) for p in g};hits=len(pred&g)
     elif scheme=='plural-final-s-tolerance':
      # Maximum bipartite match prevents one prediction earning multiple gold hits.
      assigned={}
      def augment(p,seen):
       for ref in sorted(g):
        if ref in seen or not (p==ref or p+'s'==ref or ref+'s'==p):continue
        seen.add(ref)
        if ref not in assigned or augment(assigned[ref],seen):assigned[ref]=p;return True
       return False
      hits=sum(augment(p,set()) for p in sorted(pred))
     else:hits=len(pred&g)
     budget=len(item['predictions'][:10]) if scheme=='casefold-exact-returned-budget' else 10
     scores.append((hits/budget if budget else 0.,hits/len(g),2*hits/(budget+len(g))))
    means=np.mean(scores,axis=0);matching.append({'dataset':d,'method':method,'matching':scheme,'precision':float(means[0]),'recall':float(means[1]),'f1':float(means[2]),'primary':scheme=='casefold-exact'})
 # Small, explicitly selected error casebook; these examples are not a random sample.
 cases=[];casebook=['# Keyword extraction error casebook','',
 'Each dataset contributes a median-length document and the largest absolute F1 disagreement between the independent reconstruction and current YAKE. These are diagnostic selections, not representative estimates or causal explanations. Literal-presence categories use normalized Unicode word boundaries; absence is a proxy, not proof a reference is impossible to extract. Full texts are not reproduced.','']
 for d,rows in datasetrows.items():
  byid={i:(t,g) for i,t,g in rows};ordered=sorted(byid,key=lambda i:(len(byid[i][0].split()),i))
  disagreements={i:abs(allrecords[('archived_main',d,i,'Independent-reconstruction')]['f1']-allrecords[('archived_main',d,i,'YAKE-package')]['f1']) for i in byid}
  largest=sorted(byid,key=lambda i:(-disagreements[i],i))[0]
  for selection,i in [('median-length',ordered[len(ordered)//2]),('largest-absolute-F1-disagreement',largest)]:
   text,g=byid[i];normalized=normalize(text)
   present={p for p in g if re.search(r'(?<!\w)'+re.escape(p)+r'(?!\w)',normalized)}
   item={'dataset':d,'document_id':i,'selection':selection,'gold_count':len(g),'literal_present_gold_count_proxy':len(present),'whitespace_words':len(text.split()),'methods':{}}
   casebook += ['## '+d+' / '+i+' / '+selection,'',f"Reference phrases: {len(g)}; literal-present proxy: {len(present)}; whitespace words: {len(text.split())}.",'']
   for method in ['YAKE-package','Independent-reconstruction']:
    phrases=[p for p,s in next(x['predictions'] for x in original if x['metrics']['dataset']==d and x['metrics']['document_id']==i and x['metrics']['method']==method)]
    pred={normalize(p) for p in phrases};metrics=allrecords[('archived_main',d,i,method)]
    evidence={'f1':metrics['f1'],'predictions':phrases,'exact_hits':sorted(pred&g),'unmatched_predictions':sorted(pred-g),'missed_literal_present_gold_examples':sorted(present-pred)[:8],'nonliteral_gold_examples':sorted(g-present)[:8]}
    item['methods'][method]=evidence
    show=lambda values:'; '.join(v.replace('|','/').replace('\n',' ') for v in values) or '(none)'
    casebook += [f"**{method}: F1 {metrics['f1']:.4f}**",'', '- Predictions: '+show(phrases),'- Exact hits: '+show(evidence['exact_hits']),'- Unmatched predictions: '+show(evidence['unmatched_predictions']),'- Missed literal-present reference examples (up to 8): '+show(evidence['missed_literal_present_gold_examples']),'- Reference examples without a literal match (up to 8): '+show(evidence['nonliteral_gold_examples']),'']
   cases.append(item)
 dump(a.run/'qualitative_cases.json',cases);(a.run/'CASEBOOK.md').write_text('\n'.join(casebook))
 dump(a.run/'annotation_audit.json',annotation);csvout(a.run/'length_error_slices.csv',slices);csvout(a.run/'matching_sensitivity.csv',matching)
 # Export full four-dataset ablation and one-factor sensitivity tables.
 core=summaries['core'];ablationrows=[];sensitivity=[]
 for d in DATASETS:
  base=core[d]['Independent-baseline']['f1']
  for method,values in core[d].items():
   row={'dataset':d,'method':method,**{k:values[k] for k in ['precision','recall','f1']},'f1_delta_from_independent':values['f1']-base}
   sensitivity.append(row)
   if method=='Independent-baseline' or method.startswith('without-'):ablationrows.append(row)
 csvout(a.run/'all_dataset_ablations.csv',ablationrows);csvout(a.run/'controlled_sensitivity.csv',sensitivity)
 historicaltable=[]
 for d in DATASETS:
  for m,v in summaries['history'][d].items():historicaltable.append({'dataset':d,'method':m,**{k:v[k] for k in ['precision','recall','f1']},'paper_yake_f1':PUBLISHED[d][0][2] if m.startswith('YAKE') else None})
 csvout(a.run/'historical_comparison.csv',historicaltable)
 # Exact phrase/score output identity is stronger than aggregate equality.
 predmaps={suite:{(item['metrics']['dataset'],item['metrics']['document_id'],item['metrics']['method']):item['predictions'] for item in items} for suite,items in inputs.items()}
 for d in DATASETS:
  for i in gold[d]:
   assert predmaps['core'][(d,i,'Independent-baseline')]==predmaps['archived_main'][(d,i,'Independent-reconstruction')]
   assert predmaps['history'][(d,i,'YAKE-current-window1')]==predmaps['archived_main'][(d,i,'YAKE-package')]
   assert predmaps['history'][(d,i,'YAKE-0.3.0-window1')]==predmaps['history'][(d,i,'YAKE-0.3.2-window1')]
   assert predmaps['baselines'][(d,i,'TF-IDF-native')]==predmaps['baselines'][(d,i,'TF-IDF-no-POS')]
   for prefix in ['TextRank','SingleRank','TF-IDF']:
    current=predmaps['baselines'][(d,i,prefix+'-common')];archived=predmaps['archived_main'][(d,i,prefix+'-PKE')]
    assert [p for p,s in current]==[p for p,s in archived]
    assert abs(allrecords[('baselines',d,i,prefix+'-common')]['f1']-allrecords[('archived_main',d,i,prefix+'-PKE')]['f1'])<1e-12
  equality[d]['exact_ranked_outputs_equal']=True
  equality[d]['030_and_032_outputs_equal']=True
  equality[d]['all_three_common_PKE_ranked_phrases_and_metrics_equal_archived']=True
  equality[d]['TF_IDF_native_equals_no_POS_null_control']=True
 validation['baseline_equality']=equality;validation['additional_evaluations']=sum(m['records'] for m in suites.values());validation['archived_main_evaluations']=len(original)
 # Separate validation for official task gold (244) needs that protocol's stemmer and source labels.
 import tarfile,io
 taskgold={}
 with tarfile.open(ROOT/'.cache/fidelity_sources/SemEval2010-official.tar.gz') as archive:
  for part in ['train','test_answer']:
   with tarfile.open(fileobj=io.BytesIO(archive.extractfile('SemEval2010/'+part+'.tar.gz').read())) as inner:
    member=next(m for m in inner.getmembers() if m.name.endswith('combined.stem.final'))
    for line in inner.extractfile(member).read().decode().splitlines():
     ident,phrases=line.split(' : ',1);taskgold[ident]={normalize(s) for s in phrases.split(',') if s.strip()}
 secondary=lines(a.run/'semeval244_stemmed/predictions.jsonl');unique=set()
 for item in secondary:
  r=item['metrics'];g=taskgold[r['document_id']];pred={' '.join(stemmer.stem(w) for w in normalize(p).split()) for p,s in item['predictions'][:10]};hits=len(pred&g)
  assert r['hits']==hits and abs(r['f1']-2*hits/(10+len(g)))<1e-12
  unique.add((r['document_id'],r['method']))
 assert len(unique)==len(secondary)==244*8
 validation['semeval244_stemmed']={'unique_records':len(unique),'all_recomputed':True,'protocol_separate':True}
 dump(a.run/'EVIDENCE_VALIDATION.json',validation)
 dump(a.run/'analysis_manifest.json',{'script_sha256':sha(Path(__file__)),'python':sys.version,'platform':platform.platform(),'installed_packages':{p:importlib.metadata.version(p) for p in ['pandas','numpy','yake','spacy','segtok','jellyfish','scipy','nltk','networkx','pke']},'input_manifest_sha256':{s:sha(a.run/s/'manifest.json') for s in suites},'archived_manifest_sha256':sha(BASE/'manifest.json'),'no_posthoc_configuration_selection':True,'statistics_note':'Exploratory paired tests; Holm correction per declared family. Matching changes are separately labelled sensitivities.'})
 print('Audit analysis validated',validation['additional_evaluations'],'new evaluations and',len(original),'archived evaluations.')
if __name__=='__main__':main()
