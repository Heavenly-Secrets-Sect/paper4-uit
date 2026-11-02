"""Driver for round 4 "levboot": experiments/run_experiment.py, unchanged, plus two logging hooks
installed in every worker process (no file of the runner or of src/paper4 is modified):

1. ``evaluate`` is wrapped so that every ok row whose method returns a pre-scaled interval
   (info ``prescale``) also gets the coverage and interval score of the **raw percentile interval**,
   i.e. with the pre-scale and the runner's width factor removed: half_raw = half / (prescale * c_T)
   (c_T = 1 when the row is uncalibrated). Fields: raw_n_covered_nonnull, raw_iscore_nonnull_mean,
   raw_width_kept, raw_factor_removed.
2. ``tolerant_v5_1`` (the reference) is wrapped in ``ext_r4levboot.bootstrap_hooks`` with the
   profile-only simulator ("ORIG", which calls the frozen ``estimator.simulate_from_fit``), so its rows
   carry the same bootstrap tries / successes and leverage profile as the arms. Its intervals are
   unchanged (checked by pairing with results/ext_v51_eval).

Run: python experiments/ext/r4levboot/run.py --config experiments/configs/ext_r4levboot_<x>.json --workers 3
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402

_INSTALLED = False


def _install():
    global _INSTALLED
    if _INSTALLED:
        return
    from paper4 import ext_r4levboot as L
    from paper4.metrics import truth_effects

    orig_eval = R.evaluate

    def evaluate_plus(sem, res, H, *, tau_effect=0.1):
        row = orig_eval(sem, res, H, tau_effect=tau_effect)
        if res.status == "ok" and res.lo is not None and "prescale" in res.info:
            f = float(res.info["prescale"]) * float(res.info.get("c_T", 1.0))
            mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2 / f
            lo, hi = mid - half, mid + half
            _, C_t, _, _ = truth_effects(sem, H)
            n = sem.n
            nonnull = ~np.eye(n, dtype=bool) & (np.abs(C_t) > tau_effect)
            kept = nonnull & ~(res.C == 0.0)
            inside = (lo <= C_t) & (C_t <= hi)
            from paper4.metrics import interval_score
            sc = interval_score(lo, hi, C_t)
            row.update({"raw_n_covered_nonnull": int(inside[nonnull].sum()),
                        "raw_iscore_nonnull_mean": float(sc[nonnull].mean()) if nonnull.any() else None,
                        "raw_width_kept": float(np.median((hi - lo)[kept])) if kept.any() else None,
                        "raw_factor_removed": f})
        return row

    R.evaluate = evaluate_plus
    ext = R.ext_methods()
    ref = ext[L.REF_NAME]

    def ref_logged(data, skel, lag_max, H, n_boot, rng):
        stats: dict = {}
        with L.bootstrap_hooks(L.make_simulator("ORIG", stats), stats):
            res = ref(data, skel, lag_max, H, n_boot, rng)
        res.info = {**res.info, **stats, "lev_mode": "ORIG"}
        return res

    ext[L.REF_NAME] = ref_logged
    _INSTALLED = True


def run_unit_logged(args):
    _install()
    return _ORIG_RUN_UNIT(args)


_ORIG_RUN_UNIT = R.run_unit

if __name__ == "__main__":
    R.run_unit = run_unit_logged   # R.main and R.calibrate look the name up at call time
    raise SystemExit(R.main(sys.argv[1:]))
