# Individual submission and demonstration

**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**

## Review before submission

- Review PROJECT_REPORT.md, FIDELITY_REPORT.md, FIDELITY_PROTOCOL.md and the full comparison table.
- Use PRESENTATION_SCRIPT.md for the complete walkthrough, including historical sources, all-dataset ablations and diagnostic evidence.
- Confirm instructor approval of the selected paper/scope if still required.
- Describe the work as four-dataset experimental comparison with current implementations and independent equation reconstruction, not exact publication-time equivalence.
- Explain primary SemEval: 243 nonempty-gold pairs; C-86 text recovered but its Maui gold is empty. Present the separate 244-text stemmed-task evaluation under its own protocol.
- Distinguish modern POS-filtered PKE baselines from the earlier adapted RAKE/TF-IDF experiments.
- Do not call higher scores proof of a better original algorithm; preprocessing/settings are different.
- Commit code, dependencies, tests, report, config/protocol, manifests, aggregate results and per-document metrics.
- Keep raw data, paper PDF, environments, full predictions and POS caches local.
- Check that the public GitHub link exposes the report and full expanded results.
- Submit the repository link according to the assignment instructions.

## Short demonstration (full script in PRESENTATION_SCRIPT.md)

1. Identify the paper and explain document-to-keyword extraction (45 seconds).
2. Show all four dataset counts and languages from the manifest (45 seconds).
3. Explain YAKE's five features and the independent word/phrase scorer (60 seconds).
4. Run 31 tests and explain one arithmetic and one POS/IDF test (45 seconds).
5. Show median-length package and independent traces from results/expanded_walkthrough; explain a selected/rejected phrase (60 seconds).
6. Show all four paper-versus-run tables and the four-panel comparison chart (90 seconds).
7. Explain modern PKE baselines, corpus IDF and pretrained POS tagging (45 seconds).
8. Show the completed fidelity audit and its four externally unresolved historical facts (45 seconds).
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

**Did you reproduce the whole table?** We ran all four datasets and all five named methods using declared current implementations, plus our reconstruction. Original executable/configuration identity is unresolved, and primary SemEval has 243 usable exact-match pairs. A separate 244-text stemmed-task experiment is complete.

**What did you implement?** Independent equation reconstruction, Unicode RAKE, experiment integration, evidence generation and evaluation. PKE/YAKE package algorithms and POS models are attributed reused code.

**Why do the numbers differ?** Known tokenizer, candidate, stoplist, POS-model and scoring differences remain. Thirteen one-choice sensitivities were measured on all four datasets; combined interactions and original author choices remain unresolved.

**Are your significance tests the paper's tests?** They compare our own paired document outputs. Original per-document author outputs are unavailable; the follow-up audit adds two-sided paired tests and Holm correction within declared comparison families. Original author outputs remain unavailable.

## Completed follow-up evidence

Present `results/fidelity/20261010_audit/REPORT.md` and `EVIDENCE_VALIDATION.json` alongside the original expanded run. The audit retains all five ablations across all four datasets, thirteen controlled sensitivities, recovered historical implementations, baseline candidate-policy controls, matching/length diagnostics and the separate 244-document stemmed evaluation. Historical execution uses current dependencies; do not describe it as an identified original runtime.
