"""95% cluster-bootstrap CI (by topology) of tolerant_eiv2 coverage in the noise0.3 cells."""
import json
from collections import defaultdict
import numpy as np
rows = [json.loads(l) for l in open("results/ext_eiv2_eval/runs.jsonl")]
for T in (80, 150):
    for k in ("none", "missing", "reversed"):
        d = defaultdict(lambda: [0, 0])
        for r in rows:
            if r["method"] == "tolerant_eiv2" and r["scenario"] == "noise0.3" and r["T"] == T and r["kind"] == k and r["status"] == "ok":
                d[r["topology"]][0] += r["n_covered_nonnull"]; d[r["topology"]][1] += r["n_nonnull"]
        a = np.array([v[0] for v in d.values()]); b = np.array([v[1] for v in d.values()])
        idx = np.random.default_rng(0).integers(0, len(a), (4000, len(a)))
        bs = a[idx].sum(1) / b[idx].sum(1); lo, hi = np.quantile(bs, [0.025, 0.975])
        print(f"noise0.3 T{T} {k}: cov {a.sum()/b.sum():.3f} 95% CI [{lo:.3f}, {hi:.3f}] ({len(a)} topologies)")
