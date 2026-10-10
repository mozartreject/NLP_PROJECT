# Individual submission and demonstration

**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**

## Review before submission

- Review PROJECT_REPORT.md, EXPANDED_PROTOCOL.md and the full comparison table.
- Confirm instructor approval of the selected paper/scope if still required.
- Describe the work as four-dataset experimental comparison with current implementations and independent equation reconstruction, not exact publication-time equivalence.
- Explain the SemEval archive count difference: 243 available versus 244 described.
- Distinguish modern POS-filtered PKE baselines from the earlier adapted RAKE/TF-IDF experiments.
- Do not call higher scores proof of a better original algorithm; preprocessing/settings are different.
- Commit code, dependencies, tests, report, config/protocol, manifests, aggregate results and per-document metrics.
- Keep raw data, paper PDF, environments, full predictions and POS caches local.
- Check that the public GitHub link exposes the report and full expanded results.
- Submit the repository link according to the assignment instructions.

## 8-minute demonstration

1. Identify the paper and explain document-to-keyword extraction (45 seconds).
2. Show all four dataset counts and languages from the manifest (45 seconds).
3. Explain YAKE's five features and the independent word/phrase scorer (60 seconds).
4. Run 16 tests and explain one arithmetic and one POS/IDF test (45 seconds).
5. Show median-length package and independent traces from results/expanded_walkthrough; explain a selected/rejected phrase (60 seconds).
6. Show all four paper-versus-run tables and the four-panel comparison chart (90 seconds).
7. Explain modern PKE baselines, corpus IDF and pretrained POS tagging (45 seconds).
8. Explain reconstruction differences, SemEval count mismatch and why scores are not controlled improvements (45 seconds).
9. Show immutable evidence and resume capability (30 seconds).

## Commands

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv_full/bin/activate
python -m unittest discover -s tests -v
open "$HOME/Desktop/NLP_PROJECT/results/expanded/20261009T100336_607448Z"
```

A smoke run is a separate experiment. Present the complete expanded run above, not the newest small run. The earlier engineering_demo.py selects the latest engineering run and only covers 500N; it is not the four-dataset visualization.

## Questions to prepare

**Where is training?** YAKE and graph/statistical keyword scoring do not have supervised training in this project. POS models are pretrained dependencies; TF-IDF computes unlabeled collection statistics.

**Did you reproduce the whole table?** We ran all four datasets and all five named methods using declared current implementations, plus our reconstruction. Original executable/configuration identity is unresolved, and SemEval has one fewer available document.

**What did you implement?** Independent equation reconstruction, Unicode RAKE, experiment integration, evidence generation and evaluation. PKE/YAKE package algorithms and POS models are attributed reused code.

**Why do the numbers differ?** Known tokenizer, candidate, stoplist, POS-model and scoring differences remain. Their individual effects have not all been experimentally isolated.

**Are your significance tests the paper's tests?** They compare our own paired document outputs. Original per-document author outputs are unavailable; exploratory p-values are unadjusted for multiple comparisons.
