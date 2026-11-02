# ext_r4lfdropen_eval

r4lfdropen: tolerant_v5_1_lfdr (two-groups local-fdr probabilistic targeted opening, pi0 fixed by the stated missing count) vs tolerant_v5_1 (frozen factors) on the a2 grid, D-07 development, seed_base 20261102 (pairs with results/ext_v51_eval). Width factor of the candidate tuned on D-07H development. Rule in docs/ext/r4lfdropen.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.922 | 0.922 | 3.290 | 4.84 | 0.553 | 0.000 | 0.382 |
| clean | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.953 | 0.953 | 4.124 | 5.46 | 0.521 | 0.000 | 0.319 |
| clean | 40 | missing | 0.5 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.790 | 5.09 | 0.572 | 0.000 | 0.401 |
| clean | 40 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.950 | 0.950 | 4.262 | 5.56 | 0.593 | 0.000 | 0.361 |
| clean | 40 | reversed | 0.2 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | oracle | 60/60 | 0.880 | 0.880 | 1.473 | 2.72 | 0.273 | 0.000 | 0.120 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.193 | 2.84 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.953 | 0.953 | 2.281 | 3.02 | 0.354 | 0.000 | 0.228 |
| clean | 80 | missing | 0.5 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.424 | 3.10 | 0.364 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.936 | 0.936 | 2.535 | 3.55 | 0.405 | 0.000 | 0.219 |
| clean | 80 | reversed | 0.2 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | oracle | 60/60 | 0.899 | 0.899 | 1.028 | 1.68 | 0.190 | 0.000 | 0.083 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.966 | 0.966 | 1.463 | 1.76 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.963 | 0.963 | 1.405 | 1.78 | 0.209 | 0.000 | 0.173 |
| clean | 150 | missing | 0.5 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 1.596 | 1.99 | 0.245 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.954 | 0.954 | 1.542 | 2.26 | 0.239 | 0.000 | 0.155 |
| clean | 150 | reversed | 0.2 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | oracle | 60/60 | 0.943 | 0.943 | 0.780 | 1.02 | 0.133 | 0.000 | 0.053 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_lfdr | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v5_1_lfdr |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -1.65 [-2.01, -1.38] | +0.00 [+0.00, +0.00] |
| clean | 40 | extra | 0.2 | -1.90 [-2.51, -1.49] | +0.00 [+0.00, +0.00] |
| clean | 40 | extra | 0.5 | -2.09 [-2.57, -1.75] | +0.00 [+0.00, +0.00] |
| clean | 40 | missing | 0.2 | -2.12 [-2.50, -1.76] | +0.62 [+0.27, +0.93] |
| clean | 40 | missing | 0.5 | -2.37 [-2.70, -2.00] | +0.47 [+0.25, +0.70] |
| clean | 40 | reversed | 0.2 | -1.98 [-2.65, -1.41] | +0.00 [+0.00, +0.00] |
| clean | 40 | reversed | 0.5 | -2.02 [-2.48, -1.58] | +0.00 [+0.00, +0.00] |
| clean | 80 | none | 0.0 | -0.86 [-1.01, -0.68] | +0.00 [+0.00, +0.00] |
| clean | 80 | extra | 0.2 | -0.85 [-1.03, -0.70] | +0.00 [+0.00, +0.00] |
| clean | 80 | extra | 0.5 | -0.99 [-1.17, -0.81] | +0.00 [+0.00, +0.00] |
| clean | 80 | missing | 0.2 | -1.16 [-1.33, -0.98] | +0.18 [+0.02, +0.32] |
| clean | 80 | missing | 0.5 | -1.42 [-1.58, -1.23] | +0.45 [+0.25, +0.64] |
| clean | 80 | reversed | 0.2 | -1.11 [-1.30, -0.93] | +0.00 [+0.00, +0.00] |
| clean | 80 | reversed | 0.5 | -1.37 [-1.58, -1.17] | +0.00 [+0.00, +0.00] |
| clean | 150 | none | 0.0 | -0.55 [-0.64, -0.46] | +0.00 [+0.00, +0.00] |
| clean | 150 | extra | 0.2 | -0.58 [-0.66, -0.50] | +0.00 [+0.00, +0.00] |
| clean | 150 | extra | 0.5 | -0.65 [-0.74, -0.57] | +0.00 [+0.00, +0.00] |
| clean | 150 | missing | 0.2 | -0.73 [-0.83, -0.65] | +0.02 [-0.06, +0.13] |
| clean | 150 | missing | 0.5 | -0.96 [-1.06, -0.86] | +0.28 [+0.11, +0.45] |
| clean | 150 | reversed | 0.2 | -0.80 [-0.91, -0.72] | +0.00 [+0.00, +0.00] |
| clean | 150 | reversed | 0.5 | -1.01 [-1.16, -0.87] | +0.00 [+0.00, +0.00] |
