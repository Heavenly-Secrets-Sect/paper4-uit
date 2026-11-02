# ext_r4lfdropen_lag4

r4lfdropen secondary (descriptive, not ruling): lag_max 4, missing 0.2/0.5 at T [80, 150], D-07 development, seed_base 20261102. Both methods calibrated in this run on D-07H development (no frozen factors exist for lag_max 4).

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 4, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | oracle | 60/60 | 0.903 | 0.903 | 0.900 | 1.50 | 0.152 | 0.000 | 0.051 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.946 | 0.946 | 1.967 | 2.74 | 0.329 | 0.000 | 0.323 |
| clean | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.946 | 0.946 | 1.967 | 2.74 | 0.329 | 0.000 | 0.323 |
| clean | 80 | missing | 0.2 | oracle | 60/60 | 0.903 | 0.903 | 0.900 | 1.50 | 0.152 | 0.000 | 0.051 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.922 | 0.922 | 2.105 | 3.31 | 0.374 | 0.000 | 0.339 |
| clean | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.954 | 0.954 | 2.793 | 3.93 | 0.345 | 0.000 | 0.339 |
| clean | 80 | missing | 0.5 | oracle | 60/60 | 0.903 | 0.903 | 0.900 | 1.50 | 0.152 | 0.000 | 0.051 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.940 | 0.940 | 2.623 | 3.67 | 0.397 | 0.000 | 0.381 |
| clean | 80 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.945 | 0.945 | 3.238 | 4.33 | 0.406 | 0.000 | 0.351 |
| clean | 150 | none | 0.0 | oracle | 60/60 | 0.937 | 0.937 | 0.684 | 0.91 | 0.101 | 0.000 | 0.039 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.964 | 0.964 | 1.310 | 1.53 | 0.186 | 0.000 | 0.207 |
| clean | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.964 | 0.964 | 1.310 | 1.53 | 0.186 | 0.000 | 0.207 |
| clean | 150 | missing | 0.2 | oracle | 60/60 | 0.937 | 0.937 | 0.684 | 0.91 | 0.101 | 0.000 | 0.039 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.961 | 0.961 | 1.418 | 1.80 | 0.216 | 0.000 | 0.211 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.961 | 0.961 | 1.435 | 1.96 | 0.208 | 0.000 | 0.212 |
| clean | 150 | missing | 0.5 | oracle | 60/60 | 0.937 | 0.937 | 0.684 | 0.91 | 0.101 | 0.000 | 0.039 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.962 | 0.962 | 1.604 | 2.07 | 0.242 | 0.000 | 0.237 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.954 | 0.954 | 1.611 | 2.27 | 0.245 | 0.000 | 0.227 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v5_1_lfdr |
|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | -1.23 [-1.62, -0.96] | +0.00 [+0.00, +0.00] |
| clean | 80 | missing | 0.2 | -1.81 [-2.05, -1.62] | +0.62 [+0.41, +0.84] |
| clean | 80 | missing | 0.5 | -2.16 [-2.33, -1.98] | +0.66 [+0.34, +1.01] |
| clean | 150 | none | 0.0 | -0.63 [-0.71, -0.54] | +0.00 [+0.00, +0.00] |
| clean | 150 | missing | 0.2 | -0.89 [-1.05, -0.76] | +0.17 [+0.04, +0.29] |
| clean | 150 | missing | 0.5 | -1.16 [-1.31, -1.01] | +0.20 [+0.08, +0.34] |
