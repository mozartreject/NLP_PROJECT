# Reproduction protocol

The repository was reorganized without changing the measured results. Current commands use `project.py`. Original paths, source hashes and public run evidence remain byte-for-byte inside `../results/evidence.zip`. Use `python project.py evidence --restore` to unpack result files locally; generated runs are ignored by Git. Archived source hashes identify pre-cleanup code, while new runs hash the reorganized scripts.

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
- Independent-reconstruction: printed-equation scorer from the earlier project. English uses the prior scikit-learn stoplist; Spanish uses spaCy Spanish stopwords. Singleton casing safeguard, one-based sentence positions, full printed relatedness contributions and all-word phrase products remain documented in PROTOCOL.md. Fast extraction stops once ten phrases are selected; a test checks equality with the trace-producing mode.

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
python project.py compare --limit 2
python project.py compare
```

New runs are under results/expanded. To resume, supply the exact original run directory, with matching dataset/limit settings and unchanged source:

```bash
python project.py compare --resume results/expanded/YOUR_RUN_DIRECTORY
```

Primary comparison plots are preserved in the evidence ZIP. The README keeps the four essential figures; regenerate audit figures using `python project.py figures --run results/fidelity/YOUR_AUDIT`.

For local stage-by-stage examples, run `python project.py walkthrough`. It selects one median-length document per dataset without inspecting prediction quality, and saves document/POS/features/candidates/keywords/gold under `results/expanded_walkthrough/`. Those source-text traces are not committed.

Evidence: manifest.json, predictions.jsonl, per_document.csv, summary.json, paper_comparison.csv, paired_statistics.json, COMPARISON_REPORT.md and paper_vs_ours.png. Full predictions and POS caches remain local. Code dependencies are pinned in requirements.txt, including the PKE commit and model URLs.

## Sources

- Paper: https://doi.org/10.1007/978-3-319-76941-7_63
- Dataset repository: https://github.com/INESCTEC/KeywordExtractor-Datasets
- PKE source: https://github.com/boudinfl/pke/tree/69871ffdb720b83df23684fea53ec8776fd87e63
- Author evaluation wrapper context: https://github.com/INESCTEC/kep
- POS model releases: https://github.com/explosion/spacy-models

The later fidelity audit recovered historical YAKE releases, a preconference RAKE snapshot and the cited-page C++ baseline family. Exact paper runtime identity, POS-tagged inputs and complete parameterization remain unresolved. See PROTOCOL.md and REPORT.md. A full-coverage comparison cannot, by itself, prove exact historical replication.


# Fidelity audit protocol

This audit follows the ECIR 2018 paper's equations (Section 2), experiment design (Section 3) and Table 1. It preserves the original 3,614-document run. Follow-up configurations are diagnostic experiments, not a search for whichever settings best reproduce the published scores. No best-scoring sensitivity variant is promoted as a new validated algorithm.

## Source recovery

`prepare_fidelity_sources.py` verifies PyPI's archived source-distribution hashes for YAKE 0.3.0 and 0.3.2, dated January 13 and March 28, 2018. The scorer files differ from the November 2018 Git snapshot previously inspected: the early releases include PL/PR. Neither a later Git snapshot nor today's package is evidence of the exact paper executable.

`historical_release_sweep.py` inventories all six extant PyPI releases uploaded before/during ECIR 2018: 0.2.0, 0.2.1, 0.2.2, 0.2.4, 0.3.0 and 0.3.2. The scorer, extractor and English/Spanish stoplist files are byte-identical within the 0.2.0/0.2.1/0.2.2 family and within the 0.3.0/0.3.2 family. All three distinct families are executed with windows 1 and 2. Release 0.3.2 is additionally executed directly, rather than relying only on its source equivalence.

Historical source is loaded into isolated module namespaces. Only its internal module import is redirected; scoring and candidate code are unchanged. Old code returns score/phrase pairs, which the adapter converts to phrase/score pairs. Execution uses current pinned dependencies and current Python, not an independently recovered 2018 environment. PyPI upload dates establish availability, not which build the authors ran.

The archived Hasan download page cited in the paper exposes TextRank, SingleRank and TF-IDF. Its 2010 version-1.0 package was recovered through a 2021 Internet Archive capture; the package identity has not been verified against the authors' ECIR execution. C++ originals remain cached locally. Two compatibility changes are recorded with original/patched hashes: rename the TextRank `ratio` identifier to avoid a libc++ collision, and restore console output to `/dev/null` instead of `/dev/tty` for noninteractive execution. The compiler command is `g++ -O2 -std=c++98`.

The cited RAKE tutorial is pinned to commit `14e153aa9cb2c02456df3880cd5fd30f7ee3aa95`, March 3, 2018. It is tested with its Smart English stoplist on the three English datasets and with explicit language-specific KEP stoplists on all four. KEP stoplists are from 2020 and are labelled accordingly; their historical identity is unresolved.

## Missing SemEval document

The Maui archive contains 244 texts, while the INESCTEC archive contains 243 nonempty text/gold pairs. The missing ID is C-86. All 243 shared normalized gold sets match, and texts match after stripping outer whitespace. The original 243 text and gold byte streams are retained when building a recovery archive.

**C-86's Maui `.key` file is empty.** Recovering the text does not recover comparable unstemmed reference keywords. The primary exact-match audit therefore keeps 243 scored SemEval documents and explicitly excludes this empty-gold pair. It does not invent keywords or define empty-gold recall as zero to make the document count match.

The original task repository provides combined Porter-stemmed annotations for all 244 documents, including 14 unique stemmed phrases for C-86. `semeval244_sensitivity.py` evaluates all 244 using these original task labels and wordwise Porter-stemmed predictions, under the project's top-10 budget. TF-IDF document frequencies are recomputed on all 244. This is a **separate annotation/matching sensitivity**, not an unstemmed replacement for the paper table, nor the original SemEval competition's top-15/micro-averaged evaluation.

## Four-dataset independent interventions

`replication/fidelity_core.py` retains a default policy that matches `replication/core.py`. Every full-run default extraction is checked against the original scorer. The baseline, five feature removals and thirteen one-choice sensitivities are executed on all 3,614 valid primary document/gold pairs.

The sensitivities are:

1. segtok sentence/token segmentation;
2. split punctuation within hyphenated/apostrophe-containing words;
3. author-package stoplists instead of the original English sklearn / Spanish spaCy lists;
4. natural-log casing denominator;
5. natural-log position formula;
6. frequency mean/standard deviation from non-stopword terms only;
7. omit PL/PR relatedness additions;
8. median of unique sentence positions instead of occurrence-weighted positions;
9. alternative singleton casing denominator `ln(1+tf)` for tf=1 only;
10. neighbor window 2 instead of 1;
11. casing denominator `1+ln(tf)` at every frequency;
12. internal-stopword transition weighting in phrase scores;
13. merge final-s term statistics and use the resulting term identities for boundary lookup, while retaining surface phrase strings.

These interventions isolate a defined engineering choice in the reconstruction. They are not a complete factorial experiment, do not isolate all interactions, and do not prove that a difference explains the published results. Historical-code runs test bundles of differences directly.

All five feature ablations use the previously documented neutral values: casing/frequency/spread contributions become zero; position/relatedness become one. Values are never chosen using gold outcomes.

## Corpus edge-case repair and provenance

A full-corpus segtok sensitivity run encountered a URL token containing embedded whitespace. The repair splits such returned tokens on whitespace before candidate construction. A regression test covers that case. All 3,093 previously saved segtok-variant records were invalidated and rerun; 55,680 other configuration records were retained because their executed code paths were unchanged. The failed manifest, prior source snapshot and explicit source-revision entry are preserved. No failed document is silently removed from the scored collections.

Some historical outputs contain Unicode NEL/line/paragraph separator characters inside valid JSON strings. The evidence reader now separates JSONL records only on LF; `splitlines()` incorrectly split those strings. Extraction outputs were retained unchanged. The history manifest records this reader-only revision and preserves the prior runner snapshot. The baseline suite uses the same provenance rule if its finalization needs the repaired reader. Source hashes can therefore refer to a preserved extraction snapshot rather than the current file; both revisions remain available under `source_snapshots/`.

## Modern baseline candidate policies

The archived PKE run uses common POS-filtered 1–3 grams. Follow-up runs compare it against PKE-native TextRank top-33%-word candidate construction, SingleRank longest noun/adjective sequences and TF-IDF native n-grams. Candidate phrases are constrained to a maximum of three words. TextRank weights are pruned after candidate filtering so removed candidates cannot be re-created during output lookup.

The TF-IDF no-POS control uses 1–3 grams with PKE's ordinary filters; in this pinned PKE version that is equivalent to native TF-IDF candidate selection. Their equality is an explicit null control, not two independent algorithm improvements. Document frequencies are computed separately for each candidate policy. Thus changing candidates also entails the corresponding corpus statistics, while other settings and cached POS inputs remain fixed.

## Recovered C++ execution choices

Cached modern universal tags are mapped NOUN→NN, PROPN→NNP, ADJ→JJ and all other tags→XX. This bridge preserves candidate category eligibility, but does not reproduce the original Stanford tagging, morphology distinctions or tokenization. English and Spanish inputs use this same declared category bridge; the original Spanish adaptation remains unknown.

Unfilled source parameter files do not reveal the ECIR settings. We explicitly set TextRank ratio=0.33/window=2/20 source iterations; SingleRank window=10/top=10/20 source iterations; TF-IDF top=10. These are declared diagnostic settings, not recovered author configurations.

TextRank emits phrases in document order rather than a score-sorted phrase list. The wrapper discards >3-word outputs and takes the first ten remaining phrases in source order. SingleRank/TF-IDF likewise retain the source's selected outputs and filter overlength phrases without refilling the budget. The output-order and phrase-filtering policy is a material unresolved fidelity gap. No ranking score is fabricated: placeholder zero values in local prediction records have `scores_available=false`.

The sources have an internal plural-tolerant, corpus/micro-style evaluator. That evaluator is not used as the primary project metric. Outputs are independently scored with the common exact, casefolded top-10 document-level metric; alternative plural and stem matching are reported separately.

## Evaluation, statistics and error analysis

Every saved primary prediction metric is independently recomputed using unique exact hits / 10, hits / unique gold count and `2*hits/(10+gold_count)`. The latter identity provides a separate arithmetic check of document F1. Original archived package/reconstruction baseline metrics must match the corresponding new baseline metrics on every document.

Paired two-sided t-tests and seeded bootstrap intervals are computed for **precision, recall and F1**, rather than F1 alone. Bootstrapping uses 2,000 document resamples, seed 42. Holm correction is applied within each full suite's family of contrasts/metrics. Recovered historical YAKE-versus-baseline statistics form a separate explicitly corrected 48-comparison family. Confidence intervals are pointwise, not simultaneous.

These tests follow the paper's paired-document design but cannot reproduce its significance arrows: the original per-document method outputs and exact configurations are unavailable. Corrections are additional analysis; the paper reports significance level 0.05 without this correction.

Additional diagnostics quantify annotation phrase lengths, literal phrase presence in normalized input text, document-length quartile results and Spearman length/F1 association. Literal presence is a proxy, not a proven extraction upper bound. Length associations are descriptive and cannot establish a causal length effect. An eight-example casebook shows one median-length and one largest-absolute-F1-disagreement document per dataset, with exact hits, unmatched predictions and missed literal-present reference examples. These diagnostic selections are not representative samples or causal explanations. Matching sensitivities include fixed-ten exact matching, exact matching with precision divided by the actual returned output count, one-to-one final-s plural tolerance and wordwise Porter stemming (also labelled an English-oriented diagnostic for Spanish).

Primary results are never overwritten by a different matching rule. Empty method outputs remain zero-score records. Timing includes competing processes and cache effects; no end-to-end speed claim is made from these audit runs.

## Reproduce

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv_full/bin/activate
python -m pip install -r requirements.txt
python project.py prepare
python -m unittest discover -s tests -v
python project.py audit --suite core --run results/fidelity/NEW_AUDIT/core
python project.py audit --suite history --run results/fidelity/NEW_AUDIT/history
python project.py audit --suite baselines --run results/fidelity/NEW_AUDIT/baselines
python project.py recovered-baselines --run results/fidelity/NEW_AUDIT/recovered_cpp
python project.py semeval244 --run results/fidelity/NEW_AUDIT/semeval244_stemmed
python project.py historical --run results/fidelity/NEW_AUDIT/early_releases
python project.py analyze --run results/fidelity/NEW_AUDIT
python project.py report --run results/fidelity/NEW_AUDIT
python project.py figures --run results/fidelity/NEW_AUDIT
```

