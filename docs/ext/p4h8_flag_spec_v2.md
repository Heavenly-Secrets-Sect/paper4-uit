# P4-H8 flag specification, version 2 (corrects two defects, extends to lags 1 to 3)

Written 2026-11-15 **before any v2 dump was read**. Supersedes [p4h8_flag_spec.md](p4h8_flag_spec.md) for the final claim; version 1 and its result stay on record.

## Why a second version
After the version 1 test, a per-scenario breakdown requested by the user exposed two defects in the version 1 dump script (found by inspecting the stored features, not by looking at which model would score better):
1. The stated-damage counts (`k_miss`, `k_extra`, `k_rev`) were read from the raw damage record, which holds only the kind, the rate and a total k, so all three features were 0 in every row. The flag therefore knew nothing about the stated damage.
2. The stated-skeleton features used only the contemporaneous (oriented) edges; lagged edges, about 70% of all edges, were ignored, so "adjacent" and "has a path" were true for only 2% of the non-null pairs.
Version 1 still beat the old flag overall (AUROC 0.869 vs 0.792) but did not meet its criterion (T = 40: +0.014). Version 1 results are not discarded.

## Changes
- Stated counts from `methods.stated_counts` (0 / 4 / 11 for missing and extra at rates 0 / 0.2 / 0.5, and the reversal count for reversed).
- New features: adjacent in any stated edge (`adj_any`), undirected distance in the stated skeleton (`und_dist`); the oriented-only features stay.
- One model pooled over lags 1 to 3 (lag and log T are features), trained on the calibration dumps of the three lags (P4-H8 calibration split, 550 topologies each), labels from the frozen marginal factors of each lag (`p4h8_frozen_lag{1,2,3}.json`). Model and hyperparameters selected by grouped 5-fold CV on a 40% sample of the calibration topologies (to bound the cost), the final fit on all of them.
- Fresh evaluation sets, each used once for the flag: lag 1 on the **P4-H7 test split** (150 topologies, sealed until now; the version 1 flag already looked at P4-H8 test lag 1), lags 2 and 3 on the P4-H8 test split of the same lag (used before only for the guarantee study, not for any flag). Stated, not hidden.
- Reported per lag, per T, per stated kind and per damage level (rate 0.2 and 0.5, identified by the stated count of the kind), as AUROC of the new flag, of the old frozen flag and of minus the final width, with the cluster bootstrap by topology; cells with fewer than 20 missed pairs are reported as "too few", not dropped silently.

## Success criterion (unchanged in spirit, now per lag)
For each lag, the new flag beats the old flag by at least 0.03 AUROC in each T group {19-30}, {40}, {80-150} present at that lag, with the 95% cluster-bootstrap interval of the difference above 0. Whatever the outcome, all numbers are reported.

## Known weaknesses
One generator, clean Gaussian, 14 nodes; labels depend on the guarantee-study factors; the flag is not evaluated under measurement noise (where the intervals themselves lose their guarantee).
