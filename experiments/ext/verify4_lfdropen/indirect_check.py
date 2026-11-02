"""Are the top-k false pairs (opened by the floor but not truly missing) 'indirect' (sharing a node with a
truly missing pair) more often than off-skeleton non-missing pairs in general? Writes results/ext_verify4_lfdropen/indirect.json"""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results/ext_r4lfdropen_eval"
logs = {}
for l in open(R / "skeletons.jsonl"):
    s = json.loads(l)
    if s["kind"] == "missing":
        logs[(s["topology"], s["replicate"], s["rate"])] = [tuple(sorted(e["pair"])) for e in s["log"]]
out = defaultdict(lambda: defaultdict(list))
for l in open(R / "runs.jsonl"):
    r = json.loads(l)
    if r["method"] != "tolerant_v5_1_lfdr" or r["kind"] != "missing" or r["status"] != "ok":
        continue
    tr = logs[(r["topology"], r["replicate"], r["rate"])]
    trs = {"%d-%d" % e for e in tr}
    nodes = {x for e in tr for x in e}
    p = r["info_lfdr_p_data"]
    order = sorted(p, key=lambda x: p[x])
    k = int(r["info_lfdr_k_floor"])
    def touches(key):
        a, b = map(int, key.split("-"))
        return a in nodes or b in nodes
    fp = [x for x in order[:k] if x not in trs]
    base = [x for x in order if x not in trs]
    g = out[f"{r['T']}|{r['rate']}"]
    if fp:
        g["fp_touch"].append(np.mean([touches(x) for x in fp]))
    g["base_touch"].append(np.mean([touches(x) for x in base]))
    g["true_rank_median"].append(float(np.median([order.index(t) + 1 for t in trs])))
    g["true_p_median"].append(float(np.median([p[t] for t in trs])))
    g["n_fp_topk"].append(len(fp))
res = {c: {k: float(np.mean(v)) for k, v in g.items()} for c, g in sorted(out.items())}
(ROOT / "results/ext_verify4_lfdropen/indirect.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))


# Theoretical-null check: share of p < 0.10 among off-skeleton pairs that are not truly missing and touch no
# missing node (should be about 0.10 if f0 = N(0,1) is right). Appended to indirect.json under "null_check".
nc = defaultdict(list)
for l in open(R / "runs.jsonl"):
    r = json.loads(l)
    if r["method"] != "tolerant_v5_1_lfdr" or r["kind"] != "missing" or r["status"] != "ok":
        continue
    tr = logs[(r["topology"], r["replicate"], r["rate"])]
    nodes = {x for e in tr for x in e}
    trs = {"%d-%d" % e for e in tr}
    for key_, pv in r["info_lfdr_p_data"].items():
        a, b = map(int, key_.split("-"))
        if key_ not in trs and a not in nodes and b not in nodes:
            nc[f"{r['T']}|{r['rate']}"].append(pv)
res["null_check"] = {c: {"n": len(v), "share_p_lt_010": float(np.mean(np.array(v) < 0.10)),
                         "share_p_lt_001": float(np.mean(np.array(v) < 0.01))} for c, v in sorted(nc.items())}
(ROOT / "results/ext_verify4_lfdropen/indirect.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res["null_check"], indent=1))