The three `fidelity_experiments.py` suites support resuming their same directory with unchanged source/settings. The C++ and secondary SemEval/early-release runners start fresh output files when invoked; rerunning them replaces those selected output directories, so use a new audit directory when preserving evidence. Raw documents, recovered source archives, binaries and prediction dumps remain local and ignored. Aggregate evidence, source links/hashes and analysis code are public.

## Sources

- ECIR paper: https://doi.org/10.1007/978-3-319-76941-7_63
- PyPI release metadata: https://pypi.org/pypi/yake/json
- Archived cited baseline page: https://web.archive.org/web/20180114033255/http://www.hlt.utdallas.edu/~saidul/code.html
- Recovered baseline archive: https://web.archive.org/web/20210425074158id_/http://www.hlt.utdallas.edu/~saidul/code/Keyphrase_Extractor-1.0.zip
- Cited RAKE source: https://github.com/zelandiya/RAKE-tutorial/tree/14e153aa9cb2c02456df3880cd5fd30f7ee3aa95
- Maui archive: https://github.com/zelandiya/keyword-extraction-datasets
- Original SemEval task archive: https://github.com/snkim/AutomaticKeyphraseExtraction
- KEP wrapper/context (2020, not verified paper runtime): https://github.com/INESCTEC/kep

## Printed equations versus recovered scorer families

