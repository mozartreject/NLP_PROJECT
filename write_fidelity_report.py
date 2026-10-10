"""Build the final fidelity report from verified aggregate evidence."""
import argparse,json
from pathlib import Path
from fidelity_experiments import ROOT
DATASETS=['SemEval2010','Schutz2008','500N-KPCrowd','WICC']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=ROOT/'results/fidelity/20261010_audit');a=ap.parse_args();load=lambda sub:json.loads((a.run/sub/'summary.json').read_text())
 core=load('core');history=load('history');early=load('early_releases');baselines=load('baselines');cpp=load('recovered_cpp');secondary=load('semeval244_stemmed');validation=json.loads((a.run/'EVIDENCE_VALIDATION.json').read_text())
 rows=['# Replication fidelity audit — completed follow-up experiments','',
 '**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**','',
 'The original four-dataset comparison remains unchanged. This audit investigates its documented gaps using recovered historical sources, all-dataset ablations, controlled interventions and a separate original-task annotation evaluation. It does not identify the exact publication executable or retroactively tune a configuration to the paper’s scores.','',
 f"**New document/configuration evaluations: {validation['additional_evaluations']:,}.** Original archived comparison: {validation['archived_main_evaluations']:,}. Every saved primary metric was independently recomputed, and all 1,952 supplementary stemmed-evaluation records were checked separately.",'',
 '## What the new experiments establish','',
 f"- Relatedness removal changes news F1 from {core['500N-KPCrowd']['Independent-baseline']['f1']:.4f} to {core['500N-KPCrowd']['without-WRel']['f1']:.4f}, while WICC changes from {core['WICC']['Independent-baseline']['f1']:.4f} to {core['WICC']['without-WRel']['f1']:.4f}. The feature effect depends on the dataset and this reconstruction.",
 '- Recovered source versions and window settings change the measured results, but the historical runs still do not reproduce the published four-dataset YAKE row. Source recovery alone does not establish original runtime equivalence.',
 '- The original independent reconstruction and current-package baseline retain exactly the same ranked outputs as the archived comparison on every primary document. The audit supplements that evidence rather than silently replacing it.',
 '- The missing SemEval text can be evaluated under original task stemmed labels; its empty Maui gold prevents adding it to the comparable unstemmed primary experiment.','',
 '## Coverage of the previous gaps','',
 '| Gap | Work completed | Remaining boundary |','|---|---|---|',
 '| Historical YAKE | Audited six PyPI releases; executed all three distinct scorer families with windows 1 and 2; directly replayed 0.3.0 and 0.3.2 | Original version, dependency versions and executable settings are not identified |',
 '| Baseline implementations | Recovered and executed cited-page C++ TextRank/SingleRank/TF-IDF and preconference RAKE; pinned and hashed sources | Original tagged inputs and parameter files missing; modern POS bridge and declared output policy remain |',
 '| Preprocessing / equations | Thirteen one-choice sensitivities across four datasets; default extraction checked against original scorer | Complete interactions and unspecified author choices cannot be inferred from scores |',
 '| SemEval missing document | Identified C-86 and recovered its text; original task has 14 unique stemmed gold phrases; ran separate 244-document evaluation | Maui gold is empty; comparable unstemmed annotations were not recovered |',
 '| Ablation scope | All five feature removals repeated on all four valid primary collections | Exploratory findings, not the original paper’s experiments |',
 '| Significance analysis | Paired two-sided t-tests for P/R/F1, seeded bootstrap intervals and Holm corrections | Original document-level outputs unavailable; original significance arrows cannot be exactly regenerated |',
 '| Error / matching analysis | Annotation lengths/presence proxies, length quartile slices, Spearman associations, plural and Porter matching sensitivities | Diagnostics do not establish causality or replace the exact-match primary metric |','',
 '## Full four-dataset feature ablations','',
 'Values are mean per-document F1. Each feature removal modifies the independent printed-equation reconstruction.','',
 '| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |','|---|---:|---:|---:|---:|']
 for m in ['Independent-baseline','without-WCase','without-WPosition','without-WFreq','without-WRel','without-WSpread']:
  rows.append('| '+m+' | '+' | '.join(f"{core[d][m]['f1']:.4f}" for d in DATASETS)+' |')
 rows+=['','## Controlled reconstruction sensitivities','','Each row changes one declared choice relative to the baseline. No row is selected as a new final model.','','| Choice | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |','|---|---:|---:|---:|---:|']
 for m in core[DATASETS[0]]:
  if m=='Independent-baseline' or m.startswith('without-'):continue
  rows.append('| '+m+' | '+' | '.join(f"{core[d][m]['f1']:.4f}" for d in DATASETS)+' |')
 rows+=['','## Historical YAKE source families','','Historical sources use current pinned dependencies. Byte-identical runtime-file families are recorded in configs/historical_releases.json. PyPI availability does not establish the version used in the paper.','','| Source / window | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |','|---|---:|---:|---:|---:|']
 for data,methods in [(early,list(early[DATASETS[0]])),(history,[m for m in history[DATASETS[0]] if m.startswith('YAKE')])]:
  for m in methods:rows.append('| '+m+' | '+' | '.join(f"{data[d][m]['f1']:.4f}" for d in DATASETS)+' |')
 rows+=['','## Recovered baseline sources','','These runs execute recovered C++ sources with modern universal-to-Penn category mapping. Top-10 retrieval and max-three-word wrapper choices are explicit. TextRank source emits document-order phrases, so its first-ten wrapper is not an identified paper ranking policy.','','| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |','|---|---:|---:|---:|---:|']
 for m in cpp[DATASETS[0]]:rows.append('| '+m+' | '+' | '.join(f"{cpp[d][m]['f1']:.4f}" for d in DATASETS)+' |')
 for m in ['RAKE-2018-Smart-English','RAKE-2018-KEP-stopwords']:
  rows.append('| '+m+' | '+' | '.join(f"{history[d][m]['f1']:.4f}" if m in history[d] else 'Not applicable' for d in DATASETS)+' |')
 rows+=['','The paper’s footnotes repeat the RAKE link for SingleRank/TF-IDF. The cited Hasan page supplies all three graph/statistical implementations, but that does not prove those exact builds/settings generated every paper-table baseline. The C++ programs’ internal micro/plural-tolerant evaluator was bypassed in favor of the project’s common exact document-level metric.','','## Modern PKE candidate-policy effects','','All values use the same primary metric. TF-IDF-native and TF-IDF-no-POS are equivalent in this pinned version and serve as a recorded null control.','','| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |','|---|---:|---:|---:|---:|']
 for m in baselines[DATASETS[0]]:rows.append('| '+m+' | '+' | '.join(f"{baselines[d][m]['f1']:.4f}" for d in DATASETS)+' |')
 rows+=['','## Separate SemEval evaluation with all 244 texts','','C-86 has an empty Maui `.key` file. The original task archive supplies stemmed combined gold annotations for all 244 texts. These results stem predictions wordwise with NLTK Porter, use top 10 and mean document F1, and refit TF-IDF corpus statistics on the selected collection. They must not be mixed with the unstemmed paper-table comparison.','','| Configuration | Precision @ 10 | Recall | Mean document F1 |','|---|---:|---:|---:|']
 for m,v in secondary.items():rows.append(f"| {m} | {v['precision']:.4f} | {v['recall']:.4f} | {v['f1']:.4f} |")
 rows+=['','## Statistics and diagnostic evidence','',
 '- `core/paired_statistics.json`: all ablation and one-choice contrasts for precision, recall and F1, with Holm correction across that suite.','- `history/paired_statistics.json`: source/window/RAKE contrasts against current YAKE, corrected within that suite.','- `baselines/paired_statistics.json`: modern candidate-policy contrasts, corrected within that suite.','- `recovered_paired_statistics.json`: 48 corrected historical-YAKE-versus-recovered-baseline contrasts.','- `matching_sensitivity.csv`: exact/plural/Porter interpretations of frozen archived predictions.','- `length_error_slices.csv`: within-dataset quartiles and descriptive length/F1 correlation.','- `annotation_audit.json`: reference phrase counts, overlength phrases and literal-presence proxies.','- `CASEBOOK.md` / `qualitative_cases.json`: eight explicitly selected median-length and largest-disagreement examples, with exact hits and missed/unmatched phrase evidence.','- `EVIDENCE_VALIDATION.json`: independent metric checks and archived/new baseline equality.','',
 'Two-sided paired tests follow the paper’s comparison design, but these are our rerun outputs. Original significance marks cannot be reproduced without the authors’ per-document outputs. Bootstrap intervals are pointwise; Holm p-values use explicitly stated families. No claim of significance against the paper’s aggregate scores is made.','',
 '## What remains externally unresolved','',
 '1. The authors’ exact YAKE version, complete execution settings and original dependency environment.','2. Original POS-tagged baseline input files, tagger versions, parameter files and output-to-top-10 policy.','3. Comparable unstemmed C-86 gold annotations used for a 244-document exact-match evaluation.','4. Original per-document outputs for all methods and original statistical-test implementation choices.','',
 'Additional parameter sweeps cannot establish those historical facts. They require archived author artifacts or clarification. The work is a substantially stronger, audited experimental reproduction; it is not asserted to be an exact executable recreation.','',
 '## Attribution and reproduction','',
 'See FIDELITY_PROTOCOL.md for source links, adaptations, configurations, metric rules and all reproduction commands. Historical code and datasets remain local; aggregate evidence is committed. The audit adds no supervised training stage.','']
 text='\n'.join(rows);(ROOT/'FIDELITY_REPORT.md').write_text(text);(a.run/'REPORT.md').write_text(text)
 print('Built fidelity report from actual completed results.')
if __name__=='__main__':main()
