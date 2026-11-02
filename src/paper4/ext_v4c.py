"""R2-4 (direction "v4c"): two-sided width calibration for the module and for the published baselines.

Problem (docs/ext/synthesis_round1.md, B6 / X5 / redteam E3). The runner's width-factor grid
``C_GRID`` starts at 1.0, so calibration can only widen an interval. Where a method over-covers on
the calibration bank its factor sits at the floor 1.0:
- ``tolerant_v4`` at T = 40 on stated missing edges (coverage 0.98);
- ``pselect_cal``, ``ida_cal`` (and ``fullvar_cal``) on several undamaged / extra cells in E3, which
  biases the descriptive comparisons outside the missing cells towards the module.

Fix, without touching the runner: every method here returns its interval pre-scaled about its
midpoint by ``PRESCALE`` = 0.5 (as ``ext_narrow`` does). Listed in ``calibrate_methods``, the runner's
grid 1.0..10 (step 0.1) then maps to effective factors 0.5..5 (step 0.05), tuned per (T, stated
damage kind) on the calibration bank exactly as for ``tolerant_v4``.

Methods (each is the named method unchanged, then pre-scaled):
- ``tolerant_v4c``      = ``tolerant_v3`` (the code of the frozen module v4 before its width factor);
- ``pselect_union_c2``  = ``pselect_union``;
- ``bvar_minnesota_c2`` = ``bvar_minnesota``;
- ``ida_union_c2``      = ``ida_union``; the one exception to PRESCALE = 0.5: when the stated damage
  kind is ``missing`` the pre-scale is 1.0 (effective grid 1.0..10). On the calibration bank E3 tuned
  ``ida_cal|T|missing`` to 7.7 / 8.9 / 8.6, above the 5.0 ceiling that a 0.5 pre-scale would impose.
  On those cells the floor never binds, so ``ida_union_c2`` equals E3's ``ida_cal`` there.

Methods see only the data, the public skeleton and its stated damage. The bootstrap stream is the
runner's name-fixed ``ext_seed`` stream, so ``tolerant_v4c`` does not share bootstrap draws with the
built-in ``tolerant_v4`` (and the ``*_c2`` baselines not with the built-in baselines).
"""
from __future__ import annotations

from . import methods as M
from .methods import MethodResult, _failed, width_key

PRESCALE = 0.5


def _prescale(res: MethodResult, name: str, p: float) -> MethodResult:
    if res.status != "ok":
        return _failed(name, res.status)
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return MethodResult(name, "ok", res.C, mid - p * half, mid + p * half, res.theta, res.B,
                        {**res.info, "prescale": p})


def tolerant_v4c(data, skel, lag_max, H, n_boot, rng):
    """Module v3 (= frozen v4 before widening), pre-scaled for two-sided calibration."""
    return _prescale(M.tolerant_v3(data, skel, lag_max, H, n_boot, rng), "tolerant_v4c", PRESCALE)


def pselect_union_c2(data, skel, lag_max, H, n_boot, rng):
    return _prescale(M.pselect_union(data, skel, lag_max, H, n_boot, rng), "pselect_union_c2", PRESCALE)


def bvar_minnesota_c2(data, skel, lag_max, H, n_boot, rng):
    return _prescale(M.bvar_minnesota(data, skel, lag_max, H, n_boot, rng), "bvar_minnesota_c2", PRESCALE)


def ida_union_c2(data, skel, lag_max, H, n_boot, rng):
    p = 1.0 if width_key(skel.damage) == "missing" else PRESCALE
    return _prescale(M.ida_union(data, skel, lag_max, H, n_boot, rng), "ida_union_c2", p)


METHODS = {
    "tolerant_v4c": tolerant_v4c,
    "pselect_union_c2": pselect_union_c2,
    "bvar_minnesota_c2": bvar_minnesota_c2,
    "ida_union_c2": ida_union_c2,
}
