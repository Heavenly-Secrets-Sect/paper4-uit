"""D-07 Topology Bank Generator (Option B: 40 DAGs, Dual-Profile).

Generates 40 synthetic DAG topologies (14 nodes, 21 edges) for Enhanced v2
confirmatory evaluation per docs/enhanced_v2_protocol_claim_map.md (D-07 & D-04):
- 14 variables from Core Reference Subset (tier1_core14)
- Exactly 21 directed edges per graph (average degree d = 3.0)
- Dual-profile topology structure:
  * 50% Erdős-Rényi (ER) random DAGs (20 DAGs: 10 dev, 10 conf)
  * 50% Scale-Free / Hub Networks (20 DAGs: 10 dev, 10 conf, max out-degree >= 4)
- 100% acyclic, weakly connected, with >= 3 unshielded colliders (v-structures)
- Strict symmetric split: 20 development (00-19) and 20 confirmatory (20-39)
- Canonical JSON output with LF line endings and fixed SHA-256 manifest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from itertools import combinations
from pathlib import Path

SEED = 20260924
BANK_DIR = Path(__file__).resolve().parents[1]
DAGS_DIR = BANK_DIR / "topologies"
MANIFEST_NAME = "d07_manifest.json"
MANIFEST_PATH = BANK_DIR / MANIFEST_NAME

CORE14_NODES = [
    "bank_npl_ratio",
    "bank_car_ratio",
    "bank_nim_ratio",
    "bank_roe_ratio",
    "bank_ldr_ratio",
    "bank_provision_coverage_proxy_pct",
    "bank_z_score",
    "macro_gdp_yoy_pct",
    "macro_cpi_avg_pct",
    "macro_policy_rate_pct",
    "stock_adj_close_last_vnd",
    "stock_return_qoq_pct",
    "stock_avg_daily_volume_cp",
    "stock_avg_daily_trade_value_vnd",
]

MACRO_NODES = [
    "macro_gdp_yoy_pct",
    "macro_cpi_avg_pct",
    "macro_policy_rate_pct",
]


def count_v_structures(nodes: list[str], edges: list[list[str]]) -> int:
    adj_in: dict[str, set[str]] = {n: set() for n in nodes}
    edge_set = {(u, v) for u, v in edges}
    for u, v in edges:
        adj_in[v].add(u)
    v_structures = set()
    for w, parents in adj_in.items():
        if len(parents) >= 2:
            for u, v in combinations(sorted(parents), 2):
                if (u, v) not in edge_set and (v, u) not in edge_set:
                    v_structures.add((u, w, v))
    return len(v_structures)


def is_connected(nodes: list[str], edges: list[list[str]]) -> bool:
    adj: dict[str, set[str]] = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    visited = set()
    stack = [nodes[0]]
    while stack:
        curr = stack.pop()
        if curr not in visited:
            visited.add(curr)
            stack.extend(adj[curr] - visited)
    return len(visited) == len(nodes)


def is_acyclic(nodes: list[str], edges: list[list[str]]) -> bool:
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    in_degree: dict[str, int] = {n: 0 for n in nodes}
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    queue = [n for n in nodes if in_degree[n] == 0]
    visited = 0
    while queue:
        curr = queue.pop(0)
        visited += 1
        for nxt in adj[curr]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)
    return visited == len(nodes)


def sha256_text(text: str) -> str:
    raw = text.encode("utf-8").replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


def generate_er_dag(rng: random.Random, nodes: list[str], n_edges: int = 21) -> list[list[str]]:
    while True:
        perm = list(nodes)
        rng.shuffle(perm)
        all_possible = []
        for i in range(len(perm)):
            for j in range(i + 1, len(perm)):
                all_possible.append((perm[i], perm[j]))
        sampled = rng.sample(all_possible, n_edges)
        edges = [[u, v] for u, v in sorted(sampled)]
        if not is_connected(nodes, edges):
            continue
        if count_v_structures(nodes, edges) < 3:
            continue
        if not is_acyclic(nodes, edges):
            continue
        return edges


def generate_hub_dag(rng: random.Random, nodes: list[str], n_edges: int = 21) -> list[list[str]]:
    while True:
        # Select 1-2 macro nodes as primary hubs, place them early in topological sort
        hubs = rng.sample(MACRO_NODES, rng.choice([1, 2]))
        other_nodes = [n for n in nodes if n not in hubs]
        rng.shuffle(other_nodes)
        perm = hubs + other_nodes

        all_pairs = []
        for i in range(len(perm)):
            for j in range(i + 1, len(perm)):
                all_pairs.append((perm[i], perm[j]))

        edges_set: set[tuple[str, str]] = set()
        primary_hub = hubs[0]
        primary_idx = perm.index(primary_hub)
        primary_targets = perm[primary_idx + 1:]
        hub_degree = rng.randint(4, min(6, len(primary_targets)))
        for target in rng.sample(primary_targets, hub_degree):
            edges_set.add((primary_hub, target))

        if len(hubs) > 1:
            sec_hub = hubs[1]
            sec_idx = perm.index(sec_hub)
            sec_targets = [n for n in perm[sec_idx + 1:] if (sec_hub, n) not in edges_set]
            if len(sec_targets) >= 3:
                sec_degree = rng.randint(3, min(5, len(sec_targets)))
                for target in rng.sample(sec_targets, sec_degree):
                    edges_set.add((sec_hub, target))

        remaining_needed = n_edges - len(edges_set)
        if remaining_needed < 0:
            continue

        remaining_candidates = [pair for pair in all_pairs if pair not in edges_set]

        # Preferential attachment: weight candidate (u, v) based on out-degree of u
        curr_out: dict[str, int] = {n: 0 for n in perm}
        for u, v in edges_set:
            curr_out[u] += 1

        while len(edges_set) < n_edges and remaining_candidates:
            weights = [(curr_out[u] + 1) ** 1.5 for u, v in remaining_candidates]
            chosen = rng.choices(remaining_candidates, weights=weights, k=1)[0]
            edges_set.add(chosen)
            curr_out[chosen[0]] += 1
            remaining_candidates.remove(chosen)

        if len(edges_set) != n_edges:
            continue

        edges = [[u, v] for u, v in sorted(edges_set)]
        if not is_connected(nodes, edges):
            continue
        if count_v_structures(nodes, edges) < 3:
            continue
        if not is_acyclic(nodes, edges):
            continue

        # Invariant check: at least 1 node has out-degree >= 4
        out_degs = {n: 0 for n in nodes}
        for u, v in edges:
            out_degs[u] += 1
        if max(out_degs.values()) < 4:
            continue

        return edges


def generate_d07_bank(
    seed: int = SEED,
    bank_dir: Path = BANK_DIR,
    manifest_name: str = MANIFEST_NAME,
    decision_id: str = "D-07",
):
    """Write a 40-DAG bank. The defaults regenerate D-07 byte for byte.

    Any other seed must go to another directory, and an existing bank there is
    never overwritten, so the frozen D-07 bank cannot be replaced by accident.
    """
    bank_dir = Path(bank_dir)
    if bank_dir.resolve() == BANK_DIR.resolve():
        if seed != SEED or manifest_name != MANIFEST_NAME:
            raise ValueError("the D-07 bank directory only takes the D-07 seed and manifest name")
    elif (bank_dir / manifest_name).exists():
        raise FileExistsError(f"{bank_dir / manifest_name} exists; a bank is generated once")
    dags_dir = bank_dir / "topologies"
    manifest_path = bank_dir / manifest_name
    dags_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    topologies_manifest = []
    seen_edge_sets = set()

    # Plan: 40 DAGs
    # Dev: syn_dag_00..09 (ER, 10), syn_dag_10..19 (Hub, 10) -> 20 dev
    # Conf: syn_dag_20..29 (ER, 10), syn_dag_30..39 (Hub, 10) -> 20 conf
    specs = []
    for idx in range(40):
        if idx < 10:
            profile = "erdos_renyi"
            split = "development"
        elif idx < 20:
            profile = "scale_free_hub"
            split = "development"
        elif idx < 30:
            profile = "erdos_renyi"
            split = "confirmatory"
        else:
            profile = "scale_free_hub"
            split = "confirmatory"
        specs.append((idx, profile, split))

    for idx, profile, split in specs:
        while True:
            if profile == "erdos_renyi":
                edges = generate_er_dag(rng, CORE14_NODES, n_edges=21)
            else:
                edges = generate_hub_dag(rng, CORE14_NODES, n_edges=21)

            edge_key = tuple((u, v) for u, v in edges)
            if edge_key in seen_edge_sets:
                continue
            seen_edge_sets.add(edge_key)
            break

        dag_id = f"syn_dag_{idx:02d}"
        dag_filename = f"synthetic_dag_{idx:02d}.json"
        dag_file_path = dags_dir / dag_filename

        out_degs = {n: 0 for n in CORE14_NODES}
        for u, v in edges:
            out_degs[u] += 1

        dag_content = {
            "schema": "synthetic_dag/v1",
            "id": dag_id,
            "seed": seed + idx,
            "profile": profile,
            "nodes": CORE14_NODES,
            "edges": edges,
            "metrics": {
                "n_nodes": len(CORE14_NODES),
                "n_edges": len(edges),
                "n_v_structures": count_v_structures(CORE14_NODES, edges),
                "max_out_degree": max(out_degs.values()),
                "is_connected": True,
            },
        }

        dag_text = json.dumps(dag_content, indent=2, ensure_ascii=False) + "\n"
        with open(dag_file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(dag_text)

        dag_sha256 = sha256_text(dag_text)

        topologies_manifest.append({
            "id": dag_id,
            "file": f"topologies/{dag_filename}",
            "sha256": dag_sha256,
            "split": split,
            "profile": profile,
            "n_v_structures": dag_content["metrics"]["n_v_structures"],
            "max_out_degree": dag_content["metrics"]["max_out_degree"],
        })

    manifest = {
        "schema": "topology_bank_manifest/v1",
        "protocol": "docs/enhanced_v2_protocol_claim_map.md",
        "decision_id": decision_id,
        "generator_seed": seed,
        "n_topologies": len(topologies_manifest),
        "split_summary": {
            "development": 20,
            "confirmatory": 20,
        },
        "profile_summary": {
            "erdos_renyi": 20,
            "scale_free_hub": 20,
        },
        "topologies": topologies_manifest,
    }

    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(manifest_text)

    manifest_sha = sha256_text(manifest_text)
    print(f"Generated {decision_id} topology bank at {bank_dir} (seed {seed})")
    print(f"Manifest SHA-256: {manifest_sha}")
    print(f"Topologies: {len(topologies_manifest)} total (20 dev, 20 conf; 20 ER, 20 Hub)")
    return manifest_sha


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Generate a 40-DAG D-07-style topology bank")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--bank-dir", type=Path, default=BANK_DIR)
    parser.add_argument("--manifest-name", default=MANIFEST_NAME)
    parser.add_argument("--decision-id", default="D-07")
    args = parser.parse_args(argv)
    generate_d07_bank(args.seed, args.bank_dir, args.manifest_name, args.decision_id)


if __name__ == "__main__":
    main()
