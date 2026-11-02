# ext_narrow_ges

narrow: tolerant_v5 (frozen as in ext_narrow_eval) on skeletons learned by the GES of Paper 2, against tolerant_v4, pselect_union, plugin; D-07 development, a3_ges seeds. Descriptive rule in docs/ext/narrow.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | plugin | 60/60 | 0.862 | 0.862 | 2.139 | 4.74 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | pselect_union | 60/60 | 0.889 | 0.915 | 3.733 | 6.48 | 0.982 | 0.275 | 0.633 |
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 2.958 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5 | 60/60 | 0.941 | 0.941 | 3.120 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | ges | 0.0 | plugin | 60/60 | 0.383 | 0.408 | 1.368 | 21.81 | 0.941 | 0.061 | 0.557 |
| clean | 40 | ges | 0.0 | pselect_union | 60/60 | 0.855 | 0.886 | 3.460 | 6.71 | 1.013 | 0.277 | 0.586 |
| clean | 40 | ges | 0.0 | tolerant_v4 | 59/60 | 0.979 | 0.979 | 6.974 | 8.31 | 0.847 | 0.000 | 0.494 |
| clean | 40 | ges | 0.0 | tolerant_v5 | 58/60 | 0.970 | 0.970 | 5.224 | 6.10 | 0.691 | 0.000 | 0.439 |
| clean | 80 | none | 0.0 | plugin | 60/60 | 0.869 | 0.869 | 1.426 | 2.78 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | pselect_union | 60/60 | 0.929 | 0.937 | 2.434 | 3.45 | 0.436 | 0.031 | 0.298 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.933 | 0.933 | 1.828 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5 | 60/60 | 0.926 | 0.926 | 1.665 | 2.47 | 0.296 | 0.000 | 0.237 |
| clean | 80 | ges | 0.0 | plugin | 60/60 | 0.350 | 0.371 | 1.008 | 22.51 | 0.787 | 0.058 | 0.430 |
| clean | 80 | ges | 0.0 | pselect_union | 60/60 | 0.907 | 0.914 | 2.332 | 4.01 | 0.514 | 0.031 | 0.253 |
| clean | 80 | ges | 0.0 | tolerant_v4 | 60/60 | 0.950 | 0.950 | 2.758 | 3.69 | 0.451 | 0.000 | 0.286 |
| clean | 80 | ges | 0.0 | tolerant_v5 | 60/60 | 0.936 | 0.936 | 2.659 | 3.64 | 0.436 | 0.000 | 0.256 |
| clean | 150 | none | 0.0 | plugin | 60/60 | 0.930 | 0.930 | 1.068 | 1.58 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | pselect_union | 60/60 | 0.977 | 0.977 | 1.702 | 2.03 | 0.221 | 0.005 | 0.189 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5 | 60/60 | 0.955 | 0.955 | 1.217 | 1.55 | 0.191 | 0.000 | 0.170 |
| clean | 150 | ges | 0.0 | plugin | 60/60 | 0.320 | 0.336 | 0.765 | 22.19 | 0.728 | 0.048 | 0.326 |
| clean | 150 | ges | 0.0 | pselect_union | 60/60 | 0.914 | 0.914 | 1.653 | 3.06 | 0.267 | 0.005 | 0.162 |
| clean | 150 | ges | 0.0 | tolerant_v4 | 60/60 | 0.937 | 0.937 | 1.805 | 2.59 | 0.299 | 0.000 | 0.214 |
| clean | 150 | ges | 0.0 | tolerant_v5 | 60/60 | 0.950 | 0.950 | 2.005 | 2.77 | 0.306 | 0.000 | 0.188 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | plugin | pselect_union | tolerant_v5 |
|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.35 [-0.09, +0.88] | +2.09 [+1.57, +2.57] | +0.00 [-0.13, +0.14] |
| clean | 40 | ges | 0.0 | +13.51 [+11.68, +15.24] | -1.58 [-2.17, -1.01] | -2.24 [-2.58, -1.84] |
| clean | 80 | none | 0.0 | +0.28 [+0.13, +0.44] | +0.95 [+0.77, +1.16] | -0.03 [-0.11, +0.05] |
| clean | 80 | ges | 0.0 | +18.82 [+16.88, +20.88] | +0.32 [+0.05, +0.57] | -0.05 [-0.20, +0.12] |
| clean | 150 | none | 0.0 | +0.01 [-0.05, +0.08] | +0.47 [+0.37, +0.59] | -0.01 [-0.04, +0.02] |
| clean | 150 | ges | 0.0 | +19.60 [+17.81, +21.28] | +0.48 [+0.11, +0.82] | +0.18 [+0.01, +0.37] |

## Interval score difference vs `pselect_union` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | plugin | tolerant_v4 | tolerant_v5 |
|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -1.74 [-2.52, -0.73] | -2.09 [-2.57, -1.57] | -2.09 [-2.55, -1.56] |
| clean | 40 | ges | 0.0 | +15.10 [+13.41, +16.78] | +1.58 [+1.01, +2.17] | -0.62 [-1.24, +0.01] |
| clean | 80 | none | 0.0 | -0.67 [-0.90, -0.40] | -0.95 [-1.16, -0.77] | -0.98 [-1.18, -0.78] |
| clean | 80 | ges | 0.0 | +18.50 [+16.69, +20.40] | -0.32 [-0.57, -0.05] | -0.36 [-0.57, -0.17] |
| clean | 150 | none | 0.0 | -0.45 [-0.58, -0.30] | -0.47 [-0.59, -0.37] | -0.48 [-0.61, -0.36] |
| clean | 150 | ges | 0.0 | +19.13 [+17.42, +20.67] | -0.48 [-0.82, -0.11] | -0.29 [-0.70, +0.13] |
