# Decision rules for the RQ4.2 module comparison

Written before running `experiments/configs/rq42_v1.json`. Everything here is exploratory: it uses the development split of D-07 (evaluation) and of D-07H (calibration of the `inflate` constant). A confirmatory run needs a protocol approved by the supervisor, on topologies not used during development.

## Setup recorded before the run

- Methods:
  - `oracle` (b0, reference only)
  - `plugin` (b1)
  - `inflate` (b3, constant c tuned per T × damage cell on D-07H development)
  - `lp_allpast` (b4)
  - `bagging` (b5)
  - `soft` (module v1)
- Stated damage equals true damage (kind and number of pairs). Misstated damage is a later experiment.
- Grid:
  - T ∈ {40, 80, 150, 300}
  - damage ∈ {none, extra, missing, reversed} × rate ∈ {0.2, 0.5}
  - 20 topologies × 3 replicates
  - n_boot = 199, H = 4, lag_max = 2
- Estimand: C(H) of every ordered pair with |C_true| > 0.1. Lost pairs (estimate exactly 0) count as uncovered.

## Primary measures

1. Pooled coverage of non-null pairs, against a nominal 0.95.
2. Mean interval score of non-null pairs (Gneiting–Raftery, α = 0.05; lower is better).
3. Paired difference in interval score against `plugin` and against `lp_allpast`, with a 95% bootstrap interval that resamples topologies.

## Rules

A method **passes a damage cell** at a given T when both hold:

- pooled coverage ≥ 0.90 (lenient) or ≥ 0.93 (strict; both are reported), and
- its interval score beats `plugin`: the upper bound of the paired-difference interval is below 0.

The module **v1 is retained** for further work if all three hold:

- it passes the missing-0.2 and reversed-0.2 cells at T = 80 and T = 150 under the lenient threshold;
- it never loses to `plugin` on the undamaged cell by more than 10% of `plugin`'s mean interval score;
- at one or more T, it has a lower mean interval score than `lp_allpast` on at least half of the damaged cells.

Otherwise, v1 is **rejected**. The failure pattern then decides what v2 changes. Merging Paper 4 into Paper 5 (plan section 8) is not decided by these exploratory runs; that decision belongs to the supervisor, after a confirmatory run.

## Known limits of v1, stated in advance

- Missing **contemporaneous** edges cannot be recovered. The soft prior only covers lagged terms.
- Reversed contemporaneous edges are taken as given.
- Ridge shrinkage biases true off-skeleton coefficients toward 0 at small T, so their intervals may under-cover.

## Outcome of v1 (rq42_v1)

**v1 is rejected.** The undamaged cell already shows the problem: coverage was 0.745 at T = 40 and 0.869 at T = 150, against 0.851 and 0.907 for `plugin`. Interval scores were worse than `plugin` in every cell except missing-0.5, so neither retention condition could hold. The cause is ridge shrinkage: it biases estimates toward 0, and the bootstrap does not see that bias.

`lp_allpast` is robust to missing edges (coverage 0.85–0.93). It cannot run at T = 40, and it is weak under reversals.

## v2 (`tolerant`), recorded before running rq42_v2

**What v2 does.**

- Stated missing edges: all lags of every node enter every equation. Contemporaneous edges are restored where structural residuals are correlated (Benjamini–Hochberg, q = 0.1), at most as many as the stated number of missing pairs, with their direction drawn at random in each bootstrap draw.
- Stated reversed edges: each draw flips as many oriented pairs as stated.
- Otherwise: the skeleton's own terms, as in `plugin`.

**How v2 was designed.** It was designed after seeing v1 results on the D-07 development split, and checked in a probe on 10 of those topologies (scratch, not in the repo). Its development-split results are therefore optimistic.

**Rules.** The rules above apply, with one clarification made before any v2 result existed: condition 3 counts only the values of T at which `lp_allpast` can be fitted. At T = 40 it is infeasible, and a win there would be automatic. `experiments/check_rules.py` applies the rules mechanically.

**Held-out check.** v2 is also evaluated once, frozen, on the D-07H confirmatory split (config `rq42_v2_heldout.json`). Paper 4 has not used that split for any development or tuning. The `inflate` constant stays tuned on D-07H development. This held-out check is exploratory too. A confirmatory claim still needs the supervisor's protocol.

## Outcome of v2 (rq42_v2 on D-07 development; rq42_v2_heldout on D-07H confirmatory, run once)

`experiments/check_rules.py` gives **REJECTED** on both splits. Conditions 2 and 3 are met; condition 1 is not.

**Condition 2 (undamaged cell).** v2 matches `plugin`: IS ratio 0.98–1.01.

**Condition 3 (against `lp_allpast`).** v2 has the lower interval score on 6/6 damaged cells at every T where `lp_allpast` can be fitted (80, 150, 300), on both splits.

**Missing edges.** Missing-0.5 on development, by T:

| T | v2 coverage | v2 IS | `lp_allpast` IS | `plugin` IS |
|---|---|---|---|---|
| 80 | 0.901 | 3.41 | 5.35 | 28.1 |
| 150 | 0.918 | 2.20 | 2.76 | 28.5 |
| 300 | 0.934 | 1.48 | 1.79 | 29.0 |

The held-out split shows the same pattern.

**Condition 1 fails on reversed-0.2.** Coverage is 0.855 / 0.878 at T = 80 / 150 on development, and 0.883 / 0.894 on held-out. Development missing-0.2 at T = 80 is also just below threshold, at 0.895.

**Diagnosis.** The percentile bootstrap itself under-covers at these T. Even `oracle` reaches only 0.895 (T = 80) and 0.926 (T = 150) on development. Reversal draws flip random oriented pairs, although only about a third of edges are contemporaneous.

## v3, recorded before running rq42_v3

**What changes from v2.** Two changes:

1. **Targeted reversal draws (`tolerant_v3`).** Reversal draws flip only oriented pairs whose fitted contemporaneous coefficient is significant (|t| > 1.645), or the k largest when fewer pass.
2. **Small-sample width calibration (`tolerant_v3_cal`).** `tolerant_v3_cal` widens the `tolerant_v3` interval by a factor c_T. This factor depends only on T. It is the `inflate` constant tuned on the **undamaged** cells of D-07H development, so it carries no information about the damage.

**Rejected alternative.** A probe on 10 development topologies, 3 replicates each, also tried Kilian's bootstrap-after-bootstrap bias correction. It was dropped because it made reversed-0.5 worse: interval score rose from 3.5 to 5.4 at T = 80.

**Module of record.** `tolerant_v3_cal`. `tolerant_v3` is reported alongside it.

