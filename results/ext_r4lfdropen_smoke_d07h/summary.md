# ext_r4lfdropen_smoke_d07h

r4lfdropen smoke test of the driver and method on D-07H development (2 topologies, 1 replicate, T 40/80); no evaluation use.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | none | 0.0 | tolerant_v5_1 | 2/2 | 0.985 | 0.985 | 2.549 | 2.94 | 0.354 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | tolerant_v5_1_lfdr | 2/2 | 0.910 | 0.910 | 1.862 | 2.80 | 0.354 | 0.000 | 0.235 |
| clean | 40 | extra | 0.2 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 2/2 | 0.955 | 0.955 | 2.978 | 3.65 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.940 | 0.940 | 2.520 | 3.42 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.5 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 3.208 | 3.48 | 0.392 | 0.000 | 0.336 |
| clean | 40 | extra | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.925 | 0.925 | 2.714 | 3.29 | 0.392 | 0.000 | 0.336 |
| clean | 40 | missing | 0.2 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 3.094 | 4.13 | 0.443 | 0.000 | 0.227 |
| clean | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.925 | 0.925 | 3.206 | 5.01 | 0.417 | 0.000 | 0.282 |
| clean | 40 | missing | 0.5 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.910 | 0.910 | 3.789 | 5.31 | 0.604 | 0.000 | 0.554 |
| clean | 40 | missing | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.866 | 0.866 | 3.263 | 4.91 | 0.637 | 0.000 | 0.277 |
| clean | 40 | reversed | 0.2 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 2.956 | 3.60 | 0.432 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.910 | 0.910 | 2.322 | 3.15 | 0.432 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.5 | oracle | 2/2 | 0.836 | 0.836 | 1.247 | 3.05 | 0.290 | 0.000 | 0.109 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 3.087 | 4.27 | 0.593 | 0.000 | 0.572 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.925 | 0.925 | 2.426 | 4.25 | 0.593 | 0.000 | 0.572 |
| clean | 80 | none | 0.0 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 2/2 | 0.985 | 0.985 | 1.652 | 2.06 | 0.233 | 0.000 | 0.200 |
| clean | 80 | none | 0.0 | tolerant_v5_1_lfdr | 2/2 | 0.925 | 0.925 | 1.271 | 1.93 | 0.233 | 0.000 | 0.200 |
| clean | 80 | extra | 0.2 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 1.660 | 2.28 | 0.266 | 0.000 | 0.182 |
| clean | 80 | extra | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.940 | 0.940 | 1.453 | 2.21 | 0.266 | 0.000 | 0.182 |
| clean | 80 | extra | 0.5 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 1.662 | 2.46 | 0.239 | 0.000 | 0.243 |
| clean | 80 | extra | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.925 | 0.925 | 1.454 | 2.48 | 0.239 | 0.000 | 0.243 |
| clean | 80 | missing | 0.2 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 2/2 | 0.955 | 0.955 | 2.125 | 2.44 | 0.332 | 0.000 | 0.244 |
| clean | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.940 | 0.940 | 1.756 | 2.63 | 0.267 | 0.000 | 0.208 |
| clean | 80 | missing | 0.5 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 2.342 | 2.93 | 0.345 | 0.000 | 0.262 |
| clean | 80 | missing | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.866 | 0.866 | 1.834 | 3.79 | 0.321 | 0.000 | 0.253 |
| clean | 80 | reversed | 0.2 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 2/2 | 0.985 | 0.985 | 1.905 | 1.99 | 0.256 | 0.000 | 0.234 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1_lfdr | 2/2 | 0.970 | 0.970 | 1.552 | 1.79 | 0.256 | 0.000 | 0.234 |
| clean | 80 | reversed | 0.5 | oracle | 2/2 | 0.985 | 0.985 | 0.956 | 1.12 | 0.139 | 0.000 | 0.045 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 2/2 | 1.000 | 1.000 | 2.049 | 2.12 | 0.276 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1_lfdr | 2/2 | 0.970 | 0.970 | 1.670 | 1.77 | 0.276 | 0.000 | 0.264 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v5_1_lfdr |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.11 [-0.58, +0.80] | -0.14 [-0.27, -0.02] |
| clean | 40 | extra | 0.2 | -0.59 [-0.84, -0.35] | -0.22 [-0.42, -0.03] |
| clean | 40 | extra | 0.5 | -0.43 [-1.16, +0.30] | -0.20 [-0.38, -0.02] |
| clean | 40 | missing | 0.2 | -1.08 [-1.40, -0.76] | +0.88 [+0.71, +1.05] |
| clean | 40 | missing | 0.5 | -2.25 [-2.33, -2.18] | -0.40 [-1.58, +0.78] |
| clean | 40 | reversed | 0.2 | -0.54 [-1.04, -0.05] | -0.45 [-0.51, -0.39] |
| clean | 40 | reversed | 0.5 | -1.22 [-1.30, -1.13] | -0.02 [-0.57, +0.53] |
| clean | 80 | none | 0.0 | -0.94 [-1.40, -0.48] | -0.13 [-0.14, -0.12] |
| clean | 80 | extra | 0.2 | -1.16 [-1.45, -0.87] | -0.07 [-0.08, -0.07] |
| clean | 80 | extra | 0.5 | -1.34 [-1.48, -1.19] | +0.03 [-0.03, +0.08] |
| clean | 80 | missing | 0.2 | -1.32 [-1.45, -1.20] | +0.19 [-0.56, +0.94] |
| clean | 80 | missing | 0.5 | -1.82 [-2.21, -1.42] | +0.86 [-0.49, +2.21] |
| clean | 80 | reversed | 0.2 | -0.87 [-1.11, -0.63] | -0.20 [-0.31, -0.08] |
| clean | 80 | reversed | 0.5 | -1.00 [-1.23, -0.77] | -0.35 [-0.38, -0.32] |
