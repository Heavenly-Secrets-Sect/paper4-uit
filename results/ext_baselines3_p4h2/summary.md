# ext_baselines3_p4h2

FROZEN CONFIRMATORY SPEC P7 (docs/ext/baselines3.md, 'Frozen spec P7 for P4-H2'). DO NOT RUN except as the single sealed confirmatory run, through experiments/ext/baselines3/run_cells.py. tolerant_v4 and tolerant_v5_1 against the full-budget baseline envelope at T 80/150 x missing 0.2/0.5 (cell positions of the a2 kinds list kept), all width factors frozen in experiments/ext/baselines3/frozen_calibration_p7.json (D-07H development), no calibration phase.

Bank P4-H2 / confirmatory; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.974 | 0.974 | 2.685 | 3.13 | 0.405 | 0.000 | 0.302 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 2.175 | 2.68 | 0.339 | 0.000 | 0.251 |
| clean | 80 | missing | 0.2 | pselect_union_v3 | 60/60 | 0.968 | 0.974 | 2.773 | 3.46 | 0.463 | 0.061 | 0.269 |
| clean | 80 | missing | 0.2 | pselect_union_v3_cal | 60/60 | 0.943 | 0.951 | 2.357 | 3.30 | 0.463 | 0.061 | 0.269 |
| clean | 80 | missing | 0.2 | pselect_cal | 60/60 | 0.962 | 0.963 | 3.159 | 3.91 | 0.452 | 0.022 | 0.295 |
| clean | 80 | missing | 0.2 | fullvar_cal | 60/60 | 0.973 | 0.973 | 2.930 | 3.41 | 0.417 | 0.000 | 0.304 |
| clean | 80 | missing | 0.2 | targeted_lp | 60/60 | 0.940 | 0.940 | 2.539 | 3.49 | 0.425 | 0.005 | 0.288 |
| clean | 80 | missing | 0.2 | targeted_lp_cal | 60/60 | 0.955 | 0.955 | 2.793 | 3.50 | 0.425 | 0.005 | 0.288 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2_cal | 60/60 | 0.969 | 0.969 | 3.995 | 4.64 | 0.380 | 0.000 | 0.269 |
| clean | 80 | missing | 0.2 | tlp2_db_p3 | 60/60 | 0.872 | 0.873 | 1.873 | 3.71 | 0.422 | 0.007 | 0.290 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.972 | 0.972 | 2.759 | 3.18 | 0.411 | 0.000 | 0.300 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.969 | 0.969 | 2.422 | 2.89 | 0.393 | 0.000 | 0.246 |
| clean | 80 | missing | 0.5 | pselect_union_v3 | 60/60 | 0.978 | 0.981 | 2.959 | 3.41 | 0.479 | 0.063 | 0.268 |
| clean | 80 | missing | 0.5 | pselect_union_v3_cal | 60/60 | 0.952 | 0.957 | 2.515 | 3.20 | 0.479 | 0.063 | 0.268 |
| clean | 80 | missing | 0.5 | pselect_cal | 60/60 | 0.943 | 0.943 | 3.020 | 4.12 | 0.511 | 0.023 | 0.295 |
| clean | 80 | missing | 0.5 | fullvar_cal | 60/60 | 0.953 | 0.953 | 2.882 | 3.74 | 0.480 | 0.000 | 0.320 |
| clean | 80 | missing | 0.5 | targeted_lp | 60/60 | 0.912 | 0.913 | 2.603 | 3.82 | 0.525 | 0.038 | 0.454 |
| clean | 80 | missing | 0.5 | targeted_lp_cal | 60/60 | 0.940 | 0.941 | 2.863 | 3.75 | 0.525 | 0.038 | 0.454 |
| clean | 80 | missing | 0.5 | bvar_minnesota_v2_cal | 60/60 | 0.969 | 0.969 | 3.840 | 4.44 | 0.509 | 0.000 | 0.280 |
| clean | 80 | missing | 0.5 | tlp2_db_p3 | 60/60 | 0.804 | 0.813 | 1.968 | 4.83 | 0.522 | 0.047 | 0.469 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.661 | 1.98 | 0.254 | 0.000 | 0.190 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.964 | 0.964 | 1.421 | 1.75 | 0.210 | 0.000 | 0.184 |
| clean | 150 | missing | 0.2 | pselect_union_v3 | 60/60 | 0.983 | 0.983 | 1.942 | 2.15 | 0.236 | 0.005 | 0.178 |
| clean | 150 | missing | 0.2 | pselect_union_v3_cal | 60/60 | 0.950 | 0.950 | 1.554 | 1.95 | 0.236 | 0.005 | 0.178 |
| clean | 150 | missing | 0.2 | pselect_cal | 60/60 | 0.972 | 0.972 | 2.216 | 2.62 | 0.246 | 0.001 | 0.173 |
| clean | 150 | missing | 0.2 | fullvar_cal | 60/60 | 0.976 | 0.976 | 2.188 | 2.62 | 0.261 | 0.000 | 0.211 |
| clean | 150 | missing | 0.2 | targeted_lp | 60/60 | 0.932 | 0.932 | 1.508 | 2.11 | 0.243 | 0.002 | 0.209 |
| clean | 150 | missing | 0.2 | targeted_lp_cal | 60/60 | 0.979 | 0.979 | 1.960 | 2.22 | 0.243 | 0.002 | 0.209 |
| clean | 150 | missing | 0.2 | bvar_minnesota_v2_cal | 60/60 | 0.953 | 0.953 | 2.968 | 3.72 | 0.249 | 0.000 | 0.204 |
| clean | 150 | missing | 0.2 | tlp2_db_p3 | 60/60 | 0.905 | 0.906 | 1.346 | 2.21 | 0.237 | 0.002 | 0.200 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.971 | 0.971 | 1.725 | 2.11 | 0.273 | 0.000 | 0.192 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.960 | 0.960 | 1.577 | 1.99 | 0.226 | 0.000 | 0.169 |
| clean | 150 | missing | 0.5 | pselect_union_v3 | 60/60 | 0.988 | 0.988 | 2.009 | 2.30 | 0.248 | 0.004 | 0.171 |
| clean | 150 | missing | 0.5 | pselect_union_v3_cal | 60/60 | 0.959 | 0.959 | 1.607 | 2.04 | 0.248 | 0.004 | 0.171 |
| clean | 150 | missing | 0.5 | pselect_cal | 60/60 | 0.937 | 0.937 | 2.159 | 3.06 | 0.266 | 0.001 | 0.186 |
| clean | 150 | missing | 0.5 | fullvar_cal | 60/60 | 0.953 | 0.953 | 2.275 | 3.01 | 0.291 | 0.000 | 0.216 |
| clean | 150 | missing | 0.5 | targeted_lp | 60/60 | 0.896 | 0.900 | 1.583 | 2.55 | 0.301 | 0.014 | 0.256 |
| clean | 150 | missing | 0.5 | targeted_lp_cal | 60/60 | 0.962 | 0.962 | 2.058 | 2.43 | 0.301 | 0.014 | 0.256 |
| clean | 150 | missing | 0.5 | bvar_minnesota_v2_cal | 60/60 | 0.957 | 0.957 | 2.906 | 3.79 | 0.352 | 0.000 | 0.212 |
| clean | 150 | missing | 0.5 | tlp2_db_p3 | 60/60 | 0.857 | 0.861 | 1.451 | 2.88 | 0.298 | 0.015 | 0.249 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 | pselect_union_v3 | pselect_union_v3_cal | pselect_cal | fullvar_cal | targeted_lp | targeted_lp_cal | bvar_minnesota_v2_cal | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 80 | missing | 0.2 | -0.44 [-0.54, -0.34] | +0.33 [+0.19, +0.49] | +0.17 [-0.00, +0.35] | +0.78 [+0.61, +0.97] | +0.28 [+0.16, +0.43] | +0.36 [+0.15, +0.58] | +0.37 [+0.20, +0.54] | +1.51 [+1.38, +1.66] | +0.58 [+0.28, +0.95] |
| clean | 80 | missing | 0.5 | -0.29 [-0.39, -0.17] | +0.23 [+0.07, +0.36] | +0.02 [-0.15, +0.17] | +0.94 [+0.65, +1.21] | +0.56 [+0.32, +0.86] | +0.64 [+0.41, +0.89] | +0.57 [+0.38, +0.77] | +1.26 [+1.09, +1.43] | +1.65 [+1.20, +2.06] |
| clean | 80 | reversed | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 150 | none | 0.0 | – | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 150 | missing | 0.2 | -0.23 [-0.30, -0.17] | +0.17 [+0.10, +0.26] | -0.03 [-0.11, +0.06] | +0.64 [+0.51, +0.78] | +0.64 [+0.53, +0.76] | +0.13 [-0.01, +0.28] | +0.24 [+0.17, +0.31] | +1.74 [+1.56, +1.92] | +0.23 [+0.07, +0.41] |
| clean | 150 | missing | 0.5 | -0.12 [-0.28, +0.02] | +0.18 [+0.04, +0.32] | -0.07 [-0.25, +0.11] | +0.94 [+0.75, +1.17] | +0.89 [+0.75, +1.04] | +0.44 [+0.17, +0.70] | +0.32 [+0.13, +0.47] | +1.68 [+1.41, +1.99] | +0.77 [+0.44, +1.08] |
| clean | 150 | reversed | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – | – | – | – | – |
