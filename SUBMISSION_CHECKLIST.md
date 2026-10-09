# Demonstration and submission checklist

## Before submission

- Confirm the author details: Joshua Rebello, SAP ID 70562200090, B.Tech AI & DS, 4th year.
- Review the report and be able to explain each code component.
- Confirm the selected paper/scope has instructor approval where required by the course policy.
- Keep the title and claims as selected-benchmark reproduction, not exact full-paper replication.
- Confirm the actual full-run folder: results/engineering/20261009T093634_374606Z.
- Include report, protocol, source code, requirements, configs, tests and selected results in the repository.
- Include manifest.json, summary.json, per_document.csv, paired_intervals.json and comparison.png from the full run.
- Raw data, .venv and full prediction dumps are excluded by the ignore rules. Keep source download instructions and dataset hash available.
- Check rights before publishing the paper PDF or dataset sample text. Trace JSON/CSV can contain source text or phrases.
- Create a public GitHub repository when ready, check the public link, and submit only the repository link as directed by the assignment.

## Suggested 6–8 minute demonstration

1. Explain the input/output task and identify the ECIR paper (45 seconds).
2. Explain why YAKE needs no supervised training (30 seconds).
3. Show dataset count and archive hash in the full-run manifest (30 seconds).
4. Run the eight unit tests and explain the hand-calculated score check (45 seconds).
5. Show sample_trace.json and exported feature/candidate/decision CSV files; trace one retained and one rejected phrase (90 seconds).
6. Show the 500-document report and comparison chart, not a five-document smoke chart (60 seconds).
7. Explain the largest ablation drop and the casing improvement without claiming universal conclusions (45 seconds).
8. Show the paper's Table 1 and describe the reproduction gap and implementation choices (60 seconds).
9. Explain evidence folders and repeatability (30 seconds).

## Safe presentation commands

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv/bin/activate
python -m unittest discover -s tests -v
open "$HOME/Desktop/NLP_PROJECT/results/engineering/20261009T093634_374606Z"
```

A smoke run creates a newer folder. `engineering_demo.py` selects the latest completed run, even if it has only five documents. For the final presentation, open the full-run folder above explicitly, or rerun the full experiment before generating the chart. Always check the chart's document count.

## Likely questions

**Where is training?** There is no supervised training. The system computes document-local statistics and scores candidates directly.

**Is it an exact replication?** No. It is a selected-benchmark reproduction with an independent equation reconstruction; preprocessing and ambiguous formula choices are documented.

**Why is recall low?** Only ten predictions are allowed, while the normalized gold sets average about 49 phrases; exact matching also rejects variants and partial matches.

**Why do your scores differ from the paper?** Known code/formula and preprocessing differences exist. Their separate effects have not all been isolated, so we do not claim a single proven cause.

**What did you implement?** The independent scorer, experiment/evidence pipeline, ablations and evaluation integration. The YAKE package is an attributed reference implementation.

**Why not select the best ablation as your main result?** The ablations are exploratory findings on the evaluated benchmark; selecting a winner requires independent validation to support a new-method claim.
