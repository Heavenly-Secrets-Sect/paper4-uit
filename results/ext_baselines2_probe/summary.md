# ext_baselines2_probe

R2-1 design/timing probe on D-07H development (not evaluation): cost and raw coverage of pselect_union_v2 / bvar_minnesota_v2 next to round-1 versions and tolerant_v3. 4 topologies x 1 replicate.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v3 | 4/4 | 0.890 | 0.890 | 2.311 | 3.71 | 0.465 | 0.000 | 0.235 |
| clean | 40 | none | 0.0 | pselect_union | 4/4 | 0.868 | 0.891 | 4.044 | 6.72 | 1.050 | 0.529 | 0.661 |
| clean | 40 | none | 0.0 | pselect_union_v2 | 4/4 | 0.654 | 0.857 | 4.948 | 12.75 | 1.107 | 0.846 | 0.222 |
| clean | 40 | none | 0.0 | bvar_minnesota | 4/4 | 0.787 | 0.787 | 2.173 | 4.83 | 0.510 | 0.000 | 0.475 |
| clean | 40 | none | 0.0 | bvar_minnesota_v2 | 4/4 | 0.860 | 0.860 | 2.036 | 3.93 | 0.432 | 0.000 | 0.316 |
| clean | 40 | missing | 0.2 | tolerant_v3 | 4/4 | 0.971 | 0.971 | 7.038 | 8.25 | 0.839 | 0.000 | 0.532 |
| clean | 40 | missing | 0.2 | pselect_union | 4/4 | 0.831 | 0.873 | 3.780 | 7.45 | 1.053 | 0.537 | 0.572 |
| clean | 40 | missing | 0.2 | pselect_union_v2 | 4/4 | 0.640 | 0.773 | 4.527 | 14.68 | 1.113 | 0.838 | 0.550 |
| clean | 40 | missing | 0.2 | bvar_minnesota | 4/4 | 0.647 | 0.647 | 2.033 | 10.49 | 0.629 | 0.000 | 0.486 |
| clean | 40 | missing | 0.2 | bvar_minnesota_v2 | 4/4 | 0.728 | 0.728 | 2.005 | 8.18 | 0.584 | 0.000 | 0.365 |
| clean | 40 | missing | 0.5 | tolerant_v3 | 4/4 | 0.971 | 0.971 | 7.273 | 7.90 | 0.793 | 0.000 | 0.476 |
| clean | 40 | missing | 0.5 | pselect_union | 4/4 | 0.846 | 0.873 | 3.737 | 8.19 | 1.056 | 0.537 | 0.561 |
| clean | 40 | missing | 0.5 | pselect_union_v2 | 4/4 | 0.765 | 0.879 | 4.336 | 9.99 | 1.094 | 0.757 | 0.449 |
| clean | 40 | missing | 0.5 | bvar_minnesota | 4/4 | 0.441 | 0.441 | 1.289 | 18.19 | 0.859 | 0.000 | 0.633 |
| clean | 40 | missing | 0.5 | bvar_minnesota_v2 | 4/4 | 0.588 | 0.588 | 1.825 | 12.46 | 0.684 | 0.000 | 0.425 |
| clean | 40 | reversed | 0.2 | tolerant_v3 | 4/4 | 0.890 | 0.890 | 2.523 | 4.11 | 0.488 | 0.000 | 0.257 |
| clean | 40 | reversed | 0.2 | pselect_union | 4/4 | 0.868 | 0.877 | 3.868 | 7.45 | 1.050 | 0.522 | 0.661 |
| clean | 40 | reversed | 0.2 | pselect_union_v2 | 4/4 | 0.735 | 0.857 | 5.038 | 11.31 | 1.083 | 0.794 | 1.079 |
| clean | 40 | reversed | 0.2 | bvar_minnesota | 4/4 | 0.735 | 0.735 | 2.215 | 6.17 | 0.608 | 0.000 | 0.540 |
| clean | 40 | reversed | 0.2 | bvar_minnesota_v2 | 4/4 | 0.824 | 0.824 | 1.874 | 5.21 | 0.468 | 0.000 | 0.419 |
| clean | 40 | reversed | 0.5 | tolerant_v3 | 4/4 | 0.868 | 0.868 | 2.599 | 4.86 | 0.550 | 0.000 | 0.424 |
| clean | 40 | reversed | 0.5 | pselect_union | 4/4 | 0.875 | 0.954 | 3.844 | 7.09 | 1.050 | 0.522 | 0.661 |
| clean | 40 | reversed | 0.5 | pselect_union_v2 | 4/4 | 0.647 | 0.773 | 5.376 | 12.02 | 1.123 | 0.838 | 0.957 |
| clean | 40 | reversed | 0.5 | bvar_minnesota | 4/4 | 0.647 | 0.647 | 2.189 | 9.37 | 0.681 | 0.000 | 0.541 |
| clean | 40 | reversed | 0.5 | bvar_minnesota_v2 | 4/4 | 0.735 | 0.735 | 1.972 | 7.89 | 0.620 | 0.000 | 0.438 |
| clean | 80 | none | 0.0 | tolerant_v3 | 4/4 | 0.912 | 0.912 | 1.385 | 2.29 | 0.237 | 0.000 | 0.253 |
| clean | 80 | none | 0.0 | pselect_union | 4/4 | 0.926 | 0.926 | 2.649 | 3.70 | 0.503 | 0.000 | 0.282 |
| clean | 80 | none | 0.0 | pselect_union_v2 | 4/4 | 0.926 | 0.926 | 2.211 | 3.74 | 0.481 | 0.007 | 0.271 |
| clean | 80 | none | 0.0 | bvar_minnesota | 4/4 | 0.890 | 0.890 | 1.685 | 2.56 | 0.403 | 0.000 | 0.361 |
| clean | 80 | none | 0.0 | bvar_minnesota_v2 | 4/4 | 0.919 | 0.919 | 1.534 | 2.25 | 0.299 | 0.000 | 0.248 |
| clean | 80 | missing | 0.2 | tolerant_v3 | 4/4 | 0.897 | 0.897 | 2.259 | 3.30 | 0.396 | 0.000 | 0.331 |
| clean | 80 | missing | 0.2 | pselect_union | 4/4 | 0.934 | 0.934 | 2.750 | 4.11 | 0.478 | 0.000 | 0.348 |
| clean | 80 | missing | 0.2 | pselect_union_v2 | 4/4 | 0.934 | 0.933 | 2.406 | 3.75 | 0.577 | 0.007 | 0.241 |
| clean | 80 | missing | 0.2 | bvar_minnesota | 4/4 | 0.750 | 0.750 | 1.698 | 7.20 | 0.483 | 0.000 | 0.351 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2 | 4/4 | 0.772 | 0.772 | 1.611 | 6.02 | 0.421 | 0.000 | 0.281 |
| clean | 80 | missing | 0.5 | tolerant_v3 | 4/4 | 0.882 | 0.882 | 2.300 | 3.53 | 0.429 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | pselect_union | 4/4 | 0.890 | 0.890 | 2.664 | 4.99 | 0.566 | 0.000 | 0.356 |
| clean | 80 | missing | 0.5 | pselect_union_v2 | 4/4 | 0.912 | 0.911 | 2.495 | 4.65 | 0.540 | 0.007 | 0.233 |
| clean | 80 | missing | 0.5 | bvar_minnesota | 4/4 | 0.515 | 0.515 | 1.465 | 15.23 | 0.588 | 0.000 | 0.354 |
| clean | 80 | missing | 0.5 | bvar_minnesota_v2 | 4/4 | 0.662 | 0.662 | 1.459 | 10.16 | 0.512 | 0.000 | 0.263 |
| clean | 80 | reversed | 0.2 | tolerant_v3 | 4/4 | 0.912 | 0.912 | 1.635 | 2.49 | 0.354 | 0.000 | 0.219 |
| clean | 80 | reversed | 0.2 | pselect_union | 4/4 | 0.912 | 0.912 | 2.680 | 4.22 | 0.530 | 0.000 | 0.376 |
| clean | 80 | reversed | 0.2 | pselect_union_v2 | 4/4 | 0.875 | 0.874 | 2.602 | 4.80 | 0.528 | 0.007 | 0.290 |
| clean | 80 | reversed | 0.2 | bvar_minnesota | 4/4 | 0.853 | 0.853 | 1.773 | 4.36 | 0.476 | 0.000 | 0.364 |
| clean | 80 | reversed | 0.2 | bvar_minnesota_v2 | 4/4 | 0.860 | 0.860 | 1.573 | 3.75 | 0.348 | 0.000 | 0.268 |
| clean | 80 | reversed | 0.5 | tolerant_v3 | 4/4 | 0.868 | 0.868 | 1.702 | 2.95 | 0.373 | 0.000 | 0.279 |
| clean | 80 | reversed | 0.5 | pselect_union | 4/4 | 0.890 | 0.890 | 2.733 | 4.91 | 0.647 | 0.000 | 0.405 |
| clean | 80 | reversed | 0.5 | pselect_union_v2 | 4/4 | 0.838 | 0.844 | 2.474 | 6.82 | 0.704 | 0.007 | 0.416 |
| clean | 80 | reversed | 0.5 | bvar_minnesota | 4/4 | 0.750 | 0.750 | 1.629 | 6.88 | 0.520 | 0.000 | 0.362 |
| clean | 80 | reversed | 0.5 | bvar_minnesota_v2 | 4/4 | 0.765 | 0.765 | 1.538 | 5.61 | 0.443 | 0.000 | 0.301 |
| clean | 150 | none | 0.0 | tolerant_v3 | 4/4 | 0.949 | 0.949 | 1.089 | 1.88 | 0.148 | 0.000 | 0.191 |
| clean | 150 | none | 0.0 | pselect_union | 4/4 | 0.978 | 0.978 | 1.852 | 2.09 | 0.254 | 0.000 | 0.166 |
| clean | 150 | none | 0.0 | pselect_union_v2 | 4/4 | 0.978 | 0.978 | 1.628 | 1.86 | 0.168 | 0.000 | 0.190 |
| clean | 150 | none | 0.0 | bvar_minnesota | 4/4 | 0.919 | 0.919 | 1.420 | 1.77 | 0.223 | 0.000 | 0.230 |
| clean | 150 | none | 0.0 | bvar_minnesota_v2 | 4/4 | 0.941 | 0.941 | 1.213 | 1.54 | 0.202 | 0.000 | 0.182 |
| clean | 150 | missing | 0.2 | tolerant_v3 | 4/4 | 0.919 | 0.919 | 1.463 | 2.23 | 0.290 | 0.000 | 0.209 |
| clean | 150 | missing | 0.2 | pselect_union | 4/4 | 0.956 | 0.956 | 1.914 | 2.56 | 0.289 | 0.000 | 0.184 |
| clean | 150 | missing | 0.2 | pselect_union_v2 | 4/4 | 0.978 | 0.978 | 1.802 | 1.87 | 0.207 | 0.000 | 0.165 |
| clean | 150 | missing | 0.2 | bvar_minnesota | 4/4 | 0.801 | 0.801 | 1.282 | 6.27 | 0.297 | 0.000 | 0.236 |
| clean | 150 | missing | 0.2 | bvar_minnesota_v2 | 4/4 | 0.816 | 0.816 | 1.152 | 4.56 | 0.278 | 0.000 | 0.193 |
| clean | 150 | missing | 0.5 | tolerant_v3 | 4/4 | 0.941 | 0.941 | 1.576 | 1.99 | 0.338 | 0.000 | 0.178 |
| clean | 150 | missing | 0.5 | pselect_union | 4/4 | 0.904 | 0.904 | 1.874 | 4.03 | 0.309 | 0.000 | 0.186 |
| clean | 150 | missing | 0.5 | pselect_union_v2 | 4/4 | 0.985 | 0.985 | 1.845 | 2.15 | 0.269 | 0.000 | 0.139 |
| clean | 150 | missing | 0.5 | bvar_minnesota | 4/4 | 0.544 | 0.544 | 1.174 | 12.52 | 0.450 | 0.000 | 0.285 |
| clean | 150 | missing | 0.5 | bvar_minnesota_v2 | 4/4 | 0.676 | 0.676 | 1.158 | 7.52 | 0.343 | 0.000 | 0.213 |
| clean | 150 | reversed | 0.2 | tolerant_v3 | 4/4 | 0.934 | 0.934 | 1.278 | 1.71 | 0.198 | 0.000 | 0.208 |
| clean | 150 | reversed | 0.2 | pselect_union | 4/4 | 0.949 | 0.949 | 1.996 | 3.05 | 0.231 | 0.000 | 0.200 |
| clean | 150 | reversed | 0.2 | pselect_union_v2 | 4/4 | 0.912 | 0.912 | 1.718 | 3.22 | 0.265 | 0.000 | 0.192 |
| clean | 150 | reversed | 0.2 | bvar_minnesota | 4/4 | 0.890 | 0.890 | 1.468 | 3.04 | 0.238 | 0.000 | 0.239 |
| clean | 150 | reversed | 0.2 | bvar_minnesota_v2 | 4/4 | 0.882 | 0.882 | 1.228 | 2.67 | 0.187 | 0.000 | 0.176 |
| clean | 150 | reversed | 0.5 | tolerant_v3 | 4/4 | 0.846 | 0.846 | 1.385 | 2.77 | 0.243 | 0.000 | 0.188 |
| clean | 150 | reversed | 0.5 | pselect_union | 4/4 | 0.824 | 0.824 | 1.939 | 4.68 | 0.388 | 0.000 | 0.256 |
| clean | 150 | reversed | 0.5 | pselect_union_v2 | 4/4 | 0.794 | 0.794 | 1.821 | 4.48 | 0.420 | 0.000 | 0.228 |
| clean | 150 | reversed | 0.5 | bvar_minnesota | 4/4 | 0.699 | 0.699 | 1.367 | 6.31 | 0.398 | 0.000 | 0.290 |
| clean | 150 | reversed | 0.5 | bvar_minnesota_v2 | 4/4 | 0.691 | 0.691 | 1.247 | 6.24 | 0.341 | 0.000 | 0.225 |

