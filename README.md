# YAKE keyword extraction: partial experimental replication

Paper: Campos et al. (2018), A Text Feature Based Automatic Keyword Extraction Method for Single Documents. ECIR 2018, Springer LNCS 10772, pp. 684–691. DOI: 10.1007/978-3-319-76941-7_63.

## Run

Activate `.venv`, then run `python main.py --text "Your paragraph"`.
Run `python evaluate.py --limit 5` for a smoke check and `python evaluate.py` for all 500 documents.

## Scope and attribution

The original `evaluate.py` pipeline uses the authors' YAKE implementation. The added `replication/core.py` independently reconstructs the printed equations with documented choices. Dataset: 500N-KPCrowd-v1.1, downloaded from https://github.com/INESCTEC/KeywordExtractor-Datasets. Original dataset citation: Marujo, Viveiros, and Neto (2013), Keyphrase Cloud Generation of Broadcast News. Cite both the method and dataset in the report.

Modern YAKE package versions may differ from the 2018 implementation. Maximum phrase length 3, top 10, Levenshtein deduplication threshold 0.8. Context window fixed to 1 as an explicit implementation choice; historical code equivalence has not been established.

RAKE is a locally implemented adaptation with sklearn's English stopwords and a 1–3 word candidate restriction. TF-IDF is an sklearn adaptation with 1–3 grams, no POS filtering, and statistics fitted to the evaluated collection. These baselines are not the original paper's exact baseline implementations. TextRank and SingleRank are not replicated here. One collection is evaluated instead of the paper's four.

Evaluation uses case-insensitive exact phrase matches after whitespace normalization, without stemming. Precision is hits / 10 even when fewer phrases are returned. Recall uses all unique gold phrases, including absent phrases. F1 is calculated per document, then averaged. This protocol must be reported; original tokenization, annotations and aggregation details may differ, so identical published numbers are not expected. Runtime excludes TF-IDF fitting and is not an end-to-end speed comparison.

`results/full/metadata.json` records settings, package versions, and the dataset archive checksum. CSV records document-level metrics; JSON records predictions and aggregate metrics. Inspect errors and explain the method yourself before submission. The technical report is in `PROJECT_REPORT.md`; review it before submission.

Do not redistribute dataset documents in your public repository without checking their terms. Obtain them from the source; commit code, metadata and aggregate results. Requirements contain pinned versions of the active environment.

## Independent engineering replication

See `ENGINEERING_PROTOCOL.md` for exact scope, printed-equation reconstruction choices, reference-code differences, evaluation, and demonstration instructions.

```bash
python -m unittest discover -s tests -v
python run_replication.py --ablations
python engineering_demo.py
```

New runs are immutable timestamped directories under `results/engineering/`. `replication/core.py` implements the independent scoring pipeline; `configs/paper.json` controls exposed experimental settings. Initial package/adapted-baseline experiments remain intact. YAKE is unsupervised and has no training epochs.

## Fresh environment and dataset setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data
curl -fL "https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/master/datasets/500N-KPCrowd-v1.1.zip" -o data/500N-KPCrowd-v1.1.zip
python -m unittest discover -s tests -v
python run_replication.py --ablations
python engineering_demo.py
```

The full-run archive hash recorded in the report identifies the evaluated dataset. A changed upstream archive is a different input and should be reported. The dependency versions were validated on the current Mac/Python environment; other Python versions may require compatibility changes.

## Submission documents

- `PROJECT_REPORT.md`: technical report draft by Joshua Rebello (SAP ID 70562200090), based on actual measured results.
- `SUBMISSION_CHECKLIST.md`: individual review, demonstration and publication steps.
- `ENGINEERING_PROTOCOL.md`: detailed implementation choices and scope.

For the saved final demonstration, use `results/engineering/20261009T093634_374606Z` explicitly. A five-document smoke run is not the final benchmark evidence.
