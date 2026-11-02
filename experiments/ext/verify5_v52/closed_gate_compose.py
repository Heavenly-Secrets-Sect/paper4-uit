"""Skeptic test of the composition where both components would act (P2 missing/reversed, T19/25/30):
patch (process-local) ext_r5ngorient3.ng_evidence3 to a closed-gate stub; then tolerant_v5_2 must equal
tolerant_v5_1_hs2 bit for bit (raw C/lo/hi, hs_reduced, hs_eq_total, hs_draws_reduced), including runs with reduction."""
import importlib.util, json, warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
spec = importlib.util.spec_from_file_location("run_v52", ROOT / "experiments/ext/r5v52/run_v52.py")
RV = importlib.util.module_from_spec(spec); spec.loader.exec_module(RV)
import paper4.ext_r5ngorient3 as A
from paper4.ext_r5hubscreen2 import tolerant_v5_1_hs2

def closed(xr, yr, **kw):
    return {"p": 0.5, "gate": False, "gate_p": 1.0, "R": 0.0, "se": float("nan"), "form": "none", "fam": ""}

def job(args):
    warnings.filterwarnings("ignore")
    A.ng_evidence3 = closed
    t_idx, rep = args
    cfg = json.loads((ROOT / "experiments/configs/ext_r5v52_p2.json").read_text())
    gen = RV.generator_config(cfg); H, lag, n_boot = cfg["H"], gen.lag_max, 99
    topo = RV.load_bank(cfg["bank"], cfg["split"])[t_idx]
    unit = cfg["seed_base"] + 1000 * t_idx + rep
    R = np.random.default_rng
    sem = RV.build_dynamic_sem(topo, gen, R([unit, 0]))
    skels = RV.unit_skeletons(sem, unit, dict(cfg, damage=RV.LAYOUT))
    tag = RV.ext_seed("tolerant_v5_1")
    out = []
    for T in (19, 25, 30):
        data = sem.simulate(T, R([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if not (kind in ("missing", "reversed") and float(rate) == 0.2): continue
            skel = RV.public(full)
            a = RV.tolerant_v5_2(data, skel, lag, H, n_boot, R([unit, 3, T, c_idx, tag]))
            b = tolerant_v5_1_hs2(data, skel, lag, H, n_boot, R([unit, 3, T, c_idx, tag]))
            ia, ib = a.info or {}, b.info or {}
            eq = a.status == b.status and (a.status != "ok" or (np.array_equal(a.C, b.C) and np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi)))
            flags = all(ia.get(k) == ib.get(k) for k in ("hs_reduced", "hs_eq_total", "hs_draws_reduced", "hs_draws_total"))
            out.append({"topo": topo.id, "rep": rep, "T": T, "kind": kind, "status": [a.status, b.status], "eq": bool(eq), "flags": bool(flags),
                        "red": ia.get("hs_reduced"), "evred": ia.get("hs_ev_reduced"), "ev_fail": ia.get("hs_ev_fit_fail"),
                        "targeted": ia.get("v51_targeted"), "contemp": ia.get("hs_contemp_dropped"),
                        "fl": {k: [ia.get(k), ib.get(k)] for k in ("hs_eq_total", "hs_draws_reduced", "hs_draws_total")}})
    return out

if __name__ == "__main__":
    jobs = [(t, r) for t in (0, 4, 9, 13, 18) for r in (0, 1)]
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for o in ex.map(job, jobs): rows += o
    (ROOT / "results/ext_verify5_v52/closed_gate_compose.json").write_text(json.dumps(rows, indent=1))
    n = len(rows); eq = sum(r["eq"] and r["flags"] for r in rows); red = [r for r in rows if r["red"]]
    print("runs", n, "identical", eq, "reduced", len(red), "reduced identical", sum(r["eq"] and r["flags"] for r in red),
          "targeted reduced", sum(1 for r in red if r["targeted"]), "evred", sum(1 for r in rows if r["evred"]),
          "contemp", sum(r["contemp"] or 0 for r in rows))
    for r in rows:
        if not (r["eq"] and r["flags"]): print("MISMATCH", r)
