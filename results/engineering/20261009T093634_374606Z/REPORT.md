# Selected-benchmark experimental reproduction

Documents: 500. No training phase.

| Method | P@10 | Recall | Macro F1 | Mean seconds/document |
|---|---:|---:|---:|---:|
| paper-equations | 0.4000 | 0.0979 | 0.1506 | 0.04040 |
| YAKE-package | 0.2036 | 0.0498 | 0.0762 | 0.00952 |
| without-WCase | 0.4284 | 0.1048 | 0.1616 | 0.03524 |
| without-WPosition | 0.3690 | 0.0921 | 0.1408 | 0.04833 |
| without-WFreq | 0.4132 | 0.1007 | 0.1552 | 0.03782 |
| without-WRel | 0.2800 | 0.0660 | 0.1027 | 0.05426 |
| without-WSpread | 0.4052 | 0.0989 | 0.1524 | 0.03977 |

Scores do not establish exact agreement with the 2018 paper. See ENGINEERING_PROTOCOL.md for preprocessing and equation ambiguities.
Bootstrap intervals compare matched document F1 values; they are not the paper's paired t-test.
Ablations are defined engineering interventions, not claimed original-paper experiments.
