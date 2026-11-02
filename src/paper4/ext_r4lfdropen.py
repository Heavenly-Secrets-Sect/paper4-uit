"""Round 4, candidate "lfdropen": probabilistic targeted lag opening by a two-groups local fdr.

Only step (2) of ``tolerant_v5_1`` changes, and only in its targeted branch (stated missing edges,
r < TAU). Every other branch calls exactly the code ``ext_v51.tolerant_v5_1`` calls, on the same
random stream (see "Random stream" below), so it reproduces v5_1 bit for bit.

Step (2) in v5_1 (``ext_narrow.select_open``): open the lag blocks of the K off-skeleton pairs with
the smallest combined Sidak p of ``ext_narrow.screen_pairs``, K = max(3k, #{p < 0.10}).

Step (2) here (``select_open_lfdr``):

1. p_i = the combined Sidak p of each of the m off-skeleton pairs (``screen_pairs``, unchanged),
   clipped to [1e-12, 1 - 1e-12]; z_i = Phi^-1(1 - p_i).
2. Two-groups model (Efron, Tibshirani, Storey and Tusher 2001, JASA 96:1151; Scott and Berger 2010,
   Ann. Statist. 38:2587): f(z) = pi0 f0(z) + (1 - pi0) f1(z), theoretical null f0 = N(0, 1),
   f1 = N(mu, s^2). pi0 is FIXED by the stated missing count, pi0 = 1 - min(k, m - 1) / m (not
   estimated); mu, s are fitted by EM with pi0 fixed (start mu = 2.5, s = 1; s floored at 0.5; at
   most 200 iterations, stop when max(|d mu|, |d s|) < 1e-6).
3. P_i = 1 - lfdr_i = (1 - pi0) f1(z_i) / f(z_i), the posterior probability that pair i is non-null.
4. Opened set = the top min(k, m) pairs by p (a floor of k pairs, replacing v5_1's 3k; Kilian 2001,
   J. Forecasting 20:161: under-fitting tightens IRF intervals, so the floor stays), plus every other
   pair i with probability P_i:
     - on the data fit: deterministically, P_i >= 0.5;
     - in each bootstrap draw: an independent Bernoulli(P_i) draw, with P recomputed from that draw's
       screen (the selection is re-run in every draw, as in v5_1).
   Terms are de-duplicated as in ``ext_v51.tolerant_sel_dd``.

The rest (fit, contemporaneous repair by BH with a random direction per draw, reversal draws among
significant contemporaneous edges, residual bootstrap re-running (1)-(4) in every draw, percentile
interval, PRESCALE 0.5 for the runner's two-sided width calibration) is ``tolerant_sel_dd`` line for
line.

**Random stream.** The runner gives every extension method ``default_rng([unit, 3, T, c_idx, tag])``
with ``tag = 1000 + crc32(name) % 1e6``. When the generator carries exactly that seed structure with
this method's own tag, the method re-seeds its main stream with v5_1's tag (common random numbers:
same residual resampling, direction and flip draws as v5_1 as long as the structures agree) and uses
the generator it was given only for the Bernoulli opening draws. The seed holds no truth (unit index,
T, cell position). With any other generator the main stream is the given one and the Bernoulli
stream is spawned from its seed sequence (no draws consumed).

Methods see only the data, the public skeleton and its stated damage.
"""
from __future__ import annotations

import math
import zlib
from statistics import NormalDist

import numpy as np

from .effects import irf
from .estimator import bootstrap_C, fit_equations, percentile_interval
from .ext_narrow import _prescale, opened_terms, screen_pairs
from .ext_v51 import TAU, allag_ratio
from .methods import (ALPHA, MethodResult, _failed, _flip_from, _too_few, contemporaneous_pool,
                      repair_candidates, stated_counts, tolerant)
from .skeleton import Skeleton, _creates_cycle

NAME = "tolerant_v5_1_lfdr"
REF_NAME = "tolerant_v5_1"
P_CLIP = 1e-12
MU0, S0, S_FLOOR = 2.5, 1.0, 0.5
EM_ITER, EM_TOL = 200, 1e-6
_ND = NormalDist()
_SQ2PI = math.sqrt(2 * math.pi)


def _stream_tag(name: str) -> int:
    """The runner's ``ext_seed`` (experiments/run_experiment.py), reproduced here."""
    return 1000 + zlib.crc32(name.encode()) % 1_000_000


def split_streams(rng, own: str = NAME, ref: str = REF_NAME):
    """(main stream, Bernoulli stream); see module doc "Random stream"."""
    ss = getattr(rng.bit_generator, "seed_seq", None)
    ent = getattr(ss, "entropy", None)
    if isinstance(ent, (list, tuple)) and len(ent) == 5 and int(ent[-1]) == _stream_tag(own) \
            and not getattr(ss, "spawn_key", ()):
        main = np.random.default_rng([int(x) for x in ent[:-1]] + [_stream_tag(ref)])
        return main, rng, True
    child = ss.spawn(1)[0] if ss is not None else np.random.SeedSequence()
    return rng, np.random.default_rng(child), False


def _phi(z):
    return np.exp(-0.5 * z * z) / _SQ2PI


def lfdr_posterior(pvals, k_miss: int):
    """P_i = 1 - lfdr_i under the two-groups model with pi0 fixed by k (module doc).
    Returns (P, info) with info = {pi0, mu, s, iters}."""
    p = np.clip(np.asarray(pvals, dtype=float), P_CLIP, 1 - P_CLIP)
    m = len(p)
    if m == 0:
        return np.zeros(0), {"pi0": None, "mu": None, "s": None, "iters": 0}
    pi0 = 1.0 - min(k_miss, m - 1) / m
    z = np.array([_ND.inv_cdf(1.0 - x) for x in p])
    mu, s = MU0, S0

    def post(mu_, s_):
        a = (1 - pi0) * _phi((z - mu_) / s_) / s_
        b = pi0 * _phi(z)
        tot = a + b
        with np.errstate(invalid="ignore", divide="ignore"):
            w = np.where(tot > 0, a / np.where(tot > 0, tot, 1.0), 0.0)
        return w

    it = 0
    if pi0 < 1.0:
        for it in range(1, EM_ITER + 1):
            w = post(mu, s)
            sw = float(w.sum())
            if sw <= 1e-300:
                break
            mu_new = float(w @ z / sw)
            s_new = max(math.sqrt(float(w @ (z - mu_new) ** 2) / sw), S_FLOOR)
            change = max(abs(mu_new - mu), abs(s_new - s))
            mu, s = mu_new, s_new
            if change < EM_TOL:
                break
        P = post(mu, s)
    else:
        P = np.zeros(m)
    # P = 1 - pi0 * phi(z) / (pi0 * phi(z) + (1 - pi0) * phi((z - mu) / s) / s), as in the design
    return P, {"pi0": pi0, "mu": mu, "s": s, "iters": it}


def select_open_lfdr(data, skel: Skeleton, lag_max: int, k_miss: int, bern_rng=None):
    """Step (2) of this candidate (module doc). ``bern_rng`` None = data fit (P >= 0.5);
    otherwise one Bernoulli(P_i) draw per non-forced pair. Returns (opened, tests, P, em_info)."""
    tests = screen_pairs(data, skel, lag_max)  # (p, u, v), smallest p first
    P, em = lfdr_posterior([t[0] for t in tests], k_miss)
    k0 = min(int(math.ceil(k_miss)), len(tests))
    rest = np.arange(k0, len(tests))
    if bern_rng is None:
        take = P[rest] >= 0.5
    else:
        take = bern_rng.random(len(rest)) < P[rest]
    opened = [(u, v) for _, u, v in tests[:k0]] + [(tests[i][1], tests[i][2]) for i in rest[take]]
    return opened, tests, P, em


def _pkey(u, v):
    a, b = (u, v) if u < v else (v, u)
    return f"{a}-{b}"


