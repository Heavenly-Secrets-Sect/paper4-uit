"""RQ4.3: which skeleton edge, when wrong, moves the effect most, and is that stable across topologies?

For every true edge e of every (topology, replicate): damage only e (delete it; additionally
reverse it when it is contemporaneous), refit on a long series, and record for every non-null
target pair (i -> j) the shift of the estimated C(H) away from the estimate on the true skeleton.
A long series isolates the bias a wrong edge causes from sampling noise.

Edges are labelled by their role relative to the target pair, not by identity, so the map can
transfer to other topologies:
- ``on_path``     the edge lies on a directed path i ~> j
- ``into_source`` the edge points into i
- ``into_target`` the edge points into j and is not on a path from i
- ``other``       anything else
Stability: the cost by role is compared across topology profiles (Erdos-Renyi vs scale-free hub)
and across the development and confirmatory halves of the bank.

Run:  python experiments/run_edge_cost.py [--T 2000] [--replicates 2] [--workers 10]
Writes results/rq43_edge_cost/{pairs.jsonl, summary.md}.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paper4 import methods as M  # noqa: E402
from paper4.generator import GeneratorConfig, build_dynamic_sem  # noqa: E402
from paper4.metrics import truth_effects  # noqa: E402
from paper4.skeleton import _creates_cycle, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

H, LAG_MAX, TAU = 4, 2, 0.1
ROLES = ("on_path", "into_source", "into_target", "other")


def descendants(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    children = defaultdict(set)
    for u, v in edges:
        children[u].add(v)
    out = []
    for s in range(n):
        seen, stack = set(), [s]
        while stack:
            for c in children[stack.pop()]:
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        out.append(seen)
    return out


def role(edge, i, j, desc) -> str:
    a, b = edge
    reach_a = a == i or a in desc[i]
    if reach_a and (b == j or j in desc[b]):
        return "on_path"
    if b == i:
        return "into_source"
    if b == j:
        return "into_target"
    return "other"


def run_unit(args):
    topo, t_idx, rep, T, seed_base, split = args
    unit = seed_base + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, GeneratorConfig(lag_max=LAG_MAX), np.random.default_rng([unit, 0]))
    data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
    truth = true_skeleton(sem)
    _, C_true, _, _ = truth_effects(sem, H)
    base = M.plugin(data, truth, LAG_MAX, H, 0, None).C
    edges = set(sem.edge_lag)
    desc = descendants(sem.n, edges)
    off = ~np.eye(sem.n, dtype=bool)
    targets = [(i, j) for j in range(sem.n) for i in range(sem.n) if off[j, i] and abs(C_true[j, i]) > TAU]
    rows = []
    for e, lag in sorted(sem.edge_lag.items()):
        variants = [("missing", truth.copy())]
        variants[0][1].oriented.discard(e)
        if lag == 0:
            rev = truth.copy()
            trial = (rev.oriented - {e}) | {(e[1], e[0])}
            if not _creates_cycle(trial, sem.n):
                rev.oriented = trial
                variants.append(("reversed", rev))
        for kind, skel in variants:
            C_hat = M.plugin(data, skel, LAG_MAX, H, 0, None).C
            for i, j in targets:
                rows.append({
                    "topology": topo.id, "profile": topo.profile, "split": split, "replicate": rep,
                    "edge": list(e), "edge_lag": lag, "kind": kind, "role": role(e, i, j, desc),
                    "target": [i, j], "C_true": float(C_true[j, i]),
                    "shift": float(C_hat[j, i] - base[j, i]),
                    "rel_shift": float(abs(C_hat[j, i] - base[j, i]) / abs(C_true[j, i])),
                })
    return rows


def summarize(rows: list[dict], T: int) -> str:
    def cell(sel):
        v = np.array([r["rel_shift"] for r in sel])
        if not len(v):
            return "–"
        return f"{np.median(v):.3f} / {np.mean(v > 0.2):.2f} (n={len(v)})"

    lines = [
        "# RQ4.3: cost of one wrong edge, by role relative to the target pair", "",
        f"Point estimate (`plugin`) on a series of T = {T}, H = {H}. Cost of a wrong edge for a target pair = "
        "|C_hat(damaged) - C_hat(true skeleton)| / |C_true|. Cells: median relative shift / share of pairs shifted by more than 20%.",
        "",
        "| damage | edge lag | role | all | Erdos-Renyi | scale-free hub | development | confirmatory |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for kind in ("missing", "reversed"):
        for lagsel, label in ((lambda r: r["edge_lag"] == 0, "contemporaneous"), (lambda r: r["edge_lag"] > 0, "lagged")):
            for rl in ROLES:
                sel = [r for r in rows if r["kind"] == kind and lagsel(r) and r["role"] == rl]
                if not sel:
                    continue
                lines.append(
                    f"| {kind} | {label} | {rl} | {cell(sel)} | "
                    f"{cell([r for r in sel if r['profile'] == 'erdos_renyi'])} | "
                    f"{cell([r for r in sel if r['profile'] == 'scale_free_hub'])} | "
                    f"{cell([r for r in sel if r['split'] == 'development'])} | "
                    f"{cell([r for r in sel if r['split'] == 'confirmatory'])} |")

    # stability: rank correlation of role-x-kind-x-lag median costs between the two splits and profiles
    def medians(filter_fn):
        out = {}
        for kind in ("missing", "reversed"):
            for lagc in ("c", "l"):
                for rl in ROLES:
                    v = [r["rel_shift"] for r in rows if r["kind"] == kind and r["role"] == rl
                         and ((r["edge_lag"] == 0) == (lagc == "c")) and filter_fn(r)]
                    if len(v) >= 20:
                        out[(kind, lagc, rl)] = float(np.median(v))
        return out

    def spearman(a, b):
        keys = sorted(a.keys() & b.keys())
        if len(keys) < 3:
            return float("nan"), len(keys)
        ra = np.argsort(np.argsort([a[k] for k in keys]))
        rb = np.argsort(np.argsort([b[k] for k in keys]))
        return float(np.corrcoef(ra, rb)[0, 1]), len(keys)

    s1 = spearman(medians(lambda r: r["split"] == "development"), medians(lambda r: r["split"] == "confirmatory"))
    s2 = spearman(medians(lambda r: r["profile"] == "erdos_renyi"), medians(lambda r: r["profile"] == "scale_free_hub"))
    lines += ["", "## Stability of the role map", "",
              f"- Spearman correlation of median cost by (damage, lag, role), development vs confirmatory topologies: "
              f"{s1[0]:.2f} over {s1[1]} cells",
              f"- Erdos-Renyi vs scale-free hub: {s2[0]:.2f} over {s2[1]} cells"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--T", type=int, default=2000)
    parser.add_argument("--replicates", type=int, default=2)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--seed-base", type=int, default=20261201)
    args = parser.parse_args(argv)
    jobs = []
    for split in ("development", "confirmatory"):
        for t_idx, topo in enumerate(load_bank("D-07", split)):
            for rep in range(args.replicates):
                jobs.append((topo, t_idx + (100 if split == "confirmatory" else 0), rep, args.T, args.seed_base, split))
    with ProcessPoolExecutor(args.workers) as pool:
        rows = [r for rs in pool.map(run_unit, jobs) for r in rs]
    out = ROOT / "results" / "rq43_edge_cost"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "pairs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    (out / "summary.md").write_text(summarize(rows, args.T), encoding="utf-8")
    print(f"{len(rows)} rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
