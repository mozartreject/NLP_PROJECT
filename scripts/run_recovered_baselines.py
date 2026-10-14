"""Execute recovered Hasan C++ baselines with a declared modern POS bridge.
These sources do not encode ECIR's complete settings; no exact-executable claim.
"""
import argparse,csv,hashlib,json,re,shutil,subprocess,time,urllib.request,zipfile
from pathlib import Path
import spacy
from scripts.fidelity_experiments import ROOT,load_rows,score,dump,sha
CACHE=ROOT/'.cache/recovered_cpp'
ARCHIVE_URL='https://web.archive.org/web/20210425074158id_/http://www.hlt.utdallas.edu/~saidul/code/Keyphrase_Extractor-1.0.zip'

def prepare():
 CACHE.mkdir(parents=True,exist_ok=True);path=CACHE/'Keyphrase_Extractor-1.0.zip'
 if not path.exists():
  with urllib.request.urlopen(ARCHIVE_URL,timeout=60) as response:path.write_bytes(response.read())
 assert sha(path)=='6f051a4aeeaa49c96ff27f3a889666886a7b32596c18695f4b90f8407f8a0016'
 audit={'archive_url':ARCHIVE_URL,'archive_sha256':sha(path),'compiler_version':subprocess.check_output(['g++','--version'],text=True),'patches':['TextRank: rename identifier ratio to selection_ratio (modern libc++ name collision)','All methods: redirect restored console output to /dev/null instead of /dev/tty (noninteractive execution)'],'sources':{}}
 with zipfile.ZipFile(path) as z:
  for method in ['TextRank','SingleRank','TfIdf']:
   folder=CACHE/method;folder.mkdir(exist_ok=True);source=z.read(f'{method}/{method}.cpp');text=source.decode()
   if method=='TextRank':text=re.sub(r'\bratio\b','selection_ratio',text)
   text=text.replace('freopen("/dev/tty","w",stdout)','freopen("/dev/null","w",stdout)')
   patched=folder/(method+'.cpp');patched.write_text(text)
   exe=folder/method
   subprocess.run(['g++','-O2','-std=c++98',str(patched),'-o',str(exe)],check=True,capture_output=True,text=True)
   audit['sources'][method]={'original_sha256':hashlib.sha256(source).hexdigest(),'patched_sha256':sha(patched),'binary_sha256':sha(exe)}
 dump(CACHE/'source_audit.json',audit);return audit

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--limit',type=int,default=0);a=ap.parse_args();audit=prepare();a.run.mkdir(parents=True,exist_ok=True)
 manifest={'status':'running','source_audit':audit,'script_sha256':sha(Path(__file__)),'limit':a.limit,'POS_bridge':'Cached spaCy universal tags mapped NOUN→NN, PROPN→NNP, ADJ→JJ; other tags→XX. This is not the historical Stanford tagger.','settings':{'TextRank':{'ratio':.33,'window':2,'iterations':20},'SingleRank':{'top':10,'window':10,'iterations':20},'TfIdf':{'top':10}},'selection':'Raw source output order, then discard >3-word phrases, then first 10; no invented ranking scores. TextRank output is document order, not a sorted phrase-score list.','datasets':{}}
 dump(a.run/'manifest.json',manifest);records=[];summaries={}
 with (a.run/'predictions.jsonl').open('w') as f:
  for dataset in ['500N-KPCrowd','SemEval2010','Schutz2008','WICC']:
   rows,digest,lang=load_rows(dataset,a.limit);oldhash=sha(ROOT/'data/SemEval2010.zip') if dataset=='SemEval2010' else digest
   key=hashlib.sha256((oldhash+spacy.__version__+('3.7.1' if lang=='en' else '3.7.0')+'rulesents_no_stemming').encode()).hexdigest()[:16]
   poscache=ROOT/'.cache/full_pos'/key;inputdir=CACHE/dataset/'input';inputdir.mkdir(parents=True,exist_ok=True);ids=[]
   for ident,text,gold in rows:
    parsed=json.loads((poscache/(ident+'.json')).read_text());parts=[]
    for sent in parsed:
     parts.append(' '.join(token.replace(' ','_')+'_'+{'NOUN':'NN','PROPN':'NNP','ADJ':'JJ'}.get(pos,'XX') for token,pos in sent if token.strip()))
    (inputdir/(ident+'.txt')).write_text('\n'.join(parts)+'\n');ids.append(ident+'.txt')
   listing=CACHE/dataset/'files.txt';listing.write_text('\n'.join(ids)+'\n');summaries[dataset]={};manifest['datasets'][dataset]={'documents':len(rows),'archive_sha256':digest}
   for method in ['TextRank','SingleRank','TfIdf']:
    out=CACHE/dataset/method;out.mkdir(exist_ok=True);params=CACHE/dataset/(method+'.params')
    entries=[f'Input_file_list={listing}','Gold_standard_file_list=',f'Input_file_directory={inputdir}/','Gold_standard_file_directory=',f'Output_file_directory={out}/']
    entries += ['Ratio=0.33','Window_size=2'] if method=='TextRank' else ['Keyphrases_per_file=10','Window_size=10'] if method=='SingleRank' else ['Keyphrases_per_file=10']
    params.write_text('\n'.join(entries)+'\n');begin=time.perf_counter()
    print(dataset,method,'executing',len(rows),'documents',flush=True)
    completed=subprocess.run([str(CACHE/method/method),str(params)],capture_output=True,text=True,timeout=1200)
    elapsed=time.perf_counter()-begin
    (a.run/(dataset+'_'+method+'_console.txt')).write_text(completed.stdout+completed.stderr)
    if completed.returncode:raise RuntimeError(method+' failed: '+completed.stderr[:1000])
    group=[]
    for ident,text,gold in rows:
     path=out/(ident+'.txt.phrases');assert path.exists(),path
     raw=[s.strip() for s in path.read_text().splitlines() if s.strip()]
     phrases=[s for s in raw if len(s.split())<=3][:10];p,r,F=score(phrases,gold)
     record=dict(dataset=dataset,document_id=ident,method=method+'-recovered-modernPOS',precision=p,recall=r,f1=F,returned=len(phrases),raw_returned=len(raw),discarded_over3=sum(len(s.split())>3 for s in raw))
     f.write(json.dumps({'metrics':record,'predictions':[[s,0.] for s in phrases],'scores_available':False},ensure_ascii=False)+'\n');f.flush();records.append(record);group.append(record)
    summaries[dataset][method+'-recovered-modernPOS']={k:sum(r[k] for r in group)/len(group) for k in ['precision','recall','f1','returned','raw_returned','discarded_over3']};summaries[dataset][method+'-recovered-modernPOS']['batch_seconds']=elapsed
    dump(a.run/'summary.json',summaries);dump(a.run/'manifest.json',manifest)
    print(dataset,method,'F1',round(summaries[dataset][method+'-recovered-modernPOS']['f1'],4),flush=True)
 with (a.run/'per_document.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 manifest.update(status='complete',records=len(records));dump(a.run/'manifest.json',manifest);dump(a.run/'summary.json',summaries)
 print('COMPLETE recovered C++',len(records),flush=True)
if __name__=='__main__':main()
