"""Inspect latest complete experiment and export a labeled comparison chart."""
import csv
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

runs=sorted(p for p in (ROOT/'results/engineering').iterdir() if p.is_dir() and (p/'summary.json').exists())
if not runs: raise SystemExit('Run python run_replication.py first')
run=runs[-1]
manifest=json.loads((run/'manifest.json').read_text())
if manifest['status']!='complete': raise SystemExit('Latest run is incomplete')
summary=json.loads((run/'summary.json').read_text())
trace=json.loads((run/'sample_trace.json').read_text())
for field in ['features','candidates','decisions']:
    rows=trace[field]
    if rows:
        with (run/(field+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
fig,ax=plt.subplots(figsize=(10,5))
names=list(summary);values=[summary[n]['f1'] for n in names]
bars=ax.barh(names,values,color=['#4564c6','#26a689']+['#98a7c3']*(len(names)-2))
ax.invert_yaxis();ax.set_xlabel('Mean per-document F1 (case-insensitive exact match)')
ax.set_title(f"500N-KPCrowd: {len(manifest['document_ids'])} documents; k={manifest['config']['top_k']}")
ax.set_xlim(0,max(values)*1.25)
for bar,value in zip(bars,values):ax.text(value+.001,bar.get_y()+bar.get_height()/2,f'{value:.4f}',va='center')
fig.tight_layout();fig.savefig(run/'comparison.png',dpi=180);plt.close(fig)
print((run/'REPORT.md').read_text())
print('Trace example:',trace['document_id'])
print('Word types:',len(trace['features']),'Candidates:',len(trace['candidates']))
print('Evidence folder:',run)
