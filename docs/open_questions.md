# Open questions for Paper 4

These items are intentionally unresolved. The repository is a context baseline, not an approved study protocol.

## Research direction

- Is the central contribution robust effect estimation, uncertainty calibration, or a different question?
- Which effect is the target: a structural coefficient, a lag-specific response, a direct effect, a total effect, or another estimand?
- What claim should Paper 4 own, and what should be deferred to Paper 5?

## Model and method

- Which dynamic structural model is in scope (linear/nonlinear, stationary/nonstationary, observed/latent variables)?
- What lag range and stability assumptions are appropriate?
- How will false, missing, and reversed skeleton edges be generated and stratified?
- Which estimator and candidate baselines will be compared?
- How will uncertainty across plausible skeletons be represented, and how will nominal coverage and interval width be assessed?
- How will data used for structure selection be separated from data used to fit/evaluate effects?

## Data and release

- Which synthetic generator conditions and sample sizes are in scope?
- Is the real/semi-synthetic panel included for a descriptive case study, and with what wording?
- Which source data can be copied or published, under what license and approval?
- What output schema should later be shared with Paper 5?

## Provisional implementation defaults (pending supervisor decision)

The code needs a value for each item below to run. These are defaults, not decisions; each is a parameter or an isolated function so it can change without touching the rest.

1. **Lag of an edge.** The shared interface (plan section 7) carries adjacency and orientation but no lag. Default (`estimator.parent_terms`): every adjacent pair admits lags 1..lag_max in both directions, since time order already fixes the direction of a lagged edge; orientation only decides the contemporaneous term (u -> v adds u_t to the equation of v); every node keeps its own lags. An oracle reference with the true lags (`true_skeleton(sem, with_lags=True)`) is kept for comparison.
2. **Meaning of "strength".** Default: report both edge coefficients (per edge and lag) and the cumulative effect C(H) of every ordered pair (`metrics.evaluate`). A missing true edge has no coefficient in the fitted model, which is why the effect level is also reported.
3. **Inflation function for extending T.** Not implemented until defined. Coverage should be measured on generator data with known truth; data replicated from one series would shrink intervals artificially.
4. **Reversal on a dynamic graph.** A lagged edge cannot point backwards in time. Default (`skeleton.damage`): `reversed` flips contemporaneous edges only, with k counted from the number of contemporaneous edges; `reversed_any` (all oriented pairs) is kept as an ablation. Damaged pairs and their true lags go to a private log that only the evaluation reads; the interface record carries kind, rate and k.
5. **Comparison for "narrower" intervals in RQ4.2.** Default: compare widths only among methods that reach nominal coverage, including a fixed inflation of the point-reporting interval.
6. **Generator draws.** One lag per edge: contemporaneous with probability q0 = 0.3, otherwise uniform on 1..lag_max (lag_max = 2); cross coefficients |b| ~ U(0.3, 0.8) with random sign; own lag-1 coefficients ~ U(0.2, 0.6); noise variances ~ U(0.5, 1.5); lagged part shrunk until the companion spectral radius is below 0.9.

