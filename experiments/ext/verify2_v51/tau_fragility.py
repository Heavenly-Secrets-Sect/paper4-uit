"""Skeptic check (verify2_v51): is the tau procedure's outcome fragile at T = 100?
probe_tau2 gave d(100) CI upper = -0.004 (2000 topology resamples, seed 0). If it were >= 0, T* = 80
and tau = (r(80) + r(100)) / 2 ~ 2.94, which would send T = 150 to the all-lag branch.
Re-runs probe_tau2.unit for T = 100 only (D-07H development, same seeds -> must reproduce d(100)),
then recomputes the CI under 200 bootstrap seeds. Writes results/ext_verify2_v51/tau_fragility.json
"""
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/v51"))
sys.path.insert(0, str(ROOT / "src"))
import probe_tau2 as P  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

if __name__ == "__main__":
    topos = load_bank("D-07H", "development")[:20]
    jobs = [(i, rp, t, [100], 199) for i, t in enumerate(topos) for rp in range(3)]
    rows = []
    with ProcessPoolExecutor(2) as pool:
        for o in pool.map(P.unit, jobs):
            rows.extend(o)
    rep = P.analyse(rows, [100])[100]
    # rebuild per-topology diffs exactly as analyse() does
    IS = {}
    for v in ("targeted", "all"):
        rs = [r for r in rows if r["v"] == v and r["status"] == "ok"]
        c = rep["c_star"][v]
        for r in rs:
            dd, hh = np.array(r["dist"]), np.array(r["half"])
            IS[(r["topo"], r["rep"], r["rate"], v)] = float(np.mean(2 * c * hh + 40 * np.maximum(dd - c * hh, 0)))
    diffs = defaultdict(list)
    for (t, rp, rate, v), s in IS.items():
        if v == "targeted":
            diffs[t].append(s - IS[(t, rp, rate, "all")])
    topos_ = list(diffs)
    his = []
    for seed in range(200):
        rng = np.random.default_rng(seed)
        boots = [np.mean([x for i in rng.choice(len(topos_), len(topos_)) for x in diffs[topos_[i]]]) for _ in range(2000)]
        his.append(float(np.quantile(boots, 0.975)))
    his = np.array(his)
    out = {"reproduced": {"d": rep["d"], "lo": rep["lo"], "hi": rep["hi"], "c_star": rep["c_star"]},
           "probe_tau2_reported": json.load(open(ROOT / "results/ext_v51_probe/probe_tau2.json"))["report"]["100"]["hi"],
           "hi_over_200_seeds": {"min": float(his.min()), "max": float(his.max()), "median": float(np.median(his)),
                                 "share_hi_ge_0": float((his >= 0).mean())},
           "c_star_sensitivity_note": "c* chosen on the same runs; not re-sampled here"}
    (ROOT / "results/ext_verify2_v51").mkdir(parents=True, exist_ok=True)
    (ROOT / "results/ext_verify2_v51/tau_fragility.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
