# ext_v51fix_p4h2

FROZEN CONFIRMATORY SPEC v2 (docs/ext/v51fix.md, 'Frozen spec for P4-H2, v2'; supersedes ext_v51_p4h2, which must NOT be run). DO NOT RUN except as the single sealed confirmatory run, after experiments/ext/v51fix/preflight_p4h2.py passes. tolerant_v5_1 (src/paper4/ext_v51.py, unchanged) against frozen tolerant_v4 on the a2 grid, P4-H2 confirmatory; width factors of both methods frozen in experiments/ext/v51/frozen_v4_v51.json. Rule: experiments/ext/v51fix/rule_p4h2_v2.py.

Bank P4-H2 / confirmatory; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.932 | 0.932 | 2.898 | 4.28 | 0.495 | 0.000 | 0.353 |
| clean | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.918 | 0.918 | 2.714 | 4.24 | 0.495 | 0.000 | 0.353 |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.925 | 0.925 | 2.809 | 4.32 | 0.500 | 0.000 | 0.366 |
| clean | 40 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.927 | 0.927 | 2.938 | 4.33 | 0.500 | 0.000 | 0.366 |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.942 | 0.942 | 3.211 | 4.53 | 0.525 | 0.000 | 0.387 |
| clean | 40 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.942 | 0.942 | 3.191 | 4.52 | 0.525 | 0.000 | 0.387 |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.977 | 0.977 | 6.784 | 7.81 | 0.822 | 0.000 | 0.437 |
| clean | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.928 | 0.928 | 3.318 | 4.62 | 0.531 | 0.000 | 0.372 |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.981 | 0.981 | 6.520 | 7.54 | 0.789 | 0.000 | 0.503 |
| clean | 40 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.947 | 0.947 | 3.747 | 4.99 | 0.596 | 0.000 | 0.389 |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.940 | 0.940 | 3.216 | 4.53 | 0.487 | 0.000 | 0.354 |
| clean | 40 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.938 | 0.938 | 3.188 | 4.52 | 0.512 | 0.000 | 0.354 |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.922 | 0.922 | 3.263 | 5.01 | 0.492 | 0.000 | 0.408 |
| clean | 40 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.923 | 0.923 | 3.127 | 5.02 | 0.498 | 0.000 | 0.408 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.949 | 0.949 | 1.852 | 2.38 | 0.267 | 0.000 | 0.228 |
| clean | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.954 | 0.954 | 1.798 | 2.37 | 0.267 | 0.000 | 0.228 |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.947 | 0.947 | 1.886 | 2.49 | 0.278 | 0.000 | 0.224 |
| clean | 80 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.932 | 0.932 | 1.728 | 2.51 | 0.278 | 0.000 | 0.224 |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.954 | 0.954 | 1.964 | 2.55 | 0.303 | 0.000 | 0.234 |
| clean | 80 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.936 | 0.936 | 1.804 | 2.52 | 0.303 | 0.000 | 0.234 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.974 | 0.974 | 2.685 | 3.13 | 0.405 | 0.000 | 0.302 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.963 | 0.963 | 2.175 | 2.68 | 0.339 | 0.000 | 0.251 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.972 | 0.972 | 2.759 | 3.18 | 0.411 | 0.000 | 0.300 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.969 | 0.969 | 2.422 | 2.89 | 0.393 | 0.000 | 0.246 |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.952 | 0.952 | 2.141 | 2.77 | 0.341 | 0.000 | 0.251 |
| clean | 80 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.069 | 2.73 | 0.330 | 0.000 | 0.251 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 2.141 | 2.90 | 0.338 | 0.000 | 0.300 |
| clean | 80 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.942 | 0.942 | 2.072 | 2.91 | 0.349 | 0.000 | 0.300 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 1.291 | 1.56 | 0.188 | 0.000 | 0.173 |
| clean | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.957 | 0.957 | 1.268 | 1.56 | 0.188 | 0.000 | 0.173 |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.961 | 0.961 | 1.278 | 1.57 | 0.191 | 0.000 | 0.171 |
| clean | 150 | extra | 0.2 | tolerant_v5_1 | 60/60 | 0.960 | 0.960 | 1.312 | 1.59 | 0.191 | 0.000 | 0.171 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 1.366 | 1.63 | 0.201 | 0.000 | 0.184 |
| clean | 150 | extra | 0.5 | tolerant_v5_1 | 60/60 | 0.959 | 0.959 | 1.381 | 1.62 | 0.201 | 0.000 | 0.184 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.661 | 1.98 | 0.254 | 0.000 | 0.190 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.964 | 0.964 | 1.421 | 1.75 | 0.210 | 0.000 | 0.184 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.971 | 0.971 | 1.725 | 2.11 | 0.273 | 0.000 | 0.192 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.960 | 0.960 | 1.577 | 1.99 | 0.226 | 0.000 | 0.169 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.536 | 1.88 | 0.232 | 0.000 | 0.189 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1 | 60/60 | 0.952 | 0.952 | 1.415 | 1.84 | 0.246 | 0.000 | 0.189 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.953 | 0.953 | 1.552 | 2.00 | 0.252 | 0.000 | 0.217 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1 | 60/60 | 0.936 | 0.936 | 1.457 | 2.00 | 0.258 | 0.000 | 0.217 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 |
|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.03 [-0.11, +0.06] |
| clean | 40 | extra | 0.2 | +0.01 [-0.09, +0.10] |
| clean | 40 | extra | 0.5 | -0.02 [-0.10, +0.06] |
| clean | 40 | missing | 0.2 | -3.19 [-3.52, -2.84] |
| clean | 40 | missing | 0.5 | -2.55 [-2.77, -2.35] |
| clean | 40 | reversed | 0.2 | -0.01 [-0.08, +0.06] |
| clean | 40 | reversed | 0.5 | +0.01 [-0.06, +0.09] |
| clean | 80 | none | 0.0 | -0.02 [-0.07, +0.03] |
| clean | 80 | extra | 0.2 | +0.02 [-0.05, +0.09] |
| clean | 80 | extra | 0.5 | -0.02 [-0.07, +0.03] |
| clean | 80 | missing | 0.2 | -0.44 [-0.54, -0.33] |
| clean | 80 | missing | 0.5 | -0.29 [-0.39, -0.18] |
| clean | 80 | reversed | 0.2 | -0.04 [-0.12, +0.01] |
| clean | 80 | reversed | 0.5 | +0.01 [-0.04, +0.07] |
| clean | 150 | none | 0.0 | -0.00 [-0.03, +0.02] |
| clean | 150 | extra | 0.2 | +0.03 [-0.02, +0.08] |
| clean | 150 | extra | 0.5 | -0.00 [-0.03, +0.02] |
| clean | 150 | missing | 0.2 | -0.23 [-0.30, -0.17] |
| clean | 150 | missing | 0.5 | -0.12 [-0.28, +0.02] |
| clean | 150 | reversed | 0.2 | -0.05 [-0.10, +0.01] |
| clean | 150 | reversed | 0.5 | -0.01 [-0.06, +0.05] |