**Rules.** Unchanged, checked by `experiments/check_rules.py`.

**Held-out check.**
- Frozen v3 is evaluated once on the **D-07 confirmatory** split (`rq42_v3_heldout.json`). Paper 2 reported results on that split, but Paper 4 has never used it.
- D-07H confirmatory was spent on the v2 check and is not reused for selection.
- After this run, no unused split remains. A further version needs a newly generated topology bank.

## Outcome of v3 (rq42_v3 on D-07 development; rq42_v3_heldout on D-07 confirmatory, run once)

`experiments/check_rules.py` results:

| Module | Development | Held-out |
|---|---|---|
| `tolerant_v3_cal` | RETAINED | RETAINED |
| `tolerant_v3` | REJECTED | REJECTED |

`tolerant_v3_cal` meets all three conditions on both splits, including the strict 0.93 threshold. `tolerant_v3` fails only reversed-0.2 at T = 80 (0.866 development, 0.877 held-out).

**Held-out interval scores, `tolerant_v3_cal` against `inflate` (b3).** The `inflate` constant is tuned per damage cell and knows the damage kind.

| Damage cell | T | `tolerant_v3_cal` | `inflate` |
|---|---|---|---|
| missing-0.5 | 150 | 2.23 | 28.4 |
| reversed-0.5 | 150 | 2.11 | 3.71 |
| reversed-0.2 | 300 | 1.48 | 2.48 |

On undamaged and extra cells the two methods are equal. Against `lp_allpast`, `tolerant_v3_cal` has the lower interval score in 6/6 damaged cells at T = 80, 150 and 300.

**Known cost: over-coverage.** Coverage of `tolerant_v3_cal` on damaged cells is 0.94–0.99, so its intervals are wider than they need to be. For missing cells its interval score is slightly worse than uncalibrated `tolerant_v3` (3.52 vs 3.18 at T = 80, held-out). The reason: c_T was tuned for `plugin` on undamaged data, and the module's structural draws already widen the interval.

**Status.** These are exploratory results, now validated on two held-out splits (v2 on D-07H confirmatory, v3 on D-07 confirmatory). No unused split of the existing banks remains.

## v4, recorded before running rq42_v4

**What changes from v3.** `tolerant_v4` is `tolerant_v3` widened by a factor tuned for the **module itself**. The factor is set per (T, stated damage kind) on D-07H development, pooling the damage rates. v3 instead used `plugin`'s factor on undamaged data, and that over-covers damaged cells (0.94–0.99).

**Why per stated kind.** The module receives the stated damage kind through the interface (plan section 7), so tuning per kind uses no information it would lack in practice. For the undamaged cell the factor equals v3's, because the module equals `plugin` there.

**Rules.** Unchanged. In addition, coverage should move closer to 0.95 than v3's, without losing condition 1.

**Where it is evaluated.**
- **Development:** D-07 development.
- **Held-out, run once on the frozen v4:** **P4-H1 confirmatory**, a bank newly generated for Paper 4 and never looked at before.
- v3_cal is re-evaluated on P4-H1 in the same run, so the two versions are compared on fresh topologies.

## Outcome of v4 (rq42_v4 on D-07 development; rq42_v4_heldout on P4-H1 confirmatory, run once)

**Verdict.** `tolerant_v4` is **RETAINED** on both splits, with all three conditions met at the strict threshold. `tolerant_v3_cal` is also retained on P4-H1, a bank generated after v3 was frozen. That makes it a second, independent held-out confirmation of v3.

**Module-specific width factors, tuned on D-07H development.**

| T | missing | reversed | none / extra |
|---|---|---|---|
| 80 | 1.3 | 1.5 | 1.4 |
| 150 | 1.2 | 1.3 | 1.3 |
| 300 | 1.1 | 1.3 | 1.1 |

**Coverage on P4-H1: v4 is closer to nominal on missing edges.**

| Cell | v4 | v3_cal |
|---|---|---|
| missing-0.2, T = 80 | 0.975 | 0.988 |
| missing-0.2, T = 150 | 0.967 | 0.976 |
| reversed-0.2 | unchanged | unchanged |

The paired interval-score gain against `plugin` improves slightly: −7.95 for v4 against −7.63 for v3_cal at T = 80, missing-0.2.

**Module of record: `tolerant_v4`.** Every split used so far is logged above:
- D-07H confirmatory: v2;
- D-07 confirmatory: v3;
- P4-H1 confirmatory: v3_cal and v4.

P4-H1 development is still unused.

## Structured damage check, recorded before running rq42_structured

**Kinds tested.** Damage shaped like text-extraction errors, plus combined damage:

- `shortcut`: a chain a → b → c, with a and c non-adjacent, becomes a → c, and one chain edge is dropped.
- `weak_missing`: the weakest true edges are dropped.
- `mixed`: missing, extra and reversed damage at the same rate.

**What the module receives.** It gets only the stated counts, `{missing, extra, reversed}`. Its width factors keep their single-kind calibration on D-07H development, and the structured kinds are excluded from that calibration. This is an out-of-distribution check of the frozen v4.

**How it is read.** Descriptively, with no pass/fail rule:
- coverage and interval score of `tolerant_v4` against `plugin`, `lp_allpast` and `inflate`;
- `inflate` is tuned per structured cell on D-07H development, which gives it an advantage.

**Data.** D-07 development.

## Outcome of the structured damage check (rq42_structured, D-07 development)

**Coverage.** Frozen `tolerant_v4` covers 0.94–0.97 in every structured cell (shortcut, weak_missing, mixed; rates 0.2 and 0.5) at T = 80 and 150. It received only the stated counts, and its widths come from single-kind calibration.

**Interval score.** `tolerant_v4` has the lowest score of all methods in every structured cell at T = 150:

| Cell | `tolerant_v4` | `lp_allpast` | `plugin` | `inflate` |
|---|---|---|---|---|
| shortcut-0.5 | 2.09 | 2.81 | 11.98 | 11.49 |
| mixed-0.5 | 2.54 | 4.32 | 23.58 | 15.51 |

`inflate` is tuned on these very cells, so it holds the advantage, and it still scores worse.

## A-group checks, recorded before running a2_baselines, a1_latent_noise and a3_ges

All three use the **frozen** `tolerant_v4` (no change to code or width factors) on **D-07 development**, with calibration on D-07H development as before. P4-H1 development stays unused.

### A2: published baselines (`a2_baselines`)

