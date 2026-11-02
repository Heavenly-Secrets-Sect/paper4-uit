"""R3-4 analysis (ID revlag3): feasible reversal comparators vs the frozen module on reversal-affected
pairs, exactly as pre-registered in docs/ext/revlag3.md (section "Đăng ký trước", R3-4).

Affected pair (red-team definition): non-null pair with dC = |C_true - C_true with the reversed true
edges zeroed| >= theta (primary 0.05; 0.02 / 0.10 sensitivity). oracle_cal = oracle interval widened
about its midpoint by plugin's c_T on cell none (1.4 / 1.3 / 1.2), as in round 2.

Cluster bootstrap by topology (all clusters of the run), 2000 resamples, percentile CI, seed 20261103
(analyze_lag.Boot, unchanged). One-sided p = share of resamples on the H0 side (floor 1/2000).

Run:  python experiments/ext/revlag3/analyze_rev.py --run ext_revlag3_rev
Writes results/<run>/rev_analysis.{md,json}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "revlag"))
from analyze_lag import OCAL, Boot, ci, covered, holm, interval_score, load, p_le  # noqa: E402

KEY = ["topo", "rep", "scen", "T", "cell", "j", "i"]
NEW = ("tolerant_v4R", "tolerant_v4R_mix", "tolerant_v4Rmap")
CELLS = ("reversed|0.2", "reversed|0.5")


def wide(df, methods):
    base = df[df.mname == methods[0]][KEY + ["cname", "C_t", "dC", "role"]].copy()
    for m in methods:
        s = df[df.mname == m][KEY + ["C_e", "lo", "hi"]].rename(columns={"C_e": f"C_{m}", "lo": f"lo_{m}", "hi": f"hi_{m}"})
        base = base.merge(s, on=KEY)
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--new", nargs="*", default=list(NEW), help="comparators (default: the two registered methods)")
    ap.add_argument("--tag", default="rev_analysis")
    a = ap.parse_args()
    df, methods, cells = load(a.run)
    out = ROOT / "results" / a.run
    boot = Boot(df.topo.unique())
    new = [m for m in a.new if m in methods]
    W = wide(df, ["tolerant_v4", "oracle"] + new)
    n_rows = {m: int((df.mname == m).sum()) for m in methods}
    mid, half = (W.lo_oracle + W.hi_oracle) / 2, (W.hi_oracle - W.lo_oracle) / 2
    c = W["T"].map(OCAL)
    W["cov_ocal"] = covered(mid - c * half, mid + c * half, W.C_t)
    W["cov_oraw"] = covered(W.lo_oracle, W.hi_oracle, W.C_t)
    for m in ["tolerant_v4"] + new:
        W[f"cov_{m}"] = covered(W[f"lo_{m}"], W[f"hi_{m}"], W.C_t)
        W[f"is_{m}"] = interval_score(W[f"lo_{m}"], W[f"hi_{m}"], W.C_t)
        W[f"err_{m}"] = np.abs(W[f"C_{m}"] - W.C_t)
        W[f"w_{m}"] = W[f"hi_{m}"] - W[f"lo_{m}"]
    W["err_oracle"] = np.abs(W.C_oracle - W.C_t)
    res = {"n_rows": n_rows, "n_wide": int(len(W)), "R1": [], "R2a": [], "R2b": [], "desc": [], "sens": []}
    L = [f"# R3-4: feasible reversal comparators vs tolerant_v4 on reversal-affected pairs ({a.run})", "",
         f"Rows per method: {n_rows}; paired rows (all methods ok): {len(W)}.", ""]

    # R1 (primary): delta coverage new - v4 on affected pairs, theta 0.05, T 80/150
    L += ["## R1: coverage trên cặp affected (dC >= 0.05), method mới − v4 (ghép cặp)", "",
          "| method | cell | T | n aff | cov v4 | cov new | cov oracle_cal | delta [CI] | p một phía | p Holm (4) | p Holm (toàn họ) | closed share [CI] | gap new − oracle_cal [CI] | đạt |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in new:
        for cname in CELLS:
            for T in (80, 150, 40):
                s = W[(W.cname == cname) & (W["T"] == T) & (W.dC >= 0.05)]
                d, rd = boot.ratio(s.topo.values, (s[f"cov_{m}"] - s["cov_tolerant_v4"]).values)
                g0, rg0 = boot.ratio(s.topo.values, (s["cov_ocal"] - s["cov_tolerant_v4"]).values)
                g1, rg1 = boot.ratio(s.topo.values, (s[f"cov_{m}"] - s["cov_ocal"]).values)
                with np.errstate(invalid="ignore", divide="ignore"):
                    sh, rsh = d / g0, rd / rg0
                res["R1"].append(dict(method=m, cell=cname, T=T, n=len(s), cov_v4=s.cov_tolerant_v4.mean(),
                                      cov_new=s[f"cov_{m}"].mean(), cov_ocal=s.cov_ocal.mean(), d=d, ci=ci(rd),
                                      p=p_le(rd, 0.0), share=sh, share_ci=ci(rsh), gap=g1, gap_ci=ci(rg1),
                                      primary=T in (80, 150)))
    for m in new:
        prim = [r for r in res["R1"] if r["primary"] and r["method"] == m]
        for r, ph in zip(prim, holm([r["p"] for r in prim])):
            r["p_holm4"] = float(ph)
            r["pass"] = bool(r["ci"][0] > 0 and ph < 0.05)
    allp = [r for r in res["R1"] if r["primary"]]
    for r, ph in zip(allp, holm([r["p"] for r in allp])):
        r["p_holm8"] = float(ph)
        r["pass8"] = bool(r["ci"][0] > 0 and ph < 0.05)
    for r in res["R1"]:
        pr = r["primary"]
        L.append(f"| {r['method']} | {r['cell']} | {r['T']} | {r['n']} | {r['cov_v4']:.3f} | {r['cov_new']:.3f} | "
                 f"{r['cov_ocal']:.3f} | {r['d']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p']:.4f} | "
                 f"{r['p_holm4']:.4f} | {r['p_holm8']:.4f} | " if pr else
                 f"| {r['method']} | {r['cell']} | {r['T']} | {r['n']} | {r['cov_v4']:.3f} | {r['cov_new']:.3f} | "
                 f"{r['cov_ocal']:.3f} | {r['d']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p']:.4f} | - | - | ")
        L[-1] += (f"{r['share']:.2f} [{r['share_ci'][0]:.2f}, {r['share_ci'][1]:.2f}] | {r['gap']:+.3f} "
                  f"[{r['gap_ci'][0]:+.3f}, {r['gap_ci'][1]:+.3f}] | "
                  f"{('yes' if r['pass'] else 'no') if pr else '(T40, báo)'} |")

    # R2a: IS ratio, all non-null pairs, 6 reversed cells; R2b coverage >= 0.90, 4 primary cells
    L += ["", "## R2: không làm tệ (mọi cặp non-null của cell reversed)", "",
          "| method | cell | T | n | cov v4 | cov new | IS v4 | IS new | ratio | R2a (≤1.05) | R2b (cov ≥ 0.90, T≥80) | IS delta [CI] |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in new:
        for cname in CELLS:
            for T in (40, 80, 150):
                s = W[(W.cname == cname) & (W["T"] == T)]
                i4, iN = s.is_tolerant_v4.mean(), s[f"is_{m}"].mean()
                d, rd = boot.ratio(s.topo.values, (s[f"is_{m}"] - s.is_tolerant_v4).values)
                r2a = dict(method=m, cell=cname, T=T, n=len(s), is_v4=i4, is_new=iN, ratio=iN / i4,
                           ok=bool(iN <= 1.05 * i4), d=d, ci=ci(rd), p_worse=p_le(-rd, 0.0))
                res["R2a"].append(r2a)
                cv = s[f"cov_{m}"].mean()
                if T >= 80:
                    res["R2b"].append(dict(method=m, cell=cname, T=T, cov=cv, ok=bool(cv >= 0.90)))
                L.append(f"| {m} | {cname} | {T} | {len(s)} | {s.cov_tolerant_v4.mean():.3f} | {cv:.3f} | {i4:.3f} | {iN:.3f} | "
                         f"{iN / i4:.3f} | {'yes' if r2a['ok'] else 'NO'} | "
                         f"{('yes' if cv >= 0.90 else 'NO') if T >= 80 else '-'} | {d:+.3f} [{r2a['ci'][0]:+.3f}, {r2a['ci'][1]:+.3f}] |")
    for m in new:
        rows = [r for r in res["R2a"] if r["method"] == m]
        for r, ph in zip(rows, holm([r["p_worse"] for r in rows])):
            r["worse_holm"] = bool(ph < 0.05 and r["d"] > 0)

    # verdicts
    L += ["", "## Verdict theo rule ghi trước", ""]
    res["verdict"] = {}
    for m in new:
        n1 = sum(r["pass"] for r in res["R1"] if r["primary"] and r["method"] == m)
        n8 = sum(r["pass8"] for r in res["R1"] if r["primary"] and r["method"] == m)
        r2a = all(r["ok"] for r in res["R2a"] if r["method"] == m)
        r2b = all(r["ok"] for r in res["R2b"] if r["method"] == m)
        nwh = sum(r["worse_holm"] for r in res["R2a"] if r["method"] == m)
        if n1 >= 3 and r2a and r2b:
            v = "GIẢM ĐƯỢC (gap giảm bằng method khả thi)"
        elif n1 >= 1 and r2a and r2b:
            v = "GIẢM MỘT PHẦN"
        elif n1 == 0:
            v = "KHÔNG GIẢM"
        else:
            v = "KHÔNG KẾT LUẬN (R1 có cell đạt nhưng R2 hỏng)"
        keep = n1 == 4 and r2a and r2b
        res["verdict"][m] = dict(R1=n1, R1_holm8=n8, R2a=r2a, R2b=r2b, R2a_worse_holm=nwh, verdict=v,
                                 module="GIỮ" if keep else "LOẠI")
        L.append(f"- **{m}**: R1 {n1}/4 cell (Holm 4: {n1}/4; Holm toàn họ ({4 * len(new)} test): {n8}/4); R2a {'đạt' if r2a else 'KHÔNG đạt'}; "
                 f"R2b {'đạt' if r2b else 'KHÔNG đạt'}; IS tệ hơn có ý nghĩa sau Holm (6 cell): {nwh}/6. "
                 f"Câu trả lời: **{v}**. Version: **{'GIỮ' if keep else 'LOẠI'}**.")

    # descriptive: point error, width, sensitivity theta, oracle raw
    L += ["", "## Mô tả (không quyết định verdict)", "",
          "Cặp affected (theta 0.05): median |C − C_true| và median width.", "",
          "| cell | T | n | err v4 | " + " | ".join(f"err {m}" for m in new) + " | err oracle | width v4 | " +
          " | ".join(f"width {m}" for m in new) + " | cov oracle raw |",
          "|---|---|---|---|" + "---|" * len(new) + "---|---|" + "---|" * len(new) + "---|"]
    for cname in CELLS:
        for T in (40, 80, 150):
            s = W[(W.cname == cname) & (W["T"] == T) & (W.dC >= 0.05)]
            row = dict(cell=cname, T=T, n=len(s), err_v4=float(s.err_tolerant_v4.median()),
                       err_oracle=float(s.err_oracle.median()), w_v4=float(s.w_tolerant_v4.median()),
                       cov_oraw=float(s.cov_oraw.mean()))
            for m in new:
                row[f"err_{m}"] = float(s[f"err_{m}"].median())
                row[f"w_{m}"] = float(s[f"w_{m}"].median())
            res["desc"].append(row)
            L.append(f"| {cname} | {T} | {len(s)} | {row['err_v4']:.3f} | " +
                     " | ".join(f"{row[f'err_{m}']:.3f}" for m in new) + f" | {row['err_oracle']:.3f} | {row['w_v4']:.3f} | " +
                     " | ".join(f"{row[f'w_{m}']:.3f}" for m in new) + f" | {row['cov_oraw']:.3f} |")
    L += ["", "Sensitivity theta (delta coverage new − v4 trên cặp affected, T 80/150):", "",
          "| method | theta | cell | T | n | delta [CI] |", "|---|---|---|---|---|---|"]
    for m in new:
        for th in (0.02, 0.10):
            for cname in CELLS:
                for T in (80, 150):
                    s = W[(W.cname == cname) & (W["T"] == T) & (W.dC >= th)]
                    d, rd = boot.ratio(s.topo.values, (s[f"cov_{m}"] - s["cov_tolerant_v4"]).values)
                    res["sens"].append(dict(method=m, theta=th, cell=cname, T=T, n=len(s), d=d, ci=ci(rd)))
                    L.append(f"| {m} | {th} | {cname} | {T} | {len(s)} | {d:+.3f} [{ci(rd)[0]:+.3f}, {ci(rd)[1]:+.3f}] |")
    L += ["", "Cặp unaffected (non-null, dC < 0.05): coverage.", "", "| cell | T | n | cov v4 | " +
          " | ".join(f"cov {m}" for m in new) + " | cov oracle_cal |", "|---|---|---|---|" + "---|" * len(new) + "---|"]
    res["unaff"] = []
    for cname in CELLS:
        for T in (40, 80, 150):
            s = W[(W.cname == cname) & (W["T"] == T) & (W.dC < 0.05)]
            row = dict(cell=cname, T=T, n=len(s), cov_v4=float(s.cov_tolerant_v4.mean()), cov_ocal=float(s.cov_ocal.mean()),
                       **{f"cov_{m}": float(s[f"cov_{m}"].mean()) for m in new})
            res["unaff"].append(row)
            L.append(f"| {cname} | {T} | {len(s)} | {row['cov_v4']:.3f} | " + " | ".join(f"{row[f'cov_{m}']:.3f}" for m in new)
                     + f" | {row['cov_ocal']:.3f} |")
    (out / f"{a.tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / f"{a.tag}.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic)
                                                      else (list(o) if isinstance(o, tuple) else str(o))), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
