# P4-H8 specification: the confirmatory study of the topology-level coverage guarantee (larger set, lags 1 to 3)

Written 2026-11-15 after the design split of P4-H8 had been run for a feasibility check and the calibration split had been launched, and **before any calibration result was read and before any test topology was run**. Status: DRAFT until frozen (see "Freeze"). It extends [p4h7_spec.md](p4h7_spec.md), which becomes a pilot (see "Relation to P4-H7"). Method, unit, scores and factor rule are those of the P4-H7 specification and are not repeated; only the differences are listed.

## Why a new set
The teachers asked to widen the simulation context (more topologies, more lags). The P4-H7 set has 150 topologies per calibration and test split and was run at lag 1 only. A larger calibration set lowers the price of a guarantee (the order statistic moves towards the median and the Beta bound tightens), and a larger test set gives narrower confidence intervals on the hit rate.

## Set
`data/topology_bank/P4-H8`, made by `data/topology_bank/generate_scalable_bank.py --seed 20261116 --splits design=100,calibration=550,test=550`. 1200 topologies (14 nodes, 21 edges; half Erdős–Rényi, half scale-free hub), i.i.d. from one generator law, assigned to splits by a seeded permutation stratified by profile. No edge set shared with any earlier set. Manifest SHA-256 `4a506c4445edae44fa58b50f1e1c832b99d7198c79b2cc6089aab7e930843934`.

| Split | n | Use |
|---|---|---|
| design | 100 | feasibility looks, ablations; no tuning of the choices below |
| calibration | 550 | the factors, one pass per lag |
| test | 550 | **one** run per lag with frozen factors. Sealed. |

## Grid (differences from P4-H7)
- Lag (generator `lag_max`) in {1, 2, 3}; lag 1 is the case of the real panel. T grid: lag 1 {19, 30, 40, 80, 150}; lag 2 {30, 40, 80, 150}; lag 3 {40, 80, 150} (T = 19 with lag 3 leaves too few rows for any of the compared fits; T = 19 and 25 at lag 2 are not run).
- Seed base 20261116 for all splits (unit seeds differ by split offset and topology index inside the runner).
- Everything else as in P4-H7: kinds {none, extra, missing, reversed}, rates {0.2, 0.5}, H = 4, n_boot = 199, tau_effect = 0.1, clean Gaussian scenario, β = 0.10 headline (β = 0.05 also reported), δ = 0.10, PAC alpha = 0.05 (N = 550 > 59 so PAC factors are defined in every cell), exact order statistics rounded up to 3 decimals, the shipped pooled rule recomputed on the same calibration split as comparator.
- Factors are stored per lag: `experiments/calibration/p4h8_frozen_lag{1,2,3}.json`.

## Success criteria (decided now; per lag, not pooled over lags)
(i) Among the non-abstaining cells of a lag, the marginal β = 0.10 hit rate's exact 95% binomial interval reaches 0.90 in at least 80% of them, and no cell has an upper limit below 0.85. With 550 test topologies the interval half-width is at most about 0.04, so a cell whose true hit rate is 0.90 fails (i) only if the estimate falls below about 0.86. (ii) Costs (width and interval score relative to the pooled shipped rule) are reported whatever the outcome. A lag that fails (i) has its guarantee claim withdrawn for the failing cells and the failure is reported.

### Rules added before any calibration result was read at lag 2 and 3 and before any test run
- **Expected runs.** A unit contributes one run per stated-damage skeleton, filed under the cell of its strongest stated damage kind (a draw with k = 0 belongs to the undamaged cell). A missing record where a run was expected is a fit failure and counts as a miss (S = infinity). Units with no expected run in a cell (for example reversed damage with k = 0 at both rates) are not retained in that cell; this is a function of the unit alone. Implemented by `--expected-runs` in `p4h7_factors.py` and `p4h7_test_eval.py`.
- **Abstention.** If the factor is infinite, or exceeds 10 (the maximum of the shipped grid), the cell has no usable guarantee: the method abstains there. Abstaining cells are excluded from criterion (i) and listed as the region where no guarantee is available; they are not hidden.
- **Correction of the pilot.** The first version of the factor script (used for the P4-H7 pilot) dropped units that had no record at all from the denominator instead of counting them as failures. The pilot factors are therefore very slightly too small in the cells where it happened (for example 149 retained units instead of 150 for one T = 19 cell). The P4-H8 rule above fixes it.

## Violations and extensions (exploratory, labelled as such)
Not part of the guarantee: Student-t(4) and Laplace innovations, measurement noise, misstated damage, and cells outside the grid (T = 19 at lag 2). They are run on the test split only after the confirmatory run, with the same frozen factors, and reported as violations of the clean-Gaussian assumption. Noise laws are not yet implemented in the unit runner; if they are added the spec of the run will be recorded in `docs/decision_rules.md` before it runs.

## Relation to P4-H7
P4-H7 (design 60, calibration 150, test 150, lag 1) is the pilot of this study. Its calibration factors and its design-split dry run informed the choice of β, δ and the scripts, so P4-H7 results are not independent of the choices made here. Its test split stays sealed; it may later be run once as a replication at lag 1, and is not needed for the claims of this study.

## Order of work and freeze
1. Design split: feasibility and ablation looks (done for lags 1 and 2; lag 3 running).
2. Calibration split per lag: factors written by `p4h7_factors.py --frozen-out experiments/calibration/p4h8_frozen_lag<k>.json`.
3. Freeze: SHA-256 of this file, of the three factor files, of the scripts and of the manifest are recorded in `docs/decision_rules.md`.
4. Test split: `p4h7_units.py --bank P4-H8 --split test --lag <k> --frozen experiments/calibration/p4h8_frozen_lag<k>.json --confirm-frozen`, then `p4h7_test_eval.py`. Needs the user's approval.

## Known weaknesses stated in advance
Exchangeability holds by construction within one generator law, with a single node set (14 nodes, 21 edges, two profiles). It says nothing about other sizes, real panels, heavy-tailed noise or latent confounders. One run per topology (replicates share the DAG). The success criterion uses the hit rate at β = 0.10; it does not guarantee per-pair coverage.
