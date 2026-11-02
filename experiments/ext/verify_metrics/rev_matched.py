"""Is the module's under-coverage on reversed pairs specific to reversal, or shared by lag-0 pairs in general? (skeptic check)"""
import numpy as np
z = np.load("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_metrics_pairs/pairs.npz")
d = {k: z[k] for k in z.files}
methods = [str(m) for m in d["methods"]]; cells = [str(c) for c in d["cells"]]
cov = (d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"])
T = np.isin(d["T"], (80, 150))
rev = np.isin(d["cell"], [cells.index("reversed|0.2"), cells.index("reversed|0.5")])
none = d["cell"] == cells.index("none|0.0")
for m in ("tolerant_v4", "oracle", "plugin"):
    mm = d["method"] == methods.index(m)
    for lab, s in (("reversed cells, damaged (all lag0)", rev & (d["role"] == 2)),
                   ("reversed cells, untouched, direct lag0", rev & (d["role"] == 0) & (d["direct_lag"] == 0)),
                   ("none cell, direct lag0", none & (d["direct_lag"] == 0)),
                   ("none cell, all", none)):
        sel = mm & T & s
        a = np.abs(d["C_t"][sel])
        print(f"{m:12s} {lab:42s} n={sel.sum():5d} miss={1 - cov[sel].mean():.3f} med|C|={np.median(a):.2f}")
    # T separately for damaged
    for t in (80, 150):
        sel = mm & (d["T"] == t) & rev & (d["role"] == 2)
        print(f"   T={t} reversed damaged miss={1 - cov[sel].mean():.3f}")
