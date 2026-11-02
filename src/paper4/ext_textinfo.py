"""Text-informed tolerant module (direction "textinfo"): per-pair side information instead of a bare count.

Module v4 reads only the stated damage COUNT and relaxes the skeleton blindly within that budget:
all lags of all nodes when edges are said to be missing, residual-correlation repair, reversal
draws among significant contemporaneous pairs. Paper 1 already extracted text evidence for the
prior graph (confidence, number of sources, conflicts, verifier rejections, co-mentions). This
module reads that evidence as **per-pair side information** and spends the same budget on the
most suspicious pairs first. It makes no LLM call; the side information is precomputed.

Side information, attached by the caller to ``skel.damage["text"]`` (unknown keys are ignored by
every other method), with unordered pair keys ``"u-v"`` (u < v, node indices):

- ``doubt``:      score per skeleton pair; higher = more likely extra or reversed.
- ``suspicion``:  score per non-adjacent pair; higher = more likely a missing edge.
- ``sign``:       optional +1 / -1 per skeleton pair (sign of the relation stated by the text).

Only the ranking of the scores matters: they are turned into rank-based normal scores z
(van der Waerden), so any monotone scale works (heuristic text scores in [0, 1], or synthetic
scores in simulation). A pair's weight is w = exp(gamma * z), normalised to mean 1 within its set.
With no text, or tied scores, every weight is 1.

What changes relative to v3/v4 (budget = the stated counts, exactly as in v4):

1. **Stated missing edges: targeted lag opening.** Instead of every node's lags in every equation,
   the lag blocks of the off-skeleton pairs are opened in the order of p / w, where p is the
   structural adjacency p-value of the pair (``diagnose.structural_pvalues``: lag-block Wald tests
   in the skeleton's all-lag structural fit and the correlation of the structural residuals, Sidak)
   and w the suspicion weight. This is the ordering of weighted Benjamini-Hochberg (Genovese,
   Roeder and Wasserman 2006): p-value weights with mean 1 keep the FDR guarantee whatever their
   quality, and good weights raise power. Opened set = the K first pairs,
   K = max(ceil(OPEN_MULT * k_missing), #weighted-BH rejections at Q_OPEN), capped by the number
   of off-skeleton pairs. When the all-lag fit cannot be made, every lag is opened (v4).
2. **Contemporaneous repair ranked by text**: weighted BH (same weights) on the correlations of
   the all-lag structural residuals, at most k_missing pairs, random direction per draw (as v4).
3. **Stated reversals: weighted reversal draws.** The pool is v3's (significant contemporaneous
   coefficients). Each bootstrap draw flips k_reversed pairs sampled without replacement with
   probability proportional to the doubt weight (Gumbel top-k), skipping flips that create a cycle.
   Uniform weights give exactly v3's draw.
4. **Optional sign pruning** (``textinfo_sign``): bootstrap draws whose fitted total coefficient of
   a pair contradicts a *confident* sign hint (a hint on a pair whose doubt is in the lower half,
   i.e. the text believes the edge) are discarded, unless that would discard more than half of
   the draws (then nothing is pruned).

Stated extra edges are handled as in v4 (the skeleton's own terms): dropping a true edge costs
bias, keeping a null one only variance.

Variants:
- ``textinfo``       the module (targeted opening, weighted repair, weighted reversal draws);
- ``textinfo_all``   every lag opened as in v4; text acts only through the repair ranking and the
                     reversal draws (the "safe" variant: it can lose no lagged term);
- ``textinfo_null``  ``textinfo`` with every weight 1 (text ignored): isolates the part of any gain
                     that comes from the targeted opening alone;
- ``textinfo_sign``  ``textinfo`` plus sign pruning.
With nothing stated missing the three first coincide on reversal cells except for the weights, and
with nothing stated missing or reversed all variants reduce to v3 (the skeleton's own terms).

Methods see only the data, the skeleton, its stated counts and the attached side information.
"""
from __future__ import annotations

import math

import numpy as np

from .diagnose import structural_pvalues
from .effects import cumulative, irf
from .estimator import fit_equations, parent_terms, percentile_interval, simulate_from_fit, soft_terms
from .methods import (ALPHA, MethodResult, _failed, _fisher_p, _too_few, contemporaneous_pool,
                      stated_counts)
from .skeleton import Skeleton, _creates_cycle

GAMMA = 0.5        # weight temperature: w = exp(GAMMA * z); chosen in the D-07H probe
OPEN_MULT = 5.0    # opened lag blocks >= OPEN_MULT * stated missing pairs; chosen in the D-07H probe
Q_OPEN = 0.1       # weighted-BH level for opening beyond the floor
Q_REPAIR = 0.1     # weighted-BH level of the contemporaneous repair (v4 uses 0.1)
OPEN_MODE = "targeted"  # "targeted" (text-and-data ordered lag blocks) or "all" (every lag, as v4)


# --------------------------------------------------------------------------- side information

def pair_key(u: int, v: int) -> str:
    a, b = (u, v) if u < v else (v, u)
    return f"{a}-{b}"


def _norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation, |error| < 1.2e-9)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549671010229583e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    lo = 0.02425
    if p < lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - lo:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def normal_scores(scores: dict[str, float], keys: list[str]) -> dict[str, float]:
    """Rank-based normal scores (van der Waerden, mid-ranks for ties) of ``scores`` over ``keys``.
    Missing keys get the lowest-information value: the median rank (z = 0 when ties are broken
    evenly). All zero when there are fewer than two distinct scores."""
    if not keys:
        return {}
    vals = np.array([float(scores.get(k, np.nan)) for k in keys])
    known = np.isfinite(vals)
    if known.sum() < 2 or np.unique(vals[known]).size < 2:
        return {k: 0.0 for k in keys}
    fill = np.nanmedian(vals)
    vals = np.where(known, vals, fill)
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(len(vals))
    ranks[order] = np.arange(1, len(vals) + 1)
    for v in np.unique(vals):  # mid-ranks for ties
        idx = vals == v
        ranks[idx] = ranks[idx].mean()
    m = len(vals)
    return {k: _norm_ppf(r / (m + 1)) for k, r in zip(keys, ranks)}


def weights(scores: dict[str, float] | None, keys: list[str], gamma: float) -> dict[str, float]:
    """w = exp(gamma * z), normalised to mean 1 over ``keys``. All 1 without scores or with gamma = 0."""
    if not scores or gamma == 0 or not keys:
        return {k: 1.0 for k in keys}
    z = normal_scores(scores, keys)
    w = {k: math.exp(gamma * z[k]) for k in keys}
    mean = sum(w.values()) / len(w)
    return {k: v / mean for k, v in w.items()}


def weighted_bh(pvals: dict[str, float], w: dict[str, float], q: float) -> tuple[list[str], int]:
    """Keys ordered by p / w, and the number of weighted-BH rejections at level q."""
    keys = sorted(pvals, key=lambda k: (pvals[k] / max(w.get(k, 1.0), 1e-12), k))
    m = len(keys)
    n_rej = 0
    for rank, k in enumerate(keys, start=1):
        if pvals[k] / max(w.get(k, 1.0), 1e-12) <= q * rank / m:
            n_rej = rank
    return keys, n_rej


# --------------------------------------------------------------------------- module pieces

def _off_pairs(skel: Skeleton) -> list[tuple[int, int]]:
    return [(u, v) for u in range(skel.n) for v in range(u + 1, skel.n) if not skel.is_adjacent(u, v)]


def weighted_repair(residuals: np.ndarray, skel: Skeleton, cap: int, w: dict[str, float],
                    q: float = Q_REPAIR) -> list[tuple[int, int]]:
    """v4's residual-correlation repair, with weighted BH: non-adjacent pairs whose structural
    residuals are correlated, ranked by p / w, at most ``cap`` of them."""
    if cap <= 0:
        return []
    m = residuals.shape[0]
    corr = np.corrcoef(residuals.T)
    pv = {pair_key(u, v): _fisher_p(corr[u, v], m) for u, v in _off_pairs(skel)}
    keys, n_rej = weighted_bh(pv, w, q)
    out = []
    for k in keys[: min(n_rej, cap)]:
        u, v = map(int, k.split("-"))
        out.append((u, v))
    return out


def _weighted_flip(skel: Skeleton, pool: list[tuple[int, int]], k: int, w_pool: np.ndarray, rng) -> Skeleton:
    """Flip k oriented pairs of ``pool`` sampled without replacement with probability proportional
    to ``w_pool`` (Gumbel top-k order), skipping flips that would create a cycle. With equal weights
    the order is a uniform random permutation, as in v3."""
    out = skel.copy()
    if not pool or k <= 0:
        return out
    keys = np.log(np.maximum(w_pool, 1e-12)) + rng.gumbel(size=len(pool))
    flipped = 0
    for idx in np.argsort(-keys):
        if flipped == k:
            break
        u, v = pool[idx]
        trial = (out.oriented - {(u, v)}) | {(v, u)}
        if not _creates_cycle(trial, skel.n):
            out.oriented = trial
            flipped += 1
    return out


def _total_coef(B: np.ndarray, u: int, v: int) -> float:
    """Sum of every fitted coefficient linking u and v, in both equations (contemporaneous and lagged).
    Orientation does not change the sign of a contemporaneous link, and lag blocks are admitted in
    both directions, so this is the sign the text refers to."""
    return float(B[:, v, u].sum() + B[:, u, v].sum())


