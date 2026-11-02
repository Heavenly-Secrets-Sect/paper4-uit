"""Driver of round 4, ID "ngorient" (docs/ext/r4ngorient.md).

Why a separate driver: the evaluation needs a non-Gaussian-shock generator (laws.py) and pair-level
plus evidence-diagnostic output, and generator.py / run_experiment.py must not be edited. The driver
re-uses the runner's own helpers (generator_config, unit_skeletons, public, ext_methods, ext_seed,
C_GRID, the unit seed formula and the cell index c_idx), so that with ``shock = "gauss"`` every
``tolerant_v5_1`` run reproduces the stored rows of results/ext_v51_eval exactly (checked by
check_pairing.py).

Per unit (topology x replicate): build the SEM as the runner (rng([unit, 0])), damaged skeletons as
the runner (rng([unit, 1, k_idx])), data for every T:
  gauss  -> DynamicSEM.simulate(T, rng([unit, 2, T]))           (the runner's data, unchanged)
  ng_*   -> laws.simulate(sem, T, rng([unit, 2, T]), node laws from rng([unit, 8]))
Methods: ``oracle`` (built-in stream rng(2), fitted once per T as the runner) and any ext method on
rng(ext_seed(stream_of.get(name, name))). ``stream_of`` lets an arm share v5_1's stream (common
random numbers: under a closed gate NG-A then reproduces v5_1's draws exactly).

phase "main": width factor per (name|T|width_key) from the frozen file (sha256 checked) for every
method in ``calibrate_methods``; rows, pairs and diagnostics written to results/<name>/.
phase "calibration": unit seed + 500 000 as the runner; collects |C_true - mid| and half-width on
non-null pairs per (name|T|width_key) for cells none/extra/missing/reversed and picks the factor
exactly as run_experiment.calibrate; writes results/<name>/calibration.json.

Methods never see truth; truth labels are attached to the evidence diagnostics here, outside.

Run:  python experiments/ext/r4ngorient/run_ng.py --config experiments/configs/ext_r4ngorient_<x>.json --workers 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "revlag"))
sys.path.insert(0, str(HERE))

import laws  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import C_GRID, ext_methods, ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from run_pairs import delta_C, roles  # noqa: E402  (experiments/ext/revlag, unchanged)

PCOLS = ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "dC", "role", "fac")


def cell_list(cfg):
    return [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]]


def sortability(data: np.ndarray, edges) -> dict:
    """Varsortability (Reisach, Seiler, Weichwald 2021) and R2-sortability (Reisach et al. 2023) of
    the observed series over ordered pairs (a, b) joined by a directed path of ``edges``: share of
    pairs with var(a) < var(b) (resp. R2(a) < R2(b)), ties 1/2. R2 of each node on all others."""
    n = data.shape[1]
    A = np.zeros((n, n), dtype=int)
    for u, v in edges:
        A[u, v] = 1
    reach = np.zeros((n, n), dtype=bool)
    P = A.copy()
    for _ in range(n):
        reach |= P > 0
        P = (P @ A > 0).astype(int)
    var = data.var(axis=0)
    Z = data - data.mean(axis=0)
    r2 = np.zeros(n)
    for j in range(n):
        X = np.delete(Z, j, axis=1)
        b = np.linalg.lstsq(X, Z[:, j], rcond=None)[0]
        res = Z[:, j] - X @ b
        r2[j] = 1 - float(res @ res) / float(Z[:, j] @ Z[:, j])
    a_idx, b_idx = np.nonzero(reach)
    if len(a_idx) == 0:
        return {"n_pairs": 0, "varsort": None, "r2sort": None}
    vs = np.mean((var[a_idx] < var[b_idx]) + 0.5 * (var[a_idx] == var[b_idx]))
    rs = np.mean((r2[a_idx] < r2[b_idx]) + 0.5 * (r2[a_idx] == r2[b_idx]))
    return {"n_pairs": int(len(a_idx)), "varsort": float(vs), "r2sort": float(rs)}


def label_diag(diag: dict, sem, full) -> dict:
    """Attach truth labels to the method's evidence records (evaluation only)."""
    lag0 = {e for e, lag in sem.edge_lag.items() if lag == 0}
    missing_lag0 = set()
    if full.damage.get("kind") == "missing":
        for e in full.log:
            u, v = e["pair"]
            if e.get("true_lag") == 0:
                missing_lag0.add(frozenset((u, v)))
    out = {"cands": [], "pool": [], "cand_tally": [], "pool_tally": [], "n_gate_draws": diag["n_gate_draws"]}
    for rec in diag["data_cands"]:
        u, v = rec[0], rec[1]
        true_uv = (u, v) in lag0
        true_vu = (v, u) in lag0
        out["cands"].append({"u": u, "v": v, "gate": bool(rec[2]), "pA": rec[3], "dl": rec[4] if len(rec) > 4 else None,
                             "pB": rec[5] if len(rec) > 5 else None, "true_contemp": bool(true_uv or true_vu),
                             "true_uv": bool(true_uv), "damaged_missing": frozenset((u, v)) in missing_lag0})
    for rec in diag["data_pool"]:
        u, v = rec[0], rec[1]
        out["pool"].append({"u": u, "v": v, "gate": bool(rec[2]), "pA": rec[3], "dl": rec[4] if len(rec) > 4 else None,
                            "wB": rec[5] if len(rec) > 5 else None, "reversed": bool((v, u) in lag0),
                            "true_lag0": bool((u, v) in lag0 or (v, u) in lag0)})
    for key, (n_pres, n_uv) in diag["cand_tally"].items():
        u, v = map(int, key.split("-"))
        true_uv, true_vu = (u, v) in lag0, (v, u) in lag0
        out["cand_tally"].append({"u": u, "v": v, "n": n_pres, "n_uv": n_uv, "true_contemp": bool(true_uv or true_vu),
                                  "true_uv": bool(true_uv), "damaged_missing": frozenset((u, v)) in missing_lag0})
    for key, (n_ev, n_fl) in diag["pool_tally"].items():
        u, v = map(int, key.split("-"))
        out["pool_tally"].append({"u": u, "v": v, "n": n_ev, "n_flip": n_fl, "reversed": bool((v, u) in lag0)})
    return out