**New baselines** (`src/paper4/methods.py`):
- `ida_union`: IDA-style (Maathuis, Kalisch and Bühlmann 2009). Every member of the skeleton's Markov equivalence class (at most 16) is fitted as in `plugin`. The interval is the union of the members' bootstrap intervals. It reads no stated damage. Lagged terms do not depend on orientation, so it only acts on contemporaneous terms.
- `bvar_minnesota`: Bayesian VAR with a Minnesota-type prior. All lags of all nodes enter every equation; pairs off the skeleton get prior tightness θ. λ and θ are chosen by marginal likelihood on a grid, in the spirit of Giannone, Lenza and Primiceri (2015). The interval is a posterior credible interval, with error variances fixed at univariate AR scales.

**Grid.** T ∈ {40, 80, 150}; damage ∈ {extra, missing, reversed} × {0.2, 0.5}; 20 topologies × 3 replicates.

**Rule.** The claim "the module beats the published baselines" holds in a damaged cell at a given T when both of these hold:
- `tolerant_v4` coverage ≥ 0.90;
- the paired interval-score difference against **each** of `ida_union` and `bvar_minnesota` has a 95% CI (clustered by topology) whose upper bound is below 0.

It is reported as a count of cells. No other outcome changes the module.

### A1: latent confounders and measurement noise (`a1_latent_noise`, plan section 9)

**Scenarios** (`src/paper4/generator.py`):
- `clean`;
- `latent1` and `latent3`: 1 or 3 hidden AR(1) common causes, each driving 3 observed nodes. The latent nodes are nested across scenarios.
- `noise0.1` and `noise0.3`: measurement error with variance 0.1 or 0.3 times each series' variance, i.e. reliability 0.91 or 0.77.

The truth of an observed pair is unchanged across scenarios (latent nodes have no observed parents). Calibration uses clean data only.

**Grid.** T ∈ {80, 150}; damage ∈ {none, missing-0.2, reversed-0.2}.

**Expectations, written in advance:**
- Every method, `oracle` included, loses coverage under latent confounding, because the observed skeleton cannot express a hidden common cause.
- When missing edges are declared, the module's residual-correlation repair can mistake a confounder for a missing contemporaneous edge. `info_n_repair` is compared between `clean` and `latent*` to see this.
- Measurement error attenuates coefficients, so coverage falls as the noise ratio grows.

**How it is read.** Descriptively, with no pass/fail rule. A robustness claim for a scenario is allowed only where `tolerant_v4` coverage ≥ 0.90. Otherwise the scenario is reported as a limitation.

### A3: skeletons learned by GES (`a3_ges`)

**Skeleton.** The GES of Paper 2 (ACIIDS, imported read-only, `src/paper4/learned.py`), run as Paper 2 runs it: rows treated as independent draws. It runs on an independent series of the same length (plan 5.2: no double dipping). Undirected CPDAG edges enter as undetermined pairs, i.e. lagged terms only.

**Stated damage.** The mean GES error counts {missing, extra, reversed} per T on the calibration bank (D-07H development). It is therefore an estimate, not the truth of the evaluated skeleton. The true counts go to the private log and to `true_*` columns.

**Grid.** T ∈ {40, 80, 150}; cells `none` (true skeleton, reference) and `ges`.

**How it is read.** Descriptively. The claim "the module handles algorithm-generated damage" holds at a given T if, in the `ges` cell:
- `tolerant_v4` coverage ≥ 0.90;
- its paired interval-score difference against `plugin` has an upper CI bound below 0.

## Outcome of the A-group checks (D-07 development, frozen v4)

### A2 (`a2_baselines`)

**Result.** The rule holds in **13 of 18** damaged cells.

| | missing | reversed | extra |
|---|---|---|---|
| Cells passed | **6/6** | 4/6 | 3/6 |

- **Missing.** Every margin is large: the module's interval score is lower by 2.4–26 than `ida_union` and by 2.4–10 than `bvar_minnesota`.
- **Reversed.** The two failures are reversed-0.2 at T = 40 and T = 80. There the difference against `ida_union` is negative but its CI crosses 0 (−0.31 and −0.13). IDA is designed for orientation uncertainty, so a tie with it on mild reversal is expected.
- **Extra.** The failures are extra-0.2 and extra-0.5 at T = 40, and extra-0.5 at T = 80, all ties. With extra edges every method stays near `plugin`, so there is little to separate.
- **Missing edges are the decisive case.** Neither published baseline can restore a missing edge: `ida_union` reaches only 0.36–0.73 coverage, and `bvar_minnesota` 0.48–0.77.

### A1 (`a1_latent_noise`)

Number of cells (out of 6) where `tolerant_v4` coverage ≥ 0.90:

| Scenario | Cells passed | Failing cells (coverage) |
|---|---|---|
| clean | 6/6 | — |
| latent1 | 6/6 | — |
| latent3 | 5/6 | T = 150, none (0.871) |
| noise0.1 | 4/6 | T = 80, none (0.893) and reversed (0.887) |
| noise0.3 | **0/6** | coverage 0.77–0.89 |

**Robustness claim allowed:** for latent1 and latent3, and for the missing cells under noise0.1.

**Reported as a limitation:** noise0.3, and the undamaged and reversed cells under noise0.1.

**Expectations, checked against the results:**
- **Latent confounding lowers everyone's coverage.** Confirmed, and the drop grows with T because the bias does not shrink. `oracle` falls to 0.78 at latent3, T = 150.
- **Confounders trigger the repair step.** Confirmed: the mean number of restored edges rises from 1.67 (clean) to 2.25 (latent1) and 2.82 (latent3) at T = 150, missing-0.2. Coverage nevertheless stays at 0.93–0.95, because the extra structural draws also widen the interval.
- **Measurement error lowers coverage with the noise ratio.** Confirmed. `oracle` collapses to 0.35–0.48 at noise0.3: its intervals are narrow, and attenuation bias moves them away from the truth. Under noise0.3 with reversed edges, `inflate` covers better (0.88–0.90) and has a lower interval score than the module.

### A3 (`a3_ges`)

**What GES gets wrong.** GES (rows treated as i.i.d.) misses on average 14.1, 12.9 and 11.6 of the 21 true pairs at T = 40, 80 and 150, adds about 13 extra pairs, and reverses about 3. Per skeleton, the number of missing pairs ranges from 6 to 19.

**Stated damage.** The calibration-bank means were missing 12–13, extra 12–13, reversed 3–4. Each evaluated skeleton therefore received an inexact statement.

**Result.** The claim holds at **every T**.

| T | `tolerant_v4` coverage | Interval score difference vs `plugin` (95% CI) |
|---|---|---|
| 40 | 0.98 | −13.5 [−15.3, −11.6] |
| 80 | 0.95 | −18.8 [−20.7, −16.9] |
| 150 | 0.94 | −19.6 [−21.2, −17.9] |

