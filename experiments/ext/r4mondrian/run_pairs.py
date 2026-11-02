"""Pair-level driver for round 4, ID "mondrian" (docs/ext/r4mondrian.md).

Mirrors experiments/run_experiment.py for ``tolerant_v5_1`` exactly: same unit seeds (calibration
phase: + 500 000), same damaged skeletons (``unit_skeletons``), same data, same scenario streams,
same cell positions c_idx and the runner's stream rng(ext_seed("tolerant_v5_1")). v5_1 is called
through ``ext_r4mondrian.v51_with_structure`` (v5_1 unchanged plus the record of its draws'
structures). Per run it writes the runner's ``evaluate`` row of v5_1 with the frozen width factor
(experiments/ext/v51/frozen_v4_v51.json) so that pairing with stored runs can be checked, and per
non-null pair: C_true, mid, unscaled h, frozen-v5_1 lo/hi, the class statistics (diff, f, R,
contest), and (main phase, if requested) the oracle interval and dC (reversal / deletion
affected-pair label of experiments/ext/revlag/run_pairs.py).

The oracle (built-in, rng(2)) is fitted once per T at the first cell (c_idx 0), as a full-grid
runner does.

Methods never see truth; truth-side labels are for scoring only.

Run:  python experiments/ext/r4mondrian/run_pairs.py --config experiments/configs/ext_r4mondrian_<x>.json --phase main --workers 3
Writes results/<name>/{pairs.npz, runs.jsonl, manifest.json}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "revlag"))

from paper4 import ext_r4mondrian as X  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.generator import add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from run_pairs import delta_C  # noqa: E402  (experiments/ext/revlag/run_pairs.py, unchanged)

NAME = "tolerant_v5_1"
FROZEN = ROOT / "experiments" / "ext" / "v51" / "frozen_v4_v51.json"
KINDCODE = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}
COLS = ("topo", "rep", "scen", "T", "cell", "stated", "j", "i", "C_t", "mid", "h", "lo51", "hi51",
        "diff", "f", "R", "contest", "dC", "olo", "ohi")


def run_unit(args):
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    cfg, topo, t_idx, rep, phase, fac = args
    gen = generator_config(cfg)
    H, lag_max, n_boot, tau = cfg["H"], gen.lag_max, cfg["n_boot"], cfg["tau_effect"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    oracle_skel = true_skeleton(sem, with_lags=True)
    n = sem.n
    _, C_t, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(n, dtype=bool) & (np.abs(C_t) > tau)
    jj, ii = np.nonzero(nonnull)
    k = len(jj)
    cols = {c: [] for c in COLS}
    rows = []
    scen_list = (cfg.get("scenarios") or [{"name": "clean"}]) if phase == "main" else [{"name": "clean"}]
    with_oracle = phase == "main" and cfg.get("oracle", False)
    for s_idx, sc in enumerate(scen_list):
        sem_s = add_latent(sem, sc.get("latent", 0), np.random.default_rng([unit, 5]),
                           n_children=sc.get("latent_children", 3))
        for T in cfg["T"]:
            data = sem_s.simulate(T, np.random.default_rng([unit, 2, T]))
            data = add_measurement_noise(data, sc.get("meas_noise", 0.0), np.random.default_rng([unit, 6, T]))
            oracle_res = None
            for c_idx, ((kind, rate), full) in enumerate(skels.items()):
                rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
                skel = public(full)
                wk = M.width_key(skel.damage)
                if with_oracle and oracle_res is None:
                    oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                res, st = X.v51_with_structure(data, skel, lag_max, H, n_boot, rng(ext_seed(NAME)))
                frozen = M.calibrate_width(res, fac.get(f"{NAME}|{T}|{wk}"), NAME)
                row = evaluate(sem_s, frozen, H, tau_effect=tau)
                row.update({"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind,
                            "rate": rate, "k": skel.damage.get("k", 0), "scenario": sc["name"],
                            "stated": wk})
                if st is not None:
                    row.update({"share_R_nonnull": float(st["R"][nonnull].mean()), "n_draws": st["n_draws"]})
                rows.append(row)
                if res.status != "ok":
                    continue
                mid, h = X.mid_half(res)
                dC = delta_C(sem, full, H) if (phase == "main" and kind != "none") else np.zeros((n, n))
                olo = oracle_res.lo if with_oracle and oracle_res.status == "ok" else np.full((n, n), np.nan)
                ohi = oracle_res.hi if with_oracle and oracle_res.status == "ok" else np.full((n, n), np.nan)
                vals = {"topo": [t_idx] * k, "rep": [rep] * k, "scen": [s_idx] * k, "T": [T] * k,
                        "cell": [c_idx] * k, "stated": [KINDCODE[wk]] * k, "j": jj, "i": ii,
                        "C_t": C_t[jj, ii], "mid": mid[jj, ii], "h": h[jj, ii], "lo51": frozen.lo[jj, ii],
                        "hi51": frozen.hi[jj, ii], "diff": st["diff"][jj, ii], "f": st["f"][jj, ii],
                        "R": st["R"][jj, ii], "contest": st["contest"][jj, ii], "dC": dC[jj, ii],
                        "olo": olo[jj, ii], "ohi": ohi[jj, ii]}
                for c in COLS:
                    cols[c].extend(np.asarray(vals[c]).tolist())
    return cols, rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--phase", choices=("calibration", "main"), required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-units", type=int, default=0)
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    for forbidden in ("P4-H1", "P4-H2"):
        if forbidden in (cfg["bank"], cfg.get("calibration", {}).get("bank")):
            raise SystemExit(f"bank {forbidden} is out of bounds for r4mondrian")
    if cfg["split"] != "development":
        raise SystemExit("development split only")
    fac = {k: v for k, v in json.loads(FROZEN.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, args.phase, fac)
            for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    if args.max_units:
        jobs = jobs[: args.max_units]
    cols = {c: [] for c in COLS}
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        for c, r in pool.map(run_unit, jobs):
            for key in COLS:
                cols[key].extend(c[key])
            rows.extend(r)
    np.savez_compressed(out / "pairs.npz", **{k: np.asarray(v) for k, v in cols.items()})
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    files = [Path(__file__), ROOT / "src" / "paper4" / "ext_r4mondrian.py", FROZEN, Path(args.config)]
    manifest = {"config": cfg, "phase": args.phase, "seconds": round(time.perf_counter() - start, 1),
                "n_runs": len(rows), "n_pairs": len(cols["topo"]), "max_units": args.max_units,
                "python": sys.executable, "numpy": np.__version__,
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies],
                "sha256": {str(p.resolve().relative_to(ROOT)) if p.resolve().is_relative_to(ROOT) else str(p):
                           hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} runs, {len(cols['topo'])} pairs in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
