# Round-1 redteam numbers written to file (recomputed from stored results)

## pselect_union internals (results/a2b_pselect)

| T | mean n_graphs (all cells) | mean n_selected (all cells) | mean n_selected (none cell) |
|---|---|---|---|
| 40 | 16.00 | 15.90 | 15.90 |
| 80 | 16.00 | 23.72 | 23.72 |
| 150 | 16.00 | 28.20 | 28.20 |

Draws per graph in round 1: per = max(10, 199 // n_graphs) = max(10, 199 // 16) = 12.

## F7: v4 - pselect_union at missing-0.2 (t-based CI clustered by topology, df 19)

| T | estimate | per-test 95% CI | Bonferroni (54 tests) CI |
|---|---|---|---|
| 40 | +0.803 | [+0.121, +1.485] | [-0.473, +2.079] |
| 80 | -0.464 | [-0.723, -0.205] | [-0.949, +0.020] |
| 150 | -0.252 | [-0.436, -0.068] | [-0.597, +0.092] |

## F6 reframed: share of v4's margin over pselect_cal reached by fullvar_cal (results/ext_redteam_calbase)

| T | cell | IS v4 | IS pselect_cal | IS fullvar_cal | share |
|---|---|---|---|---|---|
| 80 | missing-0.2 | 3.277 | 3.956 | 3.500 | +0.67 |
| 80 | missing-0.5 | 3.370 | 4.127 | 3.816 | +0.41 |
| 150 | missing-0.2 | 2.057 | 2.616 | 2.587 | +0.05 |
| 150 | missing-0.5 | 2.215 | 2.893 | 2.914 | -0.03 |
