# Engineering protocol: YAKE ECIR 2018

## Scope and claim

Selected paper: Campos et al., *A Text Feature Based Automatic Keyword Extraction Method for Single Documents*, ECIR 2018, Springer LNCS 10772, 684–691. DOI: 10.1007/978-3-319-76941-7_63.

This project is a **selected-benchmark experimental reproduction and independent reconstruction of printed equations**, not a verified exact reproduction of all original experiments. The original paper evaluates four datasets. We currently evaluate the 500-document 500N-KPCrowd news dataset. Existing `evaluate.py` results remain a package-based reproduction with adapted baselines; the new pipeline does not replace those evidence files.

No neural model, labels, or gradient-based training is involved in YAKE. Gold keywords are read only for evaluation and recorded alongside the example trace. Extraction depends only on document text. Show the computation stages rather than claiming training epochs.

## Independent implementation

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

## Reference and historical source audit

The package reference uses the installed YAKE version with identical exposed n-gram, window, top-k and deduplication settings. It is independently compared against the reconstruction rather than treated as proof of printed-equation fidelity.

Historical author source inspected at commit `36b3f0967cbef4048261c33845eb036163c6f278` (16 November 2018), `yake/datarepresentation.py`:
https://github.com/INESCTEC/yake/blob/36b3f0967cbef4048261c33845eb036163c6f278/yake/datarepresentation.py

This source already omits PL/PR, uses natural-log casing and position formulas, and adds internal-stopword weighting. It postdates the conference publication. Thus neither that historical implementation nor the current package is assumed to be the exact code used for the paper's reported table.

## Evaluation

All 500 document IDs must be unique; paired gold-keyword files must exist and be nonempty. The archive SHA-256 is recorded. There is no train/test split for the single-document algorithm. The earlier TF-IDF adaptation uses corpus-wide unsupervised IDF statistics and must be described as transductive.

Primary matching is case-insensitive exact phrase matching with whitespace normalization. Precision is hits divided by configured k, including unfilled slots. Recall is hits divided by unique gold phrases. Primary F1 is the mean of per-document F1. The report also saves the harmonic mean of macro precision and recall, because these are different quantities. No stemming, substring credit or silently discarded failed documents.

Matched document F1 differences receive a seeded 2,000-resample paired bootstrap interval. This is an additional engineering analysis; it does not reproduce the paper's paired t-test. The interval covers document resampling uncertainty under this evaluation protocol, not all sources of replication uncertainty.

Ablations remove casing/frequency/spread denominator contributions by setting them to 0; remove position/relatedness multiplicative effects by setting them to 1. These are defined interventions, not original-paper experiments. Configurations and results must remain unchanged after evaluating gold labels.

## Commands and demonstration

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv/bin/activate
python -m unittest discover -s tests -v
python run_replication.py --limit 5 --ablations
python run_replication.py --ablations
python engineering_demo.py
```

Each execution creates a new UTC-stamped folder in `results/engineering`. A complete run contains:

1. `manifest.json`: document IDs, archive hash, source hashes, Python/package versions, config, completion status and elapsed time.
2. `sample_trace.json`: document, sentence tokens, per-word feature values, term scores, every phrase candidate, filtering and deduplication decisions, and gold labels.
3. `predictions.json`: every method's ranked keyword scores for every document.
4. `per_document.csv`: paired metrics, extraction timing and keyword count.
5. `summary.json`: aggregated scores and both F1 conventions.
6. `paired_intervals.json`: matched bootstrap contrasts.
7. `REPORT.md`: human-readable actual results.
8. `comparison.png`: generated by the demonstration utility.

During the presentation, open the original paper, show the documented equation differences, run the unit tests, run a five-document smoke experiment, then show the complete 500-document report and sample trace. Explain weak examples using the predictions and gold phrases. Present the actual ranking even if another method wins.

`walkthrough.py` still shows actual author-package intermediate values. `sample_trace.json` now shows the independently computed values. Use both to demonstrate why they differ.

## Attribution and limitations

Credit the paper, author YAKE implementation, INESCTEC dataset repository and scikit-learn stoplist. The independent reconstruction is new project code; the package reference is reused upstream software. An installed library run alone is not a from-scratch algorithm implementation.

This reconstruction has no POS filtering, and previous RAKE/TF-IDF baselines are adaptations. It cannot establish that YAKE's original comparative claims fail or hold. Differences may come from tokenizer, stopwords, printed-equation ambiguities, gold matching, implementation version and metric aggregation. Timings include extraction and trace construction, not dataset loading, bootstrap analysis or plotting; hardware and workload affect them.

Do not redistribute the downloaded paper or raw dataset on public GitHub without checking their licenses. Preserve download links, dataset hashes and setup instructions; the existing ignore file excludes raw data and full prediction dumps. Review gold/text traces before publishing because those contain sample dataset text. Ask the instructor to approve the selected scope if that course-policy step has not already happened.