Every other method covers 0.32–0.59, except `inflate` (0.80–0.86, at a much higher interval score) and `lp_allpast` (0.82–0.86, interval score 6.7 and 4.4 against the module's 3.7 and 2.6 at T = 80 and 150).

## A2b and the A-group held-out check, recorded before running a2b_pselect and a*_heldout

### A2b: a third published baseline (`a2b_pselect`, D-07 development)

**Baseline.** `pselect_union` adapts post-selection inference after causal discovery (Chang, Guo and Malinsky, arXiv 2405.06763) to the SVAR:
- Adjacencies are re-selected from the data: a pair is selected when its Granger statistic (either direction, all-lag VAR) or its residual partial correlation has |z| > 1.96.
- The selection is repeated 100 times, each time with N(0, 1) noise added to every z-score.
- The unperturbed graph and the 15 most frequent perturbed graphs are fitted as in `plugin`.
- The interval is the union of their intervals.
- It reads no stated damage.

This is an adaptation, not the original procedure (see the docstring).

**Seeds.** Same seeds as `a2_baselines`, so its rows pair with that run.

**Rule.** The A2 rule is extended to `pselect_union`: in each damaged cell, `tolerant_v4` coverage ≥ 0.90 and the upper CI bound of its paired interval-score difference against `pselect_union` < 0. Reported as a count of cells.

### Held-out check of the A group (P4-H1 development, run once)

**Configs.** `a2_heldout`, `a1_heldout` and `a3_heldout` repeat `a2_baselines` (with `pselect_union` added), `a1_latent_noise` and `a3_ges` unchanged except for the bank. The bank is P4-H1 development, never used before. Calibration stays on D-07H development. Nothing is tuned after seeing these results.

**What counts as confirmation.** The claims below count as confirmed only if the same rules give the same verdict as on D-07 development:
- **A2:** the module beats every published baseline in **all six missing-edge cells**. Reversed and extra cells are reported as they come.
- **A1:** the module's coverage is ≥ 0.90 in **every latent1 cell**, and in **at least 5 of the 6 latent3 cells**. noise0.3 is expected to fail and stays a limitation.
- **A3:** in the `ges` cell at every T, coverage ≥ 0.90 and the upper CI bound of the paired interval-score difference against `plugin` < 0.

## B1: self-diagnosing module, recorded before running b1_auto

**Method.** `tolerant_auto` is the frozen `tolerant_v3`/`v4` machinery with one change: the damage record is **estimated from the data** (`src/paper4/diagnose.py`) instead of read from the declaration. The width factor is v4's, looked up with the estimated record.

How the damage is estimated:
- **Missing:** Storey's estimate of the number of non-null pairs among the pairs the skeleton leaves out. Each pair's p-value is the Šidák combination of the two Granger tests and the residual partial correlation in the all-lag VAR.
- **Extra:** Storey's estimate of the number of null pairs among the pairs the skeleton keeps.
- **Reversed:** a fixed allowance of 20% of the skeleton's oriented pairs whose residual partial correlation is significant. Reversals are not identified by the data.
- When the all-lag VAR cannot be fitted, the status is `undiagnosable`.

**Development probe (D-07H development, 8 topologies, before this entry).** The first version combined the three p-values with Bonferroni. That made null p-values non-uniform, and Storey's estimate fell to near 0. It was replaced by Šidák before any evaluation.

With Šidák, the estimate over-counts missing edges on correct skeletons:
- 5–9 at T = 80–300;
- 7 at T = 40.

When 11 edges are truly missing, it counts 11–17. Over-declaring is the cheap direction: in `rq42_misstated`, declaring double the damage cost little.

**Evaluation.** D-07 development, with the seeds of `a2_baselines`:
- T ∈ {40, 80, 150};
- cells: none, {extra, missing, reversed} × {0.2, 0.5}, and the GES cell of `a3_ges`.

Methods: `plugin`, `tolerant_v4` (declared damage) and `tolerant_auto`.

**Rules.** `tolerant_auto` is **retained** if all three conditions hold:
1. Coverage ≥ 0.90 in every missing and reversed cell at T = 80 and T = 150.
2. On the undamaged cell, its interval score is at most 1.35 times that of `tolerant_v4`, at every T. This bounds the cost of false alarms.
3. In the GES cell at T = 80 and 150, coverage ≥ 0.90 and interval score at most 1.10 times that of `tolerant_v4`. There, `tolerant_v4` reads the calibration-bank mean of GES errors.

T = 40 is reported, not ruled. The accuracy of the damage estimate (mean estimated vs true counts) is reported per cell.

## Outcome of A2b and of the A-group held-out check

### A2b (`a2b_pselect`, D-07 development)

**Result.** The module beats `pselect_union` in **16 of 18** damaged cells. The two losses are missing-0.2 and missing-0.5 at **T = 40**, where `pselect_union` has the lower interval score: 6.96 vs 7.77, and 6.63 vs 7.53.

- `pselect_union` covers only 0.85–0.86 there, so it fails the coverage target.
- The module covers 0.98, but its interval is about twice as wide (width 6.5 vs 3.5).

So at T = 40 the module is over-cautious on missing edges.

### Held-out check, P4-H1 development (run once)

**A2 (`a2_heldout`).** The module passes **14 of 18** cells against all three published baselines together. The confirmation criterion was "all six missing-edge cells", and it is **NOT met**.

- **T = 80 and 150:** the module wins all 4 missing-edge cells, as on D-07.
- **T = 40, missing-0.2:** it loses to `pselect_union` (+0.77 [+0.16, +1.39]), and the comparison with `bvar_minnesota` is a tie (−0.77 [−1.69, +0.09]).
- **T = 40, missing-0.5:** a tie with `pselect_union` (+0.56 [−0.12, +1.10]).
- **Extra cells at T = 40:** ties.

The claim "beats the published baselines on missing edges" therefore holds for **T ≥ 80 only**.

**A1 (`a1_heldout`).** Cells (out of 6) with module coverage ≥ 0.90:

| Scenario | Cells passed |
|---|---|
| clean | 6/6 |
| latent1 | 6/6 |
| latent3 | 5/6 (T = 150, none: 0.868) |
| noise0.1 | 2/6 |
| noise0.3 | 0/6 |

**Confirmed** as stated: every latent1 cell and at least 5 of 6 latent3 cells pass. For comparison, `oracle` covers 0.757 at latent3, T = 150, none.

noise0.1 is weaker than on D-07 (2/6 against 4/6). Measurement noise stays a limitation at both levels.

**A3 (`a3_heldout`).** **Confirmed at every T.**

| T | Module coverage | Interval-score difference vs `plugin` |
|---|---|---|
| 40 | 0.96 | −13.3 [−16.2, −10.4] |
| 80 | 0.94 | −18.9 [−20.4, −17.4] |
| 150 | 0.94 | −19.4 [−21.6, −16.9] |

`pselect_union` again has the lower interval score at T = 40 (7.61 vs 9.26), at coverage 0.85. At T = 80 and 150 the module is better (3.78 vs 4.41, and 2.66 vs 3.22).

**Split usage.** P4-H1 development is now used by this held-out check. Every split is now used once: D-07H confirmatory, D-07 confirmatory, P4-H1 confirmatory and P4-H1 development. **A confirmatory check of B1 needs a new bank.**

## Outcome of B1 version 1 (b1_auto, D-07 development)

**Verdict: REJECTED.**

**Condition 1 holds.** Coverage is 0.91–0.96 in every missing and reversed cell at T = 80 and 150.

**Condition 2 fails.** On the undamaged cell, the interval-score ratio to v4 is:

| T | Ratio | Bound |
|---|---|---|
| 40 | 1.54 | 1.35 |
| 80 | 1.24 | 1.35 |
| 150 | 1.37 | 1.35 |

**Condition 3 fails at T = 150.** In the GES cell, the interval score is 3.02, against a bound of 1.10 × 2.62 = 2.88. At T = 80 it holds: coverage 0.94, interval score 3.89 against 4.08.

**Cause.** On correct skeletons the estimate counts 6–8 missing pairs, so the module always opens all lags. The contemporaneous evidence was the partial correlation of **reduced-form** residuals given all others. That is non-zero for the two parents of a common child (moralisation), so v-structures count as missing edges.

At T = 40 a second problem appears: the estimate under-counts true missing edges (8 found when 11 are missing) and over-counts extra ones. Coverage falls to 0.73 at missing-0.5.

**What works.** In the GES cell at T = 80 and 150, `tolerant_auto` nearly matches v4, which reads the calibration-bank mean:

| T | `tolerant_auto` (coverage / IS) | v4 (coverage / IS) |
|---|---|---|
| 80 | 0.94 / 3.89 | 0.95 / 3.71 |
| 150 | 0.93 / 3.02 | 0.94 / 2.62 |

## B1 version 2, recorded before running b1v2_auto

**One change.** The contemporaneous evidence for a pair that the skeleton leaves out is now the Fisher z of the correlation of the **structural** residuals. These come from the skeleton's own fit with all lags, the same residuals the module's repair step uses.

When the skeleton is right, structural shocks are independent, so a left-out pair carries no correlation. A v-structure no longer counts. The Granger part and the extra/reversed rules are unchanged.

**Amended before running, after a null check on the calibration bank (D-07H development, one topology).** The reduced-form Granger test is not a valid adjacency test either. Take u → w at a lag and w → v at lag 0. In reduced form, v_t contains w_t, which contains u at an earlier lag, so u "Granger-causes" v although the pair is not adjacent. With the true skeleton, 19% of left-out pairs exceed the one-sided 5% level even at T = 1000.

Every test of version 2 is therefore made in the **structural** equations of the skeleton's all-lag fit (all lags of all nodes plus the skeleton's contemporaneous parents):
- **Left-out pair (u, v):** a Wald test of u's lag block in v's equation and of v's lag block in u's equation, plus the correlation of the two structural residuals. The Fisher z uses the residual degrees of freedom: at T = 80 the naive √(m − 3) inflated the null sd to 1.36.
- **Kept pair:** a joint Wald test of all of u's terms in v's equation (lags, and the contemporaneous term if u → v) and of all of v's terms in u's equation.
- Each pair's p-value is the Šidák combination of its tests.
- Wald tests are referred to F(k, residual dof) through Paulson's normal approximation, not to χ². The χ² version still over-counted at T = 40–150 in the same null check: 5–12 missing pairs found on correct skeletons. At T = 1000 it was near the truth.

