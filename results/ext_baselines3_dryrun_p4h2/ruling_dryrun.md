# Spec P7 ruling (DEV DRY RUN on D-07 development: pipeline test, NOT a result)

Validity: PASS

| m | X | T | cell | cov m | IS m | IS X | cov X | m - X [95% CI] | p2 | raw | Holm 0.05 | Holm 0.025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.50 | 0.960 | -0.22 [-0.37, -0.05] | 0.0157 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.36 | 0.936 | -0.09 [-0.27, +0.10] | 0.3577 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.88 | 0.961 | -0.60 [-0.79, -0.42] | 0.0001 | W | W | W |
| tolerant_v4 | fullvar_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.44 | 0.960 | -0.17 [-0.26, -0.08] | 0.0006 | W | W | W |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.51 | 0.956 | -0.23 [-0.42, -0.04] | 0.0119 | W | T | T |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.95 | 0.858 | -0.67 [-0.96, -0.40] | 0.0001 | W | W | W |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.959 | 3.28 | 4.86 | 0.958 | -1.58 [-1.94, -1.26] | 0.0001 | W | W | W |
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.5 | 0.957 | 3.37 | 3.58 | 0.965 | -0.21 [-0.37, -0.03] | 0.0235 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.40 | 0.943 | -0.03 [-0.19, +0.14] | 0.7496 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.07 | 0.944 | -0.70 [-0.86, -0.55] | 0.0001 | W | W | W |
| tolerant_v4 | fullvar_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.86 | 0.950 | -0.49 [-0.64, -0.33] | 0.0001 | W | W | W |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.95 | 0.925 | -0.58 [-0.78, -0.40] | 0.0001 | W | W | W |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.5 | 0.957 | 3.37 | 5.47 | 0.797 | -2.10 [-2.52, -1.70] | 0.0001 | W | W | W |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.58 | 0.958 | -1.21 [-1.42, -0.99] | 0.0001 | W | W | W |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.15 | 0.986 | -0.09 [-0.16, -0.02] | 0.0071 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.2 | 0.968 | 2.06 | 1.91 | 0.962 | +0.15 [+0.04, +0.25] | 0.0082 | L | T | T |
| tolerant_v4 | pselect_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.56 | 0.981 | -0.50 [-0.62, -0.39] | 0.0001 | W | W | W |
| tolerant_v4 | fullvar_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.58 | 0.981 | -0.52 [-0.63, -0.43] | 0.0001 | W | W | W |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.978 | -0.29 [-0.38, -0.19] | 0.0001 | W | W | W |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.915 | -0.29 [-0.44, -0.14] | 0.0002 | W | W | W |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.968 | 2.06 | 3.71 | 0.968 | -1.65 [-1.88, -1.43] | 0.0001 | W | W | W |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.32 | 0.991 | -0.11 [-0.18, -0.03] | 0.0047 | W | W | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.00 | 0.967 | +0.22 [+0.14, +0.30] | 0.0001 | L | L | L |
| tolerant_v4 | pselect_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.86 | 0.955 | -0.65 [-0.83, -0.48] | 0.0001 | W | W | W |
| tolerant_v4 | fullvar_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.95 | 0.962 | -0.73 [-0.85, -0.62] | 0.0001 | W | W | W |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.59 | 0.960 | -0.38 [-0.50, -0.26] | 0.0001 | W | W | W |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.99 | 0.869 | -0.78 [-0.94, -0.60] | 0.0001 | W | W | W |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.962 | 2.22 | 3.63 | 0.962 | -1.42 [-1.58, -1.26] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.50 | 0.960 | -0.66 [-0.79, -0.51] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.36 | 0.936 | -0.52 [-0.66, -0.37] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.88 | 0.961 | -1.04 [-1.21, -0.88] | 0.0001 | W | W | W |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.44 | 0.960 | -0.60 [-0.74, -0.47] | 0.0001 | W | W | W |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.51 | 0.956 | -0.66 [-0.87, -0.47] | 0.0001 | W | W | W |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.95 | 0.858 | -1.11 [-1.35, -0.86] | 0.0001 | W | W | W |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.949 | 2.84 | 4.86 | 0.958 | -2.02 [-2.34, -1.72] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.5 | 0.951 | 3.10 | 3.58 | 0.965 | -0.48 [-0.63, -0.32] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.40 | 0.943 | -0.30 [-0.44, -0.15] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.07 | 0.944 | -0.97 [-1.13, -0.81] | 0.0001 | W | W | W |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.86 | 0.950 | -0.76 [-0.93, -0.58] | 0.0001 | W | W | W |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.95 | 0.925 | -0.85 [-1.03, -0.67] | 0.0001 | W | W | W |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.5 | 0.951 | 3.10 | 5.47 | 0.797 | -2.36 [-2.74, -2.01] | 0.0001 | W | W | W |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.58 | 0.958 | -1.48 [-1.68, -1.28] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.15 | 0.986 | -0.39 [-0.44, -0.33] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.2 | 0.966 | 1.76 | 1.91 | 0.962 | -0.15 [-0.24, -0.07] | 0.0004 | W | W | W |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.56 | 0.981 | -0.80 [-0.90, -0.71] | 0.0001 | W | W | W |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.58 | 0.981 | -0.82 [-0.93, -0.72] | 0.0001 | W | W | W |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.978 | -0.58 [-0.70, -0.46] | 0.0001 | W | W | W |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.915 | -0.58 [-0.74, -0.44] | 0.0001 | W | W | W |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.966 | 1.76 | 3.71 | 0.968 | -1.95 [-2.18, -1.73] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.32 | 0.991 | -0.34 [-0.41, -0.26] | 0.0001 | W | W | W |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.00 | 0.967 | -0.01 [-0.08, +0.05] | 0.7583 | T | T | T |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.86 | 0.955 | -0.87 [-1.05, -0.71] | 0.0001 | W | W | W |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.95 | 0.962 | -0.96 [-1.08, -0.85] | 0.0001 | W | W | W |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.59 | 0.960 | -0.61 [-0.76, -0.45] | 0.0001 | W | W | W |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.99 | 0.869 | -1.01 [-1.21, -0.79] | 0.0001 | W | W | W |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.968 | 1.99 | 3.63 | 0.962 | -1.65 [-1.79, -1.51] | 0.0001 | W | W | W |

