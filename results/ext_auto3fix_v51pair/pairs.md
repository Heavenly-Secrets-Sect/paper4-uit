# D3: tolerant_auto3 vs tolerant_v5_1 on stored D-07 a2-grid rows (descriptive, no rule)

Pairing: tolerant_v4 rows identical on 1260/1260 common keys (ext_gate_auto3 vs ext_v51_eval).
auto3 does not read the stated damage; v5_1 does. auto3 rows use round-1 bootstrap seeds.

| cell | cov auto3 | cov v5_1 | IS auto3 | IS v5_1 | auto3 - v5_1 [95% CI] | p | Holm(21) | call |
|---|---|---|---|---|---|---|---|---|
| 40|none|0.0 | 0.952 | 0.920 | 4.93 | 4.37 | +0.56 [+0.15, +0.95] | 0.0070 | no | auto3 worse |
| 40|extra|0.2 | 0.958 | 0.914 | 4.81 | 4.63 | +0.18 [-0.27, +0.60] | 0.4040 | no | tie |
| 40|extra|0.5 | 0.960 | 0.920 | 5.01 | 4.81 | +0.20 [-0.31, +0.70] | 0.4110 | no | tie |
| 40|missing|0.2 | 0.911 | 0.922 | 8.56 | 4.84 | +3.73 [+2.91, +4.56] | 0.0000 | yes | auto3 worse |
| 40|missing|0.5 | 0.954 | 0.939 | 8.97 | 5.09 | +3.88 [+2.96, +5.00] | 0.0000 | yes | auto3 worse |
| 40|reversed|0.2 | 0.943 | 0.928 | 5.12 | 4.70 | +0.41 [+0.05, +0.80] | 0.0260 | no | auto3 worse |
| 40|reversed|0.5 | 0.926 | 0.920 | 5.53 | 4.74 | +0.79 [+0.36, +1.24] | 0.0000 | yes | auto3 worse |
| 80|none|0.0 | 0.947 | 0.939 | 2.68 | 2.53 | +0.15 [+0.03, +0.26] | 0.0220 | no | auto3 worse |
| 80|extra|0.2 | 0.954 | 0.927 | 2.67 | 2.53 | +0.14 [-0.03, +0.31] | 0.1110 | no | tie |
| 80|extra|0.5 | 0.949 | 0.925 | 2.77 | 2.67 | +0.10 [-0.01, +0.20] | 0.0750 | no | tie |
| 80|missing|0.2 | 0.951 | 0.949 | 3.48 | 2.84 | +0.64 [+0.39, +1.05] | 0.0000 | yes | auto3 worse |
| 80|missing|0.5 | 0.949 | 0.951 | 3.40 | 3.10 | +0.30 [+0.17, +0.44] | 0.0000 | yes | auto3 worse |
| 80|reversed|0.2 | 0.932 | 0.941 | 2.87 | 2.79 | +0.08 [+0.00, +0.17] | 0.0500 | no | auto3 worse |
| 80|reversed|0.5 | 0.903 | 0.918 | 3.44 | 3.05 | +0.40 [+0.26, +0.56] | 0.0000 | yes | auto3 worse |
| 150|none|0.0 | 0.985 | 0.963 | 1.87 | 1.57 | +0.30 [+0.21, +0.40] | 0.0000 | yes | auto3 worse |
| 150|extra|0.2 | 0.982 | 0.963 | 1.87 | 1.60 | +0.27 [+0.20, +0.35] | 0.0000 | yes | auto3 worse |
| 150|extra|0.5 | 0.981 | 0.963 | 1.89 | 1.68 | +0.22 [+0.16, +0.29] | 0.0000 | yes | auto3 worse |
| 150|missing|0.2 | 0.980 | 0.966 | 2.34 | 1.76 | +0.58 [+0.50, +0.66] | 0.0000 | yes | auto3 worse |
| 150|missing|0.5 | 0.980 | 0.968 | 2.40 | 1.99 | +0.41 [+0.31, +0.53] | 0.0000 | yes | auto3 worse |
| 150|reversed|0.2 | 0.971 | 0.959 | 2.11 | 1.83 | +0.28 [+0.19, +0.39] | 0.0000 | yes | auto3 worse |
| 150|reversed|0.5 | 0.966 | 0.943 | 2.33 | 2.03 | +0.30 [+0.16, +0.46] | 0.0000 | yes | auto3 worse |

- all21: better/tie/worse 0/4/17; Holm better 0, Holm worse 13
- T40: better/tie/worse 0/2/5; Holm better 0, Holm worse 3
- T80_150: better/tie/worse 0/2/12; Holm better 0, Holm worse 10
- missing_reversed_T80_150: better/tie/worse 0/0/8; Holm better 0, Holm worse 7
