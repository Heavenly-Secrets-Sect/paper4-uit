# ext_r4leadlag_decomp_latent

r4leadlag POST HOC descriptive decomposition: A and D with tolerant_v5_1's frozen width factors (gate effect only), latent1/latent3 x missing-0.2/0.5 x T 80/150, same seeds as ext_r4leadlag_eval_latent; paired with that run's tolerant_v5_1 rows. Not part of the pre-registered rule.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latent1 | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.929 | 0.929 | 1.917 | 2.81 | 0.299 | 0.000 | 0.222 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.951 | 0.951 | 2.438 | 3.14 | 0.361 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.949 | 0.949 | 2.374 | 3.19 | 0.355 | 0.000 | 0.226 |
| latent1 | 80 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.956 | 0.956 | 2.668 | 3.50 | 0.393 | 0.000 | 0.229 |
| latent1 | 80 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.951 | 0.951 | 2.622 | 3.57 | 0.392 | 0.000 | 0.230 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.926 | 0.926 | 1.342 | 2.01 | 0.214 | 0.000 | 0.174 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.956 | 0.956 | 1.537 | 2.16 | 0.235 | 0.000 | 0.185 |
| latent1 | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.949 | 0.949 | 1.519 | 2.17 | 0.241 | 0.000 | 0.188 |
| latent1 | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.955 | 0.955 | 1.655 | 2.39 | 0.256 | 0.000 | 0.183 |
| latent1 | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.951 | 0.951 | 1.619 | 2.41 | 0.270 | 0.000 | 0.202 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.947 | 0.947 | 2.056 | 2.76 | 0.348 | 0.000 | 0.204 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.962 | 0.962 | 2.560 | 3.19 | 0.371 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.962 | 0.962 | 2.585 | 3.18 | 0.374 | 0.000 | 0.240 |
| latent3 | 80 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.969 | 0.969 | 2.763 | 3.59 | 0.402 | 0.000 | 0.249 |
| latent3 | 80 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.965 | 0.965 | 2.710 | 3.53 | 0.403 | 0.000 | 0.251 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.875 | 0.875 | 1.450 | 2.97 | 0.292 | 0.000 | 0.171 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.915 | 0.915 | 1.733 | 2.87 | 0.273 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.918 | 0.918 | 1.681 | 2.86 | 0.275 | 0.000 | 0.177 |
| latent3 | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.934 | 0.934 | 1.822 | 2.88 | 0.297 | 0.000 | 0.211 |
| latent3 | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.928 | 0.928 | 1.835 | 2.85 | 0.302 | 0.000 | 0.208 |
