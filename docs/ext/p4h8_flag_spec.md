# P4-H8 flag specification: improving the reliability flag (feedback point 5)

Written 2026-11-15, **before the flag dumps of the calibration, design and test splits were produced** (only a 3-topology smoke run of the dump script existed). Status: DRAFT until frozen. Same set, seeds and lag-1 cells as [p4h8_spec.md](p4h8_spec.md).

## Question
Can a per-pair flag, computed only from what a user has at deployment, predict which non-null pairs the final interval misses better than the existing frozen flag (AUROC 0.72 at T = 80/150 and 0.81 at T = 40 in the earlier study, logistic on three observable features)?

## Label and population
Unit of analysis: a non-null pair (|C_true| > 0.1) of one run (topology, T, stated damage). Label y = 1 if the pair is outside the final interval, where the final interval is the pre-scaled interval with its half-width multiplied by the frozen marginal β = 0.10 factor of the cell (`experiments/calibration/p4h8_frozen_lag1.json`, key `cell|beta0.1`). The flag is scored on the final interval, as a user would see it.

## Features (all observable; stored by `p4h8_flag_units.py`)
Interval and effect: midpoint, half-width, |midpoint| / half-width, zero inside the interval (final interval), log T. Stated information: counts of stated missing / extra / reversed edges. Stated skeleton: directed path from cause to effect exists, its length, cause–effect adjacent, out-degree of the cause, in-degree of the effect. Context in the run: median half-width of the cause's row and of the effect's column, rank of the pair's half-width among all pairs of the run. Method internals: rows-to-regressors ratio of the all-lag fit, whether targeted opening was used, number of repaired edges. The truth enters only the stored distance used to form the label.

## Models and training (calibration split only)
1. **Old flag**: `experiments/ext/revlag/frozen_flag.json`, applied unchanged (stated code from the cell kind).
2. **Width comparators**: score = −final width; score = −final relative width.
3. **New logistic**: all features above, standardised, L2 penalty chosen by 5-fold CV grouped by topology on the calibration split.
4. **New gradient boosting** (`HistGradientBoostingClassifier`): depth and learning rate chosen by the same grouped CV; no other tuning.
The better of 3 and 4 by calibration CV AUROC is the candidate; the choice is made before the test split is read. The design split is used only to check that the pipeline runs and for a sanity look; it is not used to choose anything. Both fitted models are saved and hashed in `experiments/calibration/p4h8_flag_frozen.json` before the test split is dumped.

## Evaluation (test split, once)
AUROC overall and in the T groups {19, 30}, {40}, {80, 150}, with a 95% cluster bootstrap by topology (1,000 draws), and the paired difference between the candidate and the old flag. Lift: miss rate in the top decile of the score divided by the overall miss rate.

## Success criterion (fixed now)
The candidate beats the old flag by at least 0.03 AUROC in each of the three T groups, with the cluster-bootstrap 95% interval of the difference above 0. Otherwise the result is reported as no meaningful improvement. Whatever the outcome is reported, including which features carry the signal (permutation importance on the calibration split).

## Known weaknesses
One generator, clean Gaussian scenario, lag 1, 14 nodes; the label depends on the factor of the guarantee study, so the flag is calibrated to that interval, not to an arbitrary one. Features such as the stated-skeleton path rely on the stated skeleton being the damaged one the method received. The test split of P4-H8 was already used once for the guarantee study (different question, frozen factors); this is stated rather than hidden.
