# YAKE keyword extraction: selected-benchmark reproduction and independent equation reconstruction

**Student:** Joshua Rebello  
**SAP ID:** 70562200090  
**Programme:** B.Tech AI & DS, 4th year  
**Course:** Natural Language Processing mini-project  
**Experiment date:** 9 October 2026  
**Submission status:** Technical report draft prepared for individual submission; review before submission.

## Abstract

This project studies automatic keyword extraction using the method introduced by Campos et al. at ECIR 2018. An independent Python implementation reconstructs the paper's seven scoring equations with explicitly documented decisions for ambiguous cases. We compare it against YAKE 0.4.8 on all 500 documents of the 500N-KPCrowd-v1.1 dataset, using exact phrase matching and top-ten output. The reconstruction obtains mean per-document F1 of 0.1506; the package reference obtains 0.0762. Five feature ablations, deterministic checks, paired bootstrap intervals and detailed intermediate traces extend the evaluation. These results describe the implemented configurations, rather than proving exact reproduction of the original paper: preprocessing, word scoring and phrase scoring differ across the printed equations and available author code. The project reproduces a selected benchmark, not all four original datasets.

## 1. Problem and objectives

The task is to extract a ranked list of useful keywords or short phrases from a document without supervised training. Such a system can support indexing, search and document summaries. The input is English document text; the output is at most ten phrases of one to three words with importance scores.

The objectives are to implement document-level statistical scoring independently, compare with the public YAKE package, evaluate all selected-benchmark documents, inspect the contribution of each feature, and preserve enough evidence to explain and repeat every computation. The project demonstrates course topics including tokenization, stopword filtering, n-grams, frequency statistics, similarity and text extraction. The earlier adapted TF-IDF comparison additionally demonstrates corpus-based weighting.

## 2. Selected research paper

