"""Regenerate README scientific figures from archived experiment evidence."""
from pathlib import Path
import os, json, hashlib
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'readme_figures'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
OUT = ROOT / 'assets/figures'
OUT.mkdir(parents=True, exist_ok=True)
RUN = ROOT / 'results/expanded/20261009T100336_607448Z'
ABL = ROOT / 'results/engineering/20261009T093634_374606Z'
def read(p): return json.loads(p.read_text())
scores = read(RUN/'summary.json')
config = read(ROOT/'configs/paper_table1.json')
ablation = read(ABL/'summary.json')
intervals = read(ABL/'paired_intervals.json')
datasets = ['SemEval2010','Schutz2008','500N-KPCrowd','WICC']
counts = [243,1231,500,1640]
methods = config['METHODS']
labels = ['YAKE package','TextRank · PKE','TF-IDF · PKE','SingleRank · PKE','RAKE · local','Independent\nreconstruction']
BLUE, GREEN, INK, GRAY, RED = '#2563eb','#087f8c','#172b4d','#8795a8','#c44764'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc','savefig.facecolor':'#f8fafc'})
def frame(fig,title,subtitle,foot):
    fig.text(.04,.965,title,fontsize=23,weight='bold',va='top')
    fig.text(.04,.915,subtitle,fontsize=12,va='top',color='#53647d')
    fig.text(.04,.025,foot,fontsize=10,color='#53647d',va='bottom')
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=180)
    fig.savefig(OUT/(name+'.svg'))
    plt.close(fig)
# 1. An annotated scorecard with per-dataset winners, not a pooled ranking.
fig, ax = plt.subplots(figsize=(12,7.2))
fig.subplots_adjust(left=.24,right=.95,top=.78,bottom=.20)
a = np.array([[scores[d][m]['f1'] for d in datasets] for m in methods])
ax.imshow(a,cmap='Blues',vmin=0,vmax=.18,aspect='auto')
ax.set_xticks(range(4),[f'{d}\n{n:,} documents' for d,n in zip(datasets,counts)],fontsize=12)
ax.xaxis.tick_top(); ax.tick_params(length=0,pad=12)
ax.set_yticks(range(6),labels,fontsize=12)
for j in range(4):
    winner = int(a[:,j].argmax())
    for i in range(6):
        ax.text(j,i,f'{a[i,j]:.4f}',ha='center',va='center',fontsize=15,weight='bold' if i==winner else 'normal',color='white' if a[i,j]>.10 else INK)
    ax.add_patch(Rectangle((j-.47,winner-.46),.94,.92,fill=False,edgecolor='#f5b942',lw=3))
ax.set_xticks(np.arange(-.5,4,1),minor=True); ax.set_yticks(np.arange(-.5,6,1),minor=True)
ax.grid(which='minor',color='#f8fafc',lw=4); ax.tick_params(which='minor',length=0)
frame(fig,'Which method works best on each dataset?','Macro F1 at top 10  •  darker cells = higher score  •  gold outline = highest measured F1 in that column','3,614 documents · 6 configurations · exact normalized matching. Compare methods within each dataset; gold annotations differ across datasets.')
fig.text(.24,.12,'YAKE leads on SemEval and WICC. TF-IDF leads on Schutz and news.',fontsize=13,weight='bold')
save(fig,'benchmark_scorecard')
# 2. Published versus measured paired points, identical axes for all panels.
fig, axes = plt.subplots(2,2,figsize=(13,10))
fig.subplots_adjust(left=.14,right=.97,top=.80,bottom=.13,wspace=.48,hspace=.48)
for ax,d in zip(axes.flat,datasets):
    old = np.array([row[2] for row in config['PUBLISHED'][d]])
    new = np.array([scores[d][m]['f1'] for m in methods[:5]])
    for i,(p,q) in enumerate(zip(old,new)):
        ax.plot([p,q],[i,i],color='#c6d1df',lw=4,zorder=1)
        ax.text(.184,i,f'{p:.3f} → {q:.3f}',va='center',fontsize=10,color=INK)
    ax.scatter(old,range(5),color=GRAY,s=70,zorder=3)
    ax.scatter(new,range(5),color=BLUE,s=70,zorder=4)
    ax.set_yticks(range(5),['YAKE','TextRank','TF-IDF','SingleRank','RAKE'])
    ax.invert_yaxis(); ax.set_xlim(0,.255); ax.set_xticks([0,.05,.10,.15]); ax.set_xlabel('Macro F1'); ax.grid(axis='x',color='#e0e7ef'); ax.set_title(d,loc='left',weight='bold',pad=16)
