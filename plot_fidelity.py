"""Readable audit figures from completed follow-up evidence; PNG and SVG exports."""
import argparse,json,os,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/readme_figures'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from full_comparison import PUBLISHED
DATASETS=['SemEval2010','Schutz2008','500N-KPCrowd','WICC']
INK='#172b4d';BG='#f8fafc'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})
def header(fig,title,subtitle,foot):
 fig.text(.035,.965,title,fontsize=23,weight='bold',va='top');fig.text(.035,.91,subtitle,fontsize=12,color='#53647d',va='top');fig.text(.035,.025,foot,fontsize=10,color='#53647d')
def save(fig,name,out):
 fig.savefig(out/(name+'.png'),dpi=180);svg=out/(name+'.svg');fig.savefig(svg);svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().split('\n')));plt.close(fig)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=ROOT/'results/fidelity/20261010_audit');a=ap.parse_args();a.run=a.run.resolve();out=ROOT/'assets/figures';out.mkdir(exist_ok=True)
 load=lambda s:json.loads((a.run/s/'summary.json').read_text())
 core=load('core');history=load('history');early=load('early_releases')
 methods=['without-WCase','without-WPosition','without-WFreq','without-WRel','without-WSpread']
 values=np.array([[(core[d][m]['f1']-core[d]['Independent-baseline']['f1'])*100 for d in DATASETS] for m in methods])
 fig,ax=plt.subplots(figsize=(12,7));fig.subplots_adjust(left=.30,right=.96,top=.75,bottom=.20)
 ax.imshow(values,cmap='RdBu',norm=TwoSlopeNorm(vmin=-6,vcenter=0,vmax=6),aspect='auto')
 ax.set_xticks(range(4),DATASETS);ax.xaxis.tick_top();ax.tick_params(length=0,pad=14);ax.set_yticks(range(5),['Remove casing','Remove position','Remove frequency','Remove relatedness','Remove sentence spread'])
 for i in range(5):
  for j in range(4):ax.text(j,i,f'{values[i,j]:+.2f} pp',ha='center',va='center',fontsize=15,weight='bold',color='white' if abs(values[i,j])>3.5 else INK)
 ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True);ax.grid(which='minor',color=BG,lw=4);ax.tick_params(which='minor',length=0)
 header(fig,'Does each feature help across all four datasets?','F1 change after removing one feature  •  blue / + = removal helps  •  red / − = removal hurts','Baseline = independent printed-equation reconstruction. 3,614 paired documents. Effects are exploratory; no ablation is promoted as a validated new method.')
 fig.text(.30,.115,'Compare each column to its own full-model baseline.',fontsize=13,weight='bold');save(fig,'all_dataset_ablations',out)
 rows=[('Published Table 1',None,None),('YAKE 0.2.0 · window 1','early_releases','YAKE-0.2.0-window1'),('YAKE 0.2.0 · window 2','early_releases','YAKE-0.2.0-window2'),('YAKE 0.2.4 · window 1','early_releases','YAKE-0.2.4-window1'),('YAKE 0.2.4 · window 2','early_releases','YAKE-0.2.4-window2'),('YAKE 0.3.0 · window 1','history','YAKE-0.3.0-window1'),('YAKE 0.3.0 · window 2','history','YAKE-0.3.0-default-window2'),('YAKE 0.4.8 · window 1','history','YAKE-current-window1'),('YAKE 0.4.8 · window 2','history','YAKE-current-window2')]
 vals=np.array([[PUBLISHED[d][0][2] if family is None else (early if family=='early_releases' else history)[d][method]['f1'] for d in DATASETS] for label,family,method in rows])
 fig,ax=plt.subplots(figsize=(12,9));fig.subplots_adjust(left=.32,right=.96,top=.77,bottom=.17)
 ax.imshow(vals,cmap='Blues',vmin=0,vmax=max(.18,float(vals.max())),aspect='auto');ax.set_xticks(range(4),DATASETS);ax.xaxis.tick_top();ax.set_yticks(range(len(rows)),[r[0] for r in rows]);ax.tick_params(length=0,pad=12)
 for i in range(len(rows)):
  for j in range(4):ax.text(j,i,f'{vals[i,j]:.4f}',ha='center',va='center',fontsize=14,color='white' if vals[i,j]>.11 else INK)
 ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,len(rows),1),minor=True);ax.grid(which='minor',color=BG,lw=3);ax.tick_params(which='minor',length=0)
 header(fig,'Historical releases: recovered code, measured differences','Macro F1 @ 10  •  each row fixes the source version and neighbor window','Historical sources use current dependencies; exact paper executables remain unidentified.\nPrimary SemEval: 243 nonempty-gold pairs. Values rounded to four decimals.')
 fig.text(.32,.095,'Source-equivalent families: 0.2.0 / 0.2.1 / 0.2.2 and 0.3.0 / 0.3.2.',fontsize=12,weight='bold');save(fig,'historical_release_comparison',out)
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 provenance={'generator_sha256':digest(Path(__file__)),'input_sha256':{str((a.run/s/'summary.json').relative_to(ROOT)):digest(a.run/s/'summary.json') for s in ['core','history','early_releases']},'published_values_source':'full_comparison.py:PUBLISHED; ECIR 2018 Table 1','published_config_script_sha256':digest(ROOT/'full_comparison.py'),'output_sha256':{name+'.'+ext:digest(out/(name+'.'+ext)) for name in ['all_dataset_ablations','historical_release_comparison'] for ext in ['png','svg']}}
 (out/'fidelity_manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print('Saved audit heatmaps (PNG + SVG) and source/output hashes.')
if __name__=='__main__':main()
