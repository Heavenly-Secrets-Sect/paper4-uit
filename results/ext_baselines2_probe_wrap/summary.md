# ext_baselines2_probe_wrap

Plumbing check of run_eval.py on D-07H development (2 topologies, T=80, calibration on 3 D-07H topologies). Not evaluation.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | tolerant_v4 | 2/2 | 0.985 | 0.985 | 1.730 | 2.06 | 0.233 | 0.000 | 0.200 |
| clean | 80 | none | 0.0 | pselect_union_v2 | 2/2 | 0.896 | 0.896 | 2.048 | 3.63 | 0.357 | 0.000 | 0.276 |
| clean | 80 | none | 0.0 | pselect_union_v2_cal | 2/2 | 0.940 | 0.940 | 2.457 | 3.66 | 0.357 | 0.000 | 0.276 |
| clean | 80 | none | 0.0 | bvar_minnesota_v2 | 2/2 | 0.910 | 0.910 | 1.413 | 2.13 | 0.299 | 0.000 | 0.226 |
| clean | 80 | none | 0.0 | bvar_minnesota_v2_cal | 2/2 | 0.910 | 0.910 | 1.413 | 2.13 | 0.299 | 0.000 | 0.226 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 2/2 | 0.970 | 0.970 | 2.825 | 3.32 | 0.361 | 0.000 | 0.331 |
| clean | 80 | missing | 0.2 | pselect_union_v2 | 2/2 | 0.925 | 0.925 | 2.167 | 3.37 | 0.405 | 0.000 | 0.241 |
| clean | 80 | missing | 0.2 | pselect_union_v2_cal | 2/2 | 0.940 | 0.940 | 2.601 | 3.28 | 0.405 | 0.000 | 0.241 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2 | 2/2 | 0.776 | 0.776 | 1.352 | 6.55 | 0.311 | 0.000 | 0.213 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2_cal | 2/2 | 0.970 | 0.970 | 4.733 | 5.86 | 0.311 | 0.000 | 0.213 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | pselect_union_v2 | pselect_union_v2_cal | bvar_minnesota_v2 | bvar_minnesota_v2_cal |
|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | +1.57 [+1.33, +1.82] | +1.60 [+1.27, +1.92] | +0.07 [+0.01, +0.13] | +0.07 [+0.01, +0.13] |
| clean | 80 | missing | 0.2 | +0.06 [-0.50, +0.61] | -0.04 [-0.18, +0.11] | +3.23 [+1.47, +4.99] | +2.55 [+1.79, +3.30] |
