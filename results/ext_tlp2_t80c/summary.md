# ext_tlp2_t80c

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['reversed', 0.2], ['reversed', 0.5]] at T=[80]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.945 | 0.945 | 2.094 | 2.83 | 0.338 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | targeted_lp | 60/60 | 0.950 | 0.950 | 2.523 | 3.40 | 0.398 | 0.000 | 0.293 |
| clean | 80 | reversed | 0.2 | tlp2_lp_cal | 60/60 | 0.950 | 0.950 | 2.509 | 3.42 | 0.393 | 0.000 | 0.278 |
| clean | 80 | reversed | 0.2 | tlp2_db | 60/60 | 0.917 | 0.917 | 2.449 | 4.36 | 0.414 | 0.000 | 0.277 |
| clean | 80 | reversed | 0.2 | tlp2_db90 | 60/60 | 0.846 | 0.846 | 1.873 | 4.97 | 0.414 | 0.000 | 0.277 |
| clean | 80 | reversed | 0.2 | tlp2_db_p3 | 60/60 | 0.898 | 0.898 | 1.906 | 3.41 | 0.374 | 0.000 | 0.283 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.931 | 0.931 | 2.108 | 2.99 | 0.367 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | targeted_lp | 60/60 | 0.929 | 0.929 | 2.640 | 3.94 | 0.462 | 0.000 | 0.325 |
| clean | 80 | reversed | 0.5 | tlp2_lp_cal | 60/60 | 0.930 | 0.930 | 2.676 | 3.94 | 0.469 | 0.000 | 0.310 |
| clean | 80 | reversed | 0.5 | tlp2_db | 60/60 | 0.899 | 0.899 | 2.483 | 5.05 | 0.472 | 0.000 | 0.342 |
| clean | 80 | reversed | 0.5 | tlp2_db90 | 60/60 | 0.807 | 0.807 | 1.924 | 6.08 | 0.472 | 0.000 | 0.342 |
| clean | 80 | reversed | 0.5 | tlp2_db_p3 | 60/60 | 0.853 | 0.853 | 1.923 | 4.53 | 0.446 | 0.000 | 0.314 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – |
| clean | 80 | missing | 0.2 | – | – | – | – | – |
| clean | 80 | missing | 0.5 | – | – | – | – | – |
| clean | 80 | reversed | 0.2 | -0.56 [-0.77, -0.33] | +0.02 [-0.04, +0.08] | +0.96 [+0.46, +1.52] | +1.57 [+0.96, +2.31] | +0.01 [-0.21, +0.26] |
| clean | 80 | reversed | 0.5 | -0.95 [-1.21, -0.69] | -0.00 [-0.11, +0.12] | +1.11 [+0.60, +1.72] | +2.13 [+1.60, +2.77] | +0.58 [+0.34, +0.83] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – |
| clean | 80 | missing | 0.2 | – | – | – | – | – |
| clean | 80 | missing | 0.5 | – | – | – | – | – |
| clean | 80 | reversed | 0.2 | +0.56 [+0.33, +0.77] | +0.58 [+0.33, +0.82] | +1.53 [+0.91, +2.20] | +2.14 [+1.45, +2.99] | +0.57 [+0.36, +0.76] |
| clean | 80 | reversed | 0.5 | +0.95 [+0.69, +1.21] | +0.95 [+0.66, +1.22] | +2.06 [+1.45, +2.74] | +3.08 [+2.50, +3.80] | +1.53 [+1.24, +1.85] |
