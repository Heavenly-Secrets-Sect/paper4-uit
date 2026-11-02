"""In-sample comparison of tolerant_auto5 design variants on the D-07H development probe
(probe_auto5.py), and the width table of the chosen variant.

A variant = (open rule, flip pool, grid):
  open rule: 'all' (auto3), 'tgt40' (targeted when rows/(1 + n lag_max) < 2.0, i.e. T = 40 here),
             'tgt80' (threshold 3.0: T = 40 and 80), 'tgtall' (targeted at every T)
  flip pool: 'sig' (auto3) or 'mec'
  grid:      'one' (1.0..10, as auto3) or 'two' (0.5..5.0, step 0.05)
Factors per (branch, T) are tuned on the same records (in-sample, optimistic).

Run: python experiments/ext/auto5/analyse_probe.py experiments/ext/auto5/probe.pkl results/ext_auto5_probe [--write-table VARIANT]
"""
from __future__ import annotations

import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

GRID1 = np.round(np.arange(1.0, 10.0001, 0.1), 2)
GRID2 = np.round(np.arange(0.5, 5.0001, 0.05), 2)
TGT = {"all": set(), "tgt40": {40}, "tgt80": {40, 80}, "tgtall": {40, 80, 150}}
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]


def factor(recs, grid):
    d = np.concatenate([x["dist"] for x in recs]).astype(float)
    h = np.concatenate([x["half"] for x in recs]).astype(float)
    cov = np.array([(d <= c * h).mean() for c in grid])
    return float(grid[np.argmax(cov >= min(0.95, cov.max() - 0.005))])


def pick(r, rule, flip):
    if r["state"] == "closed":
        return "closed", r["var"].get(f"closed_{flip}")
    mode = "targeted" if r["T"] in TGT[rule] else "all"
    x = r["var"].get(f"{mode}_{flip}")
    branch = x["branch"] if x else ("open_tgt" if mode == "targeted" else "open_all")
    return branch, x


def evaluate(recs, rule, flip, grid):
    g = GRID1 if grid == "one" else GRID2
    by = defaultdict(list)
    for r in recs:
        b, x = pick(r, rule, flip)
        if x is not None:
            by[(b, r["T"])].append(x)
    fac = {f"{b}|{T}": factor(v, g) for (b, T), v in sorted(by.items())}
    cells = {}
    for T in sorted({r["T"] for r in recs}):
        for kind, rate in CELLS:
            num = den = 0
            iss, wid, nfail = [], [], 0
            for r in recs:
                if r["T"] != T or r["kind"] != kind or r["rate"] != rate:
                    continue
                b, x = pick(r, rule, flip)
                if x is None:
                    nfail += 1
                    continue
                c = fac[f"{b}|{T}"]
                d, h = x["dist"].astype(float), x["half"].astype(float)
                num += int((d <= c * h).sum())
                den += len(d)
                iss.append(float(np.mean(2 * c * h + 40 * np.maximum(d - c * h, 0))))
                wid.append(float(np.median(2 * c * h)))
            cells[f"{T}|{kind}|{rate}"] = {"cov": num / den if den else None, "IS": float(np.mean(iss)) if iss else None,
                                           "width": float(np.median(wid)) if wid else None, "n_fail": nfail}
    return fac, cells


def main(argv):
    src, out = argv[0], Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    P = pickle.load(open(src, "rb"))
    recs = P["records"]
    variants = [(rule, flip, grid) for rule in TGT for flip in ("sig", "mec") for grid in ("one", "two")]
    res = {f"{a}/{b}/{c}": evaluate(recs, a, b, c) for a, b, c in variants}
    gate = defaultdict(list)
    for r in recs:
        gate[f"{r['T']}|{r['kind']}|{r['rate']}"].append(r["state"] == "open")
    lines = [f"# auto5 design probe (D-07H development, {P['n_topo']} topologies x 1 replicate, n_boot {P['n_boot']}, "
             f"{len(recs)} runs, {P['seconds']} s)", "",
             "In-sample: width factors tuned on the same runs. Cell entries: coverage / mean IS.", "",
             "## Gate open rate", "", "| cell | " + " | ".join(str(T) for T in P["Ts"]) + " |", "|---|" + "---|" * len(P["Ts"])]
    for kind, rate in CELLS:
        lines.append(f"| {kind} {rate} | " + " | ".join(f"{np.mean(gate[f'{T}|{kind}|{rate}']):.2f}" for T in P["Ts"]) + " |")
    lines += ["", "## Width factors per (branch, T)", ""]
    for name, (fac, _) in res.items():
        lines.append(f"- `{name}`: " + ", ".join(f"{k} {v}" for k, v in fac.items()))
    names = list(res)
    for grid in ("one", "two"):
        sel = [n for n in names if n.endswith(grid)]
        lines += ["", f"## Coverage / IS, grid {grid}", "", "| T | cell | " + " | ".join(n.rsplit('/', 1)[0] for n in sel) + " |",
                  "|---|---|" + "---|" * len(sel)]
        for T in P["Ts"]:
            for kind, rate in CELLS:
                key = f"{T}|{kind}|{rate}"
                lines.append(f"| {T} | {kind} {rate} | " + " | ".join(
                    f"{res[n][1][key]['cov']:.3f} / {res[n][1][key]['IS']:.2f}" + (f" (fail {res[n][1][key]['n_fail']})" if res[n][1][key]['n_fail'] else "")
                    for n in sel) + " |")
    (out / "probe_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "probe_summary.json").write_text(json.dumps({n: {"factors": f, "cells": c} for n, (f, c) in res.items()} |
                                                       {"_gate_open": {k: float(np.mean(v)) for k, v in gate.items()}},
                                                       indent=1), encoding="utf-8")
    if len(argv) > 3 and argv[2] == "--write-table":
        fac = res[argv[3]][0]
        table_path = Path(__file__).resolve().parent / "width_table.json"
        table_path.write_text(json.dumps(fac, indent=2), encoding="utf-8")
        print("width table", argv[3], fac, "->", table_path)
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
