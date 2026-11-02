"""FROZEN confirmatory analysis of tolerant_auto3 on P4-H2 (docs/ext/auto5.md, "Frozen spec for P4-H2").
Written on 2026-11-02 after the D-07 development results, BEFORE any P4-H2 use. Not run on P4-H2 by
the author. Dry-run on D-07 rows only:  python experiments/ext/auto5/check_p4h2.py --dry-run

Confirmed iff all of (point rules on pooled coverage, as in B1):
  C1 coverage >= 0.90 in missing/reversed x 0.2/0.5 at T = 80 and 150 (8 cells);
  C2 IS(none) <= 1.35 x IS(tolerant_v4) at T = 40, 80, 150;
  C3 GES cell at T = 80, 150: coverage >= 0.90 and IS <= 1.10 x IS(tolerant_v4);
  L1 scenario latent1: coverage >= 0.90 in missing-0.2 and reversed-0.2 at T = 80 and 150 (4 cells).
Reported with it: one-sided cluster-bootstrap p for H0 'coverage <= 0.90' (2000 resamples by topology,
seed 0) and the number of the 14 coverage cells (C1 + C3 + L1) rejected by Holm at alpha 0.05.

Run (after the two frozen configs): python experiments/ext/auto5/check_p4h2.py
Writes results/ext_auto5_p4h2_check/ (or results/ext_auto5_p4h2_dryrun/ with --dry-run).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats5 as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
M = "tolerant_auto3"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="use the D-07 development rows (not a confirmation)")
    a = ap.parse_args(argv)
    if a.dry_run:
        main_run, lat_run, out = "ext_gate_auto3", "ext_auto5_a1", ROOT / "results" / "ext_auto5_p4h2_dryrun"
    else:
        main_run, lat_run, out = "ext_auto5_p4h2_auto3", "ext_auto5_p4h2_auto3_latent1", ROOT / "results" / "ext_auto5_p4h2_check"
    rows = S.load(ROOT / "results" / main_run / "runs.jsonl")
    lat = S.load(ROOT / "results" / lat_run / "runs.jsonl")
    if not a.dry_run:
        for run in (main_run, lat_run):
            man = json.loads((ROOT / "results" / run / "manifest.json").read_text())
            assert man["config"]["bank"] == "P4-H2" and man["config"]["split"] == "confirmatory", run
    g = defaultdict(list)
    for r in rows:
        if r["status"] == "ok" and r.get("scenario", "clean") == "clean":
            g[("clean", r["T"], r["kind"], r["rate"], r["method"])].append(r)
    for r in lat:
        if r["status"] == "ok" and r.get("scenario") == "latent1":
            g[("latent1", r["T"], r["kind"], r["rate"], r["method"])].append(r)
    IS = lambda k: float(np.mean([r["iscore_nonnull_mean"] for r in g[k]]))  # noqa: E731
    cov_cells = []
    c1 = []
    for T in (80, 150):
        for kind in ("missing", "reversed"):
            for rate in (0.2, 0.5):
                cov, p = S.coverage_test(g[("clean", T, kind, rate, M)])
                c1.append({"cell": f"{T}|{kind}|{rate}", "cov": cov, "p": p, "ok": cov >= 0.90})
    c2 = [{"T": T, "ratio": IS(("clean", T, "none", 0.0, M)) / IS(("clean", T, "none", 0.0, "tolerant_v4"))} for T in (40, 80, 150)]
    for x in c2:
        x["ok"] = x["ratio"] <= 1.35
    c3 = []
    for T in (80, 150):
        cov, p = S.coverage_test(g[("clean", T, "ges", 0.0, M)])
        ratio = IS(("clean", T, "ges", 0.0, M)) / IS(("clean", T, "ges", 0.0, "tolerant_v4"))
        c3.append({"T": T, "cov": cov, "p": p, "ratio": ratio, "ok": cov >= 0.90 and ratio <= 1.10})
    l1 = []
    for T in (80, 150):
        for kind in ("missing", "reversed"):
            cov, p = S.coverage_test(g[("latent1", T, kind, 0.2, M)])
            l1.append({"cell": f"latent1|{T}|{kind}|0.2", "cov": cov, "p": p, "ok": cov >= 0.90})
    cov_cells = c1 + c3 + l1
    rej = S.holm([x["p"] for x in cov_cells])
    R = {"C1": all(x["ok"] for x in c1), "C2": all(x["ok"] for x in c2), "C3": all(x["ok"] for x in c3),
         "L1": all(x["ok"] for x in l1)}
    R["confirmed"] = all(R.values())
    J = {"runs": [main_run, lat_run], "dry_run": a.dry_run, "C1": c1, "C2": c2, "C3": c3, "L1": l1,
         "holm_rejected": int(sum(rej)), "holm_n": len(rej), "verdict": R}
    L = [f"# Confirmatory check of tolerant_auto3 ({'DRY RUN on D-07 development rows, NOT a confirmation' if a.dry_run else 'P4-H2 confirmatory'})", "",
         f"Runs: {main_run}, {lat_run}", "",
         "- C1: " + "; ".join(f"{x['cell']} {x['cov']:.3f}" for x in c1) + f" -> {'PASS' if R['C1'] else 'FAIL'}",
         "- C2: " + "; ".join(f"T{x['T']} {x['ratio']:.3f}" for x in c2) + f" -> {'PASS' if R['C2'] else 'FAIL'}",
         "- C3: " + "; ".join(f"T{x['T']} cov {x['cov']:.3f} ratio {x['ratio']:.3f}" for x in c3) + f" -> {'PASS' if R['C3'] else 'FAIL'}",
         "- L1: " + "; ".join(f"{x['cell']} {x['cov']:.3f}" for x in l1) + f" -> {'PASS' if R['L1'] else 'FAIL'}",
         f"- Holm (alpha 0.05) over the {len(rej)} coverage cells, H0 'cov <= 0.90' rejected: {sum(rej)}/{len(rej)}",
         f"- **{'CONFIRMED' if R['confirmed'] else 'NOT CONFIRMED'}**"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "check.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
