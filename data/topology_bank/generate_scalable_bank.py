"""Scalable topology bank generator (14 nodes, 21 edges, ER and scale-free hub profiles).

Reuses the DAG samplers of ``D-07/generate_d07_bank.py`` unchanged, but takes the number of
topologies and the split sizes as parameters. Every topology is drawn i.i.d. from the same
generator law (half Erdos-Renyi, half hub), then the topologies are assigned to splits by a seeded
random permutation within each profile. Split membership is therefore random by construction, which
is what an exchangeability argument for the calibration needs. The ids carry no split information.

Example (P4-H7):
    python data/topology_bank/generate_scalable_bank.py --seed 20261115 --bank-dir data/topology_bank/P4-H7 \
        --manifest-name p4h7_manifest.json --decision-id P4-H7 --splits design=60,calibration=150,test=150

An existing bank is never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("gen_d07", HERE / "D-07" / "generate_d07_bank.py")
_d07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_d07)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8").replace(b"\r\n", b"\n")).hexdigest()


def generate(seed: int, bank_dir: Path, manifest_name: str, decision_id: str, splits: dict[str, int]) -> str:
    total = sum(splits.values())
    if any(v % 2 for v in splits.values()):
        raise ValueError("each split size must be even (half ER, half hub)")
    bank_dir = Path(bank_dir)
    if (bank_dir / manifest_name).exists():
        raise FileExistsError(f"{bank_dir / manifest_name} exists; a bank is generated once")
    dags_dir = bank_dir / "topologies"
    dags_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    nodes = _d07.CORE14_NODES
    n_er = n_hub = total // 2
    dags, seen = [], set()
    for profile, count in (("erdos_renyi", n_er), ("scale_free_hub", n_hub)):
        sampler = _d07.generate_er_dag if profile == "erdos_renyi" else _d07.generate_hub_dag
        made = 0
        while made < count:
            edges = sampler(rng, nodes, n_edges=21)
            key = tuple((u, v) for u, v in edges)
            if key in seen:
                continue
            seen.add(key)
            dags.append((profile, edges))
            made += 1
    # random assignment to splits, stratified by profile
    assign = {}
    for profile in ("erdos_renyi", "scale_free_hub"):
        idx = [i for i, (p, _) in enumerate(dags) if p == profile]
        rng.shuffle(idx)
        pos = 0
        for name, size in splits.items():
            for i in idx[pos:pos + size // 2]:
                assign[i] = name
            pos += size // 2
    # random ids so that the id does not reveal profile or split
    order = list(range(len(dags)))
    rng.shuffle(order)
    entries = []
    for rank, i in enumerate(order):
        profile, edges = dags[i]
        out_degs = {n: 0 for n in nodes}
        for u, v in edges:
            out_degs[u] += 1
        dag_id = f"syn_dag_{rank:03d}"
        content = {
            "schema": "synthetic_dag/v1", "id": dag_id, "seed": seed + rank, "profile": profile,
            "nodes": nodes, "edges": edges,
            "metrics": {"n_nodes": len(nodes), "n_edges": len(edges),
                        "n_v_structures": _d07.count_v_structures(nodes, edges),
                        "max_out_degree": max(out_degs.values()), "is_connected": True},
        }
        text = json.dumps(content, indent=2, ensure_ascii=False) + "\n"
        (dags_dir / f"synthetic_dag_{rank:03d}.json").write_text(text, encoding="utf-8", newline="\n")
        entries.append({"id": dag_id, "file": f"topologies/synthetic_dag_{rank:03d}.json", "sha256": _sha(text),
                        "split": assign[i], "profile": profile,
                        "n_v_structures": content["metrics"]["n_v_structures"],
                        "max_out_degree": content["metrics"]["max_out_degree"]})
    manifest = {
        "schema": "topology_bank_manifest/v1", "protocol": "docs/ext/p4h7_spec.md",
        "decision_id": decision_id, "generator_seed": seed, "n_topologies": len(entries),
        "split_summary": dict(splits), "profile_summary": {"erdos_renyi": n_er, "scale_free_hub": n_hub},
        "topologies": entries,
    }
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    (bank_dir / manifest_name).write_text(text, encoding="utf-8", newline="\n")
    print(f"Generated {decision_id}: {len(entries)} topologies, splits {splits}, manifest SHA-256 {_sha(text)}")
    return _sha(text)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--bank-dir", type=Path, required=True)
    p.add_argument("--manifest-name", required=True)
    p.add_argument("--decision-id", required=True)
    p.add_argument("--splits", required=True, help="name=size,name=size,... (sizes even)")
    a = p.parse_args(argv)
    splits = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in a.splits.split(",")}
    generate(a.seed, a.bank_dir, a.manifest_name, a.decision_id, splits)


if __name__ == "__main__":
    main()
