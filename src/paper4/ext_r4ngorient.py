"""Round 4, ID "ngorient": gated non-Gaussian orientation of the module's contemporaneous draws.

Background (docs/ext/r4ngorient.md). ``tolerant_v5_1`` (ext_v51.py) draws two kinds of contemporaneous
direction at random in every bootstrap draw:

- step 3, contemporaneous repair: a pair found by Benjamini-Hochberg on the structural residuals is
  added with direction u -> v or v -> u with probability 1/2 each;
- step 4, targeted reversal: k_rev pairs of the significant contemporaneous pool are flipped, chosen
  by a uniform permutation (``methods._flip_from``).

Under Gaussian shocks the direction of an isolated contemporaneous link is not identified, so the
fair coin is the right thing. Under non-Gaussian shocks it is (Shimizu et al. 2006; Hyvarinen et al.
2010, VARLiNGAM; Lanne, Meitz and Saikkonen 2017). This module replaces only the two coins by
evidence from the pairwise likelihood-ratio measure of Hyvarinen and Smith (2013, JMLR 14:111-152),
behind a Jarque-Bera non-Gaussianity gate (the "test before you identify by non-Gaussianity" advice
of Montiel Olea, Plagborg-Moller and Qian 2022, AEA P&P 112:481-485). Nothing else changes.

Direction evidence for a pair (u, v), function ``ng_evidence``:
- x, y = structural residuals of u and v from equations that EXCLUDE any u-v contemporaneous term
  (repair candidate: residuals of the base fit, where u and v are not adjacent; pool edge u -> v:
  u's residual of the base fit and v's equation refitted without u_t), standardised over m rows;
- gate: JB_i = m (skew_i^2 / 6 + exkurt_i^2 / 24), p_i = chi2_2 tail = exp(-JB_i / 2); the gate opens
  when 1 - (1 - min(p_x, p_y))^2 < 0.10 (Sidak over the two series);
- S = m (skew_x^2 + skew_y^2) / 6, K = m (exkurt_x^2 + exkurt_y^2) / 24. If S >= K: skew form, each
  series' sign flipped so its skewness is positive, R = rho mean(x^2 y - x y^2) (H-S 2013 section 2.6,
  third-order cumulant). Else tanh form R = rho mean(x tanh y - tanh(x) y) (H-S 2013 eq. for sparse
  / super-Gaussian sources), times -1 when the mean excess kurtosis of the pair is negative;
- R > 0 means u -> v (x = u). se(R) by a delete-one-block jackknife over 10 contiguous row blocks
  (form and sign flips fixed from the full sample, standardisation redone in each subsample);
- p_uv = Phi(R / se), clipped to [0.05, 0.95]; p_uv = 0.5 exactly when the gate is closed.

Use of the evidence (arm NG-A, ``tolerant_ngA``):
- step 3: ``rng.random() < p_uv`` instead of ``rng.random() < 0.5`` (cycle check unchanged; the number
  of random-number calls is unchanged, so under a closed gate the draws are those of v5_1);
- step 4: Plackett-Luce order of the pool with weight w_e = 1 - p(stated direction of e) through
  Efraimidis-Spirakis keys U^(1 / w_e), then the first k_rev flips that keep the graph acyclic, as
  ``_flip_from``. When every w_e is 0.5 (all gates closed) ``methods._flip_from`` itself is called,
  which has the same distribution (and, on the same stream, the same draws) as v5_1.
- Per-draw recomputation: in every bootstrap draw the draw's base terms are fitted first (one extra
  ``fit_equations`` in the ``tolerant`` branch; the targeted branch already fits them), gate and p are
  computed from that draw's residuals, then the structure is drawn and refitted.

Arm NG-B (``tolerant_ngB``, secondary): log-odds = Gaussian evidence + logit(NG-A's p):
- pool edge e: log-odds that e is reversed = dl_e (``ext_revlag3.orientation_evidence``: Gaussian
  log-likelihood of the structural system with e flipped minus as stated) + logit(w_e);
- repair candidate (u, v): log-odds of u -> v = Gaussian log-likelihood of the two equations with
  u -> v minus with v -> u (same terms as the draw would fit) + logit(p_uv);
- both mapped back by the logistic function and clipped to [0.05, 0.95], then used as in NG-A.

Everything else is ``tolerant_v5_1`` line for line: the same switch (``ext_v51.allag_ratio`` < TAU), the
same targeted opening re-selected per draw with de-duplicated terms, the same BH repair, the same
contemporaneous pool, residual bootstrap of 199 draws, percentile interval, PRESCALE 0.5 for the
runner's two-sided width calibration per (T, stated kind). The width factor is tuned on GAUSSIAN
D-07H development: the module does not know the shock law.

Methods read only the data, the public skeleton and ``skel.damage``. Diagnostics of the evidence
(data level and per draw) are returned in ``info["ng_diag"]`` for the evaluation, which compares
them with the truth outside the method.
"""
from __future__ import annotations

import math

import numpy as np

from . import methods as M
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .ext_narrow import _prescale, opened_terms, select_open
from .ext_revlag3 import _flip_ordered, _rss, orientation_evidence
from .ext_v51 import TAU, allag_ratio
from .skeleton import Skeleton, _creates_cycle

GATE_ALPHA = 0.10
N_BLOCKS = 10
P_CLIP = (0.05, 0.95)


# ----------------------------------------------------------------------------- evidence

def _std(r: np.ndarray) -> np.ndarray | None:
    r = np.asarray(r, float)
    c = r - r.mean()
    s = math.sqrt(float(c @ c) / len(c)) if len(c) else 0.0
    return c / s if s > 0 and math.isfinite(s) else None


def _phi(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2))


def ng_evidence(xr, yr, *, n_blocks: int = N_BLOCKS, gate_alpha: float = GATE_ALPHA) -> dict:
    """Gated Hyvarinen-Smith pairwise evidence that x -> y (module doc). Returns
    {"p": P(x -> y) in [0.05, 0.95] or 0.5, "gate": bool, "gate_p", "R", "se", "form"}."""
    out = {"p": 0.5, "gate": False, "gate_p": 1.0, "R": 0.0, "se": float("nan"), "form": "none"}
    if xr is None or yr is None:
        return out
    x, y = _std(xr), _std(yr)
    if x is None or y is None:
        return out
    m = len(x)
    skx, sky = float(np.mean(x ** 3)), float(np.mean(y ** 3))
    ekx, eky = float(np.mean(x ** 4)) - 3.0, float(np.mean(y ** 4)) - 3.0
    jbx, jby = m * (skx ** 2 / 6 + ekx ** 2 / 24), m * (sky ** 2 / 6 + eky ** 2 / 24)
    px, py = math.exp(-jbx / 2), math.exp(-jby / 2)   # chi2(2) upper tail
    gate_p = 1 - (1 - min(px, py)) ** 2
    out["gate_p"] = gate_p
    if not gate_p < gate_alpha:
        return out
    out["gate"] = True
    S = m * (skx ** 2 + sky ** 2) / 6
    K = m * (ekx ** 2 + eky ** 2) / 24
    if S >= K:
        form = "skew"
        sx = -1.0 if skx < 0 else 1.0
        sy = -1.0 if sky < 0 else 1.0
        ks = 1.0
    else:
        form = "tanh"
        sx = sy = 1.0
        ks = -1.0 if (ekx + eky) / 2 < 0 else 1.0
    xr, yr = np.asarray(xr, float), np.asarray(yr, float)

    def stat(idx) -> float | None:
        a, b = _std(xr[idx]), _std(yr[idx])
        if a is None or b is None:
            return None
        a, b = sx * a, sy * b
        rho = float(np.mean(a * b))
        if form == "skew":
            return rho * float(np.mean(a * a * b - a * b * b))
        return ks * rho * float(np.mean(a * np.tanh(b) - np.tanh(a) * b))

    R = stat(np.arange(m))
    reps = []
    for blk in np.array_split(np.arange(m), n_blocks):
        keep = np.setdiff1d(np.arange(m), blk)
        r = stat(keep)
        if r is not None and math.isfinite(r):
            reps.append(r)
    out["form"] = form
    if R is None or not math.isfinite(R) or len(reps) < 2:
        return out
    reps = np.array(reps)
    B = len(reps)
    se = math.sqrt((B - 1) / B * float(((reps - reps.mean()) ** 2).sum()))
    out["R"], out["se"] = float(R), se
    if not (se > 0 and math.isfinite(se)):
        return out
    out["p"] = min(max(_phi(R / se), P_CLIP[0]), P_CLIP[1])
    return out


def _ols_resid(x: np.ndarray, terms_j, j: int, lag_max: int) -> np.ndarray | None:
    """Residuals of one structural equation (OLS with intercept), as fit_equations."""
    T = x.shape[0]
    rows = np.arange(lag_max, T)
    y = x[rows, j]
    if not terms_j:
        return y - y.mean()
    if len(terms_j) + 2 > len(rows):
        return None
    X = np.column_stack([x[rows - lag, i] for i, lag in terms_j])
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    beta = np.linalg.lstsq(Xc, yc, rcond=None)[0]
    return yc - Xc @ beta


def _logit(p: float) -> float:
    return math.log(p / (1 - p))


def _sigmoid_clip(a: float) -> float:
    p = 1 / (1 + math.exp(-a)) if a > -700 else 0.0
    return min(max(p, P_CLIP[0]), P_CLIP[1])


def pool_probs(x, fitb, pool, skel: Skeleton, lag_max: int, full_lags: bool, arm: str):
    """Probability that each pool edge (stated u -> v) is reversed, and its evidence record."""
    w, rec = [], []
    dl = orientation_evidence(x, skel, pool, lag_max, full_lags) if arm == "B" and pool else None
    for idx, (u, v) in enumerate(pool):
        xr = fitb.residuals[:, u]
        tv = [t for t in fitb.terms[v] if t != (u, 0)]
        yr = _ols_resid(x, tv, v, lag_max)
        ev = ng_evidence(xr, yr)
        wa = 1 - ev["p"]
        if arm == "B":
            wb = _sigmoid_clip(float(dl[idx]) + _logit(wa))
            w.append(wb)
            rec.append((u, v, ev["gate"], ev["p"], float(dl[idx]), wb))
        else:
            w.append(wa)
            rec.append((u, v, ev["gate"], ev["p"]))
    return w, rec


def cand_probs(x, f0, cs, base_skel: Skeleton, term_fn, lag_max: int, arm: str):
    """P(u -> v) for each repair candidate (u, v), and its evidence record."""
    p, rec = [], []
    for u, v in cs:
        ev = ng_evidence(f0.residuals[:, u], f0.residuals[:, v])
        if arm == "B":
            dl = 0.0
            s1, s2 = base_skel.copy(), base_skel.copy()
            s1.oriented.add((u, v))
            s2.oriented.add((v, u))
            r = [_rss(x, term_fn(s, j), j, lag_max) for s in (s1, s2) for j in (u, v)]
            if all(q is not None and q > 0 for q in r):
                m = x.shape[0] - lag_max
                dl = -0.5 * m * (math.log(r[0]) + math.log(r[1]) - math.log(r[2]) - math.log(r[3]))
            pb = _sigmoid_clip(dl + _logit(ev["p"]))
            p.append(pb)
            rec.append((u, v, ev["gate"], ev["p"], dl, pb))
        else:
            p.append(ev["p"])
            rec.append((u, v, ev["gate"], ev["p"]))
    return p, rec


def _flip_weighted(skel: Skeleton, pool, w, k: int, rng) -> Skeleton:
    """Plackett-Luce order with weights w (Efraimidis-Spirakis keys), then ``_flip_from``'s rule.
    All weights 0.5 -> ``methods._flip_from`` itself (same distribution as v5_1)."""
    if all(wi == 0.5 for wi in w):
        return M._flip_from(skel, pool, k, rng)
    keys = rng.random(len(pool)) ** (1.0 / np.asarray(w, float))
    return _flip_ordered(skel, pool, list(np.argsort(-keys, kind="stable")), k)


def _add_repairs(s: Skeleton, cs, pc, rng, n: int, tally=None) -> Skeleton:
    for (u, v), p in zip(cs, pc):
        e = (u, v) if rng.random() < p else (v, u)
        if _creates_cycle(s.oriented | {e}, n):
            e = (v, u) if e == (u, v) else (u, v)
        if not _creates_cycle(s.oriented | {e}, n):
            s.oriented.add(e)
            if tally is not None:
                t = tally.setdefault(f"{u}-{v}", [0, 0])
                t[0] += 1
                t[1] += int(e == (u, v))
    return s


class _Diag:
    """Evidence diagnostics (no truth): data-level records and per-draw tallies."""

    def __init__(self):
        self.data_cands, self.data_pool = [], []
        self.cand_tally = {}          # "u-v" -> [n draws with the pair repaired, n oriented u -> v]
        self.pool_tally = {}          # "u-v" -> [n draws evaluated, n flipped]
        self.n_gate = [0, 0]          # [pairs evaluated, gates open] over draws (candidates and pool)

    def gates(self, rec):
        self.n_gate[0] += len(rec)
        self.n_gate[1] += sum(1 for r in rec if r[2])

    def flips(self, pool, s: Skeleton):
        for u, v in pool:
            t = self.pool_tally.setdefault(f"{u}-{v}", [0, 0])
            t[0] += 1
            t[1] += int((v, u) in s.oriented)

    def as_dict(self):
        return {"data_cands": self.data_cands, "data_pool": self.data_pool, "cand_tally": self.cand_tally,
                "pool_tally": self.pool_tally, "n_gate_draws": self.n_gate}


# ----------------------------------------------------------------------------- branches

def _tolerant_ng(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, arm: str,
                 name: str) -> M.MethodResult:
    """``methods.tolerant(target_reversal=True)`` with gated non-Gaussian orientation draws."""
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    full_lags = k_miss > 0
    term_j = (lambda s, j: soft_terms(s, j, lag_max)) if full_lags else (lambda s, j: parent_terms(s, j, lag_max))
    terms_of = lambda s: [term_j(s, j) for j in range(n)]  # noqa: E731
    fit0 = fit_equations(data, terms_of(skel), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status)
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    draw_structure = bool(cands) or reversing
    pool = M.contemporaneous_pool(data, fit0, k_rev) if reversing else None
    diag = _Diag()

    def evidence(x, fb, record=False):
        pc, rc = cand_probs(x, fb, cands, skel, term_j, lag_max, arm) if cands else ([], [])
        w, rp = pool_probs(x, fb, pool, skel, lag_max, full_lags, arm) if reversing else ([], [])
        if record:
            diag.data_cands, diag.data_pool = rc, rp
        else:
            diag.gates(rc)
            diag.gates(rp)
        return pc, w

    def draw_skel(pc, w, tally=None) -> Skeleton:
        s = _flip_weighted(skel, pool, w, k_rev, rng) if reversing else skel.copy()
        if tally is not None and reversing:
            diag.flips(pool, s)
        return _add_repairs(s, cands, pc, rng, n, tally)

    pc0, w0 = evidence(data, fit0, record=True)
    fit = fit_equations(data, terms_of(draw_skel(pc0, w0)), lag_max) if cands else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status)

    def refit(x):
        fb = fit_equations(x, terms_of(skel), lag_max)
        if fb.status != "ok":
            return fb
        pc, w = evidence(x, fb)
        return fit_equations(x, terms_of(draw_skel(pc, w, diag.cand_tally)), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit if draw_structure else None)
    if M._too_few(draws, n_boot):
        return M._failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    C = draws.mean(axis=0) if draw_structure else cumulative(theta, H)
    return M.MethodResult(name, "ok", C, lo, hi, theta, fit.B,
                          {"n_repair": len(cands), "full_lags": full_lags,
                           "n_reversal_pool": None if pool is None else len(pool), "ng_diag": diag.as_dict()})


