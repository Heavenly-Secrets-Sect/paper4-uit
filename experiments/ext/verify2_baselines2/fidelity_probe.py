"""Skeptic probe (verify2_baselines2), D-07H development ONLY: does the reduced bootstrap/graph budget of
pselect_union_v2 (cap 4 graphs, >= 40 draws per orientation member, ~80 draws per graph) matter, compared with
the R2-1 spec of >= 199 draws per graph and round-1's 16 graphs?  Variant psel_v2_hifi = same core with
cap = 16 and min_draws = 100 (2 members per graph -> ~200 draws per graph). Raw (uncalibrated) intervals.
Runs the unmodified runner (fork; the variant is injected into the runner's ext registry in-process only).
Output: results/ext_verify2_baselines2/fidelity/ (runner) and fidelity_summary.json."""
import functools, json, multiprocessing as mp, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import ext_baselines2 as E

core_hifi = functools.partial(E._pselect_core, cap=16, min_draws=100)
def psel_v2_hifi(data, skel, lag_max, H, n_boot, rng):
    return E._cached("pselect_v2_hifi", core_hifi, data, skel, lag_max, H, n_boot, "psel_v2_hifi")

CFG = {"name": "ext_verify2_baselines2/fidelity", "T": [80], "damage": {"kinds": ["missing"], "rates": [0.2, 0.5]},
       "methods": ["pselect_union_v2", "psel_v2_hifi"], "paired_references": ["pselect_union_v2"],
       "bank": "D-07H", "split": "development", "max_topologies": None, "replicates": 1, "H": 4, "n_boot": 199,
       "tau_effect": 0.1, "generator": json.load(open(ROOT / "experiments/configs/ext_baselines2_eval.json"))["generator"],
       "seed_base": 20261102}

def summarize():
    out = ROOT / "results" / CFG["name"]
    rows = [json.loads(l) for l in open(out / "runs.jsonl")]
    res = {}
    for kind, rate in (("none", 0.0), ("missing", 0.2), ("missing", 0.5)):
        g = {m: {r["topology"]: r for r in rows if r["kind"] == kind and r["rate"] == rate and r["method"] == m and r["status"] == "ok"}
             for m in CFG["methods"]}
        common = sorted(set(g["pselect_union_v2"]) & set(g["psel_v2_hifi"]))
        d = np.array([g["psel_v2_hifi"][t]["iscore_nonnull_mean"] - g["pselect_union_v2"][t]["iscore_nonnull_mean"] for t in common])
        rng = np.random.default_rng(11); bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)]
        res[f"80|{kind}|{rate}"] = {
            m: {"cov": sum(g[m][t]["n_covered_nonnull"] for t in common) / sum(g[m][t]["n_nonnull"] for t in common),
                "IS": float(np.mean([g[m][t]["iscore_nonnull_mean"] for t in common])),
                "width": float(np.median([g[m][t]["width_kept"] for t in common])),
                "n_draws": float(np.mean([g[m][t].get("info_n_draws", np.nan) for t in common])),
                "n_graphs": float(np.mean([g[m][t].get("info_n_graphs", np.nan) for t in common]))} for m in CFG["methods"]}
        res[f"80|{kind}|{rate}"]["hifi_minus_v2"] = {"est": float(d.mean()), "lo": float(np.quantile(bs, .025)),
                                                       "hi": float(np.quantile(bs, .975)), "n_topologies": len(common)}
    (ROOT / "results/ext_verify2_baselines2/fidelity_summary.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    if "--summarize" not in sys.argv:
        ext = dict(R.ext_methods()); ext["psel_v2_hifi"] = psel_v2_hifi; R._EXT = ext
        cfgp = ROOT / "experiments/ext/verify2_baselines2/fidelity_cfg.json"
        cfgp.write_text(json.dumps(CFG, indent=1))
        R.main(["--config", str(cfgp), "--workers", "2"])
    summarize()
