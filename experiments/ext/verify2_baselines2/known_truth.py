"""Skeptic known-truth check of ext_baselines2 (no bank data): 5-node SVAR, skeleton with two edges deleted
(0->1 contemporaneous, 3->4 at lag 2), T in {80, 150}, 40 seeds. Coverage of C(H) on non-null pairs
(deleted pairs separately) and on null pairs, for pselect_union_v2 and bvar_minnesota_v2 (raw intervals),
plus plugin on the damaged skeleton as a reference. Writes results/ext_verify2_baselines2/known_truth.json."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4 import ext_baselines2 as E
from paper4 import methods as M
from paper4.effects import cumulative, irf
from paper4.skeleton import Skeleton
n, p, H = 5, 2, 4
B = np.zeros((p + 1, n, n))
B[0, 1, 0] = 0.6; B[1, 2, 1] = 0.5; B[0, 3, 2] = 0.5; B[2, 4, 3] = 0.45; B[1, 4, 0] = 0.4
for j in range(n): B[1, j, j] = 0.4
Ct = cumulative(irf(B, H), H)
def sim(T, seed):
    r = np.random.default_rng(seed); A = np.linalg.inv(np.eye(n) - B[0]); x = np.zeros((T + 200, n))
    e = r.normal(size=(T + 200, n)) * np.sqrt([1.0, 0.8, 1.2, 0.6, 1.0])
    for t in range(2, T + 200): x[t] = A @ (B[1] @ x[t - 1] + B[2] @ x[t - 2] + e[t])
    return x[200:]
deleted = [(1, 0), (4, 3)]   # (effect j, cause i)
nonnull = [(j, i) for j in range(n) for i in range(n) if i != j and abs(Ct[j, i]) > 1e-9]
null = [(j, i) for j in range(n) for i in range(n) if i != j and abs(Ct[j, i]) <= 1e-9]
out = {"nonnull": nonnull, "null": null, "C_true": Ct.tolist()}
for T in (80, 150):
    acc = {m: {"del": [], "nn": [], "null": [], "w_nn": []} for m in ("pselect_union_v2", "bvar_minnesota_v2", "plugin")}
    for seed in range(40):
        x = sim(T, 1000 + seed)
        sk = Skeleton(n, oriented={(1, 2), (2, 3), (0, 4)}, damage={"kind": "missing", "rate": 0.4, "k": 2})
        rs = {"pselect_union_v2": E._pselect_core(x, sk, p, H, 199, np.random.default_rng(seed)),
              "bvar_minnesota_v2": E._bvar_core(x, sk, p, H, 199, np.random.default_rng(seed)),
              "plugin": M.plugin(x, sk, p, H, 199, np.random.default_rng(seed))}
        for m, r in rs.items():
            if r.status != "ok": continue
            cov = (r.lo <= Ct) & (Ct <= r.hi)
            acc[m]["del"] += [bool(cov[j, i]) for j, i in deleted]
            acc[m]["nn"] += [bool(cov[j, i]) for j, i in nonnull]
            acc[m]["null"] += [bool(cov[j, i]) for j, i in null]
            acc[m]["w_nn"] += [float(r.hi[j, i] - r.lo[j, i]) for j, i in nonnull]
    out[T] = {m: {"cov_deleted": float(np.mean(a["del"])), "cov_nonnull": float(np.mean(a["nn"])),
                  "cov_null": float(np.mean(a["null"])), "width_nonnull": float(np.mean(a["w_nn"])), "n_ok_pairs": len(a["nn"])}
              for m, a in acc.items()}
    print(T, json.dumps(out[T], indent=0))
d = ROOT / "results/ext_verify2_baselines2"; d.mkdir(parents=True, exist_ok=True)
(d / "known_truth.json").write_text(json.dumps(out, indent=1))