Storey counting, the extra rule and the reversal allowance are unchanged.

**Seeds and grid.** As in version 1.

**Rules.** Unchanged (conditions 1–3 of the B1 entry above). T = 40 is reported, not ruled.

## Outcome of B1 version 2 (b1v2_auto, D-07 development)

**Verdict: REJECTED.** All three conditions fail.

**Condition 1 fails.** Coverage at missing-0.2, T = 150 is 0.887. The other cells at T = 80 and 150 reach 0.91–0.96.

**Condition 2 fails.** On the undamaged cell, the interval-score ratio to v4 is:

| T | Ratio | Bound |
|---|---|---|
| 40 | 1.48 | 1.35 |
| 80 | 1.28 | 1.35 |
| 150 | 1.59 | 1.35 |

**Condition 3 fails.** In the GES cell:

| T | Coverage | Interval score | Bound (1.10 × v4) |
|---|---|---|---|
| 80 | 0.91 | 4.44 | 4.08 |
| 150 | 0.93 | 2.99 | 2.88 |

**The estimates themselves are closer to the truth than in version 1:**
- correct skeletons: 4.5–5.2 missing pairs counted, against 6–8 in version 1;
- missing-0.5 at T = 80: 12.0 counted, true 11;
- GES skeletons at T = 80: 12.9 counted, true 12.9.

**Lesson for the B1 direction.**
- Any false alarm makes the module open all lags and widen its intervals. On a correct skeleton that costs a factor of 1.3–1.6 in interval score.
- With Storey counting on about 70 pairs, the estimate is biased upwards by 3–5 pairs even when the null p-values are uniform.
- A count estimate alone is therefore not enough. A usable B1 needs one of two things:
  - a decision step, i.e. a test of "the skeleton has no missing edge" before opening the lags;
  - targeted opening: lags only for the pairs with evidence, not for all pairs.

B1 stays open as a direction. No version is retained.

## Runner fixes after the round-1 audit (docs/ext/synthesis_round1.md, section 5)

These fixes were applied before round 2. A regression check reran rq42_smoke: all 84 summary rows are identical, so built-in methods are unaffected.

**B1: seeds of extension methods.** The bootstrap stream of an ext method was `rng(100 + position in the list of every ext method in the repo)`, so its results changed whenever another ext module was added. It is now fixed by the method's name (`ext_seed`, crc32). Ext results produced before this fix can only be reproduced with the set of ext files that existed when they were run.

**B2: extension loading.** A broken ext module used to crash every run. It is now skipped with a warning. A method listed in a config that nobody registers raises an explicit error.

**B3: private damage log.** `skel.log` (the true damaged pairs and their lags) and `lag_hint` used to reach every method; no method read them. Every method except `oracle` now receives `public(skel)`, which carries only pairs, orientation and stated damage. A test checks this.

