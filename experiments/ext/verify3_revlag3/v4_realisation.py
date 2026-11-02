"""Verifier: does the pair-runner v4 realisation equal the main-runner v4 realisation (claim of the
P3/P4 spec draft, check 5)? Same logic as analyze_flag_p4h2_v2.py consistency block, on D-07 dev."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag3"))
from flag3 import load3
res = {}
for run, ref in (("ext_revlag_lag", "ext_v51_eval"), ("ext_revlag_lag", "a2_baselines"), ("ext_verify3_revlag3/rev_invalid_copy", "ext_v51_eval")):
    p = ROOT / "results" / ref / "runs.jsonl"
    if not p.exists():
        print(ref, "missing"); continue
    man = json.loads((ROOT / "results" / run / "manifest.json").read_text())
    ids = [t["id"] for t in man["topologies"]] if "topologies" in man else None
    rows = load3(run, "tolerant_v4", encoding="train")
    theirs = {}
    for line in open(p):
        x = json.loads(line)
        if x["method"] == "tolerant_v4" and x["status"] == "ok" and x.get("scenario", "clean") == "clean":
            theirs[(x["topology"], x["replicate"], x["T"], x["kind"], float(x["rate"]))] = (x["n_covered_nonnull"], x["n_nonnull"])
    if ids is None:
        ids = sorted({k[0] for k in theirs})
    cells = rows["cells"]; mine = {}
    cov = (rows["lo"] <= rows["C_t"]) & (rows["C_t"] <= rows["hi"])
    for t, rp, T, c, cv in zip(rows["topo"].astype(int), rows["rep"].astype(int), rows["T"].astype(int), rows["cell"].astype(int), cov):
        k, rt = cells[c].split("|"); key = (ids[t], rp, T, k, float(rt))
        mine.setdefault(key, [0, 0]); mine[key][0] += int(cv); mine[key][1] += 1
    common = set(mine) & set(theirs)
    nd = sum(tuple(mine[k]) != tuple(theirs[k]) for k in common)
    res[f"{run} vs {ref}"] = dict(n_mine=len(mine), n_theirs=len(theirs), n_common=len(common), n_diff=nd, ids_from_manifest="topologies" in man)
    print(run, ref, res[f"{run} vs {ref}"])
json.dump(res, open(ROOT / "results/ext_verify3_revlag3/v4_realisation.json", "w"), indent=1)
