# NLP project presentation script

**Joshua Rebello · SAP ID 70562200090 · B.Tech AI & DS, 4th year**

**Format:** approximately 12–15 minutes, using the GitHub README from top to bottom, with a short VS Code terminal demonstration. The quoted paragraphs are your speaking script. The “Show” lines tell you what to display. Practise explaining each claim in your own words; do not describe reused libraries as your own algorithms.

## Before the presentation

Open the repository README: https://github.com/mozartreject/NLP_PROJECT. Open VS Code with the local NLP_PROJECT folder. Have the terminal ready, and prepare the local walkthrough files before presenting:

```bash
cd "$HOME/Desktop/NLP_PROJECT"
source .venv_full/bin/activate
python full_walkthrough.py
```

This exports example traces for all four datasets. It chooses the median-length document, rather than choosing an example because it performed well. It may take time; prepare it in advance. Raw datasets and the installed environment must already be available locally.

Keep the authoritative complete results folder visible in VS Code:

```text
results/expanded/20261009T100336_607448Z/
```

Use that saved full run for the results discussion. A new smoke run is a separate small experiment and must not replace the complete results. Do not run the complete benchmark during the presentation; it took approximately 30 minutes in the saved run.

## 1. Title and introduction — 45 seconds

**Show:** the README title and author information.

> “Good morning. I am Joshua Rebello, SAP ID 70562200090, from B.Tech AI and Data Science, fourth year. My project is an experimental reproduction and comparison of the YAKE keyword extraction paper, ‘A Text Feature Based Automatic Keyword Extraction Method for Single Documents,’ published at ECIR 2018 in Springer’s proceedings.
>
> The problem is to take a document and automatically identify its important words and phrases. For example, a document about language technology might produce phrases such as ‘natural language processing’ or ‘keyword extraction.’ The task is to extract useful phrases from the document, rather than generate a summary.”

## 2. Overview and exact scope — 45 seconds

**Show:** Overview.

> “I selected this paper because it provides an interpretable approach using document-level text statistics, and its experiments can be investigated without training a large neural network.
>
> The project evaluates all four datasets and all five named methods in the paper’s comparison table. I also added an independent reconstruction of the printed YAKE equations. That gives six configurations, 3,614 documents and 21,684 document-configuration evaluations.
>
> This is a four-dataset experimental reproduction using declared current implementations. I am not claiming that the original publication-time executable and settings have been reproduced exactly.”

**Transition:** “I will first explain the implementation, then the data, and finally the results and evidence.”

## 3. Project structure — 30 seconds

**Show:** Project Structure. Point to the files; do not read the whole tree.

> “The independent equation scorer is in replication/core.py. The expanded experiment runner is full_comparison.py. The tests check scoring and evaluation behavior. The walkthrough exports intermediate computations, and the results folder stores the metrics and run manifest. The README and protocols document the decisions needed to interpret the experiments.”

## 4. Key paper concepts — 75 seconds

**Show:** Key Paper Concepts Implemented.

> “YAKE uses five local word features. Casing captures evidence such as acronyms and capitalized terms. Position captures where a word appears. Frequency measures how often it occurs relative to document statistics. Relatedness describes its neighboring-word context. Sentence spread measures how widely it appears across sentences.
>
> The scorer combines these features into word scores, builds candidate phrases of up to three words, and calculates phrase scores. Candidate filtering and near-duplicate removal then produce the final ranked keywords. Lower YAKE scores indicate greater relevance; they are not probabilities.
>
> There is no supervised training phase for YAKE in this project. The work happens through feature computation and keyword ranking. Some baselines use pretrained POS tagging, and TF-IDF computes unlabeled corpus statistics.”

**If asked about equations:** open replication/core.py and ENGINEERING_PROTOCOL.md. Explain the actual implementation and safeguards; do not improvise a formula from memory.

## 5. Datasets — 45 seconds

**Show:** the dataset table.

