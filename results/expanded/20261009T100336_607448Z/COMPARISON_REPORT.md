# Expanded four-dataset comparison

Current implementations with declared preprocessing/settings; not verified publication-time equivalence.
SemEval archive: 243 documents versus 244 described by the paper. Other archive counts match.
F1 is mean per-document F1; top 10, casefolded exact matching. No supervised training.
TF-IDF uses collection-level candidate document frequencies (transductive), with POS tagging shared across PKE methods.

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
