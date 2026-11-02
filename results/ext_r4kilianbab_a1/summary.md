# ext_r4kilianbab_a1

r4kilianbab secondary (descriptive no-harm): latent1 and noise0.1 scenarios, T 80/150, cells none / missing-0.2 / reversed-0.2 (cell list of ext_v51_a1 so v5_1 rows pair), D-07 development, seed_base 20261102. Width factors of K1/KBC from results/ext_r4kilianbab_eval/calibration.json (no re-tuning).

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | r4kilianbab_bab | 60/60 | 0.895 | 0.895 | 1.889 | 3.16 | 0.376 | 0.000 | 0.210 |
| latent1 | 80 | none | 0.0 | r4kilianbab_babbc | 60/60 | 0.896 | 0.896 | 1.762 | 3.03 | 0.376 | 0.000 | 0.210 |
| latent1 | 80 | none | 0.0 | r4kilianbab_babraw | 60/60 | 0.864 | 0.864 | 1.718 | 3.39 | 0.376 | 0.000 | 0.210 |
| latent1 | 80 | none | 0.0 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 2.418 | 3.15 | 0.364 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.2 | r4kilianbab_bab | 60/60 | 0.940 | 0.940 | 2.481 | 3.39 | 0.402 | 0.000 | 0.221 |
| latent1 | 80 | missing | 0.2 | r4kilianbab_babbc | 60/60 | 0.937 | 0.937 | 2.429 | 3.43 | 0.402 | 0.000 | 0.221 |
| latent1 | 80 | missing | 0.2 | r4kilianbab_babraw | 60/60 | 0.920 | 0.920 | 2.256 | 3.46 | 0.402 | 0.000 | 0.221 |
| latent1 | 80 | missing | 0.2 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.940 | 0.940 | 2.118 | 3.01 | 0.352 | 0.000 | 0.243 |
| latent1 | 80 | reversed | 0.2 | r4kilianbab_bab | 60/60 | 0.926 | 0.926 | 2.106 | 3.31 | 0.375 | 0.000 | 0.237 |
| latent1 | 80 | reversed | 0.2 | r4kilianbab_babbc | 60/60 | 0.951 | 0.951 | 2.357 | 3.23 | 0.375 | 0.000 | 0.237 |
| latent1 | 80 | reversed | 0.2 | r4kilianbab_babraw | 60/60 | 0.886 | 0.886 | 1.831 | 3.47 | 0.375 | 0.000 | 0.237 |
| latent1 | 80 | reversed | 0.2 | oracle | 60/60 | 0.892 | 0.892 | 1.058 | 2.03 | 0.191 | 0.000 | 0.089 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | r4kilianbab_bab | 60/60 | 0.900 | 0.900 | 1.407 | 2.52 | 0.260 | 0.000 | 0.175 |
| latent1 | 150 | none | 0.0 | r4kilianbab_babbc | 60/60 | 0.875 | 0.875 | 1.273 | 2.57 | 0.260 | 0.000 | 0.175 |
| latent1 | 150 | none | 0.0 | r4kilianbab_babraw | 60/60 | 0.861 | 0.861 | 1.224 | 2.78 | 0.260 | 0.000 | 0.175 |
| latent1 | 150 | none | 0.0 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.956 | 0.956 | 1.534 | 2.15 | 0.233 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | r4kilianbab_bab | 60/60 | 0.937 | 0.937 | 1.647 | 2.71 | 0.286 | 0.000 | 0.184 |
| latent1 | 150 | missing | 0.2 | r4kilianbab_babbc | 60/60 | 0.952 | 0.952 | 1.772 | 2.51 | 0.286 | 0.000 | 0.184 |
| latent1 | 150 | missing | 0.2 | r4kilianbab_babraw | 60/60 | 0.909 | 0.909 | 1.497 | 2.80 | 0.286 | 0.000 | 0.184 |
| latent1 | 150 | missing | 0.2 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| latent1 | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.936 | 0.936 | 1.495 | 2.19 | 0.249 | 0.000 | 0.177 |
| latent1 | 150 | reversed | 0.2 | r4kilianbab_bab | 60/60 | 0.917 | 0.917 | 1.658 | 2.53 | 0.267 | 0.000 | 0.169 |
| latent1 | 150 | reversed | 0.2 | r4kilianbab_babbc | 60/60 | 0.947 | 0.947 | 1.808 | 2.52 | 0.267 | 0.000 | 0.169 |
| latent1 | 150 | reversed | 0.2 | r4kilianbab_babraw | 60/60 | 0.886 | 0.886 | 1.442 | 2.68 | 0.267 | 0.000 | 0.169 |
| latent1 | 150 | reversed | 0.2 | oracle | 60/60 | 0.881 | 0.881 | 0.788 | 1.74 | 0.144 | 0.000 | 0.076 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | none | 0.0 | r4kilianbab_bab | 60/60 | 0.882 | 0.882 | 1.860 | 3.02 | 0.336 | 0.000 | 0.249 |
| noise0.1 | 80 | none | 0.0 | r4kilianbab_babbc | 60/60 | 0.895 | 0.895 | 1.739 | 2.75 | 0.336 | 0.000 | 0.249 |
| noise0.1 | 80 | none | 0.0 | r4kilianbab_babraw | 60/60 | 0.855 | 0.855 | 1.691 | 3.20 | 0.336 | 0.000 | 0.249 |
| noise0.1 | 80 | none | 0.0 | oracle | 60/60 | 0.766 | 0.766 | 1.059 | 2.97 | 0.270 | 0.000 | 0.098 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 2.152 | 3.26 | 0.420 | 0.000 | 0.290 |
| noise0.1 | 80 | missing | 0.2 | r4kilianbab_bab | 60/60 | 0.915 | 0.915 | 2.147 | 3.23 | 0.388 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | r4kilianbab_babbc | 60/60 | 0.915 | 0.915 | 2.105 | 3.26 | 0.388 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | r4kilianbab_babraw | 60/60 | 0.894 | 0.894 | 1.952 | 3.35 | 0.388 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | oracle | 60/60 | 0.766 | 0.766 | 1.059 | 2.97 | 0.270 | 0.000 | 0.098 |
| noise0.1 | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 2.061 | 3.21 | 0.396 | 0.000 | 0.290 |
| noise0.1 | 80 | reversed | 0.2 | r4kilianbab_bab | 60/60 | 0.891 | 0.891 | 2.020 | 3.19 | 0.366 | 0.000 | 0.261 |
| noise0.1 | 80 | reversed | 0.2 | r4kilianbab_babbc | 60/60 | 0.931 | 0.931 | 2.260 | 3.06 | 0.366 | 0.000 | 0.261 |
| noise0.1 | 80 | reversed | 0.2 | r4kilianbab_babraw | 60/60 | 0.854 | 0.854 | 1.757 | 3.40 | 0.366 | 0.000 | 0.261 |
| noise0.1 | 80 | reversed | 0.2 | oracle | 60/60 | 0.766 | 0.766 | 1.059 | 2.97 | 0.270 | 0.000 | 0.098 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | none | 0.0 | r4kilianbab_bab | 60/60 | 0.932 | 0.932 | 1.317 | 1.85 | 0.217 | 0.000 | 0.183 |
| noise0.1 | 150 | none | 0.0 | r4kilianbab_babbc | 60/60 | 0.923 | 0.923 | 1.185 | 1.71 | 0.217 | 0.000 | 0.183 |
| noise0.1 | 150 | none | 0.0 | r4kilianbab_babraw | 60/60 | 0.893 | 0.893 | 1.145 | 1.94 | 0.217 | 0.000 | 0.183 |
| noise0.1 | 150 | none | 0.0 | oracle | 60/60 | 0.755 | 0.755 | 0.780 | 2.31 | 0.192 | 0.000 | 0.069 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.397 | 2.24 | 0.265 | 0.000 | 0.218 |
| noise0.1 | 150 | missing | 0.2 | r4kilianbab_bab | 60/60 | 0.936 | 0.936 | 1.478 | 2.10 | 0.256 | 0.000 | 0.193 |
| noise0.1 | 150 | missing | 0.2 | r4kilianbab_babbc | 60/60 | 0.947 | 0.947 | 1.599 | 2.23 | 0.256 | 0.000 | 0.193 |
| noise0.1 | 150 | missing | 0.2 | r4kilianbab_babraw | 60/60 | 0.917 | 0.917 | 1.344 | 2.16 | 0.256 | 0.000 | 0.193 |
| noise0.1 | 150 | missing | 0.2 | oracle | 60/60 | 0.755 | 0.755 | 0.780 | 2.31 | 0.192 | 0.000 | 0.069 |
| noise0.1 | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.888 | 0.888 | 1.347 | 2.31 | 0.293 | 0.000 | 0.228 |
| noise0.1 | 150 | reversed | 0.2 | r4kilianbab_bab | 60/60 | 0.907 | 0.907 | 1.429 | 2.24 | 0.265 | 0.000 | 0.201 |
| noise0.1 | 150 | reversed | 0.2 | r4kilianbab_babbc | 60/60 | 0.934 | 0.934 | 1.652 | 2.26 | 0.265 | 0.000 | 0.201 |
| noise0.1 | 150 | reversed | 0.2 | r4kilianbab_babraw | 60/60 | 0.859 | 0.859 | 1.242 | 2.43 | 0.265 | 0.000 | 0.201 |
| noise0.1 | 150 | reversed | 0.2 | oracle | 60/60 | 0.755 | 0.755 | 0.780 | 2.31 | 0.192 | 0.000 | 0.069 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | r4kilianbab_bab | r4kilianbab_babbc | r4kilianbab_babraw | oracle |
|---|---|---|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | +0.35 [+0.05, +0.64] | +0.21 [-0.06, +0.47] | +0.58 [+0.18, +0.93] | -0.78 [-1.08, -0.43] |
| latent1 | 80 | missing | 0.2 | +0.23 [+0.09, +0.40] | +0.28 [+0.15, +0.42] | +0.30 [+0.12, +0.51] | -1.13 [-1.39, -0.79] |
| latent1 | 80 | reversed | 0.2 | +0.29 [+0.13, +0.45] | +0.21 [+0.08, +0.34] | +0.45 [+0.24, +0.69] | -0.98 [-1.26, -0.66] |
| latent1 | 150 | none | 0.0 | +0.51 [+0.33, +0.73] | +0.56 [+0.35, +0.81] | +0.77 [+0.53, +1.07] | -0.28 [-0.43, -0.09] |
| latent1 | 150 | missing | 0.2 | +0.55 [+0.30, +0.86] | +0.36 [+0.24, +0.50] | +0.65 [+0.34, +1.04] | -0.42 [-0.62, -0.21] |
| latent1 | 150 | reversed | 0.2 | +0.34 [+0.20, +0.49] | +0.33 [+0.23, +0.43] | +0.49 [+0.33, +0.67] | -0.45 [-0.65, -0.24] |
| noise0.1 | 80 | none | 0.0 | +0.06 [-0.09, +0.23] | -0.20 [-0.35, -0.05] | +0.25 [+0.08, +0.42] | +0.02 [-0.23, +0.25] |
| noise0.1 | 80 | missing | 0.2 | -0.03 [-0.12, +0.06] | -0.00 [-0.10, +0.10] | +0.09 [-0.04, +0.22] | -0.29 [-0.56, -0.03] |
| noise0.1 | 80 | reversed | 0.2 | -0.01 [-0.14, +0.13] | -0.15 [-0.29, +0.00] | +0.19 [+0.03, +0.37] | -0.24 [-0.47, -0.02] |
| noise0.1 | 150 | none | 0.0 | -0.05 [-0.20, +0.06] | -0.20 [-0.28, -0.11] | +0.03 [-0.11, +0.15] | +0.41 [+0.13, +0.75] |
| noise0.1 | 150 | missing | 0.2 | -0.14 [-0.26, -0.03] | -0.01 [-0.15, +0.13] | -0.08 [-0.18, +0.02] | +0.07 [-0.19, +0.36] |
| noise0.1 | 150 | reversed | 0.2 | -0.07 [-0.20, +0.05] | -0.06 [-0.20, +0.11] | +0.11 [-0.02, +0.25] | -0.00 [-0.23, +0.24] |
