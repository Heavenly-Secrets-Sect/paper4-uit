# P5 TLP spec (docs/ext/tlp3.md): DEVELOPMENT / NOT CONFIRMATORY

Rows 168, duplicates 0, expected runs per cell 3, min paired ok runs per cell 3. Failed rows by method: {'tolerant_v4': 0, 'targeted_lp': 0, 'tlp2_db': 0, 'tlp2_db_p3': 0}.
Config check: skipped (dev mode). v4 realisation vs ext_v51_p4h2: skipped (dev mode).

| cell | v4 cov / IS | targeted_lp | tlp2_db | tlp2_db_p3 |
|---|---|---|---|---|
| 80|none|0.0 | 0.942 / 2.25 (ok 3) | 0.952 / 3.69 (ok 3) | 0.904 / 4.84 (ok 3) | 0.894 / 3.17 (ok 3) |
| 80|extra|0.2 | 0.913 / 2.44 (ok 3) | 0.933 / 4.00 (ok 3) | 0.856 / 5.15 (ok 3) | 0.875 / 3.41 (ok 3) |
| 80|extra|0.5 | 0.933 / 2.78 (ok 3) | 0.894 / 4.13 (ok 3) | 0.875 / 5.35 (ok 3) | 0.846 / 4.08 (ok 3) |
| 80|missing|0.2 | 0.971 / 3.27 (ok 3) | 0.962 / 3.58 (ok 3) | 0.904 / 4.53 (ok 3) | 0.875 / 3.87 (ok 3) |
| 80|missing|0.5 | 0.981 / 3.19 (ok 3) | 0.913 / 4.03 (ok 3) | 0.856 / 4.82 (ok 3) | 0.837 / 4.65 (ok 3) |
| 80|reversed|0.2 | 0.981 / 2.26 (ok 3) | 0.933 / 4.40 (ok 3) | 0.865 / 5.12 (ok 3) | 0.894 / 4.62 (ok 3) |
| 80|reversed|0.5 | 0.981 / 2.28 (ok 3) | 0.923 / 5.42 (ok 3) | 0.913 / 5.64 (ok 3) | 0.885 / 5.30 (ok 3) |
| 150|none|0.0 | 0.981 / 1.33 (ok 3) | 0.981 / 1.88 (ok 3) | 0.942 / 1.82 (ok 3) | 0.971 / 1.58 (ok 3) |
| 150|extra|0.2 | 0.981 / 1.51 (ok 3) | 0.971 / 1.89 (ok 3) | 0.942 / 2.05 (ok 3) | 0.933 / 1.70 (ok 3) |
| 150|extra|0.5 | 0.971 / 1.56 (ok 3) | 0.962 / 1.81 (ok 3) | 0.952 / 1.83 (ok 3) | 0.933 / 1.73 (ok 3) |
| 150|missing|0.2 | 0.971 / 1.97 (ok 3) | 0.942 / 2.04 (ok 3) | 0.904 / 2.21 (ok 3) | 0.875 / 2.28 (ok 3) |
| 150|missing|0.5 | 0.962 / 1.99 (ok 3) | 0.894 / 2.41 (ok 3) | 0.856 / 2.86 (ok 3) | 0.865 / 2.82 (ok 3) |
| 150|reversed|0.2 | 0.942 / 2.20 (ok 3) | 0.933 / 2.30 (ok 3) | 0.913 / 2.70 (ok 3) | 0.913 / 2.36 (ok 3) |
| 150|reversed|0.5 | 0.885 / 2.54 (ok 3) | 0.856 / 3.93 (ok 3) | 0.837 / 3.84 (ok 3) | 0.827 / 3.94 (ok 3) |

## v4 − X, IS, 95% CI (topology bootstrap 10000), p two-sided, Holm p within 12 damaged cells

