"""R2-4 (v4c): apply the pre-registered rule A and the descriptive part B of docs/ext/v4c.md.

Inputs (all D-07 development, seed_base 20261102, so data and damaged skeletons are identical):
  results/ext_v4c_eval/runs.jsonl        plugin, tolerant_v4 (frozen), tolerant_v4c, *_c2
  results/ext_v4c_eval/calibration.json  tuned factors (runner grid; effective = c x pre-scale)
  results/a2_baselines/runs.jsonl        plugin, tolerant_v4, ida_union, bvar_minnesota (uncalibrated)
  results/a2b_pselect/runs.jsonl         pselect_union (uncalibrated)
  results/ext_redteam_calbase/runs.jsonl pselect_cal, ida_cal, bvar_cal (E3, floor 1.0)
Outputs: results/ext_v4c_eval/{ruling.md, describe.md, analysis.json}

Run: python experiments/ext/v4c/analyze.py
"""
from __future__ import annotations

import json
import zlib
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
OUT = RES / "ext_v4c_eval"
B = 2000
SEED = 20261102
TS = (40, 80, 150)
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
PRESCALE = {"tolerant_v4c": 0.5, "pselect_union_c2": 0.5, "bvar_minnesota_c2": 0.5, "ida_union_c2": 0.5}
BASE = ["pselect_union", "ida_union", "bvar_minnesota"]
CAL = {"pselect_union": "pselect_cal", "ida_union": "ida_cal", "bvar_minnesota": "bvar_cal"}
C2 = {x: f"{x}_c2" for x in BASE}


def load(path, methods=None):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if methods and r["method"] not in methods:
            continue
        out[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])] = r
    return out


def cell_label(T, kind, rate):
    return f"T{T} {kind}" + ("" if kind == "none" else f"-{rate}")


class Data:
    def __init__(self):
        self.rows = {}

    def add(self, rows, rename=None):
        for (m, *rest), r in rows.items():
            self.rows[(rename.get(m, m) if rename else m, *rest)] = r

    def runs(self, m, T, kind, rate):
        return {(k[1], k[2]): r for k, r in self.rows.items() if k[0] == m and k[3] == T and k[4] == kind
                and k[5] == rate}

    def coverage(self, m, T, kind, rate):
        ok = [r for r in self.runs(m, T, kind, rate).values() if r["status"] == "ok"]
        n = sum(r["n_nonnull"] for r in ok)
        return sum(r["n_covered_nonnull"] for r in ok) / n if n else float("nan")

    def stat(self, m, T, kind, rate, key):
        v = [r[key] for r in self.runs(m, T, kind, rate).values() if r["status"] == "ok" and r.get(key) is not None]
        return float(np.mean(v)) if v else float("nan")

    def width(self, m, T, kind, rate):
        v = [r["width_kept"] for r in self.runs(m, T, kind, rate).values()
             if r["status"] == "ok" and r.get("width_kept") is not None]
        return float(np.median(v)) if v else float("nan")

    def paired(self, a, b, T, kind, rate, key="iscore_nonnull_mean"):
        """Per-topology arrays of (value a, value b) over runs where both are ok."""
        ra, rb = self.runs(a, T, kind, rate), self.runs(b, T, kind, rate)
        by = defaultdict(lambda: ([], []))
        for k, x in ra.items():
            y = rb.get(k)
            if y and x["status"] == "ok" and y["status"] == "ok" and x.get(key) is not None and y.get(key) is not None:
                by[k[0]][0].append(x[key])
                by[k[0]][1].append(y[key])
        return by


def _boot_index(n_topo, label):
    rng = np.random.default_rng([SEED, zlib.crc32(label.encode())])
    return rng.integers(0, n_topo, size=(B, n_topo))


