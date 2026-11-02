"""Per-method timing on one D-07H development unit (design probe, not evaluation)."""
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import methods as M, ext_baselines2 as E
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
cfg = json.load(open(ROOT / "experiments/configs/ext_baselines2_probe.json"))
cfg["damage"] = {"kinds": ["missing"], "rates": [0.5]}
topo = load_bank("D-07H", "development")[5]
unit = 20261102 + 900000
sem = build_dynamic_sem(topo, R.generator_config(cfg), np.random.default_rng([unit, 0]))
sk = R.public(R.unit_skeletons(sem, unit, cfg)[("missing", 0.5)])
out = {}
for T in (40, 80, 150):
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    for name, fn in [("tolerant_v3", M.tolerant_v3), ("pselect_union", M.pselect_union),
                     ("pselect_union_v2", E._pselect_core), ("bvar_minnesota", M.bvar_minnesota),
                     ("bvar_minnesota_v2", E._bvar_core)]:
        t0 = time.perf_counter(); fn(data, sk, 2, 4, 199, np.random.default_rng(1)); out[f"{T}|{name}"] = round(time.perf_counter() - t0, 2)
print(out)
(ROOT / 'results/ext_baselines2_probe/timing.json').write_text(json.dumps(out, indent=1))
