"""R3-7 (v4cverify): independent recomputation of rule A and part B of docs/ext/v4c.md.

Written from the rule text only (docs/ext/v4c.md, section 4); it does not import or read
experiments/ext/v4c/analyze.py. Reads results/{ext_v4c_eval,a2_baselines,a2b_pselect,
ext_redteam_calbase}/runs.jsonl and calibration files. Writes results/ext_v4cverify_recompute/.

Bootstrap: cluster by topology, B = 2000, seed 20261102, percentile. One index matrix
(B x n_topology) is drawn once and shared by every cell and comparison (common random numbers);
analyze.py draws its own, so CIs/p may differ slightly (tolerances in docs/ext/v4cverify.md).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
OUT = RES / "ext_v4cverify_recompute"
B, SEED = 2000, 20261102
TS = [40, 80, 150]
CELLS = [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
NONMISS = [c for c in CELLS if c[0] != "missing"]


def load(run):
    d = {}
    for line in open(RES / run / "runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("scenario", "clean") != "clean":
            continue
        d[(r["method"], r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))] = r
    return d


V = load("ext_v4c_eval")
A2 = load("a2_baselines")
A2B = load("a2b_pselect")
E3 = load("ext_redteam_calbase")
TOPOS = sorted({k[1] for k in V})
REPS = sorted({k[2] for k in V})
TIDX = {t: i for i, t in enumerate(TOPOS)}
IDX = np.random.default_rng(SEED).integers(0, len(TOPOS), size=(B, len(TOPOS)))

SRC = {  # (label) -> (store, method name)
    "v4": (V, "tolerant_v4"), "v4c": (V, "tolerant_v4c"), "plugin": (V, "plugin"),
    "pselect_union": (A2B, "pselect_union"), "ida_union": (A2, "ida_union"), "bvar_minnesota": (A2, "bvar_minnesota"),
    "pselect_union_cal": (E3, "pselect_cal"), "ida_union_cal": (E3, "ida_cal"), "bvar_minnesota_cal": (E3, "bvar_cal"),
    "pselect_union_c2": (V, "pselect_union_c2"), "ida_union_c2": (V, "ida_union_c2"),
    "bvar_minnesota_c2": (V, "bvar_minnesota_c2"),
}


def rows(label, T, kind, rate):
    store, m = SRC[label]
    return {(k[1], k[2]): r for k, r in store.items() if k[0] == m and k[3] == T and k[4] == kind and k[5] == rate}


_cache = {}


def cellrows(label, T, kind, rate):
    key = (label, T, kind, rate)
    if key not in _cache:
        _cache[key] = rows(label, T, kind, rate)
    return _cache[key]


def coverage(label, T, kind, rate):
    rr = cellrows(label, T, kind, rate).values()
    return sum(r["n_covered_nonnull"] for r in rr) / sum(r["n_nonnull"] for r in rr)


def mean_field(label, T, kind, rate, f):
    rr = [r for r in cellrows(label, T, kind, rate).values() if r["status"] == "ok"]
    return float(np.mean([r[f] for r in rr]))


def paired(a, b, T, kind, rate):
    """Paired stats of IS(a) - IS(b) and IS(a)/IS(b) over runs where both are ok."""
    ra, rb = cellrows(a, T, kind, rate), cellrows(b, T, kind, rate)
    keys = sorted(k for k in ra if k in rb and ra[k]["status"] == "ok" and rb[k]["status"] == "ok")
    # per-topology sums (equal replicate counts per topology when all ok)
    sa = np.zeros(len(TOPOS)); sb = np.zeros(len(TOPOS)); n = np.zeros(len(TOPOS))
    for k in keys:
        i = TIDX[k[0]]
        sa[i] += ra[k]["iscore_nonnull_mean"]; sb[i] += rb[k]["iscore_nonnull_mean"]; n[i] += 1
    ma, mb = sa.sum() / n.sum(), sb.sum() / n.sum()
    bn = n[IDX].sum(1)
    ba, bb = sa[IDX].sum(1) / bn, sb[IDX].sum(1) / bn
    d, ratio = ba - bb, ba / bb
    lo, hi = np.percentile(d, [2.5, 97.5])
    rlo, rhi = np.percentile(ratio, [2.5, 97.5])
    p_less = (1 + np.sum(d >= 0)) / (B + 1)
    p_tost = max((1 + np.sum(ratio <= 0.97)) / (B + 1), (1 + np.sum(ratio >= 1.03)) / (B + 1))
    return {"n_runs": len(keys), "IS_a": ma, "IS_b": mb, "diff": ma - mb, "ci": [float(lo), float(hi)],
            "ratio": ma / mb, "ratio_ci": [float(rlo), float(rhi)], "p_less": float(p_less), "p_tost": float(p_tost)}


def holm(ps, alpha):
    order = np.argsort(ps)
    m = len(ps)
    rej = [False] * m
    for j, i in enumerate(order):
        if ps[i] <= alpha / (m - j):
            rej[i] = True
        else:
            break
    return rej


def name(T, kind, rate):
    return f"T{T} {kind}" if kind == "none" else f"T{T} {kind}-{rate}"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    # ---------------- pairing checks ----------------
    pc = {}
    for lab, store, m in [("plugin vs a2_baselines", A2, "plugin"), ("tolerant_v4 vs a2_baselines", A2, "tolerant_v4"),
                          ("tolerant_v4 vs a2b_pselect", A2B, "tolerant_v4"),
                          ("tolerant_v4 vs ext_redteam_calbase", E3, "tolerant_v4"),
                          ("plugin vs a2b_pselect", A2B, "plugin"), ("plugin vs ext_redteam_calbase", E3, "plugin")]:
        mine = {k: r for k, r in V.items() if k[0] == m}
        same_all = same_key = 0
        for k, r in mine.items():
            o = store.get(k)
            if o is None:
                continue
            if all(r.get(f) == o.get(f) for f in ("status", "n_covered_nonnull", "iscore_nonnull_mean")):
                same_key += 1
            if {f: v for f, v in r.items()} == {f: v for f, v in o.items()}:
                same_all += 1
        pc[lab] = {"n": len(mine), "match_status_ncov_IS": same_key, "match_all_fields": same_all}
    out["pairing"] = pc
    status = {m: sum(1 for k, r in V.items() if k[0] == m and r["status"] == "ok") for m in
              ["plugin", "tolerant_v4", "tolerant_v4c", "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2"]}
    out["status_ok"] = status

    # ---------------- rule A ----------------
    c1 = []
    for T in (80, 150):
        for kind, rate in CELLS:
            s = paired("v4c", "v4", T, kind, rate)
            s.update(cell=name(T, kind, rate), cov_v4=coverage("v4", T, kind, rate),
                     cov_v4c=coverage("v4c", T, kind, rate), pass_=0.97 <= s["ratio"] <= 1.03)
            c1.append(s)
    tost_rej = holm([s["p_tost"] for s in c1], 0.05)
    for s, r in zip(c1, tost_rej):
        s["tost_holm"] = r
    c2 = []
    for rate in (0.2, 0.5):
        s = paired("v4c", "v4", 40, "missing", rate)
        s.update(cell=name(40, "missing", rate), cov_v4=coverage("v4", 40, "missing", rate),
                 cov_v4c=coverage("v4c", 40, "missing", rate),
                 width_v4=mean_field("v4", 40, "missing", rate, "width_kept"),
                 width_v4c=mean_field("v4c", 40, "missing", rate, "width_kept"))
        s["pass_"] = s["cov_v4c"] >= 0.90 and s["ci"][1] < 0
        c2.append(s)
    c2h = holm([s["p_less"] for s in c2], 0.025)
    for s, r in zip(c2, c2h):
        s["pass_holm"] = bool(r and s["cov_v4c"] >= 0.90)
    extraA = []
    for kind, rate in CELLS:
        if kind == "missing":
            continue
        s = paired("v4c", "v4", 40, kind, rate)
        s.update(cell=name(40, kind, rate), cov_v4=coverage("v4", 40, kind, rate), cov_v4c=coverage("v4c", 40, kind, rate))
        extraA.append(s)
    n1 = sum(s["pass_"] for s in c1); n2 = sum(s["pass_"] for s in c2)
    out["ruleA"] = {"C1": c1, "C1_pass": n1, "C1_tost_holm": int(sum(tost_rej)), "C2": c2, "C2_pass": n2,
                    "C2_pass_holm": int(sum(s["pass_holm"] for s in c2)),
                    "verdict": "RETAINED" if (n1 == 14 and n2 == 2) else "REJECTED", "T40_other": extraA,
                    "ratio_range_C1": [min(s["ratio"] for s in c1), max(s["ratio"] for s in c1)]}

    # ---------------- effective factors ----------------
    cal = json.loads((RES / "ext_v4c_eval" / "calibration.json").read_text())
    e3cal = json.loads((RES / "ext_redteam_calbase" / "calibration.json").read_text())
    eff = {}
    for m in ["tolerant_v4c", "pselect_union_c2", "ida_union_c2", "bvar_minnesota_c2"]:
        for T in TS:
            for k in ("none", "extra", "missing", "reversed"):
                p = 1.0 if (m == "ida_union_c2" and k == "missing") else 0.5
                eff[f"{m}|{T}|{k}"] = round(cal[f"{m}|{T}|{k}"] * p, 4)
    below1 = [k for k, v in eff.items() if v < 1.0 and not k.endswith("missing") and not k.startswith("tolerant")]
    below1_all = [k for k, v in eff.items() if v < 1.0]
    floor_ceiling = [k for k in eff if cal[k] in (1.0, 10.0)]
    e3map = {"pselect_union_c2": "pselect_cal", "ida_union_c2": "ida_cal", "bvar_minnesota_c2": "bvar_cal"}
    cmp27 = {}
    for k, v in eff.items():
        m, T, kd = k.split("|")
        if m in e3map:
            e = e3cal[f"{e3map[m]}|{T}|{kd}"]
            if e != 1.0:
                cmp27[k] = [v, e, round(v - e, 4)]
    out["factors"] = {"effective": eff, "v4_frozen": {k: cal[k] for k in cal if k.startswith("mod|")},
                      "below_1_nonmissing_baselines": below1, "below_1_all": below1_all,
                      "raw_c_at_grid_floor_or_ceiling": floor_ceiling,
                      "c2_vs_E3_not_floor": {"n": len(cmp27), "exact_equal": sum(1 for x in cmp27.values() if x[2] == 0),
                                             "absdiff_ge_0.1": {k: x for k, x in cmp27.items() if abs(x[2]) >= 0.1 - 1e-9},
                                             "all": cmp27}}

    # ---------------- part B ----------------
    Xs = ["pselect_union", "ida_union", "bvar_minnesota"]
    comps = {"a": ("v4", ""), "b": ("v4", "_cal"), "c": ("v4", "_c2"), "d": ("v4c", "_c2")}
    cls = {}
    counts = {}
    for c, (M, suf) in comps.items():
        for X in Xs:
            Xp = X + suf
            res = []
            for T in TS:
                for kind, rate in CELLS:
                    s = paired(M, Xp, T, kind, rate)
                    s["cov_M"] = coverage(M, T, kind, rate)
                    s["cov_X"] = coverage(Xp, T, kind, rate)
                    s["T"], s["kind"], s["rate"], s["cell"] = T, kind, rate, name(T, kind, rate)
                    s["class"] = "W" if (s["cov_M"] >= 0.90 and s["ci"][1] < 0) else ("L" if s["ci"][0] > 0 else "T")
                    res.append(s)
            rej = holm([s["p_less"] for s in res], 0.025)
            for s, r in zip(res, rej):
                s["W_holm"] = bool(r and s["cov_M"] >= 0.90)
            cls[(c, X)] = res
            nm = [s for s in res if s["kind"] != "missing"]
            counts[f"({c}) {X}"] = {
                "W/T/L": "/".join(str(sum(s["class"] == x for s in res)) for x in "WTL"),
                "W_holm": sum(s["W_holm"] for s in res),
                "W/T/L_nonmissing": "/".join(str(sum(s["class"] == x for s in nm)) for x in "WTL"),
                "W_holm_nonmissing": sum(s["W_holm"] for s in nm)}
    out["partB_counts"] = counts

    def get(c, X, cell):
        return next(s for s in cls[(c, X)] if s["cell"] == cell)

    # D1: win both ida and bvar, on reversed + extra cells (12)
    d1cells = [name(T, k, r) for T in TS for k in ("extra", "reversed") for r in (0.2, 0.5)]
    D1 = {}
    for c in comps:
        wins, ps, covok = [], [], []
        for cell in d1cells:
            a, b = get(c, "ida_union", cell), get(c, "bvar_minnesota", cell)
            wins.append(a["class"] == "W" and b["class"] == "W")
            ps.append(max(a["p_less"], b["p_less"]))
            covok.append(a["cov_M"] >= 0.90)
        rej = holm(ps, 0.025)
        D1[c] = {"reversed": sum(w for w, cl in zip(wins, d1cells) if "reversed" in cl),
                 "extra": sum(w for w, cl in zip(wins, d1cells) if "extra" in cl),
                 "win_cells": sorted(cl for w, cl in zip(wins, d1cells) if w),
                 "win_cells_holm_iut": sorted(cl for r, ok, cl in zip(rej, covok, d1cells) if r and ok)}
    out["D1"] = D1
    out["D2"] = {c: "".join(get(c, "pselect_union", cl)["class"] for cl in d1cells) for c in comps}
    out["D3"] = {f"({c}) {X}": "".join(get(c, X, name(T, "reversed", r))["class"] for T in (80, 150) for r in (0.2, 0.5))
                 for c in comps for X in Xs}
    out["D4"] = {c: "".join(get(c, "ida_union", cl)["class"] for cl in ["T80 none", "T80 extra-0.2", "T80 extra-0.5"])
                 for c in comps}
    out["D5"] = {f"({c}) {X}": "".join(get(c, X, cl)["class"] for cl in
                                        ["T40 none", "T40 extra-0.2", "T40 extra-0.5", "T40 reversed-0.2"])
                 for c in comps for X in ("bvar_minnesota", "ida_union")}
    out["D7"] = {f"({c}) {X}": "".join(get(c, X, f"T{T} none")["class"] for T in TS) for c in ("c", "d") for X in Xs}
    misscells = ["T80 missing-0.2", "T80 missing-0.5", "T150 missing-0.2", "T150 missing-0.5",
                 "T40 missing-0.2", "T40 missing-0.5"]
    out["missing"] = {f"({c}) {X}": "".join(get(c, X, cl)["class"] for cl in misscells) for c in ("b", "c", "d")
                      for X in Xs}
    # D6: X_c2 - X_cal outside missing (45 cells)
    d6 = []
    for X in Xs:
        for T in TS:
            for kind, rate in NONMISS:
                s = paired(X + "_c2", X + "_cal", T, kind, rate)
                s["cell"] = f"{X} {name(T, kind, rate)}"
                d6.append(s)
    rej = holm([s["p_less"] for s in d6], 0.025)
    out["D6"] = {"better": sum(s["ci"][1] < 0 for s in d6), "better_holm": int(sum(rej)),
                 "worse": sum(s["ci"][0] > 0 for s in d6),
                 "better_cells": [s["cell"] for s in d6 if s["ci"][1] < 0],
                 "worse_cells": [s["cell"] for s in d6 if s["ci"][0] > 0],
                 "better_holm_cells": [s["cell"] for s, r in zip(d6, rej) if r]}
    # borderline cells in part B: CI bound within +-0.02 of 0, or cov_M within 0.002 of 0.90
    bl = []
    for (c, X), res in cls.items():
        for s in res:
            if min(abs(s["ci"][0]), abs(s["ci"][1])) <= 0.02 or abs(s["cov_M"] - 0.90) <= 0.002:
                bl.append({"comp": c, "X": X, "cell": s["cell"], "class": s["class"], "ci": s["ci"], "cov_M": s["cov_M"]})
    out["partB_borderline"] = bl
    out["partB_cells"] = {f"({c}) {X}": [{k: s[k] for k in ("cell", "class", "W_holm", "diff", "ci", "p_less", "cov_M",
                                                         "cov_X", "IS_a", "IS_b")} for s in res]
                          for (c, X), res in cls.items()}
    (OUT / "recompute.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")

    # ---------------- text summary ----------------
    L = ["# R3-7 recompute (experiments/ext/v4cverify/recompute.py)", ""]
    L.append(f"pairing: {json.dumps(pc)}")
    L.append(f"status ok: {status}")
    L += ["", "## Rule A, C1 (T80/150)", "cell | cov v4 | cov v4c | IS v4 | IS v4c | ratio | ratio CI | diff [CI] | p_TOST | pass | TOST Holm"]
    for s in c1:
        L.append(f"{s['cell']} | {s['cov_v4']:.3f} | {s['cov_v4c']:.3f} | {s['IS_b']:.3f} | {s['IS_a']:.3f} | {s['ratio']:.3f} | "
                 f"[{s['ratio_ci'][0]:.3f}, {s['ratio_ci'][1]:.3f}] | {s['diff']:+.2f} [{s['ci'][0]:+.2f}, {s['ci'][1]:+.2f}] | "
                 f"{s['p_tost']:.4f} | {s['pass_']} | {s['tost_holm']}")
    L.append(f"C1 pass {n1}/14; TOST Holm {sum(tost_rej)}/14; ratio range {out['ruleA']['ratio_range_C1']}")
    L += ["", "## Rule A, C2 (T40 missing)"]
    for s in c2:
        L.append(f"{s['cell']} | cov {s['cov_v4']:.3f} -> {s['cov_v4c']:.3f} | IS {s['IS_b']:.3f} -> {s['IS_a']:.3f} | "
                 f"width {s['width_v4']:.3f} -> {s['width_v4c']:.3f} | diff {s['diff']:+.2f} [{s['ci'][0]:+.2f}, {s['ci'][1]:+.2f}] | "
                 f"p {s['p_less']:.4f} | pass {s['pass_']} | Holm {s['pass_holm']}")
    L.append(f"C2 pass {n2}/2; Holm {out['ruleA']['C2_pass_holm']}/2")
    L.append(f"VERDICT: {out['ruleA']['verdict']}")
    L += ["", "## T40 other cells (ratio v4c/v4)"]
    for s in extraA:
        L.append(f"{s['cell']} | cov {s['cov_v4']:.3f} -> {s['cov_v4c']:.3f} | ratio {s['ratio']:.3f} [{s['ratio_ci'][0]:.3f}, {s['ratio_ci'][1]:.3f}]")
    L += ["", "## Factors", f"below 1.0 outside missing (baselines): {below1}", f"below 1.0 all: {below1_all}",
          f"raw c at floor/ceiling: {floor_ceiling}",
          f"c2 vs E3 (E3 not at floor): n={len(cmp27)}, exact equal {out['factors']['c2_vs_E3_not_floor']['exact_equal']}, "
          f"|diff|>=0.1: {out['factors']['c2_vs_E3_not_floor']['absdiff_ge_0.1']}"]
    L += ["", "## Part B counts"] + [f"{k}: {v}" for k, v in counts.items()]
    for key in ("D1", "D2", "D3", "D4", "D5", "D7", "missing", "D6"):
        L += ["", f"## {key}", json.dumps(out[key], indent=1)]
    L += ["", f"## borderline part-B cells ({len(bl)})"] + [json.dumps(b) for b in bl]
    (OUT / "recompute.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
