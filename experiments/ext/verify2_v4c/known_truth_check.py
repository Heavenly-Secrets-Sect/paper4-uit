"""Skeptic check of ext_v4c on D-07H development (calibration bank only; D-07 / P4-H* untouched).
1. Composition: runner's calibrate_width(v4c, c) == calibrate_width(v3, c*prescale) with the same rng.
2. Point estimate C is untouched by the wrapper.
3. ida_union_c2 pre-scale branch on stated missing.
4. Known truth: coverage of v3*1.3 vs v4c*2.6 on 5 units, T=150 (same rng => identical).
5. The runner gives v4c a different bootstrap stream than built-in v4 (rng(6)).
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import ext_v4c as X, methods as M
from paper4.generator import build_dynamic_sem
from paper4.metrics import truth_effects
from paper4.topology import load_bank

cfg = json.loads((ROOT / "experiments/configs/ext_v4c_eval.json").read_text())
gen = R.generator_config(cfg)
topos = load_bank("D-07H", "development")
out = {"maxdev_compose": 0.0, "maxdev_C": 0.0, "ida_prescale": {}, "coverage": {}, "ext_seed": {}}
cov_hits = {"v4_c1.3": [0, 0], "v4c_c2.6": [0, 0]}
for t_idx in range(5):
    unit = 8_800_000 + t_idx
    sem = build_dynamic_sem(topos[t_idx], gen, np.random.default_rng([unit, 0]))
    skels = R.unit_skeletons(sem, unit, cfg)
    T = 150
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    _, Ctrue, _, _ = truth_effects(sem, cfg["H"])
    for (kind, rate), full in skels.items():
        if rate not in (0.0, 0.5): continue
        skel = R.public(full)
        r = X.tolerant_v4c(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
        b = M.tolerant_v3(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
        if r.status != "ok" or b.status != "ok": continue
        a = M.calibrate_width(r, 2.6, "tolerant_v4c"); v = M.calibrate_width(b, 1.3, "tolerant_v4")
        out["maxdev_compose"] = max(out["maxdev_compose"], float(max(np.abs(a.lo - v.lo).max(), np.abs(a.hi - v.hi).max())))
        out["maxdev_C"] = max(out["maxdev_C"], float(np.abs(r.C - b.C).max()))
        n = sem.n
        mask = ~np.eye(n, dtype=bool) & (np.abs(Ctrue) > 1e-12)
        for key, res in (("v4_c1.3", v), ("v4c_c2.6", a)):
            hit = (res.lo <= Ctrue) & (Ctrue <= res.hi)
            cov_hits[key][0] += int(hit[mask].sum()); cov_hits[key][1] += int(mask.sum())
        if t_idx == 0:
            ri = X.ida_union_c2(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
            out["ida_prescale"][f"{kind}|{rate}"] = ri.info.get("prescale") if ri.status == "ok" else ri.status
out["coverage"] = {k: round(h / max(t, 1), 4) for k, (h, t) in cov_hits.items()}
out["coverage_npairs"] = {k: t for k, (h, t) in cov_hits.items()}
out["ext_seed"] = {n: R.ext_seed(n) for n in X.METHODS}
print(json.dumps(out, indent=1))
(ROOT / "results/ext_verify2_v4c/known_truth_check.json").write_text(json.dumps(out, indent=1))
