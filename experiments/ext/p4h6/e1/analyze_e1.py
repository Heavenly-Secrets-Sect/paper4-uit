"""Analyzer of E1 on P4-H6 development (frozen rule, docs/ext/p4h6_e1.md). Run once, after all four runners finished.

Reads results/ext_p4h6_e1_{r0,r1,r2,r3}/runs.jsonl (method tolerant_v5_1) and writes results/ext_p4h6_e1_analysis/{analysis.md,summary.json}.
Coverage = sum n_covered_nonnull / sum n_nonnull; interval score pooled = sum(iscore_nonnull_mean * n_nonnull) / sum n_nonnull.
Bootstrap over topologies (20), B = 10000, seed 20261114, 97.5% bounds. Rule, on T in {80, 150} and the 7 cells:
  V0 all four runs complete (1260 rows each, status ok, 20 topologies).
  V1 R1 pooled coverage lower bound >= 0.90 and every (cell, T) point coverage >= 0.85.
  V2 paired pooled coverage difference R1 - R0: point >= -0.01 and lower bound >= -0.03.
  V3 pooled interval-score ratio R1 / R0: upper bound <= 1.10.
Verdict: "A single global width factor is sufficient (on P4-H6 development)" if V0..V3 pass, else "Not sufficient". R2, R3 and T = 40 are descriptive.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
RULES = ("r0", "r1", "r2", "r3")
METHOD = "tolerant_v5_1"
TS_RULE = (80, 150)
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
N_UNITS, N_TOPO = 60, 20
B, SEED = 10000, 20261114
SMOKE = "--smoke" in sys.argv


def load(tag):
    path = ROOT / "results" / (f"ext_p4h6_e1_{tag}" + ("_smoke" if SMOKE else "")) / "runs.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if r["method"] == METHOD]


def table(rows):
    """{(T, kind, rate): {topology: [covered, nonnull, iscore_sum]}}"""
    t = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))
    for r in rows:
        c = t[(r["T"], r["kind"], float(r["rate"]))][r["topology"]]
        c[0] += r["n_covered_nonnull"]
        c[1] += r["n_nonnull"]
        c[2] += (r["iscore_nonnull_mean"] or 0.0) * r["n_nonnull"]
    return t


def agg(tab, keys, topos):
    cv = nn = sc = 0.0
    for k in keys:
        for t in topos:
            if t in tab[k]:
                cv += tab[k][t][0]
                nn += tab[k][t][1]
                sc += tab[k][t][2]
    return (cv / nn if nn else float("nan")), (sc / nn if nn else float("nan"))


def main() -> int:
    global N_UNITS, N_TOPO
    data = {t: load(t) for t in RULES}
    tabs = {t: table(r) for t, r in data.items()}
    topos = sorted({r["topology"] for r in data["r0"]})
    if SMOKE:
        N_UNITS, N_TOPO = 2, len(topos)
    need = N_UNITS * 3 * len(CELLS)
    integ = {t: {"rows": len(r), "ok": sum(1 for x in r if x["status"] == "ok"), "topologies": len({x["topology"] for x in r})} for t, r in data.items()}
    v0 = all(v["rows"] == need and v["ok"] == need and v["topologies"] == N_TOPO for v in integ.values())
    keys = [(T, k, r) for T in TS_RULE for (k, r) in CELLS]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(topos), size=(B, len(topos)))
    cov1 = agg(tabs["r1"], keys, topos)[0]
    cov0 = agg(tabs["r0"], keys, topos)[0]
    is1, is0 = agg(tabs["r1"], keys, topos)[1], agg(tabs["r0"], keys, topos)[1]
    boot_c1, boot_d, boot_ratio = np.empty(B), np.empty(B), np.empty(B)
    for b in range(B):
        sel = [topos[i] for i in idx[b]]
        c1, s1 = agg(tabs["r1"], keys, sel)
        c0, s0 = agg(tabs["r0"], keys, sel)
        boot_c1[b], boot_d[b], boot_ratio[b] = c1, c1 - c0, s1 / s0
    lo_c1 = float(np.quantile(boot_c1, 0.025))
    lo_d = float(np.quantile(boot_d, 0.025))
    hi_ratio = float(np.quantile(boot_ratio, 0.975))
    cell_cov = {f"T{T}|{k}|{r}": agg(tabs["r1"], [(T, k, r)], topos)[0] for T in TS_RULE for (k, r) in CELLS}
    v1 = lo_c1 >= 0.90 and all(v >= 0.85 for v in cell_cov.values())
    diff = cov1 - cov0
    v2 = diff >= -0.01 and lo_d >= -0.03
    v3 = hi_ratio <= 1.10
    ok = v0 and v1 and v2 and v3
    verdict = "A single global width factor is sufficient (on P4-H6 development)" if ok else "Not sufficient (on P4-H6 development)"
    md = ["# E1 on P4-H6 development: one global width factor", "", f"**Verdict: {verdict}**",
          f"V0 integrity: {'PASS' if v0 else 'FAIL'} {json.dumps(integ)}", "",
          f"- R1 pooled coverage (T in 80,150; 7 cells) {cov1:.4f}; R0 {cov0:.4f}; difference {diff:+.4f}",
          f"- V1 R1 lower 97.5% bound {lo_c1:.4f} (>= 0.90) and min cell {min(cell_cov.values()):.4f} (>= 0.85): {'PASS' if v1 else 'FAIL'}",
          f"- V2 difference {diff:+.4f} (>= -0.01), lower 97.5% bound {lo_d:+.4f} (>= -0.03): {'PASS' if v2 else 'FAIL'}",
          f"- V3 interval-score ratio R1/R0 {is1 / is0:.4f}, upper 97.5% bound {hi_ratio:.4f} (<= 1.10): {'PASS' if v3 else 'FAIL'}", "",
          "## Descriptive (not part of the verdict)", "", "| rule | pooled coverage T80,150 | pooled IS T80,150 | T40 coverage | T40 IS |", "|---|---|---|---|---|"]
    keys40 = [(40, k, r) for (k, r) in CELLS]
    for t in RULES:
        c, s = agg(tabs[t], keys, topos)
        c4, s4 = agg(tabs[t], keys40, topos)
        md.append(f"| {t.upper()} | {c:.4f} | {s:.4f} | {c4:.4f} | {s4:.4f} |")
    md += ["", "| T | cell | R0 | R1 | R2 | R3 |", "|---|---|---|---|---|---|"]
    for T in (40, 80, 150):
        for (k, r) in CELLS:
            md.append(f"| {T} | {k} {r} | " + " | ".join(f"{agg(tabs[t], [(T, k, r)], topos)[0]:.3f}" for t in RULES) + " |")
    out = ROOT / "results" / ("ext_p4h6_e1_analysis_smoke" if SMOKE else "ext_p4h6_e1_analysis")
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"verdict": verdict, "V0": v0, "V1": v1, "V2": v2, "V3": v3, "cov_R1": cov1, "cov_R0": cov0,
                                                  "lo_cov_R1": lo_c1, "lo_diff": lo_d, "ratio_IS": is1 / is0, "hi_ratio": hi_ratio}, indent=1), encoding="utf-8")
    print("\n".join(md[:9]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
