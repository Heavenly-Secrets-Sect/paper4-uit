# ext_verify3_baselines3/smoke_clt

verify3_baselines3 smoke test of the P7 pipeline on D-07H development (2 topologies, 1 replicate). Not a result.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | missing | 0.2 | tolerant_v4 | 2/2 | 0.970 | 0.970 | 2.769 | 3.03 | 0.378 | 0.000 | 0.339 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 2/2 | 0.955 | 0.955 | 2.125 | 2.44 | 0.332 | 0.000 | 0.244 |
| clean | 80 | missing | 0.2 | pselect_union_v3 | 2/2 | 1.000 | 1.000 | 2.779 | 3.01 | 0.388 | 0.000 | 0.238 |
| clean | 80 | missing | 0.2 | pselect_union_v3_cal | 2/2 | 0.970 | 0.970 | 2.362 | 2.61 | 0.388 | 0.000 | 0.238 |
| clean | 80 | missing | 0.2 | pselect_cal | 2/2 | 0.970 | 0.970 | 2.893 | 3.13 | 0.421 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | fullvar_cal | 2/2 | 0.970 | 0.970 | 2.756 | 3.08 | 0.407 | 0.000 | 0.307 |
| clean | 80 | missing | 0.2 | targeted_lp | 2/2 | 0.955 | 0.955 | 2.718 | 2.92 | 0.435 | 0.000 | 0.312 |
| clean | 80 | missing | 0.2 | targeted_lp_cal | 2/2 | 1.000 | 1.000 | 2.990 | 3.05 | 0.435 | 0.000 | 0.312 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2_cal | 2/2 | 0.970 | 0.970 | 3.965 | 4.46 | 0.387 | 0.000 | 0.271 |
| clean | 80 | missing | 0.2 | tlp2_db_p3 | 2/2 | 0.910 | 0.910 | 2.098 | 3.24 | 0.420 | 0.000 | 0.293 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 2/2 | 0.970 | 0.970 | 2.792 | 3.06 | 0.395 | 0.000 | 0.337 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 2.342 | 2.93 | 0.345 | 0.000 | 0.262 |
| clean | 80 | missing | 0.5 | pselect_union_v3 | 2/2 | 1.000 | 1.000 | 2.754 | 2.96 | 0.359 | 0.000 | 0.237 |
| clean | 80 | missing | 0.5 | pselect_union_v3_cal | 2/2 | 0.985 | 0.985 | 2.341 | 2.58 | 0.359 | 0.000 | 0.237 |
| clean | 80 | missing | 0.5 | pselect_cal | 2/2 | 0.940 | 0.940 | 2.739 | 3.23 | 0.385 | 0.000 | 0.219 |
| clean | 80 | missing | 0.5 | fullvar_cal | 2/2 | 0.940 | 0.940 | 2.878 | 3.50 | 0.345 | 0.000 | 0.321 |
| clean | 80 | missing | 0.5 | targeted_lp | 2/2 | 0.940 | 0.938 | 2.635 | 3.45 | 0.449 | 0.030 | 0.435 |
| clean | 80 | missing | 0.5 | targeted_lp_cal | 2/2 | 0.955 | 0.954 | 2.899 | 3.52 | 0.449 | 0.030 | 0.435 |
| clean | 80 | missing | 0.5 | bvar_minnesota_v2_cal | 2/2 | 0.970 | 0.970 | 3.707 | 4.29 | 0.452 | 0.000 | 0.203 |
| clean | 80 | missing | 0.5 | tlp2_db_p3 | 2/2 | 0.881 | 0.875 | 2.054 | 3.42 | 0.473 | 0.045 | 0.466 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 2/2 | 0.955 | 0.955 | 1.662 | 1.91 | 0.317 | 0.000 | 0.202 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 2/2 | 1.000 | 1.000 | 1.423 | 1.50 | 0.269 | 0.000 | 0.156 |
| clean | 150 | missing | 0.2 | pselect_union_v3 | 2/2 | 1.000 | 1.000 | 1.723 | 1.90 | 0.219 | 0.000 | 0.170 |
| clean | 150 | missing | 0.2 | pselect_union_v3_cal | 2/2 | 0.985 | 0.985 | 1.378 | 1.59 | 0.219 | 0.000 | 0.170 |
| clean | 150 | missing | 0.2 | pselect_cal | 2/2 | 0.955 | 0.955 | 2.022 | 2.46 | 0.208 | 0.000 | 0.159 |
| clean | 150 | missing | 0.2 | fullvar_cal | 2/2 | 0.970 | 0.970 | 2.297 | 2.50 | 0.312 | 0.000 | 0.205 |
| clean | 150 | missing | 0.2 | targeted_lp | 2/2 | 0.925 | 0.925 | 1.620 | 2.06 | 0.292 | 0.000 | 0.210 |
| clean | 150 | missing | 0.2 | targeted_lp_cal | 2/2 | 0.970 | 0.970 | 2.106 | 2.17 | 0.292 | 0.000 | 0.210 |
| clean | 150 | missing | 0.2 | bvar_minnesota_v2_cal | 2/2 | 0.955 | 0.955 | 2.959 | 3.61 | 0.385 | 0.000 | 0.217 |
| clean | 150 | missing | 0.2 | tlp2_db_p3 | 2/2 | 0.896 | 0.896 | 1.502 | 2.21 | 0.284 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 2/2 | 0.940 | 0.940 | 1.659 | 1.93 | 0.238 | 0.000 | 0.184 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 1.518 | 1.74 | 0.227 | 0.000 | 0.142 |
| clean | 150 | missing | 0.5 | pselect_union_v3 | 2/2 | 1.000 | 1.000 | 1.798 | 2.06 | 0.216 | 0.000 | 0.162 |
| clean | 150 | missing | 0.5 | pselect_union_v3_cal | 2/2 | 0.985 | 0.985 | 1.438 | 1.66 | 0.216 | 0.000 | 0.162 |
| clean | 150 | missing | 0.5 | pselect_cal | 2/2 | 0.910 | 0.910 | 1.974 | 2.84 | 0.195 | 0.000 | 0.079 |
| clean | 150 | missing | 0.5 | fullvar_cal | 2/2 | 0.910 | 0.910 | 2.135 | 2.79 | 0.278 | 0.000 | 0.197 |
| clean | 150 | missing | 0.5 | targeted_lp | 2/2 | 0.896 | 0.896 | 1.623 | 2.22 | 0.354 | 0.000 | 0.297 |
| clean | 150 | missing | 0.5 | targeted_lp_cal | 2/2 | 0.970 | 0.970 | 2.110 | 2.20 | 0.354 | 0.000 | 0.297 |
| clean | 150 | missing | 0.5 | bvar_minnesota_v2_cal | 2/2 | 1.000 | 1.000 | 2.949 | 3.04 | 0.406 | 0.000 | 0.203 |
| clean | 150 | missing | 0.5 | tlp2_db_p3 | 2/2 | 0.851 | 0.851 | 1.492 | 2.73 | 0.357 | 0.000 | 0.238 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 | pselect_union_v3 | pselect_union_v3_cal | pselect_cal | fullvar_cal | targeted_lp | targeted_lp_cal | bvar_minnesota_v2_cal | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 80 | missing | 0.2 | -0.59 [-0.68, -0.51] | -0.02 [-0.24, +0.19] | -0.43 [-0.64, -0.21] | +0.10 [-0.16, +0.36] | +0.05 [-0.23, +0.32] | -0.11 [-0.24, +0.02] | +0.02 [+0.01, +0.02] | +1.43 [+1.17, +1.68] | +0.20 [-0.07, +0.47] |
| clean | 80 | missing | 0.5 | -0.12 [-0.35, +0.11] | -0.09 [-0.23, +0.04] | -0.48 [-0.51, -0.44] | +0.17 [+0.00, +0.34] | +0.45 [+0.23, +0.66] | +0.40 [-0.18, +0.97] | +0.46 [-0.01, +0.93] | +1.24 [+1.11, +1.36] | +0.36 [-0.13, +0.85] |
| clean | 80 | reversed | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 150 | none | 0.0 | – | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – | – | – | – | – |
| clean | 150 | missing | 0.2 | -0.40 [-0.44, -0.37] | -0.01 [-0.11, +0.10] | -0.32 [-0.42, -0.21] | +0.55 [+0.10, +1.01] | +0.59 [+0.36, +0.82] | +0.15 [-0.13, +0.43] | +0.26 [+0.14, +0.38] | +1.70 [+1.17, +2.24] | +0.31 [-0.04, +0.65] |
| clean | 150 | missing | 0.5 | -0.19 [-0.23, -0.15] | +0.13 [-0.01, +0.27] | -0.27 [-0.33, -0.21] | +0.92 [+0.67, +1.16] | +0.87 [+0.65, +1.09] | +0.29 [+0.10, +0.49] | +0.27 [+0.19, +0.35] | +1.11 [+1.07, +1.15] | +0.80 [+0.24, +1.36] |
| clean | 150 | reversed | 0.2 | – | – | – | – | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – | – | – | – | – |
