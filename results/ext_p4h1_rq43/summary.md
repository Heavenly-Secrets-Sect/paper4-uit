# P4-H1 replication of RQ4.3: analyzer output

Bank P4-H1 (development + confirmatory, 40 topologies), plugin, T = 2000, seed_base 80261102. Bootstrap: B = 2000 topology-cluster resamples, seed 80261102.

## Cell table (all 40 topologies)

| damage | lag | role | n pairs | clusters | median [95% CI] | share >0.2 | D-07 median | dev | con | ER | hub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missing | contemp. | on_path | 1789 | 40 | 0.935 [0.882, 0.964] | 0.79 | 0.929 | 0.948 (20) | 0.918 (20) | 0.935 (20) | 0.936 (20) |
| missing | contemp. | into_source | 487 | 37 | 0.112 [0.094, 0.143] | 0.25 | 0.097 | 0.135 (19) | 0.097 (18) | 0.122 (20) | 0.087 (17) |
| missing | contemp. | into_target | 876 | 40 | 0.043 [0.035, 0.052] | 0.16 | 0.034 | 0.042 (20) | 0.045 (20) | 0.044 (20) | 0.040 (20) |
| missing | contemp. | other | 12346 | 40 | 0.000 [0.000, 0.001] | 0.01 | 0.000 | 0.001 (20) | 0.000 (20) | 0.000 (20) | 0.001 (20) |
| missing | lagged | on_path | 3979 | 40 | 0.854 [0.756, 0.908] | 0.74 | 0.805 | 0.797 (20) | 0.897 (20) | 0.834 (20) | 0.903 (20) |
| missing | lagged | into_source | 1104 | 40 | 0.077 [0.063, 0.091] | 0.16 | 0.074 | 0.086 (20) | 0.065 (20) | 0.086 (20) | 0.054 (20) |
| missing | lagged | into_target | 2079 | 40 | 0.049 [0.041, 0.058] | 0.21 | 0.058 | 0.049 (20) | 0.050 (20) | 0.044 (20) | 0.077 (20) |
| missing | lagged | other | 29441 | 40 | 0.000 [0.000, 0.001] | 0.01 | 0.000 | 0.001 (20) | 0.000 (20) | 0.000 (20) | 0.001 (20) |
| reversed | contemp. | on_path | 1482 | 40 | 0.528 [0.498, 0.566] | 0.77 | 0.527 | 0.530 (20) | 0.523 (20) | 0.521 (20) | 0.550 (20) |
| reversed | contemp. | into_source | 426 | 37 | 0.167 [0.127, 0.237] | 0.45 | 0.141 | 0.155 (19) | 0.186 (18) | 0.147 (20) | 0.295 (17) |
| reversed | contemp. | into_target | 464 | 39 | 0.062 [0.051, 0.077] | 0.11 | 0.046 | 0.062 (19) | 0.063 (20) | 0.062 (20) | 0.063 (19) |
| reversed | contemp. | other | 9469 | 40 | 0.002 [0.002, 0.003] | 0.04 | 0.002 | 0.002 (20) | 0.002 (20) | 0.001 (20) | 0.004 (20) |

## (a) on_path at least 3x every other role

| row | role | ratio on_path / role | ok | one-sided boot p |
|---|---|---|---|---|
| missing contemporaneous | into_source | 8.4 | True | 0.0005 |
| missing contemporaneous | into_target | 21.7 | True | 0.0005 |
| missing contemporaneous | other | 1952.5 | True | 0.0005 |
| missing lagged | into_source | 11.1 | True | 0.0005 |
| missing lagged | into_target | 17.4 | True | 0.0005 |
| missing lagged | other | 1856.6 | True | 0.0005 |
| reversed contemporaneous | into_source | 3.2 | True | 0.3483 |
| reversed contemporaneous | into_target | 8.5 | True | 0.0005 |
| reversed contemporaneous | other | 242.0 | True | 0.0005 |

(a) pass = True

## (b) on_path median within +/-0.15 of D-07 (doc values)

| row | median [95% CI] | ref | diff | ok | TOST p |
|---|---|---|---|---|---|
| missing contemporaneous | 0.935 [0.882, 0.964] | 0.93 | +0.005 | True | 0.0005 |
| missing lagged | 0.854 [0.756, 0.908] | 0.81 | +0.044 | True | 0.0005 |
| reversed contemporaneous | 0.528 [0.498, 0.566] | 0.53 | -0.002 | True | 0.0005 |

(b) pass = True

## (c) stability and (d) transfer (Spearman over role-by-row median costs)

| comparison | rho | cells | 95% CI | share of draws >= 0.9 | ok |
|---|---|---|---|---|---|
| dev vs con | 1.000 | 12 | [0.951, 1.000] | 1.00 | True |
| ER vs hub | 0.965 | 12 | [0.902, 0.986] | 0.98 | True |
| P4-H1 vs D-07 | 0.986 | 12 | [0.965, 1.000] | 1.00 | True |

(c) pass = True; (d) pass = True

## Holm (alpha 0.05) over 12 one-sided bootstrap tests (a: 9, b: 3)

Rejected: 11/12 (a 8/9, b 3/3).

## Verdict: REPLICATES

Criteria: {'a': True, 'b': True, 'c': True, 'd': True}
