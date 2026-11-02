"""Independent recomputation of the metrics-direction headline numbers from pairs.npz (skeptic check)."""
import numpy as np
from scipy.stats import rankdata
z = np.load("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_metrics_pairs/pairs.npz")
d = {k: z[k] for k in z.files}
methods = [str(m) for m in d["methods"]]; cells = [str(c) for c in d["cells"]]
print(methods, cells)
cov = (d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"])
M = lambda m: d["method"] == methods.index(m)
C = lambda c: d["cell"] == cells.index(c)
def auc(s, y):
    r = rankdata(s); n1 = y.sum(); n0 = len(y) - n1
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
mod = M("tolerant_v4")
for Ts in ((80, 150), (40,)):
    b = mod & np.isin(d["T"], Ts)
    y = ~cov[b]
    print(Ts, "n", b.sum(), "base", round(y.mean(), 4))
    for s in ("rel_width", "width", "zero_in", "coef_stab", "lag_stab", "resid_lb", "n_repair"):
        ok = np.isfinite(d[s][b])
        print("  ", s, "defined", round(ok.mean(), 3), "auc", round(auc(d[s][b][ok], y[ok]), 3))
    f = d["rel_width"][b] > 2
    print("  flag share", round(f.mean(), 3), "miss flagged", round(y[f].mean(), 3), "unflagged", round(y[~f].mean(), 3),
          "ratio", round(y[f].mean() / y[~f].mean(), 2), "unflagged cov", round(1 - y[~f].mean(), 3))
    q = np.quantile(d["rel_width"][b], [.2, .4, .6, .8]); bb = np.digitize(d["rel_width"][b], q)
    print("  condcov", [round(1 - y[bb == k].mean(), 3) for k in range(5)])
# pair-level spot checks
for T in (80, 150):
    for m in ("plugin", "tolerant_v4", "oracle", "pselect_union"):
        for cell in ("missing|0.5", "reversed|0.5", "reversed|0.2"):
            for role in (2, 1, 0):
                s = M(m) & C(cell) & (d["T"] == T) & (d["role"] == role)
                print(T, m, cell, role, s.sum(), "cov", round(cov[s].mean(), 3))
# reversed: module vs oracle miss, pooled T80/150
for m in ("tolerant_v4", "oracle"):
    for role in (2, 1, 0):
        s = M(m) & np.isin(d["T"], (80, 150)) & np.isin(d["cell"], [cells.index("reversed|0.2"), cells.index("reversed|0.5")]) & (d["role"] == role)
        print("rev pooled", m, role, s.sum(), "miss", round(1 - cov[s].mean(), 3))