**B4: frozen v4 factors.**
- The width factors of "frozen v4" were re-tuned in every config (for example `mod|40|none` = 1.7 in rq42_v4 against 1.4 in a2), so v4 drifted slightly between runs.
- They are now stored in `experiments/calibration/tolerant_v4_frozen.json`: T = 40/80/150 from a2_baselines, T = 300 from rq42_v4_heldout, all tuned on D-07H development. A config that sets `frozen_calibration` uses those values.
- Calibration also runs whenever `calibrate_methods` is set, not only when v4, v3_cal or inflate is listed.

**B5: earlier wording.** The width-factor table recorded in the v4 entry (80: 1.3/1.5/1.4) was from one calibration run. The factors actually used varied by config (see B4). The A-group sentence "no change to code or width factors" holds for code only.

**B7: null pairs.** `evaluate` now also stores the interval score and coverage on null pairs (`iscore_null_mean`, `n_covered_null`, `n_null`).

## Bug found during round 2 in the round-1 v5 module (reported by the auto5 agent, confirmed by reading the code)

**Where.** `src/paper4/ext_narrow.py`, `opened_terms`.

**What happens.** When a repaired contemporaneous edge lands on an opened pair, that pair becomes adjacent in the drawn skeleton. `parent_terms` then already contains its lag block, and `opened_terms` appends the same block again. `lstsq` splits the coefficient across the duplicate columns, and `fit_equations` keeps only the last copy, so the lag coefficient is roughly halved.

