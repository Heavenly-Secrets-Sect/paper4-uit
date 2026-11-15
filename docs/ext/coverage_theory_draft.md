# Coverage of the tolerant_v5_1 width factor c: a topology-level proposition, its audit, and the 0.5 pre-scale

*Status of this document: no file was edited and no experiment was run. Repository facts are those relayed in the task facts. I did not re-open them. Items I did not verify are marked UNVERIFIED.*

## 0. Draft choice and bottom line

**Choice: merge A and B.** A is the base because it has three results that B lacks:
- the superuniformity lemma, which gives a calibration-conditional (PAC) bound with ties allowed;
- the stratified 10 ER + 10 SF treatment via AM-GM;
- an honest expected-coverage corollary.

From B I take four things:
- the unit score is a maximum over the two nested rates, so the statement holds for each rate separately;
- the guarantee is reported together with the abstention rate (c_hat = +inf);
- the level depends on the realised number of retained units N', not on the nominal 20;
- the lost-pair variant is stated as a separate, weaker option.

Both drafts' CRC remarks are dropped, because at N = 20 they are vacuous (see Section 4). B's density-ratio shift template is dropped, because no density ratio between two fixed disjoint banks can be estimated from 20 + 20 units.

**What the result is.** It is a textbook exchangeable-maximum / order-statistic fact. It is not new (see the references). It applies to a modified calibration protocol, not to the shipped rule or the frozen factors in `frozen_v4_v51.json`.

**Unresolved fatal flaws, stated rather than papered over:**
1. **Exchangeability (H1) fails for the realised banks.** The banks are fixed, curated, stratified, disjoint files with no documented sampling law.
2. **Design reuse (H2) fails.** TAU was probed on D-07H, the bank that also tunes c.
3. **The shipped rule is outside the theorem.** The shipped rule is a pooled pair-level grid quantile with a "max coverage minus 0.005" fallback that drops failed fits. The proved rule is unit-level, has a +inf escape and counts failures as misses.
4. **Possible vacuity.** For the proved rule, c_hat may be +inf in exactly the lost-pair cells that motivated the fallback. This cannot be settled without the simulation in Section 3 (check V1).

**Consequence for the claim.** The paper may not state a coverage guarantee for tolerant_v5_1. It may state empirical held-out coverage, and it may present the proposition as the conditions a guaranteed calibration would need (Section 6).

---

## 1. Proposition

### 1.1 Setting and notation

Fix a cell (T, key), where key ∈ {none, extra, missing, reversed} is the strongest stated damage component.

**Unit.** A unit is one topology together with everything random inside it:
- SEM coefficients, noise variances and edge lags;
- the damage draw;
- the data series;
- the bootstrap draws, including the `select_open` re-selection and the random orientations;
- fit status.

The nonnull set P = {(i,j), i≠j : |C_true,ij| > 0.1} depends on the SEM only.

**Runs.** For a damaged key a unit has two nested runs, r ∈ {0.2, 0.5}. For key none it has one run.

**Score ratio.** For run r and pair p ∈ P let mid_p and half_p be the PRESCALED interval (after the 0.5 pre-scale, before c). Define ρ_{r,p} = |C_true,p − mid_p| / half_p.
- If half = 0 and dist = 0, set ρ = 0.
- If half = 0 and dist > 0, set ρ = +∞. The pair is "lost": it is missed for every finite c.

**Coverage rule.** For finite c the interval is the closed set [mid − c·half, mid + c·half]. A pair is covered iff ρ ≤ c. The point c = +∞ denotes the trivial interval (−∞, +∞), defined independently of half and of fit status.

**Loss.** Let G = C_GRID (91 values, effective 0.5 to 5.0) and E = G ∪ {+∞}, a finite totally ordered set. Let n = |P| ≥ 1. For finite c ∈ G:
- M_r(c) = (1/n) Σ_{p∈P} 1[ρ_{r,p} > c], or M_r(c) = 1 if run r has status ≠ ok.
- M_r(+∞) = 0.

**Score.** Fix β ∈ (0,1) (default 0.05). Define S_r = min{c ∈ E : M_r(c) ≤ β} and the unit score S = max_r S_r.

