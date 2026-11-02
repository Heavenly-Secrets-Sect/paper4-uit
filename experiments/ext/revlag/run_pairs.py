"""Pair-level rows for the round-2 "revlag" direction (R2-6b lag output, R2-7 frozen RQ4.4 flag).

Mirrors experiments/run_experiment.py exactly for the methods it supports (same unit seeds, same
damaged skeletons, same data, same per-method random streams, the public skeleton only):
- ``oracle``        runner stream rng(2), fitted once per T
- ``plugin``        rng(1)
- ``tolerant_v4``   methods.tolerant_v3 on rng(6), widened by the frozen v4 factor
                    (experiments/calibration/tolerant_v4_frozen.json)
- ``tolerant_v4L``  src/paper4/ext_revlag.py on rng(ext_seed("tolerant_v4L")), as the runner does
Supports the config keys ``scenarios`` (latent / measurement noise) and ``learned`` (GES cell, with
the stated damage read from ``ges_damage_from``, a calibration file computed on D-07H development).

Per (topology, replicate, scenario, T, cell, method) and every non-null ordered pair (|C_true| > tau):
estimate, interval, true and estimated mean / peak lag, the true lag of the pair's direct edge,
the round-1 role (0 untouched, 1 downstream, 2 damaged; metrics direction) and ``dC`` = |C_true -
C_true with the damaged true edges zeroed| (red-team definition of "affected": dC >= 0.05).
For ``tolerant_v4L`` also a percentile interval of the mean lag over its draws (descriptive).
Per run, null pairs: count, intervals excluding 0, interval score sum.

Methods never see truth. Truth-side labels are computed here for the evaluation only.

Run:  python experiments/ext/revlag/run_pairs.py --config experiments/configs/ext_revlag_<x>.json --workers 3
Writes results/<name>/{pairs.npz, nullpairs.jsonl, manifest.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from paper4 import methods as M  # noqa: E402
from paper4.effects import mean_lag, peak_lag  # noqa: E402
from paper4.ext_revlag import frozen_factor, tolerant_v4L_draws  # noqa: E402
from paper4.generator import DynamicSEM, add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import interval_score, truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import _learned_cell, ext_seed, generator_config, public, unit_skeletons  # noqa: E402

KINDCODE = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}
COLS = ("topo", "rep", "scen", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "ml_t", "ml_e",
        "pk_t", "pk_e", "direct_lag", "role", "dC", "stated", "ml_lo", "ml_hi")


def roles(sem, skel, n):
    """Round-1 role labels (copied from experiments/ext/metrics/run_pairs.py, unchanged)."""
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


def delta_C(sem, skel, H):
    """Red-team P1 definition (experiments/ext/redteam/pair_probe.py): |C_true - C0| where C0 is the
    truth with every damaged true edge (deleted or reversed) set to 0. Zero matrix for extra/none."""
    B0 = sem.B.copy()
    touched = False
    for entry in skel.log:
        if "pair" not in entry:
            continue
        u, v = entry["pair"]
        for e in ((u, v), (v, u)):
            if e in sem.edge_lag:
                B0[sem.edge_lag[e], e[1], e[0]] = 0.0
                touched = True
    _, C_t, _, _ = truth_effects(sem, H)
    if not touched:
        return np.zeros_like(C_t)
    sem0 = DynamicSEM(sem.topology_id, sem.nodes, B0, sem.noise_var, dict(sem.edge_lag), sem.config)
    _, C0, _, _ = truth_effects(sem0, H)
    return np.abs(C_t - C0)


def lag_interval(thetas, H, min_share=0.5):
    """Percentile 95% interval of the mean lag over draws (NaN where fewer than min_share of the
    draws have a defined mean lag)."""
    ml = np.stack([mean_lag(t, H) for t in thetas])                # (draws, n, n)
    ok = np.isfinite(ml)
    share = ok.mean(axis=0)
    with np.errstate(all="ignore"):
        lo = np.nanquantile(np.where(ok, ml, np.nan), 0.025, axis=0)
        hi = np.nanquantile(np.where(ok, ml, np.nan), 0.975, axis=0)
    bad = share < min_share
    return np.where(bad, np.nan, lo), np.where(bad, np.nan, hi)


def run_unit(args):
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    cfg, topo, t_idx, rep, calib = args
    gen = generator_config(cfg)
    H, lag_max, n_boot, tau = cfg["H"], gen.lag_max, cfg["n_boot"], cfg["tau_effect"]
    unit = cfg["seed_base"] + 1000 * t_idx + rep
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
    scen_list = cfg.get("scenarios") or [{"name": "clean"}]
    cols = {k: [] for k in COLS}
    nulls = []
    for s_idx, sc in enumerate(scen_list):
        sem_s = add_latent(sem, sc.get("latent", 0), np.random.default_rng([unit, 5]),
                           n_children=sc.get("latent_children", 3))
        for T in cfg["T"]:
            data = sem_s.simulate(T, np.random.default_rng([unit, 2, T]))
            data = add_measurement_noise(data, sc.get("meas_noise", 0.0), np.random.default_rng([unit, 6, T]))
            cells_T = dict(skels)
            if cfg.get("learned"):
                g, _counts = _learned_cell(cfg, sem_s, sc, T, unit, calib, "main")
                cells_T[("ges", 0.0)] = g
            oracle_res = None
            for c_idx, ((kind, rate), full) in enumerate(cells_T.items()):
                if cfg.get("only_cells") and f"{kind}|{rate}" not in cfg["only_cells"]:
                    continue
                rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
                skel = public(full)
                res, extra = {}, {}
                if "plugin" in methods:
                    res["plugin"] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
                if "oracle" in methods:
                    if oracle_res is None:
                        oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                    res["oracle"] = oracle_res
                if "tolerant_v4" in methods:
                    v3 = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                    res["tolerant_v4"] = M.calibrate_width(v3, frozen_factor(T, skel.damage), "tolerant_v4")
                if "tolerant_v4L" in methods:
                    r, thetas = tolerant_v4L_draws(data, skel, lag_max, H, n_boot, rng(ext_seed("tolerant_v4L")))
                    res["tolerant_v4L"] = r
                    if thetas is not None:
                        extra["tolerant_v4L"] = lag_interval(thetas, H)
                if kind == "ges":
                    role = np.full((n, n), -1)
                    dC = np.full((n, n), np.nan)
                else:
                    role = roles(sem, full, n)
                    dC = delta_C(sem, full, H)
                stated = KINDCODE[M.width_key(skel.damage)]
                cell_code = len(skels) if kind == "ges" else c_idx
                for m_idx, name in enumerate(methods):
                    r = res[name]
                    if r.status != "ok":
                        nulls.append({"topo": t_idx, "rep": rep, "scen": s_idx, "T": T, "cell": cell_code,
                                      "method": name, "status": r.status})
                        continue
                    excl = ~((r.lo <= 0) & (0 <= r.hi))
                    isc = interval_score(r.lo, r.hi, C_t)
                    nulls.append({"topo": t_idx, "rep": rep, "scen": s_idx, "T": T, "cell": cell_code, "method": name,
                                  "status": "ok", "n_null": int(null.sum()), "n_null_excl0": int((excl & null).sum()),
                                  "is_null_sum": float(isc[null].sum())})
                    ml_e = mean_lag(r.theta, H)
                    pk_e = peak_lag(r.theta, H)
                    k = len(jj)
                    mlo, mhi = extra.get(name, (np.full((n, n), np.nan), np.full((n, n), np.nan)))
                    vals = {"topo": [t_idx] * k, "rep": [rep] * k, "scen": [s_idx] * k, "T": [T] * k,
                            "cell": [cell_code] * k, "method": [m_idx] * k, "j": jj, "i": ii, "C_t": C_t[jj, ii],
                            "C_e": r.C[jj, ii], "lo": r.lo[jj, ii], "hi": r.hi[jj, ii], "ml_t": ml_t[jj, ii],
                            "ml_e": ml_e[jj, ii], "pk_t": pk_t[jj, ii], "pk_e": pk_e[jj, ii],
                            "direct_lag": direct[jj, ii], "role": role[jj, ii], "dC": dC[jj, ii],
                            "stated": [stated] * k, "ml_lo": mlo[jj, ii], "ml_hi": mhi[jj, ii]}
                    for key in COLS:
                        cols[key].extend(np.asarray(vals[key]).tolist())
    return cols, nulls


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-units", type=int, default=0, help="stop after this many units (probe)")
    ap.add_argument("--out-suffix", default="")
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    calib = {}
    if cfg.get("learned"):
        calib = {"ges_damage": json.loads((ROOT / cfg["ges_damage_from"]).read_text(encoding="utf-8"))["ges_damage"]}
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib) for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    if args.max_units:
        jobs = jobs[: args.max_units]
    start = time.perf_counter()
    allc = {k: [] for k in COLS}
    nulls = []
    with ProcessPoolExecutor(args.workers) as pool:
        for cols, nl in pool.map(run_unit, jobs):
            for k, v in cols.items():
                allc[k].extend(v)
            nulls.extend(nl)
    out = ROOT / "results" / (cfg["name"] + args.out_suffix)
    out.mkdir(parents=True, exist_ok=True)
    cells = [f"{k}|{r}" for k, r in [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"]
                                                       for r in cfg["damage"]["rates"]]]
    if cfg.get("learned"):
        cells.append("ges|0.0")
    np.savez_compressed(out / "pairs.npz", methods=np.array(cfg["methods"]), cells=np.array(cells),
                        scenarios=np.array([s["name"] for s in (cfg.get("scenarios") or [{"name": "clean"}])]),
                        **{k: np.asarray(v, dtype=float) for k, v in allc.items()})
    with open(out / "nullpairs.jsonl", "w", encoding="utf-8") as fh:
        for r in nulls:
            fh.write(json.dumps(r) + "\n")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_units": len(jobs),
                "n_pair_rows": len(allc["topo"]), "workers": args.workers,
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(allc['topo'])} pair rows from {len(jobs)} units in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
