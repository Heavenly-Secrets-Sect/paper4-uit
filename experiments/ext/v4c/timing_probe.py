"""Timing + sanity probe for ext_v4c on D-07H development ONLY (calibration bank; D-07 untouched).

One topology x 1 replicate, every T and every a2 damage cell, own seed (7_900_000). Prints the
wall time of each method and checks that each *_c2 / v4c interval is the underlying method's
interval shrunk by its pre-scale about the same midpoint (same rng seed). No coverage is printed.
Run: python experiments/ext/v4c/timing_probe.py > experiments/ext/v4c/timing_probe.out
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R  # noqa: E402
from paper4 import ext_v4c as X  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

cfg = json.loads((ROOT / "experiments/configs/a2_baselines.json").read_text())
gen = R.generator_config(cfg)
topo = load_bank("D-07H", "development")[0]
unit = 7_900_000
sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
skels = R.unit_skeletons(sem, unit, cfg)
pairs = [("tolerant_v4c", M.tolerant_v3), ("pselect_union_c2", M.pselect_union),
         ("bvar_minnesota_c2", M.bvar_minnesota), ("ida_union_c2", M.ida_union)]
tot = {n: 0.0 for n, _ in pairs}
maxdev = {n: 0.0 for n, _ in pairs}
for T in cfg["T"]:
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    for (kind, rate), full in skels.items():
        skel = R.public(full)
        for name, base in pairs:
            t0 = time.perf_counter()
            r = X.METHODS[name](data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
            tot[name] += time.perf_counter() - t0
            b = base(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
            if r.status == "ok" and b.status == "ok":
                p = r.info["prescale"]
                dev = max(np.max(np.abs((r.lo + r.hi) - (b.lo + b.hi))),
                          np.max(np.abs((r.hi - r.lo) - p * (b.hi - b.lo))))
                maxdev[name] = max(maxdev[name], float(dev))
                if name == "ida_union_c2":
                    assert p == (1.0 if kind == "missing" else 0.5)
                else:
                    assert p == 0.5
print("seconds per unit (3 T x 7 cells, 1 process):", {k: round(v, 1) for k, v in tot.items()})
print("max |deviation| from underlying interval x prescale:", maxdev)
