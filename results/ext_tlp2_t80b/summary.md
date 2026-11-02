# ext_tlp2_t80b

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['missing', 0.2], ['missing', 0.5]] at T=[80]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.956 | 0.956 | 2.596 | 3.24 | 0.414 | 0.000 | 0.284 |
| clean | 80 | missing | 0.2 | targeted_lp | 60/60 | 0.933 | 0.934 | 2.507 | 3.46 | 0.429 | 0.002 | 0.329 |
| clean | 80 | missing | 0.2 | tlp2_lp_cal | 60/60 | 0.959 | 0.959 | 2.774 | 3.46 | 0.434 | 0.002 | 0.322 |
| clean | 80 | missing | 0.2 | tlp2_db | 60/60 | 0.881 | 0.882 | 2.387 | 4.71 | 0.451 | 0.006 | 0.319 |
| clean | 80 | missing | 0.2 | tlp2_db90 | 60/60 | 0.802 | 0.803 | 1.883 | 5.74 | 0.451 | 0.006 | 0.319 |
| clean | 80 | missing | 0.2 | tlp2_db_p3 | 60/60 | 0.858 | 0.859 | 1.887 | 3.95 | 0.408 | 0.002 | 0.313 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.960 | 0.960 | 2.714 | 3.39 | 0.413 | 0.000 | 0.279 |
| clean | 80 | missing | 0.5 | targeted_lp | 60/60 | 0.898 | 0.897 | 2.542 | 4.17 | 0.556 | 0.034 | 0.473 |
| clean | 80 | missing | 0.5 | tlp2_lp_cal | 60/60 | 0.928 | 0.927 | 2.764 | 4.02 | 0.556 | 0.035 | 0.453 |
| clean | 80 | missing | 0.5 | tlp2_db | 60/60 | 0.825 | 0.827 | 2.454 | 6.00 | 0.638 | 0.064 | 0.529 |
| clean | 80 | missing | 0.5 | tlp2_db90 | 60/60 | 0.725 | 0.733 | 1.914 | 7.85 | 0.638 | 0.064 | 0.529 |
| clean | 80 | missing | 0.5 | tlp2_db_p3 | 60/60 | 0.797 | 0.803 | 2.002 | 5.47 | 0.528 | 0.045 | 0.465 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – |
| clean | 80 | missing | 0.2 | -0.22 [-0.41, -0.01] | +0.01 [-0.08, +0.08] | +1.25 [+0.85, +1.69] | +2.28 [+1.79, +2.81] | +0.49 [+0.29, +0.69] |
| clean | 80 | missing | 0.5 | -0.78 [-1.09, -0.50] | -0.15 [-0.29, -0.03] | +1.83 [+1.33, +2.34] | +3.67 [+3.07, +4.34] | +1.29 [+1.06, +1.54] |
| clean | 80 | reversed | 0.2 | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – |
| clean | 80 | missing | 0.2 | +0.22 [+0.01, +0.41] | +0.22 [+0.05, +0.42] | +1.47 [+1.01, +1.94] | +2.50 [+1.95, +3.07] | +0.71 [+0.45, +1.00] |
| clean | 80 | missing | 0.5 | +0.78 [+0.50, +1.09] | +0.63 [+0.44, +0.81] | +2.61 [+2.11, +3.12] | +4.45 [+3.78, +5.21] | +2.07 [+1.66, +2.53] |
| clean | 80 | reversed | 0.2 | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – |
