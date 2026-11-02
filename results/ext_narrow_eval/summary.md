# ext_narrow_eval

narrow: tolerant_v5 (targeted opening re-selected per bootstrap draw + two-sided width calibration) and ablations against tolerant_v4, pselect_union, plugin, lp_allpast on the a2 grid, D-07 development, a2_baselines seeds. Rule in docs/ext/narrow.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 2.958 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | tolerant_v5 | 60/60 | 0.935 | 0.935 | 3.126 | 4.35 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.912 | 0.912 | 2.912 | 4.72 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | tolerant_v5 | 60/60 | 0.913 | 0.913 | 2.783 | 4.70 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.919 | 0.919 | 3.201 | 4.86 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | tolerant_v5 | 60/60 | 0.910 | 0.910 | 2.984 | 4.83 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.983 | 0.983 | 6.601 | 7.77 | 0.816 | 0.000 | 0.475 |
| clean | 40 | missing | 0.2 | tolerant_v5 | 60/60 | 0.933 | 0.933 | 3.372 | 4.79 | 0.537 | 0.000 | 0.388 |
| clean | 40 | missing | 0.5 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.978 | 0.978 | 6.454 | 7.53 | 0.859 | 0.000 | 0.456 |
| clean | 40 | missing | 0.5 | tolerant_v5 | 60/60 | 0.944 | 0.944 | 4.078 | 5.12 | 0.605 | 0.000 | 0.421 |
| clean | 40 | reversed | 0.2 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.109 | 4.78 | 0.462 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.929 | 0.929 | 3.180 | 4.74 | 0.462 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | lp_allpast | 0/60 | nan | nan | nan | nan | nan | nan | nan |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.210 | 4.78 | 0.502 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | tolerant_v5 | 60/60 | 0.922 | 0.922 | 3.214 | 4.75 | 0.496 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | lp_allpast | 60/60 | 0.839 | 0.839 | 2.590 | 5.70 | 0.642 | 0.000 | nan |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.933 | 0.933 | 1.828 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | none | 0.0 | tolerant_v5 | 60/60 | 0.928 | 0.928 | 1.745 | 2.50 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | lp_allpast | 60/60 | 0.835 | 0.835 | 2.589 | 5.79 | 0.646 | 0.000 | nan |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 1.860 | 2.53 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.2 | tolerant_v5 | 60/60 | 0.935 | 0.935 | 1.774 | 2.51 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | lp_allpast | 60/60 | 0.836 | 0.836 | 2.563 | 5.75 | 0.645 | 0.000 | nan |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 1.987 | 2.65 | 0.339 | 0.000 | 0.253 |
| clean | 80 | extra | 0.5 | tolerant_v5 | 60/60 | 0.930 | 0.930 | 1.916 | 2.67 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | lp_allpast | 60/60 | 0.836 | 0.836 | 2.599 | 5.69 | 0.639 | 0.000 | nan |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 2.588 | 3.28 | 0.411 | 0.000 | 0.285 |
| clean | 80 | missing | 0.2 | tolerant_v5 | 60/60 | 0.942 | 0.942 | 2.152 | 2.78 | 0.347 | 0.000 | 0.239 |
| clean | 80 | missing | 0.5 | lp_allpast | 60/60 | 0.838 | 0.838 | 2.586 | 5.72 | 0.641 | 0.000 | nan |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 2.692 | 3.37 | 0.409 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | tolerant_v5 | 60/60 | 0.921 | 0.921 | 2.313 | 3.35 | 0.428 | 0.000 | 0.263 |
| clean | 80 | reversed | 0.2 | lp_allpast | 60/60 | 0.827 | 0.827 | 2.678 | 6.22 | 0.655 | 0.000 | nan |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.948 | 0.948 | 2.117 | 2.79 | 0.331 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.936 | 0.936 | 2.029 | 2.81 | 0.357 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | lp_allpast | 60/60 | 0.807 | 0.807 | 2.814 | 7.54 | 0.701 | 0.000 | nan |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.929 | 0.929 | 2.084 | 2.97 | 0.365 | 0.000 | 0.262 |
| clean | 80 | reversed | 0.5 | tolerant_v5 | 60/60 | 0.922 | 0.922 | 2.061 | 3.03 | 0.361 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | lp_allpast | 60/60 | 0.908 | 0.908 | 1.630 | 2.66 | 0.325 | 0.000 | nan |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.964 | 0.964 | 1.277 | 1.56 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5 | 60/60 | 0.961 | 0.961 | 1.238 | 1.54 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | lp_allpast | 60/60 | 0.908 | 0.908 | 1.632 | 2.67 | 0.334 | 0.000 | nan |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.326 | 1.58 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5 | 60/60 | 0.961 | 0.961 | 1.239 | 1.57 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | lp_allpast | 60/60 | 0.907 | 0.907 | 1.658 | 2.69 | 0.342 | 0.000 | nan |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.376 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5 | 60/60 | 0.956 | 0.956 | 1.317 | 1.66 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | lp_allpast | 60/60 | 0.902 | 0.902 | 1.636 | 2.74 | 0.325 | 0.000 | nan |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.691 | 2.06 | 0.259 | 0.000 | 0.215 |
| clean | 150 | missing | 0.2 | tolerant_v5 | 60/60 | 0.973 | 0.973 | 1.623 | 1.98 | 0.218 | 0.000 | 0.174 |
| clean | 150 | missing | 0.5 | lp_allpast | 60/60 | 0.900 | 0.900 | 1.632 | 2.88 | 0.328 | 0.000 | nan |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.761 | 2.22 | 0.255 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v5 | 60/60 | 0.960 | 0.960 | 1.776 | 2.34 | 0.270 | 0.000 | 0.187 |
| clean | 150 | reversed | 0.2 | lp_allpast | 60/60 | 0.880 | 0.880 | 1.765 | 3.51 | 0.350 | 0.000 | nan |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.970 | 0.970 | 1.532 | 1.89 | 0.210 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5 | 60/60 | 0.967 | 0.967 | 1.546 | 1.86 | 0.225 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | lp_allpast | 60/60 | 0.838 | 0.838 | 1.804 | 4.74 | 0.371 | 0.000 | nan |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 1.584 | 2.02 | 0.255 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5 | 60/60 | 0.953 | 0.953 | 1.522 | 2.02 | 0.254 | 0.000 | 0.214 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | lp_allpast | tolerant_v5 |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | – | -0.04 [-0.14, +0.09] |
| clean | 40 | extra | 0.2 | – | -0.02 [-0.16, +0.14] |
| clean | 40 | extra | 0.5 | – | -0.03 [-0.09, +0.05] |
| clean | 40 | missing | 0.2 | – | -2.98 [-3.44, -2.50] |
| clean | 40 | missing | 0.5 | – | -2.41 [-2.75, -2.07] |
| clean | 40 | reversed | 0.2 | – | -0.04 [-0.13, +0.07] |
| clean | 40 | reversed | 0.5 | – | -0.03 [-0.09, +0.04] |
| clean | 80 | none | 0.0 | +3.20 [+2.68, +3.72] | -0.00 [-0.05, +0.05] |
| clean | 80 | extra | 0.2 | +3.26 [+2.76, +3.77] | -0.01 [-0.06, +0.03] |
| clean | 80 | extra | 0.5 | +3.11 [+2.66, +3.56] | +0.02 [-0.02, +0.07] |
| clean | 80 | missing | 0.2 | +2.41 [+1.98, +2.86] | -0.50 [-0.66, -0.35] |
| clean | 80 | missing | 0.5 | +2.35 [+1.98, +2.78] | -0.02 [-0.21, +0.20] |
| clean | 80 | reversed | 0.2 | +3.43 [+3.02, +3.88] | +0.01 [-0.04, +0.07] |
| clean | 80 | reversed | 0.5 | +4.57 [+4.06, +5.10] | +0.06 [+0.00, +0.11] |
| clean | 150 | none | 0.0 | +1.10 [+0.84, +1.39] | -0.02 [-0.05, +0.02] |
| clean | 150 | extra | 0.2 | +1.09 [+0.82, +1.36] | -0.01 [-0.05, +0.03] |
| clean | 150 | extra | 0.5 | +1.03 [+0.77, +1.29] | +0.01 [-0.03, +0.04] |
| clean | 150 | missing | 0.2 | +0.68 [+0.47, +0.90] | -0.08 [-0.20, +0.08] |
| clean | 150 | missing | 0.5 | +0.67 [+0.41, +0.91] | +0.12 [-0.02, +0.25] |
| clean | 150 | reversed | 0.2 | +1.62 [+1.17, +2.16] | -0.03 [-0.05, -0.00] |
| clean | 150 | reversed | 0.5 | +2.72 [+2.15, +3.42] | +0.00 [-0.05, +0.06] |
