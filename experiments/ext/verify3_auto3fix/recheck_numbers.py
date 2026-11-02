"""Skeptic recheck (verify3_auto3fix): fragility P(CONFIRMED) re-derived, and independent pooled coverage
from raw rows of the D-07 dry-run runs (no analyzer code for the coverage part)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/auto3fix"))
import check_p4h2_v2 as C
out = {}
A = C.build(C.Run(ROOT / "results/ext_gate_auto3"), C.Run(ROOT / "results/ext_auto5_a1"))
rng = np.random.default_rng(0); nt = 20; conf = 0
for _ in range(2000):
    conf += C.evaluate(A, rng.integers(0, nt, nt))["rule_holds"]
out["fragility_p_confirmed_seed0"] = conf / 2000
for seed in (1, 2, 3):
    rng = np.random.default_rng(seed); c = 0
    for _ in range(2000):
        c += C.evaluate(A, rng.integers(0, nt, nt))["rule_holds"]
    out[f"fragility_p_confirmed_seed{seed}"] = c / 2000
# independent pooled coverage / IS ratios from raw rows
def rows(p):
    return [json.loads(l) for l in open(ROOT / p / "runs.jsonl")]
g, a = rows("results/ext_gate_auto3"), rows("results/ext_auto5_a1")
cov = defaultdict(lambda: [0, 0]); IS = defaultdict(list)
for src, rr in (("main", g), ("lat", a)):
    for r in rr:
        if r["status"] != "ok": continue
        key = (src, r.get("scenario", "clean"), r["T"], r["kind"], r["rate"], r["method"])
        cov[key][0] += r["n_covered_nonnull"]; cov[key][1] += r["n_nonnull"]
        IS[key].append(r["iscore_nonnull_mean"])
res = {}
for T in (80, 150):
    for k in ("missing", "reversed"):
        for rt in (0.2, 0.5):
            x = cov[("main", "clean", T, k, rt, "tolerant_auto3")]; res[f"C1 {T} {k} {rt}"] = round(x[0] / x[1], 4)
        x = cov[("lat", "latent1", T, k, 0.2, "tolerant_auto3")]; res[f"L1 {T} {k}"] = round(x[0] / x[1], 4)
for T in (40, 80, 150):
    res[f"C2 {T}"] = round(np.mean(IS[("main", "clean", T, "none", 0.0, "tolerant_auto3")]) / np.mean(IS[("main", "clean", T, "none", 0.0, "tolerant_v4")]), 4)
for T in (80, 150):
    x = cov[("main", "clean", T, "ges", 0.0, "tolerant_auto3")]
    res[f"C3 {T} cov"] = round(x[0] / x[1], 4)
    res[f"C3 {T} ratio"] = round(np.mean(IS[("main", "clean", T, "ges", 0.0, "tolerant_auto3")]) / np.mean(IS[("main", "clean", T, "ges", 0.0, "tolerant_v4")]), 4)
    res[f"C3 {T} n_v4_ok"] = len(IS[("main", "clean", T, "ges", 0.0, "tolerant_v4")])
out["independent_d07"] = res
od = ROOT / "results/ext_verify3_auto3fix"; od.mkdir(parents=True, exist_ok=True)
(od / "recheck_numbers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