def _bootstrap(data, fit, H, n_boot, rng, refit, sign_pairs=None):
    """Residual bootstrap as ``estimator.bootstrap_C`` that also returns, per draw, whether the draw
    respects every sign hint in ``sign_pairs`` [(u, v, sign)]."""
    p = fit.B.shape[0] - 1
    refit = refit or (lambda x: fit_equations(x, fit.terms, p, fit.penalties))
    out, ok_sign = [], []
    tries = 0
    while len(out) < n_boot and tries < 3 * n_boot:
        tries += 1
        fb = refit(simulate_from_fit(fit, data, rng))
        if fb.status == "ok":
            out.append(cumulative(irf(fb.B, H), H))
            if sign_pairs:
                ok_sign.append(all(np.sign(_total_coef(fb.B, u, v)) == s for u, v, s in sign_pairs))
    return np.array(out), np.array(ok_sign, dtype=bool)


# --------------------------------------------------------------------------- the module

def textinfo(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, use_text: bool = True,
             sign_prune: bool = False, gamma: float = GAMMA, open_mult: float = OPEN_MULT,
             q_open: float = Q_OPEN, open_mode: str = OPEN_MODE, name: str = "textinfo") -> MethodResult:
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    text = (skel.damage.get("text") or {}) if use_text else {}
    g = gamma if use_text else 0.0
    info = {"n_open": 0, "n_repair": 0, "open_fallback": False, "n_reversal_pool": None, "n_pruned": 0,
            "prune_applied": False}

    base = skel.copy()
    cands: list[tuple[int, int]] = []
    if k_miss > 0:
        off = _off_pairs(skel)
        off_keys = [pair_key(u, v) for u, v in off]
        w_s = weights(text.get("suspicion"), off_keys, g)
        fit_all = fit_equations(data, [soft_terms(skel, j, lag_max) for j in range(n)], lag_max)
        if fit_all.status != "ok":
            return _failed(name, fit_all.status)
        cands = weighted_repair(fit_all.residuals, skel, k_miss, w_s)
        try:
            if open_mode == "all":
                raise ValueError("all lags requested")
            pv_all = structural_pvalues(data, skel, lag_max)
            pv = {pair_key(*sorted(p)): q for p, q in pv_all.items() if not skel.is_adjacent(*tuple(p))}
            keys, n_rej = weighted_bh(pv, w_s, q_open)
            K = min(len(keys), max(int(math.ceil(open_mult * k_miss)), n_rej))
            opened = keys[:K]
        except ValueError:  # all lags requested, or tests underdetermined: open everything (v4)
            opened = off_keys
            info["open_fallback"] = open_mode != "all"
        for k in opened:
            u, v = map(int, k.split("-"))
            base.undetermined.add(frozenset((u, v)))
        info["n_open"] = len(opened)
        info["n_repair"] = len(cands)
    terms_of = lambda s: [parent_terms(s, j, lag_max) for j in range(n)]  # noqa: E731

    fit0 = fit_equations(data, terms_of(base), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)

    reversing = k_rev > 0
    pool, w_pool = None, None
    if reversing:
        pool = contemporaneous_pool(data, fit0, k_rev)
        sk_keys = [pair_key(*sorted(p)) for p in skel.pairs()]
        w_d = weights(text.get("doubt"), sk_keys, g)
        w_pool = np.array([w_d.get(pair_key(u, v), 1.0) for u, v in pool])
        info["n_reversal_pool"] = len(pool)
    draw_structure = bool(cands) or reversing

    def draw_skel() -> Skeleton:
        s = _weighted_flip(base, pool, k_rev, w_pool, rng) if reversing else base.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (e[1], e[0])
            if not _creates_cycle(s.oriented | {e}, n):
                s.undetermined.discard(frozenset((u, v)))
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)

    sign_pairs = None
    if sign_prune and text.get("sign"):
        sk_keys = [pair_key(*sorted(p)) for p in skel.pairs()]
        z_d = normal_scores(text.get("doubt") or {}, sk_keys)
        sign_pairs = []
        for k, s in text["sign"].items():
            if k in z_d and z_d[k] <= 0 and s in (1, -1):
                u, v = map(int, k.split("-"))
                sign_pairs.append((u, v, int(s)))
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else None
    draws, ok_sign = _bootstrap(data, fit, H, n_boot, rng, refit, sign_pairs)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    if sign_pairs:
        info["n_sign_hints"] = len(sign_pairs)
        if ok_sign.sum() >= len(draws) / 2:
            info["n_pruned"] = int((~ok_sign).sum())
            info["prune_applied"] = True
            draws = draws[ok_sign]
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)


def textinfo_null(data, skel, lag_max, H, n_boot, rng):
    return textinfo(data, skel, lag_max, H, n_boot, rng, use_text=False, name="textinfo_null")


def textinfo_all(data, skel, lag_max, H, n_boot, rng):
    return textinfo(data, skel, lag_max, H, n_boot, rng, open_mode="all", name="textinfo_all")


def textinfo_sign(data, skel, lag_max, H, n_boot, rng):
    return textinfo(data, skel, lag_max, H, n_boot, rng, sign_prune=True, name="textinfo_sign")


METHODS = {"textinfo": textinfo, "textinfo_all": textinfo_all, "textinfo_null": textinfo_null,
           "textinfo_sign": textinfo_sign}
