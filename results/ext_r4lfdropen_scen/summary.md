# ext_r4lfdropen_scen

r4lfdropen secondary (descriptive, not ruling): latent3, measurement noise 0.1 and 0.3 x missing-0.2 at T 40/80/150, D-07 development, seed_base 20261102. Factors frozen from results/ext_r4lfdropen_eval/calibration.json.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent3 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.914 | 0.914 | 2.882 | 4.77 | 0.497 | 0.000 | 0.322 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.930 | 0.930 | 3.707 | 5.24 | 0.569 | 0.000 | 0.365 |
| latent3 | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.962 | 0.962 | 4.570 | 5.93 | 0.519 | 0.000 | 0.299 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.961 | 0.961 | 2.531 | 3.21 | 0.372 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.965 | 0.965 | 2.734 | 3.47 | 0.370 | 0.000 | 0.235 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.717 | 2.86 | 0.274 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.907 | 0.907 | 1.647 | 2.96 | 0.274 | 0.000 | 0.173 |
| noise0.1 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 2.787 | 4.82 | 0.471 | 0.000 | 0.402 |
| noise0.1 | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.895 | 0.895 | 2.787 | 4.82 | 0.471 | 0.000 | 0.402 |
| noise0.1 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.900 | 0.900 | 3.259 | 5.32 | 0.560 | 0.000 | 0.424 |
| noise0.1 | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.936 | 0.936 | 4.160 | 5.81 | 0.563 | 0.000 | 0.408 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.895 | 0.895 | 1.805 | 2.95 | 0.336 | 0.000 | 0.260 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 2.152 | 3.26 | 0.420 | 0.000 | 0.290 |
| noise0.1 | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.917 | 0.917 | 2.309 | 3.58 | 0.415 | 0.000 | 0.267 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.921 | 0.921 | 1.252 | 1.91 | 0.224 | 0.000 | 0.211 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.916 | 0.916 | 1.397 | 2.24 | 0.265 | 0.000 | 0.218 |
| noise0.1 | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.910 | 0.910 | 1.408 | 2.29 | 0.253 | 0.000 | 0.220 |
| noise0.3 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.848 | 0.848 | 2.692 | 5.66 | 0.574 | 0.000 | 0.472 |
| noise0.3 | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.848 | 0.848 | 2.692 | 5.66 | 0.574 | 0.000 | 0.472 |
| noise0.3 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.850 | 0.850 | 3.235 | 6.20 | 0.676 | 0.000 | 0.517 |
| noise0.3 | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.909 | 0.909 | 4.037 | 6.18 | 0.676 | 0.000 | 0.501 |
| noise0.3 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.810 | 0.810 | 1.809 | 4.12 | 0.414 | 0.000 | 0.311 |
| noise0.3 | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.810 | 0.810 | 1.809 | 4.12 | 0.414 | 0.000 | 0.311 |
| noise0.3 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.848 | 0.848 | 2.112 | 4.26 | 0.520 | 0.000 | 0.372 |
| noise0.3 | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.841 | 0.841 | 2.239 | 4.83 | 0.522 | 0.000 | 0.331 |
| noise0.3 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.777 | 0.777 | 1.243 | 3.41 | 0.343 | 0.000 | 0.271 |
| noise0.3 | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.777 | 0.777 | 1.243 | 3.41 | 0.343 | 0.000 | 0.271 |
| noise0.3 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.788 | 0.788 | 1.382 | 3.72 | 0.403 | 0.000 | 0.268 |
| noise0.3 | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.767 | 0.767 | 1.317 | 4.10 | 0.391 | 0.000 | 0.266 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1_lfdr |
|---|---|---|---|---|
| latent3 | 40 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent3 | 40 | missing | 0.2 | +0.69 [+0.39, +0.96] |
| latent3 | 80 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent3 | 80 | missing | 0.2 | +0.26 [+0.07, +0.46] |
| latent3 | 150 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent3 | 150 | missing | 0.2 | +0.09 [-0.04, +0.20] |
| noise0.1 | 40 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.1 | 40 | missing | 0.2 | +0.49 [+0.26, +0.72] |
| noise0.1 | 80 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.1 | 80 | missing | 0.2 | +0.32 [+0.16, +0.50] |
| noise0.1 | 150 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.1 | 150 | missing | 0.2 | +0.04 [-0.09, +0.17] |
| noise0.3 | 40 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.3 | 40 | missing | 0.2 | -0.02 [-0.46, +0.37] |
| noise0.3 | 80 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.3 | 80 | missing | 0.2 | +0.57 [+0.29, +0.89] |
| noise0.3 | 150 | none | 0.0 | +0.00 [+0.00, +0.00] |
| noise0.3 | 150 | missing | 0.2 | +0.37 [+0.16, +0.59] |
