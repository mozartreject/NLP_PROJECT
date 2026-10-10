# YAKE ECIR 2018: four-dataset experimental comparison

**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**

This project compares all four datasets and the five methods in Table 1 of Campos et al. (2018), plus an independent YAKE equation reconstruction. It provides full table coverage using current implementations with documented differences; it does not claim exact publication-time executable equivalence.

Paper: *A Text Feature Based Automatic Keyword Extraction Method for Single Documents*, ECIR 2018, Springer LNCS 10772, pp. 684–691. [DOI](https://doi.org/10.1007/978-3-319-76941-7_63).

## Scope

| Dataset | Evaluated documents | Language |
|---|---:|---|
| 500N-KPCrowd | 500 | English |
| SemEval2010 | 243 | English |
| Schutz2008 | 1,231 | English |
| WICC | 1,640 | Spanish |

The public SemEval archive contains 243 documents, versus 244 described in the paper. Six configurations produce 21,684 document/configuration evaluations. Methods: YAKE-package, TextRank-PKE, TF-IDF-PKE, SingleRank-PKE, RAKE-local and Independent-reconstruction.

YAKE is unsupervised and has no training epochs. POS-based baselines reuse pretrained spaCy models. TF-IDF builds transductive corpus statistics without labels. Gold labels are used for exact-match evaluation.

## Setup

Python 3.9 was used. From the project directory:

```bash
python3 -m venv .venv_full
source .venv_full/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-full.txt
mkdir -p data
curl -fL "https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/master/datasets/500N-KPCrowd-v1.1.zip" -o data/500N-KPCrowd-v1.1.zip
curl -fL "https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/master/datasets/SemEval2010.zip" -o data/SemEval2010.zip
curl -fL "https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/master/datasets/Schutz2008.zip" -o data/Schutz2008.zip
curl -fL "https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/master/datasets/wicc.zip" -o data/wicc.zip
python -m unittest discover -s tests -v
python full_comparison.py --limit 2
python full_comparison.py
```

The existing `.venv` and original experiments remain intact. Pinning source/model versions and archive hashes identifies the evaluated inputs. Other Python/platform combinations may need compatibility changes. Dataset and paper files are not distributed here.

## Results and reports

- `PROJECT_REPORT.md`: current expanded technical report.
- `EXPANDED_PROTOCOL.md`: exact candidate policies, language models, metrics and fidelity limits.
- `results/expanded/20261009T100336_607448Z/COMPARISON_REPORT.md`: all published P/R/F1 values paired with measured results.
- `paper_comparison.csv` in that folder: 20 method/dataset comparisons.
- `summary.json`, `per_document.csv`, `manifest.json`, `paired_statistics.json`: machine-readable evidence.
- `paper_vs_ours.png`: four-dataset chart.
- `PROJECT_REPORT_500N.md`: preserved original selected-benchmark report.
- `ENGINEERING_PROTOCOL.md`: independent equation reconstruction details.

The full expanded run is timestamped. New smoke runs are different experiments and must not replace the final benchmark evidence in a presentation.

To plot a completed run:

```bash
python plot_full_comparison.py --run results/expanded/20261009T100336_607448Z
```

To resume an interrupted run, use the same source/settings:

```bash
python full_comparison.py --resume results/expanded/YOUR_RUN_DIRECTORY
```

## Earlier experiments

`evaluate.py` compares the YAKE package against earlier RAKE/TF-IDF adaptations on 500N only. These differ from the expanded POS-filtered PKE configurations and must not be merged under the same implementation label. `run_replication.py --ablations` supplies five independent-feature ablations on 500N only. Original core-only tests in `.venv` can be run with `python -m unittest discover -s tests -p test_replication.py -v`; all 16 tests use `.venv_full`.

`full_walkthrough.py` exports median-length example traces for all four datasets under `results/expanded_walkthrough/` (kept local). Run it in `.venv_full`. `walkthrough.py` and `engineering_demo.py` retain the earlier 500N traces. Modern code and printed equations have documented differences in tokenizer, casing, frequency statistics, sentence positions, relatedness and internal-stopword weighting. Numerically higher scores are not proof of a controlled improvement over the published algorithm.

## Attribution

[YAKE](https://github.com/INESCTEC/yake), [PKE](https://github.com/boudinfl/pke), [dataset repository](https://github.com/INESCTEC/KeywordExtractor-Datasets), and [spaCy models](https://github.com/explosion/spacy-models) are credited dependencies/data sources. The independent scorer, local RAKE and experiment/evidence pipeline are project code developed with AI assistance. Review the report and understand each component before submission. Raw documents, full prediction text and preprocessing caches remain local; public evidence includes metrics and manifests.
