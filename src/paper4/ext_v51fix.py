"""Direction "v51fix" (round 3): tau sensitivity of tolerant_v5_1 (docs/ext/v51fix.md, section 1.C).

``tolerant_v5_1_t294`` is ``ext_v51.tolerant_v5_1`` line for line, with the switch threshold set to
TAU_SENS = 2.9370 (midpoint of the mean ratios at T = 80 and T = 100 of probe_tau2 on D-07H
development; the value the tau procedure gives for the 11% of probe bootstrap seeds in which the CI
of d(100) crosses 0, results/ext_verify2_v51/tau_fragility.json). With it, T = 150 (r about 4.9) takes
the all-lag branch, T = 40 and 80 stay targeted. Descriptive sensitivity only, D-07 development.

This module registers ONLY ``tolerant_v5_1_t294``. It must never register ``tolerant_v5_1`` (or any
built-in name): the runner imports every ext_* module in name order and a later module would
silently overwrite an earlier registration (bug E4, docs/ext/synthesis_round2.md section 6).

Methods see only the data, the skeleton and its stated damage.
"""
from __future__ import annotations

from .ext_narrow import _prescale
from .ext_v51 import allag_ratio, tolerant_sel_dd
from .methods import stated_counts, tolerant

TAU_SENS = 2.9370
NAME = "tolerant_v5_1_t294"


def tolerant_v5_1_t294(data, skel, lag_max, H, n_boot, rng):
    T = data.shape[0]
    k_miss = stated_counts(skel.damage)["missing"]
    r = allag_ratio(skel, T, lag_max)
    targeted = k_miss > 0 and r < TAU_SENS
    if targeted:
        res = tolerant_sel_dd(data, skel, lag_max, H, n_boot, rng, reselect=True, name=NAME)
    else:
        res = tolerant(data, skel, lag_max, H, n_boot, rng, target_reversal=True, name=NAME)
    out = _prescale(res, NAME)
    out.info.update({"v51_targeted": int(targeted), "v51_ratio": float(r)})
    return out


METHODS = {NAME: tolerant_v5_1_t294}