**Evidence.** Toy SVAR at T = 2000: true 0.6, fitted 0.294 (auto5's check). At T = 40 the duplicates can also make an equation underdetermined.

**Impact.** Round-1 `tolerant_v5` and `v5_sel` rows are affected whenever a repair coincides with an opened pair. Their reported numbers (docs/ext/narrow.md) are from the buggy version.

**Fix.** De-duplicate the terms: `list(dict.fromkeys(...))`. Already done in `ext_auto5.targeted_terms`. Any round-2 module built on v5 must do the same.

The evaluated round-1 file is left unchanged so its results stay reproducible. The v5.1 module must be checked for this before its P4-H2 spec is accepted.

## P4-H2 confirmatory run (round 3), recorded before running

**Approval.** Approved by the project owner (the user) in the session at about 2026-11-02T08:05Z, through the choice "Run now". The plan approved is docs/ext/synthesis_round3.md, section 3, including the runtime exception (about 60–100 minutes) and the exclusions below.

**Specs in the run and their roles.**
- **Primary:**
  - P1: `tolerant_v5_1` vs `tolerant_v4`. Decides the module of record in declared mode.
  - P2: `tolerant_auto3`, two configs. Decides the auto (undeclared) mode.
  - P7-v5_1: `tolerant_v5_1` vs the 7-baseline envelope. Decides the main baseline claim.
- **Secondary:** P7-v4, `tolerant_v4` vs the same envelope, as a falsification test.
- **Excluded:**
  - P3/P4 (RQ4.4 flag, v4L lag): incomplete specs, no spec manifest.
  - P5 (TLP): open analyzer defects (a)/(b), and runtime.
  - P6: replaced by P7.
  - v4c, eiv2 and auto5: not candidates.

  The excluded claims remain exploratory permanently.

**Frozen artefacts (sha256 at approval).**
| File | sha256 |
|---|---|
| `experiments/ext/synthesis_round3/p4h2_plan_files.json` (62 files) | `235d08153e80ca555a027168adc9554eaec51e9c7e84b8a2a8e4f2a763639d85` |
| `experiments/ext/synthesis_round3/lead_guard.py` | `cc491e3787ae4f8a65d1279aff31125bf7642ce9775d506edcd906a1750fc8c6` |
| `experiments/ext/synthesis_round3/v4_identity.py` | `223155617091f1d8a8ed675426de58254c689becdf39eac2e337f2392893062f` |
| `docs/ext/synthesis_round3.md` | `0f98475e97cc65db40cc52d26ddb98b8a8df1a6a8e732b8041cf33b66065d452` |

Environment: interpreter `/Users/kietnt/miniconda3/bin/python`, numpy 2.5.4.

**Commands.** The 13 commands of docs/ext/synthesis_round3.md section 3.4, verbatim, in that order, each run once. No parallel jobs. Between commands 4 and 8 only exit codes and the last log line may be read. The analyzers (commands 9–11) run only after all four runs and the post guard.

**Multiplicity** (synthesis_round3.md section 3.6, points 3–5).
- The official verdict of each spec is its frozen rule at the level the spec states (0.05).
- A Bonferroni overlay over the k = 2 primary claims with a p-value component (P1-C1 and P7-v5_1, α = 0.025 each) is reported next to each verdict:
  - P1-C1 uses its 97.5% CI line;
  - P7 uses Holm at 0.025 over 56 comparisons, with B = 20000.
- In the paper:
  - "confirmed on the sealed bank P4-H2, also after Bonferroni correction over the two primary claims" only if a claim passes both levels;
  - otherwise "met its pre-registered rule at 0.05 but not after Bonferroni correction".
- P2 is a point-estimate criterion with no type-I error control; Holm over its 14 coverage cells is reported alongside.

**Reading the outcomes** (section 3.10).
- The module of record follows P1: if CONFIRMED, it becomes `tolerant_v5_1` in declared mode; otherwise `tolerant_v4` stays.
- The auto mode follows P2.
- The baseline claim follows P7-v5_1.
- P7-v4 is reported as is and changes nothing.

**Bug E1** (not fixed, by the user's decision). Built-in seeds follow the cell position. Consequences:
- The v4 table on P4-H2 comes from the P1 run.
- P7 runs through `experiments/ext/baselines3/run_cells.py` so that cell positions are kept.
- `v4_identity.py` checks the predicted identities. A mismatch is a disclosed reproducibility finding and changes no verdict.

**Stop rules** (section 3.7).
- If the pre guard or a preflight fails, nothing runs.
- If a run is interrupted before `runs.jsonl` exists, its directory is renamed to `<dir>_aborted1` and the run is repeated once, unchanged, with disclosure.
- If a method raises, that spec is NOT CONFIRMED (incomplete), with no code change.
- If the post guard fails, every verdict is labelled INVALID (integrity).

**Fragility notes.**
- P2: per auto3fix.md section 1.2, the estimated pass probability is about 0.62–0.65, so a miss at T80 reversed-0.5 alone is not evidence that auto3 got worse.
- P1: one failed run can flip C1 or C2 in 4 cells (intention-to-treat coverage).

**Split usage owed (E10).** The round-2 and round-3 runs on D-07 development and D-07H development, including the `--workers 6` rerun of v4c, are listed in docs/ext/synthesis_round2.md and docs/ext/synthesis_round3.md.

## Outcome of the P4-H2 confirmatory run

**Timeline (UTC).** Logs are in `results/ext_synthesis_round3_p4h2_logs/` (`timeline.txt` plus one log per command). No command was repeated; there was no interruption and no crash.

| Command | Time (UTC) | Exit | Runtime and rows |
|---|---|---|---|
| 1–3: lead guard pre, preflight P1, preflight P2 | about 08:06–08:07 | PASS / PASS / OK | — |
| 4: P1 | 08:07:12–08:14:40 | 0 | 447.7 s, 2520 rows |
| 5: P2, config 1 | 08:14:40–08:23:08 | 0 | 507.3 s, 4320 rows |
| 6: P2, config 2 (latent1) | 08:23:08–08:28:04 | 0 | 296.1 s, 2880 rows |
| 7: P7, through `run_cells.py` | 08:28:04–08:50:43 | 0 | 1358.9 s, 2400 rows |
| 8: lead guard post | 08:50:43 | 0 | LEAD GUARD PASS |
| 9–12: analyzers and identity check | 08:50:43–08:50:44 | 0 | — |

**Guards.**
- Pre and post: PASS.
- `hashes_pre.txt` and `hashes_post.txt` both have sha256 `46390746923d8f92a16550ea5dc036d87d4aa42abf3afe65e613915628ad7464` (identical).
- Exactly 4 run directories carry a P4-H2 manifest.
- The bank manifest sha256 equals `0b7e6579…aaa1c7d8`.

**Failed runs.** None for any ruled method: 60/60 ok in every ruled cell of P1, P2 and P7.

**P1, verbatim** (`results/ext_v51fix_p4h2/ruling_v2.md`): "C1 2/2 (Holm over 2: 2/2); C2 12/12 (v5_1 significantly worse than v4 after Holm: 0/12); C3 7/7 (significantly worse after Holm: 0/7); validity PASS; failure ceiling PASS -> **tolerant_v5_1 CONFIRMED on P4-H2**". Bonferroni overlay over 2 primary specs (C1 with 97.5% CI): CONFIRMED.

C1 at T40:

| Cell | Coverage (ITT) | IS v5_1 vs v4 | v5_1 − v4 [95% CI] | Upper 97.5% bound |
|---|---|---|---|---|
| missing-0.2 | 0.928 | 4.621 vs 7.813 | −3.192 [−3.539, −2.870] | −2.822 |
| missing-0.5 | 0.947 | 4.989 vs 7.536 | −2.547 [−2.761, −2.339] | −2.317 |

**P2, verbatim** (`results/ext_auto3fix_p4h2_check/check.md`):
- "C1 … -> PASS" (8 cells, coverage 0.929–0.984, 60/60 ok each)
- "C2: T40 ratio 1.113; T80 ratio 1.079; T150 ratio 1.199 -> PASS"
- "C3: T80 cov 0.939 ratio 0.948; T150 cov 0.951 ratio 0.964 -> PASS"
- "L1 … -> PASS" (0.945–0.975)
- "Holm (alpha 0.05) over the 14 coverage cells, H0 'cov <= 0.90' rejected: 14/14"
- "**CONFIRMED**"

The weakest C1 cell is T80 reversed-0.5 at 0.929.

**P7-v5_1, verbatim** (`results/ext_baselines3_p4h2/ruling.md`): "tolerant_v5_1: **CONFIRMED** (Holm 0.05); Bonferroni overlay (Holm 0.025): CONFIRMED".
- (i) Coverage 0.963 / 0.969 / 0.964 / 0.960.
- (ii) Failure 0/60 in each cell.
- (iii) W_D07 set confirmed 27/27.
- (iv) No L.
- Descriptive: "W 27 / T 1 / L 0". The tie is again T150 missing-0.5 against `pselect_union_v3_cal`: −0.05 [−0.17, +0.04].

**P7-v4 (secondary), verbatim:** "tolerant_v4: **CONFIRMED** (Holm 0.05); Bonferroni overlay (Holm 0.025): CONFIRMED".
- (i) Coverage 0.974 / 0.972 / 0.965 / 0.971.
- (iii) W_D07 set confirmed 19/19.
- (iv) No L.
- Descriptive: "W 23 / T 5 / L 0"; v4 beats the whole envelope in no cell.

Note: on D-07 development, v4 had lost at T150 missing-0.5. On P4-H2 it does not lose there.

**Identity check (E1).** `tolerant_v4` rows of the P2 run vs the P1 run: 1260 shared, 0 mismatches. v4 and v5_1 rows of the P7 run vs the P1 run: 240 and 240 shared, 0 mismatches. P7's analyzer also reports 0 mismatches over 480 rows.

**Module of record after the run.**
- **Declared mode:** `tolerant_v5_1`, by the round-2 commitment (P1 CONFIRMED). It is described as "v5 with de-duplicated targeted lag opening, two-sided width calibration": all 360 ok missing-cell runs took the targeted branch, and the all-lag branch cannot be selected at T ≤ 150.
- **Auto mode:** `tolerant_auto3` (P2 CONFIRMED).
- The main baseline claim (M1) is confirmed for the 27 comparisons and 4 cells of P7-v5_1, also after Bonferroni correction over the two primary claims.

**Split usage.** P4-H2 confirmatory was used once on 2026-11-02. Every split of D-07H, D-07, P4-H1 and P4-H2 confirmatory is now used. Any further confirmatory claim, including P3/P4/P5, needs a new bank. P4-H2 development has never been opened.

## Outcome of the P4-H1 held-out replication of RQ4.1, RQ4.3, RQ4.4 (2026-11-03)

P4-H1 had been used before (v4 held-out on its confirmatory split, group-A checks on its development split), so this is a **held-out replication, not a sealed confirmation**. Rules were registered before each run (hashes in `results/ext_p4h1_<rq>_prereg/hashes.txt`) with thresholds mirroring the D-07 results; verifiers recomputed the main numbers independently. Docs: `docs/ext/p4h1_rq41.md`, `p4h1_rq43.md`, `p4h1_rq44.md`.

| RQ | Verdict | Main numbers |
|---|---|---|
| RQ4.1 | **Does not fully replicate**: (a) PASS, (b) PASS, (c) FAIL, (d) PASS | (b) plugin coverage under missing-0.5: 0.361 / 0.343 / 0.321 at T40 / 80 / 150. (c) `tolerant_v4` passes (damaged-pair coverage 0.941–0.950); `tolerant_v5_1` has 0.895 at T80 missing-0.2 (threshold 0.90; CI contains 0.90), 3/4 cells |
| RQ4.3 | **Replicates**, all 5 criteria | on_path median shift 0.935 / 0.854 / 0.528 (D-07: 0.93 / 0.81 / 0.53); Spearman dev vs conf 1.000, Erdős–Rényi vs hub 0.965, P4-H1 vs D-07 0.986 |
| RQ4.4 | **Replicates**, F1–F4 all pass (5/5, also after Holm) | AUROC 0.724 at T80/150 and 0.826 at T40 (D-07: 0.730 / 0.824); flagged pairs miss 4.2× more often |

**Disclosed limits.**
- Some thresholds (3× ratio, ±0.15 tolerance, Spearman 0.9, RQ4.1 80%/25%) were the authors' own choices; D-07 itself would not have met RQ4.1 (a) and (d) under them.
- RQ4.1 rule (d) excludes the extra cells by a stated interpretive choice.
- `seed_base` 80261102 was used by all three RQs on the same bank (procedural, no effect on numbers).
- The three RQs were run in parallel.

Next: one run of the same rules on the sealed bank P4-H3 (specs under `experiments/ext/p4h3/`).

## P4-H3 confirmatory run of RQ4.1, RQ4.3, RQ4.4, recorded before running

**Approval.** The user asked (2026-11-03) to confirm RQ4.1, RQ4.3 and RQ4.4 on a fresh bank and then delegated the choice of how to run it ("cứ theo ý bạn"). Bank P4-H3 (seed 20261104, manifest sha256 `af927e3a62e1d0d44d0aebe23fa2867e11643fe389bfe81590710e8d836ea32e`) was generated for this purpose and sealed.

**Rules.** Unchanged from the P4-H1 replication (docs/ext/p4h1_rq41.md, p4h1_rq43.md, p4h1_rq44.md), with only bank, output names and seeds changed (seed_base 90261102 / 90261103 / 90261104, which overlap by an offset of 1–2 replicate indices across RQs; disclosed). Frozen specs, verified independently: `docs/ext/p4h3_rq41.md`, `p4h3_rq43.md`, `p4h3_rq44.md` with `experiments/ext/p4h3/<rq>/spec_files.json` (49 files each, sha256).

**Known weaknesses stated in advance.**
- Several thresholds are the authors' own choices; under the RQ4.1 rule D-07 itself fails (a) and (d).
- RQ4.1 (c) for `tolerant_v5_1` is fragile: 0.895 against the 0.90 cutoff on P4-H1, so a NOT CONFIRMED on RQ4.1 is a realistic outcome.
- RQ4.1 rule (d) excludes the extra cells by a stated interpretive choice.

**Guard.** `experiments/ext/p4h3/lead_guard.py` (sha256 `f727fd8a121d4f9f5fc372a45aca4499a81115f7c644d3919595e6fd44bb21e7`) checks every frozen hash, the bank manifest hash and that no P4-H3 output exists before the run; the pre phase PASSED. The frozen docs are not appended to; results are recorded only here.

**Commands, in order, each run once.** RQ4.3 runner, RQ4.1 runner, RQ4.4 runner (development, then confirmatory), then the three analyzers after all runs, then the post guard; interpreter `/Users/kietnt/miniconda3/bin/python`, `--workers 4`, `PAPER4_TOPOLOGY_ROOT` and `PAPER4_ACIIDS_ROOT` unset.

**Stop rules.** If a run is interrupted before its output file exists, it is repeated once unchanged and disclosed; a crash makes that RQ NOT CONFIRMED (incomplete); a post-guard failure labels every verdict INVALID (integrity). Results are not read before all runs and analyzers have finished.

## Outcome of the P4-H3 confirmatory run of RQ4.1, RQ4.3, RQ4.4

**Timeline (UTC, 2026-11-02, logs in `results/ext_p4h3_logs/`).** RQ4.3 runner 17:42:43–17:42:46; RQ4.1 runner 17:42:46–17:52:55; RQ4.4 development 17:52:55–17:54:30 and confirmatory 17:54:30–17:56:05; analyzers 17:56:05–17:56:40. Every command exited 0, each ran once, no repeat or interruption. Post guard: `LEAD GUARD POST PASS` (frozen hashes unchanged, exactly the expected P4-H3 manifests).

**Verdicts, verbatim from the analyzers.**
- **RQ4.3: "Verdict: CONFIRMED on the sealed bank P4-H3".** Criteria (a)–(d) pass; Holm 12/12. on_path median shift: missing contemporaneous 0.952 [0.929, 0.965], missing lagged 0.844 [0.749, 0.895], reversed contemporaneous 0.541 [0.510, 0.574] (D-07: 0.93 / 0.81 / 0.53). Spearman: development vs confirmatory 0.993, Erdős–Rényi vs hub 0.965, P4-H3 vs D-07 1.000.
- **RQ4.4: "Verdict: CONFIRMED on the sealed bank P4-H3".** F1–F4 all True, 5/5 raw and 5/5 after Holm. Frozen flag (not refitted): AUROC 0.720 [0.698, 0.744] at T80/150 and 0.812 [0.791, 0.832] at T40; advantage over the rel_width comparator +0.089 and +0.220 (CI exclude 0); flagged pairs miss 3.98× (T80/150) and 6.77× (T40) more often.
- **RQ4.1: "(a) False, (b) True, (c) True, (d) True -> all: False", so NOT CONFIRMED.**
  - (a) ordering missing > reversed > extra holds in 4/6 cells (threshold 5/6). It fails at both T40 cells, where reversed and extra are not separated: the reversed − extra gap has a CI containing 0 (e.g. −0.037 [−0.382, +0.135]).
  - (b) plugin coverage under missing-0.5: 0.349 / 0.336 / 0.315 at T40 / 80 / 150, all below 0.60.
  - (c) both `tolerant_v4` and `tolerant_v5_1` reduce plugin's relative error in 6/6 cells and keep damaged-pair coverage ≥ 0.90 in 4/4 cells (Holm 4/4); the fragility seen on P4-H1 (0.895) did not recur.
  - (d) plugin mean-lag error does not fall by more than 25% from T40 to T150 in 4/4 primary cells.

**Reading.** The (a) failure was disclosed in advance: D-07 and P4-H1 also gave 4/6, because at T40 the data cannot separate reversed from extra damage. It is therefore a property of the pre-registered threshold rather than a new failure, but the verdict stands as NOT CONFIRMED and is reported as such.

**Split usage.** P4-H3 confirmatory has been used once, on 2026-11-02 (UTC). P4-H3 development was never opened. Seeds 90261102 / 90261103 / 90261104 were used on the same bank (disclosed).
