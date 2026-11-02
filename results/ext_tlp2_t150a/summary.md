# ext_tlp2_t150a

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['none', 0.0]] at T=[150]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | targeted_lp | 60/60 | 0.959 | 0.959 | 1.475 | 1.87 | 0.237 | 0.000 | 0.192 |
| clean | 150 | none | 0.0 | tlp2_lp_cal | 60/60 | 0.974 | 0.974 | 1.635 | 1.94 | 0.234 | 0.000 | 0.184 |
| clean | 150 | none | 0.0 | tlp2_db | 60/60 | 0.946 | 0.946 | 1.375 | 1.83 | 0.219 | 0.000 | 0.187 |
| clean | 150 | none | 0.0 | tlp2_db90 | 60/60 | 0.909 | 0.909 | 1.130 | 1.92 | 0.219 | 0.000 | 0.187 |
| clean | 150 | none | 0.0 | tlp2_db_p3 | 60/60 | 0.943 | 0.943 | 1.315 | 1.80 | 0.225 | 0.000 | 0.184 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | -0.31 [-0.45, -0.17] | +0.07 [+0.02, +0.11] | -0.04 [-0.11, +0.03] | +0.05 [-0.05, +0.16] | -0.07 [-0.13, -0.02] |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | +0.31 [+0.17, +0.45] | +0.37 [+0.22, +0.53] | +0.27 [+0.14, +0.39] | +0.36 [+0.23, +0.49] | +0.24 [+0.11, +0.36] |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |
