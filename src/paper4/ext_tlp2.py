"""Targeted Local Projections, round 2 (ID tlp2): a faithful double bootstrap, and a calibrated
single-level variant that no longer depends on a module-level cache.

Reference: Nemtyrev and Boldea, arXiv 2603.00248 (v2, 2026). The round-1 adaptation is
src/paper4/ext_tlp.py (left unchanged); its deviations D1-D7 are listed in docs/ext/tlp.md. This
module removes the deviations that a reviewer could read as a handicap of the baseline:

- D1 (single-level bootstrap) -> mean symmetric double bootstrap (MSDB) with the paper's
  B1 = 200 first-level and B2 = 100 second-level draws (eqs. 23-24, 27-28).
- D3 (p = lag_max + 1 = 3, q = 2) -> p = 2q = 4 when the LP keeps MIN_DOF residual dof at the
  last horizon, else the largest feasible p. 2q matches the paper's empirical (p, q) = (8, 4) and
  p - q = 2 its main simulation (10, 8). At T = 40 with n = 14 only p = 1 is feasible (as round 1).
- D6 (common LP sample for every horizon) -> horizon-specific LP samples t = p .. T-1-h, as the
  paper's stacked regression (W has T - h rows).
- D2 (95% level): kept for ``tlp2_db`` so that it is scored on the same scale as every Paper 4
  method; ``tlp2_db90`` is the same computation at the paper's 90% level (descriptive only).

Kept from round 1 (the paper is silent or the setting forces it):
- target = plug-in SVAR on the supplied skeleton (q = lag_max), shocks identified by the
  skeleton's contemporaneous parents, unit structural shocks; estimand C(H) = sum_h beta^TLP_h
  with per-(h, pair) weights; v clipped to [0, 1];
- bootstrap DGP = unrestricted reduced-form VAR(q) (the paper: "the reduced-form VAR"), moving
  blocks of length round(T^(1/3)), residuals rescaled by sqrt(rows/dof), companion radius capped
  at 0.98 (ext_tlp._VAR);
- inside the second level, the TLP weight of each draw uses that first-level draw's own
  second-level moments (D7).

Seeds and the cache (bug noted in docs/ext/synthesis_round1.md, section 5): every method here
draws its bootstrap from a generator seeded by the CONTENT of its inputs (data bytes, skeleton,
lag_max, H) and a family tag, not from the runner's stream. Two methods of one family therefore
compute the same thing on the same inputs whatever the call order, and the in-process cache is a
pure speed-up: a cache miss recomputes the identical result. ``tlp2_lp_cal`` does not use any
cache at all.
"""
from __future__ import annotations

import zlib

import numpy as np

from .estimator import parent_terms
from .ext_tlp import _VAR, targeted_lp, tlp_weight
from .skeleton import Skeleton
from .methods import ALPHA, MethodResult, _failed

B1 = 200
B2 = 100
MIN_DOF = 5
ALPHA_PAPER = 0.10
_TINY = 1e-12


# ----------------------------------------------------------------------------------------------
# content seed

def content_seed(data: np.ndarray, skel: Skeleton, lag_max: int, H: int, tag: str) -> int:
    """A seed fixed by what the method sees, so that results do not depend on call order."""
    h = zlib.crc32(np.ascontiguousarray(data, dtype=float).tobytes())
    sk = repr((sorted(skel.oriented), sorted(tuple(sorted(p)) for p in skel.undetermined), lag_max, H, tag))
    return zlib.crc32(sk.encode(), h)


# ----------------------------------------------------------------------------------------------
# batched building blocks (a leading axis b indexes bootstrap series)

def simulate_batch(gen: _VAR, T: int, B: int, rng: np.random.Generator) -> np.ndarray:
    """B moving-block residual bootstrap series of length T from ``gen`` (same scheme as
    ext_tlp._VAR.simulate, vectorised over series)."""
    m, n = gen.resid.shape
    ell = max(1, int(round(T ** (1 / 3))))
    need = T - gen.q
    nblk = int(np.ceil(need / ell))
    starts = rng.integers(0, m - ell + 1, size=(B, nblk))
    idx = (starts[:, :, None] + np.arange(ell)).reshape(B, -1)[:, :need]
    draws = gen.resid[idx]                                   # (B, need, n)
    x = np.empty((B, T, n))
    x[:, : gen.q] = gen.x0
    c = gen.c if gen.shrunk == 1.0 else (np.eye(n) - sum(gen.A)) @ gen.mu
    At = [a.T for a in gen.A]
    for t in range(gen.q, T):
        acc = c + draws[:, t - gen.q]
        for k in range(gen.q):
            acc = acc + x[:, t - 1 - k] @ At[k]
        x[:, t] = acc
    return x


