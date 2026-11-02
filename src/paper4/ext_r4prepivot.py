"""Round 4, candidate "prepivot": per-dataset width calibration of ``tolerant_v5_1`` by a reduced
double bootstrap (Beran 1987 prepivoting; Loh 1987 calibration of the confidence coefficient;
Martin 1990 iterated bootstrap). No bank factor. Design and pre-registered rule: docs/ext/r4prepivot.md.

Idea. v5.1's percentile interval is widened by a factor tuned on a calibration bank per (T, stated
kind) (step [6]). Here the factor is estimated from the dataset itself: the bootstrap world, where
the truth is the fitted model, is used to measure how far v5.1's own bootstrap distribution misses
that truth, and the interval is widened accordingly.

Procedure for one dataset (data, stated skeleton with its stated damage):

1. Run v5.1 unchanged (``ext_v51.tolerant_v5_1``) with B = n_boot outer draws. The outer draws are
   bit-identical to v5.1's (the recorder below re-implements ``estimator.bootstrap_C`` line for line
   and only keeps the bootstrap series). The generating fit of the outer draws is ``fit``; the
   outer world's truth is C0 = cumulative(irf(fit.B, H)).
2. Keep the first B_O = 39 successful outer series x_b. For each, run the WHOLE v5.1 procedure with
   x_b as the data (re-select the opened pairs, re-repair, re-build the reversal pool, its own
   generating fit and its own per-draw re-selection) with B_I = 19 inner draws: C**_{b,1..19}.
   (Refinement of the proposed design, which used the outer draw's fit fb as generator: running the
   procedure on x_b is the textbook double bootstrap, and in the reversed branch v5.1's generator is
   the unflipped fit, not a flipped fb.)
3. Root per (b, ordered pair): r = |C0 - mean_c C**| / sd_c(C**) (ddof 1), pairs with sd > 0 only
   (sd > 1e-12 (1 + |mean|), so pairs constant up to rounding are skipped).
   Primary root set ("nn"): off-diagonal pairs with |C0| > TAU_NN = 0.1, i.e. the bootstrap
   world's analogue of the evaluated non-null set (|C_true| > tau_effect = 0.1; the bootstrap world's
   truth is known, so the filter uses only data). Secondary ("all", the originally proposed design):
   every ordered pair, diagonals included.
4. c_d = 0.95 quantile of the pooled roots; f_d = c_d / z_ref. The reference z_ref is the value
   c_d takes when v5.1's bootstrap is exactly calibrated: the inner mean and sd come from only
   B_I = 19 draws, so under normality the root is |t_{B_I-1}| * sqrt(1 + 1/B_I) and its 0.95
   quantile is z_ref = t_{0.975, 18} * sqrt(20/19) = 2.1555, not 1.96 (the outer interval uses
   199 draws, where the normal reference 1.96 applies). Without this, f_d is biased upward by
   about 10% whatever the data (refinement of the proposed design, fixed before any D-07 run).
   Secondary variant "orig" = the design exactly as proposed: root set "all", f = c_d / 1.96.
5. Interval: v5.1's UNSCALED outer percentile interval (no PRESCALE, no bank factor) widened about
   its midpoint by f_d. Point estimate, theta, B: those of v5.1.

If fewer than MIN_INNER = 20 of the 39 inner worlds give >= 10 inner draws, the method fails
("prepivot_failed"). Inner random numbers come from a seed drawn from the method's rng after the
outer bootstrap, so the outer draws are untouched.

Methods see only the data, the public skeleton and its stated damage. Existing modules are imported,
never modified; ``bootstrap_C`` is swapped in the namespaces of ``methods`` and ``ext_v51`` only for
the duration of a call (restored in ``finally``).
"""
from __future__ import annotations

import contextlib
import time

import numpy as np

from . import ext_v51, methods
from .effects import cumulative, irf
from .estimator import fit_equations, percentile_interval, simulate_from_fit
from .methods import ALPHA, MethodResult, _failed

