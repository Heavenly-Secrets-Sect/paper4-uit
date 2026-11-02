"""Descriptive part of R3-1 (docs/ext/baselines3.md 3.4), plus two disclosures found after the rule check:
(1) Bootstrap p resolution: with B = 4000 the smallest two-sided p is 2/4001 = 5.0e-4 > 0.025/56 = 4.5e-4, so the
    Bonferroni overlay (Holm at 0.025 over 56) can reject nothing. Re-scored here with B = 20000 (min p 1.0e-4) as a
    DESCRIPTIVE sensitivity; the rule verdict stays the B = 4000 one.
(2) Stored-row regression: pselect_cal / fullvar_cal / targeted_lp(_cal) differ from round-1 rows (B1 stream tag).
Writes results/ext_baselines3_eval/{describe.md, describe.json}."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import analyze as A
ROOT = HERE.parents[2]; OUT = ROOT / "results/ext_baselines3_eval"
rows = A.load(OUT / "runs.jsonl")
tl = A.load(ROOT / "results/ext_tlp2_t80b/runs.jsonl") + A.load(ROOT / "results/ext_tlp2_t150c/runs.jsonl")
allrows = rows + [r for r in tl if r["method"] == "tlp2_db_p3"]
D = {}
L = ["# R3-1 descriptive (not ruled; D-07 development)", ""]
# (1) sensitivity B = 20000
idx = A.index(allrows, set(A.MODS + A.ENVELOPE))
topos = sorted({k[0] for k in idx})
A.B = 20000
res20 = A.score(idx, topos)
v05, v025 = A.verdicts(res20), A.verdicts(res20, col="holm0.025")
A.B = 4000
D["B20000"] = {"holm0.05": v05, "holm0.025": v025}
L += ["## 1. Sensitivity: cluster bootstrap B = 20000 (same seed), descriptive", ""]
for m in A.MODS:
    L.append(f"- {m}: Holm 0.05 W {v05[m]['W']} / T {v05[m]['T']} / L {v05[m]['L']}, E-cell {v05[m]['E_cell']}, statement {v05[m]['statement']}, losses {v05[m]['losses']}; "
             f"Holm 0.025 W {v025[m]['W']} / T {v025[m]['T']} / L {v025[m]['L']}, E-cell {v025[m]['E_cell']}, statement {v025[m]['statement']}, losses {v025[m]['losses']}")
changed = [(k, res20['comps'][k]['p2']) for k in res20["comps"]]
L += ["", "Comparisons whose Holm-0.05 class differs between B = 4000 and B = 20000: (see describe.json)", ""]
res4 = A.score(idx, topos)
diff = [f"{'|'.join(map(str, k))}: {res4['comps'][k]['holm0.05']} -> {res20['comps'][k]['holm0.05']}" for k in res4["comps"]
        if res4["comps"][k]["holm0.05"] != res20["comps"][k]["holm0.05"]]
L += [f"- {d}" for d in diff] or ["- none"]
D["B_class_changes"] = diff
# (2) budget
tim = json.loads((ROOT / "results/ext_baselines3_budget/timing.json").read_text())
L += ["", "## 2. Compute budget per call", "",
      "Seconds: median of 6 calls per T in ONE process on D-07H development (timing.json; load 5-11). `info_seconds` = median wall time inside the D-07 run (3 workers in parallel with other agents), where the method records it.", "",
      "| method | draws per call | s/call T80 | s/call T150 | info_seconds D-07 T80 | T150 |", "|---|---|---|---|---|---|"]
info = defaultdict(list)
for r in rows:
    if r["status"] == "ok" and r.get("info_seconds") is not None:
        info[(r["method"], r["T"])].append(r["info_seconds"])
for name in ["tolerant_v4", "tolerant_v5_1", "pselect_union_v3", "pselect_cal", "fullvar_cal", "targeted_lp", "tlp2_db_p3", "bvar_minnesota_v2"]:
    s80, s150 = tim["summary"][f"{name}|80"], tim["summary"][f"{name}|150"]
    shown = {"targeted_lp": "targeted_lp(_cal)", "bvar_minnesota_v2": "bvar_minnesota_v2(_cal)", "pselect_union_v3": "pselect_union_v3(_cal)"}.get(name, name)
    i80 = np.median(info[(name, 80)]) if info[(name, 80)] else float("nan")
    i150 = np.median(info[(name, 150)]) if info[(name, 150)] else float("nan")
    L.append(f"| {shown} | {s80['draws']} | {s80['median_seconds']:.2f} | {s150['median_seconds']:.2f} | {i80:.2f} | {i150:.2f} |")
    D.setdefault("budget", {})[shown] = {"draws": s80["draws"], "s80": s80["median_seconds"], "s150": s150["median_seconds"],
                                          "info_s80": None if np.isnan(i80) else float(i80), "info_s150": None if np.isnan(i150) else float(i150)}
g = [r for r in rows if r["method"] == "pselect_union_v3" and r["status"] == "ok"]
for T in (80, 150):
    gg = [r for r in g if r["T"] == T]
    D[f"v3_struct_{T}"] = {k: float(np.mean([r[f"info_{k}"] for r in gg])) for k in ("n_graphs", "n_members", "n_members_ok", "n_draws", "n_selected", "n_unoriented")}
    L.append(f"\npselect_union_v3 at T{T} (D-07, 120 runs): mean " + ", ".join(f"{k} {v:.2f}" for k, v in D[f'v3_struct_{T}'].items()))
L.append(f"\nWhole D-07 run (9 methods, 2160 rows, 3 workers): 954.4 s.")
# (3) strongest baseline per cell + v5_1 - v4 + extra comparisons
extra = {"pselect_union_v2": "ext_baselines2_eval", "pselect_union_v2_cal": "ext_baselines2_eval"}
ex_idx = {}
for m, src in extra.items():
    ex_idx.update(A.index(A.load(ROOT / "results" / src / "runs.jsonl"), {m}))
idx2 = dict(idx); idx2.update(ex_idx)
idx2.update(A.index(rows, {"targeted_lp"}))
res_x = A.score(idx2, topos, mods=["tolerant_v4", "tolerant_v5_1", "pselect_union_v3", "pselect_union_v3_cal"],
                envelope=["tolerant_v4", "pselect_union_v2", "pselect_union_v2_cal", "targeted_lp"])
L += ["", "## 3. Strongest baseline per cell (by IS; among the 7 envelope members)", "", "| cell | strongest | IS | cov | strongest with cov >= 0.90 | v4 IS | v5_1 IS |", "|---|---|---|---|---|---|---|"]
for T, r in A.CELLS:
    c = {X: res4["cells"][(X, T, r)] for X in A.ENVELOPE}
    best = min(c, key=lambda X: c[X]["IS"]); best90 = min([X for X in c if c[X]["cov"] >= 0.9], key=lambda X: c[X]["IS"])
    L.append(f"| T{T} missing-{r} | {best} | {c[best]['IS']:.2f} | {c[best]['cov']:.3f} | {best90} | {res4['cells'][('tolerant_v4', T, r)]['IS']:.2f} | {res4['cells'][('tolerant_v5_1', T, r)]['IS']:.2f} |")
    D.setdefault("strongest", {})[f"{T}|{r}"] = [best, best90]
L += ["", "## 4. Extra paired comparisons (row minus column, mean IS difference [95% CI], B = 4000; no Holm family, descriptive)", "",
      "| T | cell | a | b | a - b [95% CI] |", "|---|---|---|---|---|"]
for (a, b, T, r), v in res_x["comps"].items():
    if a == b or (a.startswith("pselect_union_v3") and b == "tolerant_v4"):
        continue
    if a.startswith("pselect_union_v3") and b == "targeted_lp":
        continue
    L.append(f"| {T} | missing-{r} | {a} | {b} | {v['est']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}] |")
D["extra_comparisons"] = {"|".join(map(str, k)): v for k, v in res_x["comps"].items()}
L += ["", "Cell stats of the extra methods:", ""]
for X in ["pselect_union_v2", "pselect_union_v2_cal", "targeted_lp"]:
    L.append(f"- {X}: " + ", ".join(f"T{T} m{r} IS {res_x['cells'][(X, T, r)]['IS']:.2f} cov {res_x['cells'][(X, T, r)]['cov']:.3f}" for T, r in A.CELLS))
(OUT / "describe.md").write_text("\n".join(L) + "\n"); (OUT / "describe.json").write_text(json.dumps(D, indent=1, default=str))
print("\n".join(L))
