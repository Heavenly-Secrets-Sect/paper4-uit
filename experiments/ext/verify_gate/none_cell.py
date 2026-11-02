"""verify_gate: paired IS difference auto3 - baseline on the undamaged cell (omitted by vs_baselines.py)."""
import json
from collections import defaultdict
import numpy as np
def load(n): return [json.loads(l) for l in open(f"results/{n}/runs.jsonl")]
key=lambda r:(r["topology"],r["replicate"],r["T"],r["kind"],r["rate"])
idx=defaultdict(dict)
for r in load("ext_gate_auto3")+load("a2_baselines")+[r for r in load("a2b_pselect") if r["method"]=="pselect_union"]:
    if r["status"]=="ok" and r.get("scenario","clean")=="clean": idx[key(r)].setdefault(r["method"],r)
rng=np.random.default_rng(0)
for kind,rate in [("none",0.0),("extra",0.2),("extra",0.5)]:
  for T in (40,80,150):
    ks=[k for k in idx if k[2]==T and k[3]==kind and k[4]==rate and "tolerant_auto3" in idx[k]]
    out=[]
    for b in ("plugin","ida_union","bvar_minnesota","pselect_union"):
        d=defaultdict(list)
        for k in ks:
            if b in idx[k]: d[k[0]].append(idx[k]["tolerant_auto3"]["iscore_nonnull_mean"]-idx[k][b]["iscore_nonnull_mean"])
        t=list(d); est=np.mean([v for x in t for v in d[x]])
        bs=[np.mean([v for i in rng.choice(len(t),len(t)) for v in d[t[i]]]) for _ in range(1000)]
        lo,hi=np.quantile(bs,(0.025,0.975)); out.append(f"{b} {est:+.2f} [{lo:+.2f},{hi:+.2f}]")
    print(kind,rate,T," | ".join(out))