> “The datasets cover different domains and two languages. SemEval2010 contains 243 available English computer-science documents. Schutz2008 contains 1,231 English medical documents. 500N-KPCrowd contains 500 English news documents. WICC contains 1,640 Spanish documents.
>
> Each document is paired with human reference keywords, called gold keywords. The loader checks the document counts, IDs and paired annotations, and records archive hashes.
>
> The paper reports 244 SemEval documents, but the available archive provides 243. I retained the available data and documented the discrepancy rather than adding a synthetic example.”

## 6. Setup and running the code — 90 seconds

**Show:** Setup & Installation, then Running the Code. Switch to the prepared terminal.

> “The project runs locally in a Python virtual environment on my Mac. Dependencies and model versions are recorded so another person can recreate the setup. I will demonstrate the tests and a small cross-dataset run. The full experiment has already been completed and its evidence is saved.”

Run:

```bash
python -m unittest discover -s tests -v
```

> “The suite now contains 31 tests. These include arithmetic checks, candidate and boundary behavior, duplicate handling, and evaluation behavior. Passing them checks important implementation properties; it does not by itself prove agreement with the original paper.”

Run:

```bash
python full_comparison.py --limit 2
```

> “This is a smoke experiment using two documents per dataset. It demonstrates that the pipeline executes across all four datasets and configurations. Its scores are based on a tiny sample, so I will use the archived complete run for scientific conclusions.”

If the smoke run takes too long, continue to the saved trace and return to its output later. Do not treat a partial run as a complete benchmark.

## 7. Show one real extraction trace — 90 seconds

**Show:** results/expanded_walkthrough/500N-KPCrowd/ in VS Code. Open the following files in order.

1. **00_audit.json** — dataset count, source hash, sample ID and selection rule.
2. **01_document.txt** — the actual input document.
3. **04_package_word_features.csv** — real package feature values and word scores.
4. **05_package_candidates.csv** — candidate phrases, eligibility and scores.
5. **06_ranked_predictions.csv** — package and independent rankings, with exact-match flags.
6. **07_gold.json** — the human reference keywords.

> “This example was selected by median document length. Here is its original text. These rows show the actual feature values computed by the package, followed by its candidate phrases. The final table shows the ranked outputs from both the package and the independent reconstruction, together with exact matches against the gold annotations.
>
> I can follow a phrase from the input through scoring to the final output. I can also inspect a missed gold phrase. A phrase may be meaningful but receive no credit if it does not exactly match a reference phrase under our evaluation rule.”

**Point to an actual row before discussing it.** Do not invent a matched or missed phrase. The package CSVs describe the package; the independent calculations are stored in **03_independent_trace.json**. **02_pos_sentences.json**, when present, shows shared POS preprocessing for the baselines.

## 8. Experiment settings and baselines — 45 seconds

**Show:** Experiment Settings.

> “The extraction settings include up to three-word candidates and a top-ten output budget. The comparison includes YAKE-package, TextRank-PKE, TF-IDF-PKE, SingleRank-PKE and RAKE-local, plus the independent reconstruction.
>
> TextRank and SingleRank use word graphs; SingleRank uses weighted edges. The PKE baselines use a declared common POS-filtered candidate scheme. TF-IDF uses collection document frequencies, so this experiment is transductive. These preprocessing and implementation choices are important when comparing with the published results.”

## 9. Results tables — 60 seconds

**Show:** Results, Tables 1–3. Explain examples rather than reading every cell.

> “Table 1 pairs the published F1 with our measured F1 for each method and dataset. For example, the published YAKE SemEval score is 0.1230 and our package result is 0.1207. They are close, but that alone does not establish exact replication.
>
> On news, the package scores 0.0762 and the independent reconstruction scores 0.1506. On the other three datasets, the reconstruction scores below the package. This shows why one successful dataset is not enough to claim a better implementation.
>
> Tables 2 and 3 separate precision, recall and F1, so the comparison is not restricted to one aggregate number.”

## 10. Ablation study — 30 seconds

**Show:** Feature Ablation Study.