def _sel_dd_ng(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, arm: str, name: str,
               mult: float = 3.0, alpha_open: float = 0.10) -> M.MethodResult:
    """``ext_v51.tolerant_sel_dd`` (reselect=True) with gated non-Gaussian orientation draws."""
    n = skel.n
    stated = M.stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    try:
        opened = select_open(data, skel, lag_max, k_miss, mult, alpha_open)
    except ValueError:
        return M._failed(name, "underdetermined")

    def terms_for(s: Skeleton, op):
        return [list(dict.fromkeys(opened_terms(s, op, j, lag_max))) for j in range(n)]

    fit0 = fit_equations(data, terms_for(skel, opened), lag_max)
    if fit0.status != "ok":
        return M._failed(name, fit0.status)
    cands = M.repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    pool = M.contemporaneous_pool(data, fit0, k_rev) if reversing else None
    diag = _Diag()

    def evidence(x, fb, cs, op, record=False):
        tf = lambda s, j: list(dict.fromkeys(opened_terms(s, op, j, lag_max)))  # noqa: E731
        pc, rc = cand_probs(x, fb, cs, skel, tf, lag_max, arm) if cs else ([], [])
        # pool edges: the reversal draws of v5_1 use the full skeleton's terms in the evidence (as v3)
        w, rp = pool_probs(x, fb, pool, skel, lag_max, False, arm) if reversing else ([], [])
        if record:
            diag.data_cands, diag.data_pool = rc, rp
        else:
            diag.gates(rc)
            diag.gates(rp)
        return pc, w

    def draw_skel(cs, pc, w, tally=None) -> Skeleton:
        s = _flip_weighted(skel, pool, w, k_rev, rng) if reversing else skel.copy()
        if tally is not None and reversing:
            diag.flips(pool, s)
        return _add_repairs(s, cs, pc, rng, n, tally)

    pc0, w0 = evidence(data, fit0, cands, opened, record=True)
    fit = fit_equations(data, terms_for(draw_skel(cands, pc0, w0), opened), lag_max) if cands else fit0
    if fit.status != "ok":
        return M._failed(name, fit.status)
    n_open = []

    def refit(x):
        try:
            op = select_open(x, skel, lag_max, k_miss, mult, alpha_open)
        except ValueError:
            op = opened
        n_open.append(len(op))
        f0 = fit_equations(x, terms_for(skel, op), lag_max)
        if f0.status != "ok":
            return f0
        cs = M.repair_candidates(f0.residuals, skel, k_miss)
        if not cs and not reversing:
            return f0
        pc, w = evidence(x, f0, cs, op)
        return fit_equations(x, terms_for(draw_skel(cs, pc, w, diag.cand_tally), op), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if M._too_few(draws, n_boot):
        return M._failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    return M.MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                          {"n_repair": len(cands), "n_open": len(opened),
                           "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                           "n_reversal_pool": None if pool is None else len(pool), "ng_diag": diag.as_dict()})


def _v51_ng(data, skel, lag_max, H, n_boot, rng, *, arm: str, name: str) -> M.MethodResult:
    """``ext_v51.tolerant_v5_1`` with the NG orientation of steps 3 and 4 (module doc)."""
    T = data.shape[0]
    k_miss = M.stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    if targeted:
        res = _sel_dd_ng(data, skel, lag_max, H, n_boot, rng, arm=arm, name=name)
    else:
        res = _tolerant_ng(data, skel, lag_max, H, n_boot, rng, arm=arm, name=name)
    out = _prescale(res, name)
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r)})
    return out


def tolerant_ngA(data, skel, lag_max, H, n_boot, rng):
    return _v51_ng(data, skel, lag_max, H, n_boot, rng, arm="A", name="tolerant_ngA")


def tolerant_ngB(data, skel, lag_max, H, n_boot, rng):
    return _v51_ng(data, skel, lag_max, H, n_boot, rng, arm="B", name="tolerant_ngB")


METHODS = {"tolerant_ngA": tolerant_ngA, "tolerant_ngB": tolerant_ngB}
