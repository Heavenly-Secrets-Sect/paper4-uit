# ext_tlp2_t40

R2-8 (ID tlp2): faithful double-bootstrap TLP (src/paper4/ext_tlp2.py) and cache-free calibrated TLP vs frozen tolerant_v4 and round-1 targeted_lp, D-07 development, cells [['none', 0.0], ['extra', 0.2], ['extra', 0.5], ['missing', 0.2], ['missing', 0.5], ['reversed', 0.2], ['reversed', 0.5]] at T=[40]. Run with experiments/ext/tlp2/run_cells.py. Descriptive rule pre-registered in docs/ext/tlp2.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.935 | 0.935 | 2.958 | 4.39 | 0.429 | 0.000 | 0.327 |
| clean | 40 | none | 0.0 | targeted_lp | 60/60 | 0.885 | 0.885 | 2.748 | 4.78 | 0.534 | 0.000 | 0.388 |
| clean | 40 | none | 0.0 | tlp2_lp_cal | 60/60 | 0.937 | 0.937 | 3.372 | 4.51 | 0.525 | 0.000 | 0.384 |
| clean | 40 | none | 0.0 | tlp2_db | 60/60 | 0.884 | 0.884 | 2.713 | 4.91 | 0.484 | 0.000 | 0.364 |
| clean | 40 | none | 0.0 | tlp2_db90 | 60/60 | 0.826 | 0.826 | 2.249 | 5.52 | 0.484 | 0.000 | 0.364 |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.912 | 0.912 | 2.912 | 4.72 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.2 | targeted_lp | 60/60 | 0.881 | 0.881 | 2.907 | 4.91 | 0.535 | 0.000 | 0.376 |
| clean | 40 | extra | 0.2 | tlp2_lp_cal | 60/60 | 0.935 | 0.935 | 3.361 | 4.58 | 0.531 | 0.000 | 0.379 |
| clean | 40 | extra | 0.2 | tlp2_db | 60/60 | 0.882 | 0.882 | 2.747 | 4.94 | 0.500 | 0.000 | 0.376 |
| clean | 40 | extra | 0.2 | tlp2_db90 | 60/60 | 0.823 | 0.823 | 2.285 | 5.64 | 0.500 | 0.000 | 0.376 |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.919 | 0.919 | 3.201 | 4.86 | 0.480 | 0.000 | 0.374 |
| clean | 40 | extra | 0.5 | targeted_lp | 60/60 | 0.888 | 0.888 | 2.924 | 4.94 | 0.537 | 0.000 | 0.389 |
| clean | 40 | extra | 0.5 | tlp2_lp_cal | 60/60 | 0.933 | 0.933 | 3.524 | 4.69 | 0.544 | 0.000 | 0.377 |
| clean | 40 | extra | 0.5 | tlp2_db | 60/60 | 0.885 | 0.885 | 2.833 | 4.96 | 0.541 | 0.000 | 0.364 |
| clean | 40 | extra | 0.5 | tlp2_db90 | 60/60 | 0.818 | 0.818 | 2.320 | 5.62 | 0.541 | 0.000 | 0.364 |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.983 | 0.983 | 6.601 | 7.77 | 0.816 | 0.000 | 0.475 |
| clean | 40 | missing | 0.2 | targeted_lp | 60/60 | 0.868 | 0.868 | 2.755 | 5.12 | 0.579 | 0.005 | 0.389 |
| clean | 40 | missing | 0.2 | tlp2_lp_cal | 60/60 | 0.965 | 0.965 | 4.075 | 4.86 | 0.589 | 0.005 | 0.394 |
| clean | 40 | missing | 0.2 | tlp2_db | 60/60 | 0.848 | 0.849 | 2.594 | 5.38 | 0.564 | 0.004 | 0.385 |
| clean | 40 | missing | 0.2 | tlp2_db90 | 60/60 | 0.778 | 0.780 | 2.121 | 6.28 | 0.564 | 0.004 | 0.385 |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.978 | 0.978 | 6.454 | 7.53 | 0.859 | 0.000 | 0.456 |
| clean | 40 | missing | 0.5 | targeted_lp | 60/60 | 0.828 | 0.827 | 2.635 | 5.82 | 0.627 | 0.028 | 0.532 |
| clean | 40 | missing | 0.5 | tlp2_lp_cal | 60/60 | 0.950 | 0.950 | 3.894 | 4.84 | 0.620 | 0.024 | 0.549 |
| clean | 40 | missing | 0.5 | tlp2_db | 60/60 | 0.793 | 0.794 | 2.415 | 6.47 | 0.604 | 0.027 | 0.558 |
| clean | 40 | missing | 0.5 | tlp2_db90 | 60/60 | 0.712 | 0.714 | 2.007 | 7.78 | 0.604 | 0.027 | 0.558 |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.109 | 4.78 | 0.462 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.2 | targeted_lp | 60/60 | 0.879 | 0.879 | 2.811 | 5.10 | 0.570 | 0.000 | 0.425 |
| clean | 40 | reversed | 0.2 | tlp2_lp_cal | 60/60 | 0.961 | 0.961 | 3.956 | 4.92 | 0.554 | 0.000 | 0.451 |
| clean | 40 | reversed | 0.2 | tlp2_db | 60/60 | 0.865 | 0.865 | 2.690 | 5.48 | 0.516 | 0.000 | 0.419 |
| clean | 40 | reversed | 0.2 | tlp2_db90 | 60/60 | 0.810 | 0.810 | 2.258 | 6.23 | 0.516 | 0.000 | 0.419 |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.921 | 0.921 | 3.210 | 4.78 | 0.502 | 0.000 | 0.391 |
| clean | 40 | reversed | 0.5 | targeted_lp | 60/60 | 0.871 | 0.871 | 2.929 | 5.75 | 0.601 | 0.000 | 0.479 |
| clean | 40 | reversed | 0.5 | tlp2_lp_cal | 60/60 | 0.956 | 0.956 | 4.154 | 5.31 | 0.598 | 0.000 | 0.478 |
| clean | 40 | reversed | 0.5 | tlp2_db | 60/60 | 0.866 | 0.866 | 2.803 | 5.97 | 0.593 | 0.000 | 0.445 |
| clean | 40 | reversed | 0.5 | tlp2_db90 | 60/60 | 0.792 | 0.792 | 2.293 | 6.94 | 0.593 | 0.000 | 0.445 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tlp2_lp_cal | tlp2_db | tlp2_db90 |
|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.39 [-0.81, +0.05] | -0.27 [-0.49, -0.05] | +0.13 [-0.07, +0.34] | +0.74 [+0.45, +1.06] |
| clean | 40 | extra | 0.2 | -0.18 [-0.65, +0.30] | -0.33 [-0.56, -0.11] | +0.03 [-0.10, +0.17] | +0.73 [+0.48, +1.00] |
| clean | 40 | extra | 0.5 | -0.08 [-0.54, +0.39] | -0.24 [-0.46, -0.04] | +0.02 [-0.13, +0.21] | +0.69 [+0.44, +1.00] |
| clean | 40 | missing | 0.2 | +2.65 [+2.02, +3.29] | -0.25 [-0.67, +0.15] | +0.27 [+0.15, +0.39] | +1.16 [+0.89, +1.44] |
| clean | 40 | missing | 0.5 | +1.71 [+1.04, +2.32] | -0.98 [-1.53, -0.50] | +0.66 [+0.40, +0.90] | +1.96 [+1.53, +2.42] |
| clean | 40 | reversed | 0.2 | -0.32 [-0.85, +0.28] | -0.18 [-0.64, +0.20] | +0.38 [+0.17, +0.58] | +1.12 [+0.74, +1.57] |
| clean | 40 | reversed | 0.5 | -0.97 [-1.48, -0.44] | -0.44 [-0.90, -0.06] | +0.23 [+0.02, +0.47] | +1.19 [+0.81, +1.65] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | targeted_lp | tlp2_lp_cal | tlp2_db | tlp2_db90 |
|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.39 [-0.05, +0.81] | +0.12 [-0.31, +0.53] | +0.51 [+0.19, +0.83] | +1.12 [+0.72, +1.53] |
| clean | 40 | extra | 0.2 | +0.18 [-0.30, +0.65] | -0.14 [-0.73, +0.36] | +0.22 [-0.27, +0.68] | +0.92 [+0.52, +1.35] |
| clean | 40 | extra | 0.5 | +0.08 [-0.39, +0.54] | -0.16 [-0.67, +0.28] | +0.10 [-0.28, +0.47] | +0.77 [+0.39, +1.13] |
| clean | 40 | missing | 0.2 | -2.65 [-3.29, -2.02] | -2.90 [-3.30, -2.59] | -2.38 [-3.01, -1.72] | -1.49 [-2.36, -0.62] |
| clean | 40 | missing | 0.5 | -1.71 [-2.32, -1.04] | -2.69 [-3.00, -2.37] | -1.06 [-1.72, -0.37] | +0.25 [-0.72, +1.29] |
| clean | 40 | reversed | 0.2 | +0.32 [-0.28, +0.85] | +0.14 [-0.49, +0.67] | +0.70 [+0.13, +1.17] | +1.45 [+0.83, +2.08] |
| clean | 40 | reversed | 0.5 | +0.97 [+0.44, +1.48] | +0.53 [+0.08, +0.96] | +1.19 [+0.59, +1.80] | +2.16 [+1.41, +2.89] |