> “An ablation removes one feature while retaining the rest of the configuration. I performed five such interventions on the independent reconstruction using the 500 news documents.
>
> Removing relatedness creates the largest observed drop, from 0.1506 to 0.1027. Removing casing increases the score on this dataset. These are exploratory findings on news, not original-paper ablations or a validated improvement across all datasets.”

## 11. Walk through the four figures — 90 seconds

**Show:** Generated Figures, scrolling through one figure at a time.

**Figure 1 — scorecard**

> “The first figure answers which method performs best within each dataset. Darker cells show higher F1, and gold outlines identify the highest measured score. YAKE-package leads on SemEval and WICC; TF-IDF-PKE leads on Schutz and news. No configuration wins everywhere.”

**Figure 2 — published versus measured**

> “Gray points show the paper and blue points show our experiment. Each line joins the two values for one method. All panels use the same score scale. The differences are descriptive: changes in implementations and preprocessing prevent us from treating a higher score as proof that we improved the paper.”

**Figure 3 — two YAKE implementations**

> “Blue circles represent the package, and teal diamonds represent the independent reconstruction. Precision, recall and F1 are displayed separately. The reconstruction improves the news result but performs worse on the other datasets.”

**Figure 4 — feature removal**

> “Zero means no change from the full reconstruction. Moving left means feature removal hurts; moving right means it helps. The whiskers show paired bootstrap 95% intervals from 2,000 resamples. Relatedness removal has the largest negative effect here: about 4.80 F1 percentage points.”

## 11A. Present the completed fidelity audit — 2 minutes

**Show:** the README’s Completed Fidelity Audit section, Figures 5 and 6, then FIDELITY_REPORT.md and one example from results/fidelity/20261010_audit/CASEBOOK.md. This extends the presentation to approximately 14–17 minutes; shorten the earlier setup walkthrough if your time is limited.

> “After the initial comparison, I investigated the remaining replication gaps. I inventoried all six available preconference or conference-era YAKE releases and executed all three distinct scorer families with windows one and two. I also recovered and executed the cited-page C++ baseline family and a preconference RAKE snapshot. These sources still use declared current dependency and POS inputs, so recovery does not establish exact historical execution.
>
> I repeated all five feature ablations across all four valid primary collections and ran thirteen controlled scoring and preprocessing sensitivities. Figure 5 shows why feature importance cannot be inferred from news alone: removing relatedness hurts news but improves the Spanish result in this reconstruction.
>
> Figure 6 shows that source version and window settings change measured F1. I did not select whichever combination happened to look closest to the paper and call it the original system.
>
> I also investigated SemEval’s missing document, C-86. Its Maui keyword file is empty. The original task archive provides stemmed labels, allowing a separate evaluation of all 244 texts. Those scores use a different annotation and matching protocol and are not mixed into the paper table.
>
> The audit includes paired tests for precision, recall and F1, bootstrap intervals, multiple-comparison corrections and matching and length diagnostics. Every result remains linked to saved evidence.”

**If asked what remains:** “The exact author executable and dependency settings, original tagged baseline inputs and parameter files, comparable unstemmed C-86 gold and the authors’ original per-document outputs remain unavailable. Further sweeps cannot establish those historical facts.”

## 12. Evaluation and reproducibility — 60 seconds

**Show:** Evaluation & Reproducibility; open summary.json, manifest.json and EVIDENCE_VALIDATION.json from the authoritative full-run folder.

> “Precision at ten is the number of unique exact hits divided by ten. Recall is the number of hits divided by the number of unique gold keywords. F1 combines precision and recall for each document, and the reported macro F1 is the average of those document F1 scores.
>
> Matching normalizes case and whitespace, with no stemming or partial-match credit. Empty outputs remain in the evaluation. For example, four news documents produced no RAKE phrases and were retained with zero scores.
>
> The manifest records data and source hashes, versions and settings. The per-document file contains all 21,684 records. The saved prediction metrics were independently recomputed against the gold annotations and matched. The figures are regenerated from archived summaries, with input hashes recorded for provenance.”

