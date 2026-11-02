"""Known-truth test of analyze.py on synthetic rows (written to a scratch results root, never to results/ext_r4leadlag_eval_*).
Variant A: IS 10% lower than v5_1 in the 8 primary cells, identical elsewhere -> RETAINED (8 wins).
Variant D: IS 10% higher in clean T150 missing cells -> NOT RETAINED (no-harm). Gate logs: A separates C from E0 perfectly.
Run: python experiments/ext/r4leadlag/test_analyze.py <scratch_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as AZ  # noqa: E402

root = Path(sys.argv[1])
AZ.RES = root
AZ.OUT = root / "rule"
rng = np.random.default_rng(0)
M = ["tolerant_v5_1", AZ.VARIANTS["A"], AZ.VARIANTS["D"], "oracle"]
grids = {"ext_r4leadlag_eval_clean": [("clean", T, k, r) for T in (40, 80, 150) for k, r in
                                      [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]],
         "ext_r4leadlag_eval_latent": [(sc, T, k, r) for sc in ("latent1", "latent3") for T in (40, 80, 150)
                                       for k, r in (("none", 0.0), ("missing", 0.2), ("missing", 0.5))],
         "ext_r4leadlag_eval_noise": [("noise0.1", T, k, r) for T in (80, 150) for k, r in (("none", 0.0), ("missing", 0.2))]}
for run, cells in grids.items():
    (root / run).mkdir(parents=True, exist_ok=True)
    with open(root / run / "runs.jsonl", "w") as fh:
        for t in range(20):
            for rep in range(3):
                for sc, T, k, r in cells:
                    base = 2.0 + rng.normal(0, 0.1)
                    for m in M:
                        IS = base
                        if m == AZ.VARIANTS["A"] and (sc, T, r) in AZ.PRIMARY and k == "missing":
                            IS = base * 0.9
                        if m == AZ.VARIANTS["D"] and sc == "clean" and T == 150 and k == "missing":
                            IS = base * 1.1
                        row = {"method": m, "status": "ok", "scenario": sc, "topology": f"t{t}", "replicate": rep, "T": T,
                               "kind": k, "rate": r, "iscore_nonnull_mean": IS, "n_covered_nonnull": 19, "n_nonnull": 20}
                        if m in AZ.VARIANTS.values() and k == "missing":
                            row["info_gate_p"] = [[0, 1, 0.001, 0.01], [2, 3, 0.002, 0.5]] * 6
                            row["cls_gate_p"] = ["C", "E0"] * 6 if m == AZ.VARIANTS["A"] else ["E0", "C"] * 6
                            row["info_gate_scores"] = [[0, 1, 0.001, 9.0, 0.01]]
                            row["cls_gate_scores"] = ["C"]
                        fh.write(json.dumps(row) + "\n")
AZ.main()
o = json.loads((root / "rule" / "ruling.json").read_text())
checks = {"A_retained": o["rule"]["A"]["RETAINED"] is True and o["rule"]["A"]["wins"] == 8,
          "D_not_retained": o["rule"]["D"]["RETAINED"] is False and len(o["rule"]["D"]["noharm_violations"]) == 2,
          "V1_A": o["validity"]["A"]["pass"], "V1_D": o["validity"]["D"]["pass"],
          "auroc_A_1": abs(o["auroc"]["A"]["T150_examined"]["auroc"] - 1.0) < 1e-12 and o["auroc"]["A"]["informative"],
          "auroc_D_0": abs(o["auroc"]["D"]["T150_examined"]["auroc"] - 0.0) < 1e-12 and not o["auroc"]["D"]["informative"]}
print(checks, "ALL OK" if all(checks.values()) else "FAIL")
(root / "checks.json").write_text(json.dumps(checks))
