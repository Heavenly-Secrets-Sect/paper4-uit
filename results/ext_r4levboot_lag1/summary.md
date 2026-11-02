# ext_r4levboot_lag1

Round 4 levboot, lag_max 1 region grid (T 40/80, missing and reversed 0.2; seeds of ext_region51_lag1). Descriptive. tolerant_v5_1 and the arms all calibrated in this run on D-07H development (calibration cells as ext_region51_lag1: missing/reversed x 0.2/0.5). Run through experiments/ext/r4levboot/run.py.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 1, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.967 | 0.967 | 3.410 | 4.12 | 0.410 | 0.000 | 0.314 |
| clean | 40 | none | 0.0 | r4levboot_L2 | 60/60 | 0.968 | 0.968 | 3.434 | 4.13 | 0.410 | 0.000 | 0.314 |
| clean | 40 | none | 0.0 | r4levboot_L3 | 60/60 | 0.966 | 0.966 | 3.534 | 4.26 | 0.410 | 0.000 | 0.314 |
| clean | 40 | none | 0.0 | r4levboot_W3 | 60/60 | 0.970 | 0.970 | 3.758 | 4.40 | 0.410 | 0.000 | 0.314 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.962 | 0.962 | 3.702 | 4.45 | 0.514 | 0.000 | 0.298 |
| clean | 40 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.958 | 0.958 | 3.682 | 4.49 | 0.506 | 0.000 | 0.298 |
| clean | 40 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.964 | 0.964 | 3.872 | 4.66 | 0.503 | 0.000 | 0.298 |
| clean | 40 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.960 | 0.960 | 3.861 | 4.62 | 0.514 | 0.000 | 0.298 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.967 | 0.967 | 3.805 | 4.41 | 0.504 | 0.000 | 0.321 |
| clean | 40 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.968 | 0.968 | 3.859 | 4.42 | 0.506 | 0.000 | 0.321 |
| clean | 40 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.968 | 0.968 | 4.005 | 4.59 | 0.508 | 0.000 | 0.321 |
| clean | 40 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.971 | 0.971 | 4.030 | 4.74 | 0.509 | 0.000 | 0.321 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.938 | 0.938 | 1.718 | 2.33 | 0.253 | 0.000 | 0.182 |
| clean | 80 | none | 0.0 | r4levboot_L2 | 60/60 | 0.940 | 0.940 | 1.716 | 2.33 | 0.253 | 0.000 | 0.182 |
| clean | 80 | none | 0.0 | r4levboot_L3 | 60/60 | 0.940 | 0.940 | 1.741 | 2.35 | 0.253 | 0.000 | 0.182 |
| clean | 80 | none | 0.0 | r4levboot_W3 | 60/60 | 0.932 | 0.932 | 1.738 | 2.44 | 0.253 | 0.000 | 0.182 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.111 | 2.69 | 0.314 | 0.000 | 0.208 |
| clean | 80 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.948 | 0.948 | 1.997 | 2.64 | 0.319 | 0.000 | 0.208 |
| clean | 80 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.946 | 0.946 | 2.002 | 2.65 | 0.318 | 0.000 | 0.208 |
| clean | 80 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.950 | 0.950 | 2.109 | 2.69 | 0.329 | 0.000 | 0.208 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.925 | 0.925 | 1.891 | 2.63 | 0.310 | 0.000 | 0.193 |
| clean | 80 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.933 | 0.933 | 1.956 | 2.64 | 0.311 | 0.000 | 0.193 |
| clean | 80 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.932 | 0.932 | 1.965 | 2.67 | 0.312 | 0.000 | 0.193 |
| clean | 80 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.935 | 0.935 | 2.018 | 2.73 | 0.309 | 0.000 | 0.193 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4levboot_L2 | r4levboot_L3 | r4levboot_W3 |
|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.01 [-0.01, +0.02] | +0.14 [+0.09, +0.20] | +0.28 [+0.19, +0.36] |
| clean | 40 | missing | 0.2 | +0.03 [-0.03, +0.11] | +0.21 [+0.14, +0.30] | +0.17 [+0.07, +0.27] |
| clean | 40 | reversed | 0.2 | +0.00 [-0.01, +0.02] | +0.18 [+0.14, +0.22] | +0.33 [+0.23, +0.42] |
| clean | 80 | none | 0.0 | +0.00 [-0.01, +0.01] | +0.02 [+0.01, +0.04] | +0.11 [+0.06, +0.16] |
| clean | 80 | missing | 0.2 | -0.05 [-0.08, -0.01] | -0.03 [-0.07, +0.00] | +0.00 [-0.05, +0.05] |
| clean | 80 | reversed | 0.2 | +0.00 [-0.01, +0.02] | +0.04 [+0.01, +0.08] | +0.10 [+0.06, +0.14] |
