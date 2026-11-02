"""Driver of round-4 candidate r4kilianbab (docs/ext/r4kilianbab.md). Uses the runner's functions
(run_unit, calibrate, summarize) unchanged; two additions, both outside the methods:

1. ``evaluate`` is wrapped (in every worker process, because this module is imported there) to add
   truth-side diagnostics to each row: signed centring error of the point estimate and of the
   interval midpoint on non-null pairs (raw and sign-adjusted: sign(C_true) * (x - C_true), negative =
   pulled toward 0), the number of misses on the zero side vs the far side, and, for ``oracle`` rows
   only, oracle_cal = oracle interval widened about its midpoint by 1.4 / 1.3 / 1.2 (plugin c_T of
   cell none at T 40 / 80 / 150, as experiments/ext/revlag/analyze_lag.py).
   Methods never see these quantities.
2. Width calibration: only the new arms (cfg["r4_tune_methods"]) are re-tuned on D-07H development;
   tolerant_v5_1's factors are read from cfg["frozen_calibration"]. The secondary part re-uses the
   main run's factors (cfg["r4_factors_from"]) and runs no calibration.

Run:  python experiments/ext/r4kilianbab/run_bab.py --config experiments/configs/ext_r4kilianbab_eval.json --workers 3
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as R  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

_EVAL = R.evaluate
OCAL = {"14": 1.4, "13": 1.3, "12": 1.2}


def evaluate_plus(sem, res, H, *, tau_effect=0.1):
    row = _EVAL(sem, res, H, tau_effect=tau_effect)
    if res.status != "ok" or res.lo is None:
        return row
    n = sem.n
    _, C_t, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(n, dtype=bool) & (np.abs(C_t) > tau_effect)
    if not nonnull.any():
        return row
    s = np.sign(C_t[nonnull])
    ct = C_t[nonnull]
    mid = ((res.lo + res.hi) / 2)[nonnull]
    est = res.C[nonnull]
    lo, hi = res.lo[nonnull], res.hi[nonnull]
    miss_lo, miss_hi = ct < lo, ct > hi
    # truth farther from zero than the whole interval = interval pulled toward zero
    toward0 = (miss_hi & (s > 0)) | (miss_lo & (s < 0))
    away = (miss_lo & (s > 0)) | (miss_hi & (s < 0))
    row.update({
        "x_med_err_C": float(np.median(est - ct)),
        "x_med_shrink_C": float(np.median(s * (est - ct))),
        "x_mean_shrink_C": float(np.mean(s * (est - ct))),
        "x_med_shrink_mid": float(np.median(s * (mid - ct))),
        "x_mean_shrink_mid": float(np.mean(s * (mid - ct))),
        "x_n_miss_toward0": int(toward0.sum()),
        "x_n_miss_away": int(away.sum()),
    })
    if res.name == "oracle":
        from paper4.metrics import interval_score
        m_all, h_all = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
        for tag, c in OCAL.items():
            l2, h2 = m_all - c * h_all, m_all + c * h_all
            inside = (l2 <= C_t) & (C_t <= h2)
            row[f"ocal{tag}_n_covered_nonnull"] = int(inside[nonnull].sum())
            row[f"ocal{tag}_iscore_nonnull_mean"] = float(interval_score(l2, h2, C_t)[nonnull].mean())
    return row


R.evaluate = evaluate_plus  # module global used by R._run_scenario; applied in every process importing this file


def job(args):
    return R.run_unit(args)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    calib = {}
    if cfg.get("r4_factors_from"):
        src = json.loads((ROOT / cfg["r4_factors_from"]).read_text(encoding="utf-8"))
        calib.update({k: v for k, v in src.items() if any(k.startswith(m + "|") for m in cfg["r4_tune_methods"])})
    else:
        ccfg = dict(cfg, calibrate_methods=list(cfg["r4_tune_methods"]))
        calib.update(R.calibrate(ccfg, a.workers))
    t_cal = time.perf_counter() - t0
    frozen = json.loads((ROOT / cfg["frozen_calibration"]).read_text(encoding="utf-8"))
    calib.update({k: v for k, v in frozen.items() if not k.startswith("_")})
    (out / "calibration.json").write_text(json.dumps(calib, indent=2), encoding="utf-8")
    need = [f"{m}|{T}|{k}" for m in cfg["calibrate_methods"] for T in cfg["T"] for k in ("none", "extra", "missing", "reversed")]
    missing = [k for k in need if k not in calib]
    if missing:
        raise SystemExit(f"missing width factors: {missing}")

    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib, "main") for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    rows, skels = [], []
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(job, jobs):
            rows.extend(res["rows"])
            skels.extend(res["skeletons"])
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(out / "skeletons.jsonl", "w", encoding="utf-8") as fh:
        for s in skels:
            fh.write(json.dumps(s) + "\n")
    (out / "summary.md").write_text(R.summarize(rows, cfg), encoding="utf-8")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - t0, 1), "seconds_calibration": round(t_cal, 1),
                "n_rows": len(rows), "workers": a.workers,
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows in {manifest['seconds']} s (calibration {t_cal:.1f} s) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
