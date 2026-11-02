# Confirmatory analysis (results/ext_baselines2_dryrun_p4h2)

## C1

| T | cell | X | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p one-sided | p two-sided | CI pass | Holm pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | missing-0.2 | pselect_union_v2 | 0.959 | 3.28 | 4.41 | 0.877 | -1.14 [-1.68, -0.63] | 0.0002 | 0.0005 | pass | pass |
| 80 | missing-0.5 | pselect_union_v2 | 0.957 | 3.37 | 4.56 | 0.878 | -1.19 [-1.66, -0.79] | 0.0002 | 0.0005 | pass | pass |
| 80 | missing-0.2 | pselect_union_v2_cal | 0.959 | 3.28 | 4.49 | 0.940 | -1.22 [-1.63, -0.81] | 0.0002 | 0.0005 | pass | pass |
| 80 | missing-0.5 | pselect_union_v2_cal | 0.957 | 3.37 | 4.56 | 0.937 | -1.19 [-1.48, -0.89] | 0.0002 | 0.0005 | pass | pass |

**C1: PASS** (Holm over 4: 4/4; CI only: 4/4)

## C2

| T | cell | X | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p one-sided | p two-sided | CI pass | Holm pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | missing-0.2 | bvar_minnesota_v2_cal | 0.959 | 3.28 | 4.86 | 0.958 | -1.58 [-1.94, -1.26] | 0.0002 | 0.0005 | pass | pass |
| 80 | missing-0.5 | bvar_minnesota_v2_cal | 0.957 | 3.37 | 4.58 | 0.958 | -1.21 [-1.41, -1.00] | 0.0002 | 0.0005 | pass | pass |
| 150 | missing-0.2 | bvar_minnesota_v2_cal | 0.968 | 2.06 | 3.71 | 0.968 | -1.65 [-1.89, -1.43] | 0.0002 | 0.0005 | pass | pass |
| 150 | missing-0.5 | bvar_minnesota_v2_cal | 0.962 | 2.22 | 3.63 | 0.962 | -1.42 [-1.58, -1.26] | 0.0002 | 0.0005 | pass | pass |

**C2: PASS** (Holm over 4: 4/4; CI only: 4/4)

## D

| T | cell | X | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p one-sided | p two-sided | CI pass | Holm pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 150 | missing-0.2 | pselect_union_v2 | 0.968 | 2.06 | 2.15 | 0.965 | -0.10 [-0.30, +0.08] | 0.1587 | 0.3174 | FAIL | FAIL |
| 150 | missing-0.5 | pselect_union_v2 | 0.962 | 2.22 | 2.29 | 0.967 | -0.07 [-0.24, +0.08] | 0.1875 | 0.3749 | FAIL | FAIL |
| 150 | missing-0.2 | pselect_union_v2_cal | 0.968 | 2.06 | 2.15 | 0.965 | -0.10 [-0.29, +0.08] | 0.1570 | 0.3139 | FAIL | FAIL |
| 150 | missing-0.5 | pselect_union_v2_cal | 0.962 | 2.22 | 2.29 | 0.967 | -0.07 [-0.24, +0.08] | 0.2037 | 0.4074 | FAIL | FAIL |

D is descriptive: no verdict.