def tolerant_sel_lfdr(data, skel: Skeleton, lag_max: int, H: int, n_boot: int, rng, bern_rng, *,
                      name: str = NAME) -> MethodResult:
    """``ext_v51.tolerant_sel_dd`` (reselect=True) with step (2) replaced by ``select_open_lfdr``."""
    n = skel.n
    stated = stated_counts(skel.damage)
    k_miss, k_rev = stated["missing"], stated["reversed"]
    if k_miss == 0:
        return tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=name)
    try:
        opened, tests0, P0, em0 = select_open_lfdr(data, skel, lag_max, k_miss, None)
    except ValueError:
        return _failed(name, "underdetermined")
    n_dup = [0]

    def terms_for(s: Skeleton, op):
        out = []
        for j in range(n):
            raw = opened_terms(s, op, j, lag_max)
            dd = list(dict.fromkeys(raw))
            n_dup[0] += len(raw) - len(dd)
            out.append(dd)
        return out

    fit0 = fit_equations(data, terms_for(skel, opened), lag_max)
    if fit0.status != "ok":
        return _failed(name, fit0.status)
    cands = repair_candidates(fit0.residuals, skel, k_miss)
    reversing = k_rev > 0
    pool = contemporaneous_pool(data, fit0, k_rev) if reversing else None

    def draw_skel(cs) -> Skeleton:
        s = _flip_from(skel, pool, k_rev, rng) if reversing else skel.copy()
        for u, v in cs:
            e = (u, v) if rng.random() < 0.5 else (v, u)
            if _creates_cycle(s.oriented | {e}, n):
                e = (v, u) if e == (u, v) else (u, v)
            if not _creates_cycle(s.oriented | {e}, n):
                s.oriented.add(e)
        return s

    fit = fit_equations(data, terms_for(draw_skel(cands), opened), lag_max) if cands else fit0
    if fit.status != "ok":
        return _failed(name, fit.status)
    n_dup_data = n_dup[0]
    n_open, freq, em_mu, n_fallback = [], {}, [], [0]

    def refit(x):
        try:
            op, _, _, em = select_open_lfdr(x, skel, lag_max, k_miss, bern_rng)
            if em["mu"] is not None:
                em_mu.append(em["mu"])
        except ValueError:  # selection impossible on this draw: keep the data's selection (as v5_1)
            op = opened
            n_fallback[0] += 1
        n_open.append(len(op))
        for u, v in op:
            kk = _pkey(u, v)
            freq[kk] = freq.get(kk, 0) + 1
        f0 = fit_equations(x, terms_for(skel, op), lag_max)
        if f0.status != "ok":
            return f0
        cs = repair_candidates(f0.residuals, skel, k_miss)
        if not cs and not reversing:
            return f0
        return fit_equations(x, terms_for(draw_skel(cs), op), lag_max)

    draws = bootstrap_C(data, fit, H, n_boot, rng, refit=refit)
    if _too_few(draws, n_boot):
        return _failed(name, "bootstrap_failed")
    lo, hi = percentile_interval(draws, ALPHA)
    theta = irf(fit.B, H)
    n_calls = max(len(n_open), 1)
    k0 = min(k_miss, len(tests0))
    return MethodResult(name, "ok", draws.mean(axis=0), lo, hi, theta, fit.B,
                        {"n_repair": len(cands), "n_open": len(opened),
                         "n_open_boot_mean": float(np.mean(n_open)) if n_open else None,
                         "n_reversal_pool": None if pool is None else len(pool),
                         "n_dup_terms_data": n_dup_data, "n_dup_terms_total": n_dup[0],
                         "lfdr_m": len(tests0), "lfdr_k_floor": k0, "lfdr_pi0": em0["pi0"],
                         "lfdr_mu": em0["mu"], "lfdr_s": em0["s"], "lfdr_iters": em0["iters"],
                         "lfdr_mu_boot_mean": float(np.mean(em_mu)) if em_mu else None,
                         "lfdr_n_sel_fallback": n_fallback[0],
                         "lfdr_open_data": [_pkey(u, v) for u, v in opened],
                         "lfdr_P_data": {_pkey(u, v): round(float(P0[i]), 5) for i, (_, u, v) in enumerate(tests0)},
                         "lfdr_p_data": {_pkey(u, v): float(p) for p, u, v in tests0},
                         "lfdr_open_freq": {kk: round(c / n_calls, 5) for kk, c in freq.items()}})


def tolerant_v5_1_lfdr(data, skel, lag_max, H, n_boot, rng):
    """``ext_v51.tolerant_v5_1`` with step (2) of the targeted branch replaced (module doc)."""
    main, bern, crn = split_streams(rng)
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and TAU is not None and r < TAU
    if targeted:
        res = tolerant_sel_lfdr(data, skel, lag_max, H, n_boot, main, bern, name=NAME)
    else:
        res = tolerant(data, skel, lag_max, H, n_boot, main, target_reversal=True, name=NAME)
    out = _prescale(res, NAME)
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r), "lfdr_crn": int(crn)})
    return out


METHODS = {NAME: tolerant_v5_1_lfdr}
