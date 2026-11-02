# P5 TLP spec (docs/ext/tlp3.md): DEVELOPMENT / NOT CONFIRMATORY

Rows 3360, duplicates 0, expected runs per cell 60, min paired ok runs per cell 54. Failed rows by method: {'tolerant_v4': 3, 'targeted_lp': 0, 'tlp2_db': 7, 'tlp2_db_p3': 0}.
Config check: skipped (dev mode). v4 realisation vs ext_v51_p4h2: skipped (dev mode).

| cell | v4 cov / IS | targeted_lp | tlp2_db | tlp2_db_p3 |
|---|---|---|---|---|
| 80|none|0.0 | 0.933 / 2.50 (ok 60) | 0.955 / 3.10 (ok 60) | 0.924 / 3.91 (ok 60) | 0.916 / 2.87 (ok 60) |
| 80|extra|0.2 | 0.946 / 2.53 (ok 60) | 0.953 / 3.13 (ok 60) | 0.926 / 3.83 (ok 60) | 0.915 / 2.94 (ok 60) |
| 80|extra|0.5 | 0.948 / 2.65 (ok 60) | 0.955 / 3.16 (ok 60) | 0.921 / 3.96 (ok 60) | 0.912 / 2.98 (ok 60) |
| 80|missing|0.2 | 0.956 / 3.24 (ok 60) | 0.933 / 3.46 (ok 60) | 0.881 / 4.71 (ok 60) | 0.858 / 3.95 (ok 60) |
| 80|missing|0.5 | 0.960 / 3.39 (ok 60) | 0.898 / 4.17 (ok 60) | 0.686 / 5.98 (ok 53) | 0.797 / 5.47 (ok 60) |
| 80|reversed|0.2 | 0.945 / 2.83 (ok 60) | 0.950 / 3.40 (ok 60) | 0.917 / 4.36 (ok 60) | 0.898 / 3.41 (ok 60) |
| 80|reversed|0.5 | 0.931 / 2.99 (ok 60) | 0.929 / 3.94 (ok 60) | 0.899 / 5.05 (ok 60) | 0.853 / 4.53 (ok 60) |
| 150|none|0.0 | 0.964 / 1.56 (ok 60) | 0.959 / 1.87 (ok 60) | 0.946 / 1.83 (ok 60) | 0.943 / 1.80 (ok 60) |
| 150|extra|0.2 | 0.898 / 1.61 (ok 57) | 0.955 / 1.89 (ok 60) | 0.942 / 1.91 (ok 60) | 0.939 / 1.85 (ok 60) |
| 150|extra|0.5 | 0.968 / 1.65 (ok 60) | 0.955 / 1.91 (ok 60) | 0.935 / 2.02 (ok 60) | 0.942 / 1.86 (ok 60) |
| 150|missing|0.2 | 0.972 / 2.06 (ok 60) | 0.931 / 2.26 (ok 60) | 0.913 / 2.35 (ok 60) | 0.915 / 2.34 (ok 60) |
| 150|missing|0.5 | 0.969 / 2.19 (ok 60) | 0.908 / 2.60 (ok 60) | 0.864 / 3.06 (ok 60) | 0.869 / 2.99 (ok 60) |
| 150|reversed|0.2 | 0.971 / 1.89 (ok 60) | 0.926 / 2.66 (ok 60) | 0.913 / 2.71 (ok 60) | 0.903 / 2.71 (ok 60) |
| 150|reversed|0.5 | 0.957 / 2.06 (ok 60) | 0.863 / 3.73 (ok 60) | 0.847 / 3.99 (ok 60) | 0.833 / 4.08 (ok 60) |

## v4 − X, IS, 95% CI (topology bootstrap 10000), p two-sided, Holm p within 12 damaged cells

| cell | − targeted_lp | − tlp2_db | − tlp2_db_p3 |
|---|---|---|---|
| 80|none|0.0 | -0.60 [-0.90, -0.29] p=0.0002 | -1.41 [-1.89, -0.96] p=0.0001 | -0.37 [-0.54, -0.20] p=0.0001 |
| 80|extra|0.2 | -0.60 [-0.88, -0.31] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.31 [-1.79, -0.84] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.41 [-0.58, -0.23] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|extra|0.5 | -0.52 [-0.78, -0.26] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.31 [-1.75, -0.87] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.33 [-0.50, -0.16] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|missing|0.2 | -0.22 [-0.42, -0.02] p=0.0280 pH=0.0280 gate=v4 pure=v4 | -1.47 [-1.94, -1.02] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.71 [-1.00, -0.44] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|missing|0.5 | -0.78 [-1.07, -0.50] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.54 [-3.14, -2.01] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.07 [-2.50, -1.66] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|reversed|0.2 | -0.56 [-0.78, -0.31] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.53 [-2.23, -0.89] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.57 [-0.77, -0.37] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|reversed|0.5 | -0.95 [-1.21, -0.69] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.06 [-2.74, -1.50] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.53 [-1.85, -1.22] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|none|0.0 | -0.31 [-0.44, -0.17] p=0.0001 | -0.27 [-0.39, -0.14] p=0.0001 | -0.24 [-0.36, -0.11] p=0.0001 |
| 150|extra|0.2 | -0.28 [-0.41, -0.15] p=0.0001 pH=0.0012 gate=tie pure=v4 | -0.31 [-0.44, -0.18] p=0.0001 pH=0.0012 gate=tie pure=v4 | -0.25 [-0.35, -0.15] p=0.0001 pH=0.0012 gate=tie pure=v4 |
| 150|extra|0.5 | -0.26 [-0.38, -0.14] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.36 [-0.50, -0.23] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.21 [-0.32, -0.10] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|missing|0.2 | -0.20 [-0.36, -0.04] p=0.0114 pH=0.0228 gate=v4 pure=v4 | -0.30 [-0.45, -0.15] p=0.0002 pH=0.0012 gate=v4 pure=v4 | -0.29 [-0.44, -0.14] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|missing|0.5 | -0.41 [-0.57, -0.23] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.87 [-1.08, -0.66] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.80 [-0.97, -0.62] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|reversed|0.2 | -0.76 [-1.13, -0.49] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.81 [-1.15, -0.55] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.82 [-1.26, -0.49] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|reversed|0.5 | -1.67 [-2.13, -1.25] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.93 [-2.51, -1.43] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.02 [-2.59, -1.53] p=0.0001 pH=0.0012 gate=v4 pure=v4 |

## Counts over the 12 damaged cells (raw / Holm)

| X | v4 wins gate | v4 wins gate Holm | v4 wins pure | v4 wins pure Holm | X wins gate | X wins gate Holm | X wins pure | X wins pure Holm |
|---|---|---|---|---|---|---|---|---|
| targeted_lp | 11 | 11 | 12 | 12 | 0 | 0 | 0 | 0 |
| tlp2_db | 11 | 11 | 12 | 12 | 0 | 0 | 0 | 0 |
| tlp2_db_p3 | 11 | 11 | 12 | 12 | 0 | 0 | 0 | 0 |

## Verdict: **NOT CONFIRMED (incomplete: tlp2_db@80|missing|0.5)**

