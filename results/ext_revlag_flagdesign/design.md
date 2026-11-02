# R2-7 design: combined flag chosen on round-1 D-07 rows (ext_metrics_pairs, tolerant_v4)

Rows: 38934 non-null pairs; miss base rate 0.0503.

| feature set | OOF AUROC T80/150 | OOF AUROC T40 | OOF AUROC all |
|---|---|---|---|
| S1 | 0.7375 | 0.8382 | 0.7803 |
| S2 | 0.7343 | 0.8367 | 0.7801 |

Chosen: **S1** (rule: S2 only if it beats S1 by >= 0.005 on T80/150 OOF AUROC).

In-sample check of the frozen threshold p_hat > 0.10 (training rows, not an evaluation):
- T80/150: flagged 0.088; miss rate flagged 0.142, unflagged 0.035
- T40: flagged 0.189; miss rate flagged 0.216, unflagged 0.026

Frozen weights (standardised): intercept -3.466, log1p_rel_width +0.251, log1p_width -1.407, zero_in +0.420, logT -0.635, stated_missing +0.137, stated_reversed +0.020, stated_extra +0.066
