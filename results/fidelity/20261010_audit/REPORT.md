# Replication fidelity audit — completed follow-up experiments

**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**

The original four-dataset comparison remains unchanged. This audit investigates its documented gaps using recovered historical sources, all-dataset ablations, controlled interventions and a separate original-task annotation evaluation. It does not identify the exact publication executable or retroactively tune a configuration to the paper’s scores.

**New document/configuration evaluations: 144,872.** Original archived comparison: 21,684. Every saved primary metric was independently recomputed, and all 1,952 supplementary stemmed-evaluation records were checked separately.

## What the new experiments establish

- Relatedness removal changes news F1 from 0.1506 to 0.1027, while WICC changes from 0.0986 to 0.1175. The feature effect depends on the dataset and this reconstruction.
- Recovered source versions and window settings change the measured results, but the historical runs still do not reproduce the published four-dataset YAKE row. Source recovery alone does not establish original runtime equivalence.
- The original independent reconstruction and current-package baseline retain exactly the same ranked outputs as the archived comparison on every primary document. The audit supplements that evidence rather than silently replacing it.
- The missing SemEval text can be evaluated under original task stemmed labels; its empty Maui gold prevents adding it to the comparable unstemmed primary experiment.

## Coverage of the previous gaps

| Gap | Work completed | Remaining boundary |
|---|---|---|
| Historical YAKE | Audited six PyPI releases; executed all three distinct scorer families with windows 1 and 2; directly replayed 0.3.0 and 0.3.2 | Original version, dependency versions and executable settings are not identified |
| Baseline implementations | Recovered and executed cited-page C++ TextRank/SingleRank/TF-IDF and preconference RAKE; pinned and hashed sources | Original tagged inputs and parameter files missing; modern POS bridge and declared output policy remain |
| Preprocessing / equations | Thirteen one-choice sensitivities across four datasets; default extraction checked against original scorer | Complete interactions and unspecified author choices cannot be inferred from scores |
| SemEval missing document | Identified C-86 and recovered its text; original task has 14 unique stemmed gold phrases; ran separate 244-document evaluation | Maui gold is empty; comparable unstemmed annotations were not recovered |
| Ablation scope | All five feature removals repeated on all four valid primary collections | Exploratory findings, not the original paper’s experiments |
| Significance analysis | Paired two-sided t-tests for P/R/F1, seeded bootstrap intervals and Holm corrections | Original document-level outputs unavailable; original significance arrows cannot be exactly regenerated |
| Error / matching analysis | Annotation lengths/presence proxies, length quartile slices, Spearman associations, plural and Porter matching sensitivities | Diagnostics do not establish causality or replace the exact-match primary metric |

## Full four-dataset feature ablations

Values are mean per-document F1. Each feature removal modifies the independent printed-equation reconstruction.

| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |
|---|---:|---:|---:|---:|
| Independent-baseline | 0.0608 | 0.1157 | 0.1506 | 0.0986 |
| without-WCase | 0.0579 | 0.1296 | 0.1616 | 0.0809 |
| without-WPosition | 0.0670 | 0.0802 | 0.1408 | 0.1206 |
| without-WFreq | 0.0521 | 0.1122 | 0.1552 | 0.0811 |
| without-WRel | 0.0625 | 0.1138 | 0.1027 | 0.1175 |
| without-WSpread | 0.0608 | 0.1157 | 0.1524 | 0.0971 |

## Controlled reconstruction sensitivities

Each row changes one declared choice relative to the baseline. No row is selected as a new final model.

| Choice | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |
|---|---:|---:|---:|---:|
| Tokenizer-special-chars | 0.0592 | 0.1142 | 0.1420 | 0.0983 |
| Author-stopwords | 0.0739 | 0.1505 | 0.1588 | 0.0988 |
| Casing-natural-log | 0.0581 | 0.1078 | 0.1461 | 0.1052 |
| Position-natural-log | 0.0631 | 0.0990 | 0.0989 | 0.1224 |
| Frequency-nonstopwords | 0.0699 | 0.1161 | 0.1461 | 0.1267 |
| Relatedness-without-PLPR | 0.0629 | 0.1189 | 0.1399 | 0.1068 |
| Position-unique-sentences | 0.0608 | 0.1157 | 0.1500 | 0.0985 |
| Singleton-casing-log1p | 0.0608 | 0.1156 | 0.1473 | 0.0985 |
| Neighbor-window-2 | 0.0599 | 0.1107 | 0.1542 | 0.0940 |
| Casing-one-plus-ln | 0.0608 | 0.1154 | 0.1553 | 0.0987 |
| Internal-stopword-transition | 0.0614 | 0.1163 | 0.1506 | 0.0962 |
| Plural-stripping | 0.0577 | 0.1163 | 0.1496 | 0.0986 |
| Tokenizer-segtok | 0.0653 | 0.1067 | 0.1392 | 0.1161 |

## Historical YAKE source families

Historical sources use current pinned dependencies. Byte-identical runtime-file families are recorded in configs/historical_releases.json. PyPI availability does not establish the version used in the paper.

| Source / window | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |
|---|---:|---:|---:|---:|
| YAKE-0.2.0-window1 | 0.1139 | 0.1014 | 0.0693 | 0.1320 |
| YAKE-0.2.0-window2 | 0.1182 | 0.1033 | 0.0744 | 0.1343 |
| YAKE-0.2.4-window1 | 0.1203 | 0.1332 | 0.0820 | 0.1345 |
| YAKE-0.2.4-window2 | 0.1151 | 0.1319 | 0.0891 | 0.1350 |
| YAKE-current-window1 | 0.1207 | 0.1323 | 0.0762 | 0.1378 |
| YAKE-0.3.0-window1 | 0.1194 | 0.1339 | 0.0826 | 0.1369 |
| YAKE-0.3.2-window1 | 0.1194 | 0.1339 | 0.0826 | 0.1369 |
| YAKE-0.3.0-default-window2 | 0.1166 | 0.1323 | 0.0891 | 0.1371 |
| YAKE-current-window2 | 0.1199 | 0.1337 | 0.0764 | 0.1385 |

