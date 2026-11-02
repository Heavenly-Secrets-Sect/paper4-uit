"""Numbers for the R2-10 corrections appended to docs/ext/gate.md (no new runs; reads stored rows).

1. Share of runs in which B1 v1 / v2 (results/b1_auto, results/b1v2_auto) opened all lags
   (info_full_lags) on the undamaged cell, per T; and auto3's gate open rate there (ext_gate_auto3).
2. tolerant_auto3 vs tolerant_auto3_nogate in every cell (coverage / IS, paired difference clustered
   by topology), results/ext_gate_auto3.
Run: python experiments/ext/auto5/gate_corrections.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats5 as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_auto5_gate_corrections"
OUT.mkdir(parents=True, exist_ok=True)
L, J = ["# Numbers for the R2-10 corrections of docs/ext/gate.md", ""], {}
L += ["## 1. All-lag opening on the undamaged cell", "", "| source | T | share of runs with all lags opened | n |", "|---|---|---|---|"]
for name in ("b1_auto", "b1v2_auto"):
    rows = [r for r in S.load(ROOT / "results" / name / "runs.jsonl") if r["method"] == "tolerant_auto" and r["kind"] == "none"]
    for T in (40, 80, 150):
        ok = [r for r in rows if r["T"] == T and r["status"] == "ok"]
        s = float(np.mean([bool(r.get("info_full_lags")) for r in ok]))
        J[f"{name}|{T}"] = s
        L.append(f"| {name} tolerant_auto | {T} | {s:.3f} | {len(ok)} |")
g = S.load(ROOT / "results" / "ext_gate_auto3" / "runs.jsonl")
for T in (40, 80, 150):
    ok = [r for r in g if r["method"] == "tolerant_auto3" and r["kind"] == "none" and r["T"] == T and r["status"] == "ok"]
    s = float(np.mean([r["info_state"] == "open" for r in ok]))
    J[f"auto3_gate_open|{T}"] = s
    L.append(f"| ext_gate_auto3 tolerant_auto3 (gate open) | {T} | {s:.3f} | {len(ok)} |")
L += ["", "## 2. tolerant_auto3 vs tolerant_auto3_nogate (ext_gate_auto3)", "",
      "| T | cell | auto3 cov / IS | nogate cov / IS | auto3 - nogate [95% CI] |", "|---|---|---|---|---|"]
idx = S.index(g)
grp = defaultdict(list)
for r in g:
    if r["status"] == "ok":
        grp[(r["T"], r["kind"], r["rate"], r["method"])].append(r)
cells = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5), ("ges", 0.0)]
for T in (40, 80, 150):
    for kind, rate in cells:
        a, b = grp[(T, kind, rate, "tolerant_auto3")], grp[(T, kind, rate, "tolerant_auto3_nogate")]
        d = S.paired(idx, lambda k, T=T, kind=kind, rate=rate: k[3] == T and k[4] == kind and k[5] == rate,
                     "tolerant_auto3", "tolerant_auto3_nogate")
        J[f"{T}|{kind}|{rate}"] = {"auto3": [S.coverage(a), float(np.mean([r["iscore_nonnull_mean"] for r in a]))],
                                   "nogate": [S.coverage(b), float(np.mean([r["iscore_nonnull_mean"] for r in b]))], "diff": d}
        L.append(f"| {T} | {kind} {rate} | {J[f'{T}|{kind}|{rate}']['auto3'][0]:.3f} / {J[f'{T}|{kind}|{rate}']['auto3'][1]:.2f} | "
                 f"{J[f'{T}|{kind}|{rate}']['nogate'][0]:.3f} / {J[f'{T}|{kind}|{rate}']['nogate'][1]:.2f} | {S.fmt(d)} |")
(OUT / "gate_corrections.md").write_text("\n".join(L) + "\n", encoding="utf-8")
(OUT / "gate_corrections.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
print("\n".join(L))
