# ext_eiv2_smoke_d07h

eiv2 driver smoke test on D-07H development (1 topology), not an evaluation.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 19, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| noise0.3 | 80 | none | 0.0 | plugin | 1/1 | 0.711 | 0.711 | 1.229 | 3.02 | 0.336 | 0.000 | 0.266 |
| noise0.3 | 80 | none | 0.0 | tolerant_v4 | 1/1 | 0.842 | 0.842 | 1.578 | 2.42 | 0.336 | 0.000 | 0.266 |
| noise0.3 | 80 | none | 0.0 | tolerant_eiv2 | 1/1 | 0.947 | 0.947 | 2.043 | 2.51 | 0.298 | 0.000 | 0.233 |
| noise0.3 | 80 | none | 0.0 | plugin_eiv2 | 1/1 | 0.895 | 0.895 | 1.703 | 3.17 | 0.298 | 0.000 | 0.233 |
| noise0.3 | 80 | missing | 0.2 | plugin | 1/1 | 0.447 | 0.447 | 0.802 | 12.97 | 0.434 | 0.000 | 0.245 |
| noise0.3 | 80 | missing | 0.2 | tolerant_v4 | 1/1 | 0.895 | 0.895 | 2.302 | 3.99 | 0.438 | 0.000 | 0.547 |
| noise0.3 | 80 | missing | 0.2 | tolerant_eiv2 | 1/1 | 0.974 | 0.974 | 3.981 | 4.28 | 0.433 | 0.000 | 0.461 |
| noise0.3 | 80 | missing | 0.2 | plugin_eiv2 | 1/1 | 0.579 | 0.579 | 1.326 | 9.95 | 0.503 | 0.000 | 0.358 |
| noise0.3 | 80 | reversed | 0.2 | plugin | 1/1 | 0.737 | 0.737 | 1.003 | 5.28 | 0.320 | 0.000 | 0.303 |
| noise0.3 | 80 | reversed | 0.2 | tolerant_v4 | 1/1 | 0.842 | 0.842 | 1.601 | 3.30 | 0.315 | 0.000 | 0.303 |
| noise0.3 | 80 | reversed | 0.2 | tolerant_eiv2 | 1/1 | 1.000 | 1.000 | 3.260 | 3.34 | 0.350 | 0.000 | 0.238 |
| noise0.3 | 80 | reversed | 0.2 | plugin_eiv2 | 1/1 | 0.868 | 0.868 | 1.848 | 2.87 | 0.297 | 0.000 | 0.238 |
| het0.3 | 80 | none | 0.0 | plugin | 1/1 | 0.553 | 0.553 | 1.141 | 6.58 | 0.348 | 0.000 | 0.415 |
| het0.3 | 80 | none | 0.0 | tolerant_v4 | 1/1 | 0.737 | 0.737 | 1.582 | 4.30 | 0.348 | 0.000 | 0.415 |
| het0.3 | 80 | none | 0.0 | tolerant_eiv2 | 1/1 | 0.789 | 0.789 | 1.880 | 3.58 | 0.535 | 0.000 | 0.455 |
| het0.3 | 80 | none | 0.0 | plugin_eiv2 | 1/1 | 0.684 | 0.684 | 1.482 | 5.12 | 0.535 | 0.000 | 0.455 |
| het0.3 | 80 | missing | 0.2 | plugin | 1/1 | 0.395 | 0.395 | 0.907 | 14.49 | 0.452 | 0.000 | 0.366 |
| het0.3 | 80 | missing | 0.2 | tolerant_v4 | 1/1 | 0.895 | 0.895 | 2.530 | 3.80 | 0.375 | 0.000 | 0.388 |
| het0.3 | 80 | missing | 0.2 | tolerant_eiv2 | 1/1 | 1.000 | 1.000 | 4.137 | 4.26 | 0.432 | 0.000 | 0.377 |
| het0.3 | 80 | missing | 0.2 | plugin_eiv2 | 1/1 | 0.500 | 0.500 | 1.132 | 14.37 | 0.565 | 0.000 | 0.375 |
| het0.3 | 80 | reversed | 0.2 | plugin | 1/1 | 0.737 | 0.737 | 1.121 | 7.30 | 0.324 | 0.000 | 0.415 |
| het0.3 | 80 | reversed | 0.2 | tolerant_v4 | 1/1 | 0.789 | 0.789 | 2.035 | 4.10 | 0.375 | 0.000 | 0.415 |
| het0.3 | 80 | reversed | 0.2 | tolerant_eiv2 | 1/1 | 0.947 | 0.947 | 3.123 | 3.72 | 0.562 | 0.000 | 0.448 |
| het0.3 | 80 | reversed | 0.2 | plugin_eiv2 | 1/1 | 0.711 | 0.711 | 1.501 | 6.52 | 0.527 | 0.000 | 0.448 |

## Interval score difference vs `plugin` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tolerant_eiv2 | plugin_eiv2 |
|---|---|---|---|---|---|---|
| noise0.3 | 80 | none | 0.0 | -0.60 [-0.60, -0.60] | -0.51 [-0.51, -0.51] | +0.15 [+0.15, +0.15] |
| noise0.3 | 80 | missing | 0.2 | -8.98 [-8.98, -8.98] | -8.69 [-8.69, -8.69] | -3.02 [-3.02, -3.02] |
| noise0.3 | 80 | reversed | 0.2 | -1.98 [-1.98, -1.98] | -1.94 [-1.94, -1.94] | -2.40 [-2.40, -2.40] |
| het0.3 | 80 | none | 0.0 | -2.28 [-2.28, -2.28] | -3.00 [-3.00, -3.00] | -1.46 [-1.46, -1.46] |
| het0.3 | 80 | missing | 0.2 | -10.69 [-10.69, -10.69] | -10.23 [-10.23, -10.23] | -0.12 [-0.12, -0.12] |
| het0.3 | 80 | reversed | 0.2 | -3.20 [-3.20, -3.20] | -3.58 [-3.58, -3.58] | -0.78 [-0.78, -0.78] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | plugin | tolerant_eiv2 | plugin_eiv2 |
|---|---|---|---|---|---|---|
| noise0.3 | 80 | none | 0.0 | +0.60 [+0.60, +0.60] | +0.09 [+0.09, +0.09] | +0.76 [+0.76, +0.76] |
| noise0.3 | 80 | missing | 0.2 | +8.98 [+8.98, +8.98] | +0.29 [+0.29, +0.29] | +5.96 [+5.96, +5.96] |
| noise0.3 | 80 | reversed | 0.2 | +1.98 [+1.98, +1.98] | +0.04 [+0.04, +0.04] | -0.43 [-0.43, -0.43] |
| het0.3 | 80 | none | 0.0 | +2.28 [+2.28, +2.28] | -0.72 [-0.72, -0.72] | +0.82 [+0.82, +0.82] |
| het0.3 | 80 | missing | 0.2 | +10.69 [+10.69, +10.69] | +0.46 [+0.46, +0.46] | +10.57 [+10.57, +10.57] |
| het0.3 | 80 | reversed | 0.2 | +3.20 [+3.20, +3.20] | -0.38 [-0.38, -0.38] | +2.42 [+2.42, +2.42] |
