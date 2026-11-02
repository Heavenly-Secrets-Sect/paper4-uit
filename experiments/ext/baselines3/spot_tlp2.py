"""Pre-registered check (docs/ext/baselines3.md 3.1): recompute tlp2_db_p3 on D-07 development for 3 topologies x
replicate 0 x T 80/150 x missing 0.2/0.5 (12 calls), built exactly as the runner's main phase builds them, and compare
with the stored rows of results/ext_tlp2_t80b / ext_tlp2_t150c. -> results/ext_baselines3_eval/spot_tlp2.json"""
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4.generator import build_dynamic_sem
from paper4.metrics import evaluate
from paper4.topology import load_bank

cfg = json.loads((ROOT / "experiments/configs/ext_baselines3_eval.json").read_text())
gen = R.generator_config(cfg); fn = R.ext_methods()["tlp2_db_p3"]
assert fn.__module__ == "paper4.ext_tlp2"
stored = {}
for src in ("ext_tlp2_t80b", "ext_tlp2_t150c"):
    for l in open(ROOT / "results" / src / "runs.jsonl"):
        r = json.loads(l)
        if r["method"] == "tlp2_db_p3":
            stored[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])] = r
out = []
for t_idx, topo in enumerate(load_bank("D-07", "development")[:3]):
    rep = 0
    unit = cfg["seed_base"] + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = R.unit_skeletons(sem, unit, cfg)
    for T in (80, 150):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for rate in (0.2, 0.5):
            t0 = time.perf_counter()
            res = fn(data, R.public(skels[("missing", rate)]), gen.lag_max, cfg["H"], cfg["n_boot"], None)
            sec = time.perf_counter() - t0
            row = evaluate(sem, res, cfg["H"], tau_effect=cfg["tau_effect"])
            s = stored[(topo.id, rep, T, "missing", rate)]
            out.append({"topology": topo.id, "T": T, "rate": rate, "seconds": round(sec, 2),
                        "iscore_new": row.get("iscore_nonnull_mean"), "iscore_stored": s.get("iscore_nonnull_mean"),
                        "cov_new": row.get("n_covered_nonnull"), "cov_stored": s.get("n_covered_nonnull"),
                        "identical": row.get("iscore_nonnull_mean") == s.get("iscore_nonnull_mean")
                        and row.get("n_covered_nonnull") == s.get("n_covered_nonnull")})
            print(out[-1], flush=True)
(ROOT / "results/ext_baselines3_eval").mkdir(parents=True, exist_ok=True)
(ROOT / "results/ext_baselines3_eval/spot_tlp2.json").write_text(json.dumps(
    {"n": len(out), "n_identical": sum(o["identical"] for o in out), "calls": out}, indent=1))
print("identical", sum(o["identical"] for o in out), "/", len(out))
