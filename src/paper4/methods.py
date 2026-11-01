"""Interval methods compared in RQ4.2. Each returns C(H) for every ordered pair with a 95% interval.

Baselines:
- ``oracle``     b0  true graph with true lags (reference only, not available in practice)
- ``plugin``     b1  dynamic SEM on the given skeleton, residual-bootstrap percentile interval
- ``inflate``    b3  b1's interval widened about its midpoint by a constant c (tuned on held-out topologies)
- ``lp_allpast`` b4  local projection on all past values of all nodes, skeleton used only for the
                     contemporaneous parents of the shocked node; Newey-West interval
- ``bagging``    b5  b1 refitted on skeletons perturbed at the stated damage rate, on bootstrap data

Tolerant module, version 1 (rejected by the rules in docs/decision_rules.md, kept for the record):
- ``soft``       the skeleton becomes a prior instead of a hard restriction: every node's lags
                 enter every equation, but lagged terms of pairs outside the skeleton get a ridge
                 penalty set from the stated damage (the prior inclusion probability of an
                 off-skeleton pair). Contemporaneous terms follow the skeleton as given.

Tolerant module, version 2 (rejected, kept for the record):
- ``tolerant``   uses the stated damage to decide what to relax: all lags plus residual-correlation
                 repair of contemporaneous edges when edges are said to be missing, orientation
                 draws when edges are said to be reversed, the skeleton as given otherwise.

Version 3:
- ``tolerant_v3``      reversal draws confined to pairs with a significant contemporaneous coefficient.
- ``tolerant_v3_cal``  tolerant_v3 widened by a factor c_T that depends on T only, tuned on the
                       undamaged cells of the calibration bank (small-sample correction).

Version 4:
- ``tolerant_v4``      tolerant_v3 widened by a factor tuned for the module itself per (T, stated
                       damage kind) on the calibration bank, pooled over damage rates, so that its
                       own coverage, not plugin's, is brought to the nominal level.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .effects import cumulative, irf
from .estimator import (bootstrap_C, fit_equations, parent_terms, percentile_interval,
                        soft_terms)
from .skeleton import Skeleton, _creates_cycle

ALPHA = 0.05


@dataclass
class MethodResult:
    name: str
    status: str
    C: np.ndarray | None = None
    lo: np.ndarray | None = None
    hi: np.ndarray | None = None
    theta: np.ndarray | None = None
    B: np.ndarray | None = None
    info: dict = field(default_factory=dict)


def _failed(name: str, status: str) -> MethodResult:
    return MethodResult(name, status)


def _too_few(draws, n_boot: int) -> bool:
    """Too few successful bootstrap refits for a percentile interval (at very small T most refits
    can be underdetermined)."""
    return len(draws) < max(10, n_boot // 4)


def plugin(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, name: str = "plugin") -> MethodResult:
    n = skel.n
    terms = [parent_terms(skel, j, lag_max) for j in range(n)]
    fit = fit_equations(data, terms, lag_max)
    if fit.status != "ok":
        return _failed(name, fit.status)
    theta = irf(fit.B, H)
    if n_boot == 0:
        return MethodResult(name, "ok", cumulative(theta, H), None, None, theta, fit.B)
    draws = bootstrap_C(data, fit, H, n_boot, rng)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    return MethodResult(name, "ok", cumulative(theta, H), lo, hi, theta, fit.B)


def oracle(data, true_skel_with_lags: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    return plugin(data, true_skel_with_lags, lag_max, H, n_boot, rng, name="oracle")


def inflate(base: MethodResult, c: float | None) -> MethodResult:
    if base.status != "ok":
        return _failed("inflate", base.status)
    if c is None:  # no calibration factor: every calibration fit at this T failed
        return _failed("inflate", "uncalibrated")
    mid, half = (base.lo + base.hi) / 2, (base.hi - base.lo) / 2
    return MethodResult("inflate", "ok", base.C, mid - c * half, mid + c * half, base.theta, base.B, {"c": c})


def _newey_west_var(X: np.ndarray, U: np.ndarray, col: int, L: int) -> np.ndarray:
    """HAC variance of coefficient ``col`` for every column of the residual matrix U."""
    n = X.shape[0]
    XtX_inv = np.linalg.inv(X.T @ X)
    w = XtX_inv[col] @ X.T          # (n,): influence weights of the coefficient
    s = w[:, None] * U              # (n, m)
    var = (s * s).sum(axis=0)
    for lag in range(1, L + 1):
        weight = 1 - lag / (L + 1)
        var += 2 * weight * (s[lag:] * s[:-lag]).sum(axis=0)
    return var * n / max(n - X.shape[1], 1)


def lp_allpast(data, skel: Skeleton, lag_max: int, H: int) -> MethodResult:
    """C_ji(H) from regressing sum_{h<=H} x_{j,t+h} on x_{i,t}, the contemporaneous parents of i in
    the skeleton, and lags 1..lag_max+1 of every node (lag augmentation, Montiel Olea and
    Plagborg-Moller 2021)."""
    T, n = data.shape
    p = lag_max + 1
    rows = np.arange(p, T - H)
    if len(rows) < 3:
        return _failed("lp_allpast", "underdetermined")
    Y = np.stack([data[rows + h] for h in range(H + 1)]).sum(axis=0)    # (rows, n)
    lags = np.column_stack([data[rows - lag, i] for lag in range(1, p + 1) for i in range(n)])
    C = np.zeros((n, n))
    se = np.zeros((n, n))
    for i in range(n):
        parents = [u for u, v in skel.oriented if v == i]
        X = np.column_stack([np.ones(len(rows)), data[rows, i]] + [data[rows, u] for u in parents] + [lags])
        if X.shape[1] + 1 > len(rows):
            return _failed("lp_allpast", "underdetermined")
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        U = Y - X @ beta
        C[:, i] = beta[1]
        se[:, i] = np.sqrt(np.maximum(_newey_west_var(X, U, 1, H), 0))
    z = 1.959963984540054
    return MethodResult("lp_allpast", "ok", C, C - z * se, C + z * se)


def _perturb(skel: Skeleton, rng: np.random.Generator) -> Skeleton:
    """Undo damage of the stated kind and size at random: re-add pairs if edges are said to be
    missing, drop pairs if edges are said to be extra, flip oriented pairs if said reversed."""
    kind, k = skel.damage.get("kind", "none"), int(skel.damage.get("k", 0))
    out = skel.copy()
    if kind == "missing" and k:
        present = skel.pairs()
        pool = [(u, v) for u in range(skel.n) for v in range(u + 1, skel.n) if frozenset((u, v)) not in present]
        for idx in rng.permutation(len(pool))[:k]:
            u, v = pool[idx]
            out.undetermined.add(frozenset((u, v)))      # direction unknown: lagged terms only
    elif kind == "extra" and k:
        pool = sorted(tuple(sorted(p)) for p in skel.pairs())
        for idx in rng.permutation(len(pool))[:k]:
            u, v = pool[idx]
            out.oriented.discard((u, v)); out.oriented.discard((v, u))
            out.undetermined.discard(frozenset((u, v)))
    elif kind in ("reversed", "reversed_any") and k:
        pool = sorted(skel.oriented)
        flipped = 0
        for idx in rng.permutation(len(pool)):
            if flipped == k:
                break
            u, v = pool[idx]
            trial = (out.oriented - {(u, v)}) | {(v, u)}
            if not _creates_cycle(trial, skel.n):
                out.oriented = trial
                flipped += 1
    return out


def bagging(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    base = plugin(data, skel, lag_max, H, 0, rng, name="bagging")
    if base.status != "ok":
        return base
    n = skel.n
    base_fit = fit_equations(data, [parent_terms(skel, j, lag_max) for j in range(n)], lag_max)
    draws = []
    tries = 0
    while len(draws) < n_boot and tries < 3 * n_boot:
        tries += 1
        s = _perturb(skel, rng)
        terms = [parent_terms(s, j, lag_max) for j in range(n)]
        d = bootstrap_C(data, base_fit, H, 1, rng, refit=lambda x, terms=terms: fit_equations(x, terms, lag_max))
        if len(d):
            draws.append(d[0])
    if _too_few(draws, n_boot):
        return _failed("bagging", "bootstrap_failed")
    lo, hi = percentile_interval(np.array(draws), ALPHA)
    base.lo, base.hi = lo, hi
    return base


def soft_penalties(data, skel: Skeleton, lag_max: int) -> tuple[list, list[np.ndarray], dict]:
    """Ridge penalty per regressor from the stated damage.

    Prior: an off-skeleton lagged coefficient is N(0, pi_out * b2), a skeleton lagged coefficient
    is N(0, pi_in * b2), where b2 is the mean squared cross coefficient fitted on the skeleton and
    pi is the prior probability that the pair carries an edge. The ridge penalty is then
    sigma_j^2 / (pi * b2). pi_out = (stated missing pairs) / (off-skeleton pairs), with a floor of
    half a pair; pi_in = 1 - (stated extra pairs) / (skeleton pairs). Own lags and contemporaneous
    terms are not penalised. As T grows the data outweigh the fixed penalty.
    """
    n = skel.n
    hard = fit_equations(data, [parent_terms(skel, j, lag_max) for j in range(n)], lag_max)
    if hard.status != "ok":
        return None, None, {"status": hard.status}
    cross = [hard.B[lag, j, i] for j in range(n) for (i, lag) in hard.terms[j] if i != j and lag > 0]
    b2 = float(np.mean(np.square(cross))) if cross else 0.25
    sigma2 = (hard.residuals ** 2).sum(axis=0) / np.maximum(hard.dof, 1.0)

    kind, k = skel.damage.get("kind", "none"), int(skel.damage.get("k", 0))
    n_in = len(skel.pairs())
    n_out = n * (n - 1) // 2 - n_in
    pi_out = max(k if kind == "missing" else 0, 0.5) / max(n_out, 1)
    pi_in = 1 - (k / n_in if kind == "extra" and n_in else 0.0)
    pi_in = max(pi_in, 0.05)

    terms, pens = [], []
    for j in range(n):
        tj = soft_terms(skel, j, lag_max)
        pen = np.zeros(len(tj))
        for idx, (i, lag) in enumerate(tj):
            if i == j or lag == 0:
                continue
            pi = pi_in if skel.is_adjacent(i, j) else pi_out
            pen[idx] = sigma2[j] / (pi * b2)
        terms.append(tj)
        pens.append(pen)
    return terms, pens, {"pi_out": pi_out, "pi_in": pi_in, "b2": b2}


def soft(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    terms, pens, info = soft_penalties(data, skel, lag_max)
    if terms is None:
        return _failed("soft", info["status"])
    fit = fit_equations(data, terms, lag_max, pens)
    theta = irf(fit.B, H)
    draws = bootstrap_C(data, fit, H, n_boot, rng)
    if _too_few(draws, n_boot):
        return _failed("soft", "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    return MethodResult("soft", "ok", cumulative(theta, H), lo, hi, theta, fit.B, info)


# --------------------------------------------------------------------------- tolerant module v2

def _fisher_p(r: float, m: int) -> float:
    import math
    z = math.atanh(max(min(r, 0.999999), -0.999999)) * math.sqrt(max(m - 3, 1))
    return math.erfc(abs(z) / math.sqrt(2))


def repair_candidates(residuals: np.ndarray, skel: Skeleton, cap: int, q: float = 0.1) -> list[tuple[int, int]]:
    """Non-adjacent pairs whose structural residuals are correlated, by Benjamini-Hochberg at level
    q, at most ``cap`` of them (strongest first). Structural shocks are independent in the model,
    so a contemporaneous edge missing from the skeleton leaves exactly this footprint; a missing
    lagged edge does not, because every lag is already in the equations."""
    if cap <= 0:
        return []
    m, n = residuals.shape
    corr = np.corrcoef(residuals.T)
    tests = sorted((_fisher_p(corr[u, v], m), u, v)
                   for u in range(n) for v in range(u + 1, n) if not skel.is_adjacent(u, v))
    keep = 0
    for rank, (p, _, _) in enumerate(tests, start=1):
        if p <= q * rank / len(tests):
            keep = rank
    return [(u, v) for _, u, v in tests[:keep]][:cap]


def tolerant(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, target_reversal: bool = False,
             name: str = "tolerant") -> MethodResult:
    """Skeleton-error-tolerant estimate driven by the stated damage (version 2; version 3 with
    ``target_reversal=True``, see ``tolerant_v3``).

    - Stated missing edges: every node's lags enter every equation (no lagged term can be lost),
      and contemporaneous edges are restored where structural residuals are correlated, at most
      as many as the stated number of missing pairs. Their direction is not identified, so each
      bootstrap draw orients them at random.
    - Stated reversed edges: each bootstrap draw flips as many oriented pairs as stated.
    - Otherwise the skeleton's own terms are used, as in ``plugin``.
    The interval is the percentile interval over draws that combine data resampling with these
    structural draws; the point estimate is the mean of the draws when structure is drawn.
    """
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    terms_of = (lambda s: [soft_terms(s, j, lag_max) for j in range(n)]) if full_lags else \
               (lambda s: [parent_terms(s, j, lag_max) for j in range(n)])
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    cands = repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    draw_structure = bool(cands) or reversing
    if reversing:
        pool = contemporaneous_pool(data, fit0, k_rev) if target_reversal else sorted(skel.oriented)
    else:
        pool = None

    def draw_skel() -> Skeleton:
        s = _flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel()), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if draw_structure else None
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "full_lags": full_lags,
                         "n_reversal_pool": None if pool is None else len(pool)})


def stated_counts(damage: dict) -> dict[str, int]:
    """Stated number of missing, extra and reversed pairs. Accepts the single-kind record
    {"kind", "rate", "k"} and the composite record {"missing", "extra", "reversed"} of the plan's
    interface (section 7: damage as extra / missing / reversed levels)."""
    if any(key in damage for key in ("missing", "extra", "reversed")):
        return {key: int(damage.get(key, 0)) for key in ("missing", "extra", "reversed")}
    kind, k = damage.get("kind", "none"), int(damage.get("k", 0))
    return {"missing": k if kind == "missing" else 0,
            "extra": k if kind == "extra" else 0,
            "reversed": k if kind in ("reversed", "reversed_any") else 0}


def width_key(damage: dict) -> str:
    """Which calibrated module width applies to a stated damage: the strongest component wins
    (missing, then reversed, then extra)."""
    s = stated_counts(damage)
    for key in ("missing", "reversed", "extra"):
        if s[key] > 0:
            return key
    return "none"


def contemporaneous_pool(data, fit, k: int, t_crit: float = 1.645) -> list[tuple[int, int]]:
    """Oriented pairs whose fitted contemporaneous coefficient is significant (|t| > t_crit).
    The size of a contemporaneous link is identified even when its direction is not, so a stated
    reversal is most plausibly among these pairs. Falls back to the k largest |t| when fewer than
    k pass."""
    T, n = data.shape
    p = fit.B.shape[0] - 1
    rows = np.arange(p, T)
    ranked = []
    for j in range(n):
        tj = fit.terms[j]
        if not any(lag == 0 for _, lag in tj):
            continue
        X = np.column_stack([np.ones(len(rows))] + [data[rows - lag, i] for i, lag in tj])
        s2 = (fit.residuals[:, j] ** 2).sum() / max(fit.dof[j], 1.0)
        cov = s2 * np.linalg.pinv(X.T @ X)
        for idx, (i, lag) in enumerate(tj):
            if lag == 0:
                ranked.append((abs(fit.B[0, j, i]) / np.sqrt(cov[idx + 1, idx + 1]), (i, j)))
    ranked.sort(reverse=True)
    significant = [e for t, e in ranked if t > t_crit]
    return significant if len(significant) >= k else [e for _, e in ranked[: max(k, 1)]]


def _flip_from(skel: Skeleton, pool: list[tuple[int, int]], k: int, rng) -> Skeleton:
    out = skel.copy()
    flipped = 0
    for idx in rng.permutation(len(pool)):
        if flipped == k:
            break
        u, v = pool[idx]
        trial = (out.oriented - {(u, v)}) | {(v, u)}
        if not _creates_cycle(trial, skel.n):
            out.oriented = trial
            flipped += 1
    return out


def tolerant_v3(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng) -> MethodResult:
    """Version 3: as version 2, with reversal draws confined to oriented pairs whose
    contemporaneous coefficient is significant."""
    return tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name="tolerant_v3")


def calibrate_width(res: MethodResult, c: float, name: str) -> MethodResult:
    """Widen an interval about its midpoint by a factor c that depends on T only, tuned on the
    undamaged cells of the calibration bank: a small-sample correction of the bootstrap that
    carries no information about the damage."""
    if res.status != "ok":
        return _failed(name, res.status)
    if c is None:
        return _failed(name, "uncalibrated")
    out = inflate(res, c)
    out.name = name
    out.info = {**res.info, "c_T": c}
    return out
