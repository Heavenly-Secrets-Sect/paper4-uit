"""Analyzer of E2 on P4-H6 (frozen rule, docs/ext/p4h6_e2.md). Run once, after all three runners finished.

Reads results/ext_p4h6_e2_{gauss,ngmix,ngt10}/runs.jsonl and writes results/ext_p4h6_e2_analysis/{analysis.md,summary.json}.
Metric: coverage of the 95% interval of C(H) on non-null pairs of method tolerant_v5_1 (sum n_covered_nonnull / sum n_nonnull).
Clusters for the bootstrap are topologies (20 in the confirmatory split); B = 10000, seed 20261113.

Rule per shock s in {ng_mix, ng_t10}, on T in {80, 150}, 7 cells (none, extra/missing/reversed x 0.2/0.5):
  V1  pooled coverage: cluster-bootstrap lower 97.5% bound >= 0.90 (97.5% = Bonferroni over the two shocks).
  V2  every one of the 14 (cell, T) point coverages >= 0.85.
  V3  pooled paired difference (s minus gauss, same clusters): point >= -0.03 and lower 97.5% bound >= -0.05.
  V0  integrity: all 60 units x 3 T x 7 cells present for tolerant_v5_1 with status ok in every run directory.
Verdict: CONFIRMED if both shocks pass V0-V3; PARTIALLY CONFIRMED if exactly one passes; else NOT CONFIRMED.
T = 40 and per-kind tables are descriptive, never part of the verdict.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SHOCKS = {"gauss": "ext_p4h6_e2_gauss", "ng_mix": "ext_p4h6_e2_ngmix", "ng_t10": "ext_p4h6_e2_ngt10"}
METHOD = "tolerant_v5_1"
TS_RULE = (80, 150)
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
N_UNITS, N_TOPO = 60, 20
B, SEED = 10000, 20261113
LO_Q = 0.025


def load(name):
    path = ROOT / "results" / name / "runs.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if r["method"] == METHOD]


def table(rows):
    """{(T, kind, rate): {topology: [covered, nonnull]}}"""
    t = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in rows:
        c = t[(r["T"], r["kind"], float(r["rate"]))][r["topology"]]
        c[0] += r["n_covered_nonnull"]
        c[1] += r["n_nonnull"]
    return t


def cov(tab, keys, topos):
    cv = sum(tab[k][t][0] for k in keys for t in topos if t in tab[k])
    nn = sum(tab[k][t][1] for k in keys for t in topos if t in tab[k])
    return cv / nn if nn else float("nan")


SMOKE = "--smoke" in sys.argv  # dry run on the D-07 smoke outputs (names + "_smoke"); never part of the verdict


def main() -> int:
    global N_UNITS, N_TOPO, SHOCKS
    if SMOKE:
        SHOCKS = {s: n + "_smoke" for s, n in SHOCKS.items()}
        N_UNITS = 2
    data = {s: load(n) for s, n in SHOCKS.items()}
    tabs = {s: table(r) for s, r in data.items()}
    topos = sorted({r["topology"] for r in data["gauss"]})
    if SMOKE:
        N_TOPO = len(topos)
    out = {"verdict": None, "integrity": {}, "shocks": {}}
    # V0 integrity
    need = N_UNITS * 3 * len(CELLS)
    integ = {}
    for s, rows in data.items():
        ok = [r for r in rows if r["status"] == "ok"]
        integ[s] = {"rows": len(rows), "ok": len(ok), "need": need, "topologies": len({r["topology"] for r in rows})}
    v0 = all(v["rows"] == need and v["ok"] == need and v["topologies"] == N_TOPO for v in integ.values())
    out["integrity"] = {"pass": v0, **integ}
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(topos), size=(B, len(topos)))
    keys_rule = [(T, k, r) for T in TS_RULE for (k, r) in CELLS]

    def boot(tab_a, keys, tab_b=None):
        vals = np.empty(B)
        for b in range(B):
            sel = [topos[i] for i in idx[b]]
            vals[b] = cov(tab_a, keys, sel) - (cov(tab_b, keys, sel) if tab_b is not None else 0.0)
        return vals

    md = ["# E2 on P4-H6: frozen tolerant_v5_1 under non-Gaussian shocks", "", f"V0 integrity: {'PASS' if v0 else 'FAIL'} {json.dumps(integ)}", ""]
    passes = []
    for s in ("ng_mix", "ng_t10"):
        tab, g = tabs[s], tabs["gauss"]
        pooled = cov(tab, keys_rule, topos)
        pooled_g = cov(g, keys_rule, topos)
        lo1 = float(np.quantile(boot(tab, keys_rule), LO_Q))
        diff = pooled - pooled_g
        lo3 = float(np.quantile(boot(tab, keys_rule, g), LO_Q))
        cell_cov = {f"T{T}|{k}|{r}": cov(tab, [(T, k, r)], topos) for T in TS_RULE for (k, r) in CELLS}
        v1, v2, v3 = lo1 >= 0.90, all(v >= 0.85 for v in cell_cov.values()), (diff >= -0.03 and lo3 >= -0.05)
        ok = v0 and v1 and v2 and v3
        passes.append(ok)
        out["shocks"][s] = {"pooled": pooled, "pooled_gauss": pooled_g, "lo97.5_pooled": lo1, "diff_vs_gauss": diff, "lo97.5_diff": lo3,
                            "min_cell": min(cell_cov.values()), "V1": v1, "V2": v2, "V3": v3, "pass": ok}
        md += [f"## {s}", f"- pooled coverage (T in 80,150; 7 cells) {pooled:.4f}; gauss {pooled_g:.4f}; diff {diff:+.4f}",
               f"- V1 lower 97.5% bound {lo1:.4f} (>= 0.90): {'PASS' if v1 else 'FAIL'}",
               f"- V2 min cell coverage {min(cell_cov.values()):.4f} (>= 0.85): {'PASS' if v2 else 'FAIL'}",
               f"- V3 diff {diff:+.4f} (>= -0.03), lower 97.5% bound {lo3:+.4f} (>= -0.05): {'PASS' if v3 else 'FAIL'}",
               f"- verdict {s}: {'PASS' if ok else 'FAIL'}", ""]
    n = sum(passes)
    out["verdict"] = "CONFIRMED on the sealed bank P4-H6" if n == 2 else ("PARTIALLY CONFIRMED on the sealed bank P4-H6" if n == 1 else "NOT CONFIRMED on the sealed bank P4-H6")
    md.insert(2, f"**Verdict: {out['verdict']}**")
    md += ["## Descriptive: coverage per (T, cell) for every shock (not part of the verdict)", "",
           "| T | cell | gauss | ng_mix | ng_t10 |", "|---|---|---|---|---|"]
    for T in (40, 80, 150):
        for (k, r) in CELLS:
            md.append(f"| {T} | {k} {r} | " + " | ".join(f"{cov(tabs[s], [(T, k, r)], topos):.3f}" for s in ('gauss', 'ng_mix', 'ng_t10')) + " |")
    outdir = ROOT / "results" / ("ext_p4h6_e2_analysis_smoke" if SMOKE else "ext_p4h6_e2_analysis")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (outdir / "summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n".join(md[:14]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
