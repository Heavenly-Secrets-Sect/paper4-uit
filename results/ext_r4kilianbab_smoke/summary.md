# ext_r4kilianbab_smoke

smoke test of the r4kilianbab driver on D-07H development only (2 topologies, T 40, n_boot 49). Not evaluation.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 49, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 2.468 | 2.97 | 0.354 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | r4kilianbab_bab | 2/2 | 0.985 | 0.985 | 3.433 | 3.63 | 0.434 | 0.000 | 0.412 |
| clean | 40 | none | 0.0 | r4kilianbab_babbc | 2/2 | 0.955 | 0.955 | 2.739 | 3.14 | 0.434 | 0.000 | 0.412 |
| clean | 40 | none | 0.0 | r4kilianbab_babraw | 2/2 | 0.881 | 0.881 | 2.452 | 3.62 | 0.434 | 0.000 | 0.412 |
| clean | 40 | none | 0.0 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 2/2 | 0.925 | 0.925 | 2.723 | 3.65 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.2 | r4kilianbab_bab | 2/2 | 0.970 | 0.970 | 3.109 | 3.48 | 0.531 | 0.000 | 0.420 |
| clean | 40 | extra | 0.2 | r4kilianbab_babbc | 2/2 | 0.955 | 0.955 | 3.450 | 3.93 | 0.531 | 0.000 | 0.420 |
| clean | 40 | extra | 0.2 | r4kilianbab_babraw | 2/2 | 0.925 | 0.925 | 2.703 | 3.47 | 0.531 | 0.000 | 0.420 |
| clean | 40 | extra | 0.2 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 2/2 | 0.955 | 0.955 | 2.869 | 3.38 | 0.392 | 0.000 | 0.336 |
| clean | 40 | extra | 0.5 | r4kilianbab_bab | 2/2 | 0.970 | 0.970 | 3.867 | 3.99 | 0.487 | 0.000 | 0.431 |
| clean | 40 | extra | 0.5 | r4kilianbab_babbc | 2/2 | 1.000 | 1.000 | 4.107 | 4.35 | 0.487 | 0.000 | 0.431 |
| clean | 40 | extra | 0.5 | r4kilianbab_babraw | 2/2 | 0.940 | 0.940 | 3.363 | 4.00 | 0.487 | 0.000 | 0.431 |
| clean | 40 | extra | 0.5 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 2/2 | 0.896 | 0.896 | 2.958 | 4.41 | 0.469 | 0.000 | 0.227 |
| clean | 40 | missing | 0.2 | r4kilianbab_bab | 2/2 | 0.940 | 0.940 | 3.456 | 4.25 | 0.509 | 0.000 | 0.268 |
| clean | 40 | missing | 0.2 | r4kilianbab_babbc | 2/2 | 0.970 | 0.970 | 3.983 | 4.48 | 0.509 | 0.000 | 0.268 |
| clean | 40 | missing | 0.2 | r4kilianbab_babraw | 2/2 | 0.910 | 0.910 | 3.141 | 4.32 | 0.509 | 0.000 | 0.268 |
| clean | 40 | missing | 0.2 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.821 | 0.821 | 3.018 | 5.31 | 0.565 | 0.000 | 0.554 |
| clean | 40 | missing | 0.5 | r4kilianbab_bab | 2/2 | 0.925 | 0.925 | 3.722 | 4.50 | 0.591 | 0.000 | 0.487 |
| clean | 40 | missing | 0.5 | r4kilianbab_babbc | 2/2 | 0.910 | 0.910 | 4.289 | 6.52 | 0.591 | 0.000 | 0.487 |
| clean | 40 | missing | 0.5 | r4kilianbab_babraw | 2/2 | 0.910 | 0.910 | 3.384 | 4.50 | 0.591 | 0.000 | 0.487 |
| clean | 40 | missing | 0.5 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 2.608 | 3.66 | 0.446 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.2 | r4kilianbab_bab | 2/2 | 0.970 | 0.970 | 3.018 | 3.48 | 0.439 | 0.000 | 0.315 |
| clean | 40 | reversed | 0.2 | r4kilianbab_babbc | 2/2 | 0.940 | 0.940 | 2.997 | 3.52 | 0.439 | 0.000 | 0.315 |
| clean | 40 | reversed | 0.2 | r4kilianbab_babraw | 2/2 | 0.821 | 0.821 | 2.414 | 3.79 | 0.439 | 0.000 | 0.315 |
| clean | 40 | reversed | 0.2 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 2.983 | 4.50 | 0.593 | 0.000 | 0.572 |
| clean | 40 | reversed | 0.5 | r4kilianbab_bab | 2/2 | 0.955 | 0.955 | 3.047 | 3.93 | 0.520 | 0.000 | 0.491 |
| clean | 40 | reversed | 0.5 | r4kilianbab_babbc | 2/2 | 0.970 | 0.970 | 3.139 | 3.77 | 0.520 | 0.000 | 0.491 |
| clean | 40 | reversed | 0.5 | r4kilianbab_babraw | 2/2 | 0.881 | 0.881 | 2.438 | 4.40 | 0.520 | 0.000 | 0.491 |
| clean | 40 | reversed | 0.5 | oracle | 2/2 | 0.761 | 0.761 | 1.169 | 3.53 | 0.290 | 0.000 | 0.109 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4kilianbab_bab | r4kilianbab_babbc | r4kilianbab_babraw | oracle |
|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.66 [+0.54, +0.79] | +0.17 [-0.10, +0.45] | +0.65 [+0.48, +0.83] | +0.57 [+0.15, +0.98] |
| clean | 40 | extra | 0.2 | -0.17 [-0.67, +0.33] | +0.28 [-0.29, +0.84] | -0.18 [-0.46, +0.09] | -0.12 [-0.13, -0.11] |
| clean | 40 | extra | 0.5 | +0.61 [+0.32, +0.90] | +0.96 [+0.80, +1.13] | +0.62 [-0.07, +1.31] | +0.15 [-0.52, +0.81] |
| clean | 40 | missing | 0.2 | -0.16 [-1.04, +0.73] | +0.07 [-0.60, +0.75] | -0.09 [-0.84, +0.66] | -0.87 [-0.89, -0.85] |
| clean | 40 | missing | 0.5 | -0.82 [-2.18, +0.54] | +1.21 [+0.89, +1.53] | -0.82 [-2.44, +0.81] | -1.78 [-2.04, -1.52] |
| clean | 40 | reversed | 0.2 | -0.18 [-0.80, +0.45] | -0.13 [-0.70, +0.43] | +0.13 [-0.14, +0.40] | -0.13 [-0.29, +0.04] |
| clean | 40 | reversed | 0.5 | -0.56 [-1.10, -0.02] | -0.73 [-1.56, +0.10] | -0.09 [-0.15, -0.03] | -0.96 [-1.44, -0.49] |
