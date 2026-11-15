# P4-H7 specification: calibration with a topology-level coverage guarantee

Written 2026-11-15, before any P4-H7 topology was run. Status: DRAFT until frozen (see "Freeze"). Context: the teachers asked for a sufficient condition for correct coverage and an explanation of the 0.5 factor ([coverage_theory_draft.md](coverage_theory_draft.md), [coverage_theory_v1.md](coverage_theory_v1.md)). V1 showed the frozen v5.1 factors are pair-pooled quantiles that match the median unit score, so they carry no topology-level guarantee.

## Bank
`data/topology_bank/P4-H7`, made by `data/topology_bank/generate_scalable_bank.py --seed 20261115 --splits design=60,calibration=150,test=150`. 360 topologies (14 nodes, 21 edges; half Erdős–Rényi, half scale-free hub), all drawn i.i.d. from one generator law and assigned to splits by a seeded permutation stratified by profile. No overlap with any earlier bank (edge sets compared). Manifest SHA-256 `8286170e4dd297285183d016c3619083137090f583ea36b425fc15e4e6866220`.

| Split | n | Use |
|---|---|---|
| design | 60 | all choices below that are not fixed here; the 0.5 sensitivity study; exploratory looks |
| calibration | 150 | computing the guaranteed factors (one pass, no tuning on it) |
| test | 150 | **one** confirmatory run with the frozen factors. Sealed: no look, probe or descriptive statistic before the freeze. |

## Method under study
SRCI (`tolerant_v5_1`, code unchanged). Only the width factor c changes: instead of the pooled pair-level quantile, c is a **unit-level order statistic**.

- Unit = one topology with everything random inside it (SEM draw, damage draw, data, bootstrap). Per run (topology, damage rate r) and pair p in the non-null set P (|C_true| > 0.1): ρ_{r,p} = |C_true − mid| / half, with half taken after the fixed pre-scale. A pair is missed at factor c iff ρ > c.
- Run score S_r(β) = smallest c on the grid with at most a fraction β of P missed. Failed fits count as misses at every finite c. Unit score S = max over the two damage rates.
- Factor ĉ(k0) = k0-th smallest unit score among the N' retained calibration units. Cells: T × stated kind (none, extra, missing, reversed), as before.
- Statement the proof supports (see the draft): for a new topology from the same law, in the clean single-kind stated-damage scenario, P(S_test ≤ ĉ) ≥ k0/(N'+1); conditional on the calibration set, F(ĉ) stochastically dominates Beta(k0, N'+1−k0).

## Pre-registered choices (fixed now)
- Headline: β = 0.10. Two reported versions of ĉ:
  - **marginal**: k0 = ⌈(N'+1)·0.90⌉ (δ = 0.10);
  - **PAC**: smallest k0 with Beta(k0, N'+1−k0) cdf at 0.90 ≤ 0.05 (with confidence 0.95 over the calibration draw, at least 90% of new topologies have at most 10% of non-null pairs missed).
- Also reported (not headline): β = 0.05, and the frozen pooled factors of tolerant_v5_1 for comparison.
- T ∈ {19, 30, 40, 80, 150}; stated kind ∈ {none, extra, missing, reversed}; rate ∈ {0.2, 0.5} (none: 1 run); H = 4; n_boot = 199; tau_effect = 0.1; lag_max = 1 (matches the real panel). Secondary arm lag_max = 2 at T ∈ {40, 80, 150}.
- Factor: the exact order statistic of the unit scores (no grid, so the pre-scale constant 0.5 plays no role in the guarantee), rounded UP to 3 decimals, applied to the half-width of the pre-scaled interval. The shipped pooled rule is recomputed on the same calibration split as the comparator.
- Scenario: clean, Gaussian noise, no latent nodes (hypothesis H6). Robustness arms on the test split, **labelled exploratory violations of H6**: Student-t(4) and Laplace noise (E2 laws), and misstated damage.
- Gate: calibration needs N' ≥ 59 retained units per cell for the PAC version (0.95^59 < 0.05); fewer ⇒ report "no PAC factor" for that cell.
- Metrics on the test split: unit-level hit rate P(S_test ≤ ĉ) with a 95% exact binomial interval; fraction of non-null pairs missed per unit (distribution); pooled pair coverage; interval score and width relative to the frozen v5.1 and to plugin. Cluster (topology) bootstrap for all differences.
- Success criteria (decided now): (i) the marginal hit rate's binomial interval contains or exceeds 0.90 in at least 80% of cells and no cell's upper limit is below 0.85; (ii) the PAC factor's cost is reported honestly even if the width is much larger than the frozen factor. A failure of (i) is reported as such and the guarantee claim is withdrawn for those cells.

## Pre-scale sensitivity (design split, exploratory)
Arms from the draft: S0 invariance test, S1 lattice step, S2 floor/cap, S3 effective grid without a pre-scale constant. Output: tables of coverage, interval score, width and the floor/cap/fallback flags. The decision rule is in the draft (section 5.4). Results do not touch the test split.

## Order of work and freeze
1. Design split: pre-scale sensitivity; check the feasibility of β and δ. (May run now.)
2. Calibration split: compute ĉ for all cells; write `experiments/calibration/p4h7_frozen.json`.
3. Freeze: SHA-256 of this file, of the frozen factors and of the runner config recorded in `docs/decision_rules.md`. Changing any choice above after the freeze ⇒ the test split is no longer confirmatory.
4. Test split: one run. Needs the user's approval first. Implementation (decided at the freeze): `experiments/ext/coverage_theory/p4h7_units.py --split test --confirm-frozen` dumps the per-pair distances and half-widths; `p4h7_test_eval.py` computes hit rates, interval scores and widths for every factor variant offline from that dump (interval score and width follow exactly from dist, half and the factor for a symmetric interval), so no extra method registration is needed.

## Known weaknesses stated in advance
Exchangeability holds by construction of the bank (i.i.d. topologies, random split), but only within this generator law: it says nothing about real panels. Replicates share the DAG and are not independent clusters, so one run per topology is used. The generator, damage mechanism and clean Gaussian scenario are those of the earlier banks.
