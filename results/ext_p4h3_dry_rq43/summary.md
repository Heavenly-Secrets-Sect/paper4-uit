# P4-H3 sealed confirmatory run of RQ4.3: analyzer output

Bank P4-H3 (development + confirmatory, 40 topologies), plugin, T = 2000, seed_base 90261103. Bootstrap: B = 2000 topology-cluster resamples, seed 90261103.

## Cell table (all 40 topologies)

| damage | lag | role | n pairs | clusters | median [95% CI] | share >0.2 | D-07 median | dev | con | ER | hub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missing | contemp. | on_path | 1630 | 40 | 0.933 [0.913, 0.946] | 0.81 | 0.929 | 0.938 (20) | 0.921 (20) | 0.932 (20) | 0.934 (20) |
| missing | contemp. | into_source | 422 | 39 | 0.092 [0.080, 0.105] | 0.18 | 0.097 | 0.094 (20) | 0.092 (19) | 0.092 (20) | 0.092 (19) |
| missing | contemp. | into_target | 898 | 40 | 0.035 [0.028, 0.042] | 0.11 | 0.034 | 0.035 (20) | 0.035 (20) | 0.029 (20) | 0.043 (20) |
| missing | contemp. | other | 12188 | 40 | 0.000 [0.000, 0.001] | 0.00 | 0.000 | 0.000 (20) | 0.000 (20) | 0.000 (20) | 0.001 (20) |
| missing | lagged | on_path | 4110 | 40 | 0.816 [0.619, 0.920] | 0.71 | 0.805 | 0.785 (20) | 0.840 (20) | 0.763 (20) | 0.909 (20) |
| missing | lagged | into_source | 1179 | 40 | 0.084 [0.073, 0.094] | 0.19 | 0.074 | 0.084 (20) | 0.084 (20) | 0.090 (20) | 0.067 (20) |
| missing | lagged | into_target | 2064 | 40 | 0.052 [0.045, 0.061] | 0.21 | 0.058 | 0.057 (20) | 0.046 (20) | 0.044 (20) | 0.083 (20) |
| missing | lagged | other | 29463 | 40 | 0.000 [0.000, 0.001] | 0.01 | 0.000 | 0.001 (20) | 0.000 (20) | 0.000 (20) | 0.001 (20) |
| reversed | contemp. | on_path | 1364 | 40 | 0.523 [0.500, 0.553] | 0.77 | 0.527 | 0.541 (20) | 0.509 (20) | 0.518 (20) | 0.537 (20) |
| reversed | contemp. | into_source | 357 | 39 | 0.121 [0.094, 0.158] | 0.36 | 0.141 | 0.107 (20) | 0.129 (19) | 0.093 (20) | 0.245 (19) |
| reversed | contemp. | into_target | 471 | 39 | 0.044 [0.035, 0.056] | 0.06 | 0.046 | 0.039 (19) | 0.046 (20) | 0.037 (20) | 0.057 (19) |
| reversed | contemp. | other | 9250 | 40 | 0.002 [0.001, 0.003] | 0.03 | 0.002 | 0.002 (20) | 0.002 (20) | 0.001 (20) | 0.005 (20) |

## (a) on_path at least 3x every other role

| row | role | ratio on_path / role | ok | one-sided boot p |
|---|---|---|---|---|
| missing contemporaneous | into_source | 10.1 | True | 0.0005 |
| missing contemporaneous | into_target | 26.7 | True | 0.0005 |
| missing contemporaneous | other | 2124.3 | True | 0.0005 |
| missing lagged | into_source | 9.7 | True | 0.0005 |
| missing lagged | into_target | 15.6 | True | 0.0005 |
| missing lagged | other | 1713.6 | True | 0.0005 |
| reversed contemporaneous | into_source | 4.3 | True | 0.0045 |
| reversed contemporaneous | into_target | 11.9 | True | 0.0005 |
| reversed contemporaneous | other | 267.0 | True | 0.0005 |

(a) pass = True

## (b) on_path median within +/-0.15 of D-07 (doc values)

| row | median [95% CI] | ref | diff | ok | TOST p |
|---|---|---|---|---|---|
| missing contemporaneous | 0.933 [0.913, 0.946] | 0.93 | +0.003 | True | 0.0005 |
| missing lagged | 0.816 [0.619, 0.920] | 0.81 | +0.006 | True | 0.0550 |
| reversed contemporaneous | 0.523 [0.500, 0.553] | 0.53 | -0.007 | True | 0.0005 |

(b) pass = True

## (c) stability and (d) transfer (Spearman over role-by-row median costs)

| comparison | rho | cells | 95% CI | share of draws >= 0.9 | ok |
|---|---|---|---|---|---|
| dev vs con | 0.993 | 12 | [0.965, 1.000] | 1.00 | True |
| ER vs hub | 0.993 | 12 | [0.902, 0.993] | 0.99 | True |
| P4-H3 vs D-07 | 1.000 | 12 | [0.986, 1.000] | 1.00 | True |

(c) pass = True; (d) pass = True

## Holm (alpha 0.05) over 12 one-sided bootstrap tests (a: 9, b: 3)

Rejected: 11/12 (a 9/9, b 2/3).

## Verdict: CONFIRMED on the sealed bank P4-H3

Criteria: {'a': True, 'b': True, 'c': True, 'd': True}