B_O = 39          # outer worlds kept for the inner level
B_I = 19          # inner draws per outer world
TAU_NN = 0.1      # |C0| threshold of the primary root set (bootstrap-world analogue of tau_effect)
Q = 0.95          # target coverage
Z = 1.959963984540054
MIN_INNER = 20    # usable inner worlds required


def t_quantile(p: float, df: int) -> float:
    """Student-t quantile by bisection on the CDF (Simpson integration of the density); numpy only."""
    import math
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)

    def cdf(x):
        g = np.linspace(0.0, x, 4001)
        f = c * (1 + g * g / df) ** (-(df + 1) / 2)
        h = g[1] - g[0]
        return 0.5 + h / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())

    lo, hi = 0.0, 50.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


def z_ref(b_i: int) -> float:
    """0.95 quantile of the root when the bootstrap is exactly calibrated (module doc, step 4)."""
    return t_quantile(1 - ALPHA / 2, b_i - 1) * float(np.sqrt(1 + 1 / b_i))


class _Recorder:
    """Replacement for ``estimator.bootstrap_C`` that also records the generating fit, the draws and
    the first ``keep`` successful bootstrap series. Same random-number calls as the original."""

    def __init__(self, keep: int):
        self.keep = keep
        self.calls = []

    def __call__(self, data, fit, H, n_boot, rng, refit=None):
        p = fit.B.shape[0] - 1
        refit = refit or (lambda x: fit_equations(x, fit.terms, p, fit.penalties))
        out, xs = [], []
        tries = 0
        while len(out) < n_boot and tries < 3 * n_boot:
            tries += 1
            x = simulate_from_fit(fit, data, rng)
            fb = refit(x)
            if fb.status == "ok":
                out.append(cumulative(irf(fb.B, H), H))
                if len(xs) < self.keep:
                    xs.append(x)
        draws = np.array(out)
        self.calls.append({"fit": fit, "draws": draws, "xs": xs})
        return draws

    @contextlib.contextmanager
    def patched(self):
        old = (methods.bootstrap_C, ext_v51.bootstrap_C)
        methods.bootstrap_C = self
        ext_v51.bootstrap_C = self
        try:
            yield self
        finally:
            methods.bootstrap_C, ext_v51.bootstrap_C = old


def v51_recorded(data, skel, lag_max, H, n_boot, rng, keep: int):
    """``tolerant_v5_1`` (pre-scaled, as returned by the module) plus its recorded bootstrap call."""
    rec = _Recorder(keep)
    with rec.patched():
        res = ext_v51.tolerant_v5_1(data, skel, lag_max, H, n_boot, rng)
    return res, (rec.calls[-1] if rec.calls else None)


def roots_for(C0: np.ndarray, inner: np.ndarray, tau_nn: float = TAU_NN):
    """Roots of one outer world: (primary 'nn' roots, secondary 'all' roots)."""
    mean = inner.mean(axis=0)
    sd = inner.std(axis=0, ddof=1)
    ok = sd > 1e-12 * (1 + np.abs(mean))  # 'sd = 0' up to rounding (a constant pair gives sd ~ 1e-18)
    r = np.zeros_like(sd)
    r[ok] = np.abs(C0[ok] - mean[ok]) / sd[ok]
    n = C0.shape[0]
    off = ~np.eye(n, dtype=bool)
    nn = ok & off & (np.abs(C0) > tau_nn)
    return r[nn], r[ok]


def c_from_roots(roots: np.ndarray) -> float | None:
    return float(np.quantile(roots, Q)) if roots.size else None


def widen(lo, hi, f):
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    return mid - f * half, mid + f * half


