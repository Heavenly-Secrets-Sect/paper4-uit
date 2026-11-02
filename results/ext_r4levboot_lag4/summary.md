# ext_r4levboot_lag4

Round 4 levboot, lag_max 4 region grid (T 40/80, missing and reversed 0.2; seeds of ext_region51_lag4). Descriptive. tolerant_v5_1 and the arms all calibrated in this run on D-07H development (calibration cells as ext_region51_lag4: missing/reversed x 0.2/0.5). Run through experiments/ext/r4levboot/run.py.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 4, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 33/60 | 0.935 | 0.935 | 4.454 | 160.98 | 0.606 | 0.000 | 0.526 |
| clean | 40 | none | 0.0 | r4levboot_L2 | 33/60 | 0.940 | 0.940 | 4.533 | 161.05 | 0.606 | 0.000 | 0.526 |
| clean | 40 | none | 0.0 | r4levboot_L3 | 33/60 | 0.950 | 0.950 | 5.090 | 162.94 | 0.606 | 0.000 | 0.526 |
| clean | 40 | none | 0.0 | r4levboot_W3 | 33/60 | 0.936 | 0.936 | 4.775 | 162.29 | 0.606 | 0.000 | 0.526 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | missing | 0.2 | r4levboot_L2 | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | missing | 0.2 | r4levboot_L3 | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | missing | 0.2 | r4levboot_W3 | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 33/60 | 0.949 | 0.949 | 4.970 | 197.35 | 0.638 | 0.000 | 0.560 |
| clean | 40 | reversed | 0.2 | r4levboot_L2 | 33/60 | 0.952 | 0.952 | 4.729 | 196.22 | 0.635 | 0.000 | 0.560 |
| clean | 40 | reversed | 0.2 | r4levboot_L3 | 33/60 | 0.944 | 0.944 | 4.864 | 438.46 | 0.636 | 0.000 | 0.560 |
| clean | 40 | reversed | 0.2 | r4levboot_W3 | 33/60 | 0.944 | 0.944 | 4.854 | 202.32 | 0.664 | 0.000 | 0.560 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 2.069 | 2.66 | 0.337 | 0.000 | 0.321 |
| clean | 80 | none | 0.0 | r4levboot_L2 | 60/60 | 0.952 | 0.952 | 2.093 | 2.67 | 0.337 | 0.000 | 0.321 |
| clean | 80 | none | 0.0 | r4levboot_L3 | 60/60 | 0.962 | 0.962 | 2.383 | 3.02 | 0.337 | 0.000 | 0.321 |
| clean | 80 | none | 0.0 | r4levboot_W3 | 60/60 | 0.965 | 0.965 | 2.422 | 3.03 | 0.337 | 0.000 | 0.321 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.944 | 0.944 | 2.311 | 3.16 | 0.374 | 0.000 | 0.364 |
| clean | 80 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.943 | 0.943 | 2.349 | 3.15 | 0.363 | 0.000 | 0.364 |
| clean | 80 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.942 | 0.942 | 2.293 | 3.32 | 0.355 | 0.000 | 0.364 |
| clean | 80 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.937 | 0.937 | 2.301 | 3.39 | 0.360 | 0.000 | 0.364 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.961 | 0.961 | 2.457 | 3.05 | 0.338 | 0.000 | 0.345 |
| clean | 80 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.962 | 0.962 | 2.470 | 3.05 | 0.340 | 0.000 | 0.345 |
| clean | 80 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.967 | 0.967 | 2.761 | 3.46 | 0.353 | 0.000 | 0.345 |
| clean | 80 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.966 | 0.966 | 2.813 | 3.51 | 0.344 | 0.000 | 0.345 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4levboot_L2 | r4levboot_L3 | r4levboot_W3 |
|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.07 [-0.03, +0.21] | +1.96 [+0.98, +3.28] | +1.31 [+0.62, +2.26] |
| clean | 40 | missing | 0.2 | – | – | – |
| clean | 40 | reversed | 0.2 | -1.14 [-3.67, +0.19] | +241.11 [+0.56, +721.45] | +4.96 [+0.51, +13.31] |
| clean | 80 | none | 0.0 | +0.00 [-0.01, +0.02] | +0.36 [+0.23, +0.52] | +0.36 [+0.22, +0.51] |
| clean | 80 | missing | 0.2 | -0.01 [-0.07, +0.07] | +0.16 [+0.05, +0.29] | +0.23 [+0.10, +0.41] |
| clean | 80 | reversed | 0.2 | +0.00 [-0.01, +0.01] | +0.41 [+0.29, +0.57] | +0.46 [+0.34, +0.62] |
