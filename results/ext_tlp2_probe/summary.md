# ext_tlp2_probe

Design probe (D-07H development, 6 topologies, 1 replicate): round-1 single-level targeted_lp vs the faithful double bootstrap tlp2_db / tlp2_db90 (src/paper4/ext_tlp2.py). Sanity check before the rule in docs/ext/tlp2.md; not an evaluation.

Bank D-07H / development; 1 replicates per topology; H = 4, lag_max = 2, n_boot = 199, nominal coverage 0.95.

- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.
- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).
- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.

| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | targeted_lp | 6/6 | 0.920 | 0.920 | 2.649 | 4.47 | 0.367 | 0.000 | 0.279 |
| clean | 80 | none | 0.0 | tlp2_db | 6/6 | 0.900 | 0.900 | 2.584 | 5.11 | 0.403 | 0.000 | 0.260 |
| clean | 80 | none | 0.0 | tlp2_db90 | 6/6 | 0.836 | 0.836 | 1.946 | 5.99 | 0.403 | 0.000 | 0.260 |
| clean | 80 | extra | 0.5 | targeted_lp | 6/6 | 0.896 | 0.896 | 2.573 | 4.81 | 0.393 | 0.000 | 0.248 |
| clean | 80 | extra | 0.5 | tlp2_db | 6/6 | 0.891 | 0.891 | 2.604 | 4.90 | 0.429 | 0.000 | 0.250 |
| clean | 80 | extra | 0.5 | tlp2_db90 | 6/6 | 0.836 | 0.836 | 2.074 | 5.78 | 0.429 | 0.000 | 0.250 |
| clean | 80 | missing | 0.5 | targeted_lp | 6/6 | 0.866 | 0.864 | 2.732 | 5.45 | 0.490 | 0.050 | 0.463 |
| clean | 80 | missing | 0.5 | tlp2_db | 6/6 | 0.816 | 0.816 | 2.592 | 6.05 | 0.767 | 0.055 | 0.454 |
| clean | 80 | missing | 0.5 | tlp2_db90 | 6/6 | 0.687 | 0.689 | 2.090 | 8.47 | 0.767 | 0.055 | 0.454 |

## Interval score difference vs `targeted_lp` (negative = better), 95% CI clustered by topology

| scenario | T | damage | rate | tlp2_db | tlp2_db90 |
|---|---|---|---|---|---|
| clean | 80 | none | 0.0 | +0.64 [-0.26, +1.67] | +1.53 [+0.47, +2.69] |
| clean | 80 | extra | 0.5 | +0.09 [-1.31, +1.65] | +0.97 [-0.55, +2.53] |
| clean | 80 | missing | 0.5 | +0.60 [-1.02, +2.22] | +3.03 [+1.58, +5.02] |
