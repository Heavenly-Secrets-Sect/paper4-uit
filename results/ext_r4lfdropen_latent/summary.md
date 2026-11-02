# ext_r4lfdropen_latent

r4lfdropen no-harm check: latent1 x missing-0.2 at T 40/80/150 (+ none for identity), D-07 development, seed_base 20261102 (missing k_idx as ext_v51_a1). Factors frozen from results/ext_r4lfdropen_eval/calibration.json (run_driver.py --frozen-from). Rule in docs/ext/r4lfdropen.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.919 | 0.919 | 2.919 | 4.50 | 0.508 | 0.000 | 0.313 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.939 | 0.939 | 3.498 | 5.12 | 0.516 | 0.000 | 0.361 |
| latent1 | 40 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.955 | 0.955 | 4.419 | 5.78 | 0.537 | 0.000 | 0.360 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.953 | 0.953 | 2.418 | 3.15 | 0.364 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.953 | 0.953 | 2.489 | 3.31 | 0.345 | 0.000 | 0.202 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1 | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1_lfdr | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1 | 60/60 | 0.956 | 0.956 | 1.534 | 2.15 | 0.233 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1_lfdr | 60/60 | 0.944 | 0.944 | 1.482 | 2.22 | 0.237 | 0.000 | 0.166 |

## Interval score difference vs `tolerant_v5_1` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tolerant_v5_1_lfdr |
|---|---|---|---|---|
| latent1 | 40 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent1 | 40 | missing | 0.2 | +0.66 [+0.43, +0.88] |
| latent1 | 80 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent1 | 80 | missing | 0.2 | +0.16 [+0.09, +0.23] |
| latent1 | 150 | none | 0.0 | +0.00 [+0.00, +0.00] |
| latent1 | 150 | missing | 0.2 | +0.07 [-0.07, +0.21] |
