"""Merge probe2 (targeted opening with budget max(#BH, 1)) into the probe records and compare the
variants (in-sample, D-07H development). Flip label 'sig_bh' = sig flips, closed and all-lag branches
as in 'sig', targeted branch with the BH opening budget.
Run: python experiments/ext/auto5/analyse_probe2.py -> results/ext_auto5_probe/probe2_summary.{md,json}"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse_probe as AP  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "results" / "ext_auto5_probe"
P = pickle.load(open(HERE / "probe.pkl", "rb"))
P2 = pickle.load(open(HERE / "probe2.pkl", "rb"))
k = lambda r: (r["T"], r["kind"], r["rate"], r["topology"], r["rep"])  # noqa: E731
extra = {k(r): r for r in P2["records"]}
for r in P["records"]:
    r2 = extra[k(r)]
    assert r2["state"] == r["state"]
    r["var"]["closed_sig_bh"] = r["var"].get("closed_sig")
    r["var"]["all_sig_bh"] = r["var"].get("all_sig")
    if r["state"] == "open":
        r["var"]["targeted_sig_bh"] = r2["var"].get("targeted_sig_bh")
variants = [(rule, flip, grid) for rule in ("all", "tgt40", "tgt80", "tgtall") for flip in ("sig", "sig_bh") for grid in ("one", "two")]
res = {f"{a}/{b}/{c}": AP.evaluate(P["records"], a, b, c) for a, b, c in variants}
L = [f"# auto5 probe 2 (D-07H development, in-sample; probe2 {P2['seconds']} s)", "", "## Factors", ""]
for n, (f, _) in res.items():
    L.append(f"- `{n}`: " + ", ".join(f"{a} {b}" for a, b in f.items()))
n_open = {}
for r in P["records"]:
    for v in ("targeted_sig", "targeted_sig_bh"):
        x = r["var"].get(v)
        if x is not None and r["state"] == "open":
            n_open.setdefault((v, r["T"], r["kind"], r["rate"]), []).append(x["n_open"] or 0)
L += ["", "## Mean number of opened pairs (open runs)", "", "| T | cell | targeted_sig (max budget) | targeted_sig_bh |", "|---|---|---|---|"]
for T in P["Ts"]:
    for kind, rate in AP.CELLS:
        a, b = n_open.get(("targeted_sig", T, kind, rate)), n_open.get(("targeted_sig_bh", T, kind, rate))
        if a:
            L.append(f"| {T} | {kind} {rate} | {np.mean(a):.1f} | {np.mean(b):.1f} |")
for grid in ("one", "two"):
    sel = [n for n in res if n.endswith(grid)]
    L += ["", f"## Coverage / IS, grid {grid}", "", "| T | cell | " + " | ".join(n.rsplit('/', 1)[0] for n in sel) + " |", "|---|---|" + "---|" * len(sel)]
    for T in P["Ts"]:
        for kind, rate in AP.CELLS:
            key = f"{T}|{kind}|{rate}"
            L.append(f"| {T} | {kind} {rate} | " + " | ".join(f"{res[n][1][key]['cov']:.3f} / {res[n][1][key]['IS']:.2f}" for n in sel) + " |")
    L += ["", f"Mean IS over the 21 cells (grid {grid}): " + ", ".join(f"{n.rsplit('/', 1)[0]} {np.mean([c['IS'] for c in res[n][1].values()]):.3f}" for n in sel),
          f"Min coverage over missing/reversed cells at T >= 80 (grid {grid}): " + ", ".join(
              f"{n.rsplit('/', 1)[0]} {min(c['cov'] for kk, c in res[n][1].items() if kk.split('|')[1] in ('missing', 'reversed') and int(kk.split('|')[0]) >= 80):.3f}" for n in sel)]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "probe2_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
(OUT / "probe2_summary.json").write_text(json.dumps({n: {"factors": f, "cells": c} for n, (f, c) in res.items()}, indent=1), encoding="utf-8")
if len(sys.argv) > 2 and sys.argv[1] == "--write-table":
    (HERE / "width_table.json").write_text(json.dumps(res[sys.argv[2]][0], indent=2), encoding="utf-8")
    print("width table", sys.argv[2], res[sys.argv[2]][0])
print("\n".join(L))
