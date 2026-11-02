# ext_baselines3_eval

R3-1 (baselines3): tolerant_v4 and tolerant_v5_1 against the full-budget baseline envelope (pselect_union_v3, pselect_union_v3_cal, pselect_cal, fullvar_cal, targeted_lp_cal, bvar_minnesota_v2_cal; tlp2_db_p3 from stored content-seeded rows) on D-07 development, T 80/150, missing 0.2/0.5 only (cell positions kept by experiments/ext/baselines3/run_cells.py). Frozen width factors only. Rule pre-registered in docs/ext/baselines3.md section 3.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.959 | 0.959 | 2.588 | 3.28 | 0.411 | 0.000 | 0.285 |
| clean | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.949 | 0.949 | 2.193 | 2.84 | 0.346 | 0.000 | 0.229 |
| clean | 80 | missing | 0.2 | pselect_union_v3 | 60/60 | 0.960 | 0.964 | 2.833 | 3.50 | 0.508 | 0.057 | 0.281 |
| clean | 80 | missing | 0.2 | pselect_union_v3_cal | 60/60 | 0.936 | 0.942 | 2.408 | 3.36 | 0.508 | 0.057 | 0.281 |
| clean | 80 | missing | 0.2 | pselect_cal | 60/60 | 0.961 | 0.966 | 3.140 | 3.88 | 0.462 | 0.031 | 0.268 |
| clean | 80 | missing | 0.2 | fullvar_cal | 60/60 | 0.960 | 0.960 | 2.805 | 3.44 | 0.419 | 0.000 | 0.295 |
| clean | 80 | missing | 0.2 | targeted_lp | 60/60 | 0.939 | 0.939 | 2.480 | 3.46 | 0.425 | 0.002 | 0.330 |
| clean | 80 | missing | 0.2 | targeted_lp_cal | 60/60 | 0.956 | 0.956 | 2.728 | 3.51 | 0.425 | 0.002 | 0.330 |
| clean | 80 | missing | 0.2 | bvar_minnesota_v2_cal | 60/60 | 0.958 | 0.958 | 3.884 | 4.86 | 0.394 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.957 | 0.957 | 2.692 | 3.37 | 0.409 | 0.000 | 0.275 |
| clean | 80 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.951 | 0.951 | 2.424 | 3.10 | 0.364 | 0.000 | 0.264 |
| clean | 80 | missing | 0.5 | pselect_union_v3 | 60/60 | 0.965 | 0.968 | 2.984 | 3.58 | 0.505 | 0.069 | 0.247 |
| clean | 80 | missing | 0.5 | pselect_union_v3_cal | 60/60 | 0.943 | 0.949 | 2.536 | 3.40 | 0.505 | 0.069 | 0.247 |
| clean | 80 | missing | 0.5 | pselect_cal | 60/60 | 0.944 | 0.948 | 3.038 | 4.07 | 0.484 | 0.031 | 0.297 |
| clean | 80 | missing | 0.5 | fullvar_cal | 60/60 | 0.950 | 0.950 | 2.906 | 3.86 | 0.447 | 0.000 | 0.290 |
| clean | 80 | missing | 0.5 | targeted_lp | 60/60 | 0.901 | 0.902 | 2.543 | 4.11 | 0.554 | 0.035 | 0.431 |
| clean | 80 | missing | 0.5 | targeted_lp_cal | 60/60 | 0.925 | 0.925 | 2.797 | 3.95 | 0.554 | 0.035 | 0.431 |
| clean | 80 | missing | 0.5 | bvar_minnesota_v2_cal | 60/60 | 0.958 | 0.958 | 3.838 | 4.58 | 0.568 | 0.000 | 0.297 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.968 | 0.968 | 1.691 | 2.06 | 0.259 | 0.000 | 0.215 |
| clean | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.966 | 0.966 | 1.463 | 1.76 | 0.218 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | pselect_union_v3 | 60/60 | 0.986 | 0.987 | 1.885 | 2.15 | 0.260 | 0.016 | 0.176 |
| clean | 150 | missing | 0.2 | pselect_union_v3_cal | 60/60 | 0.962 | 0.965 | 1.508 | 1.91 | 0.260 | 0.016 | 0.176 |
| clean | 150 | missing | 0.2 | pselect_cal | 60/60 | 0.981 | 0.980 | 2.221 | 2.56 | 0.242 | 0.005 | 0.197 |
| clean | 150 | missing | 0.2 | fullvar_cal | 60/60 | 0.981 | 0.981 | 2.209 | 2.58 | 0.257 | 0.000 | 0.224 |
| clean | 150 | missing | 0.2 | targeted_lp | 60/60 | 0.931 | 0.931 | 1.506 | 2.24 | 0.259 | 0.001 | 0.208 |
| clean | 150 | missing | 0.2 | targeted_lp_cal | 60/60 | 0.978 | 0.978 | 1.958 | 2.34 | 0.259 | 0.001 | 0.208 |
| clean | 150 | missing | 0.2 | bvar_minnesota_v2_cal | 60/60 | 0.968 | 0.968 | 3.050 | 3.71 | 0.284 | 0.000 | 0.210 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.962 | 0.962 | 1.761 | 2.22 | 0.255 | 0.000 | 0.214 |
| clean | 150 | missing | 0.5 | tolerant_v5_1 | 60/60 | 0.968 | 0.968 | 1.596 | 1.99 | 0.245 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | pselect_union_v3 | 60/60 | 0.991 | 0.992 | 2.039 | 2.32 | 0.270 | 0.012 | 0.170 |
| clean | 150 | missing | 0.5 | pselect_union_v3_cal | 60/60 | 0.967 | 0.969 | 1.631 | 2.00 | 0.270 | 0.012 | 0.170 |
| clean | 150 | missing | 0.5 | pselect_cal | 60/60 | 0.955 | 0.954 | 2.138 | 2.86 | 0.269 | 0.005 | 0.201 |
| clean | 150 | missing | 0.5 | fullvar_cal | 60/60 | 0.962 | 0.962 | 2.327 | 2.95 | 0.306 | 0.000 | 0.233 |
| clean | 150 | missing | 0.5 | targeted_lp | 60/60 | 0.904 | 0.903 | 1.554 | 2.67 | 0.306 | 0.011 | 0.239 |
| clean | 150 | missing | 0.5 | targeted_lp_cal | 60/60 | 0.960 | 0.959 | 2.020 | 2.59 | 0.306 | 0.011 | 0.239 |
| clean | 150 | missing | 0.5 | bvar_minnesota_v2_cal | 60/60 | 0.962 | 0.962 | 2.967 | 3.63 | 0.403 | 0.000 | 0.224 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1 | pselect_union_v3 | pselect_union_v3_cal | pselect_cal | fullvar_cal | targeted_lp | targeted_lp_cal | bvar_minnesota_v2_cal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.2 | – | – | – | – | – | – | – | – |
| clean | 80 | extra | 0.5 | – | – | – | – | – | – | – | – |
| clean | 80 | missing | 0.2 | -0.43 [-0.55, -0.34] | +0.22 [+0.05, +0.38] | +0.09 [-0.09, +0.26] | +0.60 [+0.44, +0.79] | +0.17 [+0.08, +0.26] | +0.18 [-0.02, +0.42] | +0.23 [+0.06, +0.42] | +1.58 [+1.26, +1.95] |
| clean | 80 | missing | 0.5 | -0.27 [-0.41, -0.15] | +0.21 [+0.03, +0.37] | +0.03 [-0.14, +0.19] | +0.70 [+0.55, +0.87] | +0.49 [+0.33, +0.64] | +0.74 [+0.50, +1.02] | +0.58 [+0.40, +0.77] | +1.21 [+1.01, +1.42] |
| clean | 80 | reversed | 0.2 | – | – | – | – | – | – | – | – |
| clean | 80 | reversed | 0.5 | – | – | – | – | – | – | – | – |
| clean | 150 | none | 0.0 | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.2 | – | – | – | – | – | – | – | – |
| clean | 150 | extra | 0.5 | – | – | – | – | – | – | – | – |
| clean | 150 | missing | 0.2 | -0.30 [-0.35, -0.24] | +0.09 [+0.03, +0.15] | -0.15 [-0.25, -0.04] | +0.50 [+0.39, +0.62] | +0.52 [+0.43, +0.63] | +0.18 [+0.04, +0.33] | +0.29 [+0.19, +0.38] | +1.65 [+1.45, +1.88] |
| clean | 150 | missing | 0.5 | -0.23 [-0.30, -0.16] | +0.11 [+0.04, +0.17] | -0.22 [-0.30, -0.14] | +0.65 [+0.47, +0.83] | +0.73 [+0.62, +0.84] | +0.45 [+0.25, +0.64] | +0.38 [+0.26, +0.49] | +1.42 [+1.27, +1.57] |
| clean | 150 | reversed | 0.2 | – | – | – | – | – | – | – | – |
| clean | 150 | reversed | 0.5 | – | – | – | – | – | – | – | – |
