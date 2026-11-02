# ext_tlp2_t150d

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['reversed', 0.2], ['reversed', 0.5]] at T=[150]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.971 | 0.971 | 1.592 | 1.89 | 0.225 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | targeted_lp | 60/60 | 0.926 | 0.926 | 1.539 | 2.66 | 0.261 | 0.000 | 0.204 |
| clean | 150 | reversed | 0.2 | tlp2_lp_cal | 60/60 | 0.974 | 0.974 | 2.110 | 2.66 | 0.254 | 0.000 | 0.207 |
| clean | 150 | reversed | 0.2 | tlp2_db | 60/60 | 0.913 | 0.913 | 1.386 | 2.71 | 0.245 | 0.000 | 0.204 |
| clean | 150 | reversed | 0.2 | tlp2_db90 | 60/60 | 0.860 | 0.860 | 1.164 | 3.04 | 0.245 | 0.000 | 0.204 |
| clean | 150 | reversed | 0.2 | tlp2_db_p3 | 60/60 | 0.903 | 0.903 | 1.339 | 2.71 | 0.252 | 0.000 | 0.203 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 1.571 | 2.06 | 0.252 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | targeted_lp | 60/60 | 0.863 | 0.863 | 1.625 | 3.73 | 0.280 | 0.000 | 0.238 |
| clean | 150 | reversed | 0.5 | tlp2_lp_cal | 60/60 | 0.939 | 0.939 | 2.248 | 3.17 | 0.273 | 0.000 | 0.233 |
| clean | 150 | reversed | 0.5 | tlp2_db | 60/60 | 0.847 | 0.847 | 1.457 | 3.99 | 0.270 | 0.000 | 0.237 |
| clean | 150 | reversed | 0.5 | tlp2_db90 | 60/60 | 0.783 | 0.783 | 1.206 | 4.71 | 0.270 | 0.000 | 0.237 |
| clean | 150 | reversed | 0.5 | tlp2_db_p3 | 60/60 | 0.833 | 0.833 | 1.401 | 4.08 | 0.270 | 0.000 | 0.232 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | -0.76 [-1.15, -0.49] | -0.00 [-0.19, +0.15] | +0.05 [-0.04, +0.15] | +0.39 [+0.22, +0.57] | +0.06 [-0.02, +0.15] |
| clean | 150 | reversed | 0.5 | -1.67 [-2.15, -1.22] | -0.56 [-0.79, -0.32] | +0.26 [+0.04, +0.49] | +0.99 [+0.71, +1.29] | +0.36 [+0.21, +0.51] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | +0.76 [+0.49, +1.15] | +0.76 [+0.56, +1.03] | +0.81 [+0.55, +1.17] | +1.15 [+0.74, +1.66] | +0.82 [+0.51, +1.25] |
| clean | 150 | reversed | 0.5 | +1.67 [+1.22, +2.15] | +1.11 [+0.86, +1.41] | +1.93 [+1.44, +2.54] | +2.65 [+2.06, +3.37] | +2.02 [+1.53, +2.56] |