def prepivot_core(data, skel, lag_max, H, n_boot, rng, *, b_o: int = B_O, b_i: int = B_I):
    """Everything the evaluation needs from one dataset: v5.1's result as the module returns it
    (pre-scaled), its unscaled outer interval, and the per-dataset factors (primary and secondary)."""
    t0 = time.perf_counter()
    res, call = v51_recorded(data, skel, lag_max, H, n_boot, rng, keep=b_o)
    out = {"v51": res, "seconds_outer": None, "seconds_inner": None}
    out["seconds_outer"] = time.perf_counter() - t0
    if res.status != "ok" or call is None:
        out["status"] = res.status
        return out
    lo0, hi0 = percentile_interval(call["draws"], ALPHA)
    C0 = cumulative(irf(call["fit"].B, H), H)
    inner_seed = int(rng.integers(0, 2**62))
    t1 = time.perf_counter()
    nn_roots, all_roots, n_ok = [], [], 0
    for b, xb in enumerate(call["xs"]):
        irng = np.random.default_rng([inner_seed, b])
        rb, cb = v51_recorded(xb, skel, lag_max, H, b_i, irng, keep=0)
        if rb.status != "ok" or cb is None or len(cb["draws"]) < 2:
            continue
        n_ok += 1
        a, c = roots_for(C0, cb["draws"])
        nn_roots.append(a)
        all_roots.append(c)
    out["seconds_inner"] = time.perf_counter() - t1
    nn = np.concatenate(nn_roots) if nn_roots else np.array([])
    al = np.concatenate(all_roots) if all_roots else np.array([])
    out.update({"status": "ok" if n_ok >= MIN_INNER else "prepivot_failed", "lo0": lo0, "hi0": hi0,
                "n_inner_ok": n_ok, "n_outer_kept": len(call["xs"]), "n_roots_nn": int(nn.size),
                "n_roots_all": int(al.size), "c_nn": c_from_roots(nn), "c_all": c_from_roots(al),
                "z_ref": z_ref(b_i),
                "n_C0_nn": int((~np.eye(C0.shape[0], dtype=bool) & (np.abs(C0) > TAU_NN)).sum())})
    return out


def factors(core: dict) -> dict:
    """Primary f (root set nn, reference z_ref(B_I)) and secondary f_orig (root set all, 1.96)."""
    f = core["c_nn"] / core["z_ref"] if core.get("c_nn") is not None else None
    fo = core["c_all"] / Z if core.get("c_all") is not None else None
    return {"pp": f, "orig": fo}


def result_from_core(core: dict, name: str, which: str = "pp") -> MethodResult:
    if core["status"] != "ok":
        return _failed(name, core["status"])
    fs = factors(core)
    f = fs[which]
    if f is None:
        return _failed(name, "prepivot_failed")
    v = core["v51"]
    lo, hi = widen(core["lo0"], core["hi0"], f)
    info = {k: val for k, val in v.info.items() if k != "prescale"}
    info.update({"f_d": f, "f_pp": fs["pp"], "f_orig": fs["orig"], "c_nn": core["c_nn"], "c_all": core["c_all"],
                 "n_inner_ok": core["n_inner_ok"], "n_roots_nn": core["n_roots_nn"],
                 "n_roots_all": core["n_roots_all"], "n_C0_nn": core["n_C0_nn"], "sec_outer": core["seconds_outer"],
                 "sec_inner": core["seconds_inner"]})
    return MethodResult(name, "ok", v.C, lo, hi, v.theta, v.B, info)


def tolerant_v5_1_pp(data, skel, lag_max, H, n_boot, rng):
    """v5.1 with the per-dataset double-bootstrap width factor (primary)."""
    return result_from_core(prepivot_core(data, skel, lag_max, H, n_boot, rng), "tolerant_v5_1_pp", "pp")


def tolerant_v5_1_pp_orig(data, skel, lag_max, H, n_boot, rng):
    """Secondary: the design exactly as proposed (every ordered pair, reference 1.96)."""
    return result_from_core(prepivot_core(data, skel, lag_max, H, n_boot, rng), "tolerant_v5_1_pp_orig", "orig")


METHODS = {"tolerant_v5_1_pp": tolerant_v5_1_pp, "tolerant_v5_1_pp_orig": tolerant_v5_1_pp_orig}
