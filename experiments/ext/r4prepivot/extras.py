"""Descriptive extras for r4prepivot (not part of the rule; written after the primary verdict).

For each analysed part: Holm (0.05) count of cells where tolerant_v5_1_pp is significantly WORSE than
tolerant_v5_1 (one-sided p for H0: ratio <= 1, from the same cluster bootstrap as the rule), the
ratio f_pp / f_v51_eff per cell, and the coverage gap pp - v51. Writes results/ext_r4prepivot_extras.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import RES, holm  # noqa: E402

out = {}
for part in sys.argv[1:] or ["primary", "secondary", "lag1", "scen"]:
    p = RES / f"ext_r4prepivot_{part}" / "analysis.json"
    if not p.exists():
        continue
    o = json.loads(p.read_text(encoding="utf-8"))
    cells = o["cells"]
    for m in ("tolerant_v5_1_pp", "tolerant_v5_1_pp_orig"):
        ps = [c[m]["ratio_test"]["p_worse_than_1"] for c in cells]
        rej = holm(ps)
        out.setdefault(part, {})[m] = {
            "n_cells": len(cells),
            "worse_holm": int(sum(rej)),
            "worse_raw": int(sum(p < 0.05 for p in ps)),
            "noninf_holm": int(sum(c[m]["noninf_holm"] for c in cells)),
            "cov_ge_090": int(sum(c[m]["cov_itt"] >= 0.90 for c in cells)),
            "cells": [{"cell": c["cell"], "ratio": c[m]["ratio_test"]["ratio"], "p_worse": c[m]["ratio_test"]["p_worse_than_1"],
                       "worse_holm": bool(r), "cov_gap": c[m]["cov_itt"] - c["tolerant_v5_1"]["cov_itt"],
                       "f_ratio_to_bank": ((c["f_pp"] if m.endswith("_pp") else c["f_orig"]) or {}).get("median", float("nan"))
                       / c["f_v51_eff"] if c.get("f_v51_eff") else None}
                      for c, r in zip(cells, rej)]}
(RES / "ext_r4prepivot_extras.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for part, d in out.items():
    for m, v in d.items():
        print(part, m, {k: v[k] for k in ("n_cells", "worse_holm", "worse_raw", "noninf_holm", "cov_ge_090")})
