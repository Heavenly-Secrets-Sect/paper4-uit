"""Summary of the D-07H design probe (results/ext_revlag_probe): lag metrics of tolerant_v4 vs
tolerant_v4L vs oracle by cell and role. Descriptive; writes results/ext_revlag_probe/summary.md."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
name = sys.argv[1] if len(sys.argv) > 1 else "ext_revlag_probe"
z = np.load(ROOT / "results" / name / "pairs.npz")
d = {k: z[k] for k in z.files}
methods = [str(m) for m in d["methods"]]
cells = [str(c) for c in d["cells"]]
lines = [f"# {name}: lag output, tolerant_v4 vs tolerant_v4L (descriptive)", "",
         "mlag = mean |mean lag error| over pairs with defined lag; peak = peak-lag hit over kept pairs; def = share of "
         "non-null pairs with a defined estimated mean lag; cov = interval coverage.", "",
         "| T | cell | role | n | method | mlag | peak | def | cov | lag-int cov |", "|---|---|---|---|---|---|---|---|---|---|"]
for T in sorted(set(d["T"].astype(int))):
    for c, cname in enumerate(cells):
        for role, rname in ((None, "all"), (2, "damaged")):
            if role == 2 and cname.startswith("none"):
                continue
            for m in methods:
                sel = (d["T"] == T) & (d["cell"] == c) & (d["method"] == methods.index(m))
                if role is not None:
                    sel &= d["role"] == role
                if not sel.any():
                    continue
                kept = sel & (d["C_e"] != 0)
                lok = sel & np.isfinite(d["ml_e"]) & np.isfinite(d["ml_t"])
                cov = ((d["lo"] <= d["C_t"]) & (d["C_t"] <= d["hi"]))[sel].mean()
                li = sel & np.isfinite(d["ml_lo"]) & np.isfinite(d["ml_t"])
                lic = ((d["ml_lo"] <= d["ml_t"]) & (d["ml_t"] <= d["ml_hi"]))[li].mean() if li.any() else np.nan
                lines.append(f"| {T} | {cname} | {rname} | {sel.sum()} | {m} | "
                             f"{np.mean(np.abs(d['ml_e'][lok] - d['ml_t'][lok])):.3f} | "
                             f"{np.mean(d['pk_e'][kept] == d['pk_t'][kept]):.3f} | "
                             f"{np.isfinite(d['ml_e'][sel]).mean():.3f} | {cov:.3f} | {lic:.3f} |")
out = ROOT / "results" / name / "summary.md"
out.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
