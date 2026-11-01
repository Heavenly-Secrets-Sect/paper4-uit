"""Static DAG topologies from the shared generator bank.

The banks are copied verbatim from the ACIIDS workspace into ``data/topology_bank/`` (provenance
in ``data/topology_bank/PROVENANCE.md``). Every file is checked against the SHA-256 recorded in its
bank manifest, so a changed topology cannot slip in silently.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BANK_ROOT = Path(__file__).resolve().parents[2] / "data" / "topology_bank"
BANKS = {
    "D-07": "D-07/d07_manifest.json",
    "D-07H": "D-07H/heldout_manifest.json",
    "P4-H1": "P4-H1/p4h1_manifest.json",   # generated for Paper 4 held-out checks; see PROVENANCE.md
}
SPLITS = ("development", "confirmatory")


class TopologyError(ValueError):
    pass


@dataclass(frozen=True)
class Topology:
    bank: str
    id: str
    split: str
    profile: str
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    sha256: str

    @property
    def n_nodes(self) -> int:
        return len(self.nodes)

    def index(self, name: str) -> int:
        return self.nodes.index(name)

    def topological_order(self) -> list[int]:
        """Kahn's algorithm; raises if the topology is cyclic."""
        n = self.n_nodes
        indeg = [0] * n
        children: list[list[int]] = [[] for _ in range(n)]
        for u, v in self.edges:
            children[self.index(u)].append(self.index(v))
            indeg[self.index(v)] += 1
        queue = [i for i in range(n) if indeg[i] == 0]
        order = []
        while queue:
            i = queue.pop(0)
            order.append(i)
            for c in children[i]:
                indeg[c] -= 1
                if indeg[c] == 0:
                    queue.append(c)
        if len(order) != n:
            raise TopologyError(f"{self.id} is not acyclic")
        return order


def bank_root() -> Path:
    return Path(os.environ.get("PAPER4_TOPOLOGY_ROOT", DEFAULT_BANK_ROOT))


def _sha256_lf(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def load_bank(bank: str = "D-07", split: str | None = "development", root: Path | None = None) -> list[Topology]:
    """Load and verify every topology of ``bank`` in ``split`` (None = both splits)."""
    if bank not in BANKS:
        raise TopologyError(f"unknown bank {bank!r}; expected one of {sorted(BANKS)}")
    if split is not None and split not in SPLITS:
        raise TopologyError(f"unknown split {split!r}; expected one of {SPLITS}")
    manifest_path = (root or bank_root()) / BANKS[bank]
    if not manifest_path.exists():
        raise TopologyError(f"bank manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out = []
    for entry in manifest["topologies"]:
        if split is not None and entry["split"] != split:
            continue
        raw = (manifest_path.parent / entry["file"]).read_bytes()
        digest = _sha256_lf(raw)
        if digest != entry["sha256"]:
            raise TopologyError(f"{entry['id']}: sha256 {digest} does not match manifest {entry['sha256']}")
        dag = json.loads(raw)
        out.append(Topology(
            bank=bank,
            id=entry["id"],
            split=entry["split"],
            profile=entry["profile"],
            nodes=tuple(dag["nodes"]),
            edges=tuple((u, v) for u, v in dag["edges"]),
            sha256=digest,
        ))
    return out
