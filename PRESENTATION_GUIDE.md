# Demonstrating the complete selected experiment

This is an experimental replication of one dataset, not a from-scratch recreation of YAKE or the entire paper. Present the attribution and deviations in README.md. There is no training stage: YAKE computes statistics and ranks phrases separately for each document. TF-IDF fits corpus statistics; this is not supervised learning.

## Reproducible commands

1. Activate environment: `source .venv/bin/activate`.
2. Generate the actual pipeline trace: `python walkthrough.py`.
3. Run a small check: `python evaluate.py --limit 5`.
4. Run the complete selected collection: `python evaluate.py`.
5. Make the comparison chart: `python plot_results.py`.
6. Demonstrate an unseen paragraph: `python main.py --text "Your paragraph"`.

## What to show, in order

- Paper title, research question, scope: YAKE compared with two baseline adaptations on 500N-KPCrowd.
- Dataset provenance and integrity: `results/walkthrough/00_dataset_audit.json`, 500 matched documents and annotations, categories and checksum.
- Input document: `01_document.txt`.
- Preprocessing: `02_sentences.json`, token/term inventory in `03_word_features.csv`.
- Five features: casing, position, normalized frequency, context relatedness, sentence spread. Explain how they combine into term scores. These CSV values come from the installed YAKE 0.4.8 implementation.
- Candidate construction: `04_candidates.csv`, including rejected candidates and their scores. Explain 1–3 word phrases and stopword boundaries.
- Ranking and duplicate removal: `05_final_keywords.csv`. Lower scores indicate greater relevance. Settings: top 10, Levenshtein, threshold 0.8.
- Human annotations: `06_gold_keywords.json`; inspect matched and missed phrases.
- Baselines: explain functions in evaluate.py; flag their adaptations.
- Evaluation: exact phrase matching, P@10, recall, per-document F1 averaged over collection. No accuracy metric or train/test split is required for this unsupervised extraction study.
- Results: `results/full/summary.json`, `comparison.png`, `per_document.csv`, `metadata.json`.
- Error analysis: inspect `predictions.json` for missed phrases, long phrases, absent gold phrases and duplicate candidates. Do not claim causality from one example.
- Limitations: one dataset, current package, different baseline preprocessing. Compare the paper's numbers with the same metric and mention protocol differences; do not claim an exact reproduction.

Full run console prints progress every 50 documents. All persistent evidence is regenerated from code. Screenshots are optional; genuine artifacts and a live rerun are stronger evidence. Do not fabricate training logs. Explain and adapt the work yourself in accordance with your course's original-work policy.
