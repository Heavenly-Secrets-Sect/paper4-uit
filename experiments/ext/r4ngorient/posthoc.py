"""POST-HOC (written after the registered results; descriptive only, changes no verdict).

Question: how much of the arms' differences from v5_1 comes from the orientation evidence, and how
much from their re-tuned width factor? Calibration is a pure rescaling about the midpoint, so every
arm's interval can be put exactly on v5_1's own frozen factor for the same (T, width_key):
half_equal = half / fac_arm * fac_v5_1. With equal factors, a difference between arm and v5_1 is
due to the orientation draws only (centre and raw spread of the bootstrap distribution).

Reports per shock x T x cell: IS and coverage with equal factors, dIS [cluster-bootstrap CI,
B 20000, seed 20261104], and coverage on affected pairs (dC >= 0.05) with equal factors. Also what
the registered rule would say on these equal-factor numbers ("would-be", NOT a verdict).
Writes results/ext_r4ngorient_analysis/posthoc_equal_factor.{md,json}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import ARMS, CELLS, PRIMARY, REF, SHORT, Boot, ci, holm, p_side  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.metrics import interval_score  # noqa: E402

OUT = ROOT / "results" / "ext_r4ngorient_analysis"
FROZEN = json.loads((ROOT / "experiments/ext/r4ngorient/frozen_ngorient.json").read_text(encoding="utf-8"))


def load(s):
    z = np.load(ROOT / f"results/ext_r4ngorient_{s}/pairs.npz")
    meth = [str(m) for m in z["methods"]]
    cells = [str(c) for c in z["cells"]]
    df = pd.DataFrame({k: z[k] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "lo", "hi", "dC", "fac")})
    df["mname"] = [meth[int(m)] for m in df.method]
    df["cname"] = [cells[int(c)] for c in df.cell]
    runs = {}
    for line in open(ROOT / f"results/ext_r4ngorient_{s}/runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["method"] == REF:
            runs[(r["topology"], r["replicate"], r["T"], f"{r['kind']}|{r['rate']}")] = r.get("k", 0)
    topos = [t["id"] for t in json.loads((ROOT / f"results/ext_r4ngorient_{s}/manifest.json").read_text())["topologies"]]
    df["k"] = [runs.get((topos[int(t)], int(rp), int(T_), c), 0) for t, rp, T_, c in zip(df.topo, df.rep, df["T"], df.cname)]
    df["wk"] = np.where(df.k == 0, "none", [c.split("|")[0] for c in df.cname])
    df["topo_id"] = [topos[int(t)] for t in df.topo]
    mid = (df.lo + df.hi) / 2
    half = (df.hi - df.lo) / 2 / df.fac
    fref = np.array([FROZEN.get(f"{REF}|{int(T_)}|{wk}", np.nan) if m != "oracle" else 1.0
                     for m, T_, wk in zip(df.mname, df["T"], df.wk)])
    df["lo_e"], df["hi_e"] = mid - half * fref, mid + half * fref
    df["is_e"] = interval_score(df.lo_e.values, df.hi_e.values, df.C_t.values)
    df["cov_e"] = ((df.lo_e <= df.C_t) & (df.C_t <= df.hi_e)).astype(float)
    df["w_e"] = df.hi_e - df.lo_e
    return df


def main():
    res = {"note": "post hoc, descriptive", "cells": [], "affected": [], "would_be": {}}
    L = ["# POST-HOC: arm với chính factor của v5_1 (mô tả, viết SAU khi có kết quả; không đổi verdict)", "",
         "Sinh bởi experiments/ext/r4ngorient/posthoc.py. Interval của NG-A/NG-B được đưa về factor frozen của v5_1 cùng "
         "(T, width_key): half_eq = half / fac_arm × fac_v5_1 (calibration là phép nhân quanh trung điểm nên phép đổi là chính xác). "
         "Khác biệt còn lại chỉ đến từ orientation draws. Cluster bootstrap B = 20000, seed 20261104.", ""]
    for s in ("ngmix", "gauss", "t10"):
        df = load(s)
        boot = Boot(sorted(df.topo_id.unique()))
        run = df.groupby(["mname", "topo_id", "rep", "T", "cname"]).agg(is_e=("is_e", "mean"), cov=("cov_e", "sum"),
                                                                         n=("cov_e", "size")).reset_index()
        L += [f"## {s}: IS và coverage với factor bằng nhau", "",
              "| arm | T | cell | cov v5_1 | cov arm | IS v5_1 | IS arm | ratio | dIS [CI] | p tốt hơn | p tệ hơn |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm in ARMS:
            for T in sorted(df["T"].unique()):
                for k, r in CELLS:
                    cname = f"{k}|{r}"
                    a = run[(run.mname == arm) & (run["T"] == T) & (run.cname == cname)]
                    b = run[(run.mname == REF) & (run["T"] == T) & (run.cname == cname)]
                    if not len(a):
                        continue
                    mm = a.merge(b, on=["topo_id", "rep"], suffixes=("_a", "_b"))
                    d, rd = boot.ratio(mm.topo_id.values, (mm.is_e_a - mm.is_e_b).values)
                    row = {"shock": s, "arm": arm, "T": int(T), "cell": cname, "cov_ref": float(mm.cov_b.sum() / mm.n_b.sum()),
                           "cov_arm": float(mm.cov_a.sum() / mm.n_a.sum()), "is_ref": float(mm.is_e_b.mean()),
                           "is_arm": float(mm.is_e_a.mean()), "d": float(d), "ci": ci(rd), "p_better": p_side(rd, True),
                           "p_worse": p_side(rd, False)}
                    row["ratio"] = row["is_arm"] / row["is_ref"]
                    res["cells"].append(row)
                    L.append(f"| {SHORT[arm]} | {int(T)} | {cname} | {row['cov_ref']:.3f} | {row['cov_arm']:.3f} | {row['is_ref']:.3f} | "
                             f"{row['is_arm']:.3f} | {row['ratio']:.3f} | {row['d']:+.3f} [{row['ci'][0]:+.3f}, {row['ci'][1]:+.3f}] | "
                             f"{row['p_better']:.4f} | {row['p_worse']:.4f} |")
        L += ["", f"### {s}: cặp affected (dC ≥ 0.05) với factor bằng nhau", "",
              "| arm | cell | T | n | cov v5_1 | cov arm | Δ [CI] | median width v5_1 / arm |", "|---|---|---|---|---|---|---|---|"]
        aff = df[df.dC >= 0.05]
        key = ["topo_id", "rep", "T", "cname", "j", "i"]
        for arm in ARMS:
            for cname in ("reversed|0.2", "reversed|0.5", "missing|0.2", "missing|0.5"):
                for T in sorted(df["T"].unique()):
                    a = aff[(aff.mname == arm) & (aff.cname == cname) & (aff["T"] == T)][key + ["cov_e", "w_e"]]
                    b = aff[(aff.mname == REF) & (aff.cname == cname) & (aff["T"] == T)][key + ["cov_e", "w_e"]]
                    mm = a.merge(b, on=key, suffixes=("_a", "_b"))
                    if not len(mm):
                        continue
                    d, rd = boot.ratio(mm.topo_id.values, (mm.cov_e_a - mm.cov_e_b).values)
                    row = {"shock": s, "arm": arm, "cell": cname, "T": int(T), "n": int(len(mm)), "cov_ref": float(mm.cov_e_b.mean()),
                           "cov_arm": float(mm.cov_e_a.mean()), "d": float(d), "ci": ci(rd),
                           "w": [float(mm.w_e_b.median()), float(mm.w_e_a.median())]}
                    res["affected"].append(row)
                    L.append(f"| {SHORT[arm]} | {cname} | {int(T)} | {row['n']} | {row['cov_ref']:.3f} | {row['cov_arm']:.3f} | "
                             f"{row['d']:+.3f} [{row['ci'][0]:+.3f}, {row['ci'][1]:+.3f}] | {row['w'][0]:.3f} / {row['w'][1]:.3f} |")
        L.append("")
    # would-be rule on equal factors
    L += ["## \"Would-be\" của rule đã đăng ký trên số factor bằng nhau (KHÔNG phải verdict)", ""]
    for arm in ARMS:
        c = {(r["shock"], r["T"], r["cell"]): r for r in res["cells"] if r["arm"] == arm}
        prim = [c[("ngmix", T, f"{k}|{r}")] for T, k, r in PRIMARY]
        wins = sum(1 for r, p in zip(prim, holm([r["p_better"] for r in prim])) if p < 0.05 and r["cov_arm"] >= 0.90)
        g = [c[("gauss", T, f"{k}|{r}")] for T in (40, 80, 150) for k, r in CELLS]
        gh = holm([r["p_worse"] for r in g])
        nh_a = all(r["ratio"] <= 1.03 and p >= 0.05 for r, p in zip(g, gh))
        bad_a = [f"{r['T']} {r['cell']} (ratio {r['ratio']:.3f}, p Holm {p:.4f})" for r, p in zip(g, gh) if not (r["ratio"] <= 1.03 and p >= 0.05)]
        other = [c[("ngmix", T, f"{k}|{r}")] for T in (40, 80, 150) for k, r in CELLS if (T, k, r) not in PRIMARY]
        nh_b = all(r["ratio"] <= 1.05 and (r["cov_ref"] < 0.90 or r["cov_arm"] >= 0.90) for r in other)
        bad_b = [f"{r['T']} {r['cell']} (ratio {r['ratio']:.3f}, cov {r['cov_arm']:.3f} vs {r['cov_ref']:.3f})" for r in other
                 if not (r["ratio"] <= 1.05 and (r["cov_ref"] < 0.90 or r["cov_arm"] >= 0.90))]
        res["would_be"][arm] = {"wins": wins, "no_harm_a": nh_a, "no_harm_b": nh_b, "fail_a": bad_a, "fail_b": bad_b}
        L.append(f"- {SHORT[arm]}: WIN {wins}/8; no-harm (a) {'đạt' if nh_a else 'không'} {bad_a}; no-harm (b) "
                 f"{'đạt' if nh_b else 'không'} {bad_b}.")
    (OUT / "posthoc_equal_factor.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "posthoc_equal_factor.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
