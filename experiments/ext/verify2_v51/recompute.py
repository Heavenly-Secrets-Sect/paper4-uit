"""Skeptic check (verify2_v51): independent recomputation of every rule-bearing number of docs/ext/v51.md
from the runs.jsonl files, with own code (not experiments/ext/v51/common.py), plus bootstrap-seed
sensitivity of the CI-based conditions and Holm counts.

Writes results/ext_verify2_v51/recompute.json and recompute.md
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
TS = [40, 80, 150]
DAM = [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]


def load(name):
    return [json.loads(l) for l in open(RES / name / "runs.jsonl")]


def k_of(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def table(rows, m):
    return {k_of(r): r for r in rows if r["method"] == m}


def v4_identical(a, b):
    A, B = table(a, "tolerant_v4"), table(b, "tolerant_v4")
    same = sum(1 for k in A if k in B and A[k]["status"] == B[k]["status"]
               and (A[k]["status"] != "ok" or (A[k]["iscore_nonnull_mean"] == B[k]["iscore_nonnull_mean"]
                                               and A[k]["n_covered_nonnull"] == B[k]["n_covered_nonnull"])))
    return same, len(A), len(B)


def cell(tab, T, kind, rate, sc="clean"):
    ok = [r for k, r in tab.items() if k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate and r["status"] == "ok"]
    allr = [r for k, r in tab.items() if k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate]
    return {"n": len(ok), "of": len(allr),
            "cov": sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok),
            "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok]))}


def diffs(ta, tb, T, kind, rate, sc="clean"):
    d = defaultdict(list)
    for k, r in ta.items():
        if k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate and r["status"] == "ok":
            o = tb.get(k)
            if o is not None and o["status"] == "ok":
                d[k[1]].append(r["iscore_nonnull_mean"] - o["iscore_nonnull_mean"])
    return d


def boot(d, B, seed):
    topos = sorted(d)
    s = np.array([sum(d[t]) for t in topos]); c = np.array([len(d[t]) for t in topos])
    idx = np.random.default_rng(seed).integers(0, len(topos), size=(B, len(topos)))
    return s[idx].sum(1) / c[idx].sum(1), float(s.sum() / c.sum())


def pair_stats(d, seed=0, B=4000):
    b, est = boot(d, B, seed)
    lo, hi = np.quantile(b, (0.025, 0.975))
    return {"est": est, "lo": float(lo), "hi": float(hi),
            "p_less": (1 + int((b >= 0).sum())) / (B + 1), "p_greater": (1 + int((b <= 0).sum())) / (B + 1)}


def holm(p, a=0.025):
    o = np.argsort(p); rej = [False] * len(p)
    for i, j in enumerate(o):
        if p[j] <= a / (len(p) - i):
            rej[j] = True
        else:
            break
    return rej


out, md = {}, ["# verify2_v51: independent recomputation (experiments/ext/verify2_v51/recompute.py)", ""]

# ---------------- (a) pairing and v5 counts ----------------
nar, red, tlp, ev, abl = (load(n) for n in ("ext_narrow_eval", "ext_redteam_calbase", "ext_tlp_eval", "ext_v51_eval",
                                              "ext_narrow_ablation"))
pairing = {"ev_vs_red": v4_identical(ev, red), "ev_vs_tlp": v4_identical(ev, tlp), "ev_vs_nar": v4_identical(ev, nar),
           "ev_vs_abl": v4_identical(ev, abl), "nar_vs_red": v4_identical(nar, red), "nar_vs_tlp": v4_identical(nar, tlp)}
out["pairing"] = pairing
md += ["## Pairing (exact equality of tolerant_v4 IS and covered counts)", ""] + [f"- {k}: {v[0]}/{v[1]} (rows {v[1]} vs {v[2]})" for k, v in pairing.items()]

T5 = table(nar, "tolerant_v5")
TX = {"pselect_cal": table(red, "pselect_cal"), "fullvar_cal": table(red, "fullvar_cal"),
      "targeted_lp_cal": table(tlp, "targeted_lp_cal")}
T51, T4 = table(ev, "tolerant_v5_1"), table(ev, "tolerant_v4")
T5c2 = table(abl, "tolerant_v5_cal2")


def wins(tm, tx, seed):
    w, p = [], []
    for T in TS:
        for kind, rate in DAM:
            c = cell(tm, T, kind, rate)
            s = pair_stats(diffs(tm, tx, T, kind, rate), seed)
            w.append(c["cov"] >= 0.90 and s["hi"] < 0); p.append(s["p_less"] if c["cov"] >= 0.90 else 1.0)
    return sum(w), sum(holm(p))


md += ["", "## Win counts over 18 damaged cells (cov >= 0.90 and CI upper < 0), raw / Holm, bootstrap seeds 0, 11, 12", ""]
for lab, tm in (("v5 (round 1)", T5), ("v5_1", T51)):
    for X, tx in list(TX.items()) + ([("tolerant_v4", T4)] if lab == "v5_1" else []):
        res = [wins(tm, tx, s) for s in (0, 11, 12)]
        out[f"wins|{lab}|{X}"] = res
        md.append(f"- {lab} vs {X}: " + ", ".join(f"{a}/{b}" for a, b in res))

# ---------------- (b) rule ----------------
md += ["", "## Rule (b) recomputed (seed 0 / 11 / 12 for CI conditions)", ""]
rule = {}
for seed in (0, 11, 12):
    c1 = []; c1p = []
    for rate in (0.2, 0.5):
        c = cell(T51, 40, "missing", rate); s = pair_stats(diffs(T51, T4, 40, "missing", rate), seed)
        c1.append(c["cov"] >= 0.90 and s["hi"] < 0); c1p.append(s["p_less"])
    c4a, c4b = [], []
    for rate in (0.2, 0.5):
        sa = pair_stats(diffs(T51, TX["pselect_cal"], 40, "missing", rate), seed)
        sb = pair_stats(diffs(T51, TX["targeted_lp_cal"], 40, "missing", rate), seed)
        c4a.append(cell(T51, 40, "missing", rate)["cov"] >= 0.90 and sa["hi"] < 0); c4b.append(sb["lo"] <= 0)
    rule[seed] = {"C1": c1, "C1_holm": holm(c1p), "C4a": c4a, "C4b": c4b}
c2, c2r, c2w = [], [], []
for T in (80, 150):
    for kind, rate in DAM:
        a, b = cell(T51, T, kind, rate), cell(T4, T, kind, rate)
        c2.append(a["cov"] >= 0.90 and a["IS"] <= 1.05 * b["IS"]); c2r.append((T, kind, rate, round(a["cov"], 4), round(a["IS"] / b["IS"], 4)))
        c2w.append(pair_stats(diffs(T51, T4, T, kind, rate), 0)["p_greater"])
c3, c3r, c3w = [], [], []
for T, kind, rate in [(40, "none", 0.0), (80, "none", 0.0), (150, "none", 0.0)] + [(40, k, r) for k in ("extra", "reversed") for r in (0.2, 0.5)]:
    a, b = cell(T51, T, kind, rate), cell(T4, T, kind, rate)
    c3.append(a["IS"] <= 1.05 * b["IS"]); c3r.append((T, kind, rate, round(a["IS"] / b["IS"], 4)))
    c3w.append(pair_stats(diffs(T51, T4, T, kind, rate), 0)["p_greater"])
out["rule_b"] = {"CI_conditions_by_seed": rule, "C2": c2, "C2_cells": c2r, "C2_worse_holm": sum(holm(c2w)),
                 "C2_worse_uncorrected": sum(p <= 0.025 for p in c2w), "C3": c3, "C3_cells": c3r,
                 "C3_worse_holm": sum(holm(c3w))}
for seed, v in rule.items():
    md.append(f"- seed {seed}: C1 {sum(v['C1'])}/2 (Holm {sum(v['C1_holm'])}/2), C4a {sum(v['C4a'])}/2, C4b {sum(v['C4b'])}/2")
md.append(f"- C2 {sum(c2)}/12; min coverage {min(x[3] for x in c2r)}, ratio range {min(x[4] for x in c2r)}–{max(x[4] for x in c2r)}; "
          f"significantly worse than v4: uncorrected {out['rule_b']['C2_worse_uncorrected']}/12, Holm {out['rule_b']['C2_worse_holm']}/12")
md.append(f"- C3 {sum(c3)}/7; ratio range {min(x[3] for x in c3r)}–{max(x[3] for x in c3r)}; worse after Holm {out['rule_b']['C3_worse_holm']}/7")
# margin of C2 coverage gate
md.append(f"- C2 coverage margin: cells with cov < 0.93: {[x[:3] + (x[3],) for x in c2r if x[3] < 0.93]}")

# v5_1 vs v5 and vs v5_cal2 in missing cells
md += ["", "## v5_1 − v5 (round 1) and v5_1 − v5_cal2, missing cells (seed 0)", ""]
for T in TS:
    for rate in (0.2, 0.5):
        a = pair_stats(diffs(T51, T5, T, "missing", rate)); b = pair_stats(diffs(T51, T5c2, T, "missing", rate))
        out[f"vs_v5|{T}|{rate}"] = a; out[f"vs_v5cal2|{T}|{rate}"] = b
        md.append(f"- T={T} missing-{rate}: vs v5 {a['est']:+.3f} [{a['lo']:+.3f}, {a['hi']:+.3f}]; vs v5_cal2 {b['est']:+.3f} [{b['lo']:+.3f}, {b['hi']:+.3f}]")

# calibration factor difference v5 (round 1) vs v5_1: attribution caveat
cal_n = json.loads((RES / "ext_narrow_eval" / "calibration.json").read_text())
cal_e = json.loads((RES / "ext_v51_eval" / "calibration.json").read_text())
fac = {f"{T}|{k}": (cal_n.get(f"tolerant_v5|{T}|{k}"), cal_e.get(f"tolerant_v5_1|{T}|{k}")) for T in TS
       for k in ("none", "extra", "missing", "reversed")}
out["factors_v5_vs_v51"] = fac
md += ["", "## Width factors (runner value) tolerant_v5 (ext_narrow_eval) vs tolerant_v5_1 (ext_v51_eval)", ""]
md += [f"- {k}: {a} vs {b}" for k, (a, b) in fac.items()]

# ---------------- (c) a1 ----------------
a1 = load("ext_v51_a1") + load("ext_v51_a1t40")
A51, A4 = table(a1, "tolerant_v5_1"), table(a1, "tolerant_v4")
md += ["", "## a1 scenarios: v5_1 coverage (v4) per cell; one-sided p for cov < 0.90 (topology bootstrap, ratio of sums)", ""]
for sc in ("latent1", "latent3", "noise0.1"):
    covs, ps, lines = [], [], []
    for T in TS:
        for kind, rate in (("none", 0.0), ("missing", 0.2), ("reversed", 0.2)):
            c, c4 = cell(A51, T, kind, rate, sc), cell(A4, T, kind, rate, sc)
            per = defaultdict(lambda: [0, 0])
            for k, r in A51.items():
                if k[0] == sc and k[3] == T and k[4] == kind and k[5] == rate and r["status"] == "ok":
                    per[k[1]][0] += r["n_covered_nonnull"]; per[k[1]][1] += r["n_nonnull"]
            tp = sorted(per); cv = np.array([per[t][0] for t in tp]); nv = np.array([per[t][1] for t in tp])
            idx = np.random.default_rng(2).integers(0, len(tp), size=(10000, len(tp)))
            bc = cv[idx].sum(1) / nv[idx].sum(1)
            p = (1 + int((bc >= 0.90).sum())) / 10001
            covs.append(c["cov"]); ps.append(p)
            lines.append(f"  - T={T} {kind}-{rate}: {c['cov']:.4f} (v4 {c4['cov']:.4f}), IS {c['IS']:.2f} vs {c4['IS']:.2f}, p(cov<0.90) {p:.4f}")
    h = holm(ps)
    out[f"a1|{sc}"] = {"n_ge_090": sum(x >= 0.90 for x in covs), "holm_below": sum(h), "min_cov": min(covs)}
    md.append(f"- {sc}: cells cov >= 0.90: {sum(x >= 0.90 for x in covs)}/9; significantly below 0.90 after Holm: {sum(h)}/9; "
              f"uncorrected p<0.025: {sum(p < 0.025 for p in ps)}/9")
    md += lines

(RES / "ext_verify2_v51").mkdir(parents=True, exist_ok=True)
(RES / "ext_verify2_v51" / "recompute.json").write_text(json.dumps(out, indent=1, default=str))
(RES / "ext_verify2_v51" / "recompute.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
