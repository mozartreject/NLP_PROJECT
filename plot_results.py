"""Generate presentation figures from the completed experiment, not invented scores."""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from evaluate import ROOT

rows = json.loads((ROOT / 'results/full/summary.json').read_text())
x = np.arange(len(rows))
fig, ax = plt.subplots(figsize=(8,4.5))
for offset, key, label in [(-.25,'precision_at_10','P@10'),(0,'recall_at_10','Recall@10'),(.25,'f1_at_10','Mean F1@10')]:
    ax.bar(x+offset,[r[key] for r in rows],width=.25,label=label)
ax.set_xticks(x,[r['method'] for r in rows])
ax.set_ylim(0,max(r['precision_at_10'] for r in rows)*1.3)
ax.set_ylabel('Score'); ax.set_title('500N-KPCrowd: 500 documents, top 10 phrases')
ax.legend(); fig.tight_layout()
fig.savefig(ROOT / 'results/full/comparison.png',dpi=180)
print('Saved results/full/comparison.png')
