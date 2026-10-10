# YAKE ECIR 2018: expanded four-dataset experimental comparison

**Student:** Joshua Rebello  
**SAP ID:** 70562200090  
**Programme:** B.Tech AI & DS, 4th year  
**Course:** Natural Language Processing mini-project  
**Experiment date:** 9 October 2026

## Abstract

This project evaluates all four datasets and the five named methods in Table 1 of Campos et al.'s ECIR 2018 paper, plus an independent reconstruction of its printed YAKE equations. We evaluate 3,614 documents in six configurations, producing 21,684 document–method records. The primary SemEval2010 archive contains 243 nonempty-gold pairs rather than the paper's reported 244. A follow-up recovered C-86 text and separately evaluated all 244 texts with original task stemmed gold; see FIDELITY_REPORT.md. Methods use pinned current implementations and explicitly documented preprocessing. The report compares published precision, recall and F1 with newly measured results, without claiming executable equivalence to publication-time code. All results are computed rather than estimated or copied into unrun cells.

## 1. Problem, paper and scope

The input is document text and the output is up to ten ranked keyword phrases of at most three words. Exact phrase matching against human-provided gold keywords evaluates extraction. The selected paper is Campos et al. (2018), *A Text Feature Based Automatic Keyword Extraction Method for Single Documents*, ECIR, Springer LNCS 10772, pp. 684–691, DOI [10.1007/978-3-319-76941-7_63](https://doi.org/10.1007/978-3-319-76941-7_63).

This expanded experiment covers the full dataset/method layout of the paper's table using modern implementations. It is not an exact full-paper replication. Recovering publication-time executable baseline versions, taggers and every parameter remains unresolved. The earlier 500N report is preserved as PROJECT_REPORT_500N.md, while this report becomes the current project report.

## 2. Data and methods

English datasets are 500N-KPCrowd (500 news stories), SemEval2010 (243 available computer-science papers) and Schutz2008 (1,231 medical papers). WICC contains 1,640 Spanish computer-science articles. All available paired documents/gold files are checked; no artificial document is added to SemEval. Archive hashes and counts are recorded in the run manifest. The source is the [INESCTEC dataset repository](https://github.com/INESCTEC/KeywordExtractor-Datasets).

YAKE-package uses YAKE 0.4.8. TextRank-PKE, SingleRank-PKE and TF-IDF-PKE use PKE at commit 69871ffdb720b83df23684fea53ec8776fd87e63. RAKE-local implements Unicode phrase segmentation and degree/frequency scoring independently. The independent reconstruction implements the paper's printed feature and phrase equations with declared safeguards. See EXPANDED_PROTOCOL.md and ENGINEERING_PROTOCOL.md for all decisions.

The POS-based methods use spaCy 3.7.5, en_core_web_sm 3.7.1 and es_core_news_sm 3.7.0. Modern pretrained POS taggers are reused, not trained by this project. Common PKE candidate filtering keeps 1–3-grams consisting of nouns, proper nouns and adjectives; it rejects stopwords and applies PKE length/alphanumeric filters. This is a declared common policy rather than a verified original-paper policy. TextRank uses unweighted PageRank with window 2; SingleRank uses weighted PageRank with window 10; damping is 0.85. Neither uses additional YAKE-style Levenshtein deduplication.

YAKE uses language-appropriate package stopwords, neighbor window 1 and deduplication threshold 0.8. Independent English reconstruction retains the earlier scikit-learn stoplist; Spanish reconstruction uses spaCy Spanish stopwords. RAKE uses spaCy stopwords and rejects phrases longer than three before counting word statistics. TF-IDF uses candidate document frequencies from the evaluated collection with PKE's smoothed weighting; this is transductive unsupervised corpus statistics.

## 3. Evaluation and engineering

For each document, normalized exact matches produce P@10 = hits/10 and recall = hits/unique gold count. Per-document F1 is computed and then averaged. Casefolding and whitespace normalization are applied; no stemming, partial matches or substring credit. Unfilled slots count as precision misses. Empty outputs receive zero scores and are not discarded. Exceptions fail the run while preserving completed records.

The separate .venv_full environment preserves the original .venv. The runner saves predictions incrementally and permits same-source, same-settings resume. POS preprocessing is cached using dataset/model/policy identifiers. Sixteen tests cover original arithmetic invariants plus POS selection, explicit IDF arithmetic, RAKE scoring, Spanish stopwords and dataset counts. These validate defined behavior, not equivalence to the original authors' complete experiments.

Paired t-tests and 2,000-resample seeded bootstrap intervals compare our YAKE-package configuration against our other configurations on matched documents. They do not compare against the paper's unavailable document-level outputs. P-values are exploratory and unadjusted for multiple comparisons; intervals are pointwise. Method timings exclude shared POS and corpus-DF preparation, so they are not end-to-end comparisons.

## 4. Published scores versus measured scores

The following tables retain every published method/dataset P/R/F1 value and pair it with our computed values. The sixth configuration has no directly corresponding published row. F1 deltas are descriptive, not evidence of a controlled improvement over the published systems.

## 500N-KPCrowd

| Method | Paper P | Paper R | Paper F1 | Our P@10 | Our R | Our F1 | F1 delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| YAKE-package | 0.2510 | 0.0630 | 0.1010 | 0.2036 | 0.0498 | 0.0762 | -0.0248 |
| TextRank-PKE | 0.2650 | 0.0630 | 0.1030 | 0.1154 | 0.0342 | 0.0495 | -0.0535 |
| TF-IDF-PKE | 0.2230 | 0.0600 | 0.0950 | 0.4304 | 0.1033 | 0.1596 | +0.0646 |
| SingleRank-PKE | 0.1900 | 0.0540 | 0.0840 | 0.1672 | 0.0462 | 0.0687 | -0.0153 |
| RAKE-local | 0.1200 | 0.0380 | 0.0580 | 0.1356 | 0.0439 | 0.0630 | +0.0050 |
| Independent-reconstruction | — | — | — | 0.4000 | 0.0979 | 0.1506 | — |

## SemEval2010

| Method | Paper P | Paper R | Paper F1 | Our P@10 | Our R | Our F1 | F1 delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| YAKE-package | 0.1530 | 0.1030 | 0.1230 | 0.1523 | 0.1021 | 0.1207 | -0.0023 |
| TextRank-PKE | 0.1010 | 0.0670 | 0.0810 | 0.0309 | 0.0201 | 0.0241 | -0.0569 |
| TF-IDF-PKE | 0.0360 | 0.0230 | 0.0280 | 0.1346 | 0.0915 | 0.1078 | +0.0798 |
| SingleRank-PKE | 0.0350 | 0.0220 | 0.0270 | 0.0457 | 0.0294 | 0.0354 | +0.0084 |
| RAKE-local | 0.0070 | 0.0040 | 0.0050 | 0.0066 | 0.0037 | 0.0047 | -0.0003 |
| Independent-reconstruction | — | — | — | 0.0753 | 0.0519 | 0.0608 | — |

## Schutz2008

| Method | Paper P | Paper R | Paper F1 | Our P@10 | Our R | Our F1 | F1 delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| YAKE-package | 0.2170 | 0.0580 | 0.0910 | 0.3327 | 0.0872 | 0.1323 | +0.0413 |
| TextRank-PKE | 0.1980 | 0.0520 | 0.0820 | 0.0515 | 0.0138 | 0.0209 | -0.0611 |
| TF-IDF-PKE | 0.1000 | 0.0280 | 0.0430 | 0.4129 | 0.1074 | 0.1623 | +0.1193 |
| SingleRank-PKE | 0.0820 | 0.0240 | 0.0370 | 0.0881 | 0.0250 | 0.0369 | -0.0001 |
| RAKE-local | 0.0130 | 0.0040 | 0.0060 | 0.0158 | 0.0049 | 0.0069 | +0.0009 |
| Independent-reconstruction | — | — | — | 0.2877 | 0.0765 | 0.1157 | — |

## WICC

| Method | Paper P | Paper R | Paper F1 | Our P@10 | Our R | Our F1 | F1 delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| YAKE-package | 0.0500 | 0.1410 | 0.0730 | 0.0956 | 0.2799 | 0.1378 | +0.0648 |
| TextRank-PKE | 0.0180 | 0.0580 | 0.0270 | 0.0192 | 0.0627 | 0.0284 | +0.0014 |
| TF-IDF-PKE | 0.0260 | 0.0670 | 0.0370 | 0.0790 | 0.2200 | 0.1121 | +0.0751 |
| SingleRank-PKE | 0.0170 | 0.0450 | 0.0240 | 0.0492 | 0.1451 | 0.0710 | +0.0470 |
| RAKE-local | 0.0040 | 0.0120 | 0.0060 | 0.0043 | 0.0163 | 0.0066 | +0.0006 |
| Independent-reconstruction | — | — | — | 0.0694 | 0.1928 | 0.0986 | — |

## Interpretation limits

Do not infer superiority from paper-vs-run deltas: original executable versions, tokenization, stoplists, POS taggers and exact aggregation details have not been matched.
Our PKE baselines use a common POS-filtered 1–3-gram policy. TextRank window=2 and unweighted PageRank; SingleRank window=10 and weighted PageRank; damping=0.85.
RAKE is a local Unicode implementation with language-specific spaCy stopwords; phrases longer than 3 are discarded before word statistics.
Independent reconstruction uses the prior English stoplist for English and spaCy Spanish stopwords for WICC; it retains documented equation safeguards.
Paired statistics compare our matched document outputs, not unpublished per-document outputs from the paper. T-test p-values are unadjusted exploratory values across multiple comparisons; bootstrap intervals are pointwise.
Timing columns exclude shared POS preprocessing and corpus DF construction; those stage times appear in the manifest.

## 5. Interpretation

The highest measured F1 configurations in this run are TF-IDF-PKE on 500N-KPCrowd (0.1596), YAKE-package on SemEval2010 (0.1207), TF-IDF-PKE on Schutz2008 (0.1623), and YAKE-package on WICC (0.1378). No configuration wins every dataset. The independent reconstruction outperforms our YAKE package on news, but scores below it on the other three datasets. These are within-run findings under our declared policies.

Compare the ranking within each dataset rather than choosing the dataset with the most favorable score. A negative delta indicates a reproduction gap for that method/configuration; a positive delta does not establish superiority because tokenizers, stoplists, POS taggers, phrase generation, implementation versions and possibly gold matching/aggregation differ.

The independent reconstruction is an extra project configuration. It is not substituted for the YAKE-package row when comparing the five named methods. The earlier five feature ablations remain available as an archived 500N study. The follow-up fidelity audit repeats them on all four valid primary datasets; see FIDELITY_REPORT.md. Neither study establishes universal feature importance.

## 6. Reproducibility and limitations

The authoritative expanded run is results/expanded/20261009T100336_607448Z. EVIDENCE_VALIDATION.json verifies 3,614 evaluated documents, 21,684 unique document/configuration records, 20 paper-versus-run pairs and summary aggregation. Full per-document evidence, package/source hashes, settings, archive hashes and matched statistics are preserved. Predictions and dataset texts remain local; public evidence consists of metrics, manifests and figures.

The one-document SemEval difference prevents exact corpus identity. Current PKE implementations and the shared candidate policy are not original baseline executables. POS preprocessing and word normalization differ from historical implementations. The independent equation reconstruction retains documented ambiguities, including singleton casing and sentence indexing. We do not claim all paper findings or significance tests have been exactly reproduced. Coverage of all table cells is complete for our declared configurations.

## 7. Demonstration

Use the full run's manifest to show counts and versions, then COMPARISON_REPORT.md and paper_vs_ours.png for all four datasets. Run the 31 tests, explain one sample pipeline trace from the earlier walkthrough, and show per_document.csv to establish that the aggregate tables come from actual document-level evaluation. Explain that YAKE has no supervised training phase and that the POS models are pretrained dependencies.

## References and attribution

- Campos et al., ECIR 2018 paper and Table 1, DOI above.
- [INESCTEC YAKE](https://github.com/INESCTEC/yake), package reference.
- [Pinned PKE source](https://github.com/boudinfl/pke/tree/69871ffdb720b83df23684fea53ec8776fd87e63), three attributed baseline implementations.
- [INESCTEC KeywordExtractor-Datasets](https://github.com/INESCTEC/KeywordExtractor-Datasets), document/gold archives.
- [spaCy language models](https://github.com/explosion/spacy-models), English and Spanish POS tagging.

AI assistance was used for scaffolding, testing and report drafting. Joshua should review and be able to explain each submitted component, and adapt the disclosure to course requirements. Independent scorer, RAKE implementation and experiment/evidence integration are project code; PKE, YAKE and POS models are credited reused dependencies.


## Subsequent fidelity audit

The original results above remain an immutable archived comparison. The follow-up [fidelity report](FIDELITY_REPORT.md) investigates historical implementations, source recovery, all-dataset feature ablations, controlled preprocessing/scoring choices, matching and length effects, and a separate 244-document SemEval stemmed evaluation. Its [protocol](FIDELITY_PROTOCOL.md) documents both completed work and externally unresolved historical facts.
