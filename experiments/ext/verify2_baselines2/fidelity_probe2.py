"""Skeptic probe 2 (verify2_baselines2), D-07H development ONLY: paired v4 (frozen factors) vs pselect_union_v2
vs psel_v2_hifi (cap 16, min_draws 100 -> ~200 draws per graph, the R2-1 spec) and its width-calibrated version
psel_v2_hifi_cal (factor tuned on the runner's D-07H calibration phase, seed offset 500000, same as for the
_cal baselines), T = 80, missing 0.2/0.5. Not an evaluation; no D-07 data touched.
Output: results/ext_verify2_baselines2/fidelity2/ and fidelity2_summary.json."""
import functools, json, multiprocessing as mp, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import ext_baselines2 as E
core_hifi = functools.partial(E._pselect_core, cap=16, min_draws=100)
def mk(name):
    return lambda data, skel, lag_max, H, n_boot, rng: E._cached("pselect_v2_hifi", core_hifi, data, skel, lag_max, H, n_boot, name)
M = ["tolerant_v4", "pselect_union_v2", "pselect_union_v2_cal", "psel_v2_hifi", "psel_v2_hifi_cal"]
CFG = {"name": "ext_verify2_baselines2/fidelity2", "purpose": "skeptic D-07H probe (verify2_baselines2)", "T": [80],
       "damage": {"kinds": ["missing"], "rates": [0.2, 0.5]}, "methods": M, "paired_references": ["tolerant_v4"],
       "calibrate_methods": ["pselect_union_v2_cal", "psel_v2_hifi_cal"],
       "frozen_calibration": "experiments/calibration/tolerant_v4_frozen.json",
       "calibration": {"bank": "D-07H", "split": "development", "max_topologies": None, "replicates": 1,
                       "kinds": ["missing"], "rates": [0.2, 0.5]},
       "bank": "D-07H", "split": "development", "max_topologies": None, "replicates": 1, "H": 4, "n_boot": 199,
       "tau_effect": 0.1, "generator": json.load(open(ROOT / "experiments/configs/ext_baselines2_eval.json"))["generator"],
       "seed_base": 20261102}
def summarize():
    out = ROOT / "results" / CFG["name"]
    rows = [json.loads(l) for l in open(out / "runs.jsonl")]
    res = {"calibration": {k: v for k, v in json.load(open(out / "calibration.json")).items() if "psel" in k and "|80|" in k}}
    for rate in (0.2, 0.5):
        g = {m: {r["topology"]: r for r in rows if r["kind"] == "missing" and r["rate"] == rate and r["method"] == m and r["status"] == "ok"} for m in M}
        common = sorted(set.intersection(*[set(v) for v in g.values()]))
        cell = {m: {"cov": sum(g[m][t]["n_covered_nonnull"] for t in common) / sum(g[m][t]["n_nonnull"] for t in common),
                    "IS": float(np.mean([g[m][t]["iscore_nonnull_mean"] for t in common]))} for m in M}
        for m in M[1:]:
            d = np.array([g["tolerant_v4"][t]["iscore_nonnull_mean"] - g[m][t]["iscore_nonnull_mean"] for t in common])
            rng = np.random.default_rng(13); bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)])
            cell[f"v4_minus_{m}"] = {"est": float(d.mean()), "lo": float(np.quantile(bs, .025)), "hi": float(np.quantile(bs, .975)), "n_topologies": len(common)}
        res[f"80|missing|{rate}"] = cell
    (ROOT / "results/ext_verify2_baselines2/fidelity2_summary.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    if "--summarize" not in sys.argv:
        ext = dict(R.ext_methods()); ext["psel_v2_hifi"] = mk("psel_v2_hifi"); ext["psel_v2_hifi_cal"] = mk("psel_v2_hifi_cal"); R._EXT = ext
        cfgp = ROOT / "experiments/ext/verify2_baselines2/fidelity2_cfg.json"; cfgp.write_text(json.dumps(CFG, indent=1))
        R.main(["--config", str(cfgp), "--workers", "2"])
    summarize()
