# P4-H3 sealed confirmatory run of RQ4.3: analyzer output

Bank P4-H3 (development + confirmatory, 40 topologies), plugin, T = 2000, seed_base 90261103. Bootstrap: B = 2000 topology-cluster resamples, seed 90261103.

## Cell table (all 40 topologies)

| damage | lag | role | n pairs | clusters | median [95% CI] | share >0.2 | D-07 median | dev | con | ER | hub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missing | contemp. | on_path | 1671 | 40 | 0.952 [0.929, 0.965] | 0.83 | 0.929 | 0.953 (20) | 0.949 (20) | 0.952 (20) | 0.949 (20) |
| missing | contemp. | into_source | 452 | 37 | 0.093 [0.072, 0.105] | 0.16 | 0.097 | 0.092 (17) | 0.095 (20) | 0.089 (19) | 0.095 (18) |
| missing | contemp. | into_target | 866 | 40 | 0.048 [0.042, 0.056] | 0.15 | 0.034 | 0.048 (20) | 0.048 (20) | 0.046 (20) | 0.054 (20) |
| missing | contemp. | other | 12598 | 40 | 0.000 [0.000, 0.001] | 0.00 | 0.000 | 0.001 (20) | 0.000 (20) | 0.000 (20) | 0.001 (20) |
| missing | lagged | on_path | 4162 | 40 | 0.844 [0.749, 0.895] | 0.75 | 0.805 | 0.887 (20) | 0.753 (20) | 0.850 (20) | 0.812 (20) |
| missing | lagged | into_source | 1270 | 40 | 0.080 [0.069, 0.093] | 0.19 | 0.074 | 0.089 (20) | 0.073 (20) | 0.091 (20) | 0.059 (20) |
| missing | lagged | into_target | 1976 | 40 | 0.065 [0.050, 0.084] | 0.23 | 0.058 | 0.053 (20) | 0.073 (20) | 0.054 (20) | 0.117 (20) |
| missing | lagged | other | 30198 | 40 | 0.000 [0.000, 0.001] | 0.01 | 0.000 | 0.000 (20) | 0.001 (20) | 0.000 (20) | 0.001 (20) |
| reversed | contemp. | on_path | 1454 | 40 | 0.541 [0.510, 0.574] | 0.78 | 0.527 | 0.534 (20) | 0.548 (20) | 0.543 (20) | 0.539 (20) |
| reversed | contemp. | into_source | 387 | 37 | 0.126 [0.096, 0.159] | 0.35 | 0.141 | 0.145 (17) | 0.111 (20) | 0.097 (19) | 0.248 (18) |
| reversed | contemp. | into_target | 514 | 39 | 0.053 [0.047, 0.058] | 0.11 | 0.046 | 0.053 (19) | 0.054 (20) | 0.053 (20) | 0.053 (19) |
| reversed | contemp. | other | 9761 | 40 | 0.002 [0.002, 0.004] | 0.04 | 0.002 | 0.003 (20) | 0.002 (20) | 0.001 (20) | 0.006 (20) |

## (a) on_path at least 3x every other role

| row | role | ratio on_path / role | ok | one-sided boot p |
|---|---|---|---|---|
| missing contemporaneous | into_source | 10.2 | True | 0.0005 |
| missing contemporaneous | into_target | 19.8 | True | 0.0005 |
| missing contemporaneous | other | 2018.0 | True | 0.0005 |
| missing lagged | into_source | 10.5 | True | 0.0005 |
| missing lagged | into_target | 13.0 | True | 0.0005 |
| missing lagged | other | 1696.0 | True | 0.0005 |
| reversed contemporaneous | into_source | 4.3 | True | 0.0050 |
| reversed contemporaneous | into_target | 10.2 | True | 0.0005 |
| reversed contemporaneous | other | 220.6 | True | 0.0005 |

(a) pass = True

## (b) on_path median within +/-0.15 of D-07 (doc values)

| row | median [95% CI] | ref | diff | ok | TOST p |
|---|---|---|---|---|---|
| missing contemporaneous | 0.952 [0.929, 0.965] | 0.93 | +0.022 | True | 0.0005 |
| missing lagged | 0.844 [0.749, 0.895] | 0.81 | +0.034 | True | 0.0005 |
| reversed contemporaneous | 0.541 [0.510, 0.574] | 0.53 | +0.011 | True | 0.0005 |

(b) pass = True

## (c) stability and (d) transfer (Spearman over role-by-row median costs)

| comparison | rho | cells | 95% CI | share of draws >= 0.9 | ok |
|---|---|---|---|---|---|
| dev vs con | 0.993 | 12 | [0.923, 0.993] | 1.00 | True |
| ER vs hub | 0.965 | 12 | [0.867, 0.979] | 0.86 | True |
| P4-H3 vs D-07 | 1.000 | 12 | [0.979, 1.000] | 1.00 | True |

(c) pass = True; (d) pass = True

## Holm (alpha 0.05) over 12 one-sided bootstrap tests (a: 9, b: 3)

Rejected: 12/12 (a 9/9, b 3/3).

## Verdict: CONFIRMED on the sealed bank P4-H3

Criteria: {'a': True, 'b': True, 'c': True, 'd': True}
