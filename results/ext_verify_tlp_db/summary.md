# ext_verify_tlp_db

Skeptic probe (verify_tlp): single vs double bootstrap TLP on cells the tlp probe did not cover (T=40; extra). D-07H development, 6 topologies, exploratory.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | targeted_lp | 6/6 | 0.886 | 0.886 | 2.721 | 4.98 | 0.549 | 0.000 | 0.350 |
| clean | 40 | none | 0.0 | targeted_lp_db | 6/6 | 0.876 | 0.876 | 2.729 | 5.40 | 0.513 | 0.000 | 0.289 |
| clean | 40 | extra | 0.5 | targeted_lp | 6/6 | 0.900 | 0.900 | 3.021 | 4.94 | 0.536 | 0.000 | 0.318 |
| clean | 40 | extra | 0.5 | targeted_lp_db | 6/6 | 0.910 | 0.910 | 2.954 | 4.98 | 0.556 | 0.000 | 0.360 |
| clean | 40 | missing | 0.5 | targeted_lp | 6/6 | 0.811 | 0.820 | 2.618 | 5.94 | 0.604 | 0.035 | 0.479 |
| clean | 40 | missing | 0.5 | targeted_lp_db | 6/6 | 0.796 | 0.803 | 2.642 | 6.43 | 0.594 | 0.040 | 0.533 |
| clean | 80 | none | 0.0 | targeted_lp | 6/6 | 0.935 | 0.935 | 2.569 | 4.54 | 0.353 | 0.000 | 0.267 |
| clean | 80 | none | 0.0 | targeted_lp_db | 6/6 | 0.896 | 0.896 | 2.171 | 3.95 | 0.355 | 0.000 | 0.262 |
| clean | 80 | extra | 0.5 | targeted_lp | 6/6 | 0.920 | 0.920 | 2.781 | 4.72 | 0.395 | 0.000 | 0.284 |
| clean | 80 | extra | 0.5 | targeted_lp_db | 6/6 | 0.866 | 0.866 | 2.170 | 4.63 | 0.405 | 0.000 | 0.261 |
| clean | 80 | missing | 0.5 | targeted_lp | 6/6 | 0.871 | 0.865 | 2.673 | 5.58 | 0.473 | 0.045 | 0.474 |
| clean | 80 | missing | 0.5 | targeted_lp_db | 6/6 | 0.816 | 0.822 | 2.122 | 6.48 | 0.506 | 0.050 | 0.508 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp_db |
|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.42 [+0.06, +0.79] |
| clean | 40 | extra | 0.5 | +0.04 [-0.46, +0.49] |
| clean | 40 | missing | 0.5 | +0.49 [-0.39, +1.43] |
| clean | 80 | none | 0.0 | -0.59 [-1.14, -0.15] |
| clean | 80 | extra | 0.5 | -0.08 [-0.50, +0.42] |
| clean | 80 | missing | 0.5 | +0.89 [-0.17, +2.31] |
