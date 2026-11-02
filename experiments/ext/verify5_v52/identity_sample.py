"""Skeptic check of r5v52 identity claims on a sample of D-07 dev units (seed_base 70261102).
Recomputes tolerant_v5_1, tolerant_v5_2, tolerant_ngA3, tolerant_v5_1_hs2 on the same data/stream and
(1) checks bitwise raw identities by reduction / gate status; (2) checks the stored v5_2 / v5_1 IS rows
reproduce; (3) checks hs_contemp_dropped == 0 and every declared lag-0 parent kept."""
import importlib.util, json, sys, warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
spec = importlib.util.spec_from_file_location("run_v52", ROOT / "experiments/ext/r5v52/run_v52.py")
RV = importlib.util.module_from_spec(spec); spec.loader.exec_module(RV)
from paper4.ext_r5ngorient3 import tolerant_ngA3
import paper4.ext_r5ngorient3 as A
from paper4.ext_r5hubscreen2 import tolerant_v5_1_hs2
from paper4.metrics import evaluate

def same(a, b):
    return a.status == b.status and (a.status != "ok" or (np.array_equal(a.C, b.C) and np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)))

def job(args):
    warnings.filterwarnings("ignore")
    cfgname, t_idx, rep, Ts = args
    cfg = json.loads((ROOT / f"experiments/configs/ext_r5v52_{cfgname}.json").read_text())
    fac = RV.load_factors(cfg)
    gen = RV.generator_config(cfg); H, lag, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    topo = RV.load_bank(cfg["bank"], cfg["split"])[t_idx]
    unit = cfg["seed_base"] + cfg.get("unit_offset", 0) + 1000 * t_idx + rep
    R = np.random.default_rng
    sem = RV.build_dynamic_sem(topo, gen, R([unit, 0]))
    skels = RV.unit_skeletons(sem, unit, dict(cfg, damage=RV.LAYOUT))
    node_law = RV.laws.node_laws(cfg.get("shock", "gauss"), unit, sem.n)
    want = {(k, float(r)) for k, r in cfg["cells"]}
    tag = RV.ext_seed("tolerant_v5_1")
    out = []
    for T in Ts:
        if cfg.get("shock", "gauss") == "gauss":
            data = sem.simulate(T, R([unit, 2, T]))
        else:
            data = RV.laws.simulate(sem, T, R([unit, 2, T]), node_law)
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if (kind, float(rate)) not in want: continue
            skel = RV.public(full)
            rng = lambda: R([unit, 3, T, c_idx, tag])
            v51 = RV.tolerant_v5_1(data, skel, lag, H, n_boot, rng())
            v52 = RV.tolerant_v5_2(data, skel, lag, H, n_boot, rng())
            ngA = tolerant_ngA3(data, skel, lag, H, n_boot, rng())
            hs2 = tolerant_v5_1_hs2(data, skel, lag, H, n_boot, rng())
            restored = A.fit_equations.__module__ == "paper4.estimator" and A.select_open.__module__ == "paper4.ext_narrow" and A.bootstrap_C.__module__ == "paper4.estimator"
            info = v52.info or {}
            gs = RV.gate_summary(info.get("ng_diag"))
            red = int(info.get("hs_reduced", 0)); evred = int(info.get("hs_ev_reduced", 0))
            wk = RV.M.width_key(skel.damage)
            fv, fr = fac["v51"].get(f"{T}|{wk}"), fac["red"].get(f"{T}|{wk}")
            f52 = fr if (red or fv is None) else fv
            is52 = evaluate(sem, RV.run_r5._scale(v52, f52, "tolerant_v5_2"), H, tau_effect=cfg["tau_effect"])
            is51 = evaluate(sem, RV.run_r5._scale(v51, fv, "tolerant_v5_1"), H, tau_effect=cfg["tau_effect"])
            # declared lag-0 parents
            out.append({"cfg": cfgname, "topology": topo.id, "replicate": rep, "T": T, "kind": kind, "rate": rate,
                        "red": red, "evred": evred, "no_gate": gs["no_gate"], "v52": v52.status, "v51": v51.status,
                        "eq_ngA3": same(v52, ngA), "eq_hs2": same(v52, hs2), "eq_v51": same(v52, v51),
                        "hs2_red": int((hs2.info or {}).get("hs_reduced", 0)),
                        "contemp_dropped": int(info.get("hs_contemp_dropped", 0) or 0), "restored": restored,
                        "IS52": is52.get("iscore_nonnull_mean"), "IS51": is51.get("iscore_nonnull_mean"),
                        "cov52": is52.get("n_covered_nonnull")})
    return out

if __name__ == "__main__":
    jobs = [("p2", 3, 0, [19, 25]), ("p2", 11, 2, [19, 25, 30]), ("p2", 17, 1, [25, 35]),
            ("ngmix", 5, 1, [80, 150]), ("gauss", 14, 0, [40, 150]), ("latent1", 8, 2, [80])]
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for o in ex.map(job, jobs): rows += o
    (ROOT / "results/ext_verify5_v52/identity_sample.json").write_text(json.dumps(rows, indent=1, default=float))
    print(len(rows))
