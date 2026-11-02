"""F1 / F2 reproduction, true edge count, P1 clustered CI."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments")); sys.path.insert(0, str(ROOT / "src"))
import run_experiment as R
from paper4.topology import load_bank
from paper4.generator import build_dynamic_sem
from paper4.metrics import interval_score
cfg = json.loads((ROOT / "results/a2b_pselect/manifest.json").read_text())["config"]
topos = load_bank("D-07", "development")
unit = cfg["seed_base"] + 0
sem = build_dynamic_sem(topos[0], R.generator_config(cfg), np.random.default_rng([unit, 0]))
sk = R.unit_skeletons(sem, unit, cfg)
s = sk[("missing", 0.2)]
print("F1 damage:", s.damage, "| log:", s.log, "| lag_hint:", s.lag_hint)
# does a method receive the same object? Spy method via _EXT
seen = {}
def spy(data, skel, lag_max, H, n_boot, rng):
    seen.setdefault((skel.damage.get("kind"), skel.damage.get("rate")), list(skel.log))
    from paper4 import methods as M
    return M.plugin(data, skel, lag_max, H, 10, rng)
R._EXT = {"spy": spy}
c2 = dict(cfg, T=[40], methods=["spy"], n_boot=10)
R.run_unit((c2, topos[0], 0, 0, {}, "main"))
print("F1 log seen inside method:", {k: v for k, v in seen.items() if v})
print("true edge counts:", [len(build_dynamic_sem(t, R.generator_config(cfg), np.random.default_rng([1, 0])).edge_lag) for t in topos[:5]])
# F2
R._EXT = None
e = sorted(R.ext_methods())
print("F2 current ext sorted (idx, name, tag):", [(i, n, 100 + i) for i, n in enumerate(e) if n.startswith("tolerant_v5") or i < 3])
# P1 clustered CI of affected coverage
Rr = np.load(ROOT / "experiments/ext/redteam/out/p1.npz")["recs"]
ins = (Rr[:, 7] <= Rr[:, 6]) & (Rr[:, 6] <= Rr[:, 8])
rng = np.random.default_rng(1)
for T in (80, 150):
    for c, lab in ((5, "rev-0.2"), (6, "rev-0.5"), (3, "mis-0.2"), (4, "mis-0.5")):
        sel = (Rr[:, 2] == T) & (Rr[:, 3] == c) & (Rr[:, 4] == 1) & (Rr[:, 5] == 2)
        tt = Rr[sel, 0].astype(int); x = ins[sel]
        ids = np.unique(tt)
        num = np.array([x[tt == i].sum() for i in ids]); den = np.array([(tt == i).sum() for i in ids])
        b = [num[p].sum() / den[p].sum() for p in (rng.integers(0, len(ids), len(ids)) for _ in range(4000))]
        print(f"P1 v4 affected T={T} {lab}: {num.sum()/den.sum():.3f} [{np.quantile(b,.025):.3f},{np.quantile(b,.975):.3f}] n={den.sum()} topologies_with_affected={len(ids)}")
