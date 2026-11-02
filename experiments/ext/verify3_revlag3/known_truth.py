"""Verifier known-truth checks of ext_revlag3.orientation_evidence and tolerant_v4R (synthetic, no bank)."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.skeleton import Skeleton
from paper4 import ext_revlag3 as X, methods as M
out = {}
def sim(T, seed, vstruct=True):
    r = np.random.default_rng(seed); n = 3; x = np.zeros((T + 50, n))
    for t in range(1, T + 50):
        a = 0.5 * x[t-1, 0] + r.normal(); c = 0.5 * x[t-1, 2] + r.normal()
        b = 0.3 * x[t-1, 1] + (0.8 * a if vstruct else 0) + 0.8 * c + r.normal()
        x[t] = (a, b, c)
    return x[50:]
# case 1: v-structure a->b<-c; stated skeleton has a->b reversed (b->a), k_rev=1
res = {}
for T in (80, 150, 400):
    dls = []
    for s in range(30):
        d = sim(T, s)
        sk = Skeleton(3, {(1, 0), (2, 1)}, damage={"kind": "reversed", "rate": 0.5, "k": 1})
        pool = [(1, 0), (2, 1)]
        dl = X.orientation_evidence(d, sk, pool, 2, False)
        dls.append(dl)
    dls = np.array(dls)
    res[T] = dict(mean_dl_true_reversed=float(dls[:, 0].mean()), share_pos_true_reversed=float((dls[:, 0] > 0).mean()),
                  mean_dl_correct_edge=float(dls[:, 1].mean()), share_correct_neg=float((dls[:, 1] < 0).mean()))
out["vstructure_dl"] = res
# case 2: Markov-equivalent pair (2-node, chain): dl must be ~0
d = sim(150, 1, vstruct=True)[:, :2]
sk = Skeleton(2, {(1, 0)}, damage={"kind": "reversed", "rate": 0.5, "k": 1})
out["two_node_equivalent_dl"] = float(X.orientation_evidence(d, sk, [(1, 0)], 2, False)[0])
# case 3: tolerant_v4R vs tolerant_v3 coverage of the true C(H) for b<-a effect in the v-structure, T=150
from paper4.effects import cumulative, irf
covR, cov3, errR, err3 = [], [], [], []
for s in range(20):
    d = sim(150, 100 + s)
    sk = Skeleton(3, {(1, 0), (2, 1)}, damage={"kind": "reversed", "rate": 0.5, "k": 1})
    rR = X.tolerant_v4R(d, sk, 2, 4, 99, np.random.default_rng(s))
    r3 = M.tolerant_v3(d, sk, 2, 4, 99, np.random.default_rng(s))
    # true cumulative effect a->b over H=4: contemporaneous 0.8 * sum_{h} 0.3^h-ish; compute from true B
    B = np.zeros((3, 3, 3)); B[0, 1, 0] = 0.8; B[0, 1, 2] = 0.8; B[1, 0, 0] = 0.5; B[1, 2, 2] = 0.5; B[1, 1, 1] = 0.3
    Ct = cumulative(irf(B, 4), 4)
    j, i = 1, 0
    for r, cv, er in ((rR, covR, errR), (r3, cov3, err3)):
        if r.status == "ok":
            cv.append(bool(r.lo[j, i] <= Ct[j, i] <= r.hi[j, i])); er.append(abs(r.C[j, i] - Ct[j, i]))
out["v4R_vs_v3_true_a_to_b"] = dict(C_true=float(Ct[1, 0]), n=len(errR), med_err_v4R=float(np.median(errR)), med_err_v3=float(np.median(err3)),
                                    cov_v4R_prescaled=float(np.mean(covR)), cov_v3=float(np.mean(cov3)))
print(json.dumps(out, indent=1))
json.dump(out, open(ROOT / "results/ext_verify3_revlag3/known_truth.json", "w"), indent=1)
