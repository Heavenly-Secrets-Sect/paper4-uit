"""Verifier (auto5, round 2): small known-truth checks of src/paper4/ext_auto5.py. No bank data.
Writes results/ext_verify2_auto5/known_truth.json"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.generator import DynamicSEM, GeneratorConfig
from paper4.skeleton import Skeleton
from paper4.metrics import truth_effects, interval_score
from paper4.ext_narrow import opened_terms
from paper4 import ext_auto5 as A
from paper4.estimator import fit_equations

out = {}
# 1) de-duplication of terms
s = Skeleton(4, {(0, 1), (1, 2)}, set())
op = [(1, 2)]
raw = opened_terms(s, op, 2, 2); dd = A.targeted_terms(s, op, 2, 2)
out["dedup"] = {"opened_terms_len": len(raw), "unique": len(set(raw)), "targeted_terms_len": len(dd)}

# 2) known-truth SVAR, n=5, lag_max=2
n, p = 5, 2
B = np.zeros((p + 1, n, n))
B[0, 1, 0] = 0.5        # 0 -> 1 contemporaneous
B[1, 2, 1] = 0.6        # 1 -> 2 lag 1
B[2, 3, 2] = -0.5       # 2 -> 3 lag 2
B[1, 4, 0] = 0.4        # 0 -> 4 lag 1
for j in range(n): B[1, j, j] = 0.3
sem = DynamicSEM("toy", tuple(f"x{i}" for i in range(n)), B, np.ones(n),
                 {(0, 1): 0, (1, 2): 1, (2, 3): 2, (0, 4): 1}, GeneratorConfig(lag_max=2))
H = 4
_, C_true, _, _ = truth_effects(sem, H)
nonnull = ~np.eye(n, dtype=bool) & (np.abs(C_true) > 0.1)
full = Skeleton(n, {(0, 1), (1, 2), (2, 3), (0, 4)}, set())
miss = Skeleton(n, {(0, 1), (2, 3), (0, 4)}, set(), damage={"missing": 99})  # stated damage garbage: must be ignored
res_tab = {}
for label, sk in (("correct", full), ("missing_1_2", miss)):
    for T in (80, 300, 2000):
        covs, iss, br, c12 = [], [], [], []
        reps = 30 if T < 2000 else 5
        for r in range(reps):
            data = sem.simulate(T, np.random.default_rng([7, T, r]))
            res = A.tolerant_auto5(data, sk, p, H, 99, np.random.default_rng([8, T, r]))
            if res.status != "ok":
                br.append("fail"); continue
            ins = (res.lo <= C_true) & (C_true <= res.hi)
            covs.append(ins[nonnull].mean()); iss.append(interval_score(res.lo, res.hi, C_true)[nonnull].mean())
            br.append(res.info["branch"]); c12.append(res.C[2, 1])
        res_tab[f"{label}|T{T}"] = {"cov": float(np.mean(covs)), "IS": float(np.mean(iss)),
                                    "branches": {b: br.count(b) for b in set(br)},
                                    "C_2from1_mean_truth_1.187": float(np.mean(c12)), "reps": reps}
out["toy"] = res_tab
# orientation of C: check which index is effect of 1 on 2
out["C_true"] = np.round(C_true, 3).tolist()
# 3) damage ignored: same rng, different damage dict -> identical output
data = sem.simulate(150, np.random.default_rng(1))
r1 = A.tolerant_auto5(data, miss, p, H, 49, np.random.default_rng(3))
m2 = Skeleton(n, set(miss.oriented), set(), damage={})
r2 = A.tolerant_auto5(data, m2, p, H, 49, np.random.default_rng(3))
out["damage_ignored"] = bool(np.allclose(r1.lo, r2.lo) and np.allclose(r1.hi, r2.hi))
(ROOT / "results/ext_verify2_auto5/known_truth.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