def _solve(G: np.ndarray, R: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.solve(G, R)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(G) @ R


def var_responses_batch(x: np.ndarray, terms, lag_max: int, H: int) -> np.ndarray | None:
    """Skeleton SVAR (estimator.fit_equations, OLS with intercept) on each series, then the IRF to
    unit structural shocks. Returns (B, H+1, n, n) or None if some equation is underdetermined."""
    Bn, T, n = x.shape
    rows = np.arange(lag_max, T)
    m = len(rows)
    Bm = np.zeros((Bn, lag_max + 1, n, n))
    for j in range(n):
        tj = terms[j]
        if not tj:
            continue
        if len(tj) + 2 > m:
            return None
        X = np.stack([x[:, rows - lag, i] for i, lag in tj], axis=2)        # (B, m, k)
        y = x[:, rows, j]
        Xc = X - X.mean(axis=1, keepdims=True)
        yc = (y - y.mean(axis=1, keepdims=True))[..., None]
        Xt = np.swapaxes(Xc, 1, 2)
        beta = _solve(Xt @ Xc, Xt @ yc)[..., 0]
        for col, (i, lag) in enumerate(tj):
            Bm[:, lag, j, i] = beta[:, col]
    return irf_batch(Bm, H)


def irf_batch(Bm: np.ndarray, H: int) -> np.ndarray:
    Bn, P1, n, _ = Bm.shape
    A = np.linalg.inv(np.eye(n) - Bm[:, 0])
    th = np.zeros((Bn, H + 1, n, n))
    th[:, 0] = A
    for h in range(1, H + 1):
        acc = np.zeros((Bn, n, n))
        for k in range(1, min(h, P1 - 1) + 1):
            acc += Bm[:, k] @ th[:, h - k]
        th[:, h] = A @ acc
    return th


def lp_lags(T: int, n: int, H: int, lag_max: int, max_parents: int) -> int:
    """p = 2 * lag_max if the LP at the last horizon keeps MIN_DOF residual dof, else the largest
    feasible p (1 if none is)."""
    for p in range(2 * lag_max, 0, -1):
        rows = T - H - p
        cols = 1 + n * p + 1 + max_parents            # intercept, lags, shock, parents
        if rows - cols >= MIN_DOF:
            return p
    return 1


def lp_responses_batch(x: np.ndarray, parents: list[list[int]], p: int, H: int) -> np.ndarray:
    """theta_LP[b, h, j, i] with a horizon-specific sample t = p .. T-1-h: coefficient of x_{i,t}
    in the regression of x_{j,t+h} on x_{i,t}, the skeleton parents of i at t, an intercept and
    lags 1..p of every node. NaN where the regression has no residual dof (caller fills with the
    target's response)."""
    Bn, T, n = x.shape
    out = np.full((Bn, H + 1, n, n), np.nan)
    for h in range(H + 1):
        rows = np.arange(p, T - h)
        W = np.concatenate([np.ones((Bn, len(rows), 1))] + [x[:, rows - lag] for lag in range(1, p + 1)], axis=2)
        M = np.concatenate([x[:, rows], x[:, rows + h]], axis=2)                 # [Z, Y], (B, r, 2n)
        Wt = np.swapaxes(W, 1, 2)
        WM = Wt @ M
        # Frisch-Waugh on cross-products: residual moments of [Z, Y] after projecting out W
        R = np.swapaxes(M, 1, 2) @ M - np.swapaxes(WM, 1, 2) @ _solve(Wt @ W, WM)
        free = len(rows) - W.shape[2]
        groups: dict[int, list[int]] = {}
        for i in range(n):
            if free - (1 + len(parents[i])) >= 1:
                groups.setdefault(1 + len(parents[i]), []).append(i)
        for size, shocks in groups.items():      # one batched solve per regressor-set size
            Sa = np.array([[i] + parents[i] for i in shocks])                     # (k, size)
            beta = _solve(R[:, Sa[:, :, None], Sa[:, None, :]], R[:, Sa, n:])      # (B, k, size, n)
            # mixed indexing puts the shock axis first: out[:, h, :, shocks] has shape (k, B, n)
            out[:, h, :, shocks] = beta[:, :, 0, :].transpose(1, 0, 2)
    return out


def _fill(lp, var):
    return np.where(np.isnan(lp), var, lp)


def _moments(lp, var):
    """Variance of LP and covariance of LP with VAR over the leading (draw) axis."""
    dl = lp - lp.mean(axis=0)
    dv = var - var.mean(axis=0)
    k = len(lp) - 1
    return (dl ** 2).sum(axis=0) / k, (dl * dv).sum(axis=0) / k


# ----------------------------------------------------------------------------------------------
# the double bootstrap

def msdb(data, skel: Skeleton, lag_max: int, H: int, *, b1: int = B1, b2: int = B2, p: int | None = None,
         tag: str = "tlp2_db"):
    """Mean symmetric double bootstrap of TLP for C(H). Returns a dict with C, theta, the
    half-widths at the 95% and 90% levels and diagnostics, or a dict with a failure status."""
    T, n = data.shape
    parents = [sorted(u for u, v in skel.oriented if v == i) for i in range(n)]
    if p is None:
        p = lp_lags(T, n, H, lag_max, max(len(pa) for pa in parents))
    terms = [parent_terms(skel, j, lag_max) for j in range(n)]
    rng = np.random.default_rng(content_seed(data, skel, lag_max, H, tag))

    x0 = data[None]
    var0 = var_responses_batch(x0, terms, lag_max, H)
    if var0 is None:
        return {"status": "underdetermined"}
    raw0 = lp_responses_batch(x0, parents, p, H)
    n_inf = int(np.isnan(raw0[0, 0, 0]).sum())
    lp0, var0 = _fill(raw0, var0)[0], var0[0]
    gen = _VAR(data, lag_max)
    if not gen.ok:
        return {"status": "underdetermined"}

    lp1, var1, s_lp, s_cov, s_c = [], [], [], [], []
    tries = 0
    while len(lp1) < b1 and tries < 3 * b1:
        tries += 1
        xb = simulate_batch(gen, T, 1, rng)
        if not np.all(np.isfinite(xb)):
            continue
        vb = var_responses_batch(xb, terms, lag_max, H)
        if vb is None:
            continue
        g2 = _VAR(xb[0], lag_max)
        if not g2.ok:
            continue
        x2 = simulate_batch(g2, T, b2, rng)
        good = np.all(np.isfinite(x2), axis=(1, 2))
        if good.sum() < 5:
            continue
        x2 = x2[good]
        v2 = var_responses_batch(x2, terms, lag_max, H)
        if v2 is None:
            continue
        l2 = _fill(lp_responses_batch(x2, parents, p, H), v2)
        ok2 = np.all(np.isfinite(l2), axis=(1, 2, 3)) & np.all(np.isfinite(v2), axis=(1, 2, 3))
        if ok2.sum() < 5:
            continue
        l2, v2 = l2[ok2], v2[ok2]
        m_lp, m_cov = _moments(l2, v2)                         # second-level moments of draw b1
        w2 = tlp_weight(l2, v2, m_lp, m_cov)
        c2 = (w2 * l2 + (1 - w2) * v2).sum(axis=1)             # inner TLP C(H), (b2, n, n)
        lp1.append(_fill(lp_responses_batch(xb, parents, p, H), vb)[0])
        var1.append(vb[0])
        s_lp.append(m_lp); s_cov.append(m_cov); s_c.append(c2.var(axis=0, ddof=1))
    if len(lp1) < max(10, b1 // 4):
        return {"status": "bootstrap_failed"}
    lp1, var1, s_c = np.array(lp1), np.array(var1), np.array(s_c)
    var_lp = np.mean(s_lp, axis=0)                              # eq. 24: averaged over b1
    cov = np.mean(s_cov, axis=0)
    v0 = tlp_weight(lp0, var0, var_lp, cov)
    theta = v0 * lp0 + (1 - v0) * var0
    C = theta.sum(axis=0)
    w1 = tlp_weight(lp1, var1, var_lp, cov)                     # bias part re-estimated per b1
    C1 = (w1 * lp1 + (1 - w1) * var1).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.abs(C1 - C1.mean(axis=0)) / np.sqrt(s_c)          # eq. 27, centred at the b1 mean
    t = np.where(s_c > _TINY, t, 0.0)
    sd = np.sqrt(C1.var(axis=0, ddof=1))                        # Sigma^TLP of the original sample
    half = {a: np.quantile(t, 1 - a, axis=0) * sd for a in (ALPHA, ALPHA_PAPER)}   # eq. 28
    off = ~np.eye(n, dtype=bool)
    info = {"p_lp": p, "n_shock_lp_infeasible": n_inf, "b1": len(lp1), "b2": b2,
            "var_radius": round(gen.radius, 4), "var_shrunk": gen.shrunk != 1.0,
            "v_mean": round(float(v0[1:].mean()), 4), "v_mean_h0_off": round(float(v0[0][off].mean()), 4),
            "tq95_median": round(float(np.median(np.quantile(t, 1 - ALPHA, axis=0)[off])), 4)}
    return {"status": "ok", "C": C, "theta": theta, "half": half, "info": info}


_CACHE: dict = {}


def _db_result(data, skel, lag_max, H):
    """Shared by tlp2_db and tlp2_db90. Content-seeded, so a cache miss gives the same result."""
    key = (content_seed(data, skel, lag_max, H, "tlp2_db"), data.shape)
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = msdb(data, skel, lag_max, H)
    return _CACHE[key]


def _as_result(name, r, alpha, store_interval=False):
    if r["status"] != "ok":
        return _failed(name, r["status"])
    C, half = r["C"], r["half"][alpha]
    info = dict(r["info"])
    if store_interval:   # lets the scorer compute the interval score at the paper's own level
        info["lo"] = np.round(C - half, 6).tolist()
        info["hi"] = np.round(C + half, 6).tolist()
    return MethodResult(name, "ok", C, C - half, C + half, r["theta"], None, info)


def _tlp2_db(data, skel, lag_max, H, n_boot, rng):
    """MSDB (B1 = 200, B2 = 100, p = 2q, horizon-specific LP samples) at the 95% level."""
    return _as_result("tlp2_db", _db_result(data, skel, lag_max, H), ALPHA)


def _tlp2_db90(data, skel, lag_max, H, n_boot, rng):
    """Same computation as tlp2_db, interval at the paper's 90% level (descriptive)."""
    return _as_result("tlp2_db90", _db_result(data, skel, lag_max, H), ALPHA_PAPER, store_interval=True)


def _tlp2_lp_cal(data, skel, lag_max, H, n_boot, rng):
    """Round-1 single-level targeted_lp (ext_tlp.targeted_lp, unchanged estimator), computed here
    on every call with a content seed: no cache, no dependence on another method having run.
    Listed in ``calibrate_methods`` so the runner widens it per (T, stated kind) as tolerant_v4."""
    g = np.random.default_rng(content_seed(data, skel, lag_max, H, "tlp2_lp"))
    res = targeted_lp(data, skel, lag_max, H, n_boot, g, name="tlp2_lp_cal")
    return res


def _tlp2_db_p3(data, skel, lag_max, H, n_boot, rng):
    """Sensitivity variant of tlp2_db (added in round 2 before the evaluation rule was written):
    the same MSDB (B1 = 200, B2 = 100, horizon-specific LP samples, 95% level) but with the round-1
    LP lag order p = lag_max + 1 (ext_tlp._lp_lags), i.e. the p of the round-1 double-bootstrap
    probe. Separates the effect of p from the effect of the double bootstrap."""
    from .ext_tlp import _lp_lags
    T, n = data.shape
    parents = [sorted(u for u, v in skel.oriented if v == i) for i in range(n)]
    p = _lp_lags(T, n, H, lag_max, max(len(pa) for pa in parents))
    return _as_result("tlp2_db_p3", msdb(data, skel, lag_max, H, p=p, tag="tlp2_db_p3"), ALPHA)


METHODS = {"tlp2_db": _tlp2_db, "tlp2_db90": _tlp2_db90, "tlp2_db_p3": _tlp2_db_p3, "tlp2_lp_cal": _tlp2_lp_cal}
