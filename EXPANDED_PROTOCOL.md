# Expanded comparison protocol

## Coverage

All four datasets in Campos et al.'s ECIR 2018 Table 1 are evaluated. Five named methods are represented, plus the independent equation reconstruction as a sixth configuration. This is full table coverage using current implementations, not verified equivalence to publication-time code.

| Dataset | Paper count | Available archive count | Language |
|---|---:|---:|---|
| 500N-KPCrowd | 500 | 500 | English |
| SemEval2010 | 244 | 243 | English |
| Schutz2008 | 1,231 | 1,231 | English |
| WICC | 1,640 | 1,640 | Spanish |

No document is invented or duplicated to fill the one-document SemEval difference. Total evaluated documents: 3,614. Total document/configuration records: 21,684.

## Implementations

- YAKE-package: version 0.4.8, language en/es, maximum n=3, top=10, neighbor window=1, normalized Levenshtein deduplication threshold 0.8.
- TextRank-PKE: PKE commit 69871ffdb720b83df23684fea53ec8776fd87e63; unweighted PageRank, window=2, damping=0.85, no top-percent phrase-generation step.
- SingleRank-PKE: same pinned PKE version; weighted PageRank, window=10, damping=0.85.
- TF-IDF-PKE: same pinned PKE version; phrase frequency times `log2((N+1)/(df+1))`. Document frequencies are computed from the evaluated collection's candidates. This is transductive unsupervised corpus statistics, not supervised training.
- RAKE-local: independently implemented degree/frequency word weighting and sum-based phrase weighting, Unicode word splitting, spaCy language stopwords, stopword/punctuation-delimited phrases. Phrases longer than three words are discarded before frequency/degree counts. This differs from the ASCII-oriented historical tutorial implementation.
- Independent-reconstruction: printed-equation scorer from the earlier project. English uses the prior scikit-learn stoplist; Spanish uses spaCy Spanish stopwords. Singleton casing safeguard, one-based sentence positions, full printed relatedness contributions and all-word phrase products remain documented in ENGINEERING_PROTOCOL.md. Fast extraction stops once ten phrases are selected; a test checks equality with the trace-producing mode.

The PKE baselines share an explicit candidate policy: contiguous 1–3 grams, nouns/proper nouns/adjectives only, no stopwords, minimum word size 2, minimum candidate character count 3, and PKE's alphanumeric/punctuation filters. This policy differs from default longest-POS-sequence candidates and is recorded to make methods comparable within our run. It must not be presented as verified original-paper candidate generation. PKE outputs are not additionally Levenshtein-deduplicated.

## POS preprocessing

spaCy 3.7.5 uses en_core_web_sm 3.7.1 and es_core_news_sm 3.7.0. NER, parser and lemmatizer are disabled; rule-based sentencizer determines sentence boundaries. POS assignment remains enabled. PKE receives sentence-level token/POS pairs, with normalization=None. POS tags and stoplists are supplied by modern pretrained models rather than publication-time taggers. There is no model training in this experiment.

Shared POS results are cached under a namespace incorporating dataset archive hash, spaCy version, language-model version and declared sentence/normalization policy. Corpus DF is recomputed for the selected evaluated document set. Smoke-run corpus statistics therefore differ from full-run statistics; smoke scores are not final results.

## Metrics, timing and statistics

Casefold and normalize whitespace; exact phrase matching only. P@10 includes unfilled slots as misses; recall uses normalized unique gold phrases; F1 is averaged per document. The harmonic mean of macro precision and recall is separately recorded. Empty output receives zero scores rather than being removed. Exceptions fail the run and preserve evidence.

Paired bootstrap intervals use 2,000 resamples with seed 42. Paired t-tests compare our YAKE-package outputs against our other configurations, not against unavailable original-paper per-document outputs. P-values are exploratory and unadjusted for multiple comparisons. Do not label a universal significance claim from these values.

Method timings exclude shared POS preprocessing and corpus DF construction. The manifest records POS cache load/compute time; it does not include candidate DF construction in that field. Overall runner time includes the whole invocation. Timings for cached and uncached invocations are different and not directly interchangeable.

## Running

Use the separate environment to preserve the original package environment:

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv_full/bin/activate
python -m unittest discover -s tests -v
python full_comparison.py --limit 2
python full_comparison.py
```

New runs are under results/expanded. To resume, supply the exact original run directory, with matching dataset/limit settings and unchanged source:

```bash
python full_comparison.py --resume results/expanded/YOUR_RUN_DIRECTORY
```

Plot a completed run explicitly:

```bash
python plot_full_comparison.py --run results/expanded/YOUR_RUN_DIRECTORY
```

For local stage-by-stage examples, run `python full_walkthrough.py`. It selects one median-length document per dataset without inspecting prediction quality, and saves document/POS/features/candidates/keywords/gold under `results/expanded_walkthrough/`. Those source-text traces are not committed.

Evidence: manifest.json, predictions.jsonl, per_document.csv, summary.json, paper_comparison.csv, paired_statistics.json, COMPARISON_REPORT.md and paper_vs_ours.png. Full predictions and POS caches remain local. Code dependencies are pinned in requirements-full.txt, including the PKE commit and model URLs.

## Sources

- Paper: https://doi.org/10.1007/978-3-319-76941-7_63
- Dataset repository: https://github.com/INESCTEC/KeywordExtractor-Datasets
- PKE source: https://github.com/boudinfl/pke/tree/69871ffdb720b83df23684fea53ec8776fd87e63
- Author evaluation wrapper context: https://github.com/INESCTEC/kep
- POS model releases: https://github.com/explosion/spacy-models

The later fidelity audit recovered historical YAKE releases, a preconference RAKE snapshot and the cited-page C++ baseline family. Exact paper runtime identity, POS-tagged inputs and complete parameterization remain unresolved. See FIDELITY_PROTOCOL.md and FIDELITY_REPORT.md. A full-coverage comparison cannot, by itself, prove exact historical replication.