def diff_ci(by, label):
    topos = sorted(by)
    sa = np.array([sum(by[t][0]) for t in topos])
    sb = np.array([sum(by[t][1]) for t in topos])
    cnt = np.array([len(by[t][0]) for t in topos])
    est = (sa.sum() - sb.sum()) / cnt.sum()
    idx = _boot_index(len(topos), label)
    boots = ((sa[idx] - sb[idx]).sum(1)) / cnt[idx].sum(1)
    lo, hi = np.quantile(boots, (0.025, 0.975))
    p_less = (1 + np.sum(boots >= 0)) / (B + 1)      # H1: diff < 0
    p_greater = (1 + np.sum(boots <= 0)) / (B + 1)   # H1: diff > 0
    ma, mb = sa.sum() / cnt.sum(), sb.sum() / cnt.sum()
    return dict(est=float(est), lo=float(lo), hi=float(hi), p_less=float(p_less), p_greater=float(p_greater),
                mean_a=float(ma), mean_b=float(mb), n=int(cnt.sum()))


def ratio_ci(by, label, lo_eq=0.97, hi_eq=1.03):
    topos = sorted(by)
    sa = np.array([sum(by[t][0]) for t in topos])
    sb = np.array([sum(by[t][1]) for t in topos])
    idx = _boot_index(len(topos), label)
    boots = sa[idx].sum(1) / sb[idx].sum(1)
    lo, hi = np.quantile(boots, (0.025, 0.975))
    p_tost = max((1 + np.sum(boots <= lo_eq)) / (B + 1), (1 + np.sum(boots >= hi_eq)) / (B + 1))
    return dict(ratio=float(sa.sum() / sb.sum()), lo=float(lo), hi=float(hi), p_tost=float(p_tost))


def holm(pvals, alpha):
    order = np.argsort(pvals)
    rej = np.zeros(len(pvals), dtype=bool)
    m = len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def fmt_ci(d):
    return f"{d['est']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]"


def classify(cov_m, d):
    if cov_m >= 0.90 and d["hi"] < 0:
        return "W"
    if d["lo"] > 0:
        return "L"
    return "T"


