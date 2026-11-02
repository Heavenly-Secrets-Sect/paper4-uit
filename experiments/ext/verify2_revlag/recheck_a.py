"""Skeptic re-check of revlag (a): independent recomputation of coverage, widths, unaffected gaps.
Reads results/ext_revlag_lag/pairs.npz only. Writes results/ext_verify2_revlag/recheck_a.md"""
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
z = np.load(ROOT/"results/ext_revlag_lag/pairs.npz"); d = {k: z[k] for k in z.files}
ms = [str(m) for m in d["methods"]]; cells = [str(c) for c in d["cells"]]
OC = {40: 1.4, 80: 1.3, 150: 1.2}; V4 = {"none": {40:1.4,80:1.3,150:1.2}, "reversed": {40:1.4,80:1.4,150:1.3}}
def sel(m): return d["method"] == ms.index(m)
key = lambda s: np.stack([d[k][s] for k in ("topo","rep","T","cell","j","i")], 1)
o, v = sel("tolerant_v4"), sel("oracle")
ko, kv = key(o), key(v)
assert (ko == kv).all(), "row order differs"
T = d["T"][o]; cell = d["cell"][o].astype(int); Ct = d["C_t"][o]; dC = d["dC"][o]; topo = d["topo"][o]
lo4, hi4 = d["lo"][o], d["hi"][o]; lor, hir = d["lo"][v], d["hi"][v]
c = np.vectorize(OC.get)(T)
mid, half = (lor+hir)/2, (hir-lor)/2
loc, hic = mid-c*half, mid+c*half
cov = lambda l, h: ((l <= Ct) & (Ct <= h)).astype(float)
c4, cr, cc = cov(lo4, hi4), cov(lor, hir), cov(loc, hic)
w4, wr, wc = hi4-lo4, hir-lor, hic-loc
rng = np.random.default_rng(7); topos = np.unique(topo)
def boot(x, s, B=2000):
    tt = topo[s]; xs = x[s]
    sn = np.array([xs[tt == t].sum() for t in topos]); sd = np.array([(tt == t).sum() for t in topos])
    idx = rng.integers(0, len(topos), (B, len(topos)))
    W = np.stack([np.bincount(r, minlength=len(topos)) for r in idx])
    reps = (W@sn)/(W@sd)
    return xs.mean(), np.quantile(reps, [.025, .975])
L = ["# Skeptic re-check of revlag (a) (independent code, own bootstrap seed 7)", "",
     "| cell | T | subset | n | cov v4 | cov oracle raw | cov oracle_cal | g(v4-ocal) [CI] | med width v4 | med width ocal | med |C_e-C_t| v4 | med |C_e-C_t| oracle |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|"]
Ce4, Cer = d["C_e"][o], d["C_e"][v]
for cn in ["none|0.0", "reversed|0.2", "reversed|0.5"]:
    ci_ = cells.index(cn)
    for t in (40, 80, 150):
        base = (cell == ci_) & (T == t)
        subsets = [("all", base)] if cn.startswith("none") else [("affected", base & (dC >= .05)), ("unaffected", base & (dC < .05))]
        for nm, s in subsets:
            g, gci = boot(c4-cc, s)
            L.append(f"| {cn} | {t} | {nm} | {s.sum()} | {c4[s].mean():.3f} | {cr[s].mean():.3f} | {cc[s].mean():.3f} | {g:+.3f} [{gci[0]:+.3f}, {gci[1]:+.3f}] | "
                     f"{np.median(w4[s]):.3f} | {np.median(wc[s]):.3f} | {np.median(np.abs(Ce4[s]-Ct[s])):.3f} | {np.median(np.abs(Cer[s]-Ct[s])):.3f} |")
(ROOT/"results/ext_verify2_revlag/recheck_a.md").write_text("\n".join(L)+"\n")
print("\n".join(L))
