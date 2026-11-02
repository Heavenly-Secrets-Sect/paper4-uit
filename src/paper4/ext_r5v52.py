"""Round 5, ID "v52": ``tolerant_v5_2`` = ``tolerant_v5_1`` + component A (NG-A v3) + component B (hubscreen v2).

Design: docs/ext/synthesis_round4.md section 4.1; rule and results: docs/ext/r5v52.md.

- Component A (``ext_r5ngorient3``, verdict RETAINED for A alone, V0 PASS): gated per-variable likelihood-ratio
  evidence of Hyvarinen and Smith (2013) replaces the two fair coins of steps (3) and (4).
- Component B (``ext_r5hubscreen2``, verdict REJECTED for B alone on P2c, V0/V1 PASS): an equation whose term
  list fails the column check is reduced by conditional SIS; no lag-0 term is ever dropped.
- Step (6) unchanged: the width factor is applied by the driver (experiments/ext/r5v52/run_v52.py):
  tolerant_v5_1's frozen factor on runs without reduction, component B's f_red otherwise.

Composition WITHOUT copied branch code. ``ext_r5ngorient3``'s branches (``_tolerant_ng``, ``_sel_dd_ng``, called
through ``v51_ng``) resolve three module-level names at call time: ``fit_equations``, ``select_open`` and
``bootstrap_C``. For the duration of one call this module rebinds them, in ``ext_r5ngorient3``'s namespace only,
to component B's reducing versions and restores them in ``finally``:

  fit_equations(x, terms, lag_max)  -> ext_r5hubscreen2.fit_reduced2(x, terms, lag_max, log, phase)
  select_open(x, skel, ...)         -> ext_r5hubscreen2.select_open_hs2(x, skel, ..., log, phase)
  bootstrap_C(data, fit, ..., refit)-> estimator.bootstrap_C with refit wrapped: phase = "draw" inside a draw,
                                       ``log.end_draw()`` after each draw; refit=None (no structure drawn) is
                                       replaced by fit_reduced2(x, base_terms) exactly as tolerant_hs2 does.

Reduction log. Every fit or screen that B's own code would also perform is logged in ``log`` (same counters and
the same ``hs_reduced`` flag as ``tolerant_v5_1_hs2``). A's plain (non-targeted) branch fits the skeleton's base
terms once more in every draw only to compute evidence (``fb`` in ``_tolerant_ng.refit``); B has no such fit.
Reductions of that evidence-only fit are logged separately (``hs_ev_*``) and do NOT set ``hs_reduced``, so the
factor switch and the identity with B are unchanged by it. If the reduced evidence-only fit still fails its check,
the draw fails (as in A), counted in ``hs_ev_fit_fail``.

Consequences (checked in docs/ext/r5v52.md):
- no reduction anywhere (``hs_reduced`` = 0 and ``hs_ev_reduced`` = 0) -> bit-identical to ``tolerant_ngA3``;
- no gate open in data and draws -> bit-identical to ``tolerant_v5_1_hs2`` (same draws, same reductions);
- both -> bit-identical to ``tolerant_v5_1``.
The driver must give this method v5_1's bootstrap stream (``ext_seed("tolerant_v5_1")``), as A and B did.

Rebinding is process-local and guarded by a lock: safe with the runner's process pool, not with concurrent threads
calling ``ext_r5ngorient3`` directly while this method runs. Methods read only the data, the public skeleton and
``skel.damage``. Existing modules are imported, never modified.
"""
from __future__ import annotations

import threading

from . import estimator as _E
from . import ext_r5ngorient3 as _A
from .ext_r5hubscreen2 import RedLog2, fit_reduced2, select_open_hs2
from .ext_v51 import TAU, allag_ratio
from .methods import stated_counts

NAME = "tolerant_v5_2"
_LOCK = threading.RLock()
_REBOUND = ("fit_equations", "select_open", "bootstrap_C")


