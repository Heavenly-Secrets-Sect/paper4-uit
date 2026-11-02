"""FROZEN, NOT RUN on P4-H2. Corrected confirmatory check of the frozen RQ4.4 flag (spec P3 of
synthesis_round2.md, corrected by revlag3; docs/ext/revlag3.md, "Frozen spec P4-H2 (sửa P3/P4)").

Differences from experiments/ext/revlag/analyze_flag_p4h2.py (kept unchanged):
1. The stated kind is encoded as when the flag was trained (cell kind = public damage["kind"]),
   read from the ``stated_kind`` column written by experiments/ext/revlag3/run_pairs3.py.
   The round-2 encoding (width_key) is reported as a sensitivity line, not ruled.
2. Failed runs: tolerant_v4 runs with status != ok are counted per T set from nullpairs.jsonl;
   if their share exceeds 0.05 in either T set the verdict is NOT CONFIRMED (cannot evaluate).
3. The run's manifest must show frozen_calibration_sha256 = the pinned tolerant_v4_frozen.json hash
   and tolerant_v4 / tolerant_v4L as built-in (run_pairs3), else the script stops.
4. 1/width is reported as a descriptive comparator (lead's note on P3); it does not enter the rule.
5. Descriptive consistency check: when results/ext_v51_p4h2/runs.jsonl exists, the per-run
   (covered, non-null) counts of tolerant_v4 are compared with it (same seeds, same cell positions:
   the same v4 realisation, see bug E1 in synthesis_round2.md section 6).

Rule (unchanged from revlag.md, Spec 2): F1 T80/150 AUROC(p_hat) CI lo > 0.65; F2 T80/150
AUROC(p_hat) - AUROC(rel_width) CI lo > 0; F3 T40 AUROC CI lo > 0.65; F4 (T80/150 and T40 each)
flagged share <= 0.5, miss-rate ratio >= 2, ratio CI lo > 1. CONFIRMED iff all five hold.
Topology-cluster bootstrap over the run's topologies, 2000 resamples, seed 20261103.

Run:  python experiments/ext/revlag3/analyze_flag_p4h2_v2.py --run ext_revlag3_p4h2
Writes results/<run>/flag_confirm_v2.{md,json}.
"""
import argparse, hashlib, json, sys
from collections import Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from flag3 import HDR, evaluate3, fmt3, load3  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_flag import FROZEN_SHA, holm  # noqa: E402

