"""R2-3a: apply the pre-registered rule (docs/ext/auto5.md section 1) to results/ext_auto5_a1.

Run: python experiments/ext/auto5/check_a1.py
Writes results/ext_auto5_a1/rule_check.md and rule_check.json.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats5 as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_auto5_a1"


def main():
    rows = S.load(OUT / "runs.jsonl")
    a1 = S.load(ROOT / "results" / "a1_latent_noise" / "runs.jsonl")
    # pairing check: plugin and oracle are built-in and seeded identically
    chk = {}
    for m in ("plugin", "oracle"):
        mine = {S.key(r): r["iscore_nonnull_mean"] for r in rows if r["method"] == m and r["status"] == "ok"}
        ref = {S.key(r): r["iscore_nonnull_mean"] for r in a1 if r["method"] == m and r["status"] == "ok"}
        common = set(mine) & set(ref)
        chk[m] = {"identical": sum(abs(mine[k] - ref[k]) < 1e-9 for k in common), "compared": len(common)}
    v4m = {S.key(r): r["iscore_nonnull_mean"] for r in rows if r["method"] == "tolerant_v4" and r["status"] == "ok"}
    v4r = {S.key(r): r["iscore_nonnull_mean"] for r in a1 if r["method"] == "tolerant_v4" and r["status"] == "ok"}
    common = set(v4m) & set(v4r)
    chk["tolerant_v4 (frozen vs a1 re-tuned factors)"] = {
        "identical": sum(abs(v4m[k] - v4r[k]) < 1e-9 for k in common), "compared": len(common)}

    g = defaultdict(list)
    for r in rows:
        g[(r["scenario"], r["T"], r["kind"], r["rate"], r["method"])].append(r)
    idx = S.index(rows)
    scen = ["clean", "latent1", "latent3", "noise0.1"]
    cells = [("none", 0.0), ("missing", 0.2), ("reversed", 0.2)]
    meths = ["oracle", "plugin", "tolerant_v4", "tolerant_auto3"]
    out = {"pairing": chk, "cells": {}}
    L = ["# R2-3a: tolerant_auto3 under latent confounders and measurement noise (D-07 development)", "",
         f"Pairing check vs a1_latent_noise: {json.dumps(chk)}", "",
         "## Coverage / IS per method; gate open rate and mean n_repair of auto3", "",
         "| scenario | T | cell | " + " | ".join(meths) + " | auto3 gate open | auto3 n_repair | auto3 - v4 | auto3 - plugin | auto3 - oracle |",
         "|---|---|---|" + "---|" * (len(meths) + 5)]
    for sc in scen:
        for T in (80, 150):
            for kind, rate in cells:
                c = {}
                for m in meths:
                    ok = [r for r in g[(sc, T, kind, rate, m)] if r["status"] == "ok"]
                    c[m] = {"ok": f"{len(ok)}/{len(g[(sc, T, kind, rate, m)])}", "cov": S.coverage(ok),
                            "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else None}
                a = [r for r in g[(sc, T, kind, rate, "tolerant_auto3")] if r["status"] == "ok"]
                c["gate_open"] = float(np.mean([r["info_state"] == "open" for r in a]))
                c["n_repair"] = float(np.mean([r["info_n_repair"] for r in a]))
                sel = lambda k, sc=sc, T=T, kind=kind, rate=rate: k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate  # noqa: E731
                for ref in ("tolerant_v4", "plugin", "oracle"):
                    c[f"vs_{ref}"] = S.paired(idx, sel, "tolerant_auto3", ref)
                out["cells"][f"{sc}|{T}|{kind}|{rate}"] = c
                L.append(f"| {sc} | {T} | {kind} {rate} | " + " | ".join(f"{c[m]['cov']:.3f} / {c[m]['IS']:.2f}" for m in meths)
                         + f" | {c['gate_open']:.2f} | {c['n_repair']:.2f} | {S.fmt(c['vs_tolerant_v4'])} | {S.fmt(c['vs_plugin'])} | {S.fmt(c['vs_oracle'])} |")
    # rule
    L += ["", "## Pre-registered rule (latent1, missing-0.2 and reversed-0.2 at T = 80 and 150)", ""]
    rc, ps = [], []
    for T in (80, 150):
        for kind in ("missing", "reversed"):
            a = [r for r in g[("latent1", T, kind, 0.2, "tolerant_auto3")] if r["status"] == "ok"]
            cov, p = S.coverage_test(a)
            rc.append((T, kind, cov, p))
            ps.append(p)
    rej = S.holm(ps)
    for (T, kind, cov, p), h in zip(rc, rej):
        L.append(f"- T={T} {kind}-0.2: coverage {cov:.3f} -> {'ok' if cov >= 0.90 else 'FAIL'}; "
                 f"one-sided p(H0 cov <= 0.90) = {p:.4f}; Holm-rejected: {h}")
    passed = sum(c >= 0.90 for _, _, c, _ in rc)
    verdict = "ROBUST (rule holds)" if passed == 4 else "NOT ROBUST (rule fails)"
    L += ["", f"Cells passing (point rule): {passed}/4; cells with H0 'cov <= 0.90' rejected after Holm (alpha 0.05): {sum(rej)}/4.",
          f"**VERDICT: {verdict}**"]
    # descriptive A1-style reading for latent3 / noise0.1 (and clean, latent1) incl. none
    L += ["", "## A1-style reading (coverage >= 0.90 per cell, descriptive)", ""]
    for sc in scen:
        okc = [f"T{T} {k}" for T in (80, 150) for k, _ in cells if out["cells"][f"{sc}|{T}|{k}|{0.0 if k == 'none' else 0.2}"]["tolerant_auto3"]["cov"] >= 0.90]
        L.append(f"- {sc}: auto3 >= 0.90 in {len(okc)}/6 cells ({', '.join(okc)}); "
                 f"v4 in {sum(out['cells'][f'{sc}|{T}|{k}|{0.0 if k == chr(110)+chr(111)+chr(110)+chr(101) else 0.2}']['tolerant_v4']['cov'] >= 0.90 for T in (80, 150) for k, _ in cells)}/6")
    out["rule"] = {"cells": [{"T": T, "kind": k, "cov": c, "p_one_sided": p, "holm_reject": h} for (T, k, c, p), h in zip(rc, rej)],
                   "passed": passed, "holm_rejected": int(sum(rej)), "verdict": verdict}
    (OUT / "rule_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "rule_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
