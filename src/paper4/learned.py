"""A3: skeletons learned from data, as a source of realistic damage.

The damage in skeleton.py is drawn at random. Here the skeleton is the output of a structure
learner instead: the GES of Paper 2 (ACIIDS, ``03_causal_discovery/baselines/no_prior``), run
exactly as Paper 2 runs it, i.e. on the rows of the panel treated as independent draws. Its
errors are therefore the ones a real pipeline would pass on: missed weak or lagged edges, spurious
edges induced by autocorrelation, and orientations GES cannot or does not resolve.

Following plan section 5.2 (no double dipping), the learner sees a series independent of the one
used to estimate effects.

The ACIIDS code is imported read-only from ``PAPER4_ACIIDS_ROOT`` (default: a sibling directory
``ACIIDS`` next to this repository). Nothing is copied or modified there.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

from .skeleton import Skeleton

_GES = None


def _ges_class():
    global _GES
    if _GES is None:
        root = Path(os.environ.get("PAPER4_ACIIDS_ROOT", Path(__file__).resolve().parents[3] / "ACIIDS"))
        scripts = root / "03_causal_discovery" / "baselines" / "no_prior" / "scripts"
        if not scripts.is_dir():
            raise FileNotFoundError(f"ACIIDS GES not found under {root}; set PAPER4_ACIIDS_ROOT")
        sys.path.insert(0, str(scripts))
        import paths  # noqa: E402  (ACIIDS import-path bootstrap)
        paths.ensure()
        from algorithms.ges_wrapper import GES  # noqa: E402
        _GES = GES
    return _GES


def ges_skeleton(data: np.ndarray, *, penalty_discount: float = 1.0) -> Skeleton:
    """GES CPDAG of ``data`` (T x n) as a Skeleton: arrows are oriented pairs, lines undetermined."""
    n = data.shape[1]
    names = [f"x{i}" for i in range(n)]
    graph = _ges_class()(penalty_discount=penalty_discount).fit(data.tolist(), names).graph
    idx = {name: i for i, name in enumerate(names)}
    return Skeleton(n,
                    oriented={(idx[u], idx[v]) for u, v in graph.arrows},
                    undetermined={frozenset((idx[u], idx[v])) for u, v in graph.lines})


def damage_counts(learned: Skeleton, truth: Skeleton) -> dict[str, int]:
    """Errors of a learned skeleton against the true one, in the counts of the plan's interface
    (section 7): missing and extra pairs, and pairs present in both but oriented against the truth.
    An undetermined pair is not counted as reversed."""
    true_pairs, got = truth.pairs(), learned.pairs()
    reversed_ = sum(1 for u, v in learned.oriented if (v, u) in truth.oriented)
    return {"missing": len(true_pairs - got), "extra": len(got - true_pairs), "reversed": reversed_}
