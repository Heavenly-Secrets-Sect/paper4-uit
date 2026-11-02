# ext_r4leadlag_eval_latent

r4leadlag: latent1/latent3 (3 children each) x missing-0.2/0.5 x T 40/80/150, D-07 development, seeds of ext_v51_a1 (kinds [missing] keeps k_idx 1 and c_idx 1 for missing-0.2). Run through experiments/ext/r4leadlag/drive.py. Rule in docs/ext/r4leadlag.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | oracle | 60/60 | 0.891 | 0.891 | 1.598 | 2.67 | 0.304 | 0.000 | 0.115 |
| latent1 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | missing | 0.2 | oracle | 60/60 | 0.891 | 0.891 | 1.598 | 2.67 | 0.304 | 0.000 | 0.115 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.498 | 5.12 | 0.516 | 0.000 | 0.361 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.938 | 0.938 | 3.494 | 5.07 | 0.534 | 0.000 | 0.361 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.942 | 0.942 | 3.600 | 5.12 | 0.522 | 0.000 | 0.361 |
| latent1 | 40 | missing | 0.5 | oracle | 60/60 | 0.891 | 0.891 | 1.598 | 2.67 | 0.304 | 0.000 | 0.115 |
| latent1 | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 4.189 | 5.47 | 0.579 | 0.000 | 0.371 |
| latent1 | 40 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.948 | 0.948 | 4.154 | 5.55 | 0.566 | 0.000 | 0.371 |
| latent1 | 40 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.955 | 0.955 | 4.223 | 5.56 | 0.621 | 0.000 | 0.378 |
| latent1 | 80 | none | 0.0 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | missing | 0.2 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 2.418 | 3.15 | 0.364 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.946 | 0.946 | 2.344 | 3.13 | 0.361 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.942 | 0.942 | 2.283 | 3.18 | 0.355 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.5 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.958 | 0.958 | 2.720 | 3.47 | 0.395 | 0.000 | 0.229 |
| latent1 | 80 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.949 | 0.949 | 2.565 | 3.48 | 0.393 | 0.000 | 0.229 |
| latent1 | 80 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.946 | 0.946 | 2.521 | 3.56 | 0.392 | 0.000 | 0.230 |
| latent1 | 150 | none | 0.0 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | missing | 0.2 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.956 | 0.956 | 1.534 | 2.15 | 0.233 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.961 | 0.961 | 1.603 | 2.17 | 0.235 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.965 | 0.965 | 1.651 | 2.20 | 0.241 | 0.000 | 0.188 |
| latent1 | 150 | missing | 0.5 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| latent1 | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.957 | 0.957 | 1.686 | 2.38 | 0.258 | 0.000 | 0.183 |
| latent1 | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.961 | 0.961 | 1.727 | 2.41 | 0.256 | 0.000 | 0.183 |
| latent1 | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.965 | 0.965 | 1.759 | 2.45 | 0.270 | 0.000 | 0.202 |
| latent3 | 40 | none | 0.0 | oracle | 60/60 | 0.895 | 0.895 | 1.633 | 2.81 | 0.330 | 0.000 | 0.145 |
| latent3 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | missing | 0.2 | oracle | 60/60 | 0.895 | 0.895 | 1.633 | 2.81 | 0.330 | 0.000 | 0.145 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.930 | 0.930 | 3.707 | 5.24 | 0.569 | 0.000 | 0.365 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.929 | 0.929 | 3.622 | 5.23 | 0.579 | 0.000 | 0.365 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.940 | 0.940 | 3.704 | 5.33 | 0.589 | 0.000 | 0.365 |
| latent3 | 40 | missing | 0.5 | oracle | 60/60 | 0.895 | 0.895 | 1.633 | 2.81 | 0.330 | 0.000 | 0.145 |
| latent3 | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 4.306 | 5.50 | 0.613 | 0.000 | 0.395 |
| latent3 | 40 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.951 | 0.951 | 4.277 | 5.59 | 0.587 | 0.000 | 0.418 |
| latent3 | 40 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.957 | 0.957 | 4.419 | 5.60 | 0.641 | 0.000 | 0.388 |
| latent3 | 80 | none | 0.0 | oracle | 60/60 | 0.879 | 0.879 | 1.120 | 2.39 | 0.219 | 0.000 | 0.114 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | missing | 0.2 | oracle | 60/60 | 0.879 | 0.879 | 1.120 | 2.39 | 0.219 | 0.000 | 0.114 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.961 | 0.961 | 2.531 | 3.21 | 0.372 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.955 | 0.955 | 2.461 | 3.16 | 0.371 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.953 | 0.953 | 2.486 | 3.16 | 0.374 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.5 | oracle | 60/60 | 0.879 | 0.879 | 1.120 | 2.39 | 0.219 | 0.000 | 0.114 |
| latent3 | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 2.782 | 3.59 | 0.396 | 0.000 | 0.251 |
| latent3 | 80 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.962 | 0.962 | 2.657 | 3.54 | 0.402 | 0.000 | 0.249 |
| latent3 | 80 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.955 | 0.955 | 2.606 | 3.50 | 0.403 | 0.000 | 0.251 |
| latent3 | 150 | none | 0.0 | oracle | 60/60 | 0.779 | 0.779 | 0.837 | 3.23 | 0.215 | 0.000 | 0.106 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | missing | 0.2 | oracle | 60/60 | 0.779 | 0.779 | 0.837 | 3.23 | 0.215 | 0.000 | 0.106 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.717 | 2.86 | 0.274 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.927 | 0.927 | 1.808 | 2.82 | 0.273 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.936 | 0.936 | 1.828 | 2.79 | 0.275 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.5 | oracle | 60/60 | 0.779 | 0.779 | 0.837 | 3.23 | 0.215 | 0.000 | 0.106 |
| latent3 | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.935 | 0.935 | 1.872 | 2.87 | 0.302 | 0.000 | 0.213 |
| latent3 | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.942 | 0.942 | 1.901 | 2.87 | 0.297 | 0.000 | 0.211 |
| latent3 | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.945 | 0.945 | 1.995 | 2.83 | 0.302 | 0.000 | 0.208 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v5_1_leadlag | tolerant_v5_1_leadlag_skel |
|---|---|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | -1.83 [-2.43, -1.41] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent1 | 40 | missing | 0.2 | -2.45 [-3.01, -1.95] | -0.05 [-0.12, +0.03] | +0.00 [-0.07, +0.08] |
| latent1 | 40 | missing | 0.5 | -2.80 [-3.34, -2.32] | +0.07 [-0.01, +0.16] | +0.08 [-0.02, +0.18] |
| latent1 | 80 | none | 0.0 | -0.78 [-1.11, -0.46] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent1 | 80 | missing | 0.2 | -1.13 [-1.41, -0.76] | -0.02 [-0.06, +0.02] | +0.03 [-0.02, +0.08] |
| latent1 | 80 | missing | 0.5 | -1.44 [-1.69, -1.12] | +0.01 [-0.05, +0.08] | +0.10 [-0.02, +0.26] |
| latent1 | 150 | none | 0.0 | -0.28 [-0.44, -0.10] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent1 | 150 | missing | 0.2 | -0.42 [-0.60, -0.20] | +0.02 [+0.00, +0.03] | +0.04 [+0.01, +0.08] |
| latent1 | 150 | missing | 0.5 | -0.65 [-0.88, -0.41] | +0.03 [-0.00, +0.06] | +0.07 [+0.03, +0.11] |
| latent3 | 40 | none | 0.0 | -1.96 [-2.64, -1.39] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent3 | 40 | missing | 0.2 | -2.43 [-2.96, -1.98] | -0.01 [-0.06, +0.05] | +0.09 [+0.01, +0.20] |
| latent3 | 40 | missing | 0.5 | -2.69 [-3.15, -2.28] | +0.10 [+0.01, +0.18] | +0.11 [+0.00, +0.20] |
| latent3 | 80 | none | 0.0 | -0.37 [-0.55, -0.17] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent3 | 80 | missing | 0.2 | -0.82 [-1.08, -0.54] | -0.05 [-0.07, -0.02] | -0.05 [-0.11, +0.03] |
| latent3 | 80 | missing | 0.5 | -1.20 [-1.45, -0.96] | -0.05 [-0.10, -0.00] | -0.10 [-0.20, -0.00] |
| latent3 | 150 | none | 0.0 | +0.26 [-0.35, +0.91] | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| latent3 | 150 | missing | 0.2 | +0.37 [-0.22, +1.05] | -0.04 [-0.07, -0.02] | -0.08 [-0.13, -0.03] |
| latent3 | 150 | missing | 0.5 | +0.36 [-0.28, +1.15] | +0.00 [-0.04, +0.05] | -0.04 [-0.11, +0.02] |
