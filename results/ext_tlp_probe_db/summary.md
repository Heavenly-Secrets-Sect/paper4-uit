# ext_tlp_probe_db

Exploratory probe (D-07H development, 6 topologies): single-level targeted_lp vs the double bootstrap targeted_lp_db (B1 = 199, B2 = 49). Not an evaluation; see docs/ext/tlp.md.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | targeted_lp | 6/6 | 0.935 | 0.935 | 2.569 | 4.54 | 0.353 | 0.000 | 0.267 |
| clean | 80 | none | 0.0 | targeted_lp_db | 6/6 | 0.896 | 0.896 | 2.171 | 3.95 | 0.355 | 0.000 | 0.262 |
| clean | 80 | missing | 0.5 | targeted_lp | 6/6 | 0.886 | 0.884 | 2.819 | 5.80 | 0.541 | 0.060 | 0.487 |
| clean | 80 | missing | 0.5 | targeted_lp_db | 6/6 | 0.791 | 0.813 | 2.283 | 6.91 | 0.495 | 0.070 | 0.463 |
| clean | 80 | reversed | 0.5 | targeted_lp | 6/6 | 0.891 | 0.891 | 2.794 | 6.09 | 0.496 | 0.000 | 0.301 |
| clean | 80 | reversed | 0.5 | targeted_lp_db | 6/6 | 0.851 | 0.851 | 2.141 | 6.75 | 0.520 | 0.000 | 0.330 |
| clean | 150 | none | 0.0 | targeted_lp | 6/6 | 0.965 | 0.965 | 1.565 | 1.90 | 0.183 | 0.000 | 0.186 |
| clean | 150 | none | 0.0 | targeted_lp_db | 6/6 | 0.960 | 0.960 | 1.537 | 1.89 | 0.170 | 0.000 | 0.200 |
| clean | 150 | missing | 0.5 | targeted_lp | 6/6 | 0.910 | 0.910 | 1.650 | 2.57 | 0.353 | 0.005 | 0.314 |
| clean | 150 | missing | 0.5 | targeted_lp_db | 6/6 | 0.876 | 0.874 | 1.522 | 2.82 | 0.374 | 0.010 | 0.293 |
| clean | 150 | reversed | 0.5 | targeted_lp | 6/6 | 0.856 | 0.856 | 1.692 | 4.43 | 0.304 | 0.000 | 0.245 |
| clean | 150 | reversed | 0.5 | targeted_lp_db | 6/6 | 0.811 | 0.811 | 1.602 | 4.69 | 0.290 | 0.000 | 0.241 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp_db |
|---|---|---|---|---|
| clean | 80 | none | 0.0 | -0.59 [-1.14, -0.18] |
| clean | 80 | missing | 0.5 | +1.11 [-0.69, +3.14] |
| clean | 80 | reversed | 0.5 | +0.66 [-0.05, +1.75] |
| clean | 150 | none | 0.0 | -0.01 [-0.11, +0.06] |
| clean | 150 | missing | 0.5 | +0.25 [-0.02, +0.59] |
| clean | 150 | reversed | 0.5 | +0.25 [+0.04, +0.43] |
