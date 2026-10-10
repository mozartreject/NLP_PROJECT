"""Local median-length example traces for every dataset; includes source text."""
import csv,hashlib,json
from pathlib import Path
import spacy,yake
from spacy.lang.es.stop_words import STOP_WORDS
from yake.datarepresentation import DataCore
from full_comparison import DATASETS,load_dataset,dump,normalize
from replication.core import Config,extract
ROOT=Path(__file__).resolve().parent

def table(path,rows):
    if rows:
        with path.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

for dataset in DATASETS:
    rows,digest,lang=load_dataset(dataset)
    ident,text,gold=sorted(rows,key=lambda r:(len(r[1].split()),r[0]))[len(rows)//2]
    out=ROOT/'results/expanded_walkthrough'/dataset;out.mkdir(parents=True,exist_ok=True)
    dump(out/'00_audit.json',{'dataset':dataset,'documents':len(rows),'archive_sha256':digest,'sample_id':ident,'selection':'median whitespace-token length; no selection by result quality','training':'none'})
    (out/'01_document.txt').write_text(text)
    model_version='3.7.1' if lang=='en' else '3.7.0'
    cache_id=hashlib.sha256((digest+spacy.__version__+model_version+'rulesents_no_stemming').encode()).hexdigest()[:16]
    pos=ROOT/'.cache/full_pos'/cache_id/(ident+'.json')
    if pos.exists():dump(out/'02_pos_sentences.json',json.loads(pos.read_text()))
    independent,trace=extract(text,Config(),stopwords=STOP_WORDS if lang=='es' else None)
    dump(out/'03_independent_trace.json',trace)
    reference=yake.KeywordExtractor(lan=lang,n=3,top=10,dedupLim=.8,dedupFunc='leve',windowsSize=1)
    dc=DataCore(text=text,stopword_set=reference.stopword_set,windowsSize=1,n=3)
    dc.build_single_terms_features();dc.build_mult_terms_features()
    table(out/'04_package_word_features.csv',[{'word':t.unique_term,'tf':t.tf,'WCase':float(t.WCase),'WPosition':float(t.WPos),'WFreq':float(t.WFreq),'WRel':float(t.WRel),'WSpread':float(t.WSpread),'H':float(t.H)} for t in dc.terms.values()])
    table(out/'05_package_candidates.csv',[{'phrase':c.kw,'tf':c.tf,'size':c.size,'eligible':bool(c.isValid()),'H':float(c.H)} for c in dc.candidates.values()])
    predictions=[]
    for method,result in [('YAKE-package',reference.extract_keywords(text)),('Independent-reconstruction',independent)]:
        for rank,(phrase,score) in enumerate(result,1):predictions.append({'method':method,'rank':rank,'phrase':phrase,'score':float(score),'exact_gold_match':normalize(phrase) in gold})
    table(out/'06_ranked_predictions.csv',predictions);dump(out/'07_gold.json',sorted(gold))
    print(dataset,ident,'trace:',out,flush=True)
