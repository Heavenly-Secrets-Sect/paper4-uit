# P4-H8 comparison specification: baselines at the same guarantee level (feedback point 6)

Written 2026-11-15, **before the calibration dump of the comparison and before any test topology was run for it** (a 2-topology timing run of the dump script existed). Status: DRAFT until frozen. Same set, seeds, unit definition and factor rule as [p4h8_spec.md](p4h8_spec.md); only the methods change.

## Why
In the earlier comparison each reference method carried its own width factor chosen by a pooled pair-level rule, so the methods reached different coverage levels (0.937 to 0.988) and interval scores were compared across unequal levels. Here every method is calibrated by the **same unit-level order-statistic rule on the same calibration topologies**, so the question becomes: at the same topology-level guarantee, which method has the narrowest intervals?

## Methods (registered names in `src/paper4/`)
`tolerant_v5_1` (SRCI), `pselect_union_v3` (post-selection union, the 32x bootstrap budget variant), `pselect_cal`, `fullvar_cal` (full VAR), `targeted_lp_cal` (targeted local projection), `bvar_minnesota_v2_cal` (Bayesian VAR, Minnesota prior). Several are the group's adaptations, not published originals; SRCI receives the stated number of missing edges, the others mostly do not. Both facts stay in the paper.

## Design
- Calibration topologies: the first 150 of the P4-H8 calibration split. Test topologies: the first 200 of the P4-H8 test split (the split assignment is a seeded permutation, so the first n are a random subset). Lag 1; T in {40, 150}; kinds none, extra, missing, reversed at rates 0.2 and 0.5.
- Factors: `p4h7_factors.py --expected-runs`, marginal beta = 0.10, delta = 0.10, one factor per (method, T, kind) cell; a factor that is infinite or above 10 is an abstention. The factors are frozen in `experiments/calibration/p4h8_cmp_frozen.json` (hash in `docs/decision_rules.md`) before the test dump.
- Test: `p4h8_cmp_units.py --split test --confirm-frozen`, then `p4h8_cmp_eval.py`: per method and T, topology hit rate (at most 10% of non-null pairs missed) with exact binomial interval, pooled pair coverage, mean width and mean interval score, over the non-abstaining cells; paired interval-score difference to SRCI with a topology cluster bootstrap.

## Decision rule (fixed now)
A method is **at the guarantee level** in a cell if its hit rate's interval reaches 0.90. Among the methods at the guarantee level in a cell, the one with the lowest mean interval score is the winner of that cell. The paper reports the count of cells won by SRCI and, for each other method, the number of cells where its paired difference to SRCI has an interval excluding 0 in either direction. Methods that abstain or miss the guarantee level are listed, not dropped.

## Known weaknesses
200 test topologies give hit-rate intervals of roughly plus or minus 0.04; two T values and lag 1 only; one generator; clean Gaussian; the reference methods are not tuned for this setting beyond their frozen configurations; SRCI uses the stated damage count, which the others mostly ignore.