| cell | − targeted_lp | − tlp2_db | − tlp2_db_p3 |
|---|---|---|---|
| 80|none|0.0 | -1.44 [-2.30, -0.56] p=0.0001 | -2.59 [-3.25, -1.48] p=0.0001 | -0.91 [-1.77, -0.15] p=0.0001 |
| 80|extra|0.2 | -1.56 [-2.66, -0.74] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.71 [-3.53, -1.33] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.97 [-1.56, -0.33] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|extra|0.5 | -1.36 [-2.94, -0.33] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.57 [-3.62, -1.11] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.31 [-2.43, -0.38] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|missing|0.2 | -0.31 [-1.15, +0.24] p=0.5360 pH=1.0000 gate=tie pure=tie | -1.27 [-2.68, -0.25] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.60 [-1.41, +0.07] p=0.0738 pH=0.3650 gate=tie pure=tie |
| 80|missing|0.5 | -0.85 [-1.75, +0.18] p=0.0696 pH=0.4872 gate=tie pure=tie | -1.63 [-2.16, -1.05] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -1.46 [-3.65, +0.13] p=0.0760 pH=0.3650 gate=tie pure=tie |
| 80|reversed|0.2 | -2.14 [-4.47, -0.75] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.86 [-3.42, -2.41] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -2.36 [-5.28, -0.86] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 80|reversed|0.5 | -3.14 [-4.48, -1.05] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -3.36 [-4.31, -2.26] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -3.03 [-5.10, -0.50] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|none|0.0 | -0.55 [-0.89, -0.21] p=0.0001 | -0.49 [-0.79, -0.01] p=0.0001 | -0.25 [-0.34, -0.16] p=0.0001 |
| 150|extra|0.2 | -0.38 [-0.71, +0.07] p=0.0752 pH=0.4872 gate=tie pure=tie | -0.54 [-1.03, -0.05] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.19 [-0.30, -0.06] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|extra|0.5 | -0.26 [-0.41, +0.01] p=0.0732 pH=0.4872 gate=tie pure=tie | -0.27 [-0.53, +0.05] p=0.0792 pH=0.2816 gate=tie pure=tie | -0.17 [-0.27, -0.05] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|missing|0.2 | -0.07 [-0.43, +0.13] p=0.5750 pH=1.0000 gate=tie pure=tie | -0.24 [-0.95, +0.26] p=0.5076 pH=0.5076 gate=tie pure=tie | -0.31 [-0.65, +0.04] p=0.0730 pH=0.3650 gate=tie pure=tie |
| 150|missing|0.5 | -0.42 [-0.66, -0.10] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.87 [-1.43, -0.17] p=0.0001 pH=0.0012 gate=v4 pure=v4 | -0.83 [-1.36, -0.24] p=0.0001 pH=0.0012 gate=v4 pure=v4 |
| 150|reversed|0.2 | -0.10 [-0.53, +0.55] p=0.5084 pH=1.0000 gate=tie pure=tie | -0.50 [-1.17, +0.04] p=0.0726 pH=0.2816 gate=tie pure=tie | -0.16 [-0.61, +0.47] p=0.5298 pH=0.5298 gate=tie pure=tie |
| 150|reversed|0.5 | -1.39 [-2.97, +0.50] p=0.0750 pH=0.4872 gate=tie pure=tie | -1.30 [-2.16, +0.37] p=0.0704 pH=0.2816 gate=tie pure=tie | -1.40 [-3.11, +0.79] p=0.0776 pH=0.3650 gate=tie pure=tie |

## Counts over the 12 damaged cells (raw / Holm)

| X | v4 wins gate | v4 wins gate Holm | v4 wins pure | v4 wins pure Holm | X wins gate | X wins gate Holm | X wins pure | X wins pure Holm |
|---|---|---|---|---|---|---|---|---|
| targeted_lp | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| tlp2_db | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 0 |
| tlp2_db_p3 | 7 | 7 | 7 | 7 | 0 | 0 | 0 | 0 |

## Verdict: **NOT CONFIRMED**

