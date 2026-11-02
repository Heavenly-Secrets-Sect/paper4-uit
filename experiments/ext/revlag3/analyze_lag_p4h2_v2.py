"""FROZEN, NOT RUN on P4-H2. Corrected confirmatory check of tolerant_v4L lag reporting (spec P4 of
synthesis_round2.md, corrected by revlag3). Rule L1 + L2 exactly as experiments/ext/revlag/analyze_lag.py
part (b) (imported unchanged; sha256 pinned); additions:
1. Manifest checks: frozen_calibration_sha256 = pinned tolerant_v4_frozen.json; tolerant_v4 and
   tolerant_v4L built-in (run_pairs3; tolerant_v4L widened through ext_revlag.frozen_factor, whose
   file run_pairs3 asserted to carry the same mod|* factors).
2. Failed runs: tolerant_v4 or tolerant_v4L runs with status != ok are counted in the four L1 cells
   (reversed-0.2/0.5 x T80/150) and over all 21 cells; if the failed share exceeds 0.05 in any L1
   cell, or over the 21 cells, the verdict is NOT CONFIRMED (cannot evaluate). Pairs of failed runs
   drop out of the paired comparison (inner join), as in round 2.
CONFIRMED iff L1 (4/4 cells: CI lo > 0 and Holm p < 0.05 over 4) and L2 (0/21 cells worse on (i),
(ii), (iii)) and the failure cap holds.
Run:  python experiments/ext/revlag3/analyze_lag_p4h2_v2.py --run ext_revlag3_p4h2
Writes results/<run>/analysis_b.md (by analyze_lag.part_b), lag_confirm_v2.{md,json}.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_lag import Boot, load, part_b  # noqa: E402

V4_FROZEN_SHA = "9b630cab6b664c92c9e3098d5852a2260de039f5cb49c7b1dd2a482c3119b122"
MAX_FAIL = 0.05


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="ext_revlag3_p4h2"); a = ap.parse_args()
    out = ROOT / "results" / a.run
    man = json.loads((out / "manifest.json").read_text())
    assert man["frozen_calibration_sha256"] == V4_FROZEN_SHA, "frozen calibration of the run is not the pinned file"
    for m in ("tolerant_v4", "tolerant_v4L"):
        assert man["method_modules"].get(m) == "built-in", f"{m} not built-in"
    df, methods, cells = load(a.run)
    nl = [json.loads(x) for x in open(out / "nullpairs.jsonl")]
    nl = [r for r in nl if r["method"] in ("tolerant_v4", "tolerant_v4L")]
    fail = {}
    for cname in ("reversed|0.2", "reversed|0.5"):
        c = cells.index(cname)
        for T in (80, 150):
            rs = [r for r in nl if r["cell"] == c and r["T"] == T]
            fail[f"{cname} T{T}"] = dict(n=len(rs), failed=sum(r["status"] != "ok" for r in rs))
    fail["all 21 cells"] = dict(n=len(nl), failed=sum(r["status"] != "ok" for r in nl))
    for v in fail.values():
        v["share"] = v["failed"] / max(v["n"], 1)
    fail_ok = all(v["share"] <= MAX_FAIL and v["n"] > 0 for v in fail.values())
    res = part_b(df, Boot(df.topo.unique()), out, cells)
    if not fail_ok:
        verdict = "NOT CONFIRMED (failed runs above 5% or no runs)"
    else:
        verdict = "CONFIRMED" if (res["L1_pass"] and res["L2_pass"]) else "NOT CONFIRMED"
    L = [f"# tolerant_v4L lag reporting, corrected confirmatory check (v2) on {a.run}", "",
         f"Failed runs (tolerant_v4, tolerant_v4L): {fail} -> {'ok' if fail_ok else 'ABOVE CAP'}",
         f"L1: {res['L1_n']}/4 cells pass -> {res['L1_pass']}; L2 worse counts {res['L2_counts']} -> {res['L2_pass']}",
         "Details: analysis_b.md (analyze_lag.part_b, unchanged).", "", f"**Verdict: {verdict}**"]
    (out / "lag_confirm_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "lag_confirm_v2.json").write_text(json.dumps({"failures": fail, "failures_ok": fail_ok, "L1_n": res["L1_n"],
        "L1_pass": res["L1_pass"], "L2_pass": res["L2_pass"], "L2_counts": res["L2_counts"], "verdict": verdict},
        indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
