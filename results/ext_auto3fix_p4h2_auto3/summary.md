# ext_auto3fix_p4h2_auto3

FROZEN, NOT RUN. Confirmatory run of tolerant_auto3 on the sealed P4-H2 confirmatory split, corrected spec of round 3 (docs/ext/auto3fix.md, ID auto3fix). Identical to experiments/configs/ext_auto5_p4h2_auto3.json except name and purpose. Rule B1 C1-C3 + L1 unchanged; failed runs count as uncovered (experiments/ext/auto3fix/check_p4h2_v2.py). Run once, after python experiments/ext/auto3fix/preflight_p4h2.py: python experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3.json --workers 3; then the latent1 config; then python experiments/ext/auto3fix/check_p4h2_v2.py

Bank P4-H2 / confirmatory; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | plugin | 60/60 | 0.862 | 0.862 | 2.076 | 4.55 | 0.495 | 0.000 | 0.353 |
| clean | 40 | none | 0.0 | tolerant_v4 | 60/60 | 0.932 | 0.932 | 2.898 | 4.28 | 0.495 | 0.000 | 0.353 |
| clean | 40 | none | 0.0 | tolerant_auto3 | 60/60 | 0.955 | 0.955 | 3.538 | 4.76 | 0.513 | 0.000 | 0.367 |
| clean | 40 | extra | 0.2 | plugin | 60/60 | 0.867 | 0.867 | 2.178 | 4.54 | 0.500 | 0.000 | 0.366 |
| clean | 40 | extra | 0.2 | tolerant_v4 | 60/60 | 0.925 | 0.925 | 2.809 | 4.32 | 0.500 | 0.000 | 0.366 |
| clean | 40 | extra | 0.2 | tolerant_auto3 | 60/60 | 0.964 | 0.964 | 3.592 | 4.79 | 0.520 | 0.000 | 0.372 |
| clean | 40 | extra | 0.5 | plugin | 60/60 | 0.868 | 0.868 | 2.493 | 4.77 | 0.525 | 0.000 | 0.387 |
| clean | 40 | extra | 0.5 | tolerant_v4 | 60/60 | 0.942 | 0.942 | 3.211 | 4.53 | 0.525 | 0.000 | 0.387 |
| clean | 40 | extra | 0.5 | tolerant_auto3 | 60/60 | 0.971 | 0.971 | 4.138 | 5.58 | 0.576 | 0.000 | 0.394 |
| clean | 40 | missing | 0.2 | plugin | 60/60 | 0.677 | 0.716 | 1.852 | 11.04 | 0.595 | 0.055 | 0.383 |
| clean | 40 | missing | 0.2 | tolerant_v4 | 60/60 | 0.977 | 0.977 | 6.784 | 7.81 | 0.822 | 0.000 | 0.437 |
| clean | 40 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.948 | 0.961 | 6.100 | 8.09 | 0.715 | 0.014 | 0.476 |
| clean | 40 | missing | 0.5 | plugin | 60/60 | 0.339 | 0.592 | 1.797 | 28.28 | 0.873 | 0.428 | 0.397 |
| clean | 40 | missing | 0.5 | tolerant_v4 | 60/60 | 0.981 | 0.981 | 6.520 | 7.54 | 0.789 | 0.000 | 0.503 |
| clean | 40 | missing | 0.5 | tolerant_auto3 | 59/60 | 0.949 | 0.975 | 6.771 | 9.32 | 0.769 | 0.027 | 0.507 |
| clean | 40 | reversed | 0.2 | plugin | 60/60 | 0.839 | 0.839 | 2.057 | 5.06 | 0.499 | 0.000 | 0.354 |
| clean | 40 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.940 | 0.940 | 3.216 | 4.53 | 0.487 | 0.000 | 0.354 |
| clean | 40 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.947 | 0.947 | 3.446 | 4.79 | 0.515 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | plugin | 60/60 | 0.771 | 0.771 | 1.995 | 6.69 | 0.516 | 0.000 | 0.408 |
| clean | 40 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.922 | 0.922 | 3.263 | 5.01 | 0.492 | 0.000 | 0.408 |
| clean | 40 | reversed | 0.5 | tolerant_auto3 | 60/60 | 0.931 | 0.931 | 3.313 | 5.31 | 0.528 | 0.000 | 0.423 |
| clean | 40 | ges | 0.0 | plugin | 60/60 | 0.383 | 0.418 | 1.335 | 22.80 | 0.948 | 0.083 | 0.568 |
| clean | 40 | ges | 0.0 | tolerant_v4 | 60/60 | 0.979 | 0.979 | 7.111 | 9.19 | 0.797 | 0.000 | 0.499 |
| clean | 40 | ges | 0.0 | tolerant_auto3 | 59/60 | 0.899 | 0.905 | 6.669 | 11.04 | 0.860 | 0.006 | 0.462 |
| clean | 80 | none | 0.0 | plugin | 60/60 | 0.876 | 0.876 | 1.397 | 2.63 | 0.267 | 0.000 | 0.228 |
| clean | 80 | none | 0.0 | tolerant_v4 | 60/60 | 0.949 | 0.949 | 1.852 | 2.38 | 0.267 | 0.000 | 0.228 |
| clean | 80 | none | 0.0 | tolerant_auto3 | 60/60 | 0.963 | 0.963 | 2.028 | 2.57 | 0.278 | 0.000 | 0.243 |
| clean | 80 | extra | 0.2 | plugin | 60/60 | 0.878 | 0.878 | 1.436 | 2.71 | 0.278 | 0.000 | 0.224 |
| clean | 80 | extra | 0.2 | tolerant_v4 | 60/60 | 0.947 | 0.947 | 1.886 | 2.49 | 0.278 | 0.000 | 0.224 |
| clean | 80 | extra | 0.2 | tolerant_auto3 | 60/60 | 0.960 | 0.960 | 2.049 | 2.61 | 0.308 | 0.000 | 0.234 |
| clean | 80 | extra | 0.5 | plugin | 60/60 | 0.885 | 0.885 | 1.502 | 2.76 | 0.303 | 0.000 | 0.234 |
| clean | 80 | extra | 0.5 | tolerant_v4 | 60/60 | 0.954 | 0.954 | 1.964 | 2.55 | 0.303 | 0.000 | 0.234 |
| clean | 80 | extra | 0.5 | tolerant_auto3 | 60/60 | 0.963 | 0.963 | 2.104 | 2.66 | 0.310 | 0.000 | 0.234 |
| clean | 80 | missing | 0.2 | plugin | 60/60 | 0.655 | 0.693 | 1.300 | 10.68 | 0.422 | 0.055 | 0.252 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 60/60 | 0.974 | 0.974 | 2.685 | 3.13 | 0.405 | 0.000 | 0.302 |
| clean | 80 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.967 | 0.967 | 2.638 | 3.12 | 0.410 | 0.000 | 0.315 |
| clean | 80 | missing | 0.5 | plugin | 60/60 | 0.335 | 0.586 | 1.356 | 28.94 | 0.776 | 0.428 | 0.294 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 60/60 | 0.972 | 0.972 | 2.759 | 3.18 | 0.411 | 0.000 | 0.300 |
| clean | 80 | missing | 0.5 | tolerant_auto3 | 60/60 | 0.963 | 0.963 | 2.633 | 3.22 | 0.435 | 0.000 | 0.292 |
| clean | 80 | reversed | 0.2 | plugin | 60/60 | 0.830 | 0.830 | 1.410 | 3.93 | 0.317 | 0.000 | 0.251 |
| clean | 80 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.952 | 0.952 | 2.141 | 2.77 | 0.341 | 0.000 | 0.251 |
| clean | 80 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.946 | 0.946 | 2.075 | 2.87 | 0.346 | 0.000 | 0.271 |
| clean | 80 | reversed | 0.5 | plugin | 60/60 | 0.738 | 0.738 | 1.352 | 5.42 | 0.371 | 0.000 | 0.300 |
| clean | 80 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.946 | 0.946 | 2.141 | 2.90 | 0.338 | 0.000 | 0.300 |
| clean | 80 | reversed | 0.5 | tolerant_auto3 | 60/60 | 0.929 | 0.929 | 2.318 | 3.27 | 0.423 | 0.000 | 0.316 |
| clean | 80 | ges | 0.0 | plugin | 60/60 | 0.338 | 0.360 | 0.928 | 23.04 | 0.810 | 0.063 | 0.377 |
| clean | 80 | ges | 0.0 | tolerant_v4 | 60/60 | 0.953 | 0.953 | 2.799 | 3.58 | 0.456 | 0.000 | 0.284 |
| clean | 80 | ges | 0.0 | tolerant_auto3 | 60/60 | 0.939 | 0.939 | 2.571 | 3.39 | 0.434 | 0.000 | 0.287 |
| clean | 150 | none | 0.0 | plugin | 60/60 | 0.915 | 0.915 | 1.070 | 1.61 | 0.188 | 0.000 | 0.173 |
| clean | 150 | none | 0.0 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 1.291 | 1.56 | 0.188 | 0.000 | 0.173 |
| clean | 150 | none | 0.0 | tolerant_auto3 | 60/60 | 0.977 | 0.977 | 1.628 | 1.87 | 0.191 | 0.000 | 0.171 |
| clean | 150 | extra | 0.2 | plugin | 60/60 | 0.916 | 0.916 | 1.092 | 1.59 | 0.191 | 0.000 | 0.171 |
| clean | 150 | extra | 0.2 | tolerant_v4 | 60/60 | 0.961 | 0.961 | 1.278 | 1.57 | 0.191 | 0.000 | 0.171 |
| clean | 150 | extra | 0.2 | tolerant_auto3 | 60/60 | 0.982 | 0.982 | 1.579 | 1.84 | 0.191 | 0.000 | 0.169 |
| clean | 150 | extra | 0.5 | plugin | 60/60 | 0.914 | 0.914 | 1.144 | 1.67 | 0.201 | 0.000 | 0.184 |
| clean | 150 | extra | 0.5 | tolerant_v4 | 60/60 | 0.963 | 0.963 | 1.366 | 1.63 | 0.201 | 0.000 | 0.184 |
| clean | 150 | extra | 0.5 | tolerant_auto3 | 60/60 | 0.978 | 0.978 | 1.624 | 1.86 | 0.203 | 0.000 | 0.184 |
| clean | 150 | missing | 0.2 | plugin | 60/60 | 0.668 | 0.707 | 1.025 | 10.54 | 0.286 | 0.055 | 0.195 |
| clean | 150 | missing | 0.2 | tolerant_v4 | 60/60 | 0.965 | 0.965 | 1.661 | 1.98 | 0.254 | 0.000 | 0.190 |
| clean | 150 | missing | 0.2 | tolerant_auto3 | 60/60 | 0.981 | 0.981 | 1.999 | 2.25 | 0.269 | 0.000 | 0.200 |
| clean | 150 | missing | 0.5 | plugin | 60/60 | 0.325 | 0.569 | 0.986 | 29.25 | 0.716 | 0.428 | 0.208 |
| clean | 150 | missing | 0.5 | tolerant_v4 | 60/60 | 0.971 | 0.971 | 1.725 | 2.11 | 0.273 | 0.000 | 0.192 |
| clean | 150 | missing | 0.5 | tolerant_auto3 | 60/60 | 0.984 | 0.984 | 1.967 | 2.27 | 0.282 | 0.000 | 0.199 |
| clean | 150 | reversed | 0.2 | plugin | 60/60 | 0.826 | 0.826 | 1.061 | 2.92 | 0.236 | 0.000 | 0.189 |
| clean | 150 | reversed | 0.2 | tolerant_v4 | 60/60 | 0.967 | 0.967 | 1.536 | 1.88 | 0.232 | 0.000 | 0.189 |
| clean | 150 | reversed | 0.2 | tolerant_auto3 | 60/60 | 0.973 | 0.973 | 1.765 | 2.02 | 0.254 | 0.000 | 0.203 |
| clean | 150 | reversed | 0.5 | plugin | 60/60 | 0.717 | 0.717 | 1.068 | 5.35 | 0.279 | 0.000 | 0.217 |
| clean | 150 | reversed | 0.5 | tolerant_v4 | 60/60 | 0.953 | 0.953 | 1.552 | 2.00 | 0.252 | 0.000 | 0.217 |
| clean | 150 | reversed | 0.5 | tolerant_auto3 | 60/60 | 0.956 | 0.956 | 1.951 | 2.37 | 0.306 | 0.000 | 0.231 |
| clean | 150 | ges | 0.0 | plugin | 60/60 | 0.320 | 0.332 | 0.727 | 21.72 | 0.707 | 0.038 | 0.333 |
| clean | 150 | ges | 0.0 | tolerant_v4 | 60/60 | 0.931 | 0.931 | 1.790 | 2.74 | 0.337 | 0.000 | 0.213 |
| clean | 150 | ges | 0.0 | tolerant_auto3 | 60/60 | 0.951 | 0.951 | 1.920 | 2.64 | 0.307 | 0.000 | 0.217 |

