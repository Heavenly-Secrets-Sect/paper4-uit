"""Skeptic: TLP on a hand-built 4-node SVAR(2) with known truth."""
import sys; sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/src")
import numpy as np
from paper4 import ext_tlp as X
from paper4.effects import irf
from paper4.skeleton import Skeleton
from paper4.methods import plugin
n, H, L = 4, 4, 2
B = np.zeros((3, n, n))
B[0][1, 0] = 0.6; B[0][2, 1] = 0.5; B[0][3, 2] = -0.4       # 0->1->2->3 contemporaneous
B[1][np.arange(n), np.arange(n)] = [0.4, 0.3, 0.5, 0.2]
B[1][3, 0] = 0.4; B[2][2, 0] = 0.3
truth = irf(B, H).sum(0)
A0 = np.linalg.inv(np.eye(n) - B[0])
def sim(T, rng):
    x = np.zeros((T + 200, n))
    for t in range(2, T + 200):
        x[t] = A0 @ (B[1] @ x[t-1] + B[2] @ x[t-2] + rng.normal(size=n))
    return x[200:]
full = Skeleton(n, {(0, 1), (1, 2), (2, 3), (0, 3), (0, 2)})
miss = Skeleton(n, {(0, 1), (1, 2), (2, 3)}, damage={"kind": "missing", "rate": 0.4, "k": 2})   # drop 0-3, 0-2
mask = ~np.eye(n, dtype=bool) & (np.abs(truth) > 0.1)
for name, sk in [("true", full), ("missing", miss)]:
    for T in (150, 1000):
        cov, wid, err, errp, vs = [], [], [], [], []
        for r in range(40):
            x = sim(T, np.random.default_rng([7, T, r]))
            res = X.targeted_lp(x, sk, L, H, 199, np.random.default_rng([8, T, r]))
            pl = plugin(x, sk, L, H, 0, np.random.default_rng(0))
            cov.append(((res.lo <= truth) & (truth <= res.hi))[mask].mean()); wid.append(np.median((res.hi - res.lo)[mask]))
            err.append(np.abs(res.C - truth)[mask].mean()); errp.append(np.abs(pl.C - truth)[mask].mean()); vs.append(res.info["v_mean"])
        print(f"{name:8s} T={T:5d} cov={np.mean(cov):.3f} width={np.mean(wid):.3f} |C-truth| TLP={np.mean(err):.3f} plugin={np.mean(errp):.3f} v={np.mean(vs):.3f}")
# direct check: LP equals truth IRF at large T with true skeleton
x = sim(200000, np.random.default_rng(1))
lp = X.lp_responses(x, [sorted(u for u, v in full.oriented if v == i) for i in range(n)], 3, H)
print("max |LP - IRF| T=2e5:", np.abs(lp - irf(B, H)).max())
