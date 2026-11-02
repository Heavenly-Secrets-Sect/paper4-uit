"""Descriptive extras for ext_v51_eval (not part of the rule): duplicated terms removed by the
de-duplication, opened pairs, and null-pair interval score of v5_1 against v4.

Run: python experiments/ext/v51/describe_eval.py -> results/ext_v51_eval/describe.md
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CELLS, RES, TS, load  # noqa: E402

rows = load("ext_v51_eval")
out = ["# ext_v51_eval: descriptive extras (experiments/ext/v51/describe_eval.py)", "",
       "## Missing cells: duplicated lag terms removed on the data fit / summed over all bootstrap draws, opened pairs (data / mean per draw)", "",
       "| T | cell | dup terms data | dup terms total | n_open | n_open per draw |", "|---|---|---|---|---|---|"]
res = {}
for T in TS:
    for kind, rate in CELLS:
        if kind != "missing":
            continue
        g = [r for r in rows if r["method"] == "tolerant_v5_1" and r["T"] == T and r["kind"] == kind and r["rate"] == rate and r["status"] == "ok"]
        v = {k: float(np.mean([r.get(f"info_{k}") or 0 for r in g])) for k in ("n_dup_terms_data", "n_dup_terms_total", "n_open", "n_open_boot_mean")}
        share = float(np.mean([(r.get("info_n_dup_terms_total") or 0) > 0 for r in g]))
        res[f"{T}|{kind}|{rate}"] = {**v, "share_runs_with_dup": share}
        out.append(f"| {T} | {kind}-{rate} | {v['n_dup_terms_data']:.1f} | {v['n_dup_terms_total']:.0f} (runs with any: {share:.2f}) | {v['n_open']:.1f} | {v['n_open_boot_mean']:.1f} |")
out += ["", "## Null-pair interval score (iscore_null_mean), mean over runs", "", "| T | cell | v4 | v5_1 |", "|---|---|---|---|"]
for T in TS:
    for kind, rate in CELLS:
        vals = []
        for m in ("tolerant_v4", "tolerant_v5_1"):
            x = [r["iscore_null_mean"] for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind and r["rate"] == rate
                 and r["status"] == "ok" and r.get("iscore_null_mean") is not None]
            vals.append(float(np.mean(x)) if x else float("nan"))
        res[f"null|{T}|{kind}|{rate}"] = vals
        out.append(f"| {T} | {kind}-{rate} | {vals[0]:.3f} | {vals[1]:.3f} |")
(RES / "ext_v51_eval" / "describe.md").write_text("\n".join(out) + "\n")
(RES / "ext_v51_eval" / "describe.json").write_text(json.dumps(res, indent=1))
print("\n".join(out))
