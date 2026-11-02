"""Toy check of roles() in experiments/ext/metrics/run_pairs.py (skeptic check)."""
import sys, types
import numpy as np
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/metrics")
from run_pairs import roles
sem = types.SimpleNamespace(edge_lag={(0, 1): 0, (1, 2): 1, (2, 3): 0, (4, 3): 2})
for kind, log in (("missing", [{"pair": [1, 2]}]), ("reversed", [{"pair": [2, 3]}]), ("extra", [{"pair": [0, 4]}])):
    skel = types.SimpleNamespace(damage={"kind": kind}, log=log)
    r = roles(sem, skel, 5)
    print(kind)
    for j in range(5):
        for i in range(5):
            if i != j and r[j, i]:
                print(f"  effect {i}->{j}: role {r[j, i]}")