def main():
    D = Data()
    ev = load(RES / "ext_v4c_eval/runs.jsonl")
    D.add(ev)
    a2 = load(RES / "a2_baselines/runs.jsonl", {"plugin", "tolerant_v4", "ida_union", "bvar_minnesota"})
    a2b = load(RES / "a2b_pselect/runs.jsonl", {"pselect_union"})
    e3 = load(RES / "ext_redteam_calbase/runs.jsonl", {"pselect_cal", "ida_cal", "bvar_cal"})
    D.add({k: v for k, v in a2.items() if k[0] in ("ida_union", "bvar_minnesota")})
    D.add(a2b)
    D.add(e3)
    calib = json.loads((OUT / "calibration.json").read_text())
    out = {"bootstrap": {"B": B, "seed": SEED, "cluster": "topology"}}

    # ---- pairing check against a2_baselines
    pair = {}
    for m in ("plugin", "tolerant_v4"):
        n_same = n_tot = 0
        for k, r in ev.items():
            if k[0] != m:
                continue
            n_tot += 1
            ref = a2.get(k)
            if ref and ref["status"] == r["status"] and ref.get("n_covered_nonnull") == r.get("n_covered_nonnull") \
                    and (r.get("iscore_nonnull_mean") is None or
                         abs(ref["iscore_nonnull_mean"] - r["iscore_nonnull_mean"]) < 1e-9):
                n_same += 1
        pair[m] = [n_same, n_tot]
    out["pairing_vs_a2_baselines"] = pair
    status = defaultdict(lambda: [0, 0])
    for k, r in ev.items():
        status[k[0]][0] += r["status"] == "ok"
        status[k[0]][1] += 1
    out["status_ok"] = dict(status)

    # ---- effective factors
    eff = {}
    for m, p in PRESCALE.items():
        for T in TS:
            for kind in ("none", "extra", "missing", "reversed"):
                c = calib.get(f"{m}|{T}|{kind}")
                pp = 1.0 if (m == "ida_union_c2" and kind == "missing") else p
                eff[f"{m}|{T}|{kind}"] = None if c is None else round(c * pp, 4)
    for T in TS:
        for kind in ("none", "extra", "missing", "reversed"):
            eff[f"tolerant_v4|{T}|{kind}"] = calib.get(f"mod|{T}|{kind}")
            for x, xc in CAL.items():
                pass
    e3cal = json.loads((RES / "ext_redteam_calbase/calibration.json").read_text())
    for x, xc in CAL.items():
        for T in TS:
            for kind in ("none", "extra", "missing", "reversed"):
                eff[f"{xc}(E3)|{T}|{kind}"] = e3cal.get(f"{xc}|{T}|{kind}")
    out["effective_factors"] = eff
    floor_ceiling = []
    for key, v in eff.items():
        m = key.split("|")[0]
        if m in PRESCALE and v is not None:
            pp = 1.0 if (m == "ida_union_c2" and key.endswith("missing")) else 0.5
            if abs(v - pp * 1.0) < 1e-9:
                floor_ceiling.append(f"{key} at floor {v}")
            if abs(v - pp * 10.0) < 1e-9:
                floor_ceiling.append(f"{key} at ceiling {v}")
    out["floor_ceiling"] = floor_ceiling

    # ---- Rule A
    cond1 = []
    for T in (80, 150):
        for kind, rate in CELLS:
            by = D.paired("tolerant_v4c", "tolerant_v4", T, kind, rate)
            rc = ratio_ci(by, f"ratio|{T}|{kind}|{rate}")
            dc = diff_ci(by, f"diff|v4c-v4|{T}|{kind}|{rate}")
            cond1.append(dict(T=T, kind=kind, rate=rate, cov_v4=D.coverage("tolerant_v4", T, kind, rate),
                              cov_v4c=D.coverage("tolerant_v4c", T, kind, rate), IS_v4=dc["mean_b"],
                              IS_v4c=dc["mean_a"], **rc, diff=dc, ok=0.97 <= rc["ratio"] <= 1.03))
    tost_rej = holm(np.array([c["p_tost"] for c in cond1]), 0.05)
    for c, rj in zip(cond1, tost_rej):
        c["equiv_holm"] = bool(rj)
    cond2 = []
    for kind, rate in (("missing", 0.2), ("missing", 0.5)):
        by = D.paired("tolerant_v4c", "tolerant_v4", 40, kind, rate)
        dc = diff_ci(by, f"diff|v4c-v4|40|{kind}|{rate}")
        cov = D.coverage("tolerant_v4c", 40, kind, rate)
        cond2.append(dict(T=40, kind=kind, rate=rate, cov_v4=D.coverage("tolerant_v4", 40, kind, rate), cov_v4c=cov,
                          IS_v4=dc["mean_b"], IS_v4c=dc["mean_a"], diff=dc,
                          width_v4=D.width("tolerant_v4", 40, kind, rate),
                          width_v4c=D.width("tolerant_v4c", 40, kind, rate),
                          ok=cov >= 0.90 and dc["hi"] < 0))
    rj2 = holm(np.array([c["diff"]["p_less"] for c in cond2]), 0.025)
    for c, rj in zip(cond2, rj2):
        c["ok_holm"] = bool(rj and c["cov_v4c"] >= 0.90)
    n1, n2 = sum(c["ok"] for c in cond1), sum(c["ok"] for c in cond2)
    verdict = "RETAINED" if n1 == 14 and n2 == 2 else "REJECTED"
    other40 = []
    for kind, rate in CELLS:
        if kind == "missing":
            continue
        by = D.paired("tolerant_v4c", "tolerant_v4", 40, kind, rate)
        rc = ratio_ci(by, f"ratio|40|{kind}|{rate}")
        other40.append(dict(T=40, kind=kind, rate=rate, cov_v4=D.coverage("tolerant_v4", 40, kind, rate),
                            cov_v4c=D.coverage("tolerant_v4c", 40, kind, rate), **rc))
    null_is = []
    for T in TS:
        for kind, rate in CELLS:
            null_is.append(dict(T=T, kind=kind, rate=rate,
                                v4=D.stat("tolerant_v4", T, kind, rate, "iscore_null_mean"),
                                v4c=D.stat("tolerant_v4c", T, kind, rate, "iscore_null_mean")))
    out["ruleA"] = dict(cond1=cond1, cond2=cond2, n_cond1=n1, n_cond1_equiv_holm=int(tost_rej.sum()), n_cond2=n2,
                        n_cond2_holm=sum(c["ok_holm"] for c in cond2), verdict=verdict, other_T40=other40,
                        null_iscore=null_is)

    # ---- Part B
    comps = {"a": ("tolerant_v4", lambda x: x), "b": ("tolerant_v4", lambda x: CAL[x]),
             "c": ("tolerant_v4", lambda x: C2[x]), "d": ("tolerant_v4c", lambda x: C2[x])}
    cls = {}   # (comp, x, T, kind, rate) -> dict
    for comp, (M, ver) in comps.items():
        for x in BASE:
            xv = ver(x)
            items = []
            for T in TS:
                for kind, rate in CELLS:
                    by = D.paired(M, xv, T, kind, rate)
                    if not by:
                        continue
                    dc = diff_ci(by, f"B|{M}-{xv}|{T}|{kind}|{rate}")
                    covm = D.coverage(M, T, kind, rate)
                    items.append(((T, kind, rate), dc, covm))
            rej = holm(np.array([d["p_less"] for _, d, _ in items]), 0.025)
            for (key, dc, covm), rj in zip(items, rej):
                cls[(comp, x) + key] = dict(diff=dc, cov_M=covm, cls=classify(covm, dc),
                                            win_holm=bool(rj and covm >= 0.90))
    out["partB"] = {"|".join(map(str, k)): v for k, v in cls.items()}

    counts = {}
    for comp in comps:
        for x in BASE:
            sel = [v for k, v in cls.items() if k[0] == comp and k[1] == x]
            nm = [v for k, v in cls.items() if k[0] == comp and k[1] == x and k[3] != "missing"]
            counts[f"{comp}|{x}"] = dict(
                W=sum(v["cls"] == "W" for v in sel), T=sum(v["cls"] == "T" for v in sel),
                L=sum(v["cls"] == "L" for v in sel), W_holm=sum(v["win_holm"] for v in sel), n=len(sel),
                W_nonmissing=sum(v["cls"] == "W" for v in nm), T_nonmissing=sum(v["cls"] == "T" for v in nm),
                L_nonmissing=sum(v["cls"] == "L" for v in nm), W_holm_nonmissing=sum(v["win_holm"] for v in nm),
                n_nonmissing=len(nm))
    out["partB_counts"] = counts

    # D1: joint win vs ida & bvar on reversed/extra (A2 rule), intersection-union p, Holm across those 12 cells
    def joint(comp, cells_):
        ps, res = [], []
        for (T, kind, rate) in cells_:
            a, b = cls[(comp, "ida_union", T, kind, rate)], cls[(comp, "bvar_minnesota", T, kind, rate)]
            win = a["cls"] == "W" and b["cls"] == "W"
            ps.append(max(a["diff"]["p_less"], b["diff"]["p_less"]))
            res.append(dict(cell=cell_label(T, kind, rate), win=win, cls_ida=a["cls"], cls_bvar=b["cls"],
                            cov=a["cov_M"]))
        rej = holm(np.array(ps), 0.025)
        for r, rj in zip(res, rej):
            r["win_holm"] = bool(rj and r["cov"] >= 0.90)
        return res
    rev_ext = [(T, k, r) for k in ("reversed", "extra") for r in (0.2, 0.5) for T in TS]
    D1 = {comp: joint(comp, rev_ext) for comp in comps}
    out["D1"] = D1

    claims = {}
    stated_D1_pass = {"T150 reversed-0.2", "T40 reversed-0.5", "T80 reversed-0.5", "T150 reversed-0.5",
                      "T80 extra-0.2", "T150 extra-0.2", "T150 extra-0.5"}
    claims["D1"] = {comp: dict(pass_cells=sorted(r["cell"] for r in D1[comp] if r["win"]),
                               pass_holm=sorted(r["cell"] for r in D1[comp] if r["win_holm"]),
                               n_rev=sum(r["win"] for r in D1[comp] if "reversed" in r["cell"]),
                               n_ext=sum(r["win"] for r in D1[comp] if "extra" in r["cell"]),
                               same_as_stated=set(r["cell"] for r in D1[comp] if r["win"]) == stated_D1_pass)
                    for comp in comps}
    nonmiss_dmg = [(T, k, r) for T in TS for k in ("extra", "reversed") for r in (0.2, 0.5)]

    def cls_list(comp, x, cells_):
        return {cell_label(*c): cls[(comp, x) + c]["cls"] for c in cells_}

    claims["D2"] = {comp: cls_list(comp, "pselect_union", nonmiss_dmg) for comp in comps}
    rev80 = [(T, "reversed", r) for T in (80, 150) for r in (0.2, 0.5)]
    claims["D3"] = {comp: {x: cls_list(comp, x, rev80) for x in BASE} for comp in comps}
    d4 = [(80, "none", 0.0), (80, "extra", 0.2), (80, "extra", 0.5)]
    claims["D4"] = {comp: cls_list(comp, "ida_union", d4) for comp in comps}
    d5 = [(40, "none", 0.0), (40, "extra", 0.2), (40, "extra", 0.5), (40, "reversed", 0.2)]
    claims["D5"] = {comp: {x: cls_list(comp, x, d5) for x in ("bvar_minnesota", "ida_union")} for comp in comps}
    # D6: factors below 1.0 outside missing, and X_c2 better than X_cal outside missing
    d6_low = [k for k, v in eff.items() if k.split("|")[0] in C2.values() and not k.endswith("missing")
              and v is not None and v < 1.0 - 1e-9]
    d6_better = []
    for x in BASE:
        for T in TS:
            for kind, rate in CELLS:
                if kind == "missing":
                    continue
                by = D.paired(C2[x], CAL[x], T, kind, rate)
                dc = diff_ci(by, f"D6|{x}|{T}|{kind}|{rate}")
                d6_better.append(dict(x=x, cell=cell_label(T, kind, rate), diff=dc,
                                      cov_c2=D.coverage(C2[x], T, kind, rate), cov_cal=D.coverage(CAL[x], T, kind, rate)))
    rej6 = holm(np.array([d["diff"]["p_less"] for d in d6_better]), 0.025)
    for d, rj in zip(d6_better, rej6):
        d["better_holm"] = bool(rj)
    claims["D6"] = dict(factors_below_1=d6_low, n_cells=len(d6_better),
                        n_c2_better=sum(d["diff"]["hi"] < 0 for d in d6_better),
                        n_c2_worse=sum(d["diff"]["lo"] > 0 for d in d6_better),
                        n_c2_better_holm=sum(d["better_holm"] for d in d6_better), cells=d6_better)
    none = [(T, "none", 0.0) for T in TS]
    claims["D7"] = {comp: {x: cls_list(comp, x, none) for x in BASE} for comp in ("c", "d")}
    # missing cells (R-E3a style) for (d)
    miss80 = [(T, "missing", r) for T in (80, 150) for r in (0.2, 0.5)]
    miss40 = [(40, "missing", r) for r in (0.2, 0.5)]
    claims["missing"] = {comp: {x: cls_list(comp, x, miss80 + miss40) for x in BASE} for comp in ("b", "c", "d")}
    out["claims"] = claims

    # per-cell descriptive table values
    table = []
    for T in TS:
        for kind, rate in CELLS:
            row = dict(T=T, kind=kind, rate=rate)
            for m in ["tolerant_v4", "tolerant_v4c"] + BASE + list(CAL.values()) + list(C2.values()):
                row[m] = dict(cov=D.coverage(m, T, kind, rate), IS=D.stat(m, T, kind, rate, "iscore_nonnull_mean"),
                              width=D.width(m, T, kind, rate),
                              IS_null=D.stat(m, T, kind, rate, "iscore_null_mean"))
            table.append(row)
    out["cell_table"] = table
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    write_ruling(out)
    write_describe(out, cls)
    print("verdict:", verdict, "cond1", n1, "/14", "cond2", n2, "/2")


