# ext_v51_eval

v51 (R2-2b): tolerant_v5_1 (targeted opening re-selected per draw when the rows-to-regressors ratio of the all-lag fit is below TAU, fixed on D-07H; v5_cal2 otherwise; two-sided calibration) against frozen tolerant_v4 on the a2 grid, D-07 development, a2_baselines seeds. Rule in docs/ext/v51.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 2.958 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.912 | 0.912 | 2.912 | 4.72 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.919 | 0.919 | 3.201 | 4.86 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.983 | 0.983 | 6.601 | 7.77 | 0.816 | 0.000 | 0.475 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.922 | 0.922 | 3.290 | 4.84 | 0.553 | 0.000 | 0.382 |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.978 | 0.978 | 6.454 | 7.53 | 0.859 | 0.000 | 0.456 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.790 | 5.09 | 0.572 | 0.000 | 0.401 |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.109 | 4.78 | 0.462 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.210 | 4.78 | 0.502 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.933 | 0.933 | 1.828 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 1.860 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 1.987 | 2.65 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 2.588 | 3.28 | 0.411 | 0.000 | 0.285 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.193 | 2.84 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 2.692 | 3.37 | 0.409 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.424 | 3.10 | 0.364 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 2.117 | 2.79 | 0.331 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.929 | 0.929 | 2.084 | 2.97 | 0.365 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.326 | 1.58 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.376 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.691 | 2.06 | 0.259 | 0.000 | 0.215 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.966 | 0.966 | 1.463 | 1.76 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.761 | 2.22 | 0.255 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 1.596 | 1.99 | 0.245 | 0.000 | 0.175 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.970 | 0.970 | 1.532 | 1.89 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 1.584 | 2.02 | 0.255 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 |
|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.02 [-0.16, +0.13] |
| clean | 40 | extra | 0.2 | -0.10 [-0.22, +0.01] |
| clean | 40 | extra | 0.5 | -0.04 [-0.18, +0.05] |
| clean | 40 | missing | 0.2 | -2.93 [-3.44, -2.36] |
| clean | 40 | missing | 0.5 | -2.44 [-2.84, -2.04] |
| clean | 40 | reversed | 0.2 | -0.08 [-0.24, +0.07] |
| clean | 40 | reversed | 0.5 | -0.04 [-0.13, +0.04] |
| clean | 80 | none | 0.0 | +0.03 [-0.03, +0.09] |
| clean | 80 | extra | 0.2 | +0.00 [-0.06, +0.09] |
| clean | 80 | extra | 0.5 | +0.02 [-0.04, +0.08] |
| clean | 80 | missing | 0.2 | -0.43 [-0.55, -0.33] |
| clean | 80 | missing | 0.5 | -0.27 [-0.39, -0.15] |
| clean | 80 | reversed | 0.2 | +0.00 [-0.05, +0.05] |
| clean | 80 | reversed | 0.5 | +0.08 [+0.01, +0.14] |
| clean | 150 | none | 0.0 | +0.01 [-0.02, +0.04] |
| clean | 150 | extra | 0.2 | +0.02 [-0.00, +0.05] |
| clean | 150 | extra | 0.5 | +0.02 [-0.00, +0.04] |
| clean | 150 | missing | 0.2 | -0.30 [-0.36, -0.24] |
| clean | 150 | missing | 0.5 | -0.23 [-0.30, -0.16] |
| clean | 150 | reversed | 0.2 | -0.07 [-0.10, -0.03] |
| clean | 150 | reversed | 0.5 | +0.02 [-0.04, +0.08] |