def run_unit(args):
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    cfg, topo, t_idx, rep, fac, phase = args
    gen = generator_config(cfg)
    H, lag_max, n_boot, tau = cfg["H"], gen.lag_max, cfg["n_boot"], cfg["tau_effect"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    oracle_skel = true_skeleton(sem, with_lags=True)
    _, C_t, _, _ = truth_effects(sem, H)
    n = sem.n
    nonnull = ~np.eye(n, dtype=bool) & (np.abs(C_t) > tau)
    jj, ii = np.nonzero(nonnull)
    shock = cfg.get("shock", "gauss")
    node_law = laws.node_laws(shock, unit, n)
    ext = ext_methods()
    cal = set(cfg.get("calibrate_methods", []))
    stream_of = cfg.get("stream_of", {})
    methods = cfg["methods"] if phase == "main" else list(cfg["calibrate_methods"])
    only = set(cfg.get("only_cells") or [])
    only_T = {int(k): set(v) for k, v in (cfg.get("only_cells_by_T") or {}).items()}
    rows, diags, audit, calpairs = [], [], [], []
    pcols = {k: [] for k in PCOLS}
    lag0_edges = [e for e, lag in sem.edge_lag.items() if lag == 0]
    for T in cfg["T"]:
        if shock == "gauss":
            data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        else:
            data = laws.simulate(sem, T, np.random.default_rng([unit, 2, T]), node_law)
        audit.append({"topology": topo.id, "replicate": rep, "T": T, "shock": shock,
                      "laws": [lw for lw, _ in node_law],
                      "summary": sortability(data, list(sem.edge_lag)), "contemp": sortability(data, lag0_edges)})
        oracle_res = None
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            key = f"{kind}|{rate}"
            if only and key not in only:
                continue
            if T in only_T and key not in only_T[T]:
                continue
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)
            wk = M.width_key(skel.damage)
            res = {}
            for name in methods:
                if name == "oracle":
                    if oracle_res is None:
                        oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                    res[name] = oracle_res
                    continue
                t0 = time.perf_counter()
                raw = ext[name](data, skel, lag_max, H, n_boot, rng(ext_seed(stream_of.get(name, name))))
                sec = time.perf_counter() - t0
                diag = raw.info.pop("ng_diag", None) if raw.info else None
                if diag is not None:
                    diags.append({"topology": topo.id, "topo": t_idx, "replicate": rep, "T": T, "kind": kind,
                                  "rate": rate, "method": name, "shock": shock, **label_diag(diag, sem, full)})
                if phase == "calibration":
                    if kind in ("none", "extra", "missing", "reversed") and raw.status == "ok":
                        mid, half = (raw.lo + raw.hi) / 2, (raw.hi - raw.lo) / 2
                        calpairs.append({"cell": f"{name}|{T}|{wk}", "dist": np.abs(C_t - mid)[nonnull].tolist(),
                                         "half": half[nonnull].tolist()})
                    continue
                if name in cal:
                    raw = M.calibrate_width(raw, fac.get(f"{name}|{T}|{wk}"), name)
                raw.info["seconds"] = round(sec, 3)
                res[name] = raw
            if phase == "calibration":
                continue
            dC = delta_C(sem, full, H)
            role = roles(sem, full, n)
            for m_idx, name in enumerate(methods):
                r = res[name]
                row = evaluate(sem, r, H, tau_effect=tau)
                row.update({"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind,
                            "rate": rate, "k": skel.damage.get("k", 0), "scenario": shock})
                rows.append(row)
                if r.status != "ok":
                    continue
                k = len(jj)
                vals = {"topo": [t_idx] * k, "rep": [rep] * k, "T": [T] * k, "cell": [c_idx] * k,
                        "method": [m_idx] * k, "j": jj, "i": ii, "C_t": C_t[jj, ii], "C_e": r.C[jj, ii],
                        "lo": r.lo[jj, ii], "hi": r.hi[jj, ii], "dC": dC[jj, ii], "role": role[jj, ii],
                        "fac": [r.info.get("c_T", 1.0) or 1.0] * k}
                for key2 in PCOLS:
                    pcols[key2].extend(np.asarray(vals[key2]).tolist())
    return {"rows": rows, "diags": diags, "audit": audit, "pairs": pcols, "calpairs": calpairs}


def load_frozen(cfg) -> dict:
    if not cfg.get("frozen_calibration"):
        return {}
    path = ROOT / cfg["frozen_calibration"]
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != cfg.get("frozen_calibration_sha256"):
        raise SystemExit(f"frozen_calibration sha256 {sha} != config {cfg.get('frozen_calibration_sha256')}")
    return {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if not k.startswith("_")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-units", type=int, default=0)
    ap.add_argument("--out-suffix", default="")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    phase = cfg.get("phase", "main")
    for b in ("P4-H1", "P4-H2"):
        if cfg["bank"] == b:
            raise SystemExit(f"bank {b} is off limits for this direction")
    if cfg["split"] != "development":
        raise SystemExit("only development splits are allowed")
    fac = load_frozen(cfg) if phase == "main" else {}
    ext = ext_methods()
    for name in (cfg["methods"] if phase == "main" else cfg["calibrate_methods"]):
        if name != "oracle" and name not in ext:
            raise SystemExit(f"unknown method {name}")
    if phase == "main":
        for name in cfg.get("calibrate_methods", []):
            for T in cfg["T"]:
                for wk in ("none", "extra", "missing", "reversed"):
                    if f"{name}|{T}|{wk}" not in fac:
                        raise SystemExit(f"missing width factor {name}|{T}|{wk}")
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, fac, phase) for t_idx, topo in enumerate(topologies)
            for rep in range(cfg["replicates"])]
    if a.max_units:
        jobs = jobs[: a.max_units]
    start = time.perf_counter()
    out = ROOT / "results" / (cfg["name"] + a.out_suffix)
    out.mkdir(parents=True, exist_ok=True)
    rows, diags, audit, calpairs = [], [], [], []
    pcols = {k: [] for k in PCOLS}
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(run_unit, jobs):
            rows.extend(res["rows"])
            diags.extend(res["diags"])
            audit.extend(res["audit"])
            calpairs.extend(res["calpairs"])
            for k, v in res["pairs"].items():
                pcols[k].extend(v)
    secs = round(time.perf_counter() - start, 1)
    if phase == "calibration":
        by = defaultdict(lambda: ([], []))
        for p in calpairs:
            by[p["cell"]][0].extend(p["dist"])
            by[p["cell"]][1].extend(p["half"])
        result = {}
        for cell, (dist, half) in sorted(by.items()):
            dist, half = np.array(dist), np.array(half)
            cov = np.array([(dist <= c * half).mean() for c in C_GRID])
            target = min(1 - M.ALPHA, cov.max() - 0.005)
            result[cell] = float(C_GRID[np.argmax(cov >= target)])
        (out / "calibration.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(out / "diag.jsonl", "w", encoding="utf-8") as fh:
        for r in diags:
            fh.write(json.dumps(r) + "\n")
    with open(out / "audit.jsonl", "w", encoding="utf-8") as fh:
        for r in audit:
            fh.write(json.dumps(r) + "\n")
    if pcols["topo"]:
        np.savez_compressed(out / "pairs.npz", methods=np.array(cfg["methods"]),
                            cells=np.array([f"{k}|{r}" for k, r in cell_list(cfg)]),
                            **{k: np.asarray(v, dtype=float) for k, v in pcols.items()})
    import platform
    manifest = {"config": cfg, "phase": phase, "seconds": secs, "n_units": len(jobs), "n_rows": len(rows),
                "n_diag": len(diags), "workers": a.workers, "python": sys.executable, "numpy": np.__version__,
                "platform": platform.platform(),
                "method_modules": {m: (ext[m].__module__ if m in ext else "built-in")
                                   for m in (cfg["methods"] if phase == "main" else cfg["calibrate_methods"])},
                "frozen_calibration_sha256": cfg.get("frozen_calibration_sha256"),
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows, {len(diags)} diag records, {len(jobs)} units in {secs} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
