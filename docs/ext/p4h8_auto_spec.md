# P4-H8: SRCI without the stated damage, at the same guarantee level

Written 2026-11-16 before any run of this method on the P4-H8 topologies (a code import check only). Same units, seeds, factor rule and decision rule as [p4h8_cmp_spec.md](p4h8_cmp_spec.md); read that file for the rule.

## Question
The comparison at equal guarantee left one advantage of SRCI unmeasured: it receives the stated number of missing edges, which most references do not. How much of its advantage survives when it does not receive it?

## Method
`srci_auto` (`src/paper4/ext_srci_auto.py`): the data-driven gate and opening budget of the automatic variant of the module (`ext_auto5.auto5_raw`), which drops the stated damage before diagnosis, returned uncalibrated. The width factor is still chosen per (T, stated kind) as for every method in the comparison, so the stated kind (not the count) still enters through the factor; this is stated, not hidden.

## Design
First 150 calibration topologies, first 200 test topologies of P4-H8, lag 1, T in {40, 150}, kinds none, extra, missing, reversed, rates 0.2 and 0.5; marginal beta = 0.10, delta = 0.10; factors frozen in `experiments/calibration/p4h8_auto_frozen.json` before the test dump; abstention when the factor is infinite or above 10. Reported: hit rate, pair coverage, width and interval score per cell, and the paired interval-score difference to SRCI and to BVAR-Minnesota on the same test topologies (results of `p4h8_cmp_spec.md`), with a topology cluster bootstrap. No success threshold is set: the result is the size of the difference.
