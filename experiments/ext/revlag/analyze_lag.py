"""Analysis of the revlag pair rows for R2-6a (oracle on reversal-affected pairs) and R2-6b
(tolerant_v4L lag output), exactly as pre-registered in docs/ext/revlag.md.

Cluster bootstrap by topology (all clusters of the run), 2000 resamples, percentile 95% CI,
seed 20261103. One-sided bootstrap p = share of resamples on the H0 side (floor 1/2000).
Holm within each family of a rule.

Run:  python experiments/ext/revlag/analyze_lag.py --run ext_revlag_lag      (primary: rules a, b)
      python experiments/ext/revlag/analyze_lag.py --run ext_revlag_fresh    (descriptive L1/L2 replication)
Writes results/<run>/analysis_{a,b}.md and analysis.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
B, SEED = 2000, 20261103
OCAL = {40: 1.4, 80: 1.3, 150: 1.2}       # plugin c_T on cell none, results/a2_baselines/calibration.json
KEY = ["topo", "rep", "scen", "T", "cell", "j", "i"]


def load(run):
    z = np.load(ROOT / "results" / run / "pairs.npz")
    d = {k: z[k] for k in z.files}
    methods = [str(m) for m in d["methods"]]
    cells = [str(c) for c in d["cells"]]
    df = pd.DataFrame({k: d[k] for k in d if d[k].ndim == 1 and len(d[k]) == len(d["topo"])})
    for k in ("topo", "rep", "scen", "T", "cell", "method", "j", "i", "role", "pk_t", "pk_e"):
        df[k] = df[k].astype(int)
    df["mname"] = [methods[m] for m in df["method"]]
    df["cname"] = [cells[c] for c in df["cell"]]
    return df, methods, cells


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    m = len(p)
    for r, idx in enumerate(order):
        run = max(run, (m - r) * p[idx])
        adj[idx] = min(1.0, run)
    return adj


class Boot:
    """Topology-cluster bootstrap of ratio statistics sum(num)/sum(den) over a fixed resample set."""

    def __init__(self, topos):
        self.topos = np.array(sorted(set(topos)))
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(self.topos), size=(B, len(self.topos)))
        self.W = np.stack([np.bincount(r, minlength=len(self.topos)) for r in idx]).astype(float)  # (B, K)

    def sums(self, topo, x):
        pos = np.searchsorted(self.topos, topo)
        return np.bincount(pos, weights=x, minlength=len(self.topos))

    def ratio(self, topo, num, den=None):
        den = np.ones(len(num)) if den is None else den
        sn, sd = self.sums(topo, num), self.sums(topo, den)
        point = sn.sum() / sd.sum() if sd.sum() > 0 else np.nan
        with np.errstate(invalid="ignore", divide="ignore"):
            reps = (self.W @ sn) / (self.W @ sd)
        return point, reps


def ci(reps):
    r = reps[np.isfinite(reps)]
    return (np.quantile(r, 0.025), np.quantile(r, 0.975)) if len(r) else (np.nan, np.nan)


def p_le(reps, thr):     # one-sided p for H0: stat <= thr  (reject when stat > thr)
    r = reps[np.isfinite(reps)]
    return max(np.mean(r <= thr), 1 / B)


def p_ge(reps, thr):     # one-sided p for H0: stat >= thr  (reject when stat < thr)
    r = reps[np.isfinite(reps)]
    return max(np.mean(r >= thr), 1 / B)


def paired(df, a, b):
    """Rows of method a and b merged on the pair key (inner join)."""
    cols = KEY + ["cname", "C_t", "ml_t", "pk_t", "role", "dC", "direct_lag"]
    A = df[df.mname == a]
    Bm = df[df.mname == b]
    m = A[cols + ["C_e", "lo", "hi", "ml_e", "pk_e", "ml_lo", "ml_hi"]].merge(
        Bm[KEY + ["C_e", "lo", "hi", "ml_e", "pk_e", "ml_lo", "ml_hi"]], on=KEY, suffixes=("_a", "_b"))
    return m


def covered(lo, hi, c):
    return ((lo <= c) & (c <= hi)).astype(float)


# ----------------------------------------------------------------------------------------- (a)
def part_a(df, boot, out):
    m = paired(df, "tolerant_v4", "oracle")
    mid, half = (m.lo_b + m.hi_b) / 2, (m.hi_b - m.lo_b) / 2
    c = m["T"].map(OCAL)
    m["cov_v4"] = covered(m.lo_a, m.hi_a, m.C_t)
    m["cov_oraw"] = covered(m.lo_b, m.hi_b, m.C_t)
    m["cov_ocal"] = covered(mid - c * half, mid + c * half, m.C_t)
    res = {}
    lines = ["# R2-6a: tolerant_v4 vs oracle on reversal-affected pairs (red-team definition, dC >= theta)", "",
             "Pairs: non-null; affected = dC >= theta (dC = |C_true - C_true with the damaged true edges zeroed|).",
             "oracle_cal = oracle interval widened about its midpoint by plugin c_T on cell none (1.4/1.3/1.2).",
             "g = cov(v4) - cov(ref), paired on the same pairs; CI = topology-cluster bootstrap (20 clusters, 2000).",
             ""]
    for ref in ("ocal", "oraw"):
        for theta in (0.05, 0.02, 0.10):
            rows = []
            for rate in ("0.2", "0.5"):
                for T in (40, 80, 150):
                    cname = f"reversed|{rate}"
                    s = m[(m.cname == cname) & (m["T"] == T)]
                    aff = s[s.dC >= theta]
                    una = s[s.dC < theta]
                    if len(aff) == 0:
                        continue
                    cv4, _ = boot.ratio(aff.topo.values, aff.cov_v4.values)
                    cref, rref = boot.ratio(aff.topo.values, aff[f"cov_{ref}"].values)
                    g, rg = boot.ratio(aff.topo.values, (aff.cov_v4 - aff[f"cov_{ref}"]).values)
                    lo, hi = ci(rg)
                    # difference in differences of miss rates (affected - unaffected), v4 minus ref
                    _, r_a4 = boot.ratio(aff.topo.values, 1 - aff.cov_v4.values)
                    _, r_u4 = boot.ratio(una.topo.values, 1 - una.cov_v4.values)
                    _, r_ar = boot.ratio(aff.topo.values, 1 - aff[f"cov_{ref}"].values)
                    _, r_ur = boot.ratio(una.topo.values, 1 - una[f"cov_{ref}"].values)
                    did_point = ((1 - aff.cov_v4.mean()) - (1 - una.cov_v4.mean())) - \
                                ((1 - aff[f"cov_{ref}"].mean()) - (1 - una[f"cov_{ref}"].mean()))
                    did_lo, did_hi = ci((r_a4 - r_u4) - (r_ar - r_ur))
                    cls = None
                    if T in (80, 150):
                        if hi < -0.03:
                            cls = "M"
                        elif cref < 0.90 and lo > -0.03:
                            cls = "I"
                        elif cref >= 0.90 and lo > -0.03:
                            cls = "N"
                        else:
                            cls = "U"
                    rows.append(dict(cell=cname, T=T, n_aff=len(aff), n_unaff=len(una), cov_v4=cv4, cov_ref=cref,
                                     g=g, g_lo=lo, g_hi=hi, p_M=p_ge(rg, -0.03), p_NI=p_le(rg, -0.03),
                                     did=did_point, did_lo=did_lo, did_hi=did_hi, cls=cls))
            prim = [r for r in rows if r["cls"] is not None]
            hM = holm([r["p_M"] for r in prim])
            hN = holm([r["p_NI"] for r in prim])
            for r, a1, a2 in zip(prim, hM, hN):
                r["p_M_holm"], r["p_NI_holm"] = float(a1), float(a2)
            nM = sum(r["cls"] == "M" for r in prim)
            nI = sum(r["cls"] == "I" for r in prim)
            nN = sum(r["cls"] == "N" for r in prim)
            if nM >= 3:
                verdict = "lỗi module"
            elif nI >= 3:
                verdict = "chủ yếu khó nội tại"
            elif nM == 0 and nI + nN >= 3:
                verdict = "không có lỗi module vượt 0.03"
            else:
                verdict = "hỗn hợp / không kết luận"
            nM_h = sum((r["p_M_holm"] < 0.05) for r in prim)
            nNI_h = sum((r["p_NI_holm"] < 0.05) for r in prim)
            key = f"{ref}|{theta}"
            res[key] = dict(rows=rows, nM=nM, nI=nI, nN=nN, verdict=verdict, nM_holm=nM_h, nNI_holm=nNI_h)
            lines += [f"## ref = {'oracle_cal' if ref == 'ocal' else 'oracle raw'}, theta = {theta}", "",
                      "| cell | T | n aff | n unaff | cov v4 | cov ref | g [95% CI] | p_M (Holm) | p_NI (Holm) | DiD miss [CI] | class |",
                      "|---|---|---|---|---|---|---|---|---|---|---|"]
            for r in rows:
                pm = f"{r['p_M']:.4f} ({r['p_M_holm']:.4f})" if r["cls"] else f"{r['p_M']:.4f}"
                pn = f"{r['p_NI']:.4f} ({r['p_NI_holm']:.4f})" if r["cls"] else f"{r['p_NI']:.4f}"
                lines.append(f"| {r['cell']} | {r['T']} | {r['n_aff']} | {r['n_unaff']} | {r['cov_v4']:.3f} | "
                             f"{r['cov_ref']:.3f} | {r['g']:+.3f} [{r['g_lo']:+.3f}, {r['g_hi']:+.3f}] | {pm} | {pn} | "
                             f"{r['did']:+.3f} [{r['did_lo']:+.3f}, {r['did_hi']:+.3f}] | {r['cls'] or '(T40, báo)'} |")
            lines += ["", f"#M = {nM}, #I = {nI}, #N = {nN}, #U = {len(prim) - nM - nI - nN}; "
                          f"verdict: **{verdict}**. Holm (4 cell): #M (H0 g >= -0.03 bác) = {nM_h}, "
                          f"#non-inferior (H0 g <= -0.03 bác) = {nNI_h}.", ""]
    v02, v05, v10 = (res[f"ocal|{t}"]["verdict"] for t in (0.02, 0.05, 0.10))
    robust = v02 == v05 == v10
    res["robust"] = robust
    lines += [f"**Verdict tổng (ref oracle_cal, theta 0.05): {v05}.** Sensitivity: theta 0.02 -> {v02}; theta 0.10 -> "
              f"{v10}; raw oracle theta 0.05 -> {res['oraw|0.05']['verdict']}. Bền: **{robust}**.", ""]
    # missing cells, same definition (description)
    lines += ["## Đối chiếu: cell missing, cùng định nghĩa (theta 0.05, ref oracle_cal)", "",
              "| cell | T | n aff | cov v4 | cov oracle_cal | cov oracle raw | g vs oracle_cal [CI] |", "|---|---|---|---|---|---|---|"]
    res["missing"] = []
    for rate in ("0.2", "0.5"):
        for T in (40, 80, 150):
            s = m[(m.cname == f"missing|{rate}") & (m["T"] == T) & (m.dC >= 0.05)]
            if not len(s):
                continue
            g, rg = boot.ratio(s.topo.values, (s.cov_v4 - s.cov_ocal).values)
            lo, hi = ci(rg)
            r = dict(cell=f"missing|{rate}", T=T, n=len(s), cov_v4=s.cov_v4.mean(), cov_ocal=s.cov_ocal.mean(),
                     cov_oraw=s.cov_oraw.mean(), g=g, g_lo=lo, g_hi=hi)
            res["missing"].append(r)
            lines.append(f"| {r['cell']} | {T} | {r['n']} | {r['cov_v4']:.3f} | {r['cov_ocal']:.3f} | {r['cov_oraw']:.3f} | "
                         f"{g:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
    (out / "analysis_a.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return res


# ----------------------------------------------------------------------------------------- (b)
def part_b(df, boot, out, cells_order):
    m = paired(df, "tolerant_v4L", "tolerant_v4")          # a = v4L, b = v4
    kept = (m.C_e_a != 0) & (m.C_e_b != 0)
    m["hit_L"] = (m.pk_e_a == m.pk_t).astype(float)
    m["hit_4"] = (m.pk_e_b == m.pk_t).astype(float)
    res = {"L1": [], "L2": []}
    lines = ["# R2-6b: tolerant_v4L - tolerant_v4 (paired pairs, topology-cluster bootstrap)", ""]
    # L1
    lines += ["## L1: peak-lag hit on damaged pairs (role 2) of reversed cells, kept in both", "",
              "| cell | T | n | hit v4 | hit v4L | delta [95% CI] | p (one-sided) | p Holm | pass |", "|---|---|---|---|---|---|---|---|---|"]
    for cname in ("reversed|0.2", "reversed|0.5"):
        for T in (80, 150, 40):
            s = m[(m.cname == cname) & (m["T"] == T) & (m.role == 2) & kept]
            d, rd = boot.ratio(s.topo.values, (s.hit_L - s.hit_4).values)
            lo, hi = ci(rd)
            res["L1"].append(dict(cell=cname, T=T, n=len(s), hit_v4=s.hit_4.mean(), hit_v4L=s.hit_L.mean(), d=d,
                                  lo=lo, hi=hi, p=p_le(rd, 0.0), primary=T in (80, 150)))
    prim = [r for r in res["L1"] if r["primary"]]
    for r, a in zip(prim, holm([r["p"] for r in prim])):
        r["p_holm"] = float(a)
        r["pass"] = bool(r["lo"] > 0 and a < 0.05)
    n_pass = sum(r["pass"] for r in prim)
    L1 = n_pass == len(prim) == 4
    for r in res["L1"]:
        ph = f"{r['p_holm']:.4f}" if r["primary"] else "-"
        lines.append(f"| {r['cell']} | {r['T']} | {r['n']} | {r['hit_v4']:.3f} | {r['hit_v4L']:.3f} | {r['d']:+.3f} "
                     f"[{r['lo']:+.3f}, {r['hi']:+.3f}] | {r['p']:.4f} | {ph} | "
                     f"{('yes' if r['pass'] else 'no') if r['primary'] else '(T40, báo)'} |")
    lines += ["", f"L1: {n_pass}/4 cell đạt -> **{'ĐẠT' if L1 else 'KHÔNG ĐẠT'}**", ""]
    # L2
    lines += ["## L2: không làm tệ (21 cell, mọi cặp non-null)", "",
              "(i) mean-lag abs error (mean over pairs with mean lag defined in truth, v4 and v4L); (ii) peak hit (kept in both); "
              "(iii) share of pairs with defined estimated mean lag. 'worse' = point beyond 0.05 margin AND CI excludes 0 "
              "on the bad side; Holm column = same with Holm p < 0.05 (one-sided, 21 cells per metric).", "",
              "| T | cell | n | (i) mlerr v4 | (i) mlerr v4L | (i) delta [CI] | (ii) hit v4 | (ii) delta [CI] | (iii) def v4 | (iii) delta [CI] | worse |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for T in (40, 80, 150):
        for cname in cells_order:
            s = m[(m.cname == cname) & (m["T"] == T)]
            if not len(s):
                continue
            tdef = np.isfinite(s.ml_t)
            both = tdef & np.isfinite(s.ml_e_a) & np.isfinite(s.ml_e_b)
            sb = s[both]
            e4 = np.abs(sb.ml_e_b - sb.ml_t)
            eL = np.abs(sb.ml_e_a - sb.ml_t)
            d1, r1 = boot.ratio(sb.topo.values, (eL - e4).values)
            sk = s[(s.C_e_a != 0) & (s.C_e_b != 0)]
            d2, r2 = boot.ratio(sk.topo.values, (sk.hit_L - sk.hit_4).values)
            st = s[tdef]
            d3, r3 = boot.ratio(st.topo.values, (np.isfinite(st.ml_e_a).astype(float) - np.isfinite(st.ml_e_b).astype(float)).values)
            c1, c2, c3 = ci(r1), ci(r2), ci(r3)
            w1 = bool(d1 > 0.05 and c1[0] > 0)
            w2 = bool(d2 < -0.05 and c2[1] < 0)
            w3 = bool(d3 < -0.05 and c3[1] < 0)
            res["L2"].append(dict(T=T, cell=cname, n=len(s), n_i=int(both.sum()), mlerr_v4=float(e4.mean()),
                                  mlerr_v4L=float(eL.mean()), d1=d1, c1=c1, p1=p_le(r1, 0.0), hit_v4=float(sk.hit_4.mean()),
                                  d2=d2, c2=c2, p2=p_ge(r2, 0.0), def_v4=float(np.isfinite(st.ml_e_b).mean()), d3=d3,
                                  c3=c3, p3=p_ge(r3, 0.0), w1=w1, w2=w2, w3=w3))
    for k, pk, dk, sign in (("w1h", "p1", "d1", 1), ("w2h", "p2", "d2", -1), ("w3h", "p3", "d3", -1)):
        adj = holm([r[pk] for r in res["L2"]])
        for r, a in zip(res["L2"], adj):
            r[pk + "_holm"] = float(a)
            r[k] = bool(sign * r[dk] > 0.05 and a < 0.05)
    for r in res["L2"]:
        flags = [n for n, w in (("i", r["w1"]), ("ii", r["w2"]), ("iii", r["w3"])) if w]
        lines.append(f"| {r['T']} | {r['cell']} | {r['n']} | {r['mlerr_v4']:.3f} | {r['mlerr_v4L']:.3f} | {r['d1']:+.3f} "
                     f"[{r['c1'][0]:+.3f}, {r['c1'][1]:+.3f}] | {r['hit_v4']:.3f} | {r['d2']:+.3f} [{r['c2'][0]:+.3f}, "
                     f"{r['c2'][1]:+.3f}] | {r['def_v4']:.3f} | {r['d3']:+.3f} [{r['c3'][0]:+.3f}, {r['c3'][1]:+.3f}] | "
                     f"{','.join(flags) or '-'} |")
    nw = {k: sum(r[k] for r in res["L2"]) for k in ("w1", "w2", "w3", "w1h", "w2h", "w3h")}
    L2 = nw["w1"] == nw["w2"] == nw["w3"] == 0
    worst = max(res["L2"], key=lambda r: r["d1"])
    lines += ["", f"Số cell tệ hơn (rule, CI chưa hiệu chỉnh): (i) {nw['w1']}, (ii) {nw['w2']}, (iii) {nw['w3']}. "
                  f"Sau Holm (21 cell/metric): (i) {nw['w1h']}, (ii) {nw['w2h']}, (iii) {nw['w3h']}.",
              f"Delta (i) lớn nhất: T{worst['T']} {worst['cell']} {worst['d1']:+.3f} [{worst['c1'][0]:+.3f}, {worst['c1'][1]:+.3f}].",
              f"L2: **{'ĐẠT' if L2 else 'KHÔNG ĐẠT'}**", "",
              f"**Verdict tolerant_v4L: {'GIỮ' if (L1 and L2) else 'LOẠI'}** (L1 {'đạt' if L1 else 'không đạt'}, "
              f"L2 {'đạt' if L2 else 'không đạt'}).", ""]
    res.update(L1_pass=L1, L1_n=n_pass, L2_pass=L2, L2_counts=nw, verdict="GIỮ" if (L1 and L2) else "LOẠI")
    # report-only: coverage / IS, mean-lag error on reversed damaged, lag interval coverage
    lines += ["## Báo kèm (không quyết định verdict)", "",
              "| T | cell | cov v4 | cov v4L | IS v4 | IS v4L | mlerr damaged v4 | mlerr damaged v4L | lag-interval cov v4L (n) |",
              "|---|---|---|---|---|---|---|---|---|"]
    res["report"] = []
    for T in (40, 80, 150):
        for cname in cells_order:
            s = m[(m.cname == cname) & (m["T"] == T)]
            if not len(s):
                continue
            cv4 = covered(s.lo_b, s.hi_b, s.C_t).mean()
            cvL = covered(s.lo_a, s.hi_a, s.C_t).mean()
            is4 = interval_score(s.lo_b, s.hi_b, s.C_t).mean()
            isL = interval_score(s.lo_a, s.hi_a, s.C_t).mean()
            dmg = s[(s.role == 2) & np.isfinite(s.ml_t) & np.isfinite(s.ml_e_a) & np.isfinite(s.ml_e_b)]
            md4 = float(np.abs(dmg.ml_e_b - dmg.ml_t).mean()) if len(dmg) else np.nan
            mdL = float(np.abs(dmg.ml_e_a - dmg.ml_t).mean()) if len(dmg) else np.nan
            li = s[np.isfinite(s.ml_lo_a) & np.isfinite(s.ml_t)]
            lic = float(((li.ml_lo_a <= li.ml_t) & (li.ml_t <= li.ml_hi_a)).mean()) if len(li) else np.nan
            res["report"].append(dict(T=T, cell=cname, cov_v4=cv4, cov_v4L=cvL, is_v4=is4, is_v4L=isL, mlerr_dmg_v4=md4,
                                      mlerr_dmg_v4L=mdL, lagint_cov=lic, lagint_n=len(li)))
            lines.append(f"| {T} | {cname} | {cv4:.3f} | {cvL:.3f} | {is4:.3f} | {isL:.3f} | {md4:.3f} | {mdL:.3f} | "
                         f"{lic:.3f} ({len(li)}) |")
    (out / "analysis_b.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return res


def interval_score(lo, hi, c, alpha=0.05):
    lo, hi, c = np.asarray(lo), np.asarray(hi), np.asarray(c)
    return (hi - lo) + (2 / alpha) * (lo - c) * (c < lo) + (2 / alpha) * (c - hi) * (c > hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    df, methods, cells = load(args.run)
    out = ROOT / "results" / args.run
    boot = Boot(df.topo.unique())
    res = {}
    if "oracle" in methods and "tolerant_v4" in methods:
        res["a"] = part_a(df, boot, out)
    if "tolerant_v4L" in methods:
        res["b"] = part_b(df, boot, out, cells)
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=lambda o: o if not isinstance(o, np.generic)
                                                  else o.item()), encoding="utf-8")
    for k in ("a", "b"):
        if k in res:
            print((out / f"analysis_{k}.md").read_text())


if __name__ == "__main__":
    main()
