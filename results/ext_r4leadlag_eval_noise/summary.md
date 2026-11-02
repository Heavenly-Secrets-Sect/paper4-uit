# ext_r4leadlag_eval_noise

r4leadlag (descriptive check): noise0.1 x missing-0.2 x T 80/150, D-07 development, seeds of ext_v51_a1. Run through experiments/ext/r4leadlag/drive.py. Rule in docs/ext/r4leadlag.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 2.152 | 3.26 | 0.420 | 0.000 | 0.290 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.903 | 0.903 | 2.084 | 3.31 | 0.418 | 0.000 | 0.292 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.906 | 0.906 | 2.077 | 3.28 | 0.412 | 0.000 | 0.292 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.397 | 2.24 | 0.265 | 0.000 | 0.218 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.927 | 0.927 | 1.457 | 2.20 | 0.273 | 0.000 | 0.218 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.935 | 0.935 | 1.569 | 2.20 | 0.280 | 0.000 | 0.218 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1_leadlag | tolerant_v5_1_leadlag_skel |
|---|---|---|---|---|---|
| noise0.1 | 80 | none | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| noise0.1 | 80 | missing | 0.2 | +0.05 [+0.00, +0.11] | +0.02 [-0.06, +0.12] |
| noise0.1 | 150 | none | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| noise0.1 | 150 | missing | 0.2 | -0.05 [-0.07, -0.02] | -0.04 [-0.10, +0.01] |
