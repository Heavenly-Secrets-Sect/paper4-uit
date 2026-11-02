# ext_r4lfdropen_lag1

r4lfdropen secondary (descriptive, not ruling): lag_max 1, missing 0.2/0.5 at T [25, 40], D-07 development, seed_base 20261102. Both methods calibrated in this run on D-07H development (no frozen factors exist for lag_max 1).

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 1, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 25 | none | 0.0 | oracle | 60/60 | 0.903 | 0.903 | 1.969 | 3.29 | 0.367 | 0.000 | 0.208 |
| clean | 25 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.526 | 5.09 | 0.548 | 0.000 | 0.364 |
| clean | 25 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.939 | 0.939 | 3.526 | 5.09 | 0.548 | 0.000 | 0.364 |
| clean | 25 | missing | 0.2 | oracle | 60/60 | 0.903 | 0.903 | 1.969 | 3.29 | 0.367 | 0.000 | 0.208 |
| clean | 25 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.938 | 0.938 | 4.395 | 5.84 | 0.666 | 0.000 | 0.368 |
| clean | 25 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.946 | 0.946 | 4.586 | 6.12 | 0.669 | 0.000 | 0.379 |
| clean | 25 | missing | 0.5 | oracle | 60/60 | 0.903 | 0.903 | 1.969 | 3.29 | 0.367 | 0.000 | 0.208 |
| clean | 25 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 4.828 | 6.14 | 0.778 | 0.000 | 0.397 |
| clean | 25 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.936 | 0.936 | 4.841 | 6.41 | 0.779 | 0.000 | 0.454 |
| clean | 40 | none | 0.0 | oracle | 60/60 | 0.914 | 0.914 | 1.532 | 2.37 | 0.286 | 0.000 | 0.128 |
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.934 | 3.81 | 0.410 | 0.000 | 0.305 |
| clean | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.951 | 0.951 | 2.934 | 3.81 | 0.410 | 0.000 | 0.305 |
| clean | 40 | missing | 0.2 | oracle | 60/60 | 0.914 | 0.914 | 1.532 | 2.37 | 0.286 | 0.000 | 0.128 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.944 | 0.944 | 3.205 | 4.13 | 0.503 | 0.000 | 0.295 |
| clean | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.956 | 0.956 | 3.499 | 4.44 | 0.505 | 0.000 | 0.316 |
| clean | 40 | missing | 0.5 | oracle | 60/60 | 0.914 | 0.914 | 1.532 | 2.37 | 0.286 | 0.000 | 0.128 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.940 | 0.940 | 3.397 | 4.35 | 0.551 | 0.000 | 0.345 |
| clean | 40 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.951 | 0.951 | 3.746 | 4.62 | 0.556 | 0.000 | 0.299 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v5_1_lfdr |
|---|---|---|---|---|---|
| clean | 25 | none | 0.0 | -1.80 [-2.11, -1.54] | +0.00 [+0.00, +0.00] |
| clean | 25 | missing | 0.2 | -2.55 [-2.90, -2.28] | +0.28 [+0.16, +0.43] |
| clean | 25 | missing | 0.5 | -2.85 [-3.18, -2.51] | +0.27 [-0.07, +0.65] |
| clean | 40 | none | 0.0 | -1.44 [-1.69, -1.23] | +0.00 [+0.00, +0.00] |
| clean | 40 | missing | 0.2 | -1.76 [-2.03, -1.55] | +0.31 [+0.13, +0.49] |
| clean | 40 | missing | 0.5 | -1.98 [-2.20, -1.77] | +0.26 [+0.06, +0.45] |
