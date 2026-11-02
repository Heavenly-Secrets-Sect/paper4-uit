# ext_r4leadlag_eval_clean

r4leadlag: tolerant_v5_1_leadlag (A) and tolerant_v5_1_leadlag_skel (D) (lead-lag Haugh gate before contemporaneous repair) vs tolerant_v5_1 (frozen factors) on the clean a2 grid G, D-07 development, seeds of ext_v51_eval (kinds extra/missing/reversed keep c_idx and damage streams). Run through experiments/ext/r4leadlag/drive.py (bootstrap tag of the candidate = that of tolerant_v5_1). Rule in docs/ext/r4leadlag.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.920 | 0.920 | 2.771 | 4.37 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.914 | 0.914 | 2.909 | 4.63 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.920 | 0.920 | 3.212 | 4.81 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.922 | 0.922 | 3.290 | 4.84 | 0.553 | 0.000 | 0.382 |
| clean | 40 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.922 | 0.922 | 3.255 | 4.81 | 0.554 | 0.000 | 0.382 |
| clean | 40 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.931 | 0.931 | 3.385 | 4.91 | 0.553 | 0.000 | 0.382 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.790 | 5.09 | 0.572 | 0.000 | 0.401 |
| clean | 40 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.935 | 0.935 | 3.755 | 5.05 | 0.584 | 0.000 | 0.401 |
| clean | 40 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.947 | 0.947 | 3.903 | 5.14 | 0.609 | 0.000 | 0.387 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.928 | 0.928 | 3.102 | 4.70 | 0.466 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.920 | 0.920 | 3.279 | 4.74 | 0.506 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.939 | 0.939 | 1.853 | 2.53 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.927 | 0.927 | 1.732 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.925 | 0.925 | 1.882 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.193 | 2.84 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.940 | 0.940 | 2.127 | 2.86 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.940 | 0.940 | 2.139 | 2.87 | 0.345 | 0.000 | 0.229 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.424 | 3.10 | 0.364 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.944 | 0.944 | 2.324 | 3.09 | 0.357 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.944 | 0.944 | 2.316 | 3.10 | 0.353 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.941 | 0.941 | 2.054 | 2.79 | 0.348 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.918 | 0.918 | 2.032 | 3.05 | 0.369 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.966 | 0.966 | 1.463 | 1.76 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.972 | 0.972 | 1.519 | 1.79 | 0.213 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.978 | 0.978 | 1.604 | 1.83 | 0.219 | 0.000 | 0.176 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 1.596 | 1.99 | 0.245 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.974 | 0.974 | 1.665 | 2.03 | 0.242 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.975 | 0.975 | 1.694 | 2.08 | 0.245 | 0.000 | 0.177 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1_leadlag | tolerant_v5_1_leadlag_skel |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 40 | extra | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 40 | extra | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 40 | missing | 0.2 | -0.03 [-0.08, +0.03] | +0.08 [-0.02, +0.16] |
| clean | 40 | missing | 0.5 | -0.04 [-0.12, +0.03] | +0.05 [-0.07, +0.16] |
| clean | 40 | reversed | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 40 | reversed | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 80 | none | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 80 | extra | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 80 | extra | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 80 | missing | 0.2 | +0.01 [-0.03, +0.07] | +0.02 [-0.04, +0.08] |
| clean | 80 | missing | 0.5 | -0.01 [-0.06, +0.05] | -0.00 [-0.05, +0.05] |
| clean | 80 | reversed | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 80 | reversed | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 150 | none | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 150 | extra | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 150 | extra | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 150 | missing | 0.2 | +0.03 [+0.02, +0.05] | +0.07 [+0.04, +0.10] |
| clean | 150 | missing | 0.5 | +0.04 [+0.02, +0.07] | +0.09 [+0.04, +0.15] |
| clean | 150 | reversed | 0.2 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| clean | 150 | reversed | 0.5 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