| Component | Printed equation / original reconstruction | PyPI 0.2.0–0.2.2 | PyPI 0.2.4 / 0.3.0 / 0.3.2 | Package 0.4.8 |
|---|---|---|---|---|
| Casing denominator | log2(tf); reconstruction guards singleton division by zero | 1 + ln(tf) | 1 + ln(tf) | 1 + ln(tf) |
| Position | log2(log2(2 + sentence-position median)); reconstruction uses one-based occurrence positions | ln(ln(3 + zero-based unique-sentence median)) | Same natural-log unique-sentence form | Same natural-log unique-sentence form |
| Frequency | tf / (mean + population standard deviation); original reconstruction uses all word types | tf / non-stopword mean; no standard deviation | tf / (non-stopword mean + standard deviation) | Same non-stopword statistics |
| Relatedness | Includes PL and PR | Includes PL and PR | Includes PL and PR | Omits PL and PR |
| Phrase scoring | Product/sum of all component word scores, divided by phrase frequency | Special internal-stopword transition factors | Special internal-stopword transition factors | Special internal-stopword transition factors |
| Term normalization | Original reconstruction casefolds only | Final-s stripping | Final-s stripping | Final-s stripping |

The printed casing equation is undefined at tf=1. The paper does not fully specify sentence indexing, stoplist identity or all tokenizer behavior. Historical source resolves those choices for that release, but does not establish that the release was used to generate the paper table. Natural-log and base-2 formulas are not interchangeable in the combined scorer.