## Recovered baseline sources

These runs execute recovered C++ sources with modern universal-to-Penn category mapping. Top-10 retrieval and max-three-word wrapper choices are explicit. TextRank source emits document-order phrases, so its first-ten wrapper is not an identified paper ranking policy.

| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |
|---|---:|---:|---:|---:|
| TextRank-recovered-modernPOS | 0.0490 | 0.0602 | 0.1043 | 0.1057 |
| SingleRank-recovered-modernPOS | 0.0028 | 0.0031 | 0.0754 | 0.0417 |
| TfIdf-recovered-modernPOS | 0.0114 | 0.0123 | 0.0852 | 0.0635 |
| RAKE-2018-Smart-English | 0.0057 | 0.0074 | 0.0668 | Not applicable |
| RAKE-2018-KEP-stopwords | 0.0057 | 0.0073 | 0.0667 | 0.0130 |

The paper’s footnotes repeat the RAKE link for SingleRank/TF-IDF. The cited Hasan page supplies all three graph/statistical implementations, but that does not prove those exact builds/settings generated every paper-table baseline. The C++ programs’ internal micro/plural-tolerant evaluator was bypassed in favor of the project’s common exact document-level metric.

## Modern PKE candidate-policy effects

All values use the same primary metric. TF-IDF-native and TF-IDF-no-POS are equivalent in this pinned version and serve as a recorded null control.

| Configuration | SemEval2010 | Schutz2008 | 500N-KPCrowd | WICC |
|---|---:|---:|---:|---:|
| TextRank-common | 0.0241 | 0.0209 | 0.0495 | 0.0284 |
| TextRank-native | 0.0453 | 0.0390 | 0.0606 | 0.0416 |
| SingleRank-common | 0.0354 | 0.0369 | 0.0687 | 0.0710 |
| SingleRank-native | 0.0471 | 0.0544 | 0.0977 | 0.0792 |
| TF-IDF-common | 0.1078 | 0.1623 | 0.1596 | 0.1121 |
| TF-IDF-native | 0.1055 | 0.1605 | 0.1607 | 0.1127 |
| TF-IDF-no-POS | 0.1055 | 0.1605 | 0.1607 | 0.1127 |

## Separate SemEval evaluation with all 244 texts

C-86 has an empty Maui `.key` file. The original task archive supplies stemmed combined gold annotations for all 244 texts. These results stem predictions wordwise with NLTK Porter, use top 10 and mean document F1, and refit TF-IDF corpus statistics on the selected collection. They must not be mixed with the unstemmed paper-table comparison.

| Configuration | Precision @ 10 | Recall | Mean document F1 |
|---|---:|---:|---:|
| YAKE-package | 0.1926 | 0.1346 | 0.1566 |
| TextRank-PKE | 0.0377 | 0.0257 | 0.0302 |
| TF-IDF-PKE | 0.1545 | 0.1086 | 0.1260 |
| SingleRank-PKE | 0.0570 | 0.0384 | 0.0454 |
| RAKE-local | 0.0082 | 0.0051 | 0.0062 |
| Independent-reconstruction | 0.0902 | 0.0653 | 0.0750 |
| YAKE-0.3.0-window1 | 0.1885 | 0.1323 | 0.1537 |
| YAKE-0.3.0-default-window2 | 0.1848 | 0.1299 | 0.1508 |

## Statistics and diagnostic evidence

- `core/paired_statistics.json`: all ablation and one-choice contrasts for precision, recall and F1, with Holm correction across that suite.
- `history/paired_statistics.json`: source/window/RAKE contrasts against current YAKE, corrected within that suite.
- `baselines/paired_statistics.json`: modern candidate-policy contrasts, corrected within that suite.
- `recovered_paired_statistics.json`: 48 corrected historical-YAKE-versus-recovered-baseline contrasts.
- `matching_sensitivity.csv`: exact/plural/Porter interpretations of frozen archived predictions.
- `length_error_slices.csv`: within-dataset quartiles and descriptive length/F1 correlation.
- `annotation_audit.json`: reference phrase counts, overlength phrases and literal-presence proxies.
- `CASEBOOK.md` / `qualitative_cases.json`: eight explicitly selected median-length and largest-disagreement examples, with exact hits and missed/unmatched phrase evidence.
- `EVIDENCE_VALIDATION.json`: independent metric checks and archived/new baseline equality.

Two-sided paired tests follow the paper’s comparison design, but these are our rerun outputs. Original significance marks cannot be reproduced without the authors’ per-document outputs. Bootstrap intervals are pointwise; Holm p-values use explicitly stated families. No claim of significance against the paper’s aggregate scores is made.

## What remains externally unresolved

1. The authors’ exact YAKE version, complete execution settings and original dependency environment.
2. Original POS-tagged baseline input files, tagger versions, parameter files and output-to-top-10 policy.
3. Comparable unstemmed C-86 gold annotations used for a 244-document exact-match evaluation.
4. Original per-document outputs for all methods and original statistical-test implementation choices.

Additional parameter sweeps cannot establish those historical facts. They require archived author artifacts or clarification. The work is a substantially stronger, audited experimental reproduction; it is not asserted to be an exact executable recreation.

## Attribution and reproduction

See FIDELITY_PROTOCOL.md for source links, adaptations, configurations, metric rules and all reproduction commands. Historical code and datasets remain local; aggregate evidence is committed. The audit adds no supervised training stage.
