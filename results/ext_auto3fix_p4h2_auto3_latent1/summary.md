# ext_auto3fix_p4h2_auto3_latent1

FROZEN, NOT RUN. Confirmatory latent1 robustness of tolerant_auto3 on the sealed P4-H2 confirmatory split, corrected spec of round 3 (docs/ext/auto3fix.md, ID auto3fix). Identical to experiments/configs/ext_auto5_p4h2_auto3_latent1.json except name and purpose. Only the latent1 rows are ruled (L1).

Bank P4-H2 / confirmatory; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | oracle | 60/60 | 0.909 | 0.909 | 1.044 | 1.73 | 0.183 | 0.000 | 0.086 |
| clean | 80 | none | 0.0 | plugin | 60/60 | 0.876 | 0.876 | 1.397 | 2.63 | 0.267 | 0.000 | 0.228 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.949 | 0.949 | 1.852 | 2.38 | 0.267 | 0.000 | 0.228 |
| clean | 80 | none | 0.0 | tolerant_auto3 | 60/60 | 0.963 | 0.963 | 2.028 | 2.57 | 0.278 | 0.000 | 0.243 |
| clean | 80 | missing | 0.2 | oracle | 60/60 | 0.909 | 0.909 | 1.044 | 1.73 | 0.183 | 0.000 | 0.086 |
| clean | 80 | missing | 0.2 | plugin | 60/60 | 0.676 | 0.697 | 1.261 | 10.83 | 0.405 | 0.030 | 0.266 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.976 | 0.976 | 2.720 | 3.08 | 0.387 | 0.000 | 0.296 |
| clean | 80 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.965 | 0.966 | 2.627 | 3.29 | 0.408 | 0.001 | 0.307 |
| clean | 80 | reversed | 0.2 | oracle | 60/60 | 0.909 | 0.909 | 1.044 | 1.73 | 0.183 | 0.000 | 0.086 |
| clean | 80 | reversed | 0.2 | plugin | 60/60 | 0.831 | 0.831 | 1.398 | 3.64 | 0.292 | 0.000 | 0.255 |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 2.141 | 2.71 | 0.299 | 0.000 | 0.255 |
| clean | 80 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.948 | 0.948 | 2.022 | 2.79 | 0.340 | 0.000 | 0.280 |
| clean | 150 | none | 0.0 | oracle | 60/60 | 0.932 | 0.932 | 0.770 | 1.13 | 0.130 | 0.000 | 0.053 |
| clean | 150 | none | 0.0 | plugin | 60/60 | 0.915 | 0.915 | 1.070 | 1.61 | 0.188 | 0.000 | 0.173 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 1.291 | 1.56 | 0.188 | 0.000 | 0.173 |
| clean | 150 | none | 0.0 | tolerant_auto3 | 60/60 | 0.977 | 0.977 | 1.628 | 1.87 | 0.191 | 0.000 | 0.171 |
| clean | 150 | missing | 0.2 | oracle | 60/60 | 0.932 | 0.932 | 0.770 | 1.13 | 0.130 | 0.000 | 0.053 |
| clean | 150 | missing | 0.2 | plugin | 60/60 | 0.671 | 0.692 | 0.970 | 10.66 | 0.280 | 0.030 | 0.212 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.961 | 0.961 | 1.690 | 2.01 | 0.269 | 0.000 | 0.205 |
| clean | 150 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.984 | 0.984 | 2.043 | 2.24 | 0.277 | 0.000 | 0.209 |
| clean | 150 | reversed | 0.2 | oracle | 60/60 | 0.932 | 0.932 | 0.770 | 1.13 | 0.130 | 0.000 | 0.053 |
| clean | 150 | reversed | 0.2 | plugin | 60/60 | 0.840 | 0.840 | 1.034 | 3.00 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.961 | 0.961 | 1.517 | 1.93 | 0.224 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.979 | 0.979 | 1.800 | 2.04 | 0.238 | 0.000 | 0.198 |
| latent1 | 80 | none | 0.0 | oracle | 60/60 | 0.908 | 0.908 | 1.085 | 1.87 | 0.184 | 0.000 | 0.082 |
| latent1 | 80 | none | 0.0 | plugin | 60/60 | 0.869 | 0.869 | 1.457 | 2.92 | 0.285 | 0.000 | 0.217 |
| latent1 | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.947 | 0.947 | 1.874 | 2.65 | 0.285 | 0.000 | 0.217 |
| latent1 | 80 | none | 0.0 | tolerant_auto3 | 60/60 | 0.956 | 0.956 | 2.263 | 2.90 | 0.326 | 0.000 | 0.237 |
| latent1 | 80 | missing | 0.2 | oracle | 60/60 | 0.908 | 0.908 | 1.085 | 1.87 | 0.184 | 0.000 | 0.082 |
| latent1 | 80 | missing | 0.2 | plugin | 60/60 | 0.670 | 0.691 | 1.376 | 10.82 | 0.404 | 0.030 | 0.242 |
| latent1 | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 2.863 | 3.41 | 0.416 | 0.000 | 0.273 |
| latent1 | 80 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.956 | 0.956 | 2.724 | 3.46 | 0.420 | 0.000 | 0.280 |
| latent1 | 80 | reversed | 0.2 | oracle | 60/60 | 0.908 | 0.908 | 1.085 | 1.87 | 0.184 | 0.000 | 0.082 |
| latent1 | 80 | reversed | 0.2 | plugin | 60/60 | 0.825 | 0.825 | 1.413 | 3.73 | 0.304 | 0.000 | 0.237 |
| latent1 | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.958 | 0.958 | 2.191 | 2.84 | 0.317 | 0.000 | 0.237 |
| latent1 | 80 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.945 | 0.945 | 2.335 | 3.09 | 0.362 | 0.000 | 0.271 |
| latent1 | 150 | none | 0.0 | oracle | 60/60 | 0.883 | 0.883 | 0.770 | 1.55 | 0.146 | 0.000 | 0.077 |
| latent1 | 150 | none | 0.0 | plugin | 60/60 | 0.882 | 0.882 | 1.084 | 2.15 | 0.210 | 0.000 | 0.172 |
| latent1 | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.930 | 0.930 | 1.302 | 1.96 | 0.210 | 0.000 | 0.172 |
| latent1 | 150 | none | 0.0 | tolerant_auto3 | 60/60 | 0.971 | 0.971 | 1.851 | 2.28 | 0.256 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | oracle | 60/60 | 0.883 | 0.883 | 0.770 | 1.55 | 0.146 | 0.000 | 0.077 |
| latent1 | 150 | missing | 0.2 | plugin | 60/60 | 0.643 | 0.663 | 1.003 | 11.06 | 0.345 | 0.030 | 0.169 |
| latent1 | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.952 | 0.952 | 1.726 | 2.34 | 0.280 | 0.000 | 0.193 |
| latent1 | 150 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.975 | 0.975 | 2.092 | 2.48 | 0.300 | 0.000 | 0.208 |
| latent1 | 150 | reversed | 0.2 | oracle | 60/60 | 0.883 | 0.883 | 0.770 | 1.55 | 0.146 | 0.000 | 0.077 |
| latent1 | 150 | reversed | 0.2 | plugin | 60/60 | 0.799 | 0.799 | 1.052 | 3.59 | 0.243 | 0.000 | 0.187 |
| latent1 | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.950 | 0.950 | 1.570 | 2.09 | 0.250 | 0.000 | 0.187 |
| latent1 | 150 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.966 | 0.966 | 1.939 | 2.40 | 0.286 | 0.000 | 0.196 |

