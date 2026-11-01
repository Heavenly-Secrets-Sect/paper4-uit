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
