"""Red team E3: published baselines widened by the same per-(T, stated kind) calibration as tolerant_v4,
plus the all-lags ablation. Uses run_experiment.py unchanged; the extra methods are injected as ext
methods through run_experiment._EXT (fork start method), so nothing is written under src/.

Run: python experiments/ext/redteam/run_calbase.py experiments/ext/redteam/calbase.json 3
"""
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))
import run_experiment as R  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.effects import cumulative, irf  # noqa: E402
from paper4.estimator import bootstrap_C, fit_equations, percentile_interval, soft_terms  # noqa: E402


def fullvar(data, skel, lag_max, H, n_boot, rng):
    """Ablation: every node's lags in every equation + the skeleton's contemporaneous parents,
    residual bootstrap. No repair, no orientation draws, no stated damage."""
    terms = [soft_terms(skel, j, lag_max) for j in range(skel.n)]
    fit = fit_equations(data, terms, lag_max)
    if fit.status != "ok":
        return M._failed("fullvar_cal", fit.status)
    draws = bootstrap_C(data, fit, H, n_boot, rng)
    if M._too_few(draws, n_boot):
        return M._failed("fullvar_cal", "bootstrap_failed")
    lo, hi = percentile_interval(draws, M.ALPHA)
    theta = irf(fit.B, H)
    return M.MethodResult("fullvar_cal", "ok", cumulative(theta, H), lo, hi, theta, fit.B)


def renamed(fn, name):
    def f(data, skel, lag_max, H, n_boot, rng):
        r = fn(data, skel, lag_max, H, n_boot, rng)
        r.name = name
        return r
    return f


EXT = {
    "bvar_cal": renamed(M.bvar_minnesota, "bvar_cal"),
    "fullvar_cal": fullvar,
    "ida_cal": renamed(M.ida_union, "ida_cal"),
    "pselect_cal": renamed(M.pselect_union, "pselect_cal"),
}

if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    R._EXT = EXT          # replaces auto-loading of src/paper4/ext_*.py for this run only
    cfg, workers = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "3"
    raise SystemExit(R.main(["--config", cfg, "--workers", workers]))
