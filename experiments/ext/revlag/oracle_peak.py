"""Context numbers for R2-6b: peak-lag hit and mean-lag error of oracle / v4 / v4L on damaged
pairs (role 2) of reversed cells, ext_revlag_lag. Writes results/ext_revlag_lag/oracle_peak.md."""
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
z = np.load(ROOT / "results/ext_revlag_lag/pairs.npz"); d = {k: z[k] for k in z.files}
ms = [str(m) for m in d["methods"]]; cells = [str(c) for c in d["cells"]]
L = ["| cell | T | method | n kept | peak hit | mean-lag abs err (defined) |", "|---|---|---|---|---|---|"]
for c in ("reversed|0.2", "reversed|0.5"):
    for T in (40, 80, 150):
        for m in ms:
            s = (d["cell"] == cells.index(c)) & (d["T"] == T) & (d["role"] == 2) & (d["method"] == ms.index(m)) & (d["C_e"] != 0)
            ok = s & np.isfinite(d["ml_t"]) & np.isfinite(d["ml_e"])
            L.append(f"| {c} | {T} | {m} | {s.sum()} | {np.mean(d['pk_e'][s] == d['pk_t'][s]):.3f} | "
                     f"{np.mean(np.abs(d['ml_e'][ok] - d['ml_t'][ok])):.3f} |")
(ROOT / "results/ext_revlag_lag/oracle_peak.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
