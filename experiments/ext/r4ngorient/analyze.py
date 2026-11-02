"""Pre-registered rule and diagnostics of r4ngorient (docs/ext/r4ngorient.md, section 5.3).

Inputs: results/ext_r4ngorient_{gauss,ngmix,t10}/ (runs.jsonl, pairs.npz, diag.jsonl, audit.jsonl,
manifest.json), results/ext_r4ngorient_unittest/unit_test.json, results/ext_r4ngorient_gauss/pairing.json,
results/ext_r4ngorient_cal_ngmix/calibration.json (sensitivity).
Writes results/<--out>/{ruling.md, ruling.json}; --prefix selects the run family (v1 default, v2: ext_r4ngorient_v2_).

Statistics: run-level IS (mean over non-null pairs); paired over runs where both methods are ok;
cluster bootstrap by topology, B = 20000, seed 20261104, percentile CI; one-sided p = share of
resamples on the H0 side (floor 1/B); Holm as registered.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.metrics import interval_score  # noqa: E402

OUT = ROOT / "results" / "ext_r4ngorient_analysis"
B, SEED = 20000, 20261104
OCAL = {40: 1.4, 80: 1.3, 150: 1.2}
ARMS = ("tolerant_ngA", "tolerant_ngB")
REF = "tolerant_v5_1"
SHORT = {"tolerant_ngA": "NG-A", "tolerant_ngB": "NG-B", "tolerant_v5_1": "v5_1", "oracle": "oracle"}
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
PRIMARY = [(T, k, r) for T in (80, 150) for k in ("missing", "reversed") for r in (0.2, 0.5)]


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
    def __init__(self, topos):
        self.topos = np.array(sorted(set(topos)))
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(self.topos), size=(B, len(self.topos)))
        self.W = np.stack([np.bincount(r, minlength=len(self.topos)) for r in idx]).astype(float)

    def ratio(self, topo, num, den=None):
        num = np.asarray(num, float)
        den = np.ones(len(num)) if den is None else np.asarray(den, float)
        pos = np.searchsorted(self.topos, topo)
        sn = np.bincount(pos, weights=num, minlength=len(self.topos))
        sd = np.bincount(pos, weights=den, minlength=len(self.topos))
        point = sn.sum() / sd.sum() if sd.sum() > 0 else np.nan
        with np.errstate(invalid="ignore", divide="ignore"):
            reps = (self.W @ sn) / (self.W @ sd)
        return point, reps


def ci(reps):
    r = reps[np.isfinite(reps)]
    return [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))] if len(r) else [np.nan, np.nan]


def p_side(reps, better: bool):
    r = reps[np.isfinite(reps)]
    if not len(r):
        return 1.0
    return float(max(np.mean(r >= 0) if better else np.mean(r <= 0), 1 / B))


def load_runs(name):
    path = ROOT / "results" / name / "runs.jsonl"
    if not path.exists():
        return None
    idx = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        idx[(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"])] = r
    return idx


def cell_compare(idx, boot, arm, ref, T, kind, rate):
    keys = sorted({(k[0], k[1]) for k in idx if k[2] == T and k[3] == kind and k[4] == rate and k[5] == ref})
    topo, d, ia, ir = [], [], [], []
    fail = {arm: 0, ref: 0}
    cov = {arm: [0, 0], ref: [0, 0]}
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
            d.append(ra["iscore_nonnull_mean"] - rr["iscore_nonnull_mean"])
            ia.append(ra["iscore_nonnull_mean"])
            ir.append(rr["iscore_nonnull_mean"])
    if not d:
        return None
    est, reps = boot.ratio(np.array(topo), np.array(d))
    return {"T": T, "kind": kind, "rate": rate, "arm": arm, "ref": ref, "n_runs": len(keys), "n_paired": len(d),
            "fail_arm": fail[arm], "fail_ref": fail[ref],
            "cov_arm": cov[arm][0] / cov[arm][1] if cov[arm][1] else np.nan,
            "cov_ref": cov[ref][0] / cov[ref][1] if cov[ref][1] else np.nan,
            "is_arm": float(np.mean(ia)), "is_ref": float(np.mean(ir)), "ratio": float(np.mean(ia) / np.mean(ir)),
            "d": float(est), "ci": ci(reps), "p_better": p_side(reps, True), "p_worse": p_side(reps, False),
            "share_identical": float(np.mean(np.abs(np.array(d)) < 1e-12))}


def fmt_cmp(c, extra=""):
    return (f"| {c['T']} | {c['kind']}-{c['rate']} | {c['n_paired']}/{c['n_runs']} | {c['fail_arm']}/{c['fail_ref']} | "
            f"{c['cov_arm']:.3f} | {c['cov_ref']:.3f} | {c['is_arm']:.3f} | {c['is_ref']:.3f} | {c['ratio']:.3f} | "
            f"{c['d']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] | {c['share_identical']:.2f} |{extra}")


HDR = ("| T | cell | paired/runs | fail arm/ref | cov arm | cov ref | IS arm | IS ref | ratio | dIS [95% CI] | "
       "share identical |")


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return None
    allv = np.concatenate([pos, neg])
    ranks = pd.Series(allv).rank().values
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="ext_r4ngorient_", help="run-name prefix (v2: ext_r4ngorient_v2_)")
    ap.add_argument("--out", default="ext_r4ngorient_analysis")
    a = ap.parse_args()
    global OUT
    OUT = ROOT / "results" / a.out
    PFX = a.prefix
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"validity": {}, "rule": {}, "secondary": {}, "diag": {}}
    L = [f"# r4ngorient ({PFX}*): kết quả theo rule ghi trước (sinh bởi experiments/ext/r4ngorient/analyze.py)", "",
         f"D-07 development, seed_base {json.loads((ROOT / f'results/{PFX}gauss/manifest.json').read_text())['config']['seed_base']}, 20 topology × 3 replicate. Cluster bootstrap theo topology, "
         f"B = {B}, seed {SEED}. dIS = arm − v5_1 (âm = arm tốt hơn).", ""]
    ut = json.loads((ROOT / "results/ext_r4ngorient_unittest/unit_test.json").read_text(encoding="utf-8"))
    pairing_path = ROOT / f"results/{PFX}gauss/pairing.json"
    pairing = json.loads(pairing_path.read_text(encoding="utf-8")) if pairing_path.exists() else {"PASS": "n/a (không có run đã lưu để ghép)"}
    runs = {s: load_runs(f"{PFX}{s}") for s in ("gauss", "ngmix", "t10")}
    topos = sorted({k[0] for k in runs["gauss"]})
    boot = Boot(topos)
    tindex = {t: i for i, t in enumerate(topos)}

    # ---------------------------------------------------------------- validity
    diag = {s: [json.loads(l) for l in open(ROOT / f"results/{PFX}{s}/diag.jsonl", encoding="utf-8")]
            for s in runs if runs[s] is not None}
    g_open = defaultdict(lambda: [0, 0])
    for s, recs in diag.items():
        for r in recs:
            for key in ((s, r["method"], "all"), (s, r["method"], r["T"]), (s, r["method"], r["T"], r["kind"])):
                g_open[key][0] += r["n_gate_draws"][0]
                g_open[key][1] += r["n_gate_draws"][1]
    v3 = g_open[("gauss", "tolerant_ngA", "all")]
    v3_rate = v3[1] / v3[0] if v3[0] else float("nan")
    res["validity"] = {"V1_unit_test": ut["PASS"], "V2_pairing": pairing.get("PASS"), "V2_detail": pairing,
                       "V3_gauss_gate_open_rate": v3_rate, "V3_counts": v3, "V3": bool(v3_rate <= 0.15)}
    L += ["## Validity", "",
          f"- V1 unit test: {'PASS' if ut['PASS'] else 'FAIL'}",
          f"- V2 ghép cặp v5_1 với results/ext_v51_eval: {pairing.get('PASS')} "
          f"(shared {pairing.get('n_shared')}, field mismatch {pairing.get('n_mismatch_fields')})",
          f"- V3 tỷ lệ gate mở của NG-A trên bank Gaussian (mọi T, cell, draw, cặp): {v3_rate:.4f} "
          f"({v3[1]}/{v3[0]}) -> {'đạt' if v3_rate <= 0.15 else 'KHÔNG đạt'} (≤ 0.15)", ""]

    # ---------------------------------------------------------------- rule per arm
    verdict = {}
    all_cmp = {}
    for arm in ARMS:
        prim = [cell_compare(runs["ngmix"], boot, arm, REF, T, k, r) for T, k, r in PRIMARY]
        ph = holm([c["p_better"] for c in prim])
        for c, p in zip(prim, ph):
            c["p_holm8"] = float(p)
            c["win"] = bool(p < 0.05 and c["cov_arm"] >= 0.90 and c["fail_arm"] <= c["fail_ref"] + 1)
        n_win = sum(c["win"] for c in prim)
        cov_all = all(c["cov_arm"] >= 0.90 for c in prim)
        gauss = [cell_compare(runs["gauss"], boot, arm, REF, T, k, r) for T in (40, 80, 150) for k, r in CELLS]
        gh = holm([c["p_worse"] for c in gauss])
        for c, p in zip(gauss, gh):
            c["p_worse_holm21"] = float(p)
            c["worse_sig"] = bool(p < 0.05)
            c["ok_a"] = bool(c["ratio"] <= 1.03 and not c["worse_sig"])
        nh_a = all(c["ok_a"] for c in gauss)
        other = [cell_compare(runs["ngmix"], boot, arm, REF, T, k, r) for T in (40, 80, 150) for k, r in CELLS
                 if (T, k, r) not in PRIMARY]
        for c in other:
            c["ok_b"] = bool(c["ratio"] <= 1.05 and (c["cov_ref"] < 0.90 or c["cov_arm"] >= 0.90))
        nh_b = all(c["ok_b"] for c in other)
        valid = bool(ut["PASS"] and v3_rate <= 0.15)
        retained = bool(n_win >= 3 and cov_all and nh_a and nh_b and valid)
        verdict[arm] = {"wins": n_win, "cov_all_primary": cov_all, "no_harm_a": nh_a, "no_harm_b": nh_b,
                        "valid": valid, "RETAINED": retained}
        all_cmp[arm] = {"primary": prim, "gauss": gauss, "other": other}
        s = SHORT[arm]
        L += [f"## {s} (`{arm}`) so với v5_1", "", "### Cell chính (ng_mix, Holm qua 8, H0 dIS ≥ 0)", "",
              HDR + " p một phía | p Holm (8) | WIN |", "|" + "---|" * 14]
        for c in prim:
            L.append(fmt_cmp(c, f" {c['p_better']:.4f} | {c['p_holm8']:.4f} | {'WIN' if c['win'] else '-'} |"))
        L += ["", "### No-harm (a): lưới Gaussian, 21 cell (Holm qua 21, H0 dIS ≤ 0)", "",
              HDR + " p tệ hơn | p Holm (21) | ratio ≤ 1.03 và không tệ hơn có ý nghĩa |", "|" + "---|" * 14]
        for c in gauss:
            L.append(fmt_cmp(c, f" {c['p_worse']:.4f} | {c['p_worse_holm21']:.4f} | {'đạt' if c['ok_a'] else 'KHÔNG'} |"))
        L += ["", "### No-harm (b): ng_mix ngoài cell chính, 13 cell", "",
              HDR + " p tốt hơn (mô tả) | ratio ≤ 1.05 và coverage |", "|" + "---|" * 13]
        for c in other:
            L.append(fmt_cmp(c, f" {c['p_better']:.4f} | {'đạt' if c['ok_b'] else 'KHÔNG'} |"))
        L += ["", f"**Verdict {s}:** WIN {n_win}/8 (Holm qua 8); coverage ≥ 0.90 ở cả 8 cell chính: "
              f"{'có' if cov_all else 'KHÔNG'}; no-harm (a): {'đạt' if nh_a else 'KHÔNG đạt'}; no-harm (b): "
              f"{'đạt' if nh_b else 'KHÔNG đạt'}; validity (V1, V3): {'đạt' if valid else 'KHÔNG đạt'} -> "
              f"**{'RETAINED (exploratory)' if retained else 'REJECTED'}**.", ""]

    # NG-B vs NG-A
    bva = [cell_compare(runs["ngmix"], boot, "tolerant_ngB", "tolerant_ngA", T, k, r) for T, k, r in PRIMARY]
    for c, p in zip(bva, holm([c["p_better"] for c in bva])):
        c["p_holm8"] = float(p)
        c["beat"] = bool(p < 0.05)
    n_beat = sum(c["beat"] for c in bva)
    b_over_a = bool(verdict["tolerant_ngB"]["RETAINED"] and n_beat >= 2)
    verdict["NG-B_over_NG-A"] = {"beats": n_beat, "replaces": b_over_a}
    L += ["## NG-B so với NG-A (8 cell chính, Holm qua 8, H0 dIS(B − A) ≥ 0)", "",
          HDR + " p | p Holm (8) | B thắng |", "|" + "---|" * 14]
    for c in bva:
        L.append(fmt_cmp(c, f" {c['p_better']:.4f} | {c['p_holm8']:.4f} | {'có' if c['beat'] else '-'} |"))
    L += ["", f"NG-B thắng NG-A ở {n_beat}/8 cell; NG-B thay NG-A: **{'có' if b_over_a else 'không'}**.", ""]
    res["rule"] = {"verdict": verdict, "cmp": all_cmp, "ngB_vs_ngA": bva}

    # ---------------------------------------------------------------- pairs: affected-pair coverage
    def load_pairs(s):
        z = np.load(ROOT / f"results/{PFX}{s}/pairs.npz")
        meth = [str(m) for m in z["methods"]]
        cells = [str(c) for c in z["cells"]]
        df = pd.DataFrame({k: z[k] for k in ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi",
                                             "dC", "fac")})
        df["mname"] = [meth[int(m)] for m in df.method]
        df["cname"] = [cells[int(c)] for c in df.cell]
        return df, meth

    KEY = ["topo", "rep", "T", "cell", "j", "i"]

    def wide(df, methods):
        base = df[df.mname == methods[0]][KEY + ["cname", "C_t", "dC"]].copy()
        for m in methods:
            s_ = df[df.mname == m][KEY + ["C_e", "lo", "hi", "fac"]].rename(
                columns={"C_e": f"C_{m}", "lo": f"lo_{m}", "hi": f"hi_{m}", "fac": f"fac_{m}"})
            base = base.merge(s_, on=KEY)
        return base

    def cov(lo, hi, c):
        return ((lo <= c) & (c <= hi)).astype(float)

    pairs = {}
    for s in ("gauss", "ngmix", "t10"):
        if runs[s] is None:
            continue
        df, meth = load_pairs(s)
        W = wide(df, ["oracle", REF, *ARMS])
        mid, half = (W.lo_oracle + W.hi_oracle) / 2, (W.hi_oracle - W.lo_oracle) / 2
        c = W["T"].map(OCAL)
        W["cov_ocal"] = cov(mid - c * half, mid + c * half, W.C_t)
        for m in (REF, *ARMS):
            W[f"cov_{m}"] = cov(W[f"lo_{m}"], W[f"hi_{m}"], W.C_t)
            W[f"err_{m}"] = np.abs(W[f"C_{m}"] - W.C_t)
            W[f"w_{m}"] = W[f"hi_{m}"] - W[f"lo_{m}"]
        pairs[s] = W
    sec = []
    L += ["## Phụ: coverage trên cặp affected (dC ≥ 0.05), arm − v5_1", "",
          "| shock | arm | cell | T | n aff | cov v5_1 | cov arm | cov oracle_cal | Δ [CI] | p một phía | p Holm (4, chỉ reversed T80/150 ng_mix) | closed share [CI] | gap arm − oracle_cal | median err v5_1 / arm | median width v5_1 / arm |",
          "|" + "---|" * 15]
    for s in ("ngmix", "gauss", "t10"):
        if s not in pairs:
            continue
        W = pairs[s]
        for arm in ARMS:
            rows_s = []
            for cname in ("reversed|0.2", "reversed|0.5", "missing|0.2", "missing|0.5"):
                for T in (40, 80, 150):
                    sub = W[(W.cname == cname) & (W["T"] == T) & (W.dC >= 0.05)]
                    if not len(sub):
                        continue
                    tp = np.array([topos[int(t)] for t in sub.topo])
                    d, rd = boot.ratio(tp, (sub[f"cov_{arm}"] - sub[f"cov_{REF}"]).values)
                    g0, rg0 = boot.ratio(tp, (sub.cov_ocal - sub[f"cov_{REF}"]).values)
                    g1, rg1 = boot.ratio(tp, (sub[f"cov_{arm}"] - sub.cov_ocal).values)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        sh, rsh = d / g0, rd / rg0
                    rows_s.append({"shock": s, "arm": arm, "cell": cname, "T": T, "n": int(len(sub)),
                                   "cov_ref": float(sub[f"cov_{REF}"].mean()), "cov_arm": float(sub[f"cov_{arm}"].mean()),
                                   "cov_ocal": float(sub.cov_ocal.mean()), "d": float(d), "ci": ci(rd),
                                   "p": p_side(rd, False),  # H0: delta <= 0
                                   "share": float(sh), "share_ci": ci(rsh), "gap": float(g1),
                                   "err": [float(sub[f"err_{REF}"].median()), float(sub[f"err_{arm}"].median())],
                                   "width": [float(sub[f"w_{REF}"].median()), float(sub[f"w_{arm}"].median())],
                                   "registered": s == "ngmix" and cname.startswith("reversed") and T in (80, 150)})
            regs = [r for r in rows_s if r["registered"]]
            for r, p in zip(regs, holm([r["p"] for r in regs])):
                r["p_holm4"] = float(p)
            for r in rows_s:
                ph = f"{r['p_holm4']:.4f}" if "p_holm4" in r else "-"
                L.append(f"| {s} | {SHORT[arm]} | {r['cell']} | {r['T']} | {r['n']} | {r['cov_ref']:.3f} | {r['cov_arm']:.3f} | "
                         f"{r['cov_ocal']:.3f} | {r['d']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p']:.4f} | {ph} | "
                         f"{r['share']:.2f} [{r['share_ci'][0]:.2f}, {r['share_ci'][1]:.2f}] | {r['gap']:+.3f} | "
                         f"{r['err'][0]:.3f} / {r['err'][1]:.3f} | {r['width'][0]:.3f} / {r['width'][1]:.3f} |")
            sec += rows_s
    res["secondary"]["affected"] = sec
    L.append("")

    # ---------------------------------------------------------------- diagnostics
    L += ["## Diagnostic (mô tả)", "", "### Tỷ lệ gate mở theo draw (mọi cặp được đánh giá trong các bootstrap draw)", "",
          "| shock | method | T | kind | gate mở / đánh giá | tỷ lệ |", "|---|---|---|---|---|---|"]
    gate_tab = []
    for key in sorted((k for k in g_open if len(k) == 4), key=str):
        s, m, T, kind = key
        n0, n1 = g_open[key]
        if n0:
            gate_tab.append({"shock": s, "method": m, "T": T, "kind": kind, "n": n0, "open": n1, "rate": n1 / n0})
            L.append(f"| {s} | {SHORT[m]} | {T} | {kind} | {n1}/{n0} | {n1 / n0:.3f} |")
    res["diag"]["gate"] = gate_tab
    # data-level gate and candidate direction
    L += ["", "### Cạnh cùng kỳ thật bị xoá và được repair: chiều đúng", "",
          "Mức dữ liệu: tỷ lệ candidate có p đúng chiều (> 0.5 theo chiều thật) và tỷ lệ gate mở. Mức draw: tỷ lệ draw (có repair cặp đó) chọn đúng chiều; v5_1 rút đồng xu công bằng (khoảng 0.5, trừ khi cycle check ép chiều).", "",
          "| shock | method | T | n candidate thật (dữ liệu) | gate mở | p đúng chiều > 0.5 | n draw | draw đúng chiều |",
          "|---|---|---|---|---|---|---|---|"]
    cand_tab = []
    for s, recs in diag.items():
        for m in ARMS:
            for T in (40, 80, 150):
                rr = [r for r in recs if r["method"] == m and r["T"] == T and r["kind"] == "missing"]
                cands = [c for r in rr for c in r["cands"] if c["damaged_missing"] and c["true_contemp"]]
                tal = [c for r in rr for c in r["cand_tally"] if c["damaged_missing"] and c["true_contemp"]]
                if not rr:
                    continue
                pk = "pB" if m == "tolerant_ngB" else "pA"
                good = [((c[pk] > 0.5) if c["true_uv"] else (c[pk] < 0.5)) for c in cands]
                nd = sum(c["n"] for c in tal)
                ndc = sum((c["n_uv"] if c["true_uv"] else c["n"] - c["n_uv"]) for c in tal)
                row = {"shock": s, "method": m, "T": T, "n_cand": len(cands),
                       "gate_open": float(np.mean([c["gate"] for c in cands])) if cands else None,
                       "p_correct": float(np.mean(good)) if good else None, "n_draw": nd,
                       "draw_correct": ndc / nd if nd else None}
                cand_tab.append(row)
                f = lambda v: "-" if v is None else f"{v:.3f}"  # noqa: E731
                L.append(f"| {s} | {SHORT[m]} | {T} | {len(cands)} | {f(row['gate_open'])} | {f(row['p_correct'])} | {nd} | "
                         f"{f(row['draw_correct'])} |")
    res["diag"]["cand_direction"] = cand_tab
    # pool AUROC
    L += ["", "### Cạnh pool thật sự bị đảo: AUROC của xác suất bị đảo (mức dữ liệu), và tần suất lật theo draw", "",
          "| shock | T | n pool (đảo / không) | AUROC NG-A w = 1 − pA | AUROC NG-B wB | AUROC dl Gaussian | gate mở (NG-A) | lật/draw NG-A: đảo / không | lật/draw NG-B: đảo / không | k/|pool| TB |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    pool_tab = []
    for s, recs in diag.items():
        for T in (40, 80, 150):
            ra = [r for r in recs if r["method"] == "tolerant_ngA" and r["T"] == T and r["kind"] == "reversed"]
            rb = [r for r in recs if r["method"] == "tolerant_ngB" and r["T"] == T and r["kind"] == "reversed"]
            if not ra:
                continue
            pa = [p for r in ra for p in r["pool"]]
            pb = [p for r in rb for p in r["pool"]]
            pos_a = [1 - p["pA"] for p in pa if p["reversed"]]
            neg_a = [1 - p["pA"] for p in pa if not p["reversed"]]
            pos_b = [p["wB"] for p in pb if p["reversed"]]
            neg_b = [p["wB"] for p in pb if not p["reversed"]]
            pos_g = [p["dl"] for p in pb if p["reversed"]]
            neg_g = [p["dl"] for p in pb if not p["reversed"]]

            def flips(rs, rev):
                t = [c for r in rs for c in r["pool_tally"] if c["reversed"] == rev]
                n = sum(c["n"] for c in t)
                return sum(c["n_flip"] for c in t) / n if n else None
            kp = []
            for r in ra:
                rw = runs[s].get((r["topology"], r["replicate"], T, "reversed", r["rate"], REF))
                if r["pool"] and rw:
                    kp.append(rw.get("k", 0) / len(r["pool"]))
            row = {"shock": s, "T": T, "n_rev": len(pos_a), "n_not": len(neg_a), "auroc_A": auroc(pos_a, neg_a),
                   "auroc_B": auroc(pos_b, neg_b), "auroc_dl": auroc(pos_g, neg_g),
                   "gate_open_A": float(np.mean([p["gate"] for p in pa])) if pa else None,
                   "flip_A": [flips(ra, True), flips(ra, False)], "flip_B": [flips(rb, True), flips(rb, False)],
                   "k_over_pool": float(np.mean(kp)) if kp else None}
            pool_tab.append(row)
            f = lambda v: "-" if v is None else f"{v:.3f}"  # noqa: E731
            L.append(f"| {s} | {T} | {row['n_rev']} / {row['n_not']} | {f(row['auroc_A'])} | {f(row['auroc_B'])} | "
                     f"{f(row['auroc_dl'])} | {f(row['gate_open_A'])} | {f(row['flip_A'][0])} / {f(row['flip_A'][1])} | "
                     f"{f(row['flip_B'][0])} / {f(row['flip_B'][1])} | {f(row['k_over_pool'])} |")
    res["diag"]["pool"] = pool_tab
    # sortability
    L += ["", "### Varsortability và R²-sortability của chuỗi quan sát (truth-side audit)", "",
          "| shock | T | varsort (summary) | R²-sort (summary) | varsort (cùng kỳ) | R²-sort (cùng kỳ) | n unit |",
          "|---|---|---|---|---|---|---|"]
    sort_tab = []
    for s in ("gauss", "ngmix", "t10"):
        p = ROOT / f"results/{PFX}{s}/audit.jsonl"
        if not p.exists():
            continue
        au = [json.loads(l) for l in open(p, encoding="utf-8")]
        for T in sorted({a["T"] for a in au}):
            aa = [a for a in au if a["T"] == T]
            mv = lambda key, f: float(np.mean([a[key][f] for a in aa if a[key][f] is not None]))  # noqa: E731
            row = {"shock": s, "T": T, "vs_sum": mv("summary", "varsort"), "r2_sum": mv("summary", "r2sort"),
                   "vs_c": mv("contemp", "varsort"), "r2_c": mv("contemp", "r2sort"), "n": len(aa)}
            sort_tab.append(row)
            L.append(f"| {s} | {T} | {row['vs_sum']:.3f} | {row['r2_sum']:.3f} | {row['vs_c']:.3f} | {row['r2_c']:.3f} | {len(aa)} |")
    res["diag"]["sortability"] = sort_tab

    # ng_t10 descriptive
    if runs["t10"] is not None:
        L += ["", "### ng_t10 (mô tả)", "", HDR + " arm |", "|" + "---|" * 12]
        t10 = []
        for arm in ARMS:
            for T in (80, 150):
                for k, r in (("missing", 0.2), ("reversed", 0.2)):
                    c = cell_compare(runs["t10"], boot, arm, REF, T, k, r)
                    if c:
                        t10.append(c)
                        L.append(fmt_cmp(c, f" {SHORT[arm]} |"))
        res["diag"]["t10"] = t10

    # sensitivity: factors re-tuned on ng_mix D-07H
    calp = ROOT / "results/ext_r4ngorient_cal_ngmix/calibration.json"
    if calp.exists():
        fac_new = json.loads(calp.read_text(encoding="utf-8"))
        df, meth = load_pairs("ngmix")
        kmap = {}
        for key, rw in runs["ngmix"].items():
            kmap[(tindex[key[0]], key[1], key[2], key[3], key[4])] = rw.get("k", 0)
        cells_l = [f"{k}|{r}" for k, r in CELLS]
        df["kind"] = [c.split("|")[0] for c in df.cname]
        df["rate"] = [float(c.split("|")[1]) for c in df.cname]
        df["k"] = [kmap.get((int(t), int(rp), int(T_), kd, rt), 0) for t, rp, T_, kd, rt in
                   zip(df.topo, df.rep, df["T"], df.kind, df.rate)]
        df["wk"] = np.where(df.k == 0, "none", df.kind)
        out_s = []
        L += ["", "### Sensitivity: mọi factor tune lại trên ng_mix D-07H (mô tả)", "",
              "Factor mới (method|T|width_key): " + ", ".join(f"{k}={v}" for k, v in sorted(fac_new.items())), "",
              "| arm | T | cell | IS v5_1 (cũ → mới) | IS arm (cũ → mới) | cov v5_1 mới | cov arm mới | dIS mới [CI] |",
              "|---|---|---|---|---|---|---|---|"]
        mid = (df.lo + df.hi) / 2
        half = (df.hi - df.lo) / 2 / df.fac
        newf = np.array([fac_new.get(f"{m}|{int(T_)}|{wk}", np.nan) if m != "oracle" else 1.0
                         for m, T_, wk in zip(df.mname, df["T"], df.wk)])
        df["is_old"] = interval_score(df.lo.values, df.hi.values, df.C_t.values)
        df["is_new"] = interval_score((mid - half * newf).values, (mid + half * newf).values, df.C_t.values)
        df["cov_new"] = ((mid - half * newf <= df.C_t) & (df.C_t <= mid + half * newf)).astype(float)
        run_is = df.groupby(["mname", "topo", "rep", "T", "cname"]).agg(is_old=("is_old", "mean"), is_new=("is_new", "mean"),
                                                                        cov_new=("cov_new", "sum"), n=("cov_new", "size")).reset_index()
        # sanity: recomputed old IS equals runs.jsonl IS
        chk = []
        for _, r in run_is[run_is.mname == REF].head(200).iterrows():
            kd, rt = r.cname.split("|")
            rw = runs["ngmix"][(topos[int(r.topo)], int(r.rep), int(r["T"]), kd, float(rt), REF)]
            chk.append(abs(rw["iscore_nonnull_mean"] - r.is_old))
        hdr_at = next(i for i in range(len(L) - 1, -1, -1) if L[i].startswith("| arm | T | cell | IS v5_1"))
        L.insert(hdr_at, f"Kiểm tra: IS tính lại từ pairs.npz với factor cũ khớp runs.jsonl, max |Δ| = {max(chk):.2e} (200 run).")
        L.insert(hdr_at + 1, "")
        for arm in ARMS:
            for T, k, r in PRIMARY:
                cname = f"{k}|{r}"
                a = run_is[(run_is.mname == arm) & (run_is["T"] == T) & (run_is.cname == cname)]
                b = run_is[(run_is.mname == REF) & (run_is["T"] == T) & (run_is.cname == cname)]
                mm = a.merge(b, on=["topo", "rep"], suffixes=("_a", "_b"))
                d, rd = boot.ratio(np.array([topos[int(t)] for t in mm.topo]), (mm.is_new_a - mm.is_new_b).values)
                row = {"arm": arm, "T": T, "cell": cname, "is_ref_old": float(mm.is_old_b.mean()), "is_ref_new": float(mm.is_new_b.mean()),
                       "is_arm_old": float(mm.is_old_a.mean()), "is_arm_new": float(mm.is_new_a.mean()),
                       "cov_ref_new": float(mm.cov_new_b.sum() / mm.n_b.sum()), "cov_arm_new": float(mm.cov_new_a.sum() / mm.n_a.sum()),
                       "d": float(d), "ci": ci(rd)}
                out_s.append(row)
                L.append(f"| {SHORT[arm]} | {T} | {cname} | {row['is_ref_old']:.3f} → {row['is_ref_new']:.3f} | "
                         f"{row['is_arm_old']:.3f} → {row['is_arm_new']:.3f} | {row['cov_ref_new']:.3f} | {row['cov_arm_new']:.3f} | "
                         f"{row['d']:+.3f} [{row['ci'][0]:+.3f}, {row['ci'][1]:+.3f}] |")
        res["diag"]["sensitivity_ngmix_factors"] = {"factors": fac_new, "rows": out_s, "recompute_check_max": max(chk)}

    # oracle context and runtime
    L += ["", "### Bối cảnh: oracle và oracle_cal (mọi cặp non-null) theo shock", "",
          "| shock | T | cell | cov oracle | cov oracle_cal | cov v5_1 | cov NG-A | cov NG-B |", "|---|---|---|---|---|---|---|---|"]
    ctx = []
    for s, W in pairs.items():
        for T in sorted(W["T"].unique()):
            for cname in [f"{k}|{r}" for k, r in CELLS]:
                sub = W[(W["T"] == T) & (W.cname == cname)]
                if not len(sub):
                    continue
                co = float(cov(sub.lo_oracle, sub.hi_oracle, sub.C_t).mean())
                row = {"shock": s, "T": int(T), "cell": cname, "cov_oracle": co, "cov_ocal": float(sub.cov_ocal.mean()),
                       **{f"cov_{m}": float(sub[f"cov_{m}"].mean()) for m in (REF, *ARMS)}}
                ctx.append(row)
                L.append(f"| {s} | {int(T)} | {cname} | {co:.3f} | {row['cov_ocal']:.3f} | {row['cov_' + REF]:.3f} | "
                         f"{row['cov_tolerant_ngA']:.3f} | {row['cov_tolerant_ngB']:.3f} |")
    res["diag"]["context"] = ctx
    L += ["", "### Thời gian theo method (giây, tổng CPU trong method, mọi run)", "", "| shock | method | giây | run |", "|---|---|---|---|"]
    rt = []
    for s, idx in runs.items():
        if idx is None:
            continue
        acc = defaultdict(lambda: [0.0, 0])
        for key, rw in idx.items():
            if rw.get("info_seconds") is not None:
                acc[key[5]][0] += rw["info_seconds"]
                acc[key[5]][1] += 1
        for m, (sec_, n_) in sorted(acc.items()):
            rt.append({"shock": s, "method": m, "seconds": sec_, "runs": n_})
            L.append(f"| {s} | {SHORT.get(m, m)} | {sec_:.0f} | {n_} |")
    res["diag"]["runtime"] = rt
    (OUT / "ruling.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (OUT / "ruling.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)),
                                     encoding="utf-8")
    print("\n".join(L[:12]))
    for arm in ARMS:
        print(arm, verdict[arm])
    print("NG-B over NG-A", verdict["NG-B_over_NG-A"])


if __name__ == "__main__":
    main()