## Independent scorer choices


`replication/core.py` implements paper equations 1–7: casing, position, frequency, relatedness, sentence spread, term score, and phrase score. Lower scores rank higher. Candidate n-grams are contiguous, at most three words, and cannot begin or end with a stopword. Similarity is 1 minus character Levenshtein distance divided by maximum length; a similarity strictly above 0.8 removes the later candidate.

The following choices resolve omissions or ambiguities and must be reported:

- Regex Unicode tokenizer; punctuation and digit tokens interrupt phrases. Sentence boundaries are whitespace after `.?!` or line breaks. This differs from the author's segtok tokenizer and may split abbreviations.
- No author-code plural stripping or hidden word normalization: casefolding only.
- Sentence positions begin at 1 so the printed position equation stays positive.
- Printed casing denominator `log2(tf)` uses 1 when tf is 1 to avoid division by zero. For tf greater than 1 the printed denominator is used directly.
- Frequency mean and population standard deviation use all observed word types. The installed author package uses non-stopword terms for these statistics.
- English stopwords come from the installed scikit-learn version, recorded in the manifest. The paper does not provide a uniquely specified stoplist in its text.
- Relatedness includes the printed PL and PR contributions. The installed package omits them.
- Phrase products and sums include every word, including internal stopwords, following the printed equation. The package has special internal-stopword transition weighting.
- Alphabetical ordering resolves exact score ties deterministically.
- Neighborhood window is one preceding/following word inside the same punctuation block.

These are explicit engineering choices, not experimentally verified original settings. Do not tune them against the evaluation labels and then call the scores unbiased replication results.


## Legacy workflows

The initial news-only runner, adapted baseline evaluation, old plotting helpers, overlapping reports, and original figure exports are retained in the evidence ZIP and Git history. The active CLI focuses on the four-dataset comparison and completed fidelity audit. Original full prediction JSONL files and raw datasets were never part of the public archive. To recompute extraction matching, produce them by running the experiments locally.