**Calibration quantity.** Let N' be the number of calibration units with n ≥ 1 (the "retained" units). For δ ≥ 1/(N'+1) let k0 = ⌈(N'+1)(1−δ)⌉. Let ĉ be the k0-th smallest retained calibration score, so ĉ = max_k S_k when k0 = N'. Let F(s) = P(S ≤ s) for a fresh unit.

### 1.2 Assumptions (numbered)

- **H1 (sampling model).** The retained calibration units and the test unit are exchangeable. For parts (b) and (c) they are independent, with calibration units i.i.d. from a law P and the test unit drawn from P. H1 also requires that the seed streams give independent randomness across units. The probability space is the generator law and seed_base, not the fixed deterministic banks.
- **H1S (stratified variant, for part (c)).** The calibration design is 10 ER + 10 SF units, all independent: the 10 ER units i.i.d. from P_E and the 10 SF units i.i.d. from P_S. The test unit is drawn from the mixture (P_E + P_S)/2, or from one known profile.
- **H2 (frozen pipeline).** The map from unit to run outputs is identical for calibration and test. All design constants are chosen independently of the N+1 units: estimator, n_boot = 199, PRESCALE = 0.5, TAU = 6.6083, alpha_open, lag_max, H, tau_effect = 0.1, grid, β.
- **H3 (unit-level determinism).** The nonnull set, run statuses and scores are functions of the unit alone. Randomness across the bootstrap, damage and data is part of the unit, so within-unit dependence (shared fit, shared bootstrap resamples, nested rates) is integrated out.
- **H4 (monotone loss and escape).** For finite c, M_r is non-increasing in c, because the interval is closed with half ≥ 0. The point +∞ is a procedure change: it outputs (−∞, +∞), so M_r(+∞) = 0. Failed fits are counted as misses for finite c.
- **H5 (nonnull filter).** Units with n = 0 are dropped from calibration and test, and statements are conditional on the test unit having n ≥ 1 and on the realised N'. This is valid because n ≥ 1 is a function of the unit alone.
- **H6 (same target).** The test unit has the same T, the same stated-damage key (equal to the true single-kind damage, exact k), the same rate set {0.2, 0.5}, the same generator and the same clean scenario (no latent nodes, no measurement noise, Gaussian noise). The branch mixture (tolerant_sel_dd vs v3) has the same law in calibration and test.
- **H7 (grid).** Thresholds live on the finite totally ordered set E. Ties are allowed.

### 1.3 Statement

Conditional on the realised retained set, with the test unit retained:

**(a) Rank bound.** For any δ ≥ 1/(N'+1), P(S_test > ĉ) ≤ δ, under H1 (exchangeability suffices) and H2–H7. For the max rule (k0 = N') the bound is 1/(N'+1). That equals 1/21 ≈ 0.0476 at N' = 20 and 0.05 at N' = 19. At N' ≤ 18 it exceeds 0.05, so N' ≥ 19 is necessary for a 5% topology-level failure probability with the max rule.

**(b) Calibration-conditional (PAC) bound, max rule, independent units.** Conditional on the calibration set, the probability that a new topology satisfies S ≤ ĉ is F(ĉ). For every u ∈ [0,1), P(F(ĉ) ≤ u) ≤ u^{N'}. Hence E[F(ĉ)] ≥ N'/(N'+1), and F(ĉ) stochastically dominates a Beta(N',1) variable (equality in distribution if S is continuous, which is not the case on a grid). At N' = 20:

| u | bound on P(F(ĉ) ≤ u) |
|---|---|
| 0.80 | 0.8^20 = 0.0115 |
| 0.90 | 0.9^20 = 0.1216 |
| 0.95 | 0.95^20 = 0.3585 |

A 95%/95% statement (confidence 0.95 that F(ĉ) > 0.95) needs N' ≥ 59, since 0.95^59 = 0.0485 and 0.95^58 = 0.0510. The number of covered topologies in m fresh test topologies, given the calibration set, is Binomial(m, F(ĉ)). Unconditionally it stochastically dominates a beta-binomial, which is over-dispersed relative to Binomial(m, N'/(N'+1)).

**(c) Stratified design (H1S).**
- For the mixture test law with cdf F = (F_E + F_S)/2: P(F(ĉ) ≤ u) ≤ u^20 and E[F(ĉ)] ≥ 20/21.
- For a test unit of known profile E: P(F_E(ĉ) ≤ u) ≤ u^10 and E[F_E(ĉ)] ≥ 10/11 ≈ 0.909. The pooled max over 20 gives no more than this for a known profile.

**(d) What the event gives for the delivered interval.** On the event {S_test ≤ ĉ} with ĉ finite, at each rate the fraction of nonnull pairs of the test unit outside mid ± ĉ·half is ≤ β (lost pairs and failed fits included in the count).

**(e) Abstention accounting.** The failure event {S_test > ĉ} requires ĉ finite, so P(failure) ≤ δ is already a statement about the finite case. The trivial rule ĉ = +∞ satisfies every "abstain or valid" statement, so P(ĉ finite) must be reported. Conditional on a delivered finite interval, P(failure | ĉ finite) ≤ δ / P(ĉ finite). This is uninformative when P(ĉ finite) is small.

**(f) Expected miss fraction.** E[M_{test,r}(ĉ)] ≤ β + δ(1−β) for each rate r. The unit-weighted expected coverage per run is therefore ≥ (1−β)(1−δ), which is 0.9025 at β = δ = 0.05. This proposition does not give average pair coverage ≥ 0.95 at N' = 20.

---

## 2. Proof

**Step 0 (equivalence).** By H4 and H7, each M_r is non-increasing on the finite set E. The set {c : M_r(c) ≤ β} is therefore an up-set. It is non-empty because it contains +∞, and it has a minimum S_r. So M_r(c) ≤ β iff c ≥ S_r. Taking the maximum over r, max_r M_r(c) ≤ β iff c ≥ S. Hence {all runs of the test unit have miss fraction ≤ β at ĉ} = {S_test ≤ ĉ}.

**Step 1 (conditioning on retention).** Let O be the realised set of retained indices among 1..N+1, with N+1 ∈ O. The event {Ret = O} = {n_i ≥ 1 for i ∈ O, n_j = 0 for j ∉ O} is invariant under any permutation of O. Under exchangeability of the full vector, the conditional law of (U_i)_{i∈O} given {Ret = O} is therefore invariant under permutations of O. In the i.i.d. case the retained units are i.i.d. from P(· | n ≥ 1) and independent of the retention of the others. Scores are the same function of one unit (H2, H3), so the retained scores are exchangeable.

**Proof of (a).** Write N' = |O| − 1 and k0 = ⌈(N'+1)(1−δ)⌉. Then k0 ≤ N' because δ ≥ 1/(N'+1).
1. Call index j ∈ O "bad" if S_j is strictly greater than at least k0 of the other N' scores.
2. In the sorted order, the element at position m has at most m−1 strictly smaller values (ties only reduce this). So elements at positions m ≤ k0 are not bad, and #bad ≤ N'+1−k0 = ⌊(N'+1)δ⌋.
3. If S_{N+1} > ĉ, then S_{N+1} exceeds the k0 smallest calibration scores strictly, so N+1 is bad.
4. Badness of an index is a symmetric function of the score vector. By exchangeability P(j bad) is the same for all j ∈ O. So P(S_{N+1} > ĉ) ≤ P(N+1 bad) = E[#bad]/(N'+1) ≤ δ. ∎

**Lemma (superuniformity on a finite ordered set).** For S taking values in E with cdf F, P(F(S) ≤ u) ≤ u for every u ∈ [0,1).
*Proof.*
1. Let A = {s ∈ E : F(s) ≤ u}. Since F is non-decreasing, A is a down-set.
2. F(+∞) = 1 > u, so +∞ ∉ A.
3. E is finite, so A is empty or has a largest element s*.
4. If A is empty, the probability is 0.
5. Otherwise A = {s ≤ s*}. Every s ≤ s* has F(s) ≤ F(s*) ≤ u, and every element of A is ≤ s*. So P(F(S) ≤ u) = P(S ∈ A) = F(s*) ≤ u, because s* ∈ A.

Right-continuity is not used. In the presence of atoms, the case where F jumps above u at s_u is handled automatically: s_u ∉ A and A is the down-set below it. ∎

**Proof of (b).**
1. Conditional on the calibration set, ĉ is fixed. By independence of the test unit and Step 0, P(S_test ≤ ĉ | cal) = F(ĉ).
2. F is non-decreasing, so F(ĉ) = F(max_k S_k) = max_k F(S_k).
3. By independence of the calibration scores and the Lemma, P(F(ĉ) ≤ u) = ∏_k P(F(S_k) ≤ u) ≤ u^{N'}.
4. E[F(ĉ)] = ∫_0^1 P(F(ĉ) > u) du ≥ ∫_0^1 (1 − u^{N'}) du = N'/(N'+1).
5. For continuous S, F(S_k) is uniform and ĉ is a maximum of N' uniforms, giving Beta(N',1). Under atoms only the stochastic domination proved above holds.
6. The numerical values are 0.8^20 = 0.01153, 0.9^20 = 0.12158, 0.95^20 = 0.35849, and 0.95^59 = 0.0485 ≤ 0.05 < 0.95^58 = 0.0510. ∎

**Proof of (c).**
1. Let p_E = P_ER(F(S) ≤ u) and p_S = P_SF(F(S) ≤ u), with F the mixture cdf.
2. The mixture variable has cdf F, so by the Lemma (p_E + p_S)/2 = P_mix(F(S) ≤ u) ≤ u.
3. By AM-GM, p_E p_S ≤ ((p_E + p_S)/2)^2 ≤ u^2.
4. As in (b), F(ĉ) = max_k F(S_k), so P(F(ĉ) ≤ u) = p_E^10 p_S^10 = (p_E p_S)^10 ≤ u^20. Integrating gives E[F(ĉ)] ≥ 20/21, and E[F(ĉ)] is the marginal success probability for the mixture test unit.
5. For a known test profile E: ĉ ≥ c_E := the maximum of the 10 ER scores, so F_E(ĉ) ≥ F_E(c_E). Apply (b) to the 10 i.i.d. ER units with F_E to get P(F_E(c_E) ≤ u) ≤ u^10 and E ≥ 10/11. ∎

**Proof of (d).** Immediate from Step 0 and the definition of M_r.

**Proof of (e).** P(failure) = P(S_test > ĉ) ≤ δ by (a). Failure forces ĉ < S_test ≤ +∞, so ĉ is finite and P(failure and ĉ finite) = P(failure). Then P(failure | ĉ finite) = P(failure)/P(ĉ finite) ≤ δ/P(ĉ finite). ∎

**Proof of (f).** M ≤ β on {S_test ≤ ĉ} and M ≤ 1 otherwise, so E[M] ≤ β·P(S_test ≤ ĉ) + P(S_test > ĉ) ≤ β + (1−β)δ. ∎

**Variant ℓ (lost pairs excluded from the loss).** Define M'_r(c) as the number of non-lost nonnull pairs with ρ > c, divided by n. Lost pairs (half = 0, dist > 0) then no longer force S = +∞. Parts (a) to (c) hold verbatim with M' in place of M. The delivered statement changes to: the fraction of non-lost pairs outside the interval is ≤ β, so the total miss fraction is ≤ β + f, where f is the lost fraction. f is NOT controlled by c. Variant ℓ is reported only as an option, and any use must report f per cell.

**What the proofs use.** Only H1 to H7. Within-unit dependence enters nowhere because the unit loss is a single scalar. Nothing here says anything about the validity of the bootstrap itself.

---

## 3. Assumption audit

| # | Assumption | Status in OUR experiments | Reason | Simulation check |
|---|---|---|---|---|
| H1 | Units exchangeable / i.i.d., independent seed streams | **LIKELY VIOLATED** for the realised banks. Seed independence: TESTABLE IN SIMULATION. | Calibration is 20 fixed D-07H topologies and the test banks are fixed disjoint files from the same script. This is not a random partition of one pool, and no sampling law is documented. The repo itself says transfer between banks is "imperfect" (`r4mondrian.md`, item 3). A 20 vs 20 comparison has very low power, so non-rejection is not evidence of exchangeability. | V3: generate a pool of 300+ topologies with the actual bank script and compare random partitions with the fixed D-07H to D-07 split. Report a confidence interval for the difference in the max-score. V7: rerun under several seed_base values and check stream distinctness. |
| H1S | Stratified 10 ER + 10 SF, test from the 50/50 mixture | **PROVED** (the algebra in (c)). Whether the test banks follow a 50/50 mixture is UNTESTABLE from the facts. | AM-GM gives u^20. The known-profile guarantee is only 10/11. | V4: per-profile S_k and per-profile coverage of the pooled ĉ. |
| H2 | Pipeline frozen independently of the units | **LIKELY VIOLATED** | TAU was probed on the D-07H development bank that also tunes c (`v51.md:72-73, 213`). Per the relayed `narrow.md` line 249 (not opened by me), mult, alpha_open and PRESCALE were also chosen from D-07H probes. The project memory says the module of record was chosen after the P4-H2 run and all banks were used (UNVERIFIED by me). | V6: choose TAU on a disjoint bank, calibrate on D-07H, test on D-07, and compare c and coverage with the current protocol. Leave-one-topology-out re-selection of TAU is a diagnostic only. |
| H3 | Everything is a function of one unit; nonnull set depends on the SEM only | **PROVED** for the nonnull set (C_true is a function of the SEM). Bootstrap and data randomness being fresh per unit: TESTABLE IN SIMULATION. | `metrics.py` computes C_true from sem.B. Seeds are deterministic, so the probabilities refer to a hypothetical re-randomisation of seed_base. | V7 (seed audit). |
| H4 | Monotone loss, +∞ escape, failures counted as misses | **PROVED** for the modified rule. **LIKELY VIOLATED** by the shipped code. | Finite c gives a closed interval, so monotonicity holds. The shipped code has no +∞ point and drops failed fits (status ≠ ok). The proved rule is therefore not the rule that is run. | V5: failure-rate and lost-pair fractions per cell; recompute c with failures counted as misses and compare with the shipped c*. |
| H5 | Nonnull filter, conditional on realised N' | **PROVED** (conditioning argument). Realised N' is **TESTABLE IN SIMULATION** (a count). | Need N' ≥ 19 for the max rule at 5%. On D-07 the minimum n is 21, so units are probably not dropped, but D-07H counts were not read. | V8: report realised N' per (T, key). |
| H6 | Same T, key, rates, scenario, generator, branch mixture, exact stated k | **LIKELY VIOLATED** for P4-H runs with latent nodes, measurement noise, non-Gaussian noise (H6), misstated or combined damage. Generator equality D-07H vs evaluation: **UNTESTABLE** here (not read); checkable by a config diff. | Calibration has only pure single-kind, exactly stated damage in a clean scenario. | V9: coverage by branch; evaluate the frozen rule at rates 0.1 and 0.3, misstated k, mixed damage mapped to "missing", and T outside {40, 80, 150}. Report as limits. |
| H7 | Finite grid, ties allowed | **PROVED** | C_GRID has 91 values and +∞ is appended. | None. |
| Non-vacuity | All S_k finite, so ĉ is finite | **TESTABLE IN SIMULATION**; **LIKELY VIOLATED** in lost-pair cells | The runner's "lost pairs cap what any c can reach" comment and the max-0.005 fallback imply pooled maximum coverage < 0.955 in some cells. That means some pair-fraction is lost at every c, so S = +∞ is likely for at least one unit (not implied for every unit). With ~31 nonnull pairs, β = 0.05 allows at most 1 miss per run (0 if n ≤ 19, 2 at n = 55), in all 20 units and both rates. I expect ĉ near the grid cap (effective 5.0), well above the frozen effective 1.15 to 1.40. This expectation is NOT computed. | V1 (first check to run): fraction of units with S_k = +∞ at β ∈ {0.05, 0.10}, lost-pair fraction, and pooled maximum coverage per (T, key). |
| Pair-level dependence | Not an assumption | **PROVED not needed** | Integrated out by the unit-level loss. | V10: intraclass correlation of pair misses and variance split of S_k, for descriptive purposes only. |

**Simulation checks (V1 to V10).**
- **V1 (non-vacuity).** As in the table.
- **V2 (algebra and tightness of (a) to (c)).** Build a pool of 300+ fresh units with the actual generator, with profiles from the intended law. Repeat 5000 times: draw 20 units (and separately a fixed 10 ER + 10 SF design), set ĉ = max S_k, and estimate F(ĉ) on held-out units. Check E[F(ĉ)] ≥ 20/21 and P(F ≤ 0.8), P(F ≤ 0.9), P(F ≤ 0.95) ≲ 0.0115, 0.122, 0.358. Report the distribution of ĉ, the frequency of ĉ = +∞, and the width relative to the shipped c*. This checks the algebra only and cannot detect an H1 violation.
- **V3 to V9.** As listed in the table.
- **V11 (cost of K).** Plot 1/(N'+1) and the inflation of ĉ over the pooled c* for N' ∈ {10, 19, 20, 40, 80}.
- **V12 (replicates).** Run 3 replicates per topology and estimate the correlation of S_k across replicates and T, to get an effective N instead of assuming 20. Replicates share the DAG only (the SEM is redrawn), so they are not independent clusters either.

---

## 4. What the proposition does NOT guarantee

1. **Anything about the shipped tolerant_v5_1 or the frozen factors.** The shipped c* is a grid-rounded pooled pair-level quantile. It drops failed fits, weights topologies by n_k, uses a target that can fall to max-coverage − 0.005, and uses a TAU chosen on the same bank. The proved rule differs on every one of these points. The frozen factors 2.3 to 2.8 (effective 1.15 to 1.40) get no support.
2. **Anything about the reported bank coverage.** H1 is a superpopulation assumption. The reported coverage on D-07, P4-H1 to H6 is one realisation over fixed banks, and with roughly 20 units its standard error is about sd(M)/√20.
3. **Per-pair coverage, or average pair coverage ≥ 0.95.** Part (f) gives 0.9025 at N' = 20. The pair-pooled table figures (weights n_k) are a ratio estimator and are not controlled.
4. **Per-topology conditional coverage.** The statement is marginal over the calibration redraw and the test topology. For a single frozen ĉ, F(ĉ) is random: P(F(ĉ) ≤ 0.9) can be up to 0.12 and P(F(ĉ) ≤ 0.95) up to 0.36 at N' = 20. The same ĉ is reused in P4-H1 to H4 and H6, so these runs are not independent evidence about c.
5. **Per-profile coverage** beyond 10/11 (ER and SF distributions of ρ may differ because of hubs), **per-branch** coverage (v3 vs tolerant_sel_dd), **per-damage-subtype** or **per-rate** beyond the stated per-rate event.
6. **A non-trivial interval.** Without checking V1, ĉ may be +∞ or at the grid cap.
7. **Joint statements across cells.** The 12 (T, key) cells share SEMs, damage draws and C_true. A union bound over 12 cells would need δ/12 < 1/(N'+1), which is impossible for the max rule at N' = 20.
8. **Coverage of null pairs, or of pairs selected by estimated significance.** The nonnull set {|C_true| > 0.1} is an oracle defined by the truth.
9. **Scenarios outside H6.** Mixed or misstated damage, other rates, other T, latent nodes, measurement noise, non-Gaussian noise (P4-H6).
10. **A distribution-shift bound.** None is claimed. A bound would need a distance between bank laws that 20 + 20 units cannot estimate.
11. **The validity of the bootstrap or the width of the intervals.** Neither is addressed.
12. **A conformal-risk-control (CRC) guarantee.** CRC with loss bound B = 1 needs ((N'+1)α − 1)/N' = (21·0.05 − 1)/20 = 0.0025 mean unit loss on the calibration set at α = 0.05. That is far stricter than the code's 5% target, so a CRC statement is essentially vacuous at N' = 20.

---

## 5. The 0.5 pre-scale

### 5.1 Explanation

PRESCALE = κ = 0.5 (`ext_narrow.py:49`). `_prescale` replaces the percentile interval [lo, hi] by mid ± 0.5·half_raw, about mid = (lo+hi)/2. The runner then multiplies this prescaled half-width by c, tuned on the prescaled intervals. The calibration phase does not apply `calibrate_width` (guard `phase == 'main'`, `run_experiment.py:222`).

**Why it exists (engineering, from the relayed `ext_narrow.py` docstring and `narrow.md`).** At T = 40 with stated missing edges, tolerant_v4 over-covered (coverage 0.98, width about 6.5 vs about 3.5). v4's tuned factor `mod|40|missing` sat at the grid floor 1.0, so calibration could not narrow the interval. The pre-scale lets the raw grid 1.0..10.0 (step 0.1) reach effective factors 0.5..5.0 (step 0.05).

**No theory derives 0.5.** I found no document in `docs/` that derives it, and no probe that varies PRESCALE. It is a convenient round number, not an estimate.

**Does it bind in the module of record?** Apparently not.
- The frozen raw factors are 2.3 to 2.8, so the effective factors are 1.15 to 1.40.
- Neither the floor (0.5) nor the cap (5.0) is touched.
- The practical effect of κ = 0.5 is the finer effective step (0.05 instead of 0.1).
- Whether the max-0.005 fallback fires in a cell, and whether the grid-top coverage then differs between κ values (5.2 below), is not established.

### 5.2 Invariance statement

**Setup.** Let ρ¹ = |C_true − mid|/half_raw be the score at κ = 1. Then the prescaled score is ρ^κ = ρ¹/κ, because half_prescaled = κ·half_raw. Conventions for half = 0 are as in Section 1.1 and are κ-invariant.

**Assumptions for the invariance.**
- P1: the final interval is mid ± κc·half_raw with nothing additive and no clipping applied afterwards. This is established for `_prescale` and `inflate` from the facts, but I did not check other downstream components (UNVERIFIED).
- P2: the target is 0.95 on every compared grid, i.e. the fallback does not fire (max coverage ≥ 0.955 on each grid).
- P3: the cap does not bind: q ≤ 10κ for every compared κ, where q = ⌈0.95·n_pool⌉-th smallest pooled ρ¹.

**Statement 1.** For any fixed κ > 0, the pooled coverage is cov_κ(c) = cov_1(κc), i.e. the κ-rule on G is the κ=1 rule on the grid κG. Under P1 to P3:
- The tuned effective factor is e*_κ = κ·c*_κ = min{e ∈ κG : e ≥ q}. This is q rounded UP to the lattice κG, which has step 0.1κ.
- If q < κ (floor binds) then e*_κ = κ. The rule is then conservative but still valid.
- For two values κ, κ' the effective factors satisfy |e*_κ − e*_κ'| < 0.1·max(κ, κ').
- The final interval depends on (κ, c) only through the product κc, so the two are not separately identifiable from the data.

**Statement 2 (corrected from the draft).** Validity requires that the cap does not bind. The floor affects tightness only. The draft's wording "inside the grid on both sides" is wrong for the floor.

**Statement 3 (fallback breaks invariance).** If the fallback fires, the target is min(0.95, max_c cov(c) − 0.005), and max_c cov is evaluated at the top grid point. The top is 5.0 for κ = 0.5 and 10.0 for κ = 1. Two values of κ can then choose different targets, hence different effective factors, and Statement 1 fails. The fallback hides cap hits silently: it lowers the target instead of failing, so under-coverage at the cap is not flagged. Per-cell flags (floor binds, cap binds, fallback fires) are needed.

**Rounding is not negligible.** The expected overshoot is about half a step: 0.025 at κ = 0.5 and 0.05 at κ = 1. At an effective factor of 1.2 these are about 2% and 4% of the half-width. The draft's claim that the bias shows up mainly in efficiency is understated.

**The pooled rule is not a conformal guarantee.** The code takes an empirical ⌈0.95·n_pool⌉-th order statistic over about 600 to 1250 dependent pair scores, with no (N+1) correction. Statement 1 holds for any monotone rule of this form. The guarantee of Section 1 is a separate, unit-level statement.

### 5.3 Caveats

- **Provenance.** The relayed `narrow.md` line 249 says mult, alpha_open and PRESCALE = 0.5 were chosen from probes on D-07H before the D-07 timing smoke run. I did not open it. The project memory says all banks were used and the module of record was chosen after the P4-H2 run (UNVERIFIED by me). Therefore the sentence "κ = 0.5 was fixed before the held-out banks were scored" must not appear without checking the history.
- **Disclosure.** The D-07 smoke run (one topology, T = 40 missing) must be disclosed.
- **If κ was chosen after seeing held-out results:** H2 fails formally. By Statement 1 the damage is bounded by max(0.1κ, 0.1κ') in effective units only when neither cap nor floor binds. Where they bind, the damage is unbounded.
- **Bigger issue than κ itself.** The design probes (TAU, mult, alpha_open, κ) and the calibration of c share the D-07H bank. Even if κ was never touched, this is a selection effect on the calibration set and breaks exchangeability with a fresh topology. Remedy: split off a design bank, or use a new bank.
- **Suggested wording.** "κ = 0.5 re-parameterises the calibration grid so that the effective factors range from 0.5 to 5.0 in steps of 0.05. Only the product κc enters the interval. It was selected for convenience on the calibration bank, and Section X reports the sensitivity."

### 5.4 Sensitivity-study design (not run)

**Status.** All banks have been used, so a confirmatory study needs a fresh bank (call it D-08) with a new seed and a pre-registration written before running. Otherwise label it exploratory. The draft's single "Arm A" varied κ on the raw grid, which changes range and lattice at once (a confound), and its 2% decision margin would trigger from rounding alone. The corrected design separates the factors.

| Arm | What varies | What is fixed | Purpose |
|---|---|---|---|
| S0 (unit test of invariance) | κ ∈ {0.25, 0.5, 1, 2}; raw grid = E/κ, where E is a fixed effective lattice (0.05..5.0, step 0.05); no rounding of the raw grid to 2 decimals, or the test breaks | effective lattice, range and fallback target | The outputs must be identical up to float tolerance 1e-9. Any difference is an implementation bug (additive terms, clipping, rounding). |
| S1 (lattice only) | step ∈ {0.025, 0.05, 0.1, 0.2} | range [0.5, 5.0] | Measure the rounding-induced shift in coverage and width; expected overshoot is step/2. This is the benchmark for judging any other difference. |
| S2 (range only) | floor ∈ {0.25, 0.5, 1.0}, cap ∈ {2.5, 5, 10} | step 0.05 | Record how often floor, cap and fallback bind per (T, key), and the resulting coverage. |
| S3 (proposed replacement) | κ = 1 with the effective grid 0.3..5.0, step 0.05 | | Removes the constant and the "prove 0.5" question. |

**Data and cells.** Calibration on D-07H development (20 topologies). Evaluation on D-08 (confirmatory) or D-07 development (exploratory). T ∈ {40, 80, 150}; kinds {none, extra, missing, reversed}; rates {0.2, 0.5}.

**Stability of c*.** Use a topology-cluster bootstrap on the 20 clusters, not repeated 10/10 splits, which overlap and understate uncertainty. The three replicates share the DAG but are not independent clusters.

**Metrics per (arm, T, kind).** Coverage, interval score, mean width, effective factor κĉ, and the floor, cap and fallback flags. Paired differences use a topology-cluster bootstrap.

**Decision rule (pre-register).**
- Judge differences against the rounding bound from S1, not a fixed 2% margin.
- Drop the constant and calibrate on an effective grid (S3) if: the floor binds at κ = 0.5 in some cell (κĉ ≤ 0.55); S0 differs between κ values (bug); or in a non-binding cell the coverage differs by more than 0.01 beyond the rounding bound with a CI that excludes 0.
- Keep it as a pure re-parameterisation if all cells have κĉ ≥ 1.15, S0 agrees, and the CIs of the paired differences cover 0.
- In either case S3 is recommended, since it costs nothing.

---

## 6. Open risks and how strongly the paper may claim coverage

**Open risks.**
1. H1 and H2 are violated by the realised design and cannot be repaired after the fact.
2. Possible vacuity (ĉ = +∞ or at the cap), particularly missing/0.5.
3. The shipped rule and the proved rule are different objects. The frozen factors would have to be recomputed with the proved rule, which is required, not optional.
4. The sample size is 20 topologies with nested rates. The information per topology is nearer one run than two. A 95%/95% PAC statement for the max rule needs N' ≥ 59, and the referee's estimate of about 100 topologies for a non-trivial width is plausible (I did not derive it).
5. Grid direction: the claim that rounding up is conservative holds within the proposed rule. The frozen factors came from a different statistic, so the direction relative to the proposed rule is not established. `r4mondrian.md` reports rounding shifts of up to −0.014 in coverage and q_M0 differing from the frozen factor by 0.034 to 0.042 (I did not read `ext_r4mondrian.py` or `q_table_rep3.json`).
6. Branch-conditional coverage (r < TAU and k_miss > 0) is uncontrolled and is the most likely place for under-coverage.
7. Seeds are deterministic. The experiment is one realisation of a hypothetical randomisation, so replications under other seed_base values are needed.
8. Real misspecification is structured (the strong or confounded edges go missing, the stated count is uncertain), not a uniform random subset.

**Recommended claim ladder.**
- **For the existing results (tolerant_v5_1, frozen factors, P4-H):** an empirical claim only. "Factors were tuned on the D-07H development bank and evaluated on held-out banks." Report coverage with topology-cluster bootstrap CIs, disclose design reuse, and do not use the words "guarantee", "valid" or "conformal".
- **For the proposition:** present it as what a guaranteed calibration would require. The strongest wording the proof supports is a marginal-over-new-topologies statement. For a new topology drawn from the same generator law, in the clean single-kind stated-damage scenario, with probability at least 1 − 1/(N'+1) over the redrawn calibration set and the new topology, each rate run has at most β of its nonnull pairs outside the interval. It must be accompanied by the abstention rate P(ĉ finite).
- **Not allowed:** per-pair coverage, conditional-on-topology coverage, per-profile coverage (10/11 at best), per-branch coverage, a joint guarantee across cells, or a 95% average pair coverage.
- **To earn the marginal wording for real results:** pool D-07H and D-07 (and ideally a new bank), randomly partition them, select TAU on a third bank, use unit-level scores with failures as misses, report realised N', and show via V1 that ĉ is finite and useful.

---

## 7. References

**OPENED** (arXiv abstract pages fetched on 2026-11-14; only abstracts were read, not the full texts or the proofs):
- Barber, R.F., Candès, E.J., Ramdas, A., Tibshirani, R.J. *Conformal prediction beyond exchangeability*. arXiv:2202.13415 (v5, 17 Mar 2023). The abstract page shows no journal reference. Relevance: weighted conformal quantiles when exchangeability fails (a route to a shift bound, not applied here).
- Angelopoulos, A.N., Bates, S., Fisch, A., Lei, L., Schuster, T. *Conformal Risk Control*. arXiv:2208.02814 (v4, 13 Jun 2025). Relevance: expected monotone loss control (Section 4 item 12).
- Dunn, R., Wasserman, L., Ramdas, A. *Distribution-Free Prediction Sets for Two-Layer Hierarchical Models*. arXiv:1809.07441 (v4); the page comments state it is accepted to JASA. Relevance: the group as the unit for conformal inference. No theorem here depends on it.
- Bates, S., Angelopoulos, A., Lei, L., Malik, J., Jordan, M. *Distribution-Free, Risk-Controlling Prediction Sets*. arXiv:2101.02703 (v3, Aug 2021). Relevance: high-probability, calibration-conditional risk control for monotone losses.
- Angelopoulos, A.N., Bates, S., Candès, E.J., Jordan, M.I., Lei, L. *Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control*. arXiv:2110.01052 (v5, 29 Sep 2022). Relevance: risk control as multiple testing.
- Vovk, V. *Conditional validity of inductive conformal predictors*. arXiv:1209.2673; the comments say it is to appear in the ACML 2012 proceedings. The abstract page does not mention a Beta distribution, so the Beta/PAC result in (b) is proved directly above and is not attributed to this paper.
- Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R.J., Wasserman, L. *Distribution-Free Predictive Inference For Regression*. arXiv:1604.04173 (rev. Mar 2017). Relevance: split-conformal finite-sample coverage.

**UNVERIFIED** (not opened by me):
- Vovk, V., Gammerman, A., Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer.
- Tibshirani, R.J., Barber, R.F., Candès, E.J., Ramdas, A. (2019). Conformal prediction under covariate shift. NeurIPS. (Relevant only to the dropped shift template.)
- Loh, W.-Y. (1987). Calibrating confidence coefficients. JASA. Hall, P. (1992). *The Bootstrap and Edgeworth Expansion*. Springer. (Named by a referee as prior art on calibrating bootstrap intervals.)
- Venue and year details beyond what the opened arXiv pages show (for example the JASA 2023 issue of Dunn et al., or the AoS issue of Barber et al.).

**Repository sources, relayed from the task facts and not re-opened by me:**
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/run_experiment.py` (calibration 314-341, frozen override 444-448, guard at 222).
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/src/paper4/methods.py` (`calibrate_width`, `inflate`).
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/src/paper4/ext_narrow.py` (PRESCALE, `_prescale`).
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/src/paper4/ext_v51.py`.
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/v51/frozen_v4_v51.json`.
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/docs/ext/v51.md` (lines 72-73, 189, 213).
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/docs/ext/r4mondrian.md` (Honest limits).
- `/Users/kietnt/Desktop/Workspace/Paper4_UIT/docs/ext/narrow.md` (line 249 and the probe values: relayed only, never verified by the referee or me).

Not read by anyone: `ext_r4mondrian.py`, `q_table_rep3.json`, and the D-07H generator block.