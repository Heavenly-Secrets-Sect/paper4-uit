# ext_v51_a1

v51 (R2-2c): tolerant_v5_1 against frozen tolerant_v4 under one/three hidden common causes and 10% measurement noise (a1 scenarios, T 80/150), D-07 development, a1_latent_noise seeds. tolerant_v5 (round-1, duplicated-term bug) only in the T = 40 run, for time. Calibration on clean D-07H development with the a3_ges calibration block. Rule in docs/ext/v51.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.928 | 0.928 | 1.944 | 2.82 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 2.868 | 3.54 | 0.438 | 0.000 | 0.292 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 2.418 | 3.15 | 0.364 | 0.000 | 0.226 |
| latent1 | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.947 | 0.947 | 2.209 | 3.02 | 0.355 | 0.000 | 0.243 |
| latent1 | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.940 | 0.940 | 2.118 | 3.01 | 0.352 | 0.000 | 0.243 |
| latent1 | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.925 | 0.925 | 1.323 | 2.05 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.951 | 0.951 | 1.735 | 2.38 | 0.270 | 0.000 | 0.214 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.956 | 0.956 | 1.534 | 2.15 | 0.233 | 0.000 | 0.185 |
| latent1 | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 1.645 | 2.20 | 0.262 | 0.000 | 0.177 |
| latent1 | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.936 | 0.936 | 1.495 | 2.19 | 0.249 | 0.000 | 0.177 |
| latent3 | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.949 | 0.949 | 2.012 | 2.78 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.970 | 0.970 | 3.195 | 3.83 | 0.441 | 0.000 | 0.295 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.961 | 0.961 | 2.531 | 3.21 | 0.372 | 0.000 | 0.240 |
| latent3 | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.969 | 0.969 | 2.460 | 3.07 | 0.370 | 0.000 | 0.232 |
| latent3 | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.962 | 0.962 | 2.317 | 3.06 | 0.364 | 0.000 | 0.232 |
| latent3 | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.871 | 0.871 | 1.403 | 3.01 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.927 | 0.927 | 1.949 | 3.05 | 0.304 | 0.000 | 0.217 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.717 | 2.86 | 0.274 | 0.000 | 0.177 |
| latent3 | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.924 | 0.924 | 1.734 | 2.67 | 0.286 | 0.000 | 0.180 |
| latent3 | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.902 | 0.902 | 1.610 | 2.66 | 0.287 | 0.000 | 0.180 |
| noise0.1 | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.893 | 0.893 | 1.844 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.942 | 0.942 | 2.664 | 3.47 | 0.452 | 0.000 | 0.337 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 2.152 | 3.26 | 0.420 | 0.000 | 0.290 |
| noise0.1 | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.904 | 0.904 | 2.159 | 3.18 | 0.388 | 0.000 | 0.290 |
| noise0.1 | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 2.061 | 3.21 | 0.396 | 0.000 | 0.290 |
| noise0.1 | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 1.269 | 1.89 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.925 | 0.925 | 1.598 | 2.44 | 0.286 | 0.000 | 0.229 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.397 | 2.24 | 0.265 | 0.000 | 0.218 |
| noise0.1 | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.914 | 0.914 | 1.471 | 2.27 | 0.275 | 0.000 | 0.228 |
| noise0.1 | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.888 | 0.888 | 1.347 | 2.31 | 0.293 | 0.000 | 0.228 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 |
|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | -0.01 [-0.05, +0.03] |
| latent1 | 80 | missing | 0.2 | -0.38 [-0.57, -0.19] |
| latent1 | 80 | reversed | 0.2 | -0.01 [-0.06, +0.04] |
| latent1 | 150 | none | 0.0 | -0.03 [-0.10, +0.02] |
| latent1 | 150 | missing | 0.2 | -0.23 [-0.37, -0.08] |
| latent1 | 150 | reversed | 0.2 | -0.01 [-0.07, +0.06] |
| latent3 | 80 | none | 0.0 | -0.02 [-0.05, +0.01] |
| latent3 | 80 | missing | 0.2 | -0.62 [-0.74, -0.49] |
| latent3 | 80 | reversed | 0.2 | -0.02 [-0.10, +0.05] |
| latent3 | 150 | none | 0.0 | -0.03 [-0.12, +0.06] |
| latent3 | 150 | missing | 0.2 | -0.18 [-0.29, -0.09] |
| latent3 | 150 | reversed | 0.2 | -0.01 [-0.08, +0.05] |
| noise0.1 | 80 | none | 0.0 | +0.00 [-0.07, +0.09] |
| noise0.1 | 80 | missing | 0.2 | -0.21 [-0.38, -0.01] |
| noise0.1 | 80 | reversed | 0.2 | +0.02 [-0.03, +0.07] |
| noise0.1 | 150 | none | 0.0 | +0.02 [-0.03, +0.06] |
| noise0.1 | 150 | missing | 0.2 | -0.20 [-0.31, -0.08] |
| noise0.1 | 150 | reversed | 0.2 | +0.05 [-0.01, +0.11] |
