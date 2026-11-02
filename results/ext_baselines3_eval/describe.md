# R3-1 descriptive (not ruled; D-07 development)

## 1. Sensitivity: cluster bootstrap B = 20000 (same seed), descriptive

- tolerant_v4: Holm 0.05 W 20 / T 7 / L 1, E-cell {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}, statement d, losses ['pselect_union_v3_cal @ T150 missing-0.5']; Holm 0.025 W 19 / T 8 / L 1, E-cell {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}, statement d, losses ['pselect_union_v3_cal @ T150 missing-0.5']
- tolerant_v5_1: Holm 0.05 W 27 / T 1 / L 0, E-cell {'80|0.2': True, '80|0.5': True, '150|0.2': True, '150|0.5': False}, statement b, losses []; Holm 0.025 W 27 / T 1 / L 0, E-cell {'80|0.2': True, '80|0.5': True, '150|0.2': True, '150|0.5': False}, statement b, losses []

Comparisons whose Holm-0.05 class differs between B = 4000 and B = 20000: (see describe.json)

- tolerant_v4|pselect_union_v3|150|0.5: T -> W

## 2. Compute budget per call

Seconds: median of 6 calls per T in ONE process on D-07H development (timing.json; load 5-11). `info_seconds` = median wall time inside the D-07 run (3 workers in parallel with other agents), where the method records it.

