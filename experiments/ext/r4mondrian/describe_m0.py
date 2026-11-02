"""Descriptive (post hoc, not part of the rule): is M0's D-07 coverage consistent with the nominal 0.95
once pairs are clustered by topology? Per cell: pooled coverage of M0 (q_table.json and q_table_rep3.json),
cluster-bootstrap 95% CI (topology, B = 20000, seed 20261104), and max |IS ratio - 1| / |dcov| of M0 vs v5_1.
Run: python experiments/ext/r4mondrian/describe_m0.py -> results/ext_r4mondrian_eval/m0_guarantee.{md,json}"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import CELLS, ROOT, arms, cluster_boot  # noqa: E402

P = dict(np.load(ROOT / "results/ext_r4mondrian_eval/pairs.npz"))
out, L = {}, ["# M0 coverage vs nominal 0.95 on D-07 (descriptive, post hoc)", "",
              "| T | cell | cov M0 (rep1 table) [cluster CI] | 0.95 in CI | cov M0 (rep3 table) [cluster CI] | 0.95 in CI |",
              "|---|---|---|---|---|---|"]
for tag in ("q_table.json", "q_table_rep3.json"):
    t = {k: v for k, v in json.loads((HERE / tag).read_text()).items() if not k.startswith("_")}
    h0, _ = arms(P, t)
    cov = (np.abs(P["C_t"] - P["mid"]) <= h0).astype(float)
    for T in (40, 80, 150):
        for c, (k, r) in enumerate(CELLS):
            m = (P["T"] == T) & (P["cell"] == c)
            out.setdefault(f"{T}|{k}|{r}", {})[tag] = cluster_boot(P["topo"][m], cov[m] - 0.95)
for key, v in out.items():
    T, k, r = key.split("|")
    a, b = v["q_table.json"], v["q_table_rep3.json"]
    f = lambda d: f"{d['est'] + 0.95:.3f} [{d['lo'] + 0.95:.3f}, {d['hi'] + 0.95:.3f}]"  # noqa: E731
    L.append(f"| {T} | {k}-{r} | {f(a)} | {'yes' if a['lo'] <= 0 <= a['hi'] else 'NO'} | {f(b)} | {'yes' if b['lo'] <= 0 <= b['hi'] else 'NO'} |")
n1 = sum(not (v['q_table.json']['lo'] <= 0 <= v['q_table.json']['hi']) for v in out.values())
n3 = sum(not (v['q_table_rep3.json']['lo'] <= 0 <= v['q_table_rep3.json']['hi']) for v in out.values())
L += ["", f"Cells whose cluster CI excludes 0.95: rep1 table {n1}/21, rep3 table {n3}/21."]
R = json.loads((ROOT / "results/ext_r4mondrian_eval/ruling.json").read_text())["cells"]
mi = max(abs(r["IS_M0"] / r["IS_v51"] - 1) for r in R); mc = max(abs(r["cov_M0"] - r["cov_v51"]) for r in R)
L.append(f"M0 vs v5_1 over 21 cells: max |IS ratio - 1| = {mi:.4f}, max |cov M0 - cov v5_1| = {mc:.4f}.")
(ROOT / "results/ext_r4mondrian_eval/m0_guarantee.md").write_text("\n".join(L) + "\n")
(ROOT / "results/ext_r4mondrian_eval/m0_guarantee.json").write_text(json.dumps({"cells": out, "excl_rep1": n1, "excl_rep3": n3, "max_is_ratio_dev": mi, "max_cov_dev": mc}, indent=1))
print("\n".join(L))
