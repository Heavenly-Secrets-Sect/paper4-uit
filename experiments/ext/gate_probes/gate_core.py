"""Prototype of B1 v3 (gate). Copied into src/paper4/ext_gate.py once the design is fixed."""
from __future__ import annotations

import math

import numpy as np

from paper4.diagnose import _norm_sf, _wald_p, storey_nonnull
from paper4.effects import cumulative, irf
from paper4.estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, simulate_from_fit
from paper4.methods import ALPHA, MethodResult, _failed, _too_few
from paper4.skeleton import Skeleton, _creates_cycle


def leftout_tests(data, skel: Skeleton, lag_max: int, pairs_out):
    """For every left-out pair: (p_combined, p_corr) from the skeleton's structural all-lag fit
    (own and others' lags 1..lag_max, plus the skeleton's contemporaneous parents)."""
    T, n = data.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    L = np.column_stack([data[rows - lag, i] for lag in range(1, lag_max + 1) for i in range(n)])
    fits = []
    for j in range(n):
        pa = sorted(u for u, v in skel.oriented if v == j)
        X = np.column_stack([np.ones(m), L] + [data[rows, u] for u in pa]) if pa else np.column_stack([np.ones(m), L])
        if X.shape[1] + 2 > m:
            raise ValueError("underdetermined")
        XtX_inv = np.linalg.inv(X.T @ X)
        beta = XtX_inv @ (X.T @ data[rows, j])
        resid = data[rows, j] - X @ beta
        dof = m - X.shape[1]
        fits.append((beta, XtX_inv * (resid @ resid / dof), resid, dof))
    R = np.column_stack([f[2] for f in fits])
    corr = np.corrcoef(R.T)
    out_p, out_c = [], []
    for u, v in pairs_out:
        ps = []
        for src, eq in ((u, v), (v, u)):
            beta, cov, _, dof = fits[eq]
            idx = [1 + (lag - 1) * n + src for lag in range(1, lag_max + 1)]
            ps.append(_wald_p(beta[idx], cov[np.ix_(idx, idx)], dof))
        r = float(np.clip(corr[u, v], -0.999999, 0.999999))
        z = math.atanh(r) * math.sqrt(max(min(fits[u][3], fits[v][3]) - 1, 1))
        pc = 2 * _norm_sf(abs(z))
        ps.append(pc)
        out_p.append(1 - (1 - min(ps)) ** 3)
        out_c.append(pc)
    return np.array(out_p), np.array(out_c)


def _bh(p: np.ndarray, q: float) -> np.ndarray:
    order = np.argsort(p)
    k = len(p)
    ok = p[order] <= q * np.arange(1, k + 1) / k
    keep = np.zeros(k, dtype=bool)
    if ok.any():
        keep[order[: np.max(np.nonzero(ok)[0]) + 1]] = True
    return keep


def gate(data, skel, lag_max, rng, n_gate=99, stat="minp"):
    """Global test of 'no missing edge'. Returns (p_gate, p_comb, p_corr, pairs_out, null_fit)."""
    n = skel.n
    present = skel.pairs()
    pairs_out = [(u, v) for u in range(n) for v in range(u + 1, n) if frozenset((u, v)) not in present]
    p, pc = leftout_tests(data, skel, lag_max, pairs_out)

    def S(pp):
        if stat == "minp":
            return float(pp.min())
        return -float(np.sum(np.log(np.maximum(pp, 1e-300))))  # fisher: larger = more evidence

    s0 = S(p)
    if n_gate == 0:  # analytic Sidak over pairs (minp only)
        return 1 - (1 - s0) ** len(p), p, pc, pairs_out
    null = fit_equations(data, [parent_terms(skel, j, lag_max) for j in range(n)], lag_max)
    if null.status != "ok":
        raise ValueError("underdetermined")
    hits, done = 0, 0
    for _ in range(n_gate):
        xb = simulate_from_fit(null, data, rng)
        try:
            pb, _ = leftout_tests(xb, skel, lag_max, pairs_out)
        except (ValueError, np.linalg.LinAlgError):
            continue
        sb = S(pb)
        hits += (sb <= s0) if stat == "minp" else (sb >= s0)
        done += 1
    return (1 + hits) / (1 + done), p, pc, pairs_out


def auto3_raw(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, alpha_gate=0.05, n_gate=99,
              stat="minp", q=0.10, budget="max", open_all=False, name="tolerant_auto3"):
    """Uncalibrated interval plus the gate state in info['state']."""
    n = skel.n
    base = skel.copy()
    base.damage = {}
    try:
        p_gate, p, pc, pairs_out = gate(data, base, lag_max, rng, n_gate, stat)
    except (ValueError, np.linalg.LinAlgError):
        p_gate, p, pc, pairs_out = None, None, None, []
    info = {"p_gate": p_gate}
    if p_gate is None or p_gate > alpha_gate:
        state = "closed" if p_gate is not None else "undiagnosable"
        opened, cands = [], []
        terms_of = lambda s: [parent_terms(s, j, lag_max) for j in range(n)]  # noqa: E731
    else:
        state = "open"
        disc = _bh(p, q)
        k_st = int(np.floor(storey_nonnull(list(p)) + 0.5))
        K = max(int(disc.sum()), 1) if budget == "bh" else max(int(disc.sum()), k_st, 1)
        order = np.argsort(p)[:K]
        opened = [pairs_out[i] for i in order]
        corr_disc = _bh(pc, q)
        cands = [pairs_out[i] for i in order if corr_disc[i]]
        info.update({"n_bh": int(disc.sum()), "k_storey": k_st})
        if open_all:
            from paper4.estimator import soft_terms
            terms_of = lambda s: [soft_terms(s, j, lag_max) for j in range(n)]  # noqa: E731
        else:
            terms_of = lambda s: [parent_terms(s, j, lag_max) for j in range(n)]  # noqa: E731
    info.update({"state": state, "n_open": len(opened), "n_repair": len(cands)})
    s_open = base.copy()
    for u, v in opened:
        s_open.undetermined.add(frozenset((u, v)))

    def draw_skel():
        s = s_open.copy()
        for u, v in cands:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (e[1], e[0])
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_of(draw_skel()), lag_max)
    if fit.status != "ok":
        return _failed(name, fit.status)
    refit = (lambda x: fit_equations(x, terms_of(draw_skel()), lag_max)) if cands else None
    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if cands else cumulative(theta, H)
    return MethodResult(name, "ok", C, lo, hi, theta, fit.B, info)
