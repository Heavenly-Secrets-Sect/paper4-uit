"""Verifier: correct-direction rate of ng_evidence over the ng_mix law PAIRS (cause law x noise law, with skew signs),
which the candidate's unit test (same law for cause and noise) did not cover. 2-variable LiNGAM, b = 0.6."""
import sys, json, itertools
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments/ext/r4ngorient"))
from paper4.ext_r4ngorient import ng_evidence
import laws
rng = np.random.default_rng(777002)
opts = [("laplace", 1), ("t5", 1), ("skewexp", 1), ("skewexp", -1), ("uniform", 1)]
w = {("laplace", 1): .25, ("t5", 1): .25, ("skewexp", 1): .125, ("skewexp", -1): .125, ("uniform", 1): .25}
res = {}
for m in (78, 148, 400):
    tot = {"correct": 0, "wrong": 0, "gate": 0}
    for (lx, sx), (le, se) in itertools.product(opts, opts):
        c = wr = g = 0; R = 400
        for _ in range(R):
            x = laws.sample(rng, lx, m, sx); y = 0.6 * x + laws.sample(rng, le, m, se)
            ev = ng_evidence(x, y); g += ev["gate"]; c += ev["p"] > .5; wr += ev["p"] < .5
        key = f"m{m}|{lx}{'+' if sx>0 else '-'}->{le}{'+' if se>0 else '-'}"
        res[key] = {"gate": g / R, "correct": c / R, "wrong": wr / R}
        ww = w[(lx, sx)] * w[(le, se)]
        tot["correct"] += ww * c / R; tot["wrong"] += ww * wr / R; tot["gate"] += ww * g / R
    res[f"m{m}|MIX-AVERAGE"] = tot
    print(m, tot)
bad = {k: v for k, v in res.items() if "MIX" not in k and k.startswith("m400") and v["wrong"] > 0.15}
print("pairs with wrong-direction rate > 0.15 at m=400:", json.dumps(bad, indent=0))
(ROOT / "results/ext_verify4_ngorient/t2_mixpairs.json").write_text(json.dumps(res, indent=1))
