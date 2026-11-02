"""Width-factor confound in the hetero eiv2 - eiv paired comparison (noise0.3)."""
import json
from collections import defaultdict
import numpy as np
h = [json.loads(l) for l in open("results/ext_eiv2_hetero/runs.jsonl")]
cal = json.load(open("results/ext_eiv2_hetero/calibration.json"))
g = defaultdict(list)
for r in h: g[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)
print("# noise0.3: width factor eiv / eiv2, mean width_kept eiv / eiv2, mean r_hat eiv / eiv2")
for T in (80, 150):
    for k in ("none", "missing", "reversed"):
        w = [np.mean([r["width_kept"] for r in g[("noise0.3", T, k, m)] if r["status"] == "ok"]) for m in ("tolerant_eiv", "tolerant_eiv2")]
        f = [cal[f"{m}|{T}|{k}"] for m in ("tolerant_eiv", "tolerant_eiv2")]
        print(f"  T{T} {k}: factor {f[0]} / {f[1]}; width {w[0]:.3f} / {w[1]:.3f} (ratio {w[1]/w[0]:.3f}); width/factor ratio {(w[1]/f[1])/(w[0]/f[0]):.3f}")
