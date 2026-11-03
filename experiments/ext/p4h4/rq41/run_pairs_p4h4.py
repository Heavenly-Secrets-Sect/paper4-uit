"""RQ4.1 on P4-H4 (SEALED confirmatory run, frozen spec). Adapted from
experiments/ext/metrics/run_pairs.py (D-07); that file is not modified.

Differences from the D-07 script: bank per config (P4-H4) with both splits; methods oracle, plugin, tolerant_v4
(frozen width factors), tolerant_v5_1 (frozen width factors); methods receive run_experiment.public(skel)
(no damage log, no lag hints); no RQ4.4 signals; failed runs are logged; split-specific unit seeds.

Run: python experiments/ext/p4h4/rq41/run_pairs_p4h4.py --config experiments/configs/ext_p4h4_rq41_main.json --workers 4
Writes results/<name>/{pairs.npz, runs_status.jsonl, nullpairs.jsonl, manifest.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from paper4 import methods as M  # noqa: E402
from paper4.effects import mean_lag, peak_lag  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402  (read-only import)

NAME51 = "tolerant_v5_1"


def roles(sem, skel, n):
    """Truth-side role[j, i] of the effect of i on j: 2 damaged pair, 1 downstream of a damaged edge,
    0 untouched. Same code as experiments/ext/metrics/run_pairs.py. Uses the private damage log; only
    the evaluation calls this, never a method."""
    A = np.zeros((n, n), dtype=bool)
    for (u, v) in sem.edge_lag:
        A[u, v] = True
    reach = np.eye(n, dtype=bool)
    for _ in range(n):
        reach = reach | (reach.astype(int) @ A.astype(int) > 0)
    role = np.zeros((n, n), dtype=int)
    kind = skel.damage.get("kind", "none")
    for e in skel.log:
        if "pair" not in e:
            continue
        u, v = e["pair"]
        if kind == "missing":
            a, b = (u, v) if (u, v) in sem.edge_lag else (v, u)
        else:
            a, b = u, v
        down = np.outer(reach[:, a], reach[b, :]).T
        role = np.maximum(role, down.astype(int))
        role[b, a] = 2
        if kind == "extra":
            role[a, b] = max(role[a, b], 0)
    return role


def run_unit(args):
    cfg, topo, g_idx, split_idx, t_idx, rep, calib = args
    gen = generator_config(cfg)
    H, lag_max, n_boot, tau = cfg["H"], gen.lag_max, cfg["n_boot"], cfg["tau_effect"]
    unit = cfg["seed_base"] + 100_000 * split_idx + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    oracle_skel = true_skeleton(sem, with_lags=True)
    n = sem.n
    _, C_t, ml_t, pk_t = truth_effects(sem, H)
    off = ~np.eye(n, dtype=bool)
    nonnull = off & (np.abs(C_t) > tau)
    null = off & ~nonnull
    direct = -np.ones((n, n), dtype=int)
    for (u, v), lag in sem.edge_lag.items():
        direct[v, u] = lag
    jj, ii = np.nonzero(nonnull)
    methods = cfg["methods"]
    keys = ("topo", "split", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "ml_t", "ml_e",
            "pk_t", "pk_e", "direct_lag", "role")
    cols = {k: [] for k in keys}
    status, nulls = [], []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        oracle_res = None
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)
            res = {}
            res["plugin"] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
            if "oracle" in methods:
                if oracle_res is None:
                    oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                res["oracle"] = oracle_res
            if "tolerant_v4" in methods:
                v3 = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                res["tolerant_v4"] = M.calibrate_width(v3, calib["v4"].get(f"mod|{T}|{M.width_key(skel.damage)}"),
                                                       "tolerant_v4")
            if NAME51 in methods:
                raw = tolerant_v5_1(data, skel, lag_max, H, n_boot, rng(ext_seed(NAME51)))
                res[NAME51] = M.calibrate_width(raw, calib["v51"].get(f"{NAME51}|{T}|{M.width_key(skel.damage)}"),
                                                NAME51)
            role = roles(sem, full, n)
            for m_idx, name in enumerate(methods):
                r = res[name]
                status.append({"topo": g_idx, "split": split_idx, "rep": rep, "T": T, "cell": c_idx, "method": name,
                               "status": r.status})
                if r.status != "ok":
                    continue
                excl = ~((r.lo <= 0) & (0 <= r.hi))
                nulls.append({"topo": g_idx, "rep": rep, "T": T, "cell": c_idx, "method": name,
                              "n_null": int(null.sum()), "n_null_excl0": int((excl & null).sum())})
                ml_e = mean_lag(r.theta, H) if r.theta is not None else np.full((n, n), np.nan)
                pk_e = peak_lag(r.theta, H) if r.theta is not None else np.full((n, n), -1)
                k = len(jj)
                cols["topo"] += [g_idx] * k
                cols["split"] += [split_idx] * k
                cols["rep"] += [rep] * k
                cols["T"] += [T] * k
                cols["cell"] += [c_idx] * k
                cols["method"] += [m_idx] * k
                cols["j"] += jj.tolist()
                cols["i"] += ii.tolist()
                cols["C_t"] += C_t[jj, ii].tolist()
                cols["C_e"] += r.C[jj, ii].tolist()
                cols["lo"] += r.lo[jj, ii].tolist()
                cols["hi"] += r.hi[jj, ii].tolist()
                cols["ml_t"] += ml_t[jj, ii].tolist()
                cols["ml_e"] += ml_e[jj, ii].tolist()
                cols["pk_t"] += pk_t[jj, ii].tolist()
                cols["pk_e"] += np.asarray(pk_e)[jj, ii].tolist()
                cols["direct_lag"] += direct[jj, ii].tolist()
                cols["role"] += role[jj, ii].tolist()
    return cols, nulls, status


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-units", type=int, default=0, help="timing probe: stop after this many units")
    ap.add_argument("--out-suffix", default="")
    args = ap.parse_args(argv)
    if args.workers > 4:
        raise SystemExit("--workers max 4")
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    calib = {"v4": json.loads((ROOT / cfg["frozen_v4"]).read_text(encoding="utf-8")),
             "v51": json.loads((ROOT / cfg["frozen_v51"]).read_text(encoding="utf-8"))}
    jobs, topo_meta = [], []
    for s_idx, split in enumerate(cfg["splits"]):
        tops = load_bank(cfg["bank"], split)
        for t_idx, topo in enumerate(tops):
            g_idx = 100 * s_idx + t_idx
            topo_meta.append({"g": g_idx, "split": split, "id": topo.id, "profile": topo.profile, "sha256": topo.sha256})
            for rep in range(cfg["replicates"]):
                jobs.append((cfg, topo, g_idx, s_idx, t_idx, rep, calib))
    if args.max_units:
        jobs = jobs[:: max(1, len(jobs) // args.max_units)][: args.max_units]
    start = time.perf_counter()
    allc, nulls, status = None, [], []
    with ProcessPoolExecutor(args.workers) as pool:
        for cols, nl, st in pool.map(run_unit, jobs):
            if allc is None:
                allc = {k: list(v) for k, v in cols.items()}
            else:
                for k, v in cols.items():
                    allc[k].extend(v)
            nulls.extend(nl)
            status.extend(st)
    out = ROOT / "results" / (cfg["name"] + args.out_suffix + ("_probe" if args.max_units else ""))
    out.mkdir(parents=True, exist_ok=True)
    cells = [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]]
    np.savez_compressed(out / "pairs.npz", methods=np.array(cfg["methods"]),
                        cells=np.array([f"{k}|{r}" for k, r in cells]),
                        **{k: np.asarray(v, dtype=float) for k, v in allc.items()})
    with open(out / "nullpairs.jsonl", "w", encoding="utf-8") as fh:
        for r in nulls:
            fh.write(json.dumps(r) + "\n")
    with open(out / "runs_status.jsonl", "w", encoding="utf-8") as fh:
        for r in status:
            fh.write(json.dumps(r) + "\n")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_units": len(jobs),
                "n_pair_rows": len(allc["topo"]), "n_failed_runs": sum(s["status"] != "ok" for s in status),
                "topologies": topo_meta}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(allc['topo'])} pair rows from {len(jobs)} units in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