## Interval score difference vs `tolerant_v3` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | pselect_union | pselect_union_v2 | bvar_minnesota | bvar_minnesota_v2 |
|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +3.01 [+0.67, +5.43] | +9.04 [+5.06, +13.02] | +1.11 [-0.08, +2.38] | +0.21 [-0.32, +0.70] |
| clean | 40 | missing | 0.2 | -0.79 [-3.34, +1.92] | +6.43 [+1.71, +9.78] | +2.24 [-0.58, +6.60] | -0.06 [-2.55, +4.46] |
| clean | 40 | missing | 0.5 | +0.29 [-1.63, +3.33] | +2.09 [-2.27, +8.32] | +10.28 [+4.63, +16.41] | +4.56 [+0.38, +11.22] |
| clean | 40 | reversed | 0.2 | +3.35 [+2.60, +4.12] | +7.21 [+4.90, +10.68] | +2.06 [+1.07, +3.09] | +1.11 [+0.48, +1.73] |
| clean | 40 | reversed | 0.5 | +2.22 [+1.03, +4.35] | +7.15 [+4.17, +9.59] | +4.51 [+3.18, +6.42] | +3.03 [+1.96, +4.40] |
| clean | 80 | none | 0.0 | +1.41 [+0.42, +2.45] | +1.45 [+1.14, +1.87] | +0.27 [-0.31, +1.09] | -0.04 [-0.43, +0.28] |
| clean | 80 | missing | 0.2 | +0.81 [-0.01, +1.62] | +0.44 [-0.05, +0.92] | +3.90 [+2.83, +5.04] | +2.72 [+1.82, +4.22] |
| clean | 80 | missing | 0.5 | +1.46 [+0.58, +2.57] | +1.12 [-0.10, +2.08] | +11.70 [+9.13, +14.90] | +6.62 [+2.86, +11.35] |
| clean | 80 | reversed | 0.2 | +1.73 [+1.31, +2.08] | +2.31 [+1.40, +3.67] | +1.87 [+1.45, +2.45] | +1.26 [+1.03, +1.46] |
| clean | 80 | reversed | 0.5 | +1.96 [+1.26, +2.62] | +3.88 [+1.76, +6.00] | +3.94 [+2.56, +5.70] | +2.67 [+0.99, +4.65] |
| clean | 150 | none | 0.0 | +0.21 [-0.39, +0.69] | -0.01 [-0.82, +0.54] | -0.10 [-0.92, +0.36] | -0.34 [-1.17, +0.11] |
| clean | 150 | missing | 0.2 | +0.33 [-0.13, +0.79] | -0.36 [-0.95, +0.06] | +4.04 [+2.20, +7.09] | +2.33 [+0.68, +4.73] |
| clean | 150 | missing | 0.5 | +2.03 [+0.99, +3.17] | +0.16 [-0.04, +0.31] | +10.53 [+9.50, +11.56] | +5.52 [+2.25, +8.79] |
| clean | 150 | reversed | 0.2 | +1.35 [+0.65, +2.34] | +1.51 [+0.71, +2.25] | +1.33 [+0.88, +1.73] | +0.97 [+0.64, +1.30] |
| clean | 150 | reversed | 0.5 | +1.90 [+0.25, +3.68] | +1.71 [-0.34, +3.55] | +3.54 [+1.53, +5.43] | +3.47 [+1.23, +5.61] |