| method | draws per call | s/call T80 | s/call T150 | info_seconds D-07 T80 | T150 |
|---|---|---|---|---|---|
| tolerant_v4 | 199 bootstrap refits (repair/orientation redrawn per draw) | 0.56 | 0.66 | nan | nan |
| tolerant_v5_1 | 199 bootstrap refits with lag re-selection per draw | 1.27 | 1.44 | nan | nan |
| pselect_union_v3(_cal) | 199 per orientation member; see info n_draws | 8.34 | 11.42 | 7.21 | 10.42 |
| pselect_cal | <=16 graphs x max(10, 199 // n_graphs) draws (round-1 pselect_union) | 0.28 | 0.36 | 0.24 | 0.34 |
| fullvar_cal | 199 bootstrap refits | 0.51 | 0.61 | 0.48 | 0.60 |
| targeted_lp(_cal) | 199 single-level VAR-sieve draws (cal shares them) | 0.31 | 0.40 | nan | nan |
| tlp2_db_p3 | MSDB B1 = 200 first-level x B2 = 100 second-level draws | 5.14 | 6.03 | nan | nan |
| bvar_minnesota_v2(_cal) | 199 posterior draws (cal shares them) | 0.09 | 0.08 | nan | nan |

pselect_union_v3 at T80 (D-07, 120 runs): mean n_graphs 16.00, n_members 32.00, n_members_ok 32.00, n_draws 6368.00, n_selected 18.19, n_unoriented 9.34

pselect_union_v3 at T150 (D-07, 120 runs): mean n_graphs 16.00, n_members 32.00, n_members_ok 32.00, n_draws 6368.00, n_selected 22.88, n_unoriented 10.82

Whole D-07 run (9 methods, 2160 rows, 3 workers): 954.4 s.

## 3. Strongest baseline per cell (by IS; among the 7 envelope members)

| cell | strongest | IS | cov | strongest with cov >= 0.90 | v4 IS | v5_1 IS |
|---|---|---|---|---|---|---|
| T80 missing-0.2 | pselect_union_v3_cal | 3.36 | 0.936 | pselect_union_v3_cal | 3.28 | 2.84 |
| T80 missing-0.5 | pselect_union_v3_cal | 3.40 | 0.943 | pselect_union_v3_cal | 3.37 | 3.10 |
| T150 missing-0.2 | pselect_union_v3_cal | 1.91 | 0.962 | pselect_union_v3_cal | 2.06 | 1.76 |
| T150 missing-0.5 | pselect_union_v3_cal | 2.00 | 0.967 | pselect_union_v3_cal | 2.22 | 1.99 |

## 4. Extra paired comparisons (row minus column, mean IS difference [95% CI], B = 4000; no Holm family, descriptive)

| T | cell | a | b | a - b [95% CI] |
|---|---|---|---|---|
| 80 | missing-0.2 | tolerant_v4 | pselect_union_v2 | -1.14 [-1.68, -0.63] |
| 80 | missing-0.5 | tolerant_v4 | pselect_union_v2 | -1.19 [-1.64, -0.77] |
| 150 | missing-0.2 | tolerant_v4 | pselect_union_v2 | -0.10 [-0.30, +0.07] |
| 150 | missing-0.5 | tolerant_v4 | pselect_union_v2 | -0.07 [-0.25, +0.07] |
| 80 | missing-0.2 | tolerant_v4 | pselect_union_v2_cal | -1.22 [-1.63, -0.82] |
| 80 | missing-0.5 | tolerant_v4 | pselect_union_v2_cal | -1.19 [-1.49, -0.89] |
| 150 | missing-0.2 | tolerant_v4 | pselect_union_v2_cal | -0.10 [-0.30, +0.07] |
| 150 | missing-0.5 | tolerant_v4 | pselect_union_v2_cal | -0.07 [-0.25, +0.07] |
| 80 | missing-0.2 | tolerant_v4 | targeted_lp | -0.18 [-0.39, +0.01] |
| 80 | missing-0.5 | tolerant_v4 | targeted_lp | -0.74 [-1.00, -0.49] |
| 150 | missing-0.2 | tolerant_v4 | targeted_lp | -0.18 [-0.34, -0.03] |
| 150 | missing-0.5 | tolerant_v4 | targeted_lp | -0.45 [-0.66, -0.25] |
| 80 | missing-0.2 | tolerant_v5_1 | tolerant_v4 | -0.43 [-0.55, -0.33] |
| 80 | missing-0.5 | tolerant_v5_1 | tolerant_v4 | -0.27 [-0.40, -0.14] |
| 150 | missing-0.2 | tolerant_v5_1 | tolerant_v4 | -0.30 [-0.36, -0.24] |
| 150 | missing-0.5 | tolerant_v5_1 | tolerant_v4 | -0.23 [-0.30, -0.16] |
| 80 | missing-0.2 | tolerant_v5_1 | pselect_union_v2 | -1.57 [-2.12, -1.07] |
| 80 | missing-0.5 | tolerant_v5_1 | pselect_union_v2 | -1.46 [-1.86, -1.08] |
| 150 | missing-0.2 | tolerant_v5_1 | pselect_union_v2 | -0.39 [-0.59, -0.23] |
| 150 | missing-0.5 | tolerant_v5_1 | pselect_union_v2 | -0.30 [-0.49, -0.14] |
| 80 | missing-0.2 | tolerant_v5_1 | pselect_union_v2_cal | -1.65 [-2.07, -1.26] |
| 80 | missing-0.5 | tolerant_v5_1 | pselect_union_v2_cal | -1.46 [-1.74, -1.20] |
| 150 | missing-0.2 | tolerant_v5_1 | pselect_union_v2_cal | -0.39 [-0.59, -0.23] |
| 150 | missing-0.5 | tolerant_v5_1 | pselect_union_v2_cal | -0.30 [-0.49, -0.14] |
| 80 | missing-0.2 | tolerant_v5_1 | targeted_lp | -0.62 [-0.83, -0.41] |
| 80 | missing-0.5 | tolerant_v5_1 | targeted_lp | -1.01 [-1.24, -0.79] |
| 150 | missing-0.2 | tolerant_v5_1 | targeted_lp | -0.48 [-0.65, -0.31] |
| 150 | missing-0.5 | tolerant_v5_1 | targeted_lp | -0.68 [-0.92, -0.43] |
| 80 | missing-0.2 | pselect_union_v3 | pselect_union_v2 | -0.91 [-1.42, -0.45] |
| 80 | missing-0.5 | pselect_union_v3 | pselect_union_v2 | -0.98 [-1.41, -0.61] |
| 150 | missing-0.2 | pselect_union_v3 | pselect_union_v2 | -0.01 [-0.18, +0.14] |
| 150 | missing-0.5 | pselect_union_v3 | pselect_union_v2 | +0.03 [-0.13, +0.17] |
| 80 | missing-0.2 | pselect_union_v3 | pselect_union_v2_cal | -0.99 [-1.37, -0.65] |
| 80 | missing-0.5 | pselect_union_v3 | pselect_union_v2_cal | -0.98 [-1.23, -0.77] |
| 150 | missing-0.2 | pselect_union_v3 | pselect_union_v2_cal | -0.01 [-0.18, +0.14] |
| 150 | missing-0.5 | pselect_union_v3 | pselect_union_v2_cal | +0.03 [-0.13, +0.17] |
| 80 | missing-0.2 | pselect_union_v3_cal | pselect_union_v2 | -1.05 [-1.56, -0.58] |
| 80 | missing-0.5 | pselect_union_v3_cal | pselect_union_v2 | -1.16 [-1.53, -0.84] |
| 150 | missing-0.2 | pselect_union_v3_cal | pselect_union_v2 | -0.24 [-0.43, -0.09] |
| 150 | missing-0.5 | pselect_union_v3_cal | pselect_union_v2 | -0.29 [-0.44, -0.15] |
| 80 | missing-0.2 | pselect_union_v3_cal | pselect_union_v2_cal | -1.13 [-1.54, -0.74] |
| 80 | missing-0.5 | pselect_union_v3_cal | pselect_union_v2_cal | -1.16 [-1.40, -0.93] |
| 150 | missing-0.2 | pselect_union_v3_cal | pselect_union_v2_cal | -0.24 [-0.43, -0.09] |
| 150 | missing-0.5 | pselect_union_v3_cal | pselect_union_v2_cal | -0.29 [-0.44, -0.15] |

Cell stats of the extra methods:

- pselect_union_v2: T80 m0.2 IS 4.41 cov 0.877, T80 m0.5 IS 4.56 cov 0.878, T150 m0.2 IS 2.15 cov 0.965, T150 m0.5 IS 2.29 cov 0.967
- pselect_union_v2_cal: T80 m0.2 IS 4.49 cov 0.940, T80 m0.5 IS 4.56 cov 0.937, T150 m0.2 IS 2.15 cov 0.965, T150 m0.5 IS 2.29 cov 0.967
- targeted_lp: T80 m0.2 IS 3.46 cov 0.939, T80 m0.5 IS 4.11 cov 0.901, T150 m0.2 IS 2.24 cov 0.931, T150 m0.5 IS 2.67 cov 0.904
