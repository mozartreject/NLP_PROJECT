"""Audit all six PyPI releases available before/during ECIR 2018.
Execute both distinct earlier scoring families; 0.3.x is executed by fidelity_experiments.
"""
import argparse,csv,hashlib,importlib.util,json,math,sys,tarfile,types,urllib.request
from pathlib import Path
import numpy as np
from fidelity_experiments import ROOT,load_rows,dump,score,sha
from replication.historical import CACHE
VERSIONS=['0.2.0','0.2.1','0.2.2','0.2.4','0.3.0','0.3.2']
def prepare():
 meta=json.loads((CACHE/'pypi_yake.json').read_text());audit=[]
 for v in VERSIONS:
  f=next(f for f in meta['releases'][v] if f['packagetype']=='sdist');p=CACHE/f['filename']
  if not p.exists():
   with urllib.request.urlopen(f['url'],timeout=60) as response:p.write_bytes(response.read())
  assert sha(p)==f['digests']['sha256'];pieces={}
  with tarfile.open(p) as t:
   for m in t.getmembers():
    if m.isfile():
     rel=Path(m.name);assert not rel.is_absolute() and '..' not in rel.parts
     dest=CACHE/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.extractfile(m).read())
   for suffix in ['/yake/datarepresentation.py','/yake/yake.py','/yake/StopwordsList/stopwords_en.txt','/yake/StopwordsList/stopwords_es.txt']:
    name=next(n for n in t.getnames() if n.endswith(suffix));pieces[suffix]=hashlib.sha256(t.extractfile(name).read()).hexdigest()
  audit.append({'version':v,'url':f['url'],'upload_time':f['upload_time_iso_8601'],'archive_sha256':sha(p),'runtime_files_sha256':pieces})
 assert audit[0]['runtime_files_sha256']==audit[1]['runtime_files_sha256']==audit[2]['runtime_files_sha256']
 assert audit[4]['runtime_files_sha256']==audit[5]['runtime_files_sha256']
 return audit

def loader(v):
 alias='early_yake_'+v.replace('.','_');folder=CACHE/('yake-'+v)/'yake'
 if alias not in sys.modules:
  package=types.ModuleType(alias);package.__path__=[str(folder)];sys.modules[alias]=package
  spec=importlib.util.spec_from_file_location(alias+'.datarepresentation',folder/'datarepresentation.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
  main=types.ModuleType(alias+'.yake');main.__file__=str(folder/'yake.py');sys.modules[main.__name__]=main
  source=(folder/'yake.py').read_text().replace('from yake.datarepresentation import DataCore',f'from {alias}.datarepresentation import DataCore');exec(compile(source,str(folder/'yake.py'),'exec'),main.__dict__)
 return sys.modules[alias+'.yake'].YakeKeywordExtractor

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--limit',type=int,default=0);a=ap.parse_args();a.run.mkdir(parents=True,exist_ok=True);audit=prepare()
 dump(ROOT/'configs/historical_releases.json',{'releases':audit,'families':[['0.2.0','0.2.1','0.2.2'],['0.2.4'],['0.3.0','0.3.2']],'equality_scope':'Scorer, extractor and EN/ES stoplists byte-identical within stated families; packaging and other files may differ.'})
 manifest={'status':'running','release_audit':audit,'script_sha256':sha(Path(__file__)),'limit':a.limit,'runtime':'Pinned current dependencies, not original dependency environment','datasets':{}}
 dump(a.run/'manifest.json',manifest);records=[];summary={}
 with (a.run/'predictions.jsonl').open('w') as out:
  for dataset in ['500N-KPCrowd','SemEval2010','Schutz2008','WICC']:
   rows,digest,lang=load_rows(dataset,a.limit);manifest['datasets'][dataset]={'documents':len(rows),'archive_sha256':digest};extractors={}
   for v in ['0.2.0','0.2.4']:
    for window in [1,2]:extractors[f'YAKE-{v}-window{window}']=loader(v)(lan=lang,n=3,top=10,dedupLim=.8,windowsSize=window)
   for i,(ident,text,gold) in enumerate(rows):
    for method,e in extractors.items():
     result=[(p,float(s)) for s,p in e.extract_keywords(text)];assert all(math.isfinite(s) for p,s in result)
     P,R,F=score([p for p,s in result],gold);r={'dataset':dataset,'document_id':ident,'method':method,'precision':P,'recall':R,'f1':F,'returned':len(result)};records.append(r);out.write(json.dumps({'metrics':r,'predictions':result},ensure_ascii=False)+'\n');out.flush()
    if (i+1)%50==0 or i+1==len(rows):print('early releases',dataset,i+1,'/',len(rows),flush=True)
   summary[dataset]={}
   for m in extractors:
    group=[r for r in records if r['dataset']==dataset and r['method']==m];summary[dataset][m]={k:float(np.mean([r[k] for r in group])) for k in ['precision','recall','f1','returned']}
   dump(a.run/'summary.json',summary);dump(a.run/'manifest.json',manifest)
 with (a.run/'per_document.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 manifest.update(status='complete',records=len(records));dump(a.run/'manifest.json',manifest);print('COMPLETE early release families',len(records),flush=True)
if __name__=='__main__':main()
