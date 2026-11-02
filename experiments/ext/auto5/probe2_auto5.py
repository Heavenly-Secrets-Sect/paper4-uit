"""Second design probe (open runs only): targeted opening with the opening budget k = max(#BH, 1)
(variant key 'targeted_sig_bh'), same units and records as probe_auto5.py, merged by analyse_probe2.py.

Original docstring of probe_auto5.py follows.
Design probe and width calibration of tolerant_auto5 on D-07H development (never D-07).

Uses exactly the runner's calibration units (D-07H development, seed_base + 500000 + 1000 * topology
+ replicate, kinds extra/missing/reversed x 0.2/0.5 plus none, same data streams; the GES cell is not
part of calibration, as for auto3). For every run it records the gate decision and, for the branch the
gate chose, the raw (unwidened) interval of every design variant:
  closed: flip pool sig / mec
  open:   all lags or targeted (re-selected) x flip pool sig / mec
Output: a pickle of per-run records (dist = |C_true - midpoint|, half = half width, non-null pairs).
analyse_probe.py turns it into the in-sample comparison of variants and the width table.

Run: python experiments/ext/auto5/probe_auto5.py --config experiments/configs/ext_auto5_eval.json \
       --n-boot 199 --workers 3 --out experiments/ext/auto5/probe.pkl
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from run_experiment import generator_config, public, unit_skeletons  # noqa: E402
from paper4 import ext_auto5 as A  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from paper4.ext_gate import ALPHA_GATE, diagnose_gate  # noqa: E402
from paper4.skeleton import Skeleton  # noqa: E402

VARIANTS = {"closed": [("closed", "sig"), ("closed", "mec")],
            "open": [("all", "sig"), ("all", "mec"), ("targeted", "sig"), ("targeted", "mec")]}


def unit_job(args):
    cfg, t_idx, rep, n_boot, Ts = args
    cal = cfg["calibration"]
    topo = load_bank(cal["bank"], cal["split"])[t_idx]
    ccfg = dict(cfg, damage={"kinds": cal["kinds"], "rates": cal["rates"]})
    gen = generator_config(cfg)
    lag_max, H = gen.lag_max, cfg["H"]
    unit = cfg["seed_base"] + 500_000 + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, ccfg)
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    out = []
    for T in Ts:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            skel = public(full)
            rec = {"T": T, "kind": kind, "rate": rate, "topology": topo.id, "rep": rep, "var": {}}
            t0 = time.perf_counter()
            base = Skeleton(skel.n, set(skel.oriented), set(skel.undetermined))
            g = diagnose_gate(data, base, lag_max)["p_gate"]
            rec["p_gate"] = g
            rec["state"] = "open" if (g is not None and g <= ALPHA_GATE) else "closed"
            for v_idx, (mode, flip) in [(6, ("targeted", "sig"))]:
                if rec["state"] != "open":
                    continue
                rng = np.random.default_rng([unit, 41, T, c_idx, v_idx])
                res = A.auto5_raw(data, skel, lag_max, H, n_boot, rng, flip_mode=flip, open_mode=mode, open_budget="bh")
                if res.status != "ok":
                    rec["var"][f"{mode}_{flip}_bh"] = None
                    continue
                mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                rec["var"][f"{mode}_{flip}_bh"] = {
                    "dist": np.abs(C_true - mid)[nonnull].astype(np.float32),
                    "half": half[nonnull].astype(np.float32),
                    "branch": res.info["branch"], "n_flip_pool": res.info["n_flip_pool"],
                    "n_open": res.info["n_open"], "n_repair": res.info["n_repair"]}
            rec["sec"] = time.perf_counter() - t0
            out.append(rec)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--n-boot", type=int, default=199)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-topologies", type=int, default=None)
    ap.add_argument("--T", type=int, nargs="*", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    cal = cfg["calibration"]
    assert cal["bank"] == "D-07H" and cal["split"] == "development"
    n_topo = len(load_bank(cal["bank"], cal["split"])[: args.max_topologies or None])
    Ts = args.T or cfg["T"]
    jobs = [(cfg, t, rep, args.n_boot, Ts) for t in range(n_topo) for rep in range(cal["replicates"])]
    start = time.perf_counter()
    with ProcessPoolExecutor(args.workers) as pool:
        recs = [r for out in pool.map(unit_job, jobs) for r in out]
    with open(args.out, "wb") as fh:
        pickle.dump({"n_boot": args.n_boot, "Ts": Ts, "n_topo": n_topo, "records": recs,
                     "seconds": round(time.perf_counter() - start, 1)}, fh)
    print(f"{len(recs)} records in {time.perf_counter() - start:.1f} s -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