def write_ruling(o):
    A = o["ruleA"]
    L = ["# ext_v4c_eval: rule A (docs/ext/v4c.md, mục 4)", "",
         f"Bootstrap: B = {B}, seed {SEED}, cluster theo topology. Sinh bởi experiments/ext/v4c/analyze.py.", "",
         "## Kiểm tra ghép cặp với a2_baselines", ""]
    for m, (s, t) in o["pairing_vs_a2_baselines"].items():
        L.append(f"- `{m}`: {s}/{t} dòng trùng khít (status, n_covered_nonnull, IS).")
    L.append("- status ok: " + ", ".join(f"`{m}` {a}/{b}" for m, (a, b) in o["status_ok"].items()))
    L += ["", "## Factor hiệu dụng (c × pre-scale), D-07H development", "",
          "| method | T | none | extra | missing | reversed |", "|---|---|---|---|---|---|"]
    eff = o["effective_factors"]
    for m in ["tolerant_v4", "tolerant_v4c", "pselect_union_c2", "pselect_cal(E3)", "ida_union_c2", "ida_cal(E3)",
              "bvar_minnesota_c2", "bvar_cal(E3)"]:
        for T in TS:
            L.append(f"| {m} | {T} | " + " | ".join(str(eff.get(f"{m}|{T}|{k}")) for k in
                                                   ("none", "extra", "missing", "reversed")) + " |")
    L += ["", "Factor chạm sàn/trần của grid hiệu dụng: " + ("; ".join(o["floor_ceiling"]) or "không có"), "",
          "## Điều kiện 1: T ∈ {80, 150}, 14 cell, IS(v4c)/IS(v4) ∈ [0.97, 1.03]", "",
          "| cell | cov v4 | cov v4c | IS v4 | IS v4c | ratio | ratio CI 95% | v4c − v4 (CI) | p_TOST | đạt | TOST Holm |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in A["cond1"]:
        L.append(f"| {cell_label(c['T'], c['kind'], c['rate'])} | {c['cov_v4']:.3f} | {c['cov_v4c']:.3f} | "
                 f"{c['IS_v4']:.3f} | {c['IS_v4c']:.3f} | {c['ratio']:.3f} | [{c['lo']:.3f}, {c['hi']:.3f}] | "
                 f"{fmt_ci(c['diff'])} | {c['p_tost']:.4f} | {'có' if c['ok'] else 'KHÔNG'} | "
                 f"{'có' if c['equiv_holm'] else 'không'} |")
    L += ["", f"**Điều kiện 1: {A['n_cond1']}/14 cell đạt.** Tương đương TOST sau Holm (α = 0.05, 14 cell): "
              f"{A['n_cond1_equiv_holm']}/14.", "",
          "## Điều kiện 2: T = 40 missing, coverage v4c ≥ 0.90 và cận trên CI (v4c − v4) < 0", "",
          "| cell | cov v4 | cov v4c | IS v4 | IS v4c | width v4 | width v4c | v4c − v4 (CI) | p một phía | đạt | đạt (Holm) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in A["cond2"]:
        L.append(f"| {cell_label(c['T'], c['kind'], c['rate'])} | {c['cov_v4']:.3f} | {c['cov_v4c']:.3f} | "
                 f"{c['IS_v4']:.3f} | {c['IS_v4c']:.3f} | {c['width_v4']:.3f} | {c['width_v4c']:.3f} | "
                 f"{fmt_ci(c['diff'])} | {c['diff']['p_less']:.4f} | {'có' if c['ok'] else 'KHÔNG'} | "
                 f"{'có' if c['ok_holm'] else 'không'} |")
    L += ["", f"**Điều kiện 2: {A['n_cond2']}/2 cell đạt; sau Holm (2 cell, α một phía 0.025): {A['n_cond2_holm']}/2.**",
          "", f"## Phán quyết: `tolerant_v4c` **{'GIỮ' if A['verdict'] == 'RETAINED' else 'LOẠI'}** ({A['verdict']})", "",
          "## Báo cáo thêm (không ảnh hưởng quyết định)", "", "T = 40, cell ngoài missing:", "",
          "| cell | cov v4 | cov v4c | ratio IS v4c/v4 | CI 95% |", "|---|---|---|---|---|"]
    for c in A["other_T40"]:
        L.append(f"| {cell_label(c['T'], c['kind'], c['rate'])} | {c['cov_v4']:.3f} | {c['cov_v4c']:.3f} | "
                 f"{c['ratio']:.3f} | [{c['lo']:.3f}, {c['hi']:.3f}] |")
    L += ["", "IS trung bình trên null pair (`iscore_null_mean`):", "", "| cell | v4 | v4c |", "|---|---|---|"]
    for c in A["null_iscore"]:
        L.append(f"| {cell_label(c['T'], c['kind'], c['rate'])} | {c['v4']:.3f} | {c['v4c']:.3f} |")
    (OUT / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_describe(o, cls):
    L = ["# ext_v4c_eval: phần B, so sánh mô tả (docs/ext/v4c.md, mục 4 phần B)", "",
         "So sánh: (a) v4 vs X chưa calibrate (a2_baselines / a2b_pselect); (b) v4 vs X_cal (E3, sàn 1.0); "
         "(c) v4 vs X_c2; (d) v4c vs X_c2. W = M thắng (cov M ≥ 0.90 và cận trên CI < 0), L = M thua (cận dưới > 0), "
         "T = hòa. Holm: 21 cell mỗi cặp (M, X'), α một phía 0.025.", "",
         f"Bootstrap B = {B}, seed {SEED}, cluster theo topology.", "", "## Đếm cell", "",
         "| so sánh | X | W/T/L (21 cell) | W sau Holm | W/T/L ngoài missing (15) | W Holm ngoài missing |",
         "|---|---|---|---|---|---|"]
    for k, c in o["partB_counts"].items():
        comp, x = k.split("|")
        L.append(f"| ({comp}) | {x} | {c['W']}/{c['T']}/{c['L']} | {c['W_holm']} | "
                 f"{c['W_nonmissing']}/{c['T_nonmissing']}/{c['L_nonmissing']} | {c['W_holm_nonmissing']} |")
    L += ["", "## Bảng theo cell: coverage / IS (width)", ""]
    for x in BASE:
        L += [f"### {x}", "", "| cell | v4 | v4c | X | X_cal | X_c2 | (a) | (b) | (c) | (d) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in o["cell_table"]:
            T, kind, rate = r["T"], r["kind"], r["rate"]

            def f(m):
                v = r[m]
                return f"{v['cov']:.3f} / {v['IS']:.2f} ({v['width']:.2f})"
            parts = []
            for comp in "abcd":
                c = cls.get((comp, x, T, kind, rate))
                parts.append("–" if c is None else f"{c['cls']} {fmt_ci(c['diff'])}")
            L.append(f"| {cell_label(T, kind, rate)} | {f('tolerant_v4')} | {f('tolerant_v4c')} | {f(x)} | "
                     f"{f(CAL[x])} | {f(C2[x])} | " + " | ".join(parts) + " |")
        L.append("")
    C = o["claims"]
    L += ["## Các claim vòng 1 ngoài cell missing", "", "### D1 (A2: thắng cả ida và bvar; vòng 1: reversed 4/6, extra 3/6)", "",
          "| so sánh | reversed | extra | cell thắng | cell thắng (Holm, IUT) | giống vòng 1 |", "|---|---|---|---|---|---|"]
    for comp, v in C["D1"].items():
        L.append(f"| ({comp}) | {v['n_rev']}/6 | {v['n_ext']}/6 | {', '.join(v['pass_cells'])} | "
                 f"{', '.join(v['pass_holm'])} | {'có' if v['same_as_stated'] else 'KHÔNG'} |")
    L += ["", "### D2 (A2b: v4 thắng pselect_union ở 12/12 cell extra/reversed)", "",
          "| so sánh | " + " | ".join(C["D2"]["a"].keys()) + " |", "|---|" + "---|" * len(C["D2"]["a"])]
    for comp, v in C["D2"].items():
        L.append(f"| ({comp}) | " + " | ".join(v.values()) + " |")
    L += ["", "### D3 (E3: T ≥ 80, v4 thắng mọi baseline đã calibrate ở 4/4 cell reversed)", "",
          "| so sánh | X | " + " | ".join(C["D3"]["a"]["ida_union"].keys()) + " |", "|---|---|---|---|---|---|"]
    for comp, v in C["D3"].items():
        for x, w in v.items():
            L.append(f"| ({comp}) | {x} | " + " | ".join(w.values()) + " |")
    L += ["", "### D4 (E3: T = 80 none/extra, v4 hòa ida_cal)", "",
          "| so sánh | " + " | ".join(C["D4"]["a"].keys()) + " |", "|---|---|---|---|"]
    for comp, v in C["D4"].items():
        L.append(f"| ({comp}) | " + " | ".join(v.values()) + " |")
    L += ["", "### D5 (E3: T = 40, v4 hòa bvar_cal và ida_cal trên none/extra/reversed-0.2)", "",
          "| so sánh | X | " + " | ".join(C["D5"]["a"]["ida_union"].keys()) + " |", "|---|---|---|---|---|---|"]
    for comp, v in C["D5"].items():
        for x, w in v.items():
            L.append(f"| ({comp}) | {x} | " + " | ".join(w.values()) + " |")
    d6 = C["D6"]
    L += ["", "### D6 (baseline ở sàn 1.0 và over-cover ngoài missing)", "",
          "Factor hiệu dụng < 1.0 của X_c2 ngoài missing: " + (", ".join(d6["factors_below_1"]) or "không có"), "",
          f"X_c2 − X_cal ngoài missing ({d6['n_cells']} cell): X_c2 tốt hơn (cận trên < 0) {d6['n_c2_better']}, "
          f"sau Holm {d6['n_c2_better_holm']}; X_c2 tệ hơn (cận dưới > 0) {d6['n_c2_worse']}.", "",
          "| X | cell | cov X_cal | cov X_c2 | X_c2 − X_cal (CI) |", "|---|---|---|---|---|"]
    for d in d6["cells"]:
        L.append(f"| {d['x']} | {d['cell']} | {d['cov_cal']:.3f} | {d['cov_c2']:.3f} | {fmt_ci(d['diff'])} |")
    L += ["", "### D7 (cell none)", "", "| so sánh | X | T40 | T80 | T150 |", "|---|---|---|---|---|"]
    for comp, v in C["D7"].items():
        for x, w in v.items():
            L.append(f"| ({comp}) | {x} | " + " | ".join(w.values()) + " |")
    L += ["", "### Cell missing (R-E3a: 4 cell T ≥ 80; thêm 2 cell T40)", "",
          "| so sánh | X | " + " | ".join(C["missing"]["d"]["ida_union"].keys()) + " |",
          "|---|---|" + "---|" * len(C["missing"]["d"]["ida_union"])]
    for comp, v in C["missing"].items():
        for x, w in v.items():
            L.append(f"| ({comp}) | {x} | " + " | ".join(w.values()) + " |")
    (OUT / "describe.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
