# ext_r4levboot_smoke_d07h

Smoke test of the driver and analyzer on D-07H development only (2 topologies), not evidence.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 2/2 | 0.985 | 0.985 | 2.549 | 2.94 | 0.354 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | r4levboot_L2 | 2/2 | 0.910 | 0.910 | 1.887 | 2.86 | 0.354 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | r4levboot_L3 | 2/2 | 0.896 | 0.896 | 2.042 | 2.86 | 0.354 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | r4levboot_W3 | 2/2 | 0.940 | 0.940 | 2.215 | 3.12 | 0.354 | 0.000 | 0.235 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 2/2 | 0.955 | 0.955 | 2.978 | 3.65 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.2 | r4levboot_L2 | 2/2 | 0.955 | 0.955 | 2.660 | 3.47 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.2 | r4levboot_L3 | 2/2 | 0.925 | 0.925 | 2.702 | 3.48 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.2 | r4levboot_W3 | 2/2 | 0.910 | 0.910 | 2.428 | 3.83 | 0.406 | 0.000 | 0.320 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 3.208 | 3.48 | 0.392 | 0.000 | 0.336 |
| clean | 40 | extra | 0.5 | r4levboot_L2 | 2/2 | 0.940 | 0.940 | 2.851 | 3.31 | 0.392 | 0.000 | 0.336 |
| clean | 40 | extra | 0.5 | r4levboot_L3 | 2/2 | 0.955 | 0.955 | 2.971 | 3.38 | 0.392 | 0.000 | 0.336 |
| clean | 40 | extra | 0.5 | r4levboot_W3 | 2/2 | 0.925 | 0.925 | 2.765 | 3.62 | 0.392 | 0.000 | 0.336 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 3.094 | 4.13 | 0.443 | 0.000 | 0.227 |
| clean | 40 | missing | 0.2 | r4levboot_L2 | 2/2 | 0.925 | 0.925 | 2.620 | 4.43 | 0.440 | 0.000 | 0.227 |
| clean | 40 | missing | 0.2 | r4levboot_L3 | 2/2 | 0.940 | 0.940 | 3.009 | 4.60 | 0.416 | 0.000 | 0.227 |
| clean | 40 | missing | 0.2 | r4levboot_W3 | 2/2 | 0.940 | 0.940 | 2.731 | 4.61 | 0.429 | 0.000 | 0.227 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 2/2 | 0.910 | 0.910 | 3.789 | 5.31 | 0.604 | 0.000 | 0.554 |
| clean | 40 | missing | 0.5 | r4levboot_L2 | 2/2 | 0.866 | 0.866 | 3.186 | 5.82 | 0.610 | 0.000 | 0.554 |
| clean | 40 | missing | 0.5 | r4levboot_L3 | 2/2 | 0.910 | 0.910 | 3.485 | 5.38 | 0.617 | 0.000 | 0.554 |
| clean | 40 | missing | 0.5 | r4levboot_W3 | 2/2 | 0.925 | 0.925 | 3.555 | 5.29 | 0.564 | 0.000 | 0.554 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 2/2 | 0.970 | 0.970 | 2.956 | 3.60 | 0.432 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.2 | r4levboot_L2 | 2/2 | 0.955 | 0.955 | 2.370 | 3.24 | 0.439 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.2 | r4levboot_L3 | 2/2 | 0.910 | 0.910 | 2.416 | 3.39 | 0.450 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.2 | r4levboot_W3 | 2/2 | 0.910 | 0.910 | 2.128 | 3.43 | 0.429 | 0.000 | 0.278 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 2/2 | 0.940 | 0.940 | 3.087 | 4.27 | 0.593 | 0.000 | 0.572 |
| clean | 40 | reversed | 0.5 | r4levboot_L2 | 2/2 | 0.940 | 0.940 | 2.581 | 4.32 | 0.599 | 0.000 | 0.572 |
| clean | 40 | reversed | 0.5 | r4levboot_L3 | 2/2 | 0.925 | 0.925 | 2.441 | 4.47 | 0.592 | 0.000 | 0.572 |
| clean | 40 | reversed | 0.5 | r4levboot_W3 | 2/2 | 0.866 | 0.866 | 2.208 | 4.61 | 0.581 | 0.000 | 0.572 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4levboot_L2 | r4levboot_L3 | r4levboot_W3 |
|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.08 [-0.22, +0.06] | -0.09 [-0.26, +0.08] | +0.18 [-0.15, +0.50] |
| clean | 40 | extra | 0.2 | -0.18 [-0.28, -0.08] | -0.17 [-0.19, -0.15] | +0.19 [-0.20, +0.57] |
| clean | 40 | extra | 0.5 | -0.17 [-0.28, -0.06] | -0.10 [-0.27, +0.07] | +0.14 [-0.18, +0.45] |
| clean | 40 | missing | 0.2 | +0.30 [-0.23, +0.83] | +0.47 [+0.23, +0.70] | +0.48 [+0.01, +0.95] |
| clean | 40 | missing | 0.5 | +0.51 [+0.13, +0.90] | +0.07 [+0.01, +0.12] | -0.02 [-0.51, +0.48] |
| clean | 40 | reversed | 0.2 | -0.36 [-0.44, -0.28] | -0.21 [-0.53, +0.11] | -0.17 [-0.66, +0.31] |
| clean | 40 | reversed | 0.5 | +0.05 [-0.52, +0.62] | +0.20 [-0.53, +0.93] | +0.34 [-0.55, +1.23] |