V4_FROZEN_SHA = "9b630cab6b664c92c9e3098d5852a2260de039f5cb49c7b1dd2a482c3119b122"
MAX_FAIL = 0.05


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="ext_revlag3_p4h2"); a = ap.parse_args()
    fpath = ROOT / "experiments/ext/revlag/frozen_flag.json"
    assert hashlib.sha256(fpath.read_bytes()).hexdigest() == FROZEN_SHA, "frozen flag changed"
    frozen = json.loads(fpath.read_text())
    out = ROOT / "results" / a.run
    man = json.loads((out / "manifest.json").read_text())
    assert man["frozen_calibration_sha256"] == V4_FROZEN_SHA, "frozen calibration of the run is not the pinned file"
    assert man["method_modules"].get("tolerant_v4") == "built-in", "tolerant_v4 not built-in"
    nl = [json.loads(x) for x in open(out / "nullpairs.jsonl")]
    v4 = [r for r in nl if r["method"] == "tolerant_v4"]
    fail = {}
    for lab, f in (("T80/150", lambda T: T >= 80), ("T40", lambda T: T == 40)):
        rs = [r for r in v4 if f(r["T"])]
        fail[lab] = dict(n_runs=len(rs), n_failed=sum(r["status"] != "ok" for r in rs),
                         statuses=dict(Counter(r["status"] for r in rs if r["status"] != "ok")))
        fail[lab]["share"] = fail[lab]["n_failed"] / max(len(rs), 1)
    fail_ok = all(v["share"] <= MAX_FAIL and v["n_runs"] > 0 for v in fail.values())
    rows = load3(a.run, "tolerant_v4", encoding="train")
    e1 = evaluate3(rows, rows["T"] >= 80, frozen, "T80/150 (7 cell)")
    e3 = evaluate3(rows, rows["T"] == 40, frozen, "T40 (7 cell)")
    F = {"F1": e1["auc_p_ci"][0] > 0.65, "F2": e1["d_auc_ci"][0] > 0, "F3": e3["auc_p_ci"][0] > 0.65,
         "F4_T80_150": e1["share"] <= 0.5 and e1["ratio"] >= 2 and e1["ratio_ci"][0] > 1,
         "F4_T40": e3["share"] <= 0.5 and e3["ratio"] >= 2 and e3["ratio_ci"][0] > 1}
    ps = [e1["p_auc_le_065"], e1["p_d_le0"], e3["p_auc_le_065"], e1["p_ratio_le1"], e3["p_ratio_le1"]]
    ph = [float(x) for x in holm(ps)]
    if not fail_ok:
        verdict = "NOT CONFIRMED (failed tolerant_v4 runs above 5% or no runs)"
    else:
        verdict = "CONFIRMED" if all(F.values()) else "NOT CONFIRMED"
    r2 = load3(a.run, "tolerant_v4", encoding="round2")
    s1 = evaluate3(r2, r2["T"] >= 80, frozen, "sensitivity: round-2 encoding, T80/150")
    s3 = evaluate3(r2, r2["T"] == 40, frozen, "sensitivity: round-2 encoding, T40")
    cons = None
    ref = ROOT / "results/ext_v51_p4h2/runs.jsonl"
    if ref.exists():
        theirs = {}
        for line in open(ref):
            x = json.loads(line)
            if x["method"] == "tolerant_v4" and x["status"] == "ok":
                theirs[(x["topology"], x["replicate"], x["T"], x["kind"], float(x["rate"]))] = (x["n_covered_nonnull"], x["n_nonnull"])
        cells = rows["cells"]; ids = [t["id"] for t in man["topologies"]]
        mine = {}
        cov = (rows["lo"] <= rows["C_t"]) & (rows["C_t"] <= rows["hi"])
        for t, rp, T, c, cv in zip(rows["topo"].astype(int), rows["rep"].astype(int), rows["T"].astype(int), rows["cell"].astype(int), cov):
            k, rt = cells[c].split("|"); key = (ids[t], rp, T, k, float(rt))
            mine.setdefault(key, [0, 0]); mine[key][0] += int(cv); mine[key][1] += 1
        common = set(mine) & set(theirs)
        cons = dict(n_common=len(common), n_diff=sum(tuple(mine[k]) != tuple(theirs[k]) for k in common))
    L = [f"# Frozen RQ4.4 flag, corrected confirmatory check (v2) on {a.run}", "",
         f"Failed tolerant_v4 runs: {fail} -> {'ok' if fail_ok else 'ABOVE CAP'}", ""] + HDR + \
        [fmt3(e1), fmt3(e3), "", "Sensitivity (round-2 encoding of stated, not ruled):", ""] + HDR + [fmt3(s1), fmt3(s3), ""] + \
        [f"- {k}: {v}" for k, v in F.items()] + \
        [f"- one-sided p {[round(p, 4) for p in ps]}; Holm (5) {[round(p, 4) for p in ph]}; "
         f"conditions with Holm p < 0.05: {sum(p < 0.05 for p in ph)}/5",
         f"- 1/width (descriptive): T80/150 AUROC {e1['auc_inv']:.3f}, p_hat − 1/width {e1['d_inv']:+.3f} "
         f"[{e1['d_inv_ci'][0]:+.3f}, {e1['d_inv_ci'][1]:+.3f}]; T40 AUROC {e3['auc_inv']:.3f}, p_hat − 1/width "
         f"{e3['d_inv']:+.3f} [{e3['d_inv_ci'][0]:+.3f}, {e3['d_inv_ci'][1]:+.3f}]",
         f"- v4 realisation vs ext_v51_p4h2 (descriptive): {cons}", "", f"**Verdict: {verdict}**"]
    (out / "flag_confirm_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "flag_confirm_v2.json").write_text(json.dumps(
        {"rule": F, "p": ps, "p_holm": ph, "failures": fail, "failures_ok": fail_ok, "verdict": verdict,
         "T80_150": e1, "T40": e3, "sensitivity_round2_encoding": [s1, s3], "v4_vs_v51_p4h2": cons},
        indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
