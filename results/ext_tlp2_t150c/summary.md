# ext_tlp2_t150c

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['missing', 0.2], ['missing', 0.5]] at T=[150]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.972 | 0.972 | 1.706 | 2.06 | 0.256 | 0.000 | 0.221 |
| clean | 150 | missing | 0.2 | targeted_lp | 60/60 | 0.931 | 0.931 | 1.509 | 2.26 | 0.268 | 0.001 | 0.207 |
| clean | 150 | missing | 0.2 | tlp2_lp_cal | 60/60 | 0.976 | 0.976 | 1.982 | 2.35 | 0.254 | 0.001 | 0.203 |
| clean | 150 | missing | 0.2 | tlp2_db | 60/60 | 0.913 | 0.913 | 1.458 | 2.35 | 0.262 | 0.001 | 0.214 |
| clean | 150 | missing | 0.2 | tlp2_db90 | 60/60 | 0.856 | 0.856 | 1.201 | 2.64 | 0.262 | 0.001 | 0.214 |
| clean | 150 | missing | 0.2 | tlp2_db_p3 | 60/60 | 0.915 | 0.915 | 1.389 | 2.34 | 0.254 | 0.001 | 0.195 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.969 | 0.969 | 1.766 | 2.19 | 0.260 | 0.000 | 0.211 |
| clean | 150 | missing | 0.5 | targeted_lp | 60/60 | 0.908 | 0.907 | 1.531 | 2.60 | 0.307 | 0.012 | 0.239 |
| clean | 150 | missing | 0.5 | tlp2_lp_cal | 60/60 | 0.964 | 0.963 | 2.000 | 2.61 | 0.309 | 0.012 | 0.232 |
| clean | 150 | missing | 0.5 | tlp2_db | 60/60 | 0.864 | 0.865 | 1.534 | 3.06 | 0.350 | 0.013 | 0.275 |
| clean | 150 | missing | 0.5 | tlp2_db90 | 60/60 | 0.800 | 0.802 | 1.277 | 3.61 | 0.350 | 0.013 | 0.275 |
| clean | 150 | missing | 0.5 | tlp2_db_p3 | 60/60 | 0.869 | 0.871 | 1.466 | 2.99 | 0.307 | 0.012 | 0.251 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | -0.20 [-0.36, -0.03] | +0.10 [+0.01, +0.18] | +0.10 [+0.01, +0.19] | +0.38 [+0.27, +0.49] | +0.08 [+0.00, +0.17] |
| clean | 150 | missing | 0.5 | -0.41 [-0.58, -0.23] | +0.02 [-0.07, +0.10] | +0.46 [+0.34, +0.59] | +1.02 [+0.85, +1.19] | +0.40 [+0.30, +0.49] |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 | tlp2_db_p3 |
|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – |
| clean | 150 | missing | 0.2 | +0.20 [+0.03, +0.36] | +0.30 [+0.19, +0.40] | +0.30 [+0.15, +0.46] | +0.58 [+0.40, +0.77] | +0.29 [+0.14, +0.44] |
| clean | 150 | missing | 0.5 | +0.41 [+0.23, +0.58] | +0.42 [+0.28, +0.56] | +0.87 [+0.66, +1.07] | +1.42 [+1.17, +1.68] | +0.80 [+0.62, +0.97] |
| clean | 150 | reversed | 0.2 | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – |
