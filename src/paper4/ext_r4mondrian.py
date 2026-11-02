"""Round 4, ID "mondrian": split-conformal (Mondrian, class-conditional) calibration of step (6) of
``tolerant_v5_1`` (docs/ext/r4mondrian.md).

Only step (6), the width factor, changes. Steps (1)-(5) are ``ext_v51.tolerant_v5_1`` itself, called
unchanged on the same random stream, so the draws, the percentile midpoint ``mid`` and the
unscaled percentile half-width ``h`` are exactly those of v5_1.

Instrumentation (``v51_with_structure``). Every bootstrap draw of v5_1 refits a structure: the
terms of the refit (own lags, adjacency lags, opened lag blocks, contemporaneous parents including
repaired and flipped edges). ``bootstrap_C`` is the only place where the refit is called, so the
draws' structures are recorded by wrapping ``bootstrap_C`` in the two module namespaces that call it
(``paper4.ext_v51`` and ``paper4.methods``) for the duration of one call. The wrapper passes an
equivalent ``refit`` (the original one, or the default ``fit_equations`` on the fit's terms) and
only appends the terms of each successful refit to a list; it makes no random-number call, so the
result is bit-identical to ``ext_v51.tolerant_v5_1`` (checked against stored rows, see the doc).
Not thread-safe (process pools only, as the runner).

Arrival time. For a structure (terms per equation), an edge i -> j of weight ``lag`` exists for every
term (i, lag) of equation j (lag 0: contemporaneous; lags count as directed forward in time). The
arrival time d_ij is the shortest-path weight from i to j (own lags are always present, so once a
shock has reached j it stays); C_ji(H) is structurally non-zero iff d_ij <= H. Arrival is capped at
H + 1 ("not reached by H").

Why arrival time and not plain reachability (refinement of the design, justified in the doc): in
estimator.py every adjacent pair admits lags in both directions, so plain reachability (lag edges
included) is the connected-component indicator of the skeleton and is the same in nearly every
draw. Arrival time keeps the intent (does the drawn structure change how i reaches j?) and is
strictly finer: a change of reachability within H is a change of arrival time.

Pair class. diff_ij = share of draws whose arrival time i -> j differs from the stated skeleton's
(the skeleton's own terms, ``estimator.parent_terms``); class R (structure-sensitive) if
diff_ij >= 0.05, class S otherwise. Also returned (descriptive): f_ij = share of draws with
d_ij <= H.

Conformal factor (Lei et al. 2018, split conformal with a locally weighted score; Vovk et al. 2005,
Mondrian taxonomy). On calibration cases, for every non-null pair, s = |C_true - mid| / h (s = +inf
when h = 0 and the pair is missed, s = 0 when h = 0 and mid = C_true). For each (T, stated kind,
class) with N scores, q = the ceil((N + 1) * 0.95)-th smallest score. A class with N < 50 is merged
with the other class of its cell (then both use the pooled q, which is M0's q). Interval:
mid +/- q * h. M0 = one class per cell (the conformal version of v5_1's grid factor), M2 = the two
classes R / S.

Registered methods (``METHODS``): ``tolerant_v5_1_m0`` and ``tolerant_v5_1_m2`` read the q table
``experiments/ext/r4mondrian/q_table.json`` (written by experiments/ext/r4mondrian/calibrate.py);
without it they return status "uncalibrated". Under run_experiment.py they run on their own stream
(ext_seed of their name), so their draws are not v5_1's; the paired study uses the driver
experiments/ext/r4mondrian/run_pairs.py, which calls ``v51_with_structure`` on v5_1's stream.

Methods see only the data, the public skeleton and its stated damage. No truth.
"""
from __future__ import annotations

import contextlib
import json
import math
from pathlib import Path

import numpy as np

from . import ext_v51
from . import methods as M
from .estimator import fit_equations, parent_terms

ALPHA = 0.05
DIFF_MIN = 0.05
N_MIN = 50
Q_TABLE = Path(__file__).resolve().parents[2] / "experiments" / "ext" / "r4mondrian" / "q_table.json"


@contextlib.contextmanager
def _record_draw_terms(log: list):
    """Wrap bootstrap_C in ext_v51 and methods so that every successful refit's terms are appended
    to ``log`` (no random-number call is added or removed)."""
    orig_e, orig_m = ext_v51.bootstrap_C, M.bootstrap_C
    assert orig_e is orig_m, "ext_v51 and methods must share estimator.bootstrap_C"

    def wrapped_bootstrap_C(data, fit, H, n_boot, rng, refit=None):
        p = fit.B.shape[0] - 1
        base = refit or (lambda x: fit_equations(x, fit.terms, p, fit.penalties))

        def rec(x):
            fb = base(x)
            if fb.status == "ok":
                log.append(fb.terms)
            return fb

        return orig_e(data, fit, H, n_boot, rng, refit=rec)

    ext_v51.bootstrap_C = wrapped_bootstrap_C
    M.bootstrap_C = wrapped_bootstrap_C
    try:
        yield
    finally:
        ext_v51.bootstrap_C = orig_e
        M.bootstrap_C = orig_m