class _Ctx:
    def __init__(self, plain: bool):
        self.log = RedLog2()          # same role as tolerant_v5_1_hs2's log
        self.log_ev = RedLog2()       # evidence-only base fits of A's plain branch (module doc)
        self.plain = plain
        self.phase = "data"
        self.base_terms = None
        self.k_in_draw = 0
        self.refit_given = False


def _bindings(ctx: _Ctx):
    def fit_equations(x, terms, lag_max, penalties=None):
        if penalties is not None:
            raise NotImplementedError("tolerant_v5_2 never fits with penalties")
        if ctx.phase == "data":
            if ctx.base_terms is None:          # first data-level fit = fit0 on the skeleton's own terms
                ctx.base_terms = [list(t) for t in terms]
            return fit_reduced2(x, terms, lag_max, ctx.log, "data")
        ctx.k_in_draw += 1
        if ctx.plain and ctx.refit_given and ctx.k_in_draw == 1:   # ``fb`` of _tolerant_ng.refit
            return fit_reduced2(x, terms, lag_max, ctx.log_ev, "draw")   # fit_fail counted by fit_reduced2
        return fit_reduced2(x, terms, lag_max, ctx.log, "draw")

    def select_open(x, skel, lag_max, k_miss, mult, alpha_open):
        return select_open_hs2(x, skel, lag_max, k_miss, mult, alpha_open, ctx.log, ctx.phase)

    def bootstrap_C(data, fit, H, n_boot, rng, refit=None):
        p = fit.B.shape[0] - 1
        ctx.refit_given = refit is not None
        inner = refit if refit is not None else (lambda x: fit_reduced2(x, ctx.base_terms, p, ctx.log, "draw"))

        def wrapped(x):
            ctx.phase, ctx.k_in_draw = "draw", 0
            try:
                return inner(x)
            finally:
                ctx.phase = "data"
                ctx.log.end_draw()

        return _E.bootstrap_C(data, fit, H, n_boot, rng, refit=wrapped)

    return {"fit_equations": fit_equations, "select_open": select_open, "bootstrap_C": bootstrap_C}


def tolerant_v5_2(data, skel, lag_max, H, n_boot, rng):
    """tolerant_v5_1 + NG-A v3 (steps 3-4) + hubscreen v2 (steps 1-2 fallback); interval pre-scaled by 0.5."""
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    targeted = k_miss > 0 and TAU is not None and allag_ratio(skel, T, lag_max) < TAU
    ctx = _Ctx(plain=not targeted)
    with _LOCK:
        saved = {k: getattr(_A, k) for k in _REBOUND}
        try:
            for k, f in _bindings(ctx).items():
                setattr(_A, k, f)
            out = _A.v51_ng(data, skel, lag_max, H, n_boot, rng, evidence=_A.ng_evidence3, name=NAME)
        finally:
            for k, f in saved.items():
                setattr(_A, k, f)
    log, lev = ctx.log, ctx.log_ev
    info = {"hs_reduced": int(log.eq > 0), "hs_eq_data": log.data_eq, "hs_eq_total": log.eq,
            "hs_trunc_eq_data": log.trunc_data, "hs_trunc_eq_total": log.trunc,
            "hs_terms_dropped": log.dropped, "hs_contemp_dropped": log.contemp_dropped + lev.contemp_dropped,
            "hs_fit_fail": log.fit_fail, "hs_screen_fail": log.screen_fail,
            "hs_draws_reduced": int(sum(log.draw_flags)), "hs_draws_total": len(log.draw_flags),
            "hs_nodes_data": sorted(log.nodes),
            "hs_ev_reduced": int(lev.eq > 0), "hs_ev_eq_total": lev.eq, "hs_ev_fit_fail": lev.fit_fail}
    if out.status == "ok":
        out.info.update(info)
    else:
        out.info = {**(out.info or {}), **info}
    return out


METHODS = {NAME: tolerant_v5_2}
