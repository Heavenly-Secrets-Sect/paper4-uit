# ext_r4levboot_gw

Round 4 levboot, arm W3 (recursive-design wild bootstrap, Rademacher, HC3-type transform) on grid G, same data seeds as ext_r4levboot_g / ext_v51_eval; its tolerant_v5_1 comparator rows come from ext_r4levboot_g (paired by unit). Split from ext_r4levboot_g only for runtime (< 30 min per run). Rule in docs/ext/r4levboot.md.

Bank D-07 / development; 3 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 40 | none | 0.0 | r4levboot_W3 | 60/60 | 0.929 | 0.929 | 3.108 | 4.76 | 0.429 | 0.000 | 0.327 |
| clean | 40 | extra | 0.2 | r4levboot_W3 | 60/60 | 0.926 | 0.926 | 3.219 | 5.00 | 0.462 | 0.000 | 0.365 |
| clean | 40 | extra | 0.5 | r4levboot_W3 | 60/60 | 0.936 | 0.936 | 3.487 | 5.10 | 0.480 | 0.000 | 0.374 |
| clean | 40 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.930 | 0.930 | 3.387 | 5.07 | 0.559 | 0.000 | 0.382 |
| clean | 40 | missing | 0.5 | r4levboot_W3 | 60/60 | 0.947 | 0.947 | 3.944 | 5.49 | 0.554 | 0.000 | 0.401 |
| clean | 40 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.936 | 0.936 | 3.382 | 5.05 | 0.453 | 0.000 | 0.358 |
| clean | 40 | reversed | 0.5 | r4levboot_W3 | 60/60 | 0.923 | 0.923 | 3.332 | 5.08 | 0.507 | 0.000 | 0.391 |
| clean | 80 | none | 0.0 | r4levboot_W3 | 60/60 | 0.926 | 0.926 | 1.740 | 2.60 | 0.296 | 0.000 | 0.237 |
| clean | 80 | extra | 0.2 | r4levboot_W3 | 60/60 | 0.933 | 0.933 | 1.816 | 2.59 | 0.300 | 0.000 | 0.247 |
| clean | 80 | extra | 0.5 | r4levboot_W3 | 60/60 | 0.931 | 0.931 | 1.934 | 2.72 | 0.339 | 0.000 | 0.253 |
| clean | 80 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.950 | 0.950 | 2.235 | 2.96 | 0.354 | 0.000 | 0.229 |
| clean | 80 | missing | 0.5 | r4levboot_W3 | 60/60 | 0.954 | 0.954 | 2.438 | 3.27 | 0.361 | 0.000 | 0.264 |
| clean | 80 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.946 | 0.946 | 2.047 | 2.86 | 0.345 | 0.000 | 0.228 |
| clean | 80 | reversed | 0.5 | r4levboot_W3 | 60/60 | 0.924 | 0.924 | 2.118 | 3.08 | 0.350 | 0.000 | 0.262 |
| clean | 150 | none | 0.0 | r4levboot_W3 | 60/60 | 0.967 | 0.967 | 1.333 | 1.62 | 0.191 | 0.000 | 0.170 |
| clean | 150 | extra | 0.2 | r4levboot_W3 | 60/60 | 0.970 | 0.970 | 1.367 | 1.63 | 0.200 | 0.000 | 0.170 |
| clean | 150 | extra | 0.5 | r4levboot_W3 | 60/60 | 0.965 | 0.965 | 1.442 | 1.71 | 0.208 | 0.000 | 0.187 |
| clean | 150 | missing | 0.2 | r4levboot_W3 | 60/60 | 0.971 | 0.971 | 1.511 | 1.81 | 0.209 | 0.000 | 0.173 |
| clean | 150 | missing | 0.5 | r4levboot_W3 | 60/60 | 0.976 | 0.976 | 1.631 | 2.06 | 0.241 | 0.000 | 0.175 |
| clean | 150 | reversed | 0.2 | r4levboot_W3 | 60/60 | 0.965 | 0.965 | 1.551 | 1.94 | 0.217 | 0.000 | 0.179 |
| clean | 150 | reversed | 0.5 | r4levboot_W3 | 60/60 | 0.951 | 0.951 | 1.540 | 2.07 | 0.254 | 0.000 | 0.214 |
