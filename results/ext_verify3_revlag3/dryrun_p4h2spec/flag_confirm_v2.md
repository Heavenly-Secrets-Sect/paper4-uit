# Frozen RQ4.4 flag, corrected confirmatory check (v2) on ext_verify3_revlag3/dryrun_p4h2spec

Failed tolerant_v4 runs: {'T80/150': {'n_runs': 84, 'n_failed': 0, 'statuses': {}, 'share': 0.0}, 'T40': {'n_runs': 42, 'n_failed': 0, 'statuses': {}, 'share': 0.0}} -> ok

| tập | n | miss | AUROC(p_hat) [CI] | AUROC(rel_width) [CI] | AUROC(1/width) [CI] | p_hat − rel_width [CI] | p_hat − 1/width [CI] | flagged | miss cờ / không cờ | ratio [CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| T80/150 (7 cell) | 2814 | 0.043 | 0.643 [0.488, 0.780] | 0.667 [0.564, 0.771] | 0.566 [0.444, 0.682] | -0.024 [-0.167, +0.103] | +0.076 [+0.023, +0.139] | 0.088 | 0.120 / 0.036 | 3.36 [0.88, 6.45] |
| T40 (7 cell) | 1407 | 0.035 | 0.832 [0.691, 0.916] | 0.563 [0.455, 0.730] | 0.814 [0.654, 0.917] | +0.269 [+0.073, +0.364] | +0.019 [-0.003, +0.054] | 0.171 | 0.129 / 0.015 | 8.37 [2.17, 22.32] |

Sensitivity (round-2 encoding of stated, not ruled):

| tập | n | miss | AUROC(p_hat) [CI] | AUROC(rel_width) [CI] | AUROC(1/width) [CI] | p_hat − rel_width [CI] | p_hat − 1/width [CI] | flagged | miss cờ / không cờ | ratio [CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| sensitivity: round-2 encoding, T80/150 | 2814 | 0.043 | 0.643 [0.488, 0.780] | 0.667 [0.564, 0.771] | 0.566 [0.444, 0.682] | -0.024 [-0.167, +0.103] | +0.076 [+0.023, +0.139] | 0.088 | 0.120 / 0.036 | 3.36 [0.88, 6.45] |
| sensitivity: round-2 encoding, T40 | 1407 | 0.035 | 0.832 [0.691, 0.916] | 0.563 [0.455, 0.730] | 0.814 [0.654, 0.917] | +0.269 [+0.073, +0.364] | +0.019 [-0.003, +0.054] | 0.171 | 0.129 / 0.015 | 8.37 [2.17, 22.32] |

- F1: False
- F2: False
- F3: True
- F4_T80_150: False
- F4_T40: True
- one-sided p [0.482, 0.588, 0.0135, 0.033, 0.006]; Holm (5) [0.964, 0.964, 0.054, 0.099, 0.03]; conditions with Holm p < 0.05: 1/5
- 1/width (descriptive): T80/150 AUROC 0.566, p_hat − 1/width +0.076 [+0.023, +0.139]; T40 AUROC 0.814, p_hat − 1/width +0.019 [-0.003, +0.054]
- v4 realisation vs ext_v51_p4h2 (descriptive): None

**Verdict: NOT CONFIRMED**