## Interval score difference vs `plugin` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | tolerant_v4 | tolerant_auto3 |
|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | -0.89 [-1.15, -0.64] | -0.25 [-0.44, -0.07] | -0.06 [-0.26, +0.14] |
| clean | 80 | missing | 0.2 | -9.10 [-9.86, -8.34] | -7.76 [-8.47, -7.00] | -7.54 [-8.32, -6.73] |
| clean | 80 | reversed | 0.2 | -1.90 [-2.45, -1.44] | -0.93 [-1.42, -0.51] | -0.85 [-1.35, -0.44] |
| clean | 150 | none | 0.0 | -0.48 [-0.60, -0.37] | -0.05 [-0.15, +0.03] | +0.26 [+0.11, +0.39] |
| clean | 150 | missing | 0.2 | -9.54 [-10.28, -8.87] | -8.65 [-9.29, -7.98] | -8.43 [-9.11, -7.77] |
| clean | 150 | reversed | 0.2 | -1.87 [-2.21, -1.58] | -1.07 [-1.35, -0.81] | -0.96 [-1.30, -0.64] |
| latent1 | 80 | none | 0.0 | -1.05 [-1.25, -0.87] | -0.27 [-0.43, -0.11] | -0.02 [-0.31, +0.27] |
| latent1 | 80 | missing | 0.2 | -8.95 [-9.74, -8.19] | -7.41 [-8.11, -6.71] | -7.36 [-8.14, -6.63] |
| latent1 | 80 | reversed | 0.2 | -1.87 [-2.23, -1.53] | -0.90 [-1.22, -0.55] | -0.65 [-1.02, -0.30] |
| latent1 | 150 | none | 0.0 | -0.60 [-0.78, -0.43] | -0.19 [-0.28, -0.12] | +0.13 [-0.06, +0.33] |
| latent1 | 150 | missing | 0.2 | -9.51 [-10.30, -8.71] | -8.72 [-9.55, -7.94] | -8.58 [-9.37, -7.82] |
| latent1 | 150 | reversed | 0.2 | -2.04 [-2.49, -1.67] | -1.50 [-1.96, -1.16] | -1.19 [-1.53, -0.85] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | oracle | plugin | tolerant_auto3 |
|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | -0.65 [-0.81, -0.48] | +0.25 [+0.07, +0.44] | +0.19 [+0.11, +0.27] |
| clean | 80 | missing | 0.2 | -1.34 [-1.52, -1.16] | +7.76 [+7.00, +8.47] | +0.22 [-0.00, +0.52] |
| clean | 80 | reversed | 0.2 | -0.98 [-1.15, -0.81] | +0.93 [+0.51, +1.42] | +0.08 [-0.03, +0.19] |
| clean | 150 | none | 0.0 | -0.43 [-0.53, -0.31] | +0.05 [-0.03, +0.15] | +0.31 [+0.23, +0.38] |
| clean | 150 | missing | 0.2 | -0.88 [-1.05, -0.69] | +8.65 [+7.98, +9.29] | +0.23 [+0.14, +0.33] |
| clean | 150 | reversed | 0.2 | -0.80 [-0.94, -0.64] | +1.07 [+0.81, +1.35] | +0.11 [-0.00, +0.22] |
| latent1 | 80 | none | 0.0 | -0.78 [-0.90, -0.67] | +0.27 [+0.11, +0.43] | +0.25 [+0.09, +0.42] |
| latent1 | 80 | missing | 0.2 | -1.54 [-1.77, -1.30] | +7.41 [+6.71, +8.11] | +0.05 [-0.07, +0.21] |
| latent1 | 80 | reversed | 0.2 | -0.97 [-1.14, -0.80] | +0.90 [+0.55, +1.22] | +0.25 [+0.12, +0.38] |
| latent1 | 150 | none | 0.0 | -0.41 [-0.55, -0.25] | +0.19 [+0.12, +0.28] | +0.32 [+0.17, +0.50] |
| latent1 | 150 | missing | 0.2 | -0.79 [-0.98, -0.58] | +8.72 [+7.94, +9.55] | +0.14 [+0.02, +0.23] |
| latent1 | 150 | reversed | 0.2 | -0.54 [-0.64, -0.40] | +1.50 [+1.16, +1.96] | +0.31 [+0.18, +0.46] |
