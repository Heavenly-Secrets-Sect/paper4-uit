"""Pre-registered rule of r5v52 (docs/ext/r5v52.md, section 4): ``tolerant_v5_2`` vs ``tolerant_v5_1`` and the final
round-5 verdict of docs/ext/synthesis_round4.md section 4.2.

Inputs: results/ext_r5v52_{ngmix,gauss,p2,latent1,noise01}/ (runs.jsonl, pairs.npz, manifest.json);
results/ext_r5ngorient3_v0/v0.json (V0 of component A); for the composition check V-comp and the single-component
branches: results/ext_r5ngorient3_{ngmix,gauss}/runs.jsonl, results/ext_r5ngorient3_analysis/ruling.json,
results/ext_r5hubscreen2_{p2,g}/runs.jsonl, results/ext_r5hubscreen2_ruling/ruling.json.
Writes results/ext_r5v52_analysis/{ruling.md, ruling.json} (--prefix smoke_ -> results/ext_r5v52_smoke_analysis).

Statistics are the components' own, imported unchanged:
- P1, no-harm (a), (b), (c): experiments/ext/r5ngorient3/analyze.py (paired, compare, pooled) on top of
  experiments/ext/r4ngorient/analyze.py (Boot: topology-cluster bootstrap B = 20000, seed 20261104; holm; p_side);
- P2: experiments/ext/r5hubscreen2/analyze.py (stats, paired, boot_ratio seed 20261106 + i, holm).
A cell counts as a win or a significant loss only with >= 8 topology clusters.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
sys.path.insert(0, str(ROOT / "src"))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load("r5ngorient3_analyze", "experiments/ext/r5ngorient3/analyze.py")   # unchanged; helpers only
Bm = _load("r5hubscreen2_analyze", "experiments/ext/r5hubscreen2/analyze.py")  # unchanged; helpers only

ARM, REF, PHS = "tolerant_v5_2", "tolerant_v5_1", "plugin_hs_cal"
CELLS = A.CELLS
PRIMARY = A.PRIMARY
G = [(T, k, r) for T in (40, 80, 150) for k, r in CELLS]
NONPRIM = [(T, k, r) for T in (40, 80, 150) for k, r in CELLS if (T, k, r) not in PRIMARY]
C8 = [(T, k, 0.2) for T in (80, 150) for k in ("missing", "reversed")]
P2 = Bm.P2
P2C = Bm.P2C
MIN_CLUSTERS = 8
CELL_IDX = {f"{k}|{r}": i for i, (k, r) in enumerate(CELLS)}       # c_idx of the runner layout
RUNSETS = ("ngmix", "gauss", "p2", "latent1", "noise01")


def ok(f):
    return "ĐẠT" if f else "KHÔNG ĐẠT"


def rows_of(name):
    p = RES / name / "runs.jsonl"
    return [json.loads(l) for l in open(p, encoding="utf-8")] if p.exists() else None


def rkey(r):
    return (r["topology"], r["replicate"], r["T"], r["kind"], float(r["rate"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="")
    a = ap.parse_args()
    pre = a.prefix
    out = RES / f"ext_r5v52_{pre}analysis"
    out.mkdir(parents=True, exist_ok=True)
    smoke = bool(pre)
    J, L = {}, ["# r5v52: kết quả theo rule ghi trước (sinh bởi experiments/ext/r5v52/analyze.py)", ""]
    if smoke:
        L += ["**SMOKE: chỉ kiểm pipeline (D-07H, 2 topology, n_boot 19). Không phải evaluation.**", ""]
    rows = {s: rows_of(f"ext_r5v52_{pre}{s}") for s in RUNSETS}
    idx = {s: A.load_runs(f"ext_r5v52_{pre}{s}") for s in RUNSETS}
    missing = [s for s in RUNSETS if rows[s] is None]
    if missing:
        raise SystemExit(f"missing run sets {missing}")
    man = {s: json.loads((RES / f"ext_r5v52_{pre}{s}" / "manifest.json").read_text(encoding="utf-8")) for s in RUNSETS}
    L += [f"Dữ liệu: {man['gauss']['config']['bank']} {man['gauss']['config']['split']}, seed_base "
          f"{man['gauss']['config']['seed_base']} (+ unit_offset {man['gauss']['config'].get('unit_offset', 0)}). "
          "dIS = v5_2 − v5_1 (âm = v5_2 tốt hơn). Cluster bootstrap theo topology, B = 20000.", ""]

    # ------------------------------------------------------------------ V0 (component A)
    v0 = json.loads((RES / "ext_r5ngorient3_v0/v0.json").read_text(encoding="utf-8"))
    v0_pass = bool(v0["PASS"])
    J["V0"] = {"PASS": v0_pass, "source": "results/ext_r5ngorient3_v0/v0.json"}
    L += ["## V0 (unit test của thành phần A, chép từ results/ext_r5ngorient3_v0/v0.json)", "",
          f"- **V0: {'PASS' if v0_pass else 'FAIL'}** (C1 {v0['C1']['value']:.4f}; C2 cặp tệ nhất {v0['C2']['worst_wrong_cond']:.4f}; "
          f"C3 {v0['C3']['m400']:.4f} ≤ {v0['C3']['m148']:.4f}; C4 {ok(v0['C4']['pass'])}; C5 {ok(v0['C5']['pass'])})", ""]

    # ------------------------------------------------------------------ V1 identity with v5_1
    allr = [(s, r) for s in RUNSETS for r in rows[s]]
    arm = [(s, r) for s, r in allr if r["method"] == ARM]
    ref = {(s, *rkey(r)): r for s, r in allr if r["method"] == REF}
    noRed = lambda r: (r.get("hs_reduced") or 0) == 0 and (r.get("hs_ev_reduced") or 0) == 0  # noqa: E731

    def ident(s, r):
        rr = ref.get((s, *rkey(r)))
        if rr is None or r["v52_status"] != r["v51_status"]:
            return False
        if r["v52_status"] != "ok":
            return True
        if rr.get("fac") is None:      # f_v51 missing at this key: v5_2 uses f_red by B's rule; compare raw only
            return bool(r["raw_ident_v51"])
        return bool(r["raw_ident_v51"] and r["iscore_nonnull_mean"] == rr["iscore_nonnull_mean"]
                    and r["n_covered_nonnull"] == rr["n_covered_nonnull"] and r["fac"] == rr["fac"])

    ne = [(s, r) for s, r in arm if r["kind"] in ("none", "extra") and noRed(r)]
    ng = [(s, r) for s, r in arm if r["kind"] in ("missing", "reversed") and noRed(r) and r["no_gate"]]
    ne_ok = sum(ident(s, r) for s, r in ne)
    ng_ok = sum(ident(s, r) for s, r in ng)
    fe = [(s, r) for s, r in arm if (r.get("hs_reduced") or 0) == 0 and r["status"] == "ok"
          and ref.get((s, *rkey(r))) is not None and ref[(s, *rkey(r))]["status"] == "ok"
          and ref[(s, *rkey(r))].get("fac") is not None]
    fe_ok = sum(r["fac"] == ref[(s, *rkey(r))]["fac"] for s, r in fe)
    lag0 = sum(int(r.get("hs_contemp_dropped") or 0) for _, r in arm)
    v1_pass = bool(ne_ok == len(ne) and ng_ok == len(ng) and fe_ok == len(fe) and lag0 == 0)
    v51ok = [(s, r) for s, r in arm if r["v51_status"] == "ok"]
    ch = [(s, r) for s, r in v51ok if not r["raw_ident_v51"]]
    ch_red = [(s, r) for s, r in ch if (r.get("hs_reduced") or 0) == 1]
    ch_red_data = sum(1 for _, r in ch_red if (r.get("hs_eq_data") or 0) > 0)
    ch_gate_only = [(s, r) for s, r in ch if (r.get("hs_reduced") or 0) == 0]
    ev_red = sum(1 for _, r in arm if (r.get("hs_ev_reduced") or 0) == 1)
    ev_fail = sum(int(r.get("hs_ev_fit_fail") or 0) for _, r in arm)
    J["V1"] = {"PASS": v1_pass, "none_extra": [len(ne), ne_ok], "no_gate_no_red": [len(ng), ng_ok],
               "factor_equal": [len(fe), fe_ok], "lag0_dropped": lag0, "v51_ok_runs": len(v51ok),
               "v51_ok_changed": len(ch), "changed_by_reduction": len(ch_red), "changed_by_reduction_data_level": ch_red_data,
               "changed_by_reduction_draw_only": len(ch_red) - ch_red_data, "changed_without_reduction": len(ch_gate_only),
               "runs_with_evidence_only_reduction": ev_red, "evidence_only_fit_fail": ev_fail,
               "by_runset": {s: {"arm_rows": sum(1 for x, _ in arm if x == s),
                                 "reduced": sum(1 for x, r in arm if x == s and (r.get("hs_reduced") or 0) == 1),
                                 "gate_open_runs": sum(1 for x, r in arm if x == s and not r["no_gate"]),
                                 "both_active": sum(1 for x, r in arm if x == s and not r["no_gate"]
                                                    and (r.get("hs_reduced") or 0) == 1)} for s in RUNSETS}}
    L += ["## V1 (identity với v5_1)", "",
          f"- Run none/extra không rút gọn (5 bộ run): {ne_ok}/{len(ne)} trùng v5_1 (status, C/lo/hi raw từng bit, IS, số cặp phủ, factor)",
          f"- Run missing/reversed không gate nào mở (dữ liệu và mọi draw) và không rút gọn: {ng_ok}/{len(ng)} trùng v5_1",
          f"- Factor của v5_2 = factor của v5_1 trên run không rút gọn, cả hai ok: {fe_ok}/{len(fe)}",
          f"- Term lag 0 bị bỏ: {lag0}",
          f"- **V1: {'PASS' if v1_pass else 'FAIL'}**",
          f"- Báo kèm: run v5_1-ok {len(v51ok)}, bị v5_2 đổi {len(ch)}: do rút gọn (B) {len(ch_red)} "
          f"(mức dữ liệu {ch_red_data}, chỉ trong draw {len(ch_red) - ch_red_data}); không rút gọn, do gate (A) {len(ch_gate_only)}. "
          f"Run có rút gọn chỉ ở fit evidence của A: {ev_red} (fit-fail sau rút gọn: {ev_fail}).", "",
          "| bộ run | dòng v5_2 | run rút gọn | run có gate mở | cả hai |", "|---|---|---|---|---|"]
    for s in RUNSETS:
        b = J["V1"]["by_runset"][s]
        L.append(f"| {s} | {b['arm_rows']} | {b['reduced']} | {b['gate_open_runs']} | {b['both_active']} |")
    L.append("")

    # ------------------------------------------------------------------ V-comp: composition vs the components' runs
    def comp(s_mine, comp_name, comp_method, select, extra=(), mine=ARM):
        theirs = rows_of(comp_name)
        if theirs is None:
            return {"n": 0, "same": 0, "absent": None, "mismatch": ["no component run"]}
        tix = {rkey(r): r for r in theirs if r["method"] == comp_method}
        n = same = absent = 0
        mm = []
        for r in rows[s_mine]:
            if r["method"] != mine or not select(r):
                continue
            t = tix.get(rkey(r))
            if t is None:
                absent += 1
                continue
            n += 1
            eq = r["status"] == t["status"] and (r["status"] != "ok" or (
                r["iscore_nonnull_mean"] == t["iscore_nonnull_mean"] and r["n_covered_nonnull"] == t["n_covered_nonnull"]))
            eq = eq and all((r.get(k) or 0) == (t.get(k) or 0) for k in extra)
            same += int(eq)
            if not eq:
                mm.append(list(rkey(r)))
        return {"n": n, "same": same, "absent": absent, "mismatch": mm[:20]}

    if smoke:
        vcomp = {"skipped": "smoke"}
        vcomp_pass = True
        L += ["## V-comp: bỏ qua ở smoke (dữ liệu khác component run)", ""]
    else:
        vcomp = {"A_ngmix": comp("ngmix", "ext_r5ngorient3_ngmix", "tolerant_ngA3", noRed),
                 "A_gauss": comp("gauss", "ext_r5ngorient3_gauss", "tolerant_ngA3", noRed),
                 "B_p2": comp("p2", "ext_r5hubscreen2_p2", "tolerant_v5_1_hs2", lambda r: r["no_gate"], ("hs_reduced",),
                              mine="tolerant_v5_2_fredB"),
                 "B_g": comp("gauss", "ext_r5hubscreen2_g", "tolerant_v5_1_hs2", lambda r: r["no_gate"], ("hs_reduced",),
                             mine="tolerant_v5_2_fredB")}
        vcomp_pass = all(v["n"] > 0 and v["same"] == v["n"] for v in vcomp.values())
        L += ["## V-comp (thành phần ghép đúng: so với run của từng thành phần, cùng dữ liệu)", "",
              "| so sánh | điều kiện chọn run | so được | trùng (status, IS, số cặp phủ) | không có dòng tương ứng |",
              "|---|---|---|---|---|"]
        lab = {"A_ngmix": ("v5_2 vs tolerant_ngA3, ng_mix", "không rút gọn"),
               "A_gauss": ("v5_2 vs tolerant_ngA3, Gaussian G", "không rút gọn"),
               "B_p2": ("v5_2 (nhân f_red của B) vs tolerant_v5_1_hs2, P2", "không gate nào mở (+ cờ hs_reduced bằng nhau)"),
               "B_g": ("v5_2 (nhân f_red của B) vs tolerant_v5_1_hs2, Gaussian G", "không gate nào mở (+ cờ hs_reduced bằng nhau)")}
        for k, v in vcomp.items():
            L.append(f"| {lab[k][0]} | {lab[k][1]} | {v['n']} | {v['same']} | {v['absent']} |")
        L += ["", f"- **V-comp: {'PASS' if vcomp_pass else 'FAIL'}**", ""]
    J["V_comp"] = {"PASS": vcomp_pass, **vcomp}

    # ------------------------------------------------------------------ P1 (component A scenario)
    topos = sorted({k[0] for k in idx["gauss"]})
    boot = A.Boot(topos)
    prim = [A.compare(A.paired(idx["ngmix"], ARM, REF, T, k, r), boot) for T, k, r in PRIMARY]
    P = A.pooled(prim)
    for c, p in zip(prim, A.holm([c["p_better"] for c in prim])):
        c["p_holm8"] = float(p)
        c["win"] = bool(p < 0.05 and c["cov_arm"] >= 0.90 and c["fail_arm"] <= c["fail_ref"] + 1
                        and c["n_clusters"] >= MIN_CLUSTERS)
    cov_ok = all(c["cov_arm"] >= 0.90 for c in prim)
    fail_ok = all(c["fail_arm"] <= c["fail_ref"] + 1 for c in prim)
    p1_pass = bool(P["upper95_one_sided"] < 0 and cov_ok and fail_ok)
    J["P1"] = {"PASS": p1_pass, "pooled": P, "cov_all_primary": cov_ok, "fail_guard": fail_ok, "cells": prim,
               "wins_holm8": int(sum(c["win"] for c in prim))}
    L += ["## P1: 8 cell primary ng_mix, endpoint gộp", "",
          f"- Endpoint gộp (trung bình 8 cell của dIS/IS_v51) = {P['point']:+.4f} [95% CI {P['ci95'][0]:+.4f}, {P['ci95'][1]:+.4f}]; "
          f"cận trên 95% một phía {P['upper95_one_sided']:+.4f}; p một phía {P['p_one_sided']:.4f} -> {ok(P['upper95_one_sided'] < 0)}",
          f"- Coverage v5_2 ≥ 0.90 ở cả 8 cell: {ok(cov_ok)}; failure v5_2 ≤ v5_1 + 1 ở cả 8 cell: {ok(fail_ok)}",
          f"- **P1: {'PASS' if p1_pass else 'FAIL'}**", "", "Phụ: win theo Holm 8 (≥ 8 cluster).", "",
          A.HDR + " dIS/IS_v51 | p một phía | p Holm (8) | WIN |", "|" + "---|" * 16]
    for c in prim:
        L.append(A.fmt(c, f" {c['rel']:+.4f} | {c['p_better']:.4f} | {c['p_holm8']:.4f} | {'WIN' if c['win'] else '-'} |"))
    L += ["", f"Win Holm 8: {J['P1']['wins_holm8']}/8.", ""]

    # secondary: affected-pair coverage, 4 reversed cells (Holm 4)
    z = np.load(RES / f"ext_r5v52_{pre}ngmix" / "pairs.npz")
    order = [t["id"] for t in man["ngmix"]["topologies"]]
    cols = {k: z[k] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "lo", "hi", "dC")}
    key = lambda m: np.stack([cols[c][m] for c in ("topo", "rep", "T", "cell", "j", "i")], axis=1)  # noqa: E731
    sec = []
    m_ref, m_arm = cols["method"] == 0, cols["method"] == 1
    kr, ka = key(m_ref), key(m_arm)
    pos = {tuple(r): n for n, r in enumerate(ka)}
    ia = np.array([pos.get(tuple(r), -1) for r in kr])
    keep = ia >= 0
    cov_r = ((cols["lo"][m_ref] <= cols["C_t"][m_ref]) & (cols["C_t"][m_ref] <= cols["hi"][m_ref])).astype(float)[keep]
    lo_a, hi_a, ct_a = cols["lo"][m_arm][ia[keep]], cols["hi"][m_arm][ia[keep]], cols["C_t"][m_arm][ia[keep]]
    cov_a = ((lo_a <= ct_a) & (ct_a <= hi_a)).astype(float)
    Tm, cm, dCm, tpm = cols["T"][m_ref][keep], cols["cell"][m_ref][keep], cols["dC"][m_ref][keep], cols["topo"][m_ref][keep]
    for cname in ("reversed|0.2", "reversed|0.5"):
        for T in (80, 150):
            sel = (Tm == T) & (cm == CELL_IDX[cname]) & (dCm >= 0.05)
            if not sel.any():
                continue
            tp = np.array([order[int(t)] for t in tpm[sel]])
            d, rd = boot.ratio(tp, cov_a[sel] - cov_r[sel])
            sec.append({"cell": cname, "T": T, "n": int(sel.sum()), "cov_ref": float(cov_r[sel].mean()),
                        "cov_arm": float(cov_a[sel].mean()), "d": float(d), "ci": A.ci(rd), "p": A.p_side(rd, False)})
    for r, p in zip(sec, A.holm([r["p"] for r in sec])):
        r["p_holm4"] = float(p)
    J["P1"]["affected"] = sec
    L += ["Phụ: coverage cặp affected (dC ≥ 0.05), v5_2 − v5_1, 4 cell reversed ng_mix, Holm 4 (H0 Δ ≤ 0).", "",
          "| cell | T | n cặp | cov v5_1 | cov v5_2 | Δ [95% CI] | p một phía | p Holm (4) |", "|---|---|---|---|---|---|---|---|"]
    for r in sec:
        L.append(f"| {r['cell']} | {r['T']} | {r['n']} | {r['cov_ref']:.3f} | {r['cov_arm']:.3f} | {r['d']:+.3f} "
                 f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p']:.4f} | {r['p_holm4']:.4f} |")
    L.append("")

    # ------------------------------------------------------------------ P2 (component B scenario)
    p2 = rows["p2"]
    S = {}
    meths = [ARM, REF, PHS]
    L += ["## P2: region grid (lag_max 2, rate 0.2): ok/n · coverage (run hoàn tất) · ITT · mean IS · median IS", "",
          "| T | cell | v5_2 rút gọn | v5_2 gate mở | cả hai | " + " | ".join(meths) + " |", "|---|---|---|---|---|" + "---|" * 3]
    for T, k in P2:
        cs = []
        for m in meths:
            s_ = Bm.stats(Bm.cell(p2, T, k, m))
            S[(T, k, m)] = s_
            cs.append(f"{s_['ok']}/{s_['n']} · {s_['cov']:.3f} · {s_['itt']:.3f} · {s_['IS']:.2f} · {s_['IS_med']:.2f}")
        cg = Bm.cell(p2, T, k, ARM)
        nred = sum((r.get("hs_reduced") or 0) for r in cg)
        ngo = sum(1 for r in cg if not r["no_gate"])
        nb = sum(1 for r in cg if not r["no_gate"] and (r.get("hs_reduced") or 0))
        L.append(f"| {T} | {k} | {nred} | {ngo} | {nb} | " + " | ".join(cs) + " |")
    p2a_cells = [S[(T, k, ARM)]["ok"] >= 59 and S[(T, k, ARM)]["n"] == 60 for T, k in P2]
    p2a = all(p2a_cells)
    itts = [S[(T, k, ARM)]["itt"] for T, k in P2]
    p2b_n = sum(x >= 0.90 for x in itts)
    p2b = bool(p2b_n >= 10 and min(itts) >= 0.85)
    def p2c_of(arm_name):
        pc_ = []
        for i, (T, k) in enumerate(P2C):
            resc = {Bm.rk(r) for r in Bm.cell(p2, T, k, arm_name) if r["v51_status"] != "ok" and r["status"] == "ok"}
            pr = Bm.paired(p2, T, k, arm_name, PHS, keys=resc)
            pr["rescued"] = len(resc)
            if pr["n"]:
                pr["upper95"], pr["p_ni"] = Bm.boot_ratio(pr["_da"], pr["_db"], 20261106 + i)
            else:
                pr["upper95"], pr["p_ni"] = None, None
            pc_.append(pr)
        rej_ = Bm.holm([x["p_ni"] for x in pc_])
        pass_ = [bool(rej_[i] and pc_[i]["clusters"] >= MIN_CLUSTERS) for i in range(len(pc_))]
        unadj_ = [bool(x["n"] > 0 and x["upper95"] < Bm.NI_MARGIN and x["clusters"] >= MIN_CLUSTERS) for x in pc_]
        return pc_, rej_, pass_, unadj_

    pc, rej, pc_pass, pc_unadj = p2c_of(ARM)
    p2c = sum(pc_pass) >= 4
    p2_pass = bool(p2a and p2b and p2c)
    L += ["", "P2c: run được cứu (v5_1 không ok, v5_2 ok), ghép cặp với plugin_hs_cal (cả hai ok); H0 tỉ số ≥ 1.10, Holm 6, ≥ 8 cluster.", "",
          "| T | cell | được cứu | ghép cặp | cluster | mean IS v5_2 / plugin_hs_cal | tỉ số | cận trên 95% | p | Holm(6) | median IS | đạt |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (T, k) in enumerate(P2C):
        x = pc[i]
        if x["n"]:
            L.append(f"| {T} | {k} | {x['rescued']} | {x['n']} | {x['clusters']} | {x['mean_a']:.2f} / {x['mean_b']:.2f} | "
                     f"{x['ratio']:.3f} | {x['upper95']:.3f} | {x['p_ni']:.4f} | {'bác' if rej[i] else '-'} | "
                     f"{x['med_a']:.2f} / {x['med_b']:.2f} | {'CÓ' if pc_pass[i] else 'không'} |")
        else:
            L.append(f"| {T} | {k} | {x['rescued']} | 0 | 0 | – | – | – | – | – | – | không |")
    L += ["", f"- P2a hoàn tất ≥ 59/60: {sum(p2a_cells)}/12 -> {ok(p2a)}",
          f"- P2b ITT ≥ 0.90 ở ≥ 10/12 (được {p2b_n}/12), min ≥ 0.85 (được {min(itts):.3f}) -> {ok(p2b)}",
          f"- P2c: {sum(pc_pass)}/6 cell đạt (cần ≥ 4; không hiệu chỉnh: {sum(pc_unadj)}/6) -> {ok(p2c)}",
          f"- **P2: {'PASS' if p2_pass else 'FAIL'}**", ""]
    J["P2"] = {"PASS": p2_pass, "P2a": {"pass": p2a, "cells": int(sum(p2a_cells))},
               "P2b": {"pass": p2b, "cells_itt_ge_090": int(p2b_n), "min_itt": float(min(itts))},
               "P2c": {"pass": bool(p2c), "cells_pass_holm": int(sum(pc_pass)), "cells_pass_unadjusted": int(sum(pc_unadj)),
                       "detail": {f"{T}|{k}": {**Bm.strip(pc[i]), "holm_reject": bool(rej[i])} for i, (T, k) in enumerate(P2C)}},
               "cells": {f"{T}|{k}|{m}": S[(T, k, m)] for (T, k, m) in S}}
    FB = "tolerant_v5_2_fredB"
    if any(r["method"] == FB for r in p2):
        pcB, rejB, passB, unadjB = p2c_of(FB)
        itB = [Bm.stats(Bm.cell(p2, T, k, FB))["itt"] for T, k in P2]
        fr_own = json.loads((ROOT / man["p2"]["config"]["red_calibration"]).read_text(encoding="utf-8"))["red"]
        fr_B = json.loads((ROOT / man["p2"]["config"]["red_calibration_B"]).read_text(encoding="utf-8"))["red"]
        J["P2"]["descriptive_fredB"] = {"P2c_cells_pass_holm": int(sum(passB)), "P2c_cells_pass_unadjusted": int(sum(unadjB)),
                                        "itt": itB, "detail": {f"{T}|{k}": Bm.strip(pcB[i]) for i, (T, k) in enumerate(P2C)},
                                        "f_red_own": fr_own, "f_red_B": fr_B}
        L += ["Mô tả (không quyết định): cùng run v5_2 nhưng nhân f_red của thành phần B (`tolerant_v5_2_fredB`).", "",
              "| T | cell | f_red v5_2 / f_red B | ITT | P2c tỉ số | cận trên 95% | median IS | đạt (Holm 6) |", "|---|---|---|---|---|---|---|---|"]
        for i, (T, k) in enumerate(P2):
            wk = k
            line = f"| {T} | {k} | {fr_own.get(f'{T}|{wk}')} / {fr_B.get(f'{T}|{wk}')} | {itB[i]:.3f} |"
            if (T, k) in P2C:
                x = pcB[P2C.index((T, k))]
                line += (f" {x['ratio']:.3f} | {x['upper95']:.3f} | {x['med_a']:.2f} / {x['med_b']:.2f} | "
                         f"{'CÓ' if passB[P2C.index((T, k))] else 'không'} |" if x["n"] else " – | – | – | không |")
            else:
                line += " – | – | – | – |"
            L.append(line)
        L += ["", f"P2c với f_red của B: {sum(passB)}/6 (không hiệu chỉnh {sum(unadjB)}/6).", ""]

    # ------------------------------------------------------------------ no-harm (a), (b), (c)
    gauss = [A.compare(A.paired(idx["gauss"], ARM, REF, T, k, r), boot) for T, k, r in G]
    for c, p in zip(gauss, A.holm([c["p_worse"] for c in gauss])):
        c["p_worse_holm21"] = float(p)
        c["worse_sig"] = bool(p < 0.05 and c["n_clusters"] >= MIN_CLUSTERS)
        c["ok_a"] = bool(c["ratio"] <= 1.03 and not c["worse_sig"] and (c["cov_ref"] < 0.90 or c["cov_arm"] >= 0.90)
                         and c["n_runs"] == 60)
    nha = all(c["ok_a"] for c in gauss)
    other = [A.compare(A.paired(idx["ngmix"], ARM, REF, T, k, r), boot) for T, k, r in NONPRIM]
    for c in other:
        c["ok_b"] = bool(c["ratio"] <= 1.05 and (c["cov_ref"] < 0.90 or c["cov_arm"] >= 0.90))
    nhb = all(c["ok_b"] for c in other)
    J["no_harm_a"] = {"PASS": nha, "cells": gauss}
    J["no_harm_b"] = {"PASS": nhb, "cells": other}
    L += ["## No-harm (a): lưới Gaussian G, 21 cell (Holm 21, H0 dIS ≤ 0)", "",
          A.HDR + " p tệ hơn | p Holm (21) | đạt |", "|" + "---|" * 15]
    for c in gauss:
        L.append(A.fmt(c, f" {c['p_worse']:.4f} | {c['p_worse_holm21']:.4f} | {'đạt' if c['ok_a'] else 'KHÔNG'} |"))
    L += ["", f"**No-harm (a): {ok(nha)}** (tỉ số ≤ 1.03, không tệ hơn sau Holm 21 với ≥ 8 cluster, coverage ≥ 0.90 nơi v5_1 đạt, đủ 60 run).", "",
          "## No-harm (b): 13 cell ng_mix không primary", "", A.HDR + " p tốt hơn (mô tả) | đạt |", "|" + "---|" * 14]
    for c in other:
        L.append(A.fmt(c, f" {c['p_better']:.4f} | {'đạt' if c['ok_b'] else 'KHÔNG'} |"))
    L += ["", f"**No-harm (b): {ok(nhb)}** (tỉ số ≤ 1.05, coverage ≥ 0.90 nơi v5_1 đạt).", ""]
    desc_c = []
    for s in ("latent1", "noise01"):
        tp_s = sorted({k[0] for k in idx[s]})
        bs = A.Boot(tp_s)
        cs = [A.compare(A.paired(idx[s], ARM, REF, T, k, r), bs) for T, k, r in C8]
        for c in cs:
            c["scenario"] = s
        desc_c += cs
    for c, p in zip(desc_c, A.holm([c["p_worse"] for c in desc_c])):
        c["p_worse_holm8"] = float(p)
    J["no_harm_c"] = {"descriptive": True, "cells": desc_c}
    L += ["## No-harm (c), chỉ mô tả: latent1 và noise0.1 × T{80, 150} × {missing, reversed}-0.2", "",
          "| kịch bản " + A.HDR + " p tệ hơn | p Holm (8, mô tả) |", "|" + "---|" * 16]
    for c in desc_c:
        L.append(f"| {c['scenario']} " + A.fmt(c, f" {c['p_worse']:.4f} | {c['p_worse_holm8']:.4f} |"))
    L.append("")

    # ------------------------------------------------------------------ descriptive: v5_2 vs components where both act
    rt = defaultdict(lambda: [0.0, 0])
    for s, r in allr:
        rt[(s, r["method"])][0] += r.get("sec") or 0.0
        rt[(s, r["method"])][1] += 1
    J["runtime"] = {f"{s}|{m}": {"seconds": v[0], "runs": v[1]} for (s, m), v in rt.items()}
    L += ["## Thời gian (giây, tổng theo method)", "", "| bộ run | method | giây | run |", "|---|---|---|---|"]
    for (s, m), v in sorted(rt.items()):
        L.append(f"| {s} | {m} | {v[0]:.0f} | {v[1]} |")
    L.append("")

    # ------------------------------------------------------------------ verdict (synthesis_round4.md 4.2)
    a_rul = json.loads((RES / "ext_r5ngorient3_analysis/ruling.json").read_text(encoding="utf-8"))
    b_rul = json.loads((RES / "ext_r5hubscreen2_ruling/ruling.json").read_text(encoding="utf-8"))
    # [điều chỉnh, doc 4.8] a component is kept alone only if its own pre-registered run retained it
    a_own = bool(str(a_rul["verdict"]).startswith("RETAINED") and a_rul["V1"]["PASS"] and a_rul["no_harm_a"]["PASS"]
                 and a_rul["no_harm_b"]["PASS"])
    b_own = bool(str(b_rul["criteria"]["verdict"]).startswith("RETAINED") and b_rul["validity"]["V1"])
    valid = v1_pass and vcomp_pass
    if not valid:
        verdict = "INVALID (V1 hoặc V-comp không đạt)"
    elif v0_pass and p1_pass and p2_pass and nha and nhb:
        verdict = "RETAINED-combined (tolerant_v5_2, exploratory)"
    elif p1_pass and not p2_pass and v0_pass and nha and nhb and a_own:
        verdict = "KEEP COMPONENT A ONLY (tolerant_v5_1 + NG-A v3 = tolerant_ngA3, exploratory)"
    elif p2_pass and not p1_pass and nha and b_own:
        verdict = "KEEP COMPONENT B ONLY (tolerant_v5_1 + hubscreen v2 = tolerant_v5_1_hs2, exploratory)"
    else:
        verdict = "NOTHING RETAINED (tolerant_v5_1 giữ nguyên)"
    J["verdict"] = {"verdict": verdict, "V0": v0_pass, "V1": v1_pass, "V_comp": vcomp_pass, "P1": p1_pass, "P2": p2_pass,
                    "no_harm_a": nha, "no_harm_b": nhb, "A_own_V1_noharm": a_own, "B_own_V1": b_own}
    L += ["## Verdict vòng 5 (mục 4.2 của synthesis_round4.md)", "",
          f"- V0 {ok(v0_pass)}; V1 {ok(v1_pass)}; V-comp {ok(vcomp_pass)}",
          f"- P1 {ok(p1_pass)}; P2 {ok(p2_pass)}",
          f"- No-harm (a) {ok(nha)}; no-harm (b) {ok(nhb)}; (c) chỉ mô tả",
          f"- Thành phần đứng riêng (run riêng của nó RETAINED, kèm V1 và no-harm): A (r5ngorient3: {a_rul['verdict']}) {ok(a_own)}; "
          f"B (r5hubscreen2: {b_rul['criteria']['verdict']}) {ok(b_own)}", "", f"**Verdict: {verdict}.**", ""]
    (out / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "ruling.json").write_text(json.dumps(A.clean(J), indent=1, default=str), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