Campos, R., Mangaravite, V., Pasquali, A., Jorge, A., Nunes, C., and Jatowt, A. (2018). *A Text Feature Based Automatic Keyword Extraction Method for Single Documents*. ECIR 2018, Lecture Notes in Computer Science 10772, pp. 684–691. Springer. DOI: [10.1007/978-3-319-76941-7_63](https://doi.org/10.1007/978-3-319-76941-7_63).

The paper combines casing, word position, normalized frequency, neighboring-word relatedness and sentence spread. It scores candidate phrases using their component word scores and phrase frequency, then removes similar phrases. Lower scores indicate higher importance. YAKE requires neither labeled training examples nor a pretrained neural network or POS tagger.

The original evaluation covers SemEval2010, Schutz2008, 500N-KPCrowd and WICC. This project selects 500N-KPCrowd because it is a complete, manageable English news benchmark suitable for a short course project. Original TextRank, SingleRank, RAKE and TF-IDF comparisons are not all independently reproduced here.

## 3. Dataset and execution environment

The INESCTEC dataset archive provides 500 English broadcast-news documents and paired `.key` gold-keyword files across ten news categories. The loader reads UTF-8 text, checks that document IDs are unique and that every gold file exists and is nonempty, and retains all 500 documents. We deduplicate gold phrases after casefolding and whitespace normalization.

Measured dataset statistics are 393.908 whitespace-separated tokens per document on average and 48.912 normalized unique gold phrases per document on average (median 45). The token count is an audit statistic, not the algorithm tokenizer's exact count. Because top-k is fixed at ten, a document with 49 gold phrases cannot exceed recall 10/49 even if every returned phrase is correct. This is an illustrative bound, not the dataset's aggregate recall ceiling.

Dataset source: [INESCTEC KeywordExtractor-Datasets](https://github.com/INESCTEC/KeywordExtractor-Datasets).

Archive SHA-256:

`ee422c40d2655ee59c02add44319ea9b7a9b25947dc21947da73a2a6e47fbbf7`

The user-reported machine is a MacBook Pro M4 Pro with 24 GB memory and 1 TB storage. The run manifest records Python 3.9.6, YAKE 0.4.8, NumPy 2.0.2 and scikit-learn 1.6.1. Execution uses VS Code and a project-local virtual environment. There is no training or train/test split for the single-document algorithm: the gold phrases are used for evaluation rather than scoring.

## 4. Method and implementation

### 4.1 Processing stages

1. Split text into sentences using an explicit regex rule, then tokenize Unicode words, punctuation and digits.
2. Count word occurrences, sentence positions, acronym/title casing and neighboring words. Punctuation and digit tokens interrupt phrase blocks.
3. Compute the five word features and combine them into a word score.
4. Enumerate contiguous one-, two- and three-word candidates, recording their frequencies.
5. Compute phrase scores, reject candidates that start or end with stopwords, sort ascending and deduplicate.
6. Return up to ten phrases and compare them with the gold phrases.

The independent engine is `replication/core.py`. The experiment runner is `run_replication.py`; the settings are in `configs/paper.json`. The scorer receives only document text and configuration, not gold labels.

### 4.2 Scoring

The reconstructed feature formulas are:

- Casing: `max(acronym_count, noninitial_titlecase_count) / log2(tf)`; a denominator of 1 is used when `tf = 1`.
- Position: `log2(log2(2 + median_sentence_position))`, with sentence positions beginning at 1.
- Frequency: `tf / (mean_tf + population_std_tf)` over all observed word types.
- Relatedness: `(0.5 + WL*tf/max_tf + PL) + (0.5 + WR*tf/max_tf + PR)`.
- Spread: distinct sentences containing the word divided by total sentence count.

Here WL and WR are distinct left/right neighbor counts divided by the corresponding neighbor occurrence totals; PL and PR are distinct neighbor counts divided by maximum word frequency. The configured neighbor window is one word on each side within a punctuation block.

The word score is:

`H(w) = WRel * WPosition / (WCase + WFreq/WRel + WSpread/WRel)`.

The phrase score is:

`H(phrase) = product(H(w)) / (phrase_tf * (1 + sum(H(w))))`.

All phrase words participate in the independent implementation, including internal stopwords. English stopwords come from scikit-learn. Deduplication uses `1 - Levenshtein_distance/max_string_length`; a candidate is rejected if this similarity to an earlier retained phrase is strictly above 0.8. Equal-score candidates are ordered alphabetically.

### 4.3 Fidelity decisions and package comparison

These choices are explicit reconstruction decisions, not verified original experimental settings. The paper's casing denominator is zero for a singleton term, so a guard is necessary. The printed position formula requires a sentence-index convention. The stoplist and several preprocessing details are not uniquely specified by the paper alone.

The installed YAKE package uses segtok tokenization, plural normalization, non-stopword frequency statistics, natural-log casing/position formulas, omission of the printed PL/PR relatedness additions and special internal-stopword phrase weighting. The inspected historical author source at commit `36b3f0967cbef4048261c33845eb036163c6f278`, dated November 2018, already contains several of these differences and postdates the conference publication. It is not treated as the exact publication-time implementation.

Both methods use the same exposed top-k, maximum n-gram size, neighbor window and deduplication threshold. They nevertheless differ internally. Their comparison measures the behavior of these two configurations; it cannot isolate the effect of any one implementation difference.

## 5. Evaluation protocol

Predictions and gold phrases are casefolded and whitespace-normalized, then matched exactly. There is no stemming, substring credit or partial phrase credit. Duplicate predictions cannot earn duplicate hits.

For each document: `P@10 = hits/10`, `R = hits/unique_gold_count`, and `F1 = 2PR/(P+R)` when the denominator is nonzero. Unfilled prediction slots count as precision misses. The primary reported score is the arithmetic mean of document F1 values. The harmonic mean of macro precision and macro recall is also saved, but is not substituted for the primary score.

All 500 documents are evaluated by seven configurations, producing 3,500 unique document–method records. Source hashes in the run manifest were verified against the current source files. No extraction failure was reported in the complete run. Eight unit tests check a hand-calculated score, sentence/phrase boundaries, casing, edit distance, deterministic/empty behavior, metrics, invalid configuration and finite feature scores.

Confidence intervals use 2,000 paired bootstrap resamples of document F1 differences with seed 42. This is an added analysis, not replication of the paper's paired t-test. It describes document-resampling uncertainty for our protocol, not uncertainty about all original implementation choices.

## 6. Measured results

The authoritative run is `results/engineering/20261009T093634_374606Z`. Its total runner elapsed time is 132.93 seconds. Mean per-document times below include extraction and trace construction; they exclude dataset loading, bootstrap analysis and plotting and are not pure scoring benchmarks.

| Configuration | P@10 | Recall | Macro F1 | Mean seconds/document |
|---|---:|---:|---:|---:|
| paper-equations | 0.4000 | 0.0979 | 0.1506 | 0.04040 |
| YAKE-package | 0.2036 | 0.0498 | 0.0762 | 0.00952 |
| without-WCase | 0.4284 | 0.1048 | 0.1616 | 0.03524 |
| without-WPosition | 0.3690 | 0.0921 | 0.1408 | 0.04833 |
| without-WFreq | 0.4132 | 0.1007 | 0.1552 | 0.03782 |
| without-WRel | 0.2800 | 0.0660 | 0.1027 | 0.05426 |
| without-WSpread | 0.4052 | 0.0989 | 0.1524 | 0.03977 |

For the independent reconstruction, the harmonic mean of macro P/R is 0.1573, whereas mean document F1 is 0.1506. For the package reference these quantities are 0.0801 and 0.0762 respectively. Keeping these conventions separate avoids an aggregation error.

The paired mean F1 difference between the reconstruction and package reference is +0.0744, with a bootstrap 95% interval [0.0677, 0.0816]. The configurations differ in multiple ways, so this is not evidence that the original paper's algorithm has been improved by a controlled single change.

### 6.1 Feature ablations

For casing, frequency and spread, an ablation sets the corresponding denominator contribution to zero. Position and relatedness are set to one. Each intervention removes the named effect from the combined scoring formula. These are project-defined experiments, not ablations reported by the original paper.

Removing relatedness causes the largest observed F1 reduction, from 0.1506 to 0.1027. Removing position also lowers F1, to 0.1408. Removing casing improves F1 to 0.1616. Frequency and spread removals yield smaller improvements. These findings apply to this reconstruction, dataset and matching protocol; they do not establish universal feature importance. The highest-scoring ablation is exploratory, not a new method selected and validated on an independent test set.

### 6.2 Comparison with the published table

The paper's Table 1 reports the following YAKE results on 500N-KPCrowd: P = 0.251, R = 0.063 and F1 = 0.101.

| Method/source | P@10 | Recall | F1 | F1 difference from published YAKE |
|---|---:|---:|---:|---:|
| Published YAKE, Table 1 | 0.2510 | 0.0630 | 0.1010 | — |
| Current YAKE package run | 0.2036 | 0.0498 | 0.0762 | -0.0248 |
| Independent reconstruction | 0.4000 | 0.0979 | 0.1506 | +0.0496 |

This comparison shows a numerical reproduction gap; it does not establish a controlled improvement over the published system. Plausible contributors include tokenization, stopwords, frequency normalization, equation/code discrepancies, phrase treatment, case normalization and metric conventions. Their individual effects have not been isolated experimentally.

The original table also reports TextRank F1 0.103 on this dataset, slightly above YAKE's 0.101; the authors report no significant difference between them. Therefore the paper does not support a claim that YAKE wins every metric on every dataset.

The earlier project evaluation produced F1 0.0621 for RAKE-adapted and 0.1459 for TF-IDF-adapted. Those are secondary adapted-baseline results, not replications of the paper's baseline implementations. In particular, the project's TF-IDF adaptation uses unsupervised IDF fitted on the evaluated corpus without the original POS filtering. We do not use these numbers to validate the original paper's comparative claims.

## 7. Reproducibility and evidence

Each run creates a separate UTC-stamped folder rather than overwriting earlier results. `manifest.json` records source and archive hashes, document IDs, settings, package versions and completion state. `per_document.csv` provides paired scores and timings; `predictions.json` preserves ranked outputs. `sample_trace.json` records example text, sentence tokens, feature values, term scores, candidate scores, filtering decisions and gold labels. The demonstration utility exports readable feature/candidate/decision tables and a chart.

The prior package-based walkthrough remains available in `results/walkthrough`. It shows package internals; the independent trace shows our reconstructed internals. Presenting both makes the implementation differences inspectable.

Reproduction commands, without interactive-shell comments:

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv/bin/activate
python -m unittest discover -s tests -v
python run_replication.py --ablations
python engineering_demo.py
```

No training commands are missing. YAKE computes document-specific statistics at extraction time. Any use of the term “training” in the presentation should be corrected to “feature computation and keyword extraction.”

## 8. Limitations and future work

The scope is one English benchmark rather than the original multilingual four-dataset evaluation. The regex tokenizer is simpler than segtok and may split abbreviations incorrectly. The singleton casing guard, indexing, stoplist and population statistics are declared implementation decisions. The experiment does not reconstruct all original baseline systems, POS filtering or significance tests.

Unit tests validate selected invariants and arithmetic examples, not complete equivalence to an unavailable publication-time implementation. The run's gains and ablations have not been validated on an independent dataset. Timing results are specific to this execution environment and include trace overhead.

Useful follow-up work would independently validate on another original dataset, obtain clarification of publication-time implementation details, compare tokenizer and stoplist choices one at a time, and reproduce original POS-filtered baselines. These tasks remain future work and are not claimed as completed.

## 9. Conclusion

The project delivers a working, auditable keyword extraction system, complete selected-benchmark evaluation and transparent comparison between printed-equation reconstruction and public-package behavior. It meets the technical aim of demonstrating an NLP extraction pipeline with reproducible evidence. Exact agreement with the published scores was not achieved; the report documents the gap rather than concealing it.

## References and attribution

1. Campos et al. (2018), ECIR paper identified in Section 2. [Publisher record](https://link.springer.com/chapter/10.1007/978-3-319-76941-7_63).
2. [INESCTEC YAKE author repository](https://github.com/INESCTEC/yake). Package reference and historical implementation audit.
3. [Pinned historical scoring source](https://github.com/INESCTEC/yake/blob/36b3f0967cbef4048261c33845eb036163c6f278/yake/datarepresentation.py).
4. [INESCTEC KeywordExtractor-Datasets](https://github.com/INESCTEC/KeywordExtractor-Datasets). 500N-KPCrowd archive and gold keywords.
5. scikit-learn English stopword list and TF-IDF implementation, version recorded in the experiment manifest.

The independent engine is project code; the reference system and dependencies are credited upstream software. AI assistance was used for implementation scaffolding, testing and report drafting; the student should review and be able to explain every submitted component and adapt this disclosure to the course's requirements.
