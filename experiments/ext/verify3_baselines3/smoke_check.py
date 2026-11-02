import json, sys
from collections import Counter
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/baselines3")
import analyze_p4h2 as P
R = "/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_verify3_baselines3/"
out = {}
a = [json.loads(l) for l in open(R + "smoke/runs.jsonl")]
b = [json.loads(l) for l in open(R + "smoke_clt/runs.jsonl")]
out["n_rows"] = [len(a), len(b)]
out["status"] = dict(Counter((r["method"], r["status"]) for r in a).most_common())
out["status"] = {f"{k[0]}|{k[1]}": v for k, v in out["status"].items()}
key = lambda r: (r["method"], r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
bi = {key(r): r for r in b}
mism = []
for r in a:
    s = bi[key(r)]
    if r["status"] != s["status"] or (r["status"] == "ok" and (abs(r["iscore_nonnull_mean"] - s["iscore_nonnull_mean"]) > 1e-9 or r["n_covered_nonnull"] != s["n_covered_nonnull"])):
        mism.append([str(key(r)), r.get("iscore_nonnull_mean"), s.get("iscore_nonnull_mean")])
out["interp_mismatches_miniconda_vs_clt"] = mism
cfg = json.load(open("/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/verify3_baselines3/smoke_d07h.json"))
frozen = json.load(open("/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/baselines3/frozen_calibration_p7.json"))
man = json.load(open(R + "smoke/baselines3_manifest.json"))
out["validity_problems_expected_only_rowcounts"] = P.validity(a, cfg, man, frozen, expect_bank=False)
out["manifest_method_modules"] = man["method_modules"]
out["cT_rows"] = sorted({(r["method"], r["T"], r.get("info_c_T")) for r in a if r.get("info_c_T") is not None})
out["cT_rows"] = [list(x) for x in out["cT_rows"]]
json.dump(out, open(R + "smoke_check.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:4000])
