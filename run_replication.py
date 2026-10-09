"""Immutable, fail-fast paired experiments with complete provenance and a sample trace."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import yake
from evaluate import ROOT, load_data, metrics
from replication.core import Config, extract

def save(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'configs/paper.json')
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--ablations',action='store_true')
    args=parser.parse_args()
    if args.limit<0: parser.error('limit must be nonnegative')
    settings=json.loads(args.config.read_text())
    config=Config(**{k:v for k,v in settings.items() if k not in ('bootstrap_samples','seed')})
    rows,digest=load_data(); rows=rows[:args.limit] if args.limit else rows
    run=ROOT/'results'/'engineering'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    run.mkdir(parents=True,exist_ok=False)
    reference=yake.KeywordExtractor(lan='en',n=config.max_ngram,top=config.top_k,
                    dedupLim=config.dedup_threshold,dedupFunc='leve',windowsSize=config.window)
    methods=['paper-equations','YAKE-package']
    if args.ablations: methods += ['without-'+f for f in ['WCase','WPosition','WFreq','WRel','WSpread']]
    records=[]; predictions=[]
    started=time.perf_counter()
    save(run/'manifest.json',{'status':'running','config':settings,'dataset_sha256':digest,'document_ids':[r[0] for r in rows],
        'python':sys.version,'platform':platform.platform(),'packages':{p:importlib.metadata.version(p) for p in ['yake','numpy','scikit-learn']},
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [ROOT/'replication/core.py',ROOT/'run_replication.py',ROOT/'evaluate.py']},
        'scope':'500N selected-benchmark reproduction; independent printed-equation reconstruction with documented safeguards',
        'training':'none; reference and independent YAKE are unsupervised single-document methods',
        'matching':'casefold + whitespace exact; P@k denominator k; per-document macro F1'})
    try:
        for index,(ident,text,gold) in enumerate(rows):
            for method in methods:
                begin=time.perf_counter()
                if method=='YAKE-package':
                    result=reference.extract_keywords(text)
                    if text.strip() and not result: raise RuntimeError('Reference returned no keywords: '+ident)
                else:
                    result,trace=extract(text,config,method.removeprefix('without-') if method.startswith('without-') else None)
                    if index==0 and method=='paper-equations':
                        save(run/'sample_trace.json',dict(document_id=ident,text=text,gold=sorted(gold),**trace))
                elapsed=time.perf_counter()-begin
                if any(not np.isfinite(score) for phrase,score in result): raise RuntimeError('Nonfinite keyword score')
                phrases=[p for p,s in result]; p,r,f=metrics(phrases,gold,config.top_k)
                records.append(dict(document_id=ident,method=method,precision=p,recall=r,f1=f,seconds=elapsed,returned=len(result)))
                predictions.append(dict(document_id=ident,method=method,keywords=result,gold=sorted(gold)))
            if (index+1)%50==0: print(f'Processed {index+1}/{len(rows)}',flush=True)
        with (run/'per_document.csv').open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
        save(run/'predictions.json',predictions)
        summary={}
        for method in methods:
            group=[r for r in records if r['method']==method]
            averages={key:float(np.mean([r[key] for r in group])) for key in ['precision','recall','f1','seconds','returned']}
            p,r=averages['precision'],averages['recall']
            averages['f1_of_macro_precision_recall']=2*p*r/(p+r) if p+r else 0
            summary[method]=averages
        rng=np.random.default_rng(settings['seed']); intervals={}
        base=np.array([r['f1'] for r in records if r['method']=='paper-equations'])
        for method in methods[1:]:
            other=np.array([r['f1'] for r in records if r['method']==method]); differences=base-other
            sampled=np.array([rng.choice(differences,len(differences),replace=True).mean() for _ in range(settings['bootstrap_samples'])])
            intervals[method]={'contrast':'paper-equations minus '+method,'mean_difference':float(differences.mean()),
                'paired_bootstrap_95_percent_interval':np.quantile(sampled,[.025,.975]).tolist()}
        save(run/'summary.json',summary); save(run/'paired_intervals.json',intervals)
        manifest=json.loads((run/'manifest.json').read_text()); manifest.update(status='complete',elapsed_seconds=time.perf_counter()-started)
        save(run/'manifest.json',manifest)
        report=['# Selected-benchmark experimental reproduction','',f'Documents: {len(rows)}. No training phase.','',
            '| Method | P@10 | Recall | Macro F1 | Mean seconds/document |','|---|---:|---:|---:|---:|']
        for method,s in summary.items():
            report.append(f"| {method} | {s['precision']:.4f} | {s['recall']:.4f} | {s['f1']:.4f} | {s['seconds']:.5f} |")
            print(method, 'F1=',round(s['f1'],4))
        report += ['', 'Scores do not establish exact agreement with the 2018 paper. See ENGINEERING_PROTOCOL.md for preprocessing and equation ambiguities.',
            'Bootstrap intervals compare matched document F1 values; they are not the paper\'s paired t-test.',
            'Ablations are defined engineering interventions, not claimed original-paper experiments.']
        (run/'REPORT.md').write_text('\n'.join(report)+'\n')
        print('Evidence:',run)
    except Exception as exc:
        save(run/'failure.json',{'type':type(exc).__name__,'message':str(exc)})
        raise

if __name__=='__main__': main()
