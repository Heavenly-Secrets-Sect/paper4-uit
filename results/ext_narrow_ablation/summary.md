# ext_narrow_ablation

narrow, ablation (descriptive): targeted opening selected once (tolerant_v5_sel) and two-sided calibration alone on v3 (tolerant_v5_cal2), same seeds as ext_narrow_eval and a2_baselines, D-07 development.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 2.958 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_sel | 60/60 | 0.931 | 0.931 | 2.974 | 4.30 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_cal2 | 60/60 | 0.935 | 0.935 | 2.995 | 4.32 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.912 | 0.912 | 2.912 | 4.72 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_sel | 60/60 | 0.906 | 0.906 | 2.790 | 4.66 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_cal2 | 60/60 | 0.918 | 0.918 | 3.063 | 4.65 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.919 | 0.919 | 3.201 | 4.86 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_sel | 60/60 | 0.914 | 0.914 | 3.124 | 4.71 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_cal2 | 60/60 | 0.929 | 0.929 | 3.244 | 4.71 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.983 | 0.983 | 6.601 | 7.77 | 0.816 | 0.000 | 0.475 |
| clean | 40 | missing | 0.2 | tolerant_v5_sel | 60/60 | 0.943 | 0.946 | 3.787 | 5.34 | 0.557 | 0.003 | 0.370 |
| clean | 40 | missing | 0.2 | tolerant_v5_cal2 | 60/60 | 0.962 | 0.962 | 5.563 | 7.01 | 0.838 | 0.000 | 0.471 |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.978 | 0.978 | 6.454 | 7.53 | 0.859 | 0.000 | 0.456 |
| clean | 40 | missing | 0.5 | tolerant_v5_sel | 60/60 | 0.952 | 0.952 | 4.420 | 5.60 | 0.596 | 0.000 | 0.388 |
| clean | 40 | missing | 0.5 | tolerant_v5_cal2 | 60/60 | 0.951 | 0.951 | 5.448 | 6.98 | 0.810 | 0.000 | 0.467 |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.109 | 4.78 | 0.462 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_sel | 60/60 | 0.927 | 0.927 | 3.043 | 4.78 | 0.464 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_cal2 | 60/60 | 0.920 | 0.920 | 2.985 | 4.68 | 0.483 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.210 | 4.78 | 0.502 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_sel | 60/60 | 0.912 | 0.912 | 3.069 | 4.69 | 0.524 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_cal2 | 60/60 | 0.920 | 0.920 | 3.064 | 4.74 | 0.512 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.933 | 0.933 | 1.828 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_sel | 60/60 | 0.920 | 0.920 | 1.623 | 2.52 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_cal2 | 60/60 | 0.929 | 0.929 | 1.758 | 2.51 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 1.860 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_sel | 60/60 | 0.938 | 0.938 | 1.818 | 2.52 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_cal2 | 60/60 | 0.941 | 0.941 | 1.881 | 2.54 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 1.987 | 2.65 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_sel | 60/60 | 0.933 | 0.933 | 1.900 | 2.66 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_cal2 | 60/60 | 0.939 | 0.939 | 1.967 | 2.64 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 2.588 | 3.28 | 0.411 | 0.000 | 0.285 |
| clean | 80 | missing | 0.2 | tolerant_v5_sel | 60/60 | 0.937 | 0.937 | 2.253 | 3.13 | 0.364 | 0.000 | 0.261 |
| clean | 80 | missing | 0.2 | tolerant_v5_cal2 | 60/60 | 0.936 | 0.936 | 2.457 | 3.25 | 0.424 | 0.000 | 0.283 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 2.692 | 3.37 | 0.409 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | tolerant_v5_sel | 60/60 | 0.934 | 0.934 | 2.429 | 3.54 | 0.397 | 0.000 | 0.270 |
| clean | 80 | missing | 0.5 | tolerant_v5_cal2 | 60/60 | 0.939 | 0.939 | 2.491 | 3.34 | 0.425 | 0.000 | 0.278 |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 2.117 | 2.79 | 0.331 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_sel | 60/60 | 0.939 | 0.939 | 2.020 | 2.75 | 0.358 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_cal2 | 60/60 | 0.946 | 0.946 | 2.150 | 2.80 | 0.339 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.929 | 0.929 | 2.084 | 2.97 | 0.365 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_sel | 60/60 | 0.923 | 0.923 | 2.000 | 3.00 | 0.361 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_cal2 | 60/60 | 0.932 | 0.932 | 2.104 | 2.97 | 0.377 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_sel | 60/60 | 0.965 | 0.965 | 1.289 | 1.58 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_cal2 | 60/60 | 0.965 | 0.965 | 1.286 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.326 | 1.58 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_sel | 60/60 | 0.970 | 0.970 | 1.376 | 1.61 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_cal2 | 60/60 | 0.956 | 0.956 | 1.261 | 1.59 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.376 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_sel | 60/60 | 0.969 | 0.969 | 1.448 | 1.70 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_cal2 | 60/60 | 0.961 | 0.961 | 1.317 | 1.65 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.691 | 2.06 | 0.259 | 0.000 | 0.215 |
| clean | 150 | missing | 0.2 | tolerant_v5_sel | 60/60 | 0.978 | 0.978 | 1.629 | 1.89 | 0.224 | 0.000 | 0.176 |
| clean | 150 | missing | 0.2 | tolerant_v5_cal2 | 60/60 | 0.972 | 0.972 | 1.752 | 2.09 | 0.258 | 0.000 | 0.219 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.761 | 2.22 | 0.255 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v5_sel | 60/60 | 0.956 | 0.956 | 1.700 | 2.47 | 0.272 | 0.000 | 0.193 |
| clean | 150 | missing | 0.5 | tolerant_v5_cal2 | 60/60 | 0.971 | 0.971 | 1.826 | 2.23 | 0.261 | 0.000 | 0.211 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.970 | 0.970 | 1.532 | 1.89 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_sel | 60/60 | 0.965 | 0.965 | 1.530 | 1.87 | 0.216 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_cal2 | 60/60 | 0.969 | 0.969 | 1.516 | 1.85 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 1.584 | 2.02 | 0.255 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_sel | 60/60 | 0.951 | 0.951 | 1.494 | 2.02 | 0.245 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_cal2 | 60/60 | 0.953 | 0.953 | 1.472 | 2.00 | 0.252 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_sel | tolerant_v5_cal2 |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.09 [-0.20, +0.04] | -0.07 [-0.23, +0.09] |
| clean | 40 | extra | 0.2 | -0.06 [-0.18, +0.06] | -0.07 [-0.25, +0.06] |
| clean | 40 | extra | 0.5 | -0.15 [-0.33, -0.01] | -0.15 [-0.36, +0.02] |
| clean | 40 | missing | 0.2 | -2.43 [-2.89, -1.95] | -0.76 [-0.91, -0.61] |
| clean | 40 | missing | 0.5 | -1.93 [-2.34, -1.47] | -0.55 [-0.74, -0.34] |
| clean | 40 | reversed | 0.2 | -0.00 [-0.12, +0.14] | -0.11 [-0.29, +0.02] |
| clean | 40 | reversed | 0.5 | -0.09 [-0.17, -0.01] | -0.04 [-0.13, +0.05] |
| clean | 80 | none | 0.0 | +0.02 [-0.06, +0.09] | +0.00 [-0.04, +0.06] |
| clean | 80 | extra | 0.2 | -0.01 [-0.07, +0.05] | +0.02 [-0.05, +0.07] |
| clean | 80 | extra | 0.5 | +0.01 [-0.05, +0.09] | -0.01 [-0.06, +0.04] |
| clean | 80 | missing | 0.2 | -0.15 [-0.36, +0.06] | -0.02 [-0.09, +0.04] |
| clean | 80 | missing | 0.5 | +0.17 [-0.04, +0.39] | -0.03 [-0.10, +0.04] |
| clean | 80 | reversed | 0.2 | -0.04 [-0.08, -0.00] | +0.01 [-0.02, +0.05] |
| clean | 80 | reversed | 0.5 | +0.03 [-0.02, +0.07] | +0.01 [-0.05, +0.06] |
| clean | 150 | none | 0.0 | +0.01 [-0.01, +0.04] | -0.01 [-0.03, +0.02] |
| clean | 150 | extra | 0.2 | +0.03 [+0.00, +0.06] | +0.01 [-0.02, +0.05] |
| clean | 150 | extra | 0.5 | +0.04 [+0.02, +0.07] | -0.01 [-0.03, +0.02] |
| clean | 150 | missing | 0.2 | -0.16 [-0.23, -0.10] | +0.03 [-0.00, +0.06] |
| clean | 150 | missing | 0.5 | +0.25 [+0.03, +0.48] | +0.01 [-0.02, +0.04] |
| clean | 150 | reversed | 0.2 | -0.03 [-0.05, +0.00] | -0.05 [-0.08, -0.01] |
| clean | 150 | reversed | 0.5 | +0.01 [-0.04, +0.05] | -0.02 [-0.07, +0.03] |
