"""Pre-registered rule of r5ngorient3 (docs/ext/r5ngorient3.md, section 4): NG-A v3 (component A of
tolerant_v5_2) alone, ``tolerant_ngA3`` vs ``tolerant_v5_1`` at v5_1's frozen factors.

Inputs: results/ext_r5ngorient3_v0/v0.json; results/ext_r5ngorient3_{ngmix,gauss}/ (runs.jsonl, pairs.npz,
diag.jsonl). Writes results/ext_r5ngorient3_analysis/{ruling.md, ruling.json}. If V0 failed, only V0 is
reported and the verdict is "dropped" (no bank run exists).

Statistics (helpers imported from experiments/ext/r4ngorient/analyze.py, unchanged): run IS = mean interval
score over non-null pairs; paired over runs where both methods are ok; cluster bootstrap by topology,
B = 20000, seed 20261104, percentile; one-sided p = share of resamples on the H0 side (floor 1/B); Holm.
A cell counts as a win or a significant loss only with >= 8 topology clusters among its paired runs.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("r4_analyze", ROOT / "experiments/ext/r4ngorient/analyze.py")
_r4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r4)          # r4ngorient analyzer, unchanged: only its helpers are used
B, OCAL, Boot, auroc, ci, holm, load_runs, p_side = (_r4.B, _r4.OCAL, _r4.Boot, _r4.auroc, _r4.ci, _r4.holm,
                                                       _r4.load_runs, _r4.p_side)

OUT = ROOT / "results" / "ext_r5ngorient3_analysis"
ARM, REF, V2 = "tolerant_ngA3", "tolerant_v5_1", "tolerant_ngA"
SHORT = {ARM: "NG-A v3", REF: "v5_1", V2: "NG-A v2", "oracle": "oracle"}
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
PRIMARY = [(T, k, r) for T in (80, 150) for k in ("missing", "reversed") for r in (0.2, 0.5)]
MIN_CLUSTERS = 8


def paired(idx, arm, ref, T, kind, rate):
    keys = sorted({(k[0], k[1]) for k in idx if k[2] == T and k[3] == kind and k[4] == rate and k[5] == ref})
    topo, ia, ir = [], [], []
    fail = {arm: 0, ref: 0}
    cov = {arm: [0, 0], ref: [0, 0]}
    ident = 0
    for tp, rp in keys:
        ra, rr = idx.get((tp, rp, T, kind, rate, arm)), idx.get((tp, rp, T, kind, rate, ref))
        for m, r in ((arm, ra), (ref, rr)):
            if r is None or r["status"] != "ok":
                fail[m] += 1
            else:
                cov[m][0] += r["n_covered_nonnull"]
                cov[m][1] += r["n_nonnull"]
        if ra and rr and ra["status"] == "ok" and rr["status"] == "ok" and ra.get("iscore_nonnull_mean") is not None \
                and rr.get("iscore_nonnull_mean") is not None:
            topo.append(tp)
            ia.append(ra["iscore_nonnull_mean"])
            ir.append(rr["iscore_nonnull_mean"])
            ident += int(ra["iscore_nonnull_mean"] == rr["iscore_nonnull_mean"])
    return {"T": T, "kind": kind, "rate": rate, "arm": arm, "ref": ref, "n_runs": len(keys), "n_paired": len(ia),
            "n_clusters": len(set(topo)), "fail_arm": fail[arm], "fail_ref": fail[ref],
            "cov_arm": cov[arm][0] / cov[arm][1] if cov[arm][1] else float("nan"),
            "cov_ref": cov[ref][0] / cov[ref][1] if cov[ref][1] else float("nan"),
            "topo": np.array(topo), "ia": np.array(ia), "ir": np.array(ir),
            "share_identical": ident / len(ia) if ia else float("nan")}


def compare(c, boot):
    d = c["ia"] - c["ir"]
    est, reps = boot.ratio(c["topo"], d)
    rel, rreps = boot.ratio(c["topo"], d, c["ir"])
    c.update({"is_arm": float(c["ia"].mean()), "is_ref": float(c["ir"].mean()),
              "ratio": float(c["ia"].mean() / c["ir"].mean()), "d": float(est), "ci": ci(reps),
              "p_better": p_side(reps, True), "p_worse": p_side(reps, False), "rel": float(rel), "rel_reps": rreps})
    return c


def fmt(c, extra=""):
    return (f"| {c['T']} | {c['kind']}-{c['rate']} | {c['n_paired']}/{c['n_runs']} | {c['n_clusters']} | "
            f"{c['fail_arm']}/{c['fail_ref']} | {c['cov_arm']:.3f} | {c['cov_ref']:.3f} | {c['is_arm']:.3f} | "
            f"{c['is_ref']:.3f} | {c['ratio']:.3f} | {c['d']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] | "
            f"{c['share_identical']:.2f} |{extra}")


HDR = ("| T | cell | paired/runs | cluster | fail arm/ref | cov arm | cov ref | IS arm | IS ref | ratio | dIS [95% CI] | "
       "share identical |")


def pooled(cells):
    """Mean over cells of dIS/IS_ref; bootstrap reps aligned (same topology resamples in every cell)."""
    point = float(np.mean([c["rel"] for c in cells]))
    reps = np.mean(np.stack([c["rel_reps"] for c in cells]), axis=0)
    r = reps[np.isfinite(reps)]
    return {"point": point, "ci95": ci(reps), "upper95_one_sided": float(np.quantile(r, 0.95)),
            "p_one_sided": float(max(np.mean(r >= 0), 1 / B))}


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if k not in ("topo", "ia", "ir", "rel_reps")}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.generic):
        return o.item()
    return o


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    v0 = json.loads((ROOT / "results/ext_r5ngorient3_v0/v0.json").read_text(encoding="utf-8"))
    res = {"V0": {k: v0[k] for k in ("C1", "C2", "C3", "C4", "C5", "PASS")}}
    ok = lambda f: "ĐẠT" if f else "KHÔNG ĐẠT"  # noqa: E731
    L = ["# r5ngorient3: kết quả theo rule ghi trước (sinh bởi experiments/ext/r5ngorient3/analyze.py)", "",
         "## V0 (unit test, chép từ results/ext_r5ngorient3_v0/v0.json)", "",
         f"- C1 = {v0['C1']['value']:.4f} -> {ok(v0['C1']['pass'])}",
         f"- C2 cặp tệ nhất {v0['C2']['worst_pair']} = {v0['C2']['worst_wrong_cond']:.4f}, vượt {v0['C2']['n_over']}/25 -> {ok(v0['C2']['pass'])}",
         f"- C3 m400 {v0['C3']['m400']:.4f} vs m148 {v0['C3']['m148']:.4f} -> {ok(v0['C3']['pass'])}",
         f"- C4 -> {ok(v0['C4']['pass'])}; C5 max |Δp| {v0['C5']['max_abs_dp']:.2e}, gate lệch {v0['C5']['gate_mismatches']} -> {ok(v0['C5']['pass'])}",
         f"- **V0: {'PASS' if v0['PASS'] else 'FAIL'}**", ""]
    runs = {s: load_runs(f"ext_r5ngorient3_{s}") for s in ("ngmix", "gauss")}
    if not v0["PASS"] or runs["ngmix"] is None or runs["gauss"] is None:
        verdict = "DROPPED (V0 FAIL)" if not v0["PASS"] else "INCOMPLETE (thiếu run)"
        res["verdict"] = verdict
        L += [f"**Verdict thành phần A: {verdict}.**"]
        (OUT / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        (OUT / "ruling.json").write_text(json.dumps(clean(res), indent=1), encoding="utf-8")
        print("\n".join(L))
        return
    seed_base = {s: json.loads((ROOT / f"results/ext_r5ngorient3_{s}/manifest.json").read_text())["config"]["seed_base"]
                 for s in runs}
    topos = sorted({k[0] for k in runs["gauss"]})
    boot = Boot(topos)
    L.insert(1, f"D-07 development, seed_base {seed_base}, 20 topology × 3 replicate. Cluster bootstrap theo topology, "
                f"B = {B}, seed 20261104. dIS = arm − v5_1 (âm = arm tốt hơn). Một cell chỉ tính là win/thua có ý nghĩa "
                f"khi có ≥ {MIN_CLUSTERS} cluster.")
    L.insert(2, "")

    # ------------------------------------------------------------- V1 identity
    def load_pairs(s):
        z = np.load(ROOT / f"results/ext_r5ngorient3_{s}/pairs.npz")
        meth = [str(m) for m in z["methods"]]
        cells = [str(c) for c in z["cells"]]
        df = pd.DataFrame({k: z[k] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi",
                                             "dC", "fac")})
        df["mname"] = [meth[int(m)] for m in df.method]
        df["cname"] = [cells[int(c)] for c in df.cell]
        return df

    KEY = ["topo", "rep", "T", "cell", "j", "i"]
    pairs = {s: load_pairs(s) for s in runs}
    diag = {s: [json.loads(l) for l in open(ROOT / f"results/ext_r5ngorient3_{s}/diag.jsonl", encoding="utf-8")]
            for s in runs}
    v1 = {"none_extra": [0, 0], "no_gate": [0, 0], "factor_equal": [0, 0], "mismatch": []}
    bank_order = {s: [t["id"] for t in json.loads((ROOT / f"results/ext_r5ngorient3_{s}/manifest.json").read_text())["topologies"]]
                  for s in runs}
    for s in runs:
        for key, ra in runs[s].items():
            if key[5] != ARM or ra["status"] != "ok":
                continue
            rr = runs[s].get((*key[:5], REF))
            if rr is None or rr["status"] != "ok":
                continue
            v1["factor_equal"][0] += 1
            v1["factor_equal"][1] += int(ra.get("info_c_T") == rr.get("info_c_T"))

    def run_identical(s, tp, rp, T, kind, rate):
        ra = runs[s].get((tp, rp, T, kind, rate, ARM))
        rr = runs[s].get((tp, rp, T, kind, rate, REF))
        if ra is None or rr is None or ra["status"] != rr["status"]:
            return False
        if ra["status"] != "ok":
            return True
        if ra["iscore_nonnull_mean"] != rr["iscore_nonnull_mean"] or ra["n_covered_nonnull"] != rr["n_covered_nonnull"]:
            return False
        return True

    for s in runs:
        df = pairs[s]
        ti = {t: i for i, t in enumerate(bank_order[s])}
        a = df[df.mname == ARM].set_index(KEY)[["lo", "hi", "C_e"]]
        r = df[df.mname == REF].set_index(KEY)[["lo", "hi", "C_e"]]
        both = a.join(r, lsuffix="_a", rsuffix="_r", how="inner")
        both["same"] = (both.lo_a == both.lo_r) & (both.hi_a == both.hi_r) & (both.C_e_a == both.C_e_r)
        same_run = both.groupby(level=["topo", "rep", "T", "cell"]).same.all()
        cell_names = [f"{k}|{rt}" for k, rt in CELLS]
        for key in {(k[0], k[1], k[2], k[3], k[4]) for k in runs[s] if k[5] == REF}:
            tp, rp, T, kind, rate = key
            if kind in ("none", "extra"):
                c_idx = cell_names.index(f"{kind}|{rate}")
                okr = run_identical(s, tp, rp, T, kind, rate) and bool(same_run.get((ti[tp], rp, T, c_idx), True))
                v1["none_extra"][0] += 1
                v1["none_extra"][1] += int(okr)
                if not okr:
                    v1["mismatch"].append([s, tp, rp, T, kind, rate])
        for d in diag[s]:
            if d["method"] != ARM or d["kind"] in ("none", "extra"):
                continue
            no_gate = d["n_gate_draws"][1] == 0 and not any(c["gate"] for c in d["cands"]) and \
                not any(p["gate"] for p in d["pool"])
            if no_gate:
                c_idx = cell_names.index(f"{d['kind']}|{d['rate']}")
                okr = run_identical(s, d["topology"], d["replicate"], d["T"], d["kind"], d["rate"]) and \
                    bool(same_run.get((ti[d["topology"]], d["replicate"], d["T"], c_idx), True))
                v1["no_gate"][0] += 1
                v1["no_gate"][1] += int(okr)
                if not okr:
                    v1["mismatch"].append([s, d["topology"], d["replicate"], d["T"], d["kind"], d["rate"], "no_gate"])
    v1_pass = (v1["none_extra"][0] == v1["none_extra"][1] and v1["no_gate"][0] == v1["no_gate"][1]
               and v1["factor_equal"][0] == v1["factor_equal"][1])
    res["V1"] = {**v1, "PASS": bool(v1_pass)}
    L += ["## V1 (identity)", "",
          f"- Cell none/extra (2 shock × 3 T × 3 cell): {v1['none_extra'][1]}/{v1['none_extra'][0]} run trùng v5_1 từng bit "
          "(status, IS, số cặp phủ, lo/hi/C của mọi cặp non-null)",
          f"- Run missing/reversed không có gate nào mở (mức dữ liệu và mọi draw): {v1['no_gate'][1]}/{v1['no_gate'][0]} trùng v5_1",
          f"- Width factor của NG-A v3 bằng factor frozen của v5_1 ở {v1['factor_equal'][1]}/{v1['factor_equal'][0]} run ghép cặp",
          f"- **V1: {'PASS' if v1_pass else 'FAIL'}**", ""]

    # ------------------------------------------------------------- P1
    def block(arm, ref, idx, cells):
        return [compare(paired(idx, arm, ref, T, k, r), boot) for T, k, r in cells]

    prim = block(ARM, REF, runs["ngmix"], PRIMARY)
    P = pooled(prim)
    for c, p in zip(prim, holm([c["p_better"] for c in prim])):
        c["p_holm8"] = float(p)
        c["win"] = bool(p < 0.05 and c["cov_arm"] >= 0.90 and c["fail_arm"] <= c["fail_ref"] + 1
                        and c["n_clusters"] >= MIN_CLUSTERS)
    cov_ok = all(c["cov_arm"] >= 0.90 for c in prim)
    fail_ok = all(c["fail_arm"] <= c["fail_ref"] + 1 for c in prim)
    p1_pass = bool(P["upper95_one_sided"] < 0 and cov_ok and fail_ok)
    res["P1"] = {"pooled": P, "cov_all_primary": cov_ok, "fail_guard": fail_ok, "PASS": p1_pass,
                 "cells": prim, "wins_holm8": sum(c["win"] for c in prim)}
    L += ["## P1: 8 cell primary ng_mix, endpoint gộp", "",
          f"- Endpoint gộp = trung bình qua 8 cell của dIS/IS_v51 = {P['point']:+.4f} "
          f"[95% CI {P['ci95'][0]:+.4f}, {P['ci95'][1]:+.4f}]; cận trên 95% một phía = {P['upper95_one_sided']:+.4f}; "
          f"p một phía (H0 ≥ 0) = {P['p_one_sided']:.4f} -> {ok(P['upper95_one_sided'] < 0)}",
          f"- Coverage NG-A v3 ≥ 0.90 ở cả 8 cell: {ok(cov_ok)}; failure arm ≤ v5_1 + 1 ở cả 8 cell: {ok(fail_ok)}",
          f"- **P1: {'PASS' if p1_pass else 'FAIL'}**", "",
          "Phụ (báo, không quyết định): win theo Holm 8 từng cell.", "",
          HDR + " dIS/IS_v51 | p một phía | p Holm (8) | WIN |", "|" + "---|" * 16]
    for c in prim:
        L.append(fmt(c, f" {c['rel']:+.4f} | {c['p_better']:.4f} | {c['p_holm8']:.4f} | {'WIN' if c['win'] else '-'} |"))
    L += ["", f"Win Holm 8: {res['P1']['wins_holm8']}/8.", ""]

    # ------------------------------------------------------------- no-harm (a), (b)
    gauss = block(ARM, REF, runs["gauss"], [(T, k, r) for T in (40, 80, 150) for k, r in CELLS])
    for c, p in zip(gauss, holm([c["p_worse"] for c in gauss])):
        c["p_worse_holm21"] = float(p)
        c["worse_sig"] = bool(p < 0.05 and c["n_clusters"] >= MIN_CLUSTERS)
        c["ok_a"] = bool(c["ratio"] <= 1.03 and not c["worse_sig"] and (c["cov_ref"] < 0.90 or c["cov_arm"] >= 0.90))
    nh_a = all(c["ok_a"] for c in gauss)
    other = block(ARM, REF, runs["ngmix"], [(T, k, r) for T in (40, 80, 150) for k, r in CELLS if (T, k, r) not in PRIMARY])
    for c in other:
        c["ok_b"] = bool(c["ratio"] <= 1.05 and (c["cov_ref"] < 0.90 or c["cov_arm"] >= 0.90))
    nh_b = all(c["ok_b"] for c in other)
    res["no_harm_a"] = {"PASS": nh_a, "cells": gauss}
    res["no_harm_b"] = {"PASS": nh_b, "cells": other}
    L += ["## No-harm (a): lưới Gaussian G, 21 cell (Holm 21, H0 dIS ≤ 0)", "",
          HDR + " p tệ hơn | p Holm (21) | đạt |", "|" + "---|" * 15]
    for c in gauss:
        L.append(fmt(c, f" {c['p_worse']:.4f} | {c['p_worse_holm21']:.4f} | {'đạt' if c['ok_a'] else 'KHÔNG'} |"))
    L += ["", f"**No-harm (a): {ok(nh_a)}** (IS ratio ≤ 1.03, không tệ hơn sau Holm 21, coverage ≥ 0.90 nơi v5_1 đạt).", "",
          "## No-harm (b): 13 cell ng_mix không primary", "", HDR + " p tốt hơn (mô tả) | đạt |", "|" + "---|" * 14]
    for c in other:
        L.append(fmt(c, f" {c['p_better']:.4f} | {'đạt' if c['ok_b'] else 'KHÔNG'} |"))
    L += ["", f"**No-harm (b): {ok(nh_b)}** (IS ratio ≤ 1.05, coverage ≥ 0.90 nơi v5_1 đạt).", ""]

    retained = bool(v0["PASS"] and v1_pass and p1_pass and nh_a and nh_b)
    verdict = "RETAINED (thành phần A, exploratory)" if retained else "NOT RETAINED (bỏ thành phần A khỏi tolerant_v5_2)"
    res["verdict"] = verdict
    L += [f"## Verdict thành phần A (v5_1 + NG-A v3)", "",
          f"V0 {ok(v0['PASS'])}; V1 {ok(v1_pass)}; P1 {ok(p1_pass)}; no-harm (a) {ok(nh_a)}; no-harm (b) {ok(nh_b)} -> "
          f"**{verdict}**.", ""]

    # ------------------------------------------------------------- secondary: affected-pair coverage
    W_ = {}
    for s in runs:
        df = pairs[s]
        base = df[df.mname == "oracle"][KEY + ["cname", "C_t", "dC"]].copy()
        for m in ("oracle", REF, ARM, V2):
            s_ = df[df.mname == m][KEY + ["C_e", "lo", "hi"]].rename(
                columns={"C_e": f"C_{m}", "lo": f"lo_{m}", "hi": f"hi_{m}"})
            base = base.merge(s_, on=KEY)
        mid, half = (base.lo_oracle + base.hi_oracle) / 2, (base.hi_oracle - base.lo_oracle) / 2
        cc = base["T"].map(OCAL)
        base["cov_ocal"] = ((mid - cc * half <= base.C_t) & (base.C_t <= mid + cc * half)).astype(float)
        for m in (REF, ARM, V2):
            base[f"cov_{m}"] = ((base[f"lo_{m}"] <= base.C_t) & (base.C_t <= base[f"hi_{m}"])).astype(float)
            base[f"w_{m}"] = base[f"hi_{m}"] - base[f"lo_{m}"]
        W_[s] = base
    sec = []
    L += ["## Phụ: coverage trên cặp affected (dC ≥ 0.05), arm − v5_1", "",
          "Holm 4 chỉ cho NG-A v3 ở 4 cell reversed T80/150 ng_mix (H0 Δ ≤ 0). Các dòng khác mô tả.", "",
          "| shock | arm | cell | T | n aff | cov v5_1 | cov arm | cov oracle_cal | Δ [CI] | p một phía | p Holm (4) | closed share | median width v5_1 / arm |",
          "|" + "---|" * 13]
    for s in ("ngmix", "gauss"):
        Wd = W_[s]
        for arm in (ARM, V2):
            rows_s = []
            for cname in ("reversed|0.2", "reversed|0.5", "missing|0.2", "missing|0.5"):
                for T in (80, 150):
                    sub = Wd[(Wd.cname == cname) & (Wd["T"] == T) & (Wd.dC >= 0.05)]
                    if not len(sub):
                        continue
                    tp = np.array([bank_order[s][int(t)] for t in sub.topo])
                    d, rd = boot.ratio(tp, (sub[f"cov_{arm}"] - sub[f"cov_{REF}"]).values)
                    g0, _ = boot.ratio(tp, (sub.cov_ocal - sub[f"cov_{REF}"]).values)
                    rows_s.append({"shock": s, "arm": arm, "cell": cname, "T": T, "n": int(len(sub)),
                                   "cov_ref": float(sub[f"cov_{REF}"].mean()), "cov_arm": float(sub[f"cov_{arm}"].mean()),
                                   "cov_ocal": float(sub.cov_ocal.mean()), "d": float(d), "ci": ci(rd),
                                   "p": p_side(rd, False), "share": float(d / g0) if g0 else float("nan"),
                                   "width": [float(sub[f"w_{REF}"].median()), float(sub[f"w_{arm}"].median())],
                                   "registered": s == "ngmix" and arm == ARM and cname.startswith("reversed")})
            regs = [r for r in rows_s if r["registered"]]
            for r, p in zip(regs, holm([r["p"] for r in regs])):
                r["p_holm4"] = float(p)
            for r in rows_s:
                ph = f"{r['p_holm4']:.4f}" if "p_holm4" in r else "-"
                L.append(f"| {s} | {SHORT[arm]} | {r['cell']} | {r['T']} | {r['n']} | {r['cov_ref']:.3f} | {r['cov_arm']:.3f} | "
                         f"{r['cov_ocal']:.3f} | {r['d']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p']:.4f} | {ph} | "
                         f"{r['share']:.2f} | {r['width'][0]:.3f} / {r['width'][1]:.3f} |")
            sec += rows_s
    res["affected"] = sec
    L.append("")

    # ------------------------------------------------------------- descriptive: v2 on the same data, v3 vs v2
    prim2 = block(V2, REF, runs["ngmix"], PRIMARY)
    P2 = pooled(prim2)
    p32 = block(ARM, V2, runs["ngmix"], PRIMARY)
    P32 = pooled(p32)
    g2 = block(V2, REF, runs["gauss"], [(T, k, r) for T in (40, 80, 150) for k, r in CELLS])
    res["descriptive"] = {"v2_pooled": P2, "v2_cells": prim2, "v3_vs_v2_pooled": P32, "v3_vs_v2_cells": p32,
                          "v2_gauss": g2}
    L += ["## Mô tả: NG-A v2 (`tolerant_ngA`) trên cùng dữ liệu, và v3 so với v2 (không quyết định)", "",
          f"- v2 − v5_1, endpoint gộp 8 cell: {P2['point']:+.4f} [{P2['ci95'][0]:+.4f}, {P2['ci95'][1]:+.4f}], "
          f"cận trên một phía {P2['upper95_one_sided']:+.4f}",
          f"- v3 − v2, endpoint gộp (chia cho IS v2): {P32['point']:+.4f} [{P32['ci95'][0]:+.4f}, {P32['ci95'][1]:+.4f}], "
          f"cận trên một phía {P32['upper95_one_sided']:+.4f}", "",
          HDR + " dIS/IS_ref | so sánh |", "|" + "---|" * 14]
    for c in prim2:
        L.append(fmt(c, f" {c['rel']:+.4f} | v2 − v5_1 |"))
    for c in p32:
        L.append(fmt(c, f" {c['rel']:+.4f} | v3 − v2 |"))
    L += ["", "Gaussian G, v2 − v5_1 (mô tả):", "", HDR + " dIS/IS_ref |", "|" + "---|" * 13]
    for c in g2:
        L.append(fmt(c, f" {c['rel']:+.4f} |"))
    L.append("")

    # ------------------------------------------------------------- diagnostics: gates, directions, AUROC, runtime
    g_open = defaultdict(lambda: [0, 0])
    for s, recs in diag.items():
        for r in recs:
            for key in ((s, r["method"], "all"), (s, r["method"], r["T"])):
                g_open[key][0] += r["n_gate_draws"][0]
                g_open[key][1] += r["n_gate_draws"][1]
    L += ["## Diagnostic (mô tả)", "", "### Tỷ lệ gate mở theo draw", "", "| shock | method | T | mở / đánh giá | tỷ lệ |",
          "|---|---|---|---|---|"]
    gt = []
    for key in sorted(g_open, key=str):
        s, m, T = key
        n0, n1 = g_open[key]
        if n0:
            gt.append({"shock": s, "method": m, "T": T, "n": n0, "open": n1, "rate": n1 / n0})
            L.append(f"| {s} | {SHORT.get(m, m)} | {T} | {n1}/{n0} | {n1 / n0:.3f} |")
    res["diag_gate"] = gt
    L += ["", "### Cạnh cùng kỳ thật bị xoá, được repair: chiều đúng (mức dữ liệu và mức draw)", "",
          "| shock | method | T | n candidate thật | gate mở | p đúng chiều > 0.5 | n draw | draw đúng chiều |",
          "|---|---|---|---|---|---|---|---|"]
    ctab = []
    for s, recs in diag.items():
        for m in (ARM, V2):
            for T in (40, 80, 150):
                rr = [r for r in recs if r["method"] == m and r["T"] == T and r["kind"] == "missing"]
                cands = [c for r in rr for c in r["cands"] if c["damaged_missing"] and c["true_contemp"]]
                tal = [c for r in rr for c in r["cand_tally"] if c["damaged_missing"] and c["true_contemp"]]
                if not rr:
                    continue
                good = [((c["pA"] > 0.5) if c["true_uv"] else (c["pA"] < 0.5)) for c in cands]
                nd = sum(c["n"] for c in tal)
                ndc = sum((c["n_uv"] if c["true_uv"] else c["n"] - c["n_uv"]) for c in tal)
                row = {"shock": s, "method": m, "T": T, "n_cand": len(cands),
                       "gate_open": float(np.mean([c["gate"] for c in cands])) if cands else None,
                       "p_correct": float(np.mean(good)) if good else None, "n_draw": nd,
                       "draw_correct": ndc / nd if nd else None}
                ctab.append(row)
                f = lambda v: "-" if v is None else f"{v:.3f}"  # noqa: E731
                L.append(f"| {s} | {SHORT[m]} | {T} | {len(cands)} | {f(row['gate_open'])} | {f(row['p_correct'])} | {nd} | "
                         f"{f(row['draw_correct'])} |")
    res["diag_cand"] = ctab
    L += ["", "### Cạnh pool thật sự bị đảo: AUROC của xác suất bị đảo 1 − p (mức dữ liệu), tần suất lật theo draw", "",
          "| shock | method | T | n pool (đảo / không) | AUROC | gate mở | lật/draw: đảo / không |", "|---|---|---|---|---|---|---|"]
    ptab = []
    for s, recs in diag.items():
        for m in (ARM, V2):
            for T in (40, 80, 150):
                ra = [r for r in recs if r["method"] == m and r["T"] == T and r["kind"] == "reversed"]
                if not ra:
                    continue
                pa = [p for r in ra for p in r["pool"]]
                pos = [1 - p["pA"] for p in pa if p["reversed"]]
                neg = [1 - p["pA"] for p in pa if not p["reversed"]]

                def flips(rev):
                    t = [c for r in ra for c in r["pool_tally"] if c["reversed"] == rev]
                    n = sum(c["n"] for c in t)
                    return sum(c["n_flip"] for c in t) / n if n else None
                row = {"shock": s, "method": m, "T": T, "n_rev": len(pos), "n_not": len(neg), "auroc": auroc(pos, neg),
                       "gate_open": float(np.mean([p["gate"] for p in pa])) if pa else None,
                       "flip": [flips(True), flips(False)]}
                ptab.append(row)
                f = lambda v: "-" if v is None else f"{v:.3f}"  # noqa: E731
                L.append(f"| {s} | {SHORT[m]} | {T} | {row['n_rev']} / {row['n_not']} | {f(row['auroc'])} | "
                         f"{f(row['gate_open'])} | {f(row['flip'][0])} / {f(row['flip'][1])} |")
    res["diag_pool"] = ptab
    L += ["", "### Thời gian theo method (giây, tổng trong method)", "", "| shock | method | giây | run |", "|---|---|---|---|"]
    rt = []
    for s, idx in runs.items():
        acc = defaultdict(lambda: [0.0, 0])
        for key, rw in idx.items():
            if rw.get("info_seconds") is not None:
                acc[key[5]][0] += rw["info_seconds"]
                acc[key[5]][1] += 1
        for m, (sec_, n_) in sorted(acc.items()):
            rt.append({"shock": s, "method": m, "seconds": sec_, "runs": n_})
            L.append(f"| {s} | {SHORT.get(m, m)} | {sec_:.0f} | {n_} |")
    res["runtime"] = rt
    (OUT / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "ruling.json").write_text(json.dumps(clean(res), indent=1, default=str), encoding="utf-8")
    print("\n".join(L[:40]))
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
