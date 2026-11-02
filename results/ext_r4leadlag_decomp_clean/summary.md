# ext_r4leadlag_decomp_clean

r4leadlag POST HOC descriptive decomposition: A and D with tolerant_v5_1's frozen width factors, clean grid at T 150 (same seeds/cells as ext_r4leadlag_eval_clean); paired with that run's tolerant_v5_1 rows. Not part of the pre-registered rule.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 150 | none | 0.0 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | none | 0.0 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.264 | 1.57 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.338 | 1.60 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | extra | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.963 | 0.963 | 1.371 | 1.68 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.966 | 0.966 | 1.456 | 1.76 | 0.213 | 0.000 | 0.173 |
| clean | 150 | missing | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.967 | 0.967 | 1.475 | 1.76 | 0.219 | 0.000 | 0.176 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.969 | 0.969 | 1.596 | 1.99 | 0.242 | 0.000 | 0.175 |
| clean | 150 | missing | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.964 | 0.964 | 1.558 | 2.02 | 0.245 | 0.000 | 0.177 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_leadlag | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.2 | tolerant_v5_1_leadlag_skel | 60/60 | 0.959 | 0.959 | 1.444 | 1.83 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_leadlag | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
| clean | 150 | reversed | 0.5 | tolerant_v5_1_leadlag_skel | 60/60 | 0.943 | 0.943 | 1.491 | 2.03 | 0.248 | 0.000 | 0.214 |
