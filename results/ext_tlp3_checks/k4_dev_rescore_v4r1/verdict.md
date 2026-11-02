# P5 TLP spec (docs/ext/tlp3.md): DEVELOPMENT / NOT CONFIRMATORY

Rows 3360, duplicates 0, expected runs per cell 60, min paired ok runs per cell 54. Failed rows by method: {'tolerant_v4': 0, 'targeted_lp': 0, 'tlp2_db': 0, 'tlp2_db_p3': 0}.
Config check: skipped (dev mode). v4 realisation vs ext_v51_p4h2: skipped (dev mode).

| cell | v4 cov / IS | targeted_lp | tlp2_db | tlp2_db_p3 |
|---|---|---|---|---|
| 80|none|0.0 | 0.933 / 2.50 (ok 60) | 0.955 / 3.10 (ok 60) | 0.924 / 3.91 (ok 60) | 0.916 / 2.87 (ok 60) |
| 80|extra|0.2 | 0.946 / 2.53 (ok 60) | 0.953 / 3.13 (ok 60) | 0.926 / 3.83 (ok 60) | 0.915 / 2.94 (ok 60) |
| 80|extra|0.5 | 0.948 / 2.65 (ok 60) | 0.955 / 3.16 (ok 60) | 0.921 / 3.96 (ok 60) | 0.912 / 2.98 (ok 60) |
| 80|missing|0.2 | 0.959 / 3.28 (ok 60) | 0.933 / 3.46 (ok 60) | 0.881 / 4.71 (ok 60) | 0.858 / 3.95 (ok 60) |
| 80|missing|0.5 | 0.957 / 3.37 (ok 60) | 0.898 / 4.17 (ok 60) | 0.825 / 6.00 (ok 60) | 0.797 / 5.47 (ok 60) |
| 80|reversed|0.2 | 0.948 / 2.79 (ok 60) | 0.950 / 3.40 (ok 60) | 0.917 / 4.36 (ok 60) | 0.898 / 3.41 (ok 60) |
| 80|reversed|0.5 | 0.929 / 2.97 (ok 60) | 0.929 / 3.94 (ok 60) | 0.899 / 5.05 (ok 60) | 0.853 / 4.53 (ok 60) |
| 150|none|0.0 | 0.964 / 1.56 (ok 60) | 0.959 / 1.87 (ok 60) | 0.946 / 1.83 (ok 60) | 0.943 / 1.80 (ok 60) |
| 150|extra|0.2 | 0.965 / 1.58 (ok 60) | 0.955 / 1.89 (ok 60) | 0.942 / 1.91 (ok 60) | 0.939 / 1.85 (ok 60) |
| 150|extra|0.5 | 0.967 / 1.66 (ok 60) | 0.955 / 1.91 (ok 60) | 0.935 / 2.02 (ok 60) | 0.942 / 1.86 (ok 60) |
| 150|missing|0.2 | 0.968 / 2.06 (ok 60) | 0.931 / 2.26 (ok 60) | 0.913 / 2.35 (ok 60) | 0.915 / 2.34 (ok 60) |
| 150|missing|0.5 | 0.962 / 2.22 (ok 60) | 0.908 / 2.60 (ok 60) | 0.864 / 3.06 (ok 60) | 0.869 / 2.99 (ok 60) |
| 150|reversed|0.2 | 0.970 / 1.89 (ok 60) | 0.926 / 2.66 (ok 60) | 0.913 / 2.71 (ok 60) | 0.903 / 2.71 (ok 60) |
| 150|reversed|0.5 | 0.959 / 2.02 (ok 60) | 0.863 / 3.73 (ok 60) | 0.847 / 3.99 (ok 60) | 0.833 / 4.08 (ok 60) |

## v4 − X, IS, 95% CI (topology bootstrap 10000), p two-sided, Holm p within 12 damaged cells

| cell | − targeted_lp | − tlp2_db | − tlp2_db_p3 |
|---|---|---|---|
| 80|none|0.0 | -0.60 [-0.90, -0.29] p=0.0002 | -1.41 [-1.89, -0.96] p=0.0001 | -0.37 [-0.54, -0.20] p=0.0001 |
| 80|extra|0.2 | -0.60 [-0.88, -0.31] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.31 [-1.79, -0.84] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.41 [-0.58, -0.23] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|extra|0.5 | -0.52 [-0.78, -0.26] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.31 [-1.75, -0.87] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.33 [-0.50, -0.16] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|missing|0.2 | -0.18 [-0.38, +0.02] p=0.0788 pH=0.0788 gate=tie pure=tie | -1.43 [-1.92, -0.97] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.67 [-0.96, -0.40] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|missing|0.5 | -0.80 [-1.07, -0.55] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.63 [-3.17, -2.13] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.10 [-2.50, -1.70] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|reversed|0.2 | -0.61 [-0.83, -0.35] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.57 [-2.26, -0.95] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.61 [-0.81, -0.41] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|reversed|0.5 | -0.98 [-1.23, -0.71] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.08 [-2.75, -1.53] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.56 [-1.87, -1.25] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|none|0.0 | -0.31 [-0.44, -0.17] p=0.0001 | -0.27 [-0.39, -0.14] p=0.0001 | -0.24 [-0.36, -0.11] p=0.0001 |
| 150|extra|0.2 | -0.31 [-0.43, -0.18] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.33 [-0.46, -0.21] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.27 [-0.37, -0.17] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|extra|0.5 | -0.26 [-0.38, -0.13] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.36 [-0.49, -0.23] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.21 [-0.32, -0.10] p=0.0004 pH=0.0012 gate=v4 pure=v4 |
| 150|missing|0.2 | -0.20 [-0.36, -0.05] p=0.0068 pH=0.0136 gate=v4 pure=v4 | -0.30 [-0.45, -0.15] p=0.0002 pH=0.0012 gate=v4 pure=v4 | -0.29 [-0.44, -0.14] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|missing|0.5 | -0.38 [-0.55, -0.20] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.85 [-1.05, -0.64] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.78 [-0.94, -0.60] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|reversed|0.2 | -0.76 [-1.14, -0.48] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.81 [-1.16, -0.54] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.82 [-1.27, -0.48] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|reversed|0.5 | -1.71 [-2.19, -1.27] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.97 [-2.57, -1.46] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.07 [-2.65, -1.55] p=0.0001 pH=0.0012 gate=v4 pure=v4 |

## Counts over the 12 damaged cells (raw / Holm)

| X | v4 wins gate | v4 wins gate Holm | v4 wins pure | v4 wins pure Holm | X wins gate | X wins gate Holm | X wins pure | X wins pure Holm |
|---|---|---|---|---|---|---|---|---|
| targeted_lp | 11 | 11 | 11 | 11 | 0 | 0 | 0 | 0 |
| tlp2_db | 12 | 12 | 12 | 12 | 0 | 0 | 0 | 0 |
| tlp2_db_p3 | 12 | 12 | 12 | 12 | 0 | 0 | 0 | 0 |

## Verdict: **CONFIRMED-A'**

