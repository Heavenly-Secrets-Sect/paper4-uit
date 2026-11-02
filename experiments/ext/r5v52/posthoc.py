"""Post hoc, descriptive only (written after the ruling): tolerant_v5_2 vs component B's tolerant_v5_1_hs2 on the same
P2 runs (both ok, mean-IS ratio, no test), and the T19-missing tail of v5_2.
Writes results/ext_r5v52_analysis/posthoc.json."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
v = [json.loads(l) for l in open(R / "ext_r5v52_p2/runs.jsonl")]
b = [json.loads(l) for l in open(R / "ext_r5hubscreen2_p2/runs.jsonl")]
hs = {(x["topology"], x["replicate"], x["T"], x["kind"]): x for x in b if x["method"] == "tolerant_v5_1_hs2"}
out = {"v52_vs_hs2_p2": {}}
for T in (19, 25, 30, 35):
    for k in ("missing", "reversed", "extra"):
        pr = [(x["iscore_nonnull_mean"], hs[(x["topology"], x["replicate"], T, k)]["iscore_nonnull_mean"])
              for x in v if x["method"] == "tolerant_v5_2" and x["T"] == T and x["kind"] == k and x["status"] == "ok"
              and hs[(x["topology"], x["replicate"], T, k)]["status"] == "ok"]
        a = np.array(pr)
        out["v52_vs_hs2_p2"][f"{T}|{k}"] = {"n": len(a), "mean_v52": float(a[:, 0].mean()), "mean_hs2": float(a[:, 1].mean()),
                                           "ratio": float(a[:, 0].mean() / a[:, 1].mean())}
t = sorted(x["iscore_nonnull_mean"] for x in v if x["method"] == "tolerant_v5_2" and x["T"] == 19 and x["kind"] == "missing")
out["T19_missing_v52"] = {"top3": t[-3:], "mean": float(np.mean(t)), "mean_without_top3": float(np.mean(t[:-3])),
                          "median": float(np.median(t))}
(R / "ext_r5v52_analysis/posthoc.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
