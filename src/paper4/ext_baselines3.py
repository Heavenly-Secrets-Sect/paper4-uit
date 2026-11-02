"""R3-1 (ID ``baselines3``): full-budget post-selection union baseline, and the round-1 red-team
baselines registered under their own names so that a single frozen spec can run them.

Methods see only the data and the public skeleton (pairs + orientation). ``pselect_union_v3``
does not read the stated damage at all: it builds every working skeleton with an empty damage
record and its random stream is a hash of (family, data, pairs, orientation, lag_max, H, n_boot),
without ``skel.damage`` (ext_baselines2 hashed the stated damage too).

``pselect_union_v3``  post-selection union after causal discovery (Chang, Guo and Malinsky,
    arXiv 2405.06763), adapted to the recursive SVAR, exactly as R2-1 asked
    (docs/ext/synthesis_round1.md R2-1, docs/ext/synthesis_round2.md R3-1):
    1. Adjacency selection by tests in the skeleton's **structural** all-lag equations
       (``diagnose.structural_pvalues``; the same selection as ``pselect_union_v2``): p-value ->
       two-sided z; pair selected when z > 1.96; each of ``n_perturb`` = 100 perturbed selections
       adds N(0, 1) to every z.
    2. Graphs retained: the unperturbed selection plus the most frequent distinct perturbed
       selections, at most ``cap`` = 16 graphs (ties broken by the sorted pair list).
    3. A selected pair that the skeleton does not orient (a re-selected pair, or an undetermined
       pair) gets a **contemporaneous term in both orientations**: every graph with such pairs is
       fitted in two antithetic orientation members (a random orientation of all its unoriented
       pairs and its complete flip; a direction that closes a cycle takes the other one), so each
       such pair is fitted in both directions, as ``ida_union`` does for reversible CPDAG lines.
       A graph without unoriented pairs has one member.
    4. Bootstrap budget: **every member gets ``n_boot`` (199) residual-bootstrap draws**, so every
       selected graph gets >= 199 draws (398 when it has two members). Per-member interval =
       2.5/97.5 percentile of its own draws (the construction of ``plugin`` and of the module);
       a member whose bootstrap returns fewer than max(10, n_boot // 4) draws is dropped.
    5. Reported interval = union (min lo, max hi) over the members of all retained graphs.
       Point estimate = cumulative(mean IRF over the members of the unperturbed graph).
    ``info`` records n_graphs, n_members, n_members_ok, n_draws (total bootstrap draws spent) and
    seconds (wall time of the raw computation, measured once; the _cal row of the same input reuses
    the cached result and reports the same numbers).

``pselect_union_v3_cal``  the same raw interval pre-scaled by 0.5 about its midpoint, and listed in
    ``calibrate_methods``: the runner's width grid 1.0..10 then acts as a **two-sided** factor
    0.5..5 per (T, stated kind), tuned on D-07H development. The union over 16 graphs x 2 members
    over-covers, and the widen-only grid (E2) would pin it at 1.0; the two-sided version lets the
    calibration narrow it, which is the strongest fair version of this baseline. Same draws as the
    uncalibrated method (shared cache, content seed).

``pselect_cal``, ``fullvar_cal``  the round-1 red-team baselines of results/ext_redteam_calbase
    (experiments/ext/redteam/run_calbase.py, injected there through ``run_experiment._EXT``),
    registered here under the **same names** with the **same code**, so the runner gives them the
    same stream tag (``ext_seed(name)``) and therefore the same rows on the same cell positions.
    ``pselect_cal`` = ``methods.pselect_union`` renamed; ``fullvar_cal`` = every node's lags in every
    equation + the skeleton's contemporaneous parents, residual bootstrap. Both are width-calibrated
    by the runner when listed in ``calibrate_methods``.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from statistics import NormalDist

import numpy as np

from . import methods as M
from .diagnose import structural_pvalues
from .effects import cumulative, irf
from .estimator import bootstrap_C, fit_equations, parent_terms, percentile_interval, soft_terms
from .methods import ALPHA, MethodResult, _failed
from .skeleton import Skeleton, _creates_cycle

PRESCALE = 0.5
_CACHE: "OrderedDict[tuple, MethodResult]" = OrderedDict()
_CACHE_MAX = 16


def _content_key(family: str, data, skel: Skeleton, lag_max: int, H: int, n_boot: int) -> tuple[tuple, int]:
    h = hashlib.sha256()
    h.update(family.encode())
    h.update(np.ascontiguousarray(data, dtype=float).tobytes())
    pub = {"o": sorted(map(list, skel.oriented)), "u": sorted(sorted(p) for p in skel.undetermined),
           "n": skel.n, "p": lag_max, "H": H, "B": n_boot}
    h.update(json.dumps(pub, sort_keys=True).encode())
    digest = h.digest()
    return (family, digest), int.from_bytes(digest[:8], "little")


def _orient_member(base: Skeleton, unoriented: list[tuple[int, int]], forward: np.ndarray) -> Skeleton:
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


def _pselect_v3_core(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, *, n_perturb: int = 100,
                     tau: float = 1.0, crit: float = 1.959963984540054, cap: int = 16) -> MethodResult:
    name = "pselect_union_v3"
    t0 = time.perf_counter()
    n = skel.n
    blind = Skeleton(n, set(skel.oriented), set(skel.undetermined))      # no stated damage
    try:
        pv = structural_pvalues(data, blind, lag_max)
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

    members = []
    for g_idx, g in enumerate(graphs):
        s0 = Skeleton(n)
        unoriented = []
        for u, v in sorted(g):
            if (u, v) in blind.oriented:
                s0.oriented.add((u, v))
            elif (v, u) in blind.oriented:
                s0.oriented.add((v, u))
            else:
                unoriented.append((u, v))
        if not unoriented:
            members.append((g_idx, s0))
            continue
        fwd = rng.random(len(unoriented)) < 0.5
        members.append((g_idx, _orient_member(s0, unoriented, fwd)))
        members.append((g_idx, _orient_member(s0, unoriented, ~fwd)))

    los, his, base_thetas, base_B = [], [], [], None
    n_ok, n_draws = 0, 0
    min_ok = max(10, n_boot // 4)
    for g_idx, s in members:
        terms = [parent_terms(s, j, lag_max) for j in range(n)]
        fit = fit_equations(data, terms, lag_max)
        if fit.status != "ok":
            continue
        draws = bootstrap_C(data, fit, H, n_boot, rng)
        if len(draws) < min_ok:
            continue
        lo, hi = percentile_interval(draws, ALPHA)
        los.append(lo)
        his.append(hi)
        n_ok += 1
        n_draws += len(draws)
        if g_idx == 0:
            base_thetas.append(irf(fit.B, H))
            if base_B is None:
                base_B = fit.B
    if not base_thetas:
        return _failed(name, "underdetermined" if n_ok == 0 else "base_failed")
    theta = np.mean(base_thetas, axis=0)
    n_unor = sum(1 for u, v in base if (u, v) not in blind.oriented and (v, u) not in blind.oriented)
    return MethodResult(name, "ok", cumulative(theta, H), np.min(los, axis=0), np.max(his, axis=0), theta, base_B,
                        {"n_graphs": len(graphs), "n_members": len(members), "n_members_ok": n_ok,
                         "n_draws": n_draws, "n_selected": len(base), "n_unoriented": n_unor,
                         "seconds": round(time.perf_counter() - t0, 3)})


def _raw_v3(data, skel, lag_max, H, n_boot) -> MethodResult:
    key, seed = _content_key("pselect_v3", data, skel, lag_max, H, n_boot)
    res = _CACHE.get(key)
    if res is None:
        res = _pselect_v3_core(data, skel, lag_max, H, n_boot, np.random.default_rng(seed))
        _CACHE[key] = res
        while len(_CACHE) > _CACHE_MAX:
            _CACHE.popitem(last=False)
    else:
        _CACHE.move_to_end(key)
    return res


def pselect_union_v3(data, skel, lag_max, H, n_boot, rng):
    res = _raw_v3(data, skel, lag_max, H, n_boot)
    return MethodResult("pselect_union_v3", res.status, res.C, res.lo, res.hi, res.theta, res.B, dict(res.info))


def pselect_union_v3_cal(data, skel, lag_max, H, n_boot, rng):
    res = _raw_v3(data, skel, lag_max, H, n_boot)
    if res.status != "ok":
        return _failed("pselect_union_v3_cal", res.status)
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return MethodResult("pselect_union_v3_cal", "ok", res.C, mid - PRESCALE * half, mid + PRESCALE * half,
                        res.theta, res.B, {**res.info, "prescale": PRESCALE})


# --------------------------------------------------------------------------- round-1 red-team baselines
# Verbatim copies of experiments/ext/redteam/run_calbase.py (fullvar, renamed), so that the frozen spec
# does not need the _EXT injection of that script.

def fullvar_cal(data, skel, lag_max, H, n_boot, rng):
    """Ablation: every node's lags in every equation + the skeleton's contemporaneous parents,
    residual bootstrap. No repair, no orientation draws, no stated damage."""
    t0 = time.perf_counter()
    terms = [soft_terms(skel, j, lag_max) for j in range(skel.n)]
    fit = fit_equations(data, terms, lag_max)
    if fit.status != "ok":
        return M._failed("fullvar_cal", fit.status)
    draws = bootstrap_C(data, fit, H, n_boot, rng)
    if M._too_few(draws, n_boot):
        return M._failed("fullvar_cal", "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    return M.MethodResult("fullvar_cal", "ok", cumulative(theta, H), lo, hi, theta, fit.B,
                          {"n_draws": len(draws), "seconds": round(time.perf_counter() - t0, 3)})


def pselect_cal(data, skel, lag_max, H, n_boot, rng):
    t0 = time.perf_counter()
    r = M.pselect_union(data, skel, lag_max, H, n_boot, rng)
    r.name = "pselect_cal"
    r.info = {**r.info, "seconds": round(time.perf_counter() - t0, 3)}
    return r


METHODS = {
    "pselect_union_v3": pselect_union_v3,
    "pselect_union_v3_cal": pselect_union_v3_cal,
    "pselect_cal": pselect_cal,
    "fullvar_cal": fullvar_cal,
}