frame(fig,'Published results vs our measured results','Read each row: gray = ECIR 2018 Table 1  →  blue = our declared implementation','Descriptive comparison, not proof of improvement: versions, preprocessing and evaluation choices differ. SemEval archive: 243 vs paper’s 244 documents.')
fig.legend(handles=[Line2D([],[],marker='o',color=GRAY,lw=0,label='Published paper'),Line2D([],[],marker='o',color=BLUE,lw=0,label='Our experiment')],loc='upper left',bbox_to_anchor=(.035,.885),ncol=2,frameon=False)
save(fig,'published_vs_measured')
# 3. Explain independent reconstruction versus the package across all metrics.
fig, axes = plt.subplots(1,3,figsize=(13,6.8))
fig.subplots_adjust(left=.15,right=.97,top=.74,bottom=.20,wspace=.22)
for ax,metric,title in zip(axes,['precision','recall','f1'],['Precision @ 10','Recall','Macro F1']):
    for i,d in enumerate(datasets):
        p=scores[d]['YAKE-package'][metric]; q=scores[d]['Independent-reconstruction'][metric]
        ax.plot([p,q],[i,i],color='#c6d1df',lw=3)
        ax.scatter(p,i,color=BLUE,s=65,zorder=3); ax.scatter(q,i,color=GREEN,marker='D',s=60,zorder=3)
        ax.text(p,i-.14,f'{p:.3f}',ha='center',va='bottom',color=BLUE,fontsize=10)
        ax.text(q,i+.14,f'{q:.3f}',ha='center',va='top',color=GREEN,fontsize=10)
    ax.set_ylim(3.65,-.65); ax.set_xlim(-.015,.46 if metric=='precision' else .33 if metric=='recall' else .18)
    ax.set_yticks(range(4),datasets if metric=='precision' else ['']*4)
    ax.set_title(title,loc='left',weight='bold'); ax.grid(axis='x',color='#e0e7ef'); ax.set_xlabel('Score')
frame(fig,'Two YAKE implementations, different behavior','Our printed-equation reconstruction and the packaged implementation do not produce identical rankings.','Precision counts correct top-10 slots; recall counts recovered gold keywords. F1 is averaged per document, not computed from these mean P/R values.')
fig.legend(handles=[Line2D([],[],marker='o',color=BLUE,lw=0,label='YAKE package'),Line2D([],[],marker='D',color=GREEN,lw=0,label='Independent reconstruction')],loc='upper left',bbox_to_anchor=(.035,.865),ncol=2,frameon=False)
save(fig,'implementation_metrics')
# 4. Paired feature-removal effects, reversing archived baseline-minus-ablation intervals.
fig, ax = plt.subplots(figsize=(12,7.3))
fig.subplots_adjust(left=.29,right=.73,top=.76,bottom=.27)
keys=['without-WCase','without-WPosition','without-WFreq','without-WRel','without-WSpread']
names=['Remove casing','Remove position','Remove frequency','Remove relatedness','Remove sentence spread']
for i,k in enumerate(keys):
    row=intervals[k]; delta=-row['mean_difference']
    lo,hi=[-x for x in reversed(row['paired_bootstrap_95_percent_interval'])]
    assert lo <= delta <= hi
    color=GREEN if delta>0 else RED
    ax.errorbar(delta*100,i,xerr=np.array([[delta-lo],[hi-delta]])*100,fmt='o',color=color,ecolor=color,capsize=6,markersize=9,lw=3)
    ax.text(2.1,i,f'{delta*100:+.2f} pp',va='center',fontsize=12,weight='bold',color=color)
    ax.text(3.6,i,f'{ablation[k]["f1"]:.4f}',va='center',fontsize=12)
ax.axvline(0,color=INK,lw=1.4); ax.set_xlim(-6,1.8); ax.set_ylim(4.55,-.55)
ax.set_yticks(range(5),names); ax.set_xlabel('Change in macro F1 after removing the feature (percentage points)',labelpad=14)
ax.grid(axis='x',color='#e0e7ef'); ax.text(2.1,-.85,'Change',weight='bold'); ax.text(3.6,-.85,'F1',weight='bold')
frame(fig,'Which feature matters most in our news experiment?','500N-KPCrowd · 500 paired documents · full reconstruction baseline F1 = 0.1506','Points = ablation minus full model; whiskers = paired bootstrap 95% intervals (2,000 resamples). Exploratory interventions; not original-paper ablations.')
fig.text(.29,.12,'← Removing the feature hurts',fontsize=12,color=RED,weight='bold')
fig.text(.64,.12,'Removal helps →',fontsize=12,color=GREEN,weight='bold')
save(fig,'feature_ablations')
inputs=[RUN/'summary.json',ROOT/'configs/paper_table1.json',ABL/'summary.json',ABL/'paired_intervals.json']
(OUT/'manifest.json').write_text(json.dumps({'generator':'generate_readme_figures.py','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'figures':['benchmark_scorecard','published_vs_measured','implementation_metrics','feature_ablations'],'metric':'Mean per-document F1 at top 10; P/R as labelled'},indent=2)+'\n')
print('Generated four figures, each in PNG and SVG, from archived evidence.')
