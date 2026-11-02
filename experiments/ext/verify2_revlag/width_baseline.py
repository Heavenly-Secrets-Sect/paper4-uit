"""Context for F2: AUROC of the simplest competitor 1/width (narrow interval -> miss) on the fresh run,
with topology-cluster bootstrap CI of AUROC(p_hat) - AUROC(1/width). Writes results/ext_verify2_revlag/width_baseline.md"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from flaglib import score
fr = json.load(open(ROOT / "experiments/ext/revlag/frozen_flag.json"))
z = np.load(ROOT / "results/ext_revlag_fresh/pairs.npz"); d = {k: z[k] for k in z.files}
s = d["method"] == list(map(str, d["methods"])).index("tolerant_v4")
r = {k: d[k][s] for k in ("lo", "hi", "C_e", "C_t", "T", "stated", "topo")}
y = ~((r["lo"] <= r["C_t"]) & (r["C_t"] <= r["hi"])); ph = score(r, fr); iw = -(r["hi"] - r["lo"])
def auroc(sc, yy, w):
    # weighted Mann-Whitney via sorting
    o = np.argsort(sc, kind="mergesort"); sc, yy, w = sc[o], yy[o], w[o]
    u, inv = np.unique(sc, return_inverse=True)
    P = np.bincount(inv, w * yy, len(u)); N = np.bincount(inv, w * (~yy), len(u))
    below = np.cumsum(N) - N
    return (P * (below + .5 * N)).sum() / (P.sum() * N.sum())
rng = np.random.default_rng(11); L = ["# Context for F2: 1/width as competitor (fresh D-07 dev, tolerant_v4)", "",
      "| set | AUROC p_hat | AUROC 1/width | delta [95% cluster CI, 500 resamples] |", "|---|---|---|---|"]
for lab, sel in (("T80/150", r["T"] >= 80), ("T40", r["T"] == 40)):
    yy, pp, ww, tt = y[sel], ph[sel], iw[sel], r["topo"][sel].astype(int)
    a1, a2 = auroc(pp, yy, np.ones(len(yy))), auroc(ww, yy, np.ones(len(yy)))
    topos = np.unique(tt); pos = np.searchsorted(topos, tt); reps = []
    for _ in range(500):
        cnt = np.bincount(rng.integers(0, len(topos), len(topos)), minlength=len(topos)).astype(float)
        w = cnt[pos]; reps.append(auroc(pp, yy, w) - auroc(ww, yy, w))
    lo, hi = np.quantile(reps, [.025, .975])
    L.append(f"| {lab} | {a1:.3f} | {a2:.3f} | {a1-a2:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
(ROOT / "results/ext_verify2_revlag/width_baseline.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
