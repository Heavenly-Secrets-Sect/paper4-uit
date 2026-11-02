"""Does the interpreter (python3=/usr/bin numpy 2.0.2 vs miniconda numpy 2.5.4) change module output? D-07H only."""
import json, sys, hashlib
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import methods as M, ext_v4c as X
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
cfg = json.loads((ROOT / "experiments/configs/ext_v4c_eval.json").read_text())
gen = R.generator_config(cfg)
topo = load_bank("D-07H", "development")[1]
unit = 8_900_001
sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
skels = R.unit_skeletons(sem, unit, cfg)
data = sem.simulate(80, np.random.default_rng([unit, 2, 80]))
res = {}
for (kind, rate), full in skels.items():
    if rate not in (0.0, 0.5): continue
    skel = R.public(full)
    for name, f in (("v3", M.tolerant_v3), ("ida_c2", X.ida_union_c2), ("bvar_c2", X.bvar_minnesota_c2)):
        r = f(data, skel, gen.lag_max, cfg["H"], cfg["n_boot"], np.random.default_rng([unit, 9]))
        res[f"{name}|{kind}"] = (r.lo.round(12).tolist(), r.hi.round(12).tolist()) if r.status == "ok" else r.status
print(sys.executable, np.__version__)
print(json.dumps({k: (v if isinstance(v, str) else [round(float(np.sum(v[0])), 10), round(float(np.sum(v[1])), 10)]) for k, v in res.items()}))