def arrival(terms_list, n: int, H: int) -> np.ndarray:
    """Arrival time matrix(es) A[..., i, j] (source i, target j), capped at H + 1.
    ``terms_list``: a list of structures, each a list (per equation j) of (i, lag) terms."""
    S = len(terms_list)
    W = np.full((S, n, n), np.inf)
    for s, terms in enumerate(terms_list):
        for j in range(n):
            for i, lag in terms[j]:
                if i != j and lag < W[s, i, j]:
                    W[s, i, j] = lag
    idx = np.arange(n)
    W[:, idx, idx] = 0.0
    for k in range(n):
        W = np.minimum(W, W[:, :, k, None] + W[:, None, k, :])
    return np.minimum(W, H + 1).astype(np.int16)


def v51_with_structure(data, skel, lag_max, H, n_boot, rng):
    """``ext_v51.tolerant_v5_1`` (pre-scaled result, unchanged) plus per-pair structure statistics,
    all as (n, n) arrays indexed [j, i] like C (effect of i on j):
    diff (share of draws whose arrival i -> j differs from the stated skeleton's), f (share of
    draws with arrival <= H), R (diff >= DIFF_MIN), contest (1 - share of the modal arrival)."""
    log: list = []
    with _record_draw_terms(log):
        res = ext_v51.tolerant_v5_1(data, skel, lag_max, H, n_boot, rng)
    n = skel.n
    if res.status != "ok":
        return res, None
    A = arrival(log, n, H)                                        # (draws, i, j)
    A0 = arrival([[parent_terms(skel, j, lag_max) for j in range(n)]], n, H)[0]
    diff = (A != A0[None]).mean(axis=0)
    f = (A <= H).mean(axis=0)
    counts = np.stack([(A == v).sum(axis=0) for v in range(H + 2)])
    contest = 1.0 - counts.max(axis=0) / A.shape[0]
    st = {"diff": diff.T.copy(), "f": f.T.copy(), "R": (diff >= DIFF_MIN).T.copy(), "contest": contest.T.copy(),
          "n_draws": int(A.shape[0])}
    return res, st


def mid_half(res):
    """Midpoint and UNSCALED percentile half-width of a pre-scaled v5_1 result."""
    mid = (res.lo + res.hi) / 2
    h = (res.hi - res.lo) / 2 / res.info["prescale"]
    return mid, h


def scores(C_true, mid, h):
    """Normalised conformity scores |C_true - mid| / h (inf when h = 0 and missed, 0 when exact)."""
    dist = np.abs(C_true - mid)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(h > 0, dist / np.where(h > 0, h, 1.0), np.where(dist == 0, 0.0, np.inf))
    return s


def conformal_q(s, alpha: float = ALPHA) -> float:
    """ceil((N + 1)(1 - alpha))-th smallest score (inf if that rank exceeds N)."""
    s = np.sort(np.asarray(s, dtype=float))
    N = len(s)
    k = math.ceil(round((N + 1) * (1 - alpha), 9))
    return float("inf") if k > N or N == 0 else float(s[k - 1])


def build_q_table(by_cell: dict, alpha: float = ALPHA, n_min: int = N_MIN) -> dict:
    """``by_cell[(T, kind)] = (scores, classR)`` -> table with M0 ('all') and M2 ('R', 'S') factors."""
    out = {}
    for (T, kind), (s, R) in sorted(by_cell.items()):
        s, R = np.asarray(s, float), np.asarray(R, bool)
        q_all = conformal_q(s, alpha)
        nR, nS = int(R.sum()), int((~R).sum())
        merged = min(nR, nS) < n_min
        out[f"{T}|{kind}|all"] = {"q": q_all, "N": int(len(s))}
        for cls, mask, nn in (("R", R, nR), ("S", ~R, nS)):
            out[f"{T}|{kind}|{cls}"] = {"q": q_all if merged else conformal_q(s[mask], alpha), "N": nn,
                                        "merged": bool(merged)}
    return out


def apply_q(mid, h, R, T, kind, table):
    """M0 and M2 half-widths per pair. Returns (half_M0, half_M2) or None if a key is missing."""
    try:
        q0 = table[f"{T}|{kind}|all"]["q"]
        qR, qS = table[f"{T}|{kind}|R"]["q"], table[f"{T}|{kind}|S"]["q"]
    except KeyError:
        return None
    return q0 * h, np.where(R, qR, qS) * h


def _load_table():
    try:
        return {k: v for k, v in json.loads(Q_TABLE.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    except (OSError, ValueError):
        return None


def _method(arm: str):
    def fn(data, skel, lag_max, H, n_boot, rng):
        name = f"tolerant_v5_1_{arm}"
        table = _load_table()
        res, st = v51_with_structure(data, skel, lag_max, H, n_boot, rng)
        if res.status != "ok":
            return M._failed(name, res.status)
        if table is None:
            return M._failed(name, "uncalibrated")
        mid, h = mid_half(res)
        T = data.shape[0]
        halves = apply_q(mid, h, st["R"], T, M.width_key(skel.damage), table)
        if halves is None:
            return M._failed(name, "uncalibrated")
        half = halves[0] if arm == "m0" else halves[1]
        return M.MethodResult(name, "ok", res.C, mid - half, mid + half, res.theta, res.B,
                              {**res.info, "share_R": float(st["R"].mean())})
    return fn


METHODS = {"tolerant_v5_1_m0": _method("m0"), "tolerant_v5_1_m2": _method("m2")}
