"""Pair-level rows for round 3, ID "revlag3" (R3-4 reversal comparator, R3-9 RQ4.4 flag for auto3 /
v5_1, and the corrected P3/P4 P4-H2 spec). Successor of experiments/ext/revlag/run_pairs.py (that
file is kept unchanged); differences:

1. Width factors come ONLY from the config key ``frozen_calibration`` (path from the repo root),
   whose sha256 must equal the config key ``frozen_calibration_sha256`` (the run aborts otherwise).
   The old runner ignored that key and read a path hard-coded in src/paper4/ext_revlag.py
   (``_FROZEN``). ``tolerant_v4L`` still widens internally through ``ext_revlag.frozen_factor``;
   this runner asserts that ``ext_revlag._FROZEN`` is the same file as ``frozen_calibration`` and
   that it carries identical ``mod|*`` factors, so the two paths cannot diverge silently.
2. Any extension method (``ext_*`` module, as the main runner loads them) is supported, on the
   runner's stream ``rng(ext_seed(name))``; if it is listed in ``calibrate_methods`` it is widened by
   ``<name>|T|width_key`` of the frozen file, exactly as run_experiment.py does in the main phase.
   The defining module of every method is written to the manifest (bug E4 of synthesis_round2).
3. Two encodings of the stated damage kind are stored per row: ``stated`` = width_key(damage)
   (k-based, as in round 2) and ``stated_kind`` = the public ``damage["kind"]`` for single-kind
   records (width_key for composite records such as the GES cell). The frozen RQ4.4 flag was
   trained with the cell kind, which equals ``stated_kind``; round 2 scored it with ``stated``, which
   differs on cells whose stated k is 0 (0.56% of the fresh rows).
4. Failed runs are written to ``nullpairs.jsonl`` with their status (as before) and counted per
   (T, cell, method) in the manifest.
5. ``only_cells`` keeps the cell position c_idx of the full grid, so built-in streams (bug E1:
   seeded by cell position) are the same as in a full-grid run of the same config.

Supported built-ins (same streams as run_experiment.py): ``oracle`` rng(2), ``plugin`` rng(1),
``tolerant_v4`` (methods.tolerant_v3 on rng(6), widened by ``mod|T|width_key``), ``tolerant_v4L``
(ext_revlag on rng(ext_seed)).

Methods never see truth; truth-side labels (C_true, lags, role, dC) are for the evaluation only.

Run:  python experiments/ext/revlag3/run_pairs3.py --config experiments/configs/ext_revlag3_<x>.json --workers 3
Writes results/<name>/{pairs.npz, nullpairs.jsonl, manifest.json}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "revlag"))

from paper4 import ext_revlag  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.effects import mean_lag, peak_lag  # noqa: E402
from paper4.generator import add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import interval_score, truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import _learned_cell, ext_methods, ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from run_pairs import delta_C, lag_interval, roles  # noqa: E402  (experiments/ext/revlag, unchanged)

KINDCODE = {"none": 0, "extra": 1, "missing": 2, "reversed": 3}
STATECODE = {"closed": 0, "open": 1, "undiagnosable": 2}
COLS = ("topo", "rep", "scen", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "ml_t", "ml_e",
        "pk_t", "pk_e", "direct_lag", "role", "dC", "stated", "stated_kind", "ml_lo", "ml_hi", "aux")
BUILTIN = ("oracle", "plugin", "tolerant_v4", "tolerant_v4L")


def stated_kind_code(damage: dict) -> int:
    kind = damage.get("kind")
    if kind in KINDCODE and not any(key in damage for key in ("missing", "extra", "reversed")):
        return KINDCODE[kind]
    return KINDCODE[M.width_key(damage)]


def load_frozen(cfg: dict) -> dict:
    path = ROOT / cfg["frozen_calibration"]
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    want = cfg.get("frozen_calibration_sha256")
    if want is None or sha != want:
        raise SystemExit(f"frozen_calibration sha256 {sha} != config frozen_calibration_sha256 {want}")
    fac = {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    if "tolerant_v4L" in cfg["methods"]:
        old = {k: v for k, v in json.loads(ext_revlag._FROZEN.read_text(encoding="utf-8")).items()
               if k.startswith("mod|")}
        if any(fac.get(k) != v for k, v in old.items()):
            raise SystemExit("ext_revlag._FROZEN mod|* factors differ from frozen_calibration")
    return fac


def run_unit(args):
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    cfg, topo, t_idx, rep, calib, fac = args
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
    ext = ext_methods()
    cal = set(cfg.get("calibrate_methods", []))
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
                wk = M.width_key(skel.damage)
                res, extra = {}, {}
                for name in methods:
                    if name == "plugin":
                        res[name] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
                    elif name == "oracle":
                        if oracle_res is None:
                            oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                        res[name] = oracle_res
                    elif name == "tolerant_v4":
                        v3 = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                        res[name] = M.calibrate_width(v3, fac.get(f"mod|{T}|{wk}"), "tolerant_v4")
                    elif name == "tolerant_v4L":
                        r, thetas = ext_revlag.tolerant_v4L_draws(data, skel, lag_max, H, n_boot,
                                                                  rng(ext_seed("tolerant_v4L")))
                        res[name] = r
                        if thetas is not None:
                            extra[name] = lag_interval(thetas, H)
                    else:
                        raw = ext[name](data, skel, lag_max, H, n_boot, rng(ext_seed(name)))
                        if name in cal:
                            raw = M.calibrate_width(raw, fac.get(f"{name}|{T}|{wk}"), name)
                        res[name] = raw
                if kind == "ges":
                    role = np.full((n, n), -1)
                    dC = np.full((n, n), np.nan)
                else:
                    role = roles(sem, full, n)
                    dC = delta_C(sem, full, H)
                stated = KINDCODE[wk]
                skind = stated_kind_code(skel.damage)
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
                                  "is_null_sum": float(isc[null].sum()),
                                  "state": r.info.get("state"), "n_nonnull": int(nonnull.sum())})
                    ml_e = mean_lag(r.theta, H)
                    pk_e = peak_lag(r.theta, H)
                    k = len(jj)
                    mlo, mhi = extra.get(name, (np.full((n, n), np.nan), np.full((n, n), np.nan)))
                    aux = STATECODE.get(r.info.get("state"), -1)
                    vals = {"topo": [t_idx] * k, "rep": [rep] * k, "scen": [s_idx] * k, "T": [T] * k,
                            "cell": [cell_code] * k, "method": [m_idx] * k, "j": jj, "i": ii, "C_t": C_t[jj, ii],
                            "C_e": r.C[jj, ii], "lo": r.lo[jj, ii], "hi": r.hi[jj, ii], "ml_t": ml_t[jj, ii],
                            "ml_e": ml_e[jj, ii], "pk_t": pk_t[jj, ii], "pk_e": pk_e[jj, ii],
                            "direct_lag": direct[jj, ii], "role": role[jj, ii], "dC": dC[jj, ii],
                            "stated": [stated] * k, "stated_kind": [skind] * k, "ml_lo": mlo[jj, ii],
                            "ml_hi": mhi[jj, ii], "aux": [aux] * k}
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
    fac = load_frozen(cfg)
    ext = ext_methods()
    for name in cfg["methods"]:
        if name not in BUILTIN and name not in ext:
            raise SystemExit(f"unknown method {name}")
    calib = {}
    if cfg.get("learned"):
        calib = {"ges_damage": json.loads((ROOT / cfg["ges_damage_from"]).read_text(encoding="utf-8"))["ges_damage"]}
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib, fac) for t_idx, topo in enumerate(topologies)
            for rep in range(cfg["replicates"])]
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
    status = Counter((r["T"], cells[r["cell"]] if r["cell"] < len(cells) else str(r["cell"]), r["method"], r["status"])
                     for r in nulls)
    modules = {m: (ext[m].__module__ if m in ext and m not in BUILTIN else "built-in") for m in cfg["methods"]}
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_units": len(jobs),
                "n_pair_rows": len(allc["topo"]), "workers": args.workers, "method_modules": modules,
                "frozen_calibration_sha256": hashlib.sha256((ROOT / cfg["frozen_calibration"]).read_bytes()).hexdigest(),
                "python": sys.executable, "numpy": np.__version__,
                "status_counts": [{"T": k[0], "cell": k[1], "method": k[2], "status": k[3], "n": v}
                                  for k, v in sorted(status.items(), key=str)],
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(allc['topo'])} pair rows from {len(jobs)} units in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
