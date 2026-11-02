# ext_tlp2_t80a

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['none', 0.0], ['extra', 0.2], ['extra', 0.5]] at T=[80]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.933 | 0.933 | 1.828 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | targeted_lp | 60/60 | 0.955 | 0.955 | 2.463 | 3.10 | 0.391 | 0.000 | 0.265 |
| clean | 80 | none | 0.0 | tlp2_lp_cal | 60/60 | 0.956 | 0.956 | 2.472 | 3.10 | 0.382 | 0.000 | 0.265 |
| clean | 80 | none | 0.0 | tlp2_db | 60/60 | 0.924 | 0.924 | 2.357 | 3.91 | 0.387 | 0.000 | 0.287 |
| clean | 80 | none | 0.0 | tlp2_db90 | 60/60 | 0.860 | 0.860 | 1.822 | 4.44 | 0.387 | 0.000 | 0.287 |
| clean | 80 | none | 0.0 | tlp2_db_p3 | 60/60 | 0.916 | 0.916 | 1.904 | 2.87 | 0.352 | 0.000 | 0.257 |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 1.860 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | targeted_lp | 60/60 | 0.953 | 0.953 | 2.494 | 3.13 | 0.369 | 0.000 | 0.260 |
| clean | 80 | extra | 0.2 | tlp2_lp_cal | 60/60 | 0.957 | 0.957 | 2.510 | 3.13 | 0.385 | 0.000 | 0.261 |
| clean | 80 | extra | 0.2 | tlp2_db | 60/60 | 0.926 | 0.926 | 2.412 | 3.83 | 0.385 | 0.000 | 0.280 |
| clean | 80 | extra | 0.2 | tlp2_db90 | 60/60 | 0.863 | 0.863 | 1.882 | 4.33 | 0.385 | 0.000 | 0.280 |
| clean | 80 | extra | 0.2 | tlp2_db_p3 | 60/60 | 0.915 | 0.915 | 1.925 | 2.94 | 0.343 | 0.000 | 0.264 |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 1.987 | 2.65 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | targeted_lp | 60/60 | 0.955 | 0.955 | 2.522 | 3.16 | 0.394 | 0.000 | 0.286 |
| clean | 80 | extra | 0.5 | tlp2_lp_cal | 60/60 | 0.956 | 0.956 | 2.500 | 3.16 | 0.390 | 0.000 | 0.280 |
| clean | 80 | extra | 0.5 | tlp2_db | 60/60 | 0.921 | 0.921 | 2.417 | 3.96 | 0.394 | 0.000 | 0.298 |
| clean | 80 | extra | 0.5 | tlp2_db90 | 60/60 | 0.853 | 0.853 | 1.900 | 4.49 | 0.394 | 0.000 | 0.298 |
| clean | 80 | extra | 0.5 | tlp2_db_p3 | 60/60 | 0.912 | 0.912 | 1.934 | 2.98 | 0.351 | 0.000 | 0.285 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | -0.60 [-0.89, -0.30] | +0.00 [-0.07, +0.08] | +0.81 [+0.46, +1.21] | +1.34 [+0.84, +1.87] | -0.23 [-0.40, -0.03] |
| clean | 80 | extra | 0.2 | -0.60 [-0.86, -0.32] | +0.00 [-0.05, +0.05] | +0.71 [+0.37, +1.05] | +1.20 [+0.78, +1.67] | -0.19 [-0.35, -0.01] |
| clean | 80 | extra | 0.5 | -0.52 [-0.80, -0.27] | -0.00 [-0.08, +0.06] | +0.79 [+0.53, +1.06] | +1.32 [+0.91, +1.70] | -0.19 [-0.33, -0.00] |
| clean | 80 | missing | 0.2 | – | – | – | – | – |
| clean | 80 | missing | 0.5 | – | – | – | – | – |
| clean | 80 | reversed | 0.2 | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | +0.60 [+0.30, +0.89] | +0.60 [+0.29, +0.93] | +1.41 [+0.97, +1.90] | +1.93 [+1.35, +2.55] | +0.37 [+0.18, +0.54] |
| clean | 80 | extra | 0.2 | +0.60 [+0.32, +0.86] | +0.60 [+0.30, +0.89] | +1.31 [+0.85, +1.78] | +1.80 [+1.30, +2.35] | +0.41 [+0.22, +0.60] |
| clean | 80 | extra | 0.5 | +0.52 [+0.27, +0.80] | +0.52 [+0.24, +0.79] | +1.31 [+0.89, +1.72] | +1.84 [+1.34, +2.30] | +0.33 [+0.16, +0.50] |
| clean | 80 | missing | 0.2 | – | – | – | – | – |
| clean | 80 | missing | 0.5 | – | – | – | – | – |
| clean | 80 | reversed | 0.2 | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – |
