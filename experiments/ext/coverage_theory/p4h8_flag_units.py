"""P4-H8 reliability-flag dump (feedback point 5): per-pair features of the method output for non-null pairs.

Same units, seeds and cells as p4h7_units.py (calibration phase of the runner); a wrapper around tolerant_v5_1 records
the raw output of each run, and the non-null pair set is rebuilt from the truth exactly as the runner does. The
features use only what a user has at deployment (the interval, the stated skeleton, the stated damage, T); the
truth only enters the stored columns dist and half that define the label offline. Protocol: docs/ext/p4h8_flag_spec.md.

    python experiments/ext/coverage_theory/p4h8_flag_units.py --split calibration --out results/ext_p4h8_flag/calibration.npz
The test split is refused unless --confirm-frozen is given and the frozen flag file exists.
"""
import argparse
import sys
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(REPO / "experiments"), str(HERE)]
import run_experiment as R  # noqa: E402
from p4h7_units import build_cfg  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

FEATURES = ["mid", "half", "ratio", "zero_in", "logT", "lag", "k_miss", "k_extra", "k_rev", "has_path", "path_len",
            "adjacent", "out_deg_cause", "in_deg_effect", "row_med_half", "col_med_half", "half_rank", "v51_ratio",
            "v51_targeted", "n_repair", "dist"]  # "dist" is the label ingredient, not a feature
_REC = []
_WRAPPED = [False]


def _wrap():
    if _WRAPPED[0]:
        return
    _WRAPPED[0] = True
    reg = R.ext_methods()
    orig = reg["tolerant_v5_1"]

    def wrapper(data, skel, lag_max, H, n_boot, rng):
        res = orig(data, skel, lag_max, H, n_boot, rng)
        _REC.append({"T": data.shape[0], "status": res.status, "oriented": sorted(skel.oriented),
                     "damage": dict(skel.damage), "C": None if res.status != "ok" else np.array(res.C),
                     "lo": None if res.status != "ok" else np.array(res.lo), "hi": None if res.status != "ok" else np.array(res.hi),
                     "info": dict(res.info)})
        return res

    reg["tolerant_v5_1"] = wrapper


def _paths(oriented, n):
    adj = [[] for _ in range(n)]
    for u, v in oriented:
        adj[u].append(v)
    dist = np.full((n, n), np.inf)
    for s in range(n):
        dq = deque([s])
        d = {s: 0}
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if w not in d:
                    d[w] = d[u] + 1
                    dq.append(w)
        for t, dd in d.items():
            dist[s, t] = dd
    return dist


def unit(args):
    cfg, topo, t_idx, lag = args
    _wrap()
    _REC.clear()
    out = R.run_unit((cfg, topo, t_idx, 0, None, "calibration"))
    # truth and non-null mask, as in the runner
    seed = cfg["seed_base"] + 500_000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, R.generator_config(cfg), np.random.default_rng([seed, 0]))
    _, C_true, _, _ = truth_effects(sem, cfg["H"])
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    cells = [p["cell"] for p in out["pairs"] if p["cell"].startswith("tolerant_v5_1|")]
    ok = [r for r in _REC if r["status"] == "ok"]
    assert len(cells) == len(ok), (len(cells), len(ok))
    rows = []
    n = sem.n
    for cell, rec in zip(cells, ok):
        half = (rec["hi"] - rec["lo"]) / 2
        mid = rec["C"]
        off = ~np.eye(n, dtype=bool)
        hdist = _paths(rec["oriented"], n)
        outdeg = np.bincount([u for u, v in rec["oriented"]], minlength=n)
        indeg = np.bincount([v for u, v in rec["oriented"]], minlength=n)
        rank = np.zeros((n, n))
        vals = half[off]
        order = vals.argsort().argsort() / max(len(vals) - 1, 1)
        rank[off] = order
        row_med = np.array([np.median(half[i][off[i]]) for i in range(n)])
        col_med = np.array([np.median(half[:, j][off[:, j]]) for j in range(n)])
        info = rec["info"]
        d = rec["damage"]
        for i, j in np.argwhere(nonnull):
            rows.append([mid[i, j], half[i, j], abs(mid[i, j]) / (half[i, j] + 1e-9),
                         float(mid[i, j] - half[i, j] <= 0 <= mid[i, j] + half[i, j]), np.log(rec["T"]), lag,
                         d.get("missing", 0), d.get("extra", 0), d.get("reversed", 0), float(np.isfinite(hdist[i, j])),
                         hdist[i, j] if np.isfinite(hdist[i, j]) else 99.0, float((i, j) in set(map(tuple, rec["oriented"]))),
                         outdeg[i], indeg[j], row_med[i], col_med[j], rank[i, j], float(info.get("v51_ratio") or 0.0),
                         float(info.get("v51_targeted") or 0.0), float(info.get("n_repair") or 0.0), abs(C_true[i, j] - mid[i, j])])
    return {"cells": cells, "rows": rows, "n_pairs": [int(nonnull.sum())] * len(cells), "topo": t_idx, "ok": len(ok)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="P4-H8")
    ap.add_argument("--split", required=True, choices=["design", "calibration", "test"])
    ap.add_argument("--lag", type=int, default=1)
    ap.add_argument("--T", default="19,30,40,80,150")
    ap.add_argument("--seed-base", type=int, default=20261116)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-topologies", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm-frozen", action="store_true")
    ap.add_argument("--frozen", default="experiments/calibration/p4h8_flag_frozen.json")
    a = ap.parse_args(argv)
    if a.split == "test" and not (a.confirm_frozen and (REPO / a.frozen).exists()):
        raise SystemExit("the test split is run once, after the flag model is frozen")
    cfg = build_cfg(a.split, a.T, a.seed_base, a.lag, "0.2,0.5")
    topologies = load_bank(a.bank, a.split)[: a.max_topologies]
    ccfg = dict(cfg, replicates=1)
    jobs = [(ccfg, topo, t_idx, a.lag) for t_idx, topo in enumerate(topologies)]
    t0 = time.perf_counter()
    X, cell_ids, groups, pair_counts = [], [], [], []
    with ProcessPoolExecutor(a.workers) as pool:
        for i, res in enumerate(pool.map(unit, jobs)):
            k = 0
            for cell, npairs in zip(res["cells"], res["n_pairs"]):
                for _ in range(npairs):
                    cell_ids.append(cell)
                    groups.append(res["topo"])
                k += npairs
            X.extend(res["rows"])
            if i % 50 == 0:
                print(i, round(time.perf_counter() - t0), "s", flush=True)
    X = np.array(X, dtype=float)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, X=X, cell=np.array(cell_ids), group=np.array(groups), features=np.array(FEATURES),
                        bank=a.bank, split=a.split, lag=a.lag, seed_base=a.seed_base)
    print("done", X.shape, round(time.perf_counter() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
