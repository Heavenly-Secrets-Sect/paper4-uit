# ext_v51fix_t150tau

v51fix (R3-2, docs/ext/v51fix.md 1.C): descriptive tau sensitivity. tolerant_v5_1_t294 (= tolerant_v5_1 with TAU 2.9370, all-lag branch at T=150) against frozen tolerant_v4, T=150 only, D-07 development, a2 cell list kept so tolerant_v4 rows equal ext_v51_eval (E1).

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1_t294 | 60/60 | 0.964 | 0.964 | 1.286 | 1.58 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.326 | 1.58 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_t294 | 60/60 | 0.965 | 0.965 | 1.330 | 1.59 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.376 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_t294 | 60/60 | 0.969 | 0.969 | 1.393 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.691 | 2.06 | 0.259 | 0.000 | 0.215 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_t294 | 60/60 | 0.974 | 0.974 | 1.747 | 2.08 | 0.256 | 0.000 | 0.221 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.761 | 2.22 | 0.255 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_t294 | 60/60 | 0.975 | 0.975 | 1.805 | 2.26 | 0.260 | 0.000 | 0.205 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.970 | 0.970 | 1.532 | 1.89 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_t294 | 60/60 | 0.962 | 0.962 | 1.531 | 1.86 | 0.226 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 1.584 | 2.02 | 0.255 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_t294 | 60/60 | 0.954 | 0.954 | 1.536 | 2.03 | 0.248 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1_t294 |
|---|---|---|---|---|
| clean | 150 | none | 0.0 | +0.01 [-0.02, +0.04] |
| clean | 150 | extra | 0.2 | +0.01 [-0.03, +0.04] |
| clean | 150 | extra | 0.5 | -0.00 [-0.03, +0.03] |
| clean | 150 | missing | 0.2 | +0.03 [-0.00, +0.06] |
| clean | 150 | missing | 0.5 | +0.05 [+0.01, +0.09] |
| clean | 150 | reversed | 0.2 | -0.03 [-0.06, -0.01] |
| clean | 150 | reversed | 0.5 | +0.01 [-0.04, +0.07] |
