# ext_tlp2_smoke

Smoke test of experiments/ext/tlp2/run_cells.py (cell filter) on D-07H development, 2 topologies, 1 replicate. Not an evaluation.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | tolerant_v4 | 2/2 | 0.985 | 0.985 | 1.730 | 2.06 | 0.233 | 0.000 | 0.200 |
| clean | 80 | none | 0.0 | targeted_lp | 2/2 | 0.940 | 0.940 | 2.655 | 3.07 | 0.346 | 0.000 | 0.226 |
| clean | 80 | none | 0.0 | tlp2_lp_cal | 2/2 | 0.955 | 0.955 | 2.768 | 2.94 | 0.382 | 0.000 | 0.258 |
| clean | 80 | none | 0.0 | tlp2_db_p3 | 2/2 | 0.925 | 0.925 | 2.050 | 2.54 | 0.364 | 0.000 | 0.214 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 2/2 | 1.000 | 1.000 | 2.080 | 2.16 | 0.278 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.5 | targeted_lp | 2/2 | 0.925 | 0.925 | 2.836 | 4.81 | 0.359 | 0.000 | 0.263 |
| clean | 80 | reversed | 0.5 | tlp2_lp_cal | 2/2 | 0.910 | 0.910 | 2.791 | 4.81 | 0.353 | 0.000 | 0.295 |
| clean | 80 | reversed | 0.5 | tlp2_db_p3 | 2/2 | 0.896 | 0.896 | 2.005 | 4.15 | 0.385 | 0.000 | 0.249 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db_p3 |
|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | -1.01 [-1.46, -0.56] | -0.13 [-0.25, -0.01] | -0.53 [-0.65, -0.41] |
| clean | 80 | extra | 0.2 | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – |
| clean | 80 | missing | 0.2 | – | – | – |
| clean | 80 | missing | 0.5 | – | – | – |
| clean | 80 | reversed | 0.2 | – | – | – |
| clean | 80 | reversed | 0.5 | -2.65 [-4.15, -1.15] | -0.00 [-0.11, +0.11] | -0.66 [-0.70, -0.61] |
