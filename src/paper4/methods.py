"""Interval methods compared in RQ4.2. Each returns C(H) for every ordered pair with a 95% interval.

Baselines:
- ``oracle``     b0  true graph with true lags (reference only, not available in practice)
- ``plugin``     b1  dynamic SEM on the given skeleton, residual-bootstrap percentile interval
- ``inflate``    b3  b1's interval widened about its midpoint by a constant c (tuned on held-out topologies)
- ``lp_allpast`` b4  local projection on all past values of all nodes, skeleton used only for the
                     contemporaneous parents of the shocked node; Newey-West interval
- ``bagging``    b5  b1 refitted on skeletons perturbed at the stated damage rate, on bootstrap data

Published baselines (A2):
- ``ida_union``       IDA-style: union of b1 intervals over the skeleton's Markov equivalence class
- ``pselect_union``   adaptation of Chang, Guo and Malinsky: adjacencies re-selected from the data with
                      perturbed tests, union of intervals over the selected graphs
- ``bvar_minnesota``  Bayesian VAR, Minnesota-type prior tightened off the skeleton, hyperparameters
                      by marginal likelihood

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
from itertools import combinations

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


# --------------------------------------------------------------------------- A2: published baselines

def _cpdag(oriented: set[tuple[int, int]], n: int) -> tuple[set[tuple[int, int]], set[frozenset[int]]]:
    """Compelled arrows and reversible lines of the Markov equivalence class of a DAG: keep the
    arrows of its v-structures, then apply Meek rules R1-R3 until nothing changes."""
    adj = {frozenset(e) for e in oriented}
    parents = {v: {u for u, w in oriented if w == v} for v in range(n)}
    arrows = set()
    for c in range(n):
        for a, b in combinations(sorted(parents[c]), 2):
            if frozenset((a, b)) not in adj:
                arrows |= {(a, c), (b, c)}
    lines = {e for e in adj if not any((u, v) in arrows for u, v in (tuple(e), tuple(e)[::-1]))}
    changed = True
    while changed:
        changed = False
        for e in list(lines):
            u, v = tuple(e)
            for x, y in ((u, v), (v, u)):
                r1 = any((a, x) in arrows and frozenset((a, y)) not in adj for a in range(n) if a != y)
                r2 = any((x, b) in arrows and (b, y) in arrows for b in range(n))
                r3 = any(frozenset((x, c)) in lines and frozenset((x, d)) in lines and (c, y) in arrows
                         and (d, y) in arrows and frozenset((c, d)) not in adj
                         for c, d in combinations(range(n), 2))
                if r1 or r2 or r3:
                    arrows.add((x, y))
                    lines.discard(e)
                    changed = True
                    break
    return arrows, lines


def equivalence_class(oriented: set[tuple[int, int]], n: int, cap: int, rng) -> list[set[tuple[int, int]]]:
    """DAGs Markov equivalent to ``oriented`` (same adjacencies, same v-structures), the given DAG
    first. Exhaustive for up to 12 reversible lines; beyond that, or past ``cap`` members, a random
    subset."""
    arrows, lines = _cpdag(oriented, n)
    lines = sorted(tuple(sorted(e)) for e in lines)
    target_v = _vstructures(oriented, n)

    def valid(dag):
        return not _creates_cycle(dag, n) and _vstructures(dag, n) == target_v

    if len(lines) <= 12:
        members = []
        for bits in range(2 ** len(lines)):
            dag = arrows | {(u, v) if (bits >> i) & 1 else (v, u) for i, (u, v) in enumerate(lines)}
            if valid(dag):
                members.append(dag)
    else:
        members, seen = [], set()
        for _ in range(50 * cap):
            order = {node: r for r, node in enumerate(rng.permutation(n))}
            dag = arrows | {(u, v) if order[u] < order[v] else (v, u) for u, v in lines}
            key = frozenset(dag)
            if key not in seen and valid(dag):
                seen.add(key)
                members.append(dag)
            if len(members) >= cap:
                break
    members.sort(key=lambda d: d != oriented)
    if not members or members[0] != oriented:
        members.insert(0, set(oriented))
    if len(members) > cap:
        members = members[:1] + [members[i] for i in 1 + rng.permutation(len(members) - 1)[: cap - 1]]
    return members


def _vstructures(oriented: set[tuple[int, int]], n: int) -> set[tuple[int, int, int]]:
    adj = {frozenset(e) for e in oriented}
    parents = {v: sorted(u for u, w in oriented if w == v) for v in range(n)}
    return {(a, c, b) for c in range(n) for a, b in combinations(parents[c], 2) if frozenset((a, b)) not in adj}


def ida_union(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, cap: int = 16) -> MethodResult:
    """IDA-style baseline (Maathuis, Kalisch and Buhlmann 2009): the skeleton's orientation is only
    trusted up to Markov equivalence. Every member of the equivalence class (up to ``cap``) is fitted
    as in ``plugin``; the reported interval is the union of the members' bootstrap intervals and the
    point estimate the mean over members. Lagged terms do not depend on orientation (estimator.py),
    so only the contemporaneous terms differ between members. It reads no stated damage and cannot
    restore missing edges."""
    members = equivalence_class(skel.oriented, skel.n, cap, rng)
    per = max(10, n_boot // len(members))
    Cs, los, his = [], [], []
    for dag in members:
        s = skel.copy()
        s.oriented = set(dag)
        r = plugin(data, s, lag_max, H, per, rng, name="ida_union")
        if r.status != "ok":
            continue
        Cs.append(r.C)
        los.append(r.lo)
        his.append(r.hi)
    if not Cs:
        return _failed("ida_union", "underdetermined")
    return MethodResult("ida_union", "ok", np.mean(Cs, axis=0), np.min(los, axis=0), np.max(his, axis=0),
                        info={"n_members": len(members), "n_fitted": len(Cs)})


def _ar_scale(x: np.ndarray, p: int) -> float:
    """Residual standard deviation of a univariate AR(p): the Minnesota scale of a variable."""
    X = np.column_stack([np.ones(len(x) - p)] + [x[p - k: len(x) - k] for k in range(1, p + 1)])
    y = x[p:]
    resid = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    return float(np.sqrt(resid @ resid / max(len(y) - p - 1, 1)))


def bvar_minnesota(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng,
                   lambdas=(0.05, 0.1, 0.2, 0.5, 1.0), thetas=(0.01, 0.1, 0.3, 1.0)) -> MethodResult:
    """Bayesian VAR baseline: every equation carries every node's lags 1..lag_max and the
    skeleton's contemporaneous parents, with a Minnesota-type Gaussian prior centred at zero.

    Prior variance of the coefficient of x_i at lag l in the equation of x_j is
    (lambda / l)^2 * s_j^2 / s_i^2, multiplied by theta when i != j and the pair is off the
    skeleton (the skeleton enters as prior tightness, not as a hard restriction). Contemporaneous
    terms get a flat prior. s_i is the residual sd of a univariate AR(lag_max); the error variance
    of equation j is fixed at s_j^2. lambda and theta are chosen jointly on a grid by maximising
    the marginal likelihood of all equations, as in the hierarchical prior selection of Giannone,
    Lenza and Primiceri (2015). The interval is the 2.5-97.5% range of C(H) over posterior draws.
    """
    T, n = data.shape
    rows = np.arange(lag_max, T)
    s = np.array([_ar_scale(data[:, i], lag_max) for i in range(n)])
    eqs = []
    for j in range(n):
        tj = soft_terms(skel, j, lag_max)
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        X = X - X.mean(axis=0)
        y = data[rows, j] - data[rows, j].mean()
        eqs.append((tj, X, y))

    def prior_var(j, tj, lam, th):
        v = np.empty(len(tj))
        for idx, (i, lag) in enumerate(tj):
            if lag == 0:
                v[idx] = 1e4 * s[j] ** 2 / s[i] ** 2
            else:
                v[idx] = (lam / lag) ** 2 * s[j] ** 2 / s[i] ** 2 * (1.0 if i == j or skel.is_adjacent(i, j) else th)
        return v

    def log_ml(lam, th):
        total = 0.0
        for j, (tj, X, y) in enumerate(eqs):
            S = s[j] ** 2 * np.eye(len(y)) + (X * prior_var(j, tj, lam, th)) @ X.T
            sign, logdet = np.linalg.slogdet(S)
            total += -0.5 * (logdet + y @ np.linalg.solve(S, y))
        return total

    lam, th = max(((lam, th) for lam in lambdas for th in thetas), key=lambda g: log_ml(*g))
    p = lag_max
    means, chols = [], []
    for j, (tj, X, y) in enumerate(eqs):
        prec = X.T @ X / s[j] ** 2 + np.diag(1.0 / prior_var(j, tj, lam, th))
        cov = np.linalg.inv(prec)
        means.append(cov @ X.T @ y / s[j] ** 2)
        chols.append(np.linalg.cholesky((cov + cov.T) / 2))

    def to_B(betas):
        B = np.zeros((p + 1, n, n))
        for j, (tj, _, _) in enumerate(eqs):
            for (i, lag), b in zip(tj, betas[j]):
                B[lag, j, i] = b
        return B

    B_mean = to_B(means)
    draws = np.array([cumulative(irf(to_B([m + L @ rng.normal(size=len(m)) for m, L in zip(means, chols)]), H), H)
                      for _ in range(n_boot)])
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(B_mean, H)
    return MethodResult("bvar_minnesota", "ok", cumulative(theta, H), lo, hi, theta, B_mean,
                        {"lambda": lam, "theta": th})


def pair_evidence(data, lag_max: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Data evidence for every pair, from the reduced-form VAR with all lags of all nodes.

    Returns (G, Z, m): G[j, i] is the Granger z-score of x_i's lags in the equation of x_j (Wald
    statistic mapped to N(0, 1) by the Wilson-Hilferty transform), Z[i, j] the Fisher z of the
    partial correlation of the residuals of x_i and x_j given all other residuals, m the number of
    rows. Raises ValueError when the VAR has more regressors than rows."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    k = n * lag_max
    if k + 2 > m:
        raise ValueError("underdetermined")
    X = np.column_stack([np.ones(m)] + [data[rows - lag, i] for lag in range(1, lag_max + 1) for i in range(n)])
    Y = data[rows]
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ Y
    U = Y - X @ beta
    s2 = (U ** 2).sum(axis=0) / (m - k - 1)
    G = np.zeros((n, n))
    for i in range(n):
        idx = [1 + (lag - 1) * n + i for lag in range(1, lag_max + 1)]
        V = XtX_inv[np.ix_(idx, idx)]
        V_inv = np.linalg.inv(V)
        for j in range(n):
            b = beta[idx, j]
            W = b @ V_inv @ b / s2[j]
            c = 2 / (9 * lag_max)
            G[j, i] = ((W / lag_max) ** (1 / 3) - (1 - c)) / np.sqrt(c)
    P = np.linalg.pinv(np.cov(U.T))
    d = np.sqrt(np.diag(P))
    pcor = np.clip(-P / np.outer(d, d), -0.999999, 0.999999)
    Z = np.arctanh(pcor) * np.sqrt(max(m - k - n - 1, 1))
    np.fill_diagonal(Z, 0.0)
    return G, Z, m


def pselect_union(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, n_perturb: int = 100,
                  tau: float = 1.0, crit: float = 1.96, cap: int = 16) -> MethodResult:
    """SVAR adaptation of post-selection inference after causal discovery (Chang, Guo and Malinsky,
    arXiv 2405.06763): the adjacencies are re-selected from the data, the selection is repeated
    with randomly perturbed test statistics, and the interval is the union of the intervals fitted
    on the distinct selected graphs.

    A pair is selected when its Granger z-score in either direction or its residual partial
    correlation z-score exceeds ``crit``. Each perturbed selection adds N(0, tau^2) noise to every
    z-score. The unperturbed graph and the most frequent perturbed graphs, up to ``cap`` in total,
    are fitted as in ``plugin``. A selected pair keeps the skeleton's orientation when the skeleton
    has one and is otherwise undetermined (lagged terms only). It reads no stated damage. This is
    an adaptation, not the original procedure: the original perturbs the tests inside PC on iid
    data and screens the graphs; here the selection is one step on the VAR and every distinct graph
    is kept, which makes the union wider rather than narrower.
    """
    n = skel.n
    try:
        G, Z, _ = pair_evidence(data, lag_max)
    except ValueError:
        return _failed("pselect_union", "underdetermined")
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    stat = np.array([max(G[v, u], G[u, v], abs(Z[u, v])) for u, v in pairs])

    def graph(s):
        return frozenset(p for p, keep in zip(pairs, s > crit) if keep)

    counts = {}
    for _ in range(n_perturb):
        g = graph(stat + tau * rng.normal(size=len(stat)))
        counts[g] = counts.get(g, 0) + 1
    base = graph(stat)
    graphs = [base] + [g for g, _ in sorted(counts.items(), key=lambda kv: -kv[1]) if g != base][: cap - 1]

    def to_skel(g):
        s = Skeleton(n, damage=dict(skel.damage))
        for u, v in g:
            if (u, v) in skel.oriented:
                s.oriented.add((u, v))
            elif (v, u) in skel.oriented:
                s.oriented.add((v, u))
            else:
                s.undetermined.add(frozenset((u, v)))
        return s

    per = max(10, n_boot // len(graphs))
    fits = [plugin(data, to_skel(g), lag_max, H, per, rng, name="pselect_union") for g in graphs]
    ok = [r for r in fits if r.status == "ok"]
    if not ok or fits[0].status != "ok":
        return _failed("pselect_union", fits[0].status if fits[0].status != "ok" else "bootstrap_failed")
    return MethodResult("pselect_union", "ok", fits[0].C, np.min([r.lo for r in ok], axis=0),
                        np.max([r.hi for r in ok], axis=0), fits[0].theta, fits[0].B,
                        {"n_graphs": len(graphs), "n_selected": len(base)})
