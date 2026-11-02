# ext_verify2_baselines2/fidelity2

skeptic D-07H probe (verify2_baselines2)

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | tolerant_v4 | 20/20 | 0.934 | 0.934 | 1.792 | 2.45 | 0.294 | 0.000 | 0.249 |
| clean | 80 | none | 0.0 | pselect_union_v2 | 20/20 | 0.894 | 0.902 | 2.138 | 3.84 | 0.465 | 0.048 | 0.284 |
| clean | 80 | none | 0.0 | pselect_union_v2_cal | 20/20 | 0.949 | 0.953 | 2.993 | 3.92 | 0.465 | 0.048 | 0.284 |
| clean | 80 | none | 0.0 | psel_v2_hifi | 20/20 | 0.959 | 0.966 | 2.751 | 3.38 | 0.469 | 0.048 | 0.283 |
| clean | 80 | none | 0.0 | psel_v2_hifi_cal | 20/20 | 0.959 | 0.966 | 2.751 | 3.38 | 0.469 | 0.048 | 0.283 |
| clean | 80 | missing | 0.2 | tolerant_v4 | 20/20 | 0.964 | 0.964 | 2.729 | 3.29 | 0.410 | 0.000 | 0.286 |
| clean | 80 | missing | 0.2 | pselect_union_v2 | 20/20 | 0.884 | 0.911 | 2.211 | 4.69 | 0.482 | 0.077 | 0.276 |
| clean | 80 | missing | 0.2 | pselect_union_v2_cal | 20/20 | 0.939 | 0.959 | 3.095 | 4.60 | 0.482 | 0.077 | 0.276 |
| clean | 80 | missing | 0.2 | psel_v2_hifi | 20/20 | 0.971 | 0.982 | 2.752 | 3.39 | 0.463 | 0.077 | 0.285 |
| clean | 80 | missing | 0.2 | psel_v2_hifi_cal | 20/20 | 0.971 | 0.982 | 2.752 | 3.39 | 0.463 | 0.077 | 0.285 |
| clean | 80 | missing | 0.5 | tolerant_v4 | 20/20 | 0.961 | 0.961 | 2.770 | 3.30 | 0.420 | 0.000 | 0.293 |
| clean | 80 | missing | 0.5 | pselect_union_v2 | 20/20 | 0.879 | 0.901 | 2.349 | 4.98 | 0.549 | 0.051 | 0.243 |
| clean | 80 | missing | 0.5 | pselect_union_v2_cal | 20/20 | 0.927 | 0.944 | 3.288 | 4.84 | 0.549 | 0.051 | 0.243 |
| clean | 80 | missing | 0.5 | psel_v2_hifi | 20/20 | 0.957 | 0.969 | 2.855 | 3.62 | 0.556 | 0.051 | 0.269 |
| clean | 80 | missing | 0.5 | psel_v2_hifi_cal | 20/20 | 0.957 | 0.969 | 2.855 | 3.62 | 0.556 | 0.051 | 0.269 |

## Interval score difference vs `tolerant_v4` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | pselect_union_v2 | pselect_union_v2_cal | psel_v2_hifi | psel_v2_hifi_cal |
|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | +1.39 [+0.98, +1.76] | +1.47 [+1.03, +1.87] | +0.93 [+0.58, +1.31] | +0.93 [+0.58, +1.29] |
| clean | 80 | missing | 0.2 | +1.40 [+0.39, +2.54] | +1.31 [+0.51, +2.21] | +0.10 [-0.18, +0.37] | +0.10 [-0.17, +0.38] |
| clean | 80 | missing | 0.5 | +1.68 [+0.82, +2.82] | +1.53 [+0.88, +2.27] | +0.32 [+0.00, +0.69] | +0.32 [+0.00, +0.66] |
