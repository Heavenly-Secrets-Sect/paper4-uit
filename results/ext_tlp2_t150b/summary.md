# ext_tlp2_t150b

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['extra', 0.2], ['extra', 0.5]] at T=[150]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.304 | 1.59 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | targeted_lp | 60/60 | 0.955 | 0.955 | 1.451 | 1.89 | 0.232 | 0.000 | 0.198 |
| clean | 150 | extra | 0.2 | tlp2_lp_cal | 60/60 | 0.970 | 0.970 | 1.614 | 1.93 | 0.240 | 0.000 | 0.201 |
| clean | 150 | extra | 0.2 | tlp2_db | 60/60 | 0.942 | 0.942 | 1.381 | 1.91 | 0.221 | 0.000 | 0.192 |
| clean | 150 | extra | 0.2 | tlp2_db90 | 60/60 | 0.903 | 0.903 | 1.147 | 2.02 | 0.221 | 0.000 | 0.192 |
| clean | 150 | extra | 0.2 | tlp2_db_p3 | 60/60 | 0.939 | 0.939 | 1.319 | 1.85 | 0.230 | 0.000 | 0.197 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.374 | 1.65 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | targeted_lp | 60/60 | 0.955 | 0.955 | 1.499 | 1.91 | 0.243 | 0.000 | 0.210 |
| clean | 150 | extra | 0.5 | tlp2_lp_cal | 60/60 | 0.968 | 0.968 | 1.644 | 1.99 | 0.239 | 0.000 | 0.207 |
| clean | 150 | extra | 0.5 | tlp2_db | 60/60 | 0.935 | 0.935 | 1.409 | 2.02 | 0.227 | 0.000 | 0.207 |
| clean | 150 | extra | 0.5 | tlp2_db90 | 60/60 | 0.901 | 0.901 | 1.171 | 2.12 | 0.227 | 0.000 | 0.207 |
| clean | 150 | extra | 0.5 | tlp2_db_p3 | 60/60 | 0.942 | 0.942 | 1.390 | 1.86 | 0.232 | 0.000 | 0.205 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | -0.30 [-0.43, -0.17] | +0.04 [+0.00, +0.09] | +0.03 [-0.07, +0.12] | +0.13 [-0.00, +0.29] | -0.03 [-0.10, +0.03] |
| clean | 150 | extra | 0.5 | -0.26 [-0.38, -0.14] | +0.07 [+0.05, +0.10] | +0.10 [+0.01, +0.20] | +0.20 [+0.06, +0.35] | -0.05 [-0.09, -0.01] |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | +0.30 [+0.17, +0.43] | +0.34 [+0.20, +0.49] | +0.32 [+0.20, +0.46] | +0.43 [+0.29, +0.59] | +0.27 [+0.16, +0.36] |
| clean | 150 | extra | 0.5 | +0.26 [+0.14, +0.38] | +0.33 [+0.22, +0.45] | +0.36 [+0.23, +0.49] | +0.46 [+0.28, +0.64] | +0.21 [+0.10, +0.32] |
| clean | 150 | missing | 0.2 | – | – | – | – | – |
| clean | 150 | missing | 0.5 | – | – | – | – | – |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |
