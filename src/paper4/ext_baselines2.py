"""R2-1 (ID ``baselines2``): higher-fidelity versions of two published baselines.

Neither method reads the stated damage or anything private: they get the data and the public
skeleton (pairs + orientation). Both are new methods; ``methods.py`` (round-1 ``pselect_union``,
``bvar_minnesota``) is unchanged, so earlier results stay reproducible.

``pselect_union_v2``  post-selection union after causal discovery (Chang, Guo and Malinsky,
    arXiv 2405.06763), adapted to the recursive SVAR. Three fixes of the round-1 adaptation
    (docs/ext/synthesis_round1.md, X2 and bug B8):
    1. Selection by tests in the skeleton's **structural** all-lag equations
       (``diagnose.structural_pvalues``: kept pair = joint Wald of all of u's terms in v's equation
       and of v's in u's; left-out pair = Wald of the two lag blocks plus the correlation of the two
       structural residuals; Sidak combination), instead of reduced-form Granger + partial
       correlation, which is not a valid adjacency test when contemporaneous edges exist.
       Each pair's p-value is mapped to a two-sided z score; a pair is selected when z > 1.96
       (p < 0.05). Each perturbed selection adds N(0, 1) noise to every z (as in round 1).
    2. A selected pair that the skeleton does not orient (re-selected pair, or an undetermined
       pair) gets a **contemporaneous term in both orientations**: as ``ida_union`` does for the
       reversible lines of a CPDAG, every graph is fitted in several orientation members and the
       interval is the union over members. Members come in antithetic couples: a random
       orientation of the unoriented pairs and its complete flip, so every such pair is fitted in
       both directions (a flip that would create a cycle keeps the other direction).
       ``n_orient`` couples per graph (default 1, i.e. 2 members).
    3. Bootstrap budget: at least ``n_boot`` (199) draws in total, spread equally over the fitted
       members with a floor of ``min_draws`` (40) each. The per-member interval is the normal
       bootstrap interval C_m +/- 1.96 sd*(C_m): with 40-50 draws per member a 2.5/97.5 percentile
       is little more than the sample min/max, and the per-graph intervals of the original method
       are Wald-type. The reported interval is the union over members of all retained graphs;
       the point estimate is cumulative(mean IRF) over the members of the unperturbed graph.
    Graphs retained: the unperturbed selection plus the most frequent perturbed selections, at
    most ``cap`` (4) graphs in total.

``bvar_minnesota_v2``  Bayesian VAR with a Minnesota-type prior that is conjugate
    Normal-inverse-gamma per structural equation (Giannone, Lenza and Primiceri 2015 in its
    equation-by-equation form; equations are independent given the skeleton's recursive
    contemporaneous terms):
        sigma_j^2 ~ IG(a0, b0), a0 = 1.5, b0 = s_j^2 / 2  (the marginal of GLP's IW(diag(s^2), n + 2))
        beta_j | sigma_j^2 ~ N(0, sigma_j^2 V0_j)
    with V0 = (lambda / l)^2 / s_i^2 for x_i at lag l, times theta when the pair is off the skeleton
    and i != j, and 1e4 / s_i^2 (flat) for the skeleton's contemporaneous parents. s_i is the
    residual sd of a univariate AR(lag_max). lambda and theta maximise the closed-form marginal
    likelihood of all equations (multivariate t) plus GLP's Gamma hyperprior on lambda (mode 0.2,
    sd 0.4), on a grid. Posterior draws take **sigma_j^2 from its inverse-gamma posterior and then
    beta_j | sigma_j^2** (round 1 fixed sigma_j^2 = s_j^2). The interval is the 2.5-97.5 percentile
    of C(H) over ``n_boot`` posterior draws, the point estimate cumulative(irf(posterior mean)).

``*_cal`` variants: the same raw interval, widened by the runner (``calibrate_methods``) with a
factor tuned per (T, stated kind) on D-07H development, exactly as for ``tolerant_v4`` and as in
round-1 E3. To make the uncalibrated and calibrated rows share the very same draws, every
function here derives its random stream from a hash of (method family, data, public skeleton,
lag_max, H, n_boot) instead of the runner's stream, and caches the last few raw results per
process. A cache miss recomputes the identical result, so results do not depend on call order.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from statistics import NormalDist

import numpy as np

from .diagnose import structural_pvalues
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .methods import ALPHA, MethodResult, _ar_scale, _failed
from .skeleton import Skeleton, _creates_cycle

_Z = NormalDist().inv_cdf(1 - ALPHA / 2)
_CACHE: "OrderedDict[tuple, MethodResult]" = OrderedDict()
_CACHE_MAX = 16


def _key(family: str, data, skel: Skeleton, lag_max: int, H: int, n_boot: int) -> tuple[tuple, int]:
    h = hashlib.sha256()
    h.update(family.encode())
    h.update(np.ascontiguousarray(data, dtype=float).tobytes())
    pub = {"o": sorted(map(list, skel.oriented)), "u": sorted(sorted(p) for p in skel.undetermined),
           "d": skel.damage, "n": skel.n, "p": lag_max, "H": H, "B": n_boot}
    h.update(json.dumps(pub, sort_keys=True, default=str).encode())
    digest = h.digest()
    return (family, digest), int.from_bytes(digest[:8], "little")


def _cached(family, fn, data, skel, lag_max, H, n_boot, name):
    key, seed = _key(family, data, skel, lag_max, H, n_boot)
    res = _CACHE.get(key)
    if res is None:
        res = fn(data, skel, lag_max, H, n_boot, np.random.default_rng(seed))
        _CACHE[key] = res
        while len(_CACHE) > _CACHE_MAX:
            _CACHE.popitem(last=False)
    else:
        _CACHE.move_to_end(key)
    return MethodResult(name, res.status, res.C, res.lo, res.hi, res.theta, res.B, dict(res.info))


# --------------------------------------------------------------------------- pselect_union_v2

def _orient_member(base: Skeleton, unoriented: list[tuple[int, int]], forward: np.ndarray) -> Skeleton:
    """Add a contemporaneous edge for every unoriented pair, u -> v when forward else v -> u,
    taking the other direction when the chosen one would close a cycle."""
    s = base.copy()
    n = s.n
    for (u, v), f in zip(unoriented, forward):
        e = (u, v) if f else (v, u)
        if _creates_cycle(s.oriented | {e}, n):
            e = (e[1], e[0])
        if not _creates_cycle(s.oriented | {e}, n):
            s.oriented.add(e)
        s.undetermined.discard(frozenset((u, v)))
    return s


def _pselect_core(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, n_perturb: int = 100,
                  tau: float = 1.0, crit: float = 1.959963984540054, cap: int = 4, n_orient: int = 1,
                  min_draws: int = 40) -> MethodResult:
    name = "pselect_union_v2"
    n = skel.n
    try:
        pv = structural_pvalues(data, skel, lag_max)
    except (ValueError, np.linalg.LinAlgError):
        return _failed(name, "underdetermined")
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    nd = NormalDist()
    stat = np.array([nd.inv_cdf(1 - min(max(pv[frozenset(p)], 1e-15), 1 - 1e-15) / 2) for p in pairs])

    def graph(z):
        return frozenset(p for p, keep in zip(pairs, z > crit) if keep)

    counts: dict = {}
    for _ in range(n_perturb):
        g = graph(stat + tau * rng.normal(size=len(stat)))
        counts[g] = counts.get(g, 0) + 1
    base = graph(stat)
    graphs = [base] + [g for g, _ in sorted(counts.items(), key=lambda kv: (-kv[1], sorted(kv[0])))
                       if g != base][: cap - 1]

    # orientation members of every graph
    members = []   # (graph index, skeleton)
    for g_idx, g in enumerate(graphs):
        s0 = Skeleton(n, damage=dict(skel.damage))
        unoriented = []
        for u, v in sorted(g):
            if (u, v) in skel.oriented:
                s0.oriented.add((u, v))
            elif (v, u) in skel.oriented:
                s0.oriented.add((v, u))
            else:
                unoriented.append((u, v))
        if not unoriented:
            members.append((g_idx, s0))
            continue
        for _ in range(n_orient):
            fwd = rng.random(len(unoriented)) < 0.5
            members.append((g_idx, _orient_member(s0, unoriented, fwd)))
            members.append((g_idx, _orient_member(s0, unoriented, ~fwd)))

    per = max(min_draws, int(math.ceil(n_boot / len(members))))
    los, his, base_thetas, base_B = [], [], [], None
    n_ok, n_draws = 0, 0
    for g_idx, s in members:
        terms = [parent_terms(s, j, lag_max) for j in range(n)]
        fit = fit_equations(data, terms, lag_max)
        if fit.status != "ok":
            continue
        draws = bootstrap_C(data, fit, H, per, rng)
        if len(draws) < max(10, per // 4):
            continue
        theta = irf(fit.B, H)
        C_m = cumulative(theta, H)
        sd = draws.std(axis=0, ddof=1)
        los.append(C_m - _Z * sd)
        his.append(C_m + _Z * sd)
        n_ok += 1
        n_draws += len(draws)
        if g_idx == 0:
            base_thetas.append(theta)
            if base_B is None:
                base_B = fit.B
    if not base_thetas:
        return _failed(name, "underdetermined" if n_ok == 0 else "base_failed")
    theta = np.mean(base_thetas, axis=0)
    n_unor = sum(1 for u, v in base if (u, v) not in skel.oriented and (v, u) not in skel.oriented)
    return MethodResult(name, "ok", cumulative(theta, H), np.min(los, axis=0), np.max(his, axis=0), theta, base_B,
                        {"n_graphs": len(graphs), "n_members": len(members), "n_members_ok": n_ok,
                         "n_draws": n_draws, "n_selected": len(base), "n_unoriented": n_unor})


def pselect_union_v2(data, skel, lag_max, H, n_boot, rng):
    return _cached("pselect_v2", _pselect_core, data, skel, lag_max, H, n_boot, "pselect_union_v2")


def pselect_union_v2_cal(data, skel, lag_max, H, n_boot, rng):
    return _cached("pselect_v2", _pselect_core, data, skel, lag_max, H, n_boot, "pselect_union_v2_cal")


# --------------------------------------------------------------------------- bvar_minnesota_v2

def _gamma_logpdf_mode_sd(x: float, mode: float = 0.2, sd: float = 0.4) -> float:
    """Log density of the Gamma hyperprior of GLP (2015) on lambda, parametrised by mode and sd."""
    # mode = (k - 1) * s, var = k s^2  ->  s = (-mode + sqrt(mode^2 + 4 var)) / 2, k = 1 + mode / s
    s = (-mode + math.sqrt(mode * mode + 4 * sd * sd)) / 2
    k = 1 + mode / s
    return (k - 1) * math.log(x) - x / s - math.lgamma(k) - k * math.log(s)


def _bvar_core(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng,
               lambdas=(0.05, 0.1, 0.2, 0.3, 0.5, 1.0), thetas=(0.01, 0.03, 0.1, 0.3, 1.0),
               a0: float = 1.5) -> MethodResult:
    name = "bvar_minnesota_v2"
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    s = np.array([_ar_scale(data[:, i], lag_max) for i in range(n)])
    eqs = []
    for j in range(n):
        tj = soft_terms(skel, j, lag_max)
        X = np.column_stack([data[rows - lag, i] for i, lag in tj])
        X = X - X.mean(axis=0)
        y = data[rows, j] - data[rows, j].mean()
        eqs.append((tj, X, y, X.T @ X, X.T @ y, float(y @ y)))
    m_eff = m - 1  # one dof for the (flat, centred-out) intercept

    def prior_var(j, tj, lam, th):
        v = np.empty(len(tj))
        for idx, (i, lag) in enumerate(tj):
            if lag == 0:
                v[idx] = 1e4 / s[i] ** 2
            else:
                v[idx] = (lam / lag) ** 2 / s[i] ** 2 * (1.0 if i == j or skel.is_adjacent(i, j) else th)
        return v

    def posterior(j, lam, th):
        tj, X, y, XtX, Xty, yty = eqs[j]
        v0 = prior_var(j, tj, lam, th)
        prec = XtX + np.diag(1.0 / v0)
        L = np.linalg.cholesky(prec)
        bn = np.linalg.solve(L.T, np.linalg.solve(L, Xty))
        b0 = s[j] ** 2 / 2.0
        an = a0 + m_eff / 2.0
        bn_sc = b0 + 0.5 * max(yty - float(Xty @ bn), 1e-12)
        # log|V_n| - log|V_0| = -log|prec| - sum log v0
        logdet_ratio = -2.0 * np.log(np.diag(L)).sum() - np.log(v0).sum()
        log_ml = (math.lgamma(an) - math.lgamma(a0) + a0 * math.log(b0) - an * math.log(bn_sc)
                  + 0.5 * logdet_ratio - 0.5 * m_eff * math.log(2 * math.pi))
        return bn, L, an, bn_sc, log_ml

    best, best_val = None, -np.inf
    for lam in lambdas:
        for th in thetas:
            try:
                val = sum(posterior(j, lam, th)[4] for j in range(n)) + _gamma_logpdf_mode_sd(lam)
            except np.linalg.LinAlgError:
                continue
            if val > best_val:
                best, best_val = (lam, th), val
    if best is None:
        return _failed(name, "underdetermined")
    lam, th = best
    post = [posterior(j, lam, th) for j in range(n)]
    p = lag_max

    def to_B(betas):
        B = np.zeros((p + 1, n, n))
        for j, (tj, *_rest) in enumerate(eqs):
            for (i, lag), b in zip(tj, betas[j]):
                B[lag, j, i] = b
        return B

    B_mean = to_B([bn for bn, *_ in post])
    draws = []
    for _ in range(n_boot):
        betas = []
        for bn, L, an, bsc, _ in post:
            sig2 = bsc / rng.gamma(an)                       # sigma^2 ~ IG(an, bsc)
            z = rng.normal(size=len(bn))
            betas.append(bn + math.sqrt(sig2) * np.linalg.solve(L.T, z))   # N(bn, sig2 * prec^-1)
        draws.append(cumulative(irf(to_B(betas), H), H))
    draws = np.array(draws)
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(B_mean, H)
    return MethodResult(name, "ok", cumulative(theta, H), lo, hi, theta, B_mean,
                        {"lambda": lam, "theta": th,
                         "sigma2_post_mean_ratio": float(np.mean([(bsc / (an - 1)) / s[j] ** 2
                                                                  for j, (_, _, an, bsc, _) in enumerate(post)]))})


def bvar_minnesota_v2(data, skel, lag_max, H, n_boot, rng):
    return _cached("bvar_v2", _bvar_core, data, skel, lag_max, H, n_boot, "bvar_minnesota_v2")


def bvar_minnesota_v2_cal(data, skel, lag_max, H, n_boot, rng):
    return _cached("bvar_v2", _bvar_core, data, skel, lag_max, H, n_boot, "bvar_minnesota_v2_cal")


METHODS = {
    "pselect_union_v2": pselect_union_v2,
    "pselect_union_v2_cal": pselect_union_v2_cal,
    "bvar_minnesota_v2": bvar_minnesota_v2,
    "bvar_minnesota_v2_cal": bvar_minnesota_v2_cal,
}
