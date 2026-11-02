# ext_r4levboot_g

Round 4 levboot: leverage-adjusted residual pools (L2 HC2-type, L3 HC3-type; W3 in ext_r4levboot_gw) in the residual bootstrap of tolerant_v5_1, vs tolerant_v5_1 with frozen factors (experiments/ext/v51/frozen_v4_v51.json), grid G, D-07 development, seeds of ext_v51_eval. Arms re-tuned on D-07H development. Rule in docs/ext/r4levboot.md. Run through experiments/ext/r4levboot/run.py.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | r4levboot_L2 | 60/60 | 0.923 | 0.923 | 2.878 | 4.38 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | r4levboot_L3 | 60/60 | 0.939 | 0.939 | 3.387 | 4.88 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | r4levboot_L2 | 60/60 | 0.915 | 0.915 | 2.917 | 4.64 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | r4levboot_L3 | 60/60 | 0.923 | 0.923 | 3.113 | 5.07 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | r4levboot_L2 | 60/60 | 0.922 | 0.922 | 3.244 | 4.78 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | r4levboot_L3 | 60/60 | 0.931 | 0.931 | 3.502 | 5.15 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.922 | 0.922 | 3.290 | 4.84 | 0.553 | 0.000 | 0.382 |
| clean | 40 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.934 | 0.934 | 3.399 | 4.81 | 0.546 | 0.000 | 0.382 |
| clean | 40 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.935 | 0.935 | 3.446 | 5.15 | 0.545 | 0.000 | 0.382 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.790 | 5.09 | 0.572 | 0.000 | 0.401 |
| clean | 40 | missing | 0.5 | r4levboot_L2 | 60/60 | 0.948 | 0.948 | 3.951 | 5.23 | 0.571 | 0.000 | 0.401 |
| clean | 40 | missing | 0.5 | r4levboot_L3 | 60/60 | 0.951 | 0.951 | 4.007 | 5.42 | 0.568 | 0.000 | 0.401 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.929 | 0.929 | 3.070 | 4.69 | 0.481 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.933 | 0.933 | 3.311 | 5.00 | 0.467 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | r4levboot_L2 | 60/60 | 0.919 | 0.919 | 3.257 | 4.75 | 0.525 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | r4levboot_L3 | 60/60 | 0.917 | 0.917 | 3.336 | 5.06 | 0.519 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | r4levboot_L2 | 60/60 | 0.934 | 0.934 | 1.793 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | r4levboot_L3 | 60/60 | 0.928 | 0.928 | 1.731 | 2.61 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | r4levboot_L2 | 60/60 | 0.928 | 0.928 | 1.744 | 2.54 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | r4levboot_L3 | 60/60 | 0.934 | 0.934 | 1.818 | 2.59 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | r4levboot_L2 | 60/60 | 0.926 | 0.926 | 1.868 | 2.66 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | r4levboot_L3 | 60/60 | 0.932 | 0.932 | 1.899 | 2.68 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.193 | 2.84 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.946 | 0.946 | 2.254 | 2.87 | 0.359 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.946 | 0.946 | 2.231 | 2.95 | 0.350 | 0.000 | 0.229 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.424 | 3.10 | 0.364 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | r4levboot_L2 | 60/60 | 0.955 | 0.955 | 2.431 | 3.09 | 0.374 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | r4levboot_L3 | 60/60 | 0.953 | 0.953 | 2.474 | 3.13 | 0.377 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.942 | 0.942 | 2.049 | 2.79 | 0.346 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.947 | 0.947 | 2.103 | 2.90 | 0.343 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | r4levboot_L2 | 60/60 | 0.917 | 0.917 | 2.039 | 3.04 | 0.372 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | r4levboot_L3 | 60/60 | 0.921 | 0.921 | 2.116 | 3.13 | 0.353 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | r4levboot_L2 | 60/60 | 0.963 | 0.963 | 1.268 | 1.58 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | r4levboot_L3 | 60/60 | 0.963 | 0.963 | 1.283 | 1.59 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | r4levboot_L2 | 60/60 | 0.964 | 0.964 | 1.327 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | r4levboot_L3 | 60/60 | 0.970 | 0.970 | 1.364 | 1.63 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | r4levboot_L2 | 60/60 | 0.963 | 0.963 | 1.375 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | r4levboot_L3 | 60/60 | 0.968 | 0.968 | 1.416 | 1.71 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.966 | 0.966 | 1.463 | 1.76 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | r4levboot_L2 | 60/60 | 0.975 | 0.975 | 1.525 | 1.80 | 0.219 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | r4levboot_L3 | 60/60 | 0.975 | 0.975 | 1.614 | 1.84 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 1.596 | 1.99 | 0.245 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | r4levboot_L2 | 60/60 | 0.975 | 0.975 | 1.656 | 2.05 | 0.242 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | r4levboot_L3 | 60/60 | 0.977 | 0.977 | 1.719 | 2.09 | 0.242 | 0.000 | 0.175 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | r4levboot_L2 | 60/60 | 0.958 | 0.958 | 1.452 | 1.83 | 0.219 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | r4levboot_L3 | 60/60 | 0.963 | 0.963 | 1.487 | 1.88 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | r4levboot_L2 | 60/60 | 0.944 | 0.944 | 1.500 | 2.03 | 0.250 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | r4levboot_L3 | 60/60 | 0.948 | 0.948 | 1.533 | 2.06 | 0.252 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4levboot_L2 | r4levboot_L3 |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.01 [-0.07, +0.07] | +0.51 [+0.21, +0.79] |
| clean | 40 | extra | 0.2 | +0.02 [-0.05, +0.08] | +0.45 [+0.27, +0.65] |
| clean | 40 | extra | 0.5 | -0.04 [-0.13, +0.03] | +0.34 [+0.19, +0.50] |
| clean | 40 | missing | 0.2 | -0.02 [-0.17, +0.11] | +0.32 [+0.20, +0.42] |
| clean | 40 | missing | 0.5 | +0.14 [+0.05, +0.22] | +0.33 [+0.17, +0.50] |
| clean | 40 | reversed | 0.2 | -0.01 [-0.06, +0.04] | +0.30 [+0.16, +0.46] |
| clean | 40 | reversed | 0.5 | +0.01 [-0.02, +0.05] | +0.31 [+0.19, +0.45] |
| clean | 80 | none | 0.0 | -0.00 [-0.02, +0.02] | +0.08 [+0.03, +0.13] |
| clean | 80 | extra | 0.2 | +0.01 [-0.01, +0.03] | +0.06 [+0.03, +0.10] |
| clean | 80 | extra | 0.5 | -0.00 [-0.01, +0.00] | +0.01 [-0.02, +0.05] |
| clean | 80 | missing | 0.2 | +0.03 [-0.00, +0.08] | +0.10 [+0.04, +0.19] |
| clean | 80 | missing | 0.5 | -0.01 [-0.05, +0.03] | +0.03 [-0.03, +0.08] |
| clean | 80 | reversed | 0.2 | -0.00 [-0.01, +0.01] | +0.11 [+0.06, +0.17] |
| clean | 80 | reversed | 0.5 | -0.00 [-0.02, +0.01] | +0.08 [+0.03, +0.15] |
| clean | 150 | none | 0.0 | +0.00 [-0.00, +0.01] | +0.02 [+0.01, +0.03] |
| clean | 150 | extra | 0.2 | -0.00 [-0.00, +0.00] | +0.03 [+0.02, +0.05] |
| clean | 150 | extra | 0.5 | +0.00 [+0.00, +0.01] | +0.04 [+0.02, +0.05] |
| clean | 150 | missing | 0.2 | +0.04 [+0.02, +0.06] | +0.08 [+0.05, +0.10] |
| clean | 150 | missing | 0.5 | +0.06 [+0.04, +0.08] | +0.10 [+0.07, +0.13] |
| clean | 150 | reversed | 0.2 | +0.01 [+0.00, +0.01] | +0.05 [+0.04, +0.07] |
| clean | 150 | reversed | 0.5 | +0.00 [-0.00, +0.00] | +0.03 [+0.00, +0.05] |