## 13. Reports, dependencies and attribution — 30 seconds

**Show:** Reports & Presentation Guide, Dependencies Summary, then Reference & Attribution.

> “The report documents the complete experiment. The protocols explain baseline settings and equation ambiguities. I implemented the independent scorer, local RAKE, experiment integration and evidence and evaluation workflow. The YAKE package, PKE algorithms and pretrained language models are reused dependencies and are explicitly credited.
>
> The project demonstrates an auditable reproduction workflow: document the assumptions, inspect intermediate computations, evaluate across multiple datasets and report differences honestly.”

**Finish:** “Thank you. I can now show a particular implementation step or discuss any of the comparisons.”

## Optional live unseen-text demo

Use this only if there is time or the examiner asks for a new input:

```bash
python main.py --text "Natural language processing helps computers analyze human language. Keyword extraction identifies important phrases in documents. Unsupervised keyword extraction uses local text statistics without labeled training examples."
```

Say: “This demonstrates the packaged extractor on a fresh paragraph. The output is an extraction example, not a benchmark score, because we have not provided human gold annotations.”

## Viva answers to practise

**Did you fully replicate the paper?**

“All four datasets and all five named comparison methods were evaluated using declared current implementations, plus an independent reconstruction. Exact publication-time executable equivalence remains unresolved, and SemEval has one fewer available document. I describe the result as an experimental reproduction with documented differences.”

**Where is the training?**

“YAKE computes local statistics without supervised training. POS tagging uses pretrained models. TF-IDF computes unlabeled corpus statistics. There are no project training epochs to display.”

**Why is F1 relatively low?**

“We return only ten phrases, some documents have many gold keywords, and matching is exact. Semantically related phrases can receive no credit. Scores must be interpreted with the annotation scheme and extraction budget; they are not classification accuracy.”

**Are your results better than the paper?**

“Some are higher and some lower, but implementation and evaluation differences prevent a controlled improvement claim. The strongest comparisons are between configurations within our own declared experiment.”

**Why does removing casing help?**

“It improves this reconstruction on this news benchmark. That is an observed ablation effect; it does not prove casing is generally harmful. Establishing a broader explanation would require further controlled experiments.”

**Why use the package and an independent reconstruction?**

“The package provides a reusable reference, while the reconstruction exposes the printed equations and permits feature-level interventions. Their different results reveal the importance of implementation choices.”

**Why no train/test split?**

“YAKE does not fit a supervised model. The collections serve as evaluation benchmarks. TF-IDF uses collection document frequencies and is declared transductive; evaluating deployment on unseen collections would require a separate protocol.”

**What do the confidence intervals mean?**

“They show bootstrap uncertainty in the mean paired F1 difference using resampled documents from this benchmark. They are pointwise, exploratory intervals, not comparisons against unavailable original-paper document outputs or guarantees across all domains.”

**Which method is fastest?**

“The saved times exclude shared POS preprocessing and corpus document-frequency construction. I would not use them to claim an end-to-end speed winner.”

**What would you improve next?**

“Those follow-up experiments are now completed and reported separately. The next fidelity step requires original author execution artifacts or clarification. Any new performance claim would also require a separately designed evaluation rather than choosing a sensitivity variant after seeing these benchmarks.”

## If you have only eight minutes

Use sections 1–2 for the introduction, combine sections 3–5 into one minute, show tests and one prepared trace without a live smoke run, then focus on Figures 1, 2 and 4. Explain evaluation and the replication limits before closing. Keep setup commands and the detailed result tables available for questions.

## Claims to avoid

- “I trained YAKE” or “these are training curves.”
- “My F1 is my accuracy.”
- “My reconstruction is better on every dataset.”
- “Higher values prove I improved the published system.”
- “I implemented the YAKE package, PKE or the pretrained POS models.”
- “The smoke-run output is our full result.”
- “The confidence intervals reproduce the paper’s original significance tests.”
