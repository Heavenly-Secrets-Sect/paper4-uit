"""B3: skeletons in the shared interface format, and controlled damage.

A skeleton records which node pairs are adjacent, with a direction for the pairs whose
orientation is known (plan section 7: ``adjacency`` and ``undetermined_orient``). It carries no
lag: how adjacency maps onto lagged terms is decided by the estimator (see estimator.py).

Damage types follow the plan (section 5.2): extra edges, deleted edges, reversed edges, each at a
preset rate. The number of damaged pairs is floor(rate * base + 0.5), the damage accounting of
Paper 2 (protocol D-03), where ``base`` is the number of true adjacent pairs, or for reversals the
number of pairs that can be reversed.

Two records are kept apart:
- ``damage``: what the interface passes on (kind, rate, k). A module may read it.
- ``log``: which pairs were damaged and their true lags. Only the evaluation may read it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .generator import DynamicSEM

# "reversed" flips contemporaneous edges only: a lagged edge cannot point backwards in time, and
# with lags admitted in both directions (estimator.py) its orientation changes nothing.
# "reversed_any" flips any oriented pair and is kept as an ablation.
DAMAGE_KINDS = ("none", "extra", "missing", "reversed", "reversed_any",
                "shortcut", "weak_missing", "mixed")
# Structured kinds, shaped like errors of text extraction:
# - "shortcut":     a chain a -> b -> c with a, c non-adjacent becomes a -> c; one chain edge is dropped
# - "weak_missing": the weakest true edges (smallest |coefficient|) are dropped
# - "mixed":        missing, extra and reversed damage at the same rate, applied in that order
# Their public record lists counts as {"missing", "extra", "reversed"} (plan section 7).


@dataclass
class Skeleton:
    n: int
    oriented: set[tuple[int, int]] = field(default_factory=set)       # (u, v): u -> v
    undetermined: set[frozenset[int]] = field(default_factory=set)    # u -- v
    damage: dict = field(default_factory=dict)
    log: list[dict] = field(default_factory=list)
    lag_hint: dict[tuple[int, int], int] | None = None                # (u, v) -> lag; oracle reference only

    def pairs(self) -> set[frozenset[int]]:
        return {frozenset(e) for e in self.oriented} | set(self.undetermined)

    def is_adjacent(self, u: int, v: int) -> bool:
        return frozenset((u, v)) in self.pairs()

    def copy(self) -> "Skeleton":
        return Skeleton(self.n, set(self.oriented), set(self.undetermined), dict(self.damage),
                        list(self.log), None if self.lag_hint is None else dict(self.lag_hint))

    def adjacency(self) -> np.ndarray:
        a = np.zeros((self.n, self.n), dtype=int)
        for p in self.pairs():
            u, v = tuple(p)
            a[u, v] = a[v, u] = 1
        return a

    def to_interface(self, nodes, *, T: int, lag_max: int, generator_id: str, seed) -> dict:
        """The skeleton record of plan section 7. ``edge_score`` belongs to Paper 3 and stays empty;
        ``oriented`` is the complement of ``undetermined_orient`` and is listed for convenience."""
        return {
            "nodes": list(nodes),
            "adjacency": self.adjacency().tolist(),
            "oriented": sorted([nodes[u], nodes[v]] for u, v in self.oriented),
            "edge_score": None,
            "undetermined_orient": sorted(sorted(nodes[i] for i in p) for p in self.undetermined),
            "damage_estimate": self.damage,
            "T": T,
            "lag_max": lag_max,
            "generator_id": generator_id,
            "seed": seed if isinstance(seed, int) else list(seed),
        }


def true_skeleton(sem: DynamicSEM, *, with_lags: bool = False) -> Skeleton:
    """Every cross edge of the generator, oriented as in the generator. ``with_lags`` attaches the
    true lags, which only the oracle reference may use."""
    return Skeleton(sem.n, oriented=set(sem.edge_lag), damage={"kind": "none", "rate": 0.0, "k": 0},
                    lag_hint=dict(sem.edge_lag) if with_lags else None)


def _creates_cycle(oriented: set[tuple[int, int]], n: int) -> bool:
    children: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in oriented:
        children[u].append(v)
        indeg[v] += 1
    queue = [i for i in range(n) if indeg[i] == 0]
    seen = 0
    while queue:
        i = queue.pop()
        seen += 1
        for c in children[i]:
            indeg[c] -= 1
            if indeg[c] == 0:
                queue.append(c)
    return seen != n


def _k(rate: float, base: int) -> int:
    return int(np.floor(rate * base + 0.5))


def damage(skel: Skeleton, kind: str, rate: float, rng: np.random.Generator,
           true_lag: dict[tuple[int, int], int] | None = None,
           true_coef: dict[tuple[int, int], float] | None = None) -> Skeleton:
    if kind in ("shortcut", "weak_missing", "mixed"):
        return _structured_damage(skel, kind, rate, rng, true_lag, true_coef)
    return _simple_damage(skel, kind, rate, rng, true_lag)


def _structured_damage(skel, kind, rate, rng, true_lag, true_coef) -> Skeleton:
    n_pairs = len(skel.pairs())
    k = _k(rate, n_pairs)
    if kind == "mixed":
        out = _simple_damage(skel, "missing", rate, rng, true_lag)
        log = list(out.log)
        out = _simple_damage(out, "extra", rate * n_pairs / max(len(out.pairs()), 1), rng, true_lag)
        log += out.log
        n_contemp = sum(1 for e in skel.oriented if (true_lag or {}).get(e) == 0)
        k_rev = _k(rate, n_contemp)
        rev = out.copy()
        pool = sorted(e for e in out.oriented if (true_lag or {}).get(e) == 0)
        flipped = []
        for idx in rng.permutation(len(pool)):
            if len(flipped) == k_rev:
                break
            u, v = pool[idx]
            trial = (rev.oriented - {(u, v)}) | {(v, u)}
            if not _creates_cycle(trial, skel.n):
                rev.oriented = trial
                flipped.append({"pair": [u, v], "true_lag": 0})
        out = rev
        out.log = log + flipped
        n_miss = sum(1 for e in log if e["true_lag"] is not None)
        out.damage = {"kind": "mixed", "rate": rate, "missing": n_miss,
                      "extra": len(log) - n_miss, "reversed": len(flipped)}
        return out

    out = skel.copy()
    out.lag_hint = None
    changed = []
    if kind == "weak_missing":
        if true_coef is None:
            raise ValueError("weak_missing needs true_coef")
        strength = {frozenset(e): abs(c) for e, c in true_coef.items()}
        order = sorted(skel.pairs(), key=lambda p: (strength.get(p, 0.0), sorted(p)))
        for p in order[:k]:
            u, v = sorted(p)
            out.oriented.discard((u, v)); out.oriented.discard((v, u))
            out.undetermined.discard(p)
            changed.append({"pair": [u, v], "true_lag": (true_lag or {}).get((u, v), (true_lag or {}).get((v, u)))})
        out.damage = {"kind": kind, "rate": rate, "missing": len(changed), "extra": 0, "reversed": 0}
    else:  # shortcut
        chains = []
        for a, b in sorted(skel.oriented):
            for b2, c in sorted(skel.oriented):
                if b2 == b and a != c and not skel.is_adjacent(a, c):
                    chains.append((a, b, c))
        dropped, added = 0, 0
        for idx in rng.permutation(len(chains)):
            if added == k:
                break
            a, b, c = chains[idx]
            if out.is_adjacent(a, c) or (a, b) not in out.oriented or (b, c) not in out.oriented:
                continue
            drop = (a, b) if rng.random() < 0.5 else (b, c)
            trial = (out.oriented - {drop}) | {(a, c)}
            if _creates_cycle(trial, skel.n):
                continue
            out.oriented = trial
            changed.append({"pair": list(drop), "true_lag": (true_lag or {}).get(drop)})
            changed.append({"pair": [a, c], "true_lag": None})
            added += 1
        out.damage = {"kind": kind, "rate": rate, "missing": added, "extra": added, "reversed": 0}
    out.log = changed
    return out


def _simple_damage(skel: Skeleton, kind: str, rate: float, rng: np.random.Generator,
                   true_lag: dict[tuple[int, int], int] | None = None) -> Skeleton:
    """Return a damaged copy.

    - ``missing``:  delete k of the adjacent pairs.
    - ``extra``:    add k non-adjacent pairs; each gets a random direction, flipped if needed so
                    the oriented part stays acyclic (one of the two directions always is).
    - ``reversed``: flip k contemporaneous edges (k from the number of contemporaneous edges),
                    skipping flips that would create a directed cycle. Needs ``true_lag``.
    - ``reversed_any``: the same over all oriented pairs.

    All random choices are drawn up front from ``rng``, so for a fixed rng seed a higher rate
    damages a superset of the pairs a lower rate damages (nested rates).
    """
    if kind not in DAMAGE_KINDS:
        raise ValueError(f"unknown damage kind {kind!r}")
    out = skel.copy()
    out.lag_hint = None
    changed: list[dict] = []
    lag_of = (lambda u, v: (true_lag or {}).get((u, v), (true_lag or {}).get((v, u))))
    k = 0

    if kind == "missing":
        pool = sorted(tuple(sorted(p)) for p in skel.pairs())
        order = rng.permutation(len(pool))
        k = _k(rate, len(pool))
        for idx in order[:k]:
            u, v = pool[idx]
            out.oriented.discard((u, v))
            out.oriented.discard((v, u))
            out.undetermined.discard(frozenset((u, v)))
            changed.append({"pair": [u, v], "true_lag": lag_of(u, v)})
    elif kind == "extra":
        present = skel.pairs()
        pool = [(u, v) for u in range(skel.n) for v in range(u + 1, skel.n) if frozenset((u, v)) not in present]
        order = rng.permutation(len(pool))
        forward = rng.random(len(pool)) < 0.5
        k = _k(rate, len(present))
        for idx in order[:k]:
            u, v = pool[idx]
            edge = (u, v) if forward[idx] else (v, u)
            if _creates_cycle(out.oriented | {edge}, skel.n):
                edge = (edge[1], edge[0])
            out.oriented.add(edge)
            changed.append({"pair": list(edge), "true_lag": None})
    elif kind in ("reversed", "reversed_any"):
        if kind == "reversed":
            if true_lag is None:
                raise ValueError("reversed damage needs true_lag to find contemporaneous edges")
            pool = sorted(e for e in skel.oriented if lag_of(*e) == 0)
        else:
            pool = sorted(skel.oriented)
        order = rng.permutation(len(pool))
        k = _k(rate, len(pool))
        for idx in order:
            if len(changed) == k:
                break
            u, v = pool[idx]
            trial = (out.oriented - {(u, v)}) | {(v, u)}
            if _creates_cycle(trial, skel.n):
                continue
            out.oriented = trial
            changed.append({"pair": [u, v], "true_lag": lag_of(u, v)})

    out.damage = {"kind": kind, "rate": rate, "k": len(changed)}
    out.log = changed
    if len(changed) < k:
        out.damage["k_requested"] = k
    return out
