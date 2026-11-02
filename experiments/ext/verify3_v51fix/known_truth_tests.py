"""Known-truth tests of rule_p4h2_v2.py (verify3_v51fix). Modifies copies of results/ext_v51_eval in scratch."""
import json, shutil, subprocess, sys, copy
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "results/ext_v51_eval"
SCR = Path(sys.argv[1]); OUTR = ROOT / "results/ext_verify3_v51fix/known_truth"
OUTR.mkdir(parents=True, exist_ok=True)
base = [json.loads(l) for l in open(SRC / "runs.jsonl")]
def run(name, rows, expect):
    d = SCR / name / "ext_v51_eval"; d.mkdir(parents=True, exist_ok=True)
    for f in ("manifest.json", "calibration.json"): shutil.copy(SRC / f, d / f)
    with open(d / "runs.jsonl", "w") as fh:
        for r in rows: fh.write(json.dumps(r) + "\n")
    p = subprocess.run([sys.executable, str(ROOT / "experiments/ext/v51fix/rule_p4h2_v2.py"), "--dev-dryrun",
                        "--results-root", str(SCR / name), "--out-dir", str(OUTR / name)], capture_output=True, text=True)
    if p.returncode != 0:
        return {"test": name, "expect": expect, "got": "CRASH", "err": p.stderr[-400:]}
    j = json.loads((OUTR / name / "ruling_v2.json").read_text())
    return {"test": name, "expect": expect, "got": j["verdict"], "C1": j["C1"], "C2": j["C2"], "C3": j["C3"], "valid": j["valid"],
            "fail_total_ok": j["fail_total_ok"]}
def cellsel(r, m, T, k, rt): return r["method"] == m and r["T"] == T and r["kind"] == k and r["rate"] == rt
def mean_is(rows, m, T, k, rt): return np.mean([r["iscore_nonnull_mean"] for r in rows if cellsel(r, m, T, k, rt) and r["status"] == "ok"])
res = []
# 1. C2 IS ratio boundary at T80 extra-0.2: scale v5_1 IS to exactly 1.049 and 1.051 x v4
for target, exp in ((1.049, "CONFIRMED"), (1.051, "NOT CONFIRMED")):
    rows = copy.deepcopy(base)
    v4 = mean_is(rows, "tolerant_v4", 80, "extra", 0.2); v5 = mean_is(rows, "tolerant_v5_1", 80, "extra", 0.2)
    f = target * v4 / v5
    for r in rows:
        if cellsel(r, "tolerant_v5_1", 80, "extra", 0.2): r["iscore_nonnull_mean"] *= f
    res.append(run(f"is_ratio_{target}", rows, exp))
# 2. Coverage boundary T150 missing-0.5: reduce n_covered so pooled cov just below/above 0.90
for target, exp in ((0.901, "CONFIRMED"), (0.899, "NOT CONFIRMED")):
    rows = copy.deepcopy(base)
    g = [r for r in rows if cellsel(r, "tolerant_v5_1", 150, "missing", 0.5)]
    den = sum(r["n_nonnull"] for r in g); need = int(np.ceil(target * den)) if target > 0.9 else int(np.floor(target * den))
    cur = sum(r["n_covered_nonnull"] for r in g); drop = cur - need
    for r in g:
        x = min(drop, r["n_covered_nonnull"]); r["n_covered_nonnull"] -= x; drop -= x
        if drop == 0: break
    res.append(run(f"cov_{target}", rows, exp))
# 3. C1: shift v5_1 IS at T40 missing-0.2 by +2.6 per run (true mean diff ~ +0.46 > 0) -> NOT CONFIRMED
rows = copy.deepcopy(base)
for r in rows:
    if cellsel(r, "tolerant_v5_1", 40, "missing", 0.2): r["iscore_nonnull_mean"] += 2.6
res.append(run("c1_shift", rows, "NOT CONFIRMED"))
# 4. Overall failure ceiling: 12 failed v5_1 runs (spread 1 per cell, cells with margin) -> pass; 13 -> fail
allc = sorted({(r["T"], r["kind"], r["rate"]) for r in base})
for nfail, exp in ((12, "CONFIRMED?"), (13, "NOT CONFIRMED")):
    rows = copy.deepcopy(base); done = 0
    for c in allc:
        if c in ((40, "missing", 0.2),): continue
        for r in rows:
            if cellsel(r, "tolerant_v5_1", *c) and r["status"] == "ok" and done < nfail:
                keep = {k: r[k] for k in ("method", "topology", "profile", "replicate", "T", "kind", "rate", "k", "scenario")}
                r.clear(); r.update(keep); r["status"] = "failed"; done += 1
                break
    res.append(run(f"fail_total_{nfail}", rows, exp))
# 5. ITT by hand: fail 3 runs at T80 reversed-0.5 and compare analyzer cov_itt with hand computation
rows = copy.deepcopy(base)
g = [r for r in rows if cellsel(r, "tolerant_v5_1", 80, "reversed", 0.5)][:3]
nn = {(r["topology"], r["replicate"]): r["n_nonnull"] for r in base if r["status"] == "ok"}
for r in g:
    keep = {k: r[k] for k in ("method", "topology", "profile", "replicate", "T", "kind", "rate", "k", "scenario")}
    r.clear(); r.update(keep); r["status"] = "failed"
gg = [r for r in rows if cellsel(r, "tolerant_v5_1", 80, "reversed", 0.5)]
hand = sum(r.get("n_covered_nonnull", 0) for r in gg) / sum(nn[(r["topology"], r["replicate"])] for r in gg)
out = run("itt_three", rows, "depends")
j = json.loads((OUTR / "itt_three" / "ruling_v2.json").read_text())
out["hand_cov_itt"] = hand; out["analyzer_cov_itt"] = j["cells"]["C2|(80, 'reversed', 0.5)"]["v51"]["cov_itt"]
res.append(out)
(OUTR / "summary.json").write_text(json.dumps(res, indent=1))
for x in res: print(x)
