"""Pair-level rows for RQ4.1 (error by true lag and by edge role) and RQ4.4 (truth-free flags).

The runner (experiments/run_experiment.py) stores one row per run with medians over pairs, so a
breakdown by the true lag of a pair or by its role relative to the damaged edges cannot be formed
from the stored results. This script re-runs the seeds of ``a2_baselines`` / ``a2b_pselect``
exactly (same unit seeds, same damaged skeletons, same data, same method rng streams), so every
pooled number it produces must equal the stored summaries; ``analyze_pairs.py`` checks this.

Per (topology, replicate, T, damage cell, method), for every non-null ordered pair (|C_true| > tau):
- estimate, interval, mean lag and peak lag (estimated and true);
- truth-side labels used only by the evaluation: lag of the pair's direct edge (-1 = no direct
  edge, the effect runs through other nodes only) and role relative to the damage log
  (0 untouched, 1 downstream: some true path i ~> a -> b ~> j runs through a damaged edge a -> b,
  2 damaged: the pair's own edge is the damaged one).
For the module (``tolerant_v4``) the script also stores signals that need no truth:
- ``rel_width``  interval width / |C_hat|
- ``width``      interval width
- ``zero_in``    1 if the interval contains 0
- ``struct_sens`` |C_module - C_plugin| / module width
- ``resid_lb``   max over the two endpoint equations of the Ljung-Box Q(4) of the module's base-fit
                 structural residuals (base fit = the module's own terms before repair draws)
- ``rx_pair``    |corr| of the two endpoints' structural residuals
- ``rx_end``     max |corr| between an endpoint's residual and the residual of any node the
                 skeleton leaves non-adjacent to that endpoint
- ``coef_stab``  |C_A - C_B| / module width, A and B the first and last 60% of the sample, each
                 fitted with the module's base terms (NaN when a window is underdetermined)
- ``lag_stab``   |mean lag_A - mean lag_B| on the same windows (NaN when undefined)
and per fit: ``n_repair`` (restored contemporaneous edges), ``n_pool`` (size of the reversal
pool, 0 when no reversal is stated), ``n_resid_bh`` (non-adjacent pairs with BH-significant
residual correlation in the base fit, uncapped).
Null pairs are summarised per run: how many intervals exclude 0 (false signals).

Methods never see the truth: they get the data and the damaged skeleton with its stated damage.
The module width factors are read from results/a2_baselines/calibration.json (tuned on D-07H
development by the runner's calibration phase with the same config), so they are identical to
the factors used in a2_baselines.

Run:  python experiments/ext/metrics/run_pairs.py --config experiments/configs/ext_metrics_pairs.json --workers 3
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
from paper4.effects import cumulative, irf, mean_lag, peak_lag  # noqa: E402
from paper4.estimator import fit_equations, parent_terms, soft_terms  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402
from run_experiment import generator_config, unit_skeletons  # noqa: E402  (read-only import)

METHOD_TAG = {"plugin": 1, "oracle": 2, "tolerant_v4": 6, "ida_union": 7, "bvar_minnesota": 8, "pselect_union": 9}
SIGNALS = ("rel_width", "width", "zero_in", "struct_sens", "resid_lb", "rx_pair", "rx_end", "coef_stab", "lag_stab",
           "n_repair", "n_pool", "n_resid_bh")


def ljung_box(x: np.ndarray, L: int = 4) -> float:
    x = x - x.mean()
    m = len(x)
    d = x @ x
    if d <= 0:
        return 0.0
    q = 0.0
    for k in range(1, L + 1):
        r = (x[k:] @ x[:-k]) / d
        q += r * r / (m - k)
    return float(m * (m + 2) * q)


def module_terms(skel, lag_max):
    full = M.stated_counts(skel.damage)["missing"] > 0
    return [(soft_terms if full else parent_terms)(skel, j, lag_max) for j in range(skel.n)]


def window_effects(data, terms, lag_max, H, share):
    T = len(data)
    w = int(round(share * T))
    out = []
    for part in (data[:w], data[T - w:]):
        f = fit_equations(part, terms, lag_max)
        if f.status != "ok":
            return None
        th = irf(f.B, H)
        out.append((cumulative(th, H), mean_lag(th, H)))
    return out


def roles(sem, skel, n):
    """role[j, i] for the effect of i on j: 2 damaged pair, 1 downstream of a damaged edge, 0 untouched."""
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
        if kind == "missing":  # log pairs are sorted; orient as in the truth
            a, b = (u, v) if (u, v) in sem.edge_lag else (v, u)
        else:                   # reversed: original (true) orientation; extra: orientation in the damaged skeleton
            a, b = u, v
        down = np.outer(reach[:, a], reach[b, :]).T   # down[j, i] = reach[i, a] & reach[b, j]
        role = np.maximum(role, down.astype(int))
        role[b, a] = 2
        if kind == "extra":
            role[a, b] = max(role[a, b], 0)
    return role


def run_unit(args):
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
    cols = {k: [] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "ml_t", "ml_e",
                            "pk_t", "pk_e", "direct_lag", "role", *SIGNALS)}
    nulls = []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        oracle_res = None
        for c_idx, ((kind, rate), skel) in enumerate(skels.items()):
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            res = {}
            if "plugin" in methods or "tolerant_v4" in methods:
                res["plugin"] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
            if "oracle" in methods:
                if oracle_res is None:
                    oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                res["oracle"] = oracle_res
            if "lp_allpast" in methods:
                res["lp_allpast"] = M.lp_allpast(data, skel, lag_max, H)
            if "tolerant_v4" in methods:
                v3 = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                res["tolerant_v4"] = M.calibrate_width(v3, calib.get(f"mod|{T}|{M.width_key(skel.damage)}"),
                                                       "tolerant_v4")
            if "ida_union" in methods:
                res["ida_union"] = M.ida_union(data, skel, lag_max, H, n_boot, rng(7))
            if "bvar_minnesota" in methods:
                res["bvar_minnesota"] = M.bvar_minnesota(data, skel, lag_max, H, n_boot, rng(8))
            if "pselect_union" in methods:
                res["pselect_union"] = M.pselect_union(data, skel, lag_max, H, n_boot, rng(9))
            role = roles(sem, skel, n)

            # truth-free signals of the module
            sig = None
            mod = res.get("tolerant_v4")
            if mod is not None and mod.status == "ok":
                terms = module_terms(skel, lag_max)
                f0 = fit_equations(data, terms, lag_max)
                width = mod.hi - mod.lo
                eps = 1e-9
                sig = {k: np.full((n, n), np.nan) for k in SIGNALS}
                sig["rel_width"] = width / (np.abs(mod.C) + eps)
                sig["width"] = width
                sig["zero_in"] = ((mod.lo <= 0) & (0 <= mod.hi)).astype(float)
                if res["plugin"].status == "ok":
                    sig["struct_sens"] = np.abs(mod.C - res["plugin"].C) / (width + eps)
                if f0.status == "ok":
                    R = f0.residuals
                    lb = np.array([ljung_box(R[:, k]) for k in range(n)])
                    corr = np.abs(np.corrcoef(R.T))
                    np.fill_diagonal(corr, 0.0)
                    adj = skel.adjacency().astype(bool) | np.eye(n, dtype=bool)
                    rx_node = np.where(~adj, corr, 0.0).max(axis=1)
                    sig["resid_lb"] = np.maximum(lb[:, None], lb[None, :])
                    sig["rx_pair"] = corr
                    sig["rx_end"] = np.maximum(rx_node[:, None], rx_node[None, :])
                    sig["n_resid_bh"][:] = len(M.repair_candidates(R, skel, cap=10 ** 6))
                win = window_effects(data, terms, lag_max, H, cfg["window_share"])
                if win is not None:
                    (CA, mlA), (CB, mlB) = win
                    sig["coef_stab"] = np.abs(CA - CB) / (width + eps)
                    sig["lag_stab"] = np.abs(mlA - mlB)
                sig["n_repair"][:] = mod.info.get("n_repair", 0)
                pool = mod.info.get("n_reversal_pool")
                sig["n_pool"][:] = 0 if pool is None else pool

            for m_idx, name in enumerate(methods):
                r = res[name]
                if r.status != "ok":
                    continue
                if r.lo is not None:
                    excl = ~((r.lo <= 0) & (0 <= r.hi))
                    nulls.append({"topo": t_idx, "rep": rep, "T": T, "cell": c_idx, "method": name,
                                  "n_null": int(null.sum()), "n_null_excl0": int((excl & null).sum()),
                                  "n_null_reach": int((null & (r.C != 0)).sum())})
                ml_e = mean_lag(r.theta, H) if r.theta is not None else np.full((n, n), np.nan)
                pk_e = peak_lag(r.theta, H) if r.theta is not None else np.full((n, n), -1)
                k = len(jj)
                cols["topo"] += [t_idx] * k
                cols["rep"] += [rep] * k
                cols["T"] += [T] * k
                cols["cell"] += [c_idx] * k
                cols["method"] += [m_idx] * k
                cols["j"] += jj.tolist()
                cols["i"] += ii.tolist()
                cols["C_t"] += C_t[jj, ii].tolist()
                cols["C_e"] += r.C[jj, ii].tolist()
                cols["lo"] += (r.lo[jj, ii] if r.lo is not None else np.full(k, np.nan)).tolist()
                cols["hi"] += (r.hi[jj, ii] if r.hi is not None else np.full(k, np.nan)).tolist()
                cols["ml_t"] += ml_t[jj, ii].tolist()
                cols["ml_e"] += ml_e[jj, ii].tolist()
                cols["pk_t"] += pk_t[jj, ii].tolist()
                cols["pk_e"] += np.asarray(pk_e)[jj, ii].tolist()
                cols["direct_lag"] += direct[jj, ii].tolist()
                cols["role"] += role[jj, ii].tolist()
                for s in SIGNALS:
                    cols[s] += (sig[s][jj, ii] if (sig is not None and name == "tolerant_v4")
                                else np.full(k, np.nan)).tolist()
    return cols, nulls


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-units", type=int, default=0, help="timing probe: stop after this many units")
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    calib = json.loads((ROOT / cfg["module_width_factors_from"]).read_text(encoding="utf-8"))
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib) for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    if args.max_units:
        jobs = jobs[: args.max_units]
    start = time.perf_counter()
    allc = None
    nulls = []
    with ProcessPoolExecutor(args.workers) as pool:
        for cols, nl in pool.map(run_unit, jobs):
            if allc is None:
                allc = {k: list(v) for k, v in cols.items()}
            else:
                for k, v in cols.items():
                    allc[k].extend(v)
            nulls.extend(nl)
    out = ROOT / "results" / (cfg["name"] + ("_probe" if args.max_units else ""))
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "pairs.npz", methods=np.array(cfg["methods"]),
                        cells=np.array([f"{k}|{r}" for k, r in [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"]
                                                                                for r in cfg["damage"]["rates"]]]),
                        **{k: np.asarray(v, dtype=float) for k, v in allc.items()})
    with open(out / "nullpairs.jsonl", "w", encoding="utf-8") as fh:
        for r in nulls:
            fh.write(json.dumps(r) + "\n")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_units": len(jobs),
                "n_pair_rows": len(allc["topo"]),
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(allc['topo'])} pair rows from {len(jobs)} units in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
