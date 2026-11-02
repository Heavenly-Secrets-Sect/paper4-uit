# R3-1 rule check (D-07 development, exploratory)

Runs: results/ext_baselines3_eval (all methods except tlp2_db_p3), tlp2_db_p3 from results/ext_tlp2_t80b + ext_tlp2_t150c (content seeded). 20 topologies.

Regression (fresh vs stored rows; expected 0): tolerant_v4 vs ext_baselines2_eval: 0/240, bvar_minnesota_v2_cal vs ext_baselines2_eval: 0/240, tolerant_v5_1 vs ext_v51_eval: 0/240, pselect_cal vs ext_redteam_calbase: 240/240, fullvar_cal vs ext_redteam_calbase: 240/240, targeted_lp vs ext_tlp_eval: 240/240, targeted_lp_cal vs ext_tlp_eval: 240/240

| m | X | T | cell | cov m | IS m | IS X | cov X | m - X [95% CI] | p2 | raw | Holm 0.05 | Holm 0.025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.50 | 0.960 | -0.22 [-0.37, -0.05] | 0.0200 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.36 | 0.936 | -0.09 [-0.27, +0.10] | 0.3504 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.88 | 0.961 | -0.60 [-0.79, -0.42] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.44 | 0.960 | -0.17 [-0.26, -0.08] | 0.0010 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.51 | 0.956 | -0.23 [-0.42, -0.05] | 0.0130 | W | T | T |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.95 | 0.858 | -0.67 [-0.96, -0.40] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.959 | 3.28 | 4.86 | 0.958 | -1.58 [-1.91, -1.26] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.5 | 0.957 | 3.37 | 3.58 | 0.965 | -0.21 [-0.37, -0.02] | 0.0245 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.40 | 0.943 | -0.03 [-0.20, +0.14] | 0.7453 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.07 | 0.944 | -0.70 [-0.86, -0.55] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.86 | 0.950 | -0.49 [-0.65, -0.33] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.95 | 0.925 | -0.58 [-0.78, -0.39] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.5 | 0.957 | 3.37 | 5.47 | 0.797 | -2.10 [-2.53, -1.71] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.58 | 0.958 | -1.21 [-1.42, -0.99] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.15 | 0.986 | -0.09 [-0.16, -0.02] | 0.0070 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.2 | 0.968 | 2.06 | 1.91 | 0.962 | +0.15 [+0.04, +0.25] | 0.0085 | L | T | T |
| tolerant_v4 | pselect_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.56 | 0.981 | -0.50 [-0.62, -0.39] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.58 | 0.981 | -0.52 [-0.63, -0.42] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.978 | -0.29 [-0.38, -0.19] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.915 | -0.29 [-0.44, -0.14] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.968 | 2.06 | 3.71 | 0.968 | -1.65 [-1.88, -1.44] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.32 | 0.991 | -0.11 [-0.18, -0.03] | 0.0065 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.00 | 0.967 | +0.22 [+0.14, +0.30] | 0.0005 | L | L | T |
| tolerant_v4 | pselect_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.86 | 0.955 | -0.65 [-0.82, -0.48] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.95 | 0.962 | -0.73 [-0.85, -0.62] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.59 | 0.960 | -0.38 [-0.50, -0.26] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.99 | 0.869 | -0.78 [-0.94, -0.60] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.962 | 2.22 | 3.63 | 0.962 | -1.42 [-1.58, -1.27] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.50 | 0.960 | -0.66 [-0.79, -0.52] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.36 | 0.936 | -0.52 [-0.67, -0.37] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.88 | 0.961 | -1.04 [-1.20, -0.88] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.44 | 0.960 | -0.60 [-0.75, -0.47] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.51 | 0.956 | -0.66 [-0.86, -0.47] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.95 | 0.858 | -1.11 [-1.35, -0.86] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.949 | 2.84 | 4.86 | 0.958 | -2.02 [-2.33, -1.72] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.5 | 0.951 | 3.10 | 3.58 | 0.965 | -0.48 [-0.62, -0.32] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.40 | 0.943 | -0.30 [-0.44, -0.15] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.07 | 0.944 | -0.97 [-1.13, -0.81] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.86 | 0.950 | -0.76 [-0.94, -0.58] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.95 | 0.925 | -0.85 [-1.03, -0.67] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.5 | 0.951 | 3.10 | 5.47 | 0.797 | -2.36 [-2.75, -2.02] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.58 | 0.958 | -1.48 [-1.68, -1.28] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.15 | 0.986 | -0.39 [-0.44, -0.33] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.2 | 0.966 | 1.76 | 1.91 | 0.962 | -0.15 [-0.23, -0.07] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.56 | 0.981 | -0.80 [-0.90, -0.71] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.58 | 0.981 | -0.82 [-0.93, -0.72] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.978 | -0.58 [-0.70, -0.46] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.915 | -0.58 [-0.74, -0.43] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.966 | 1.76 | 3.71 | 0.968 | -1.95 [-2.17, -1.73] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.32 | 0.991 | -0.34 [-0.41, -0.26] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.00 | 0.967 | -0.01 [-0.08, +0.05] | 0.7788 | T | T | T |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.86 | 0.955 | -0.87 [-1.06, -0.71] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.95 | 0.962 | -0.96 [-1.08, -0.85] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.59 | 0.960 | -0.61 [-0.77, -0.44] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.99 | 0.869 | -1.01 [-1.20, -0.79] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.968 | 1.99 | 3.63 | 0.962 | -1.65 [-1.79, -1.51] | 0.0005 | W | W | T |

## tolerant_v4

- coverage >= 0.90 in 4/4 cells; failure rates: T80 m0.2: 0/60, T80 m0.5: 0/60, T150 m0.2: 0/60, T150 m0.5: 0/60
- Holm 0.05 over 56: W 19 / T 8 / L 1 (of 28); E-cell: {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}
- E-full False, E-noloss False, E-major True -> statement **(d) có so sánh thua**
- losses: ['pselect_union_v3_cal @ T150 missing-0.5']
- raw CI counts: W 24 / L 2 (of 28)
- Bonferroni overlay (Holm 0.025): W 0 / T 28 / L 0; E-cell {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}; statement c

## tolerant_v5_1

- coverage >= 0.90 in 4/4 cells; failure rates: T80 m0.2: 0/60, T80 m0.5: 0/60, T150 m0.2: 0/60, T150 m0.5: 0/60
- Holm 0.05 over 56: W 27 / T 1 / L 0 (of 28); E-cell: {'80|0.2': True, '80|0.5': True, '150|0.2': True, '150|0.5': False}
- E-full False, E-noloss True, E-major True -> statement **(b) không thua; thắng envelope ở một số cell**
- losses: none
- raw CI counts: W 27 / L 0 (of 28)
- Bonferroni overlay (Holm 0.025): W 0 / T 28 / L 0; E-cell {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}; statement c