## tolerant_v4: **NOT CONFIRMED** (Holm 0.05); Bonferroni overlay (Holm 0.025): NOT CONFIRMED

- (i) coverage >= 0.90 in 4/4 cells: True (T80 m0.2 0.959, T80 m0.5 0.957, T150 m0.2 0.968, T150 m0.5 0.962)
- (ii) failure <= 2%: True (0/60, 0/60, 0/60, 0/60)
- (iii) W_D07 set confirmed: 19/19 -> True
- (iv) no L: False ['pselect_union_v3_cal|150|0.5']
- descriptive statement on these rows: (d) có so sánh thua; W 20 / T 7 / L 1; E-cell {'80|0.2': False, '80|0.5': False, '150|0.2': False, '150|0.5': False}

## tolerant_v5_1: **CONFIRMED** (Holm 0.05); Bonferroni overlay (Holm 0.025): CONFIRMED

- (i) coverage >= 0.90 in 4/4 cells: True (T80 m0.2 0.949, T80 m0.5 0.951, T150 m0.2 0.966, T150 m0.5 0.968)
- (ii) failure <= 2%: True (0/60, 0/60, 0/60, 0/60)
- (iii) W_D07 set confirmed: 27/27 -> True
- (iv) no L: True 
- descriptive statement on these rows: (b) không thua; thắng envelope ở một số cell; W 27 / T 1 / L 0; E-cell {'80|0.2': True, '80|0.5': True, '150|0.2': True, '150|0.5': False}

