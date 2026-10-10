"""Separate 244-document evaluation using original task's stemmed gold labels.
This is not a replacement for the unstemmed paper-table evaluation.
"""
import argparse,csv,hashlib,io,json,time,tarfile,urllib.request,zipfile
from collections import Counter
from pathlib import Path
import numpy as np,pke,spacy,yake
from nltk.stem import PorterStemmer
from full_comparison import ROOT,load_model,rake,normalize
from replication.core import Config,extract
from replication.historical import load_yake,CACHE
from fidelity_experiments import dump,sha
URL='https://raw.githubusercontent.com/snkim/AutomaticKeyphraseExtraction/master/SemEval2010.tar.gz'
METHODS=['YAKE-package','TextRank-PKE','TF-IDF-PKE','SingleRank-PKE','RAKE-local','Independent-reconstruction','YAKE-0.3.0-window1','YAKE-0.3.0-default-window2']
STEMMER=PorterStemmer()
def stem(phrase):return ' '.join(STEMMER.stem(w) for w in normalize(phrase).split())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--limit',type=int,default=0);a=ap.parse_args();a.run.mkdir(parents=True,exist_ok=True)
 path=CACHE/'SemEval2010-official.tar.gz'
 if not path.exists():
  with urllib.request.urlopen(URL,timeout=60) as f:path.write_bytes(f.read())
 gold={}
 with tarfile.open(path) as t:
  for part in ['train','test_answer']:
   with tarfile.open(fileobj=io.BytesIO(t.extractfile('SemEval2010/'+part+'.tar.gz').read())) as s:
    member=next(m for m in s.getmembers() if m.name.endswith('combined.stem.final'))
    for line in s.extractfile(member).read().decode('utf8').splitlines():
     ident,phrases=line.split(' : ',1);gold[ident]={normalize(p) for p in phrases.split(',') if p.strip()}
 assert len(gold)==244 and len(gold['C-86'])==14
 rows=[]
 with zipfile.ZipFile(ROOT/'data/SemEval2010-recovered244.zip') as z:
  for n in sorted(z.namelist()):
   if '/docsutf8/' in n and n.endswith('.txt'):rows.append((Path(n).stem,z.read(n).decode('utf-8-sig')))
 assert {i for i,t in rows}==set(gold)
 if a.limit:rows=rows[:a.limit]
 manifest={'status':'running','documents':len(rows),'dataset_text_sha256':sha(ROOT/'data/SemEval2010-recovered244.zip'),'official_task_url':URL,'official_task_archive_sha256':sha(path),'script_sha256':sha(Path(__file__)),'protocol':'Original task combined.stem.final; wordwise NLTK Porter stemming of predictions; top10, fixed-slot P@10, mean document F1. NOT unstemmed Table1 evaluation.','TFIDF':'Collection DF refit on all selected documents, including C-86 in full run.','original_243_preserved':True,'configurations':METHODS,'packages':{'nltk':__import__('nltk').__version__,'spacy':spacy.__version__},'recovered_C86_gold_count':14}
 dump(a.run/'manifest.json',manifest)
 olddigest=sha(ROOT/'data/SemEval2010.zip');cache=ROOT/'.cache/full_pos'/hashlib.sha256((olddigest+spacy.__version__+'3.7.1rulesents_no_stemming').encode()).hexdigest()[:16]
 parsedmap={};df=Counter();stop=spacy.lang.en.stop_words.STOP_WORDS;nlp=None
 for ident,text in rows:
  p=cache/(ident+'.json')
  if p.exists():parsed=json.loads(p.read_text())
  else:
   if nlp is None:nlp=spacy.load('en_core_web_sm',disable=['ner','parser','lemmatizer']);nlp.add_pipe('sentencizer')
   doc=nlp(text);parsed=[[(t.text,t.pos_) for t in sent] for sent in doc.sents]
  parsedmap[ident]=parsed;m=load_model(pke.unsupervised.TfIdf,parsed,'en',stop);df.update(m.candidates.keys())
 df['--NB_DOC--']=len(rows)
 records=[];ref=yake.KeywordExtractor(lan='en',n=3,top=10,dedupLim=.8,dedupFunc='leve',windowsSize=1)
 historical={k:load_yake('0.3.0')(lan='en',n=3,top=10,dedupLim=.8,windowsSize=w) for k,w in [('YAKE-0.3.0-window1',1),('YAKE-0.3.0-default-window2',2)]}
 begin=time.perf_counter()
 with (a.run/'predictions.jsonl').open('w') as output:
  for i,(ident,text) in enumerate(rows):
   for method in METHODS:
    if method=='YAKE-package':result=ref.extract_keywords(text)
    elif method=='RAKE-local':result=rake(text,stop)
    elif method=='Independent-reconstruction':result,_=extract(text,Config(),collect_trace=False)
    elif method in historical:result=[(p,float(s)) for s,p in historical[method].extract_keywords(text)]
    else:
     cls={'TextRank-PKE':pke.unsupervised.TextRank,'TF-IDF-PKE':pke.unsupervised.TfIdf,'SingleRank-PKE':pke.unsupervised.SingleRank}[method]
     m=load_model(cls,parsedmap[ident],'en',stop)
     if method=='TF-IDF-PKE':m.candidate_weighting(df=dict(df))
     else:m.candidate_weighting(window=2 if method=='TextRank-PKE' else 10,pos={'NOUN','PROPN','ADJ'})
     result=m.get_n_best(n=10,redundancy_removal=False)
    pred={stem(p) for p,s in result};hits=len(pred&gold[ident]);P=hits/10;R=hits/len(gold[ident]);F=2*hits/(10+len(gold[ident]))
    record={'dataset':'SemEval2010-official-stemmed','document_id':ident,'method':method,'precision':P,'recall':R,'f1':F,'hits':hits,'gold_count':len(gold[ident]),'returned':len(result)}
    output.write(json.dumps({'metrics':record,'predictions':result},ensure_ascii=False)+'\n');output.flush();records.append(record)
   if (i+1)%25==0 or i+1==len(rows):print('SemEval244 sensitivity',i+1,'/',len(rows),flush=True)
 summary={}
 for method in METHODS:
  group=[r for r in records if r['method']==method];summary[method]={k:float(np.mean([r[k] for r in group])) for k in ['precision','recall','f1','hits','gold_count','returned']}
 dump(a.run/'summary.json',summary)
 with (a.run/'per_document.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 manifest.update(status='complete',records=len(records),elapsed_seconds=time.perf_counter()-begin);dump(a.run/'manifest.json',manifest)
 print('COMPLETE separate SemEval244 stemmed sensitivity',len(records),flush=True)
if __name__=='__main__':main()
