"""Skeptic re-check of revlag (b) L1 point estimates, validity identity, and (c) flag point numbers,
with independent code (numpy + scipy rankdata). Writes results/ext_verify2_revlag/recheck_bc.md"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
ROOT = Path(__file__).resolve().parents[3]
L = ["# Skeptic re-check of revlag (b) and (c)", ""]
def load(run):
    z = np.load(ROOT / f"results/{run}/pairs.npz"); return {k: z[k] for k in z.files}
# validity: oracle & v4 rows vs round 1
a, b = load("ext_metrics_pairs"), load("ext_revlag_lag")
for m in ("oracle", "tolerant_v4"):
    sa = a["method"] == list(map(str, a["methods"])).index(m); sb = b["method"] == list(map(str, b["methods"])).index(m)
    ka = np.stack([a[k][sa] for k in ("topo", "rep", "T", "cell", "j", "i")], 1); kb = np.stack([b[k][sb] for k in ("topo", "rep", "T", "cell", "j", "i")], 1)
    oa, ob = np.lexsort(ka.T[::-1]), np.lexsort(kb.T[::-1])
    same = ka.shape == kb.shape and (ka[oa] == kb[ob]).all()
    diff = sum(int((~np.isclose(a[c][sa][oa], b[c][sb][ob], rtol=0, atol=0, equal_nan=True)).sum()) for c in ("C_e", "lo", "hi", "C_t")) if same else -1
    L.append(f"- validity {m}: rows r1 {sa.sum()} r2 {sb.sum()}, same keys {same}, differing values {diff}")
# L1 point estimates
d = b; ms = list(map(str, d["methods"])); cells = list(map(str, d["cells"]))
def rows(m): 
    s = d["method"] == ms.index(m); o = np.lexsort(np.stack([d[k][s] for k in ("topo","rep","T","cell","j","i")])[::-1]); return {k: d[k][s][o] for k in d if d[k].ndim == 1 and len(d[k]) == len(d["topo"])}
v4, vL = rows("tolerant_v4"), rows("tolerant_v4L")
assert (v4["j"] == vL["j"]).all() and (v4["topo"] == vL["topo"]).all()
L += ["", "| cell | T | n kept damaged | hit v4 | hit v4L | delta |", "|---|---|---|---|---|---|"]
for cn in ("reversed|0.2", "reversed|0.5"):
    for T in (40, 80, 150):
        s = (v4["cell"] == cells.index(cn)) & (v4["T"] == T) & (v4["role"] == 2) & (v4["C_e"] != 0) & (vL["C_e"] != 0)
        h4 = (v4["pk_e"][s] == v4["pk_t"][s]).mean(); hL = (vL["pk_e"][s] == vL["pk_t"][s]).mean()
        L.append(f"| {cn} | {T} | {s.sum()} | {h4:.3f} | {hL:.3f} | {hL-h4:+.3f} |")
# n topologies contributing damaged pairs in reversed-0.2 T80
s = (v4["cell"] == cells.index("reversed|0.2")) & (v4["T"] == 80) & (v4["role"] == 2)
L.append(f"\nreversed|0.2 T80 damaged pairs come from {len(np.unique(v4['topo'][s]))} of 20 topologies; "
         f"pairs where v4L hits and v4 misses: {int(((vL['pk_e']==vL['pk_t'])&(v4['pk_e']!=v4['pk_t'])&s).sum())}, reverse: {int(((vL['pk_e']!=vL['pk_t'])&(v4['pk_e']==v4['pk_t'])&s).sum())}")
# (c) flag
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from flaglib import score
fr = json.load(open(ROOT / "experiments/ext/revlag/frozen_flag.json"))
f = load("ext_revlag_fresh"); s = f["method"] == list(map(str, f["methods"])).index("tolerant_v4")
r = {k: f[k][s] for k in ("lo", "hi", "C_e", "C_t", "T", "stated", "topo", "cell")}
y = ~((r["lo"] <= r["C_t"]) & (r["C_t"] <= r["hi"])); ph = score(r, fr)
def auroc(sc, yy):
    rk = rankdata(sc); n1 = yy.sum(); n0 = len(yy) - n1; return (rk[yy].sum() - n1*(n1+1)/2) / (n1*n0)
L += ["", "| set | n | miss | AUROC p_hat | AUROC rel_width | flagged | miss flagged | miss unflagged | ratio |", "|---|---|---|---|---|---|---|---|---|"]
relw = (r["hi"] - r["lo"]) / (np.abs(r["C_e"]) + 1e-9)
for lab, sel in (("T80/150", r["T"] >= 80), ("T40", r["T"] == 40)):
    yy, pp, rw = y[sel], ph[sel], relw[sel]; fl = pp > 0.10
    L.append(f"| {lab} | {sel.sum()} | {yy.mean():.3f} | {auroc(pp, yy):.3f} | {auroc(rw, yy):.3f} | {fl.mean():.3f} | {yy[fl].mean():.3f} | {yy[~fl].mean():.3f} | {yy[fl].mean()/yy[~fl].mean():.2f} |")
# stated coding consistency between training (cell-derived) and fresh (width_key)
KC = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}
cellk = np.array([KC[c.split("|")[0]] for c in map(str, f["cells"])])[r["cell"].astype(int)]
L.append(f"\nstated (width_key) == cell kind on fresh clean rows: {(cellk == r['stated']).mean():.4f}")
# unit seed collision check
fresh_units = {30261102 + 1000*t + rep for t in range(20) for rep in range(3)}
main_units = {20261102 + 1000*t + rep for t in range(20) for rep in range(3)}
cal_units = {20261102 + 500000 + 1000*t + rep for t in range(20) for rep in range(3)}
L.append(f"unit-seed overlap fresh vs main: {len(fresh_units & main_units)}, fresh vs calibration(+500000): {len(fresh_units & cal_units)}")
(ROOT / "results/ext_verify2_revlag/recheck_bc.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
