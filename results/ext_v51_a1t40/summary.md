# ext_v51_a1t40

v51 (R2-2c, T = 40 part): tolerant_v5_1 and tolerant_v5 against frozen tolerant_v4 under one/three hidden common causes and 10% measurement noise (a1 scenarios), D-07 development, a1_latent_noise seeds. Calibration on clean D-07H development with the a3_ges calibration block. Rule in docs/ext/v51.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 3.117 | 4.52 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | none | 0.0 | tolerant_v5 | 60/60 | 0.924 | 0.924 | 3.012 | 4.47 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.977 | 0.977 | 7.071 | 8.58 | 0.917 | 0.000 | 0.507 |
| latent1 | 40 | missing | 0.2 | tolerant_v5 | 60/60 | 0.937 | 0.937 | 3.783 | 5.30 | 0.550 | 0.000 | 0.364 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.498 | 5.12 | 0.516 | 0.000 | 0.361 |
| latent1 | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.937 | 0.937 | 3.259 | 4.72 | 0.535 | 0.000 | 0.331 |
| latent1 | 40 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.928 | 0.928 | 3.196 | 4.72 | 0.521 | 0.000 | 0.331 |
| latent1 | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.930 | 0.930 | 3.339 | 4.71 | 0.498 | 0.000 | 0.331 |
| latent3 | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.929 | 0.929 | 3.188 | 4.64 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | none | 0.0 | tolerant_v5 | 60/60 | 0.923 | 0.923 | 2.981 | 4.66 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.975 | 0.975 | 7.083 | 8.43 | 0.931 | 0.000 | 0.542 |
| latent3 | 40 | missing | 0.2 | tolerant_v5 | 60/60 | 0.942 | 0.942 | 3.874 | 5.33 | 0.566 | 0.000 | 0.368 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.930 | 0.930 | 3.707 | 5.24 | 0.569 | 0.000 | 0.365 |
| latent3 | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 3.414 | 4.87 | 0.510 | 0.000 | 0.354 |
| latent3 | 40 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.933 | 0.933 | 3.235 | 4.90 | 0.511 | 0.000 | 0.354 |
| latent3 | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.931 | 0.931 | 3.262 | 4.92 | 0.513 | 0.000 | 0.354 |
| noise0.1 | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.909 | 0.909 | 3.048 | 4.85 | 0.471 | 0.000 | 0.402 |
| noise0.1 | 40 | none | 0.0 | tolerant_v5 | 60/60 | 0.909 | 0.909 | 2.877 | 4.73 | 0.471 | 0.000 | 0.402 |
| noise0.1 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 2.787 | 4.82 | 0.471 | 0.000 | 0.402 |
| noise0.1 | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.978 | 0.978 | 6.832 | 8.00 | 0.867 | 0.000 | 0.539 |
| noise0.1 | 40 | missing | 0.2 | tolerant_v5 | 60/60 | 0.909 | 0.909 | 3.480 | 5.40 | 0.585 | 0.000 | 0.421 |
| noise0.1 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.900 | 0.900 | 3.259 | 5.32 | 0.560 | 0.000 | 0.424 |
| noise0.1 | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.910 | 0.910 | 3.136 | 5.01 | 0.531 | 0.000 | 0.402 |
| noise0.1 | 40 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.907 | 0.907 | 3.064 | 4.95 | 0.534 | 0.000 | 0.402 |
| noise0.1 | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.909 | 0.909 | 3.117 | 5.00 | 0.544 | 0.000 | 0.402 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5 | tolerant_v5_1 |
|---|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | -0.05 [-0.12, +0.02] | -0.02 [-0.12, +0.07] |
| latent1 | 40 | missing | 0.2 | -3.27 [-3.70, -2.73] | -3.46 [-4.00, -2.84] |
| latent1 | 40 | reversed | 0.2 | -0.00 [-0.13, +0.14] | -0.01 [-0.09, +0.06] |
| latent3 | 40 | none | 0.0 | +0.02 [-0.10, +0.14] | +0.13 [+0.02, +0.24] |
| latent3 | 40 | missing | 0.2 | -3.11 [-3.75, -2.51] | -3.19 [-3.83, -2.58] |
| latent3 | 40 | reversed | 0.2 | +0.03 [-0.07, +0.15] | +0.05 [-0.03, +0.15] |
| noise0.1 | 40 | none | 0.0 | -0.12 [-0.22, -0.02] | -0.03 [-0.15, +0.10] |
| noise0.1 | 40 | missing | 0.2 | -2.60 [-3.40, -1.73] | -2.69 [-3.33, -1.86] |
| noise0.1 | 40 | reversed | 0.2 | -0.06 [-0.14, +0.03] | -0.00 [-0.15, +0.15] |