## Interval score difference vs `plugin` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v4 | tolerant_auto3 |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | -0.27 [-0.56, -0.06] | +0.21 [-0.26, +0.64] |
| clean | 40 | extra | 0.2 | -0.22 [-0.39, -0.04] | +0.25 [-0.12, +0.66] |
| clean | 40 | extra | 0.5 | -0.23 [-0.44, -0.02] | +0.82 [+0.31, +1.32] |
| clean | 40 | missing | 0.2 | -3.23 [-4.10, -2.37] | -2.95 [-3.68, -2.28] |
| clean | 40 | missing | 0.5 | -20.74 [-22.15, -19.62] | -18.61 [-20.02, -17.03] |
| clean | 40 | reversed | 0.2 | -0.53 [-0.81, -0.27] | -0.27 [-0.60, +0.10] |
| clean | 40 | reversed | 0.5 | -1.68 [-2.28, -1.13] | -1.38 [-2.03, -0.83] |
| clean | 40 | ges | 0.0 | -13.61 [-16.49, -10.58] | -11.69 [-15.20, -8.36] |
| clean | 80 | none | 0.0 | -0.25 [-0.46, -0.06] | -0.06 [-0.27, +0.14] |
| clean | 80 | extra | 0.2 | -0.22 [-0.41, -0.05] | -0.09 [-0.28, +0.08] |
| clean | 80 | extra | 0.5 | -0.21 [-0.41, -0.04] | -0.09 [-0.30, +0.09] |
| clean | 80 | missing | 0.2 | -7.55 [-8.45, -6.62] | -7.56 [-8.46, -6.72] |
| clean | 80 | missing | 0.5 | -25.76 [-27.26, -24.39] | -25.72 [-27.21, -24.42] |
| clean | 80 | reversed | 0.2 | -1.16 [-1.63, -0.72] | -1.06 [-1.62, -0.65] |
| clean | 80 | reversed | 0.5 | -2.52 [-3.13, -1.89] | -2.14 [-2.78, -1.56] |
| clean | 80 | ges | 0.0 | -19.47 [-22.03, -16.97] | -19.65 [-21.92, -17.33] |
| clean | 150 | none | 0.0 | -0.05 [-0.16, +0.03] | +0.26 [+0.11, +0.40] |
| clean | 150 | extra | 0.2 | -0.02 [-0.13, +0.07] | +0.25 [+0.11, +0.38] |
| clean | 150 | extra | 0.5 | -0.04 [-0.13, +0.04] | +0.19 [+0.07, +0.30] |
| clean | 150 | missing | 0.2 | -8.56 [-9.42, -7.74] | -8.29 [-9.12, -7.45] |
| clean | 150 | missing | 0.5 | -27.14 [-28.59, -26.06] | -26.98 [-28.34, -25.85] |
| clean | 150 | reversed | 0.2 | -1.04 [-1.30, -0.81] | -0.90 [-1.13, -0.67] |
| clean | 150 | reversed | 0.5 | -3.35 [-3.95, -2.80] | -2.99 [-3.55, -2.38] |
| clean | 150 | ges | 0.0 | -18.98 [-20.97, -17.09] | -19.08 [-20.93, -17.28] |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | plugin | tolerant_auto3 |
|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | +0.27 [+0.06, +0.56] | +0.48 [+0.20, +0.77] |
| clean | 40 | extra | 0.2 | +0.22 [+0.04, +0.39] | +0.47 [+0.17, +0.78] |
| clean | 40 | extra | 0.5 | +0.23 [+0.02, +0.44] | +1.05 [+0.65, +1.49] |
| clean | 40 | missing | 0.2 | +3.23 [+2.37, +4.10] | +0.27 [-0.05, +0.60] |
| clean | 40 | missing | 0.5 | +20.74 [+19.62, +22.15] | +1.90 [+0.74, +3.34] |
| clean | 40 | reversed | 0.2 | +0.53 [+0.27, +0.81] | +0.27 [+0.11, +0.43] |
| clean | 40 | reversed | 0.5 | +1.68 [+1.13, +2.28] | +0.30 [-0.18, +0.89] |
| clean | 40 | ges | 0.0 | +13.61 [+10.58, +16.49] | +1.85 [+0.20, +3.88] |
| clean | 80 | none | 0.0 | +0.25 [+0.06, +0.46] | +0.19 [+0.12, +0.27] |
| clean | 80 | extra | 0.2 | +0.22 [+0.05, +0.41] | +0.13 [+0.05, +0.20] |
| clean | 80 | extra | 0.5 | +0.21 [+0.04, +0.41] | +0.12 [+0.05, +0.20] |
| clean | 80 | missing | 0.2 | +7.55 [+6.62, +8.45] | -0.01 [-0.07, +0.05] |
| clean | 80 | missing | 0.5 | +25.76 [+24.39, +27.26] | +0.04 [-0.05, +0.14] |
| clean | 80 | reversed | 0.2 | +1.16 [+0.72, +1.63] | +0.10 [+0.01, +0.20] |
| clean | 80 | reversed | 0.5 | +2.52 [+1.89, +3.13] | +0.37 [+0.21, +0.55] |
| clean | 80 | ges | 0.0 | +19.47 [+16.97, +22.03] | -0.18 [-0.37, +0.01] |
| clean | 150 | none | 0.0 | +0.05 [-0.03, +0.16] | +0.31 [+0.23, +0.39] |
| clean | 150 | extra | 0.2 | +0.02 [-0.07, +0.13] | +0.27 [+0.22, +0.33] |
| clean | 150 | extra | 0.5 | +0.04 [-0.04, +0.13] | +0.24 [+0.19, +0.28] |
| clean | 150 | missing | 0.2 | +8.56 [+7.74, +9.42] | +0.27 [+0.21, +0.32] |
| clean | 150 | missing | 0.5 | +27.14 [+26.06, +28.59] | +0.16 [+0.09, +0.22] |
| clean | 150 | reversed | 0.2 | +1.04 [+0.81, +1.30] | +0.14 [+0.06, +0.21] |
| clean | 150 | reversed | 0.5 | +3.35 [+2.80, +3.95] | +0.37 [+0.25, +0.50] |
| clean | 150 | ges | 0.0 | +18.98 [+17.09, +20.97] | -0.10 [-0.32, +0.06] |
