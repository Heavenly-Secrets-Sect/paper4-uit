"""Paired comparison of tolerant_auto3 (results/ext_gate_auto3) with the published baselines of
results/a2_baselines and results/a2b_pselect (same seeds; rows are matched by topology, replicate,
T, kind, rate, and checked through the identical plugin rows). 95% CI resamples topologies."""
import json, sys
from collections import defaultdict
import numpy as np
R = "results/"
def load(name):
    return [json.loads(l) for l in open(R + name + "/runs.jsonl")]
mine = load("ext_gate_auto3"); base = load("a2_baselines") + [r for r in load("a2b_pselect") if r["method"] == "pselect_union"]
key = lambda r: (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
idx = defaultdict(dict)
for r in mine + base:
    if r["status"] == "ok" and r.get("scenario", "clean") == "clean":
        idx[key(r)].setdefault(r["method"], r)
# pairing check: plugin interval score must be identical in both runs
p_m = {key(r): r["iscore_nonnull_mean"] for r in mine if r["method"] == "plugin"}
p_b = {key(r): r["iscore_nonnull_mean"] for r in load("a2_baselines") if r["method"] == "plugin"}
common = set(p_m) & set(p_b)
print("pairing check: plugin rows identical in", sum(abs(p_m[k] - p_b[k]) < 1e-9 for k in common), "of", len(common))
rng = np.random.default_rng(0)
print("| T | cell | auto3 cov/IS | " + " | ".join(f"vs {b}" for b in ("ida_union", "bvar_minnesota", "pselect_union")) + " |")
print("|---|---|---|---|---|---|")
for T in (40, 80, 150):
    for kind, rate in [("missing", 0.2), ("missing", 0.5), ("reversed", 0.2), ("reversed", 0.5), ("extra", 0.2), ("extra", 0.5)]:
        ks = [k for k in idx if k[2] == T and k[3] == kind and k[4] == rate and "tolerant_auto3" in idx[k]]
        a = [idx[k]["tolerant_auto3"] for k in ks]
        cov = sum(r["n_covered_nonnull"] for r in a) / sum(r["n_nonnull"] for r in a)
        out = []
        for b in ("ida_union", "bvar_minnesota", "pselect_union"):
            d = defaultdict(list)
            for k in ks:
                if b in idx[k]:
                    d[k[0]].append(idx[k]["tolerant_auto3"]["iscore_nonnull_mean"] - idx[k][b]["iscore_nonnull_mean"])
            topos = list(d)
            est = np.mean([v for t in topos for v in d[t]])
            boots = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in d[topos[i]]]) for _ in range(1000)]
            lo, hi = np.quantile(boots, (0.025, 0.975))
            out.append(f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}]")
        print(f"| {T} | {kind} {rate} | {cov:.3f}/{np.mean([r['iscore_nonnull_mean'] for r in a]):.2f} | " + " | ".join(out) + " |")
