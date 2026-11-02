import json, sys
from pathlib import Path
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import methods as M
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
cfg = json.loads((ROOT / "experiments/configs/ext_baselines3_eval.json").read_text())
gen = R.generator_config(cfg); ext = R.ext_methods()
topo = load_bank("D-07H", "development")[0]
unit = cfg["seed_base"] + 500000
sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
sk = R.public(R.unit_skeletons(sem, unit, cfg)[("missing", 0.2)])
data = sem.simulate(80, np.random.default_rng([unit, 2, 80]))
out = {"python": sys.executable, "numpy": np.__version__}
r = M.tolerant_v3(data, sk, 2, 4, 199, np.random.default_rng([unit, 3, 80, 3, 6])); out["v3"] = [r.lo.tolist(), r.hi.tolist()]
r = ext["pselect_union_v3"](data, sk, 2, 4, 199, None); out["psv3"] = [r.lo.tolist(), r.hi.tolist()]
r = ext["tolerant_v5_1"](data, sk, 2, 4, 199, np.random.default_rng([unit, 3, 80, 3, 7])); out["v51"] = [r.lo.tolist(), r.hi.tolist()]
print(json.dumps(out))
