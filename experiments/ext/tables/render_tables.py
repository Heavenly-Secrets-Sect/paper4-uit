"""Render results/ext_tables_main/tables.json (+ cited source files) to results/ext_tables_main/tables.md.

Usage: python3 experiments/ext/tables/render_tables.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_tables_main"
TS = [40, 80, 150]
CELLS = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
         ("reversed", 0.2), ("reversed", 0.5)]
SHORT = {"tolerant_v4": "v4", "tolerant_v5_1": "v5_1", "tolerant_v4c": "v4c"}
BUDX = {"bvar_minnesota_v2_cal": ("199", "bvar_minnesota_v2"), "bvar_minnesota_v2": ("199", "bvar_minnesota_v2"),
        "targeted_lp_cal": ("199", "targeted_lp"), "tlp2_lp_cal": ("199", None), "inflate": ("199", None),
        "pselect_union_v3_cal": ("6368", "pselect_union_v3"), "ida_cal": ("≤16 × max(10, 199 // m)", None),
        "bagging": ("≤199", None)}


def cn(kind, rate):
    return "none" if kind == "none" else f"{kind}-{rate}"


def d(c):
    return f"{c['est']:+.2f} [{c['lo']:+.2f}, {c['hi']:+.2f}]"


def d3(c):
    return f"{c['est']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]"


def cls(c):
    return f"{c['raw']}/{c['holm']}"


def ic(s):
    return f"{s['IS']:.2f} ({s['cov']:.3f})" if s else "—"


def n_draws(run, method):
    acc = defaultdict(list)
    p = ROOT / "results" / run / "runs.jsonl"
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["method"] == method and r["status"] == "ok" and r.get("info_n_draws") is not None:
                acc[int(r["T"])].append(r["info_n_draws"])
    return {T: float(np.mean(v)) for T, v in acc.items()}


def main():
    R = json.load(open(OUT / "tables.json"))
    timing = R["timing"]
    L = []
    # ------------------------------------------------------------------ table 1a (R3-1, verbatim from baselines3)
    A = json.load(open(ROOT / "results" / "ext_baselines3_eval" / "analysis.json"))
    cells_b3, comps_b3 = A["result"]["cells"], A["result"]["comps"]
    L += ["## Bảng 1a. Family ghi trước của R3-1 (T80/150 missing; Holm 0.05 trên 56; B = 4000)", "",
          "| T | cell | v4 IS (cov) | v5_1 IS (cov) | baseline mạnh nhất X | X IS (cov) | v4 − X [95% CI] | thô/Holm | v5_1 − X [95% CI] | thô/Holm |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for T, rate in ((80, 0.2), (80, 0.5), (150, 0.2), (150, 0.5)):
        X = "pselect_union_v3_cal"
        cv4, cv5, cx = (cells_b3[f"{m}|{T}|{rate}"] for m in ("tolerant_v4", "tolerant_v5_1", X))
        a, b = comps_b3[f"tolerant_v4|{X}|{T}|{rate}"], comps_b3[f"tolerant_v5_1|{X}|{T}|{rate}"]
        L.append(f"| {T} | missing-{rate} | {ic(cv4)} | {ic(cv5)} | {X} | {ic(cx)} | {d(a)} | {a['raw']}/{a['holm0.05']} | "
                 f"{d(b)} | {b['raw']}/{b['holm0.05']} |")
    v = A["verdicts"]
    L += ["", f"Đếm trên 28 so sánh mỗi method (7 baseline × 4 cell): v4 Holm W {v['tolerant_v4']['W']} / T {v['tolerant_v4']['T']} / "
          f"L {v['tolerant_v4']['L']} (thô theo CI: W 24 / L 2); v5_1 Holm W {v['tolerant_v5_1']['W']} / T {v['tolerant_v5_1']['T']} / "
          f"L {v['tolerant_v5_1']['L']} (thô: W 27 / L 0).", ""]
    # ------------------------------------------------------------------ budget table
    nd2 = n_draws("ext_baselines2_eval", "pselect_union_v2")
    nd3 = n_draws("ext_baselines3_eval", "pselect_union_v3")
    L += ["## Bảng 1c. Compute budget mỗi lần gọi", "",
          "| method | draw mỗi lần gọi | giây/lần gọi T80 | T150 |", "|---|---|---|---|"]
    bud = [("tolerant_v4", "199 refit (repair/orientation rút lại mỗi draw)", "tolerant_v4"),
           ("tolerant_v5_1", "199 refit (re-selection lag mỗi draw)", "tolerant_v5_1"),
           ("pselect_union_v3(_cal)", f"16 graph, 32 orientation member × 199; trung bình {nd3.get(80, float('nan')):.0f} (T80), {nd3.get(150, float('nan')):.0f} (T150)", "pselect_union_v3"),
           ("pselect_union_v2(_cal)", f"cap 4 graph; trung bình {nd2.get(40, float('nan')):.0f} / {nd2.get(80, float('nan')):.0f} / {nd2.get(150, float('nan')):.0f} draw (T40/80/150)", None),
           ("pselect_cal (đo giờ); pselect_union, pselect_union_c2 (cùng công thức, không đo)", "≤ 16 graph × max(10, 199 // số graph)", "pselect_cal"),
           ("fullvar_cal", "199 refit", "fullvar_cal"),
           ("targeted_lp(_cal) (đo giờ); tlp2_lp_cal (cùng draw, không đo)", "199 draw VAR-sieve một tầng", "targeted_lp"),
           ("tlp2_db_p3 (đo giờ); tlp2_db (p = 4, không đo)", "MSDB 200 × 100", "tlp2_db_p3"),
           ("bvar_minnesota_v2(_cal) (đo giờ); bvar_minnesota, bvar_cal, bvar_minnesota_c2 (không đo)", "199 posterior draw", "bvar_minnesota_v2"),
           ("ida_union, ida_cal, ida_union_c2", "≤ 16 member × max(10, 199 // số member)", None),
           ("plugin, inflate, bagging", "199 (inflate dùng lại draw của plugin)", None),
           ("lp_allpast", "0 (Newey–West giải tích)", None)]
    for name, draws, tk in bud:
        t80 = f"{timing[tk + '|80']:.2f}" if tk and f"{tk}|80" in timing else "—"
        t150 = f"{timing[tk + '|150']:.2f}" if tk and f"{tk}|150" in timing else "—"
        L.append(f"| {name} | {draws} | {t80} | {t150} |")
    L.append("")
    # ------------------------------------------------------------------ table 1b
    t1 = R["t1"]
    comp = {(c["a"], c["b"], c["T"], c["kind"], c["rate"]): c for c in t1["comps"]}
    L += ["## Bảng 1b. Envelope post hoc trên 21 cell (B = 20000; Holm 0.05 trên "
          f"{t1['comps'][0]['holm_family_size']} so sánh)", "",
          "| T | cell | v4 IS (cov) | v5_1 IS (cov) | X (nguồn) | X IS (cov) | budget X: draw; s/gọi | v4 − X [95% CI] | thô/Holm | v5_1 − X [95% CI] | thô/Holm |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]

    def bx(m, T):
        dr, tk = BUDX.get(m, ("?", None))
        sec = f"{timing[f'{tk}|{T}']:.2f}" if tk and f"{tk}|{T}" in timing else "—"
        return f"{dr}; {sec}"
    for row in t1["rows"]:
        T, kind, rate, X, X90 = row["T"], row["kind"], row["rate"], row["X"], row["X90"]
        a, b = comp[("tolerant_v4", X, T, kind, rate)], comp[("tolerant_v5_1", X, T, kind, rate)]
        src = row["src"][X].replace("ext_", "")
        L.append(f"| {T} | {cn(kind, rate)} | {ic(row['v4'])} | {ic(row['v5_1'])} | {X} ({src}) | {ic(row['stats'][X])} | "
                 f"{bx(X, T)} | {d(a)} | {cls(a)} | {d(b)} | {cls(b)} |")
        if X90 and X90 != X:
            a9, b9 = comp[("tolerant_v4", X90, T, kind, rate)], comp[("tolerant_v5_1", X90, T, kind, rate)]
            L.append(f"| {T} | {cn(kind, rate)} (X90) | | | {X90} ({row['src'][X90].replace('ext_', '')}) | "
                     f"{ic(row['stats'][X90])} | {bx(X90, T)} | {d(a9)} | {cls(a9)} | {d(b9)} | {cls(b9)} |")
    c1 = t1["counts"]
    L += ["", f"Đếm (22 so sánh mỗi module: 21 cell với X, thêm 1 cell với X90): v4 thô W {c1['tolerant_v4']['raw']['W']} / "
          f"T {c1['tolerant_v4']['raw']['T']} / L {c1['tolerant_v4']['raw']['L']}, Holm W {c1['tolerant_v4']['holm']['W']} / "
          f"T {c1['tolerant_v4']['holm']['T']} / L {c1['tolerant_v4']['holm']['L']}; v5_1 thô W {c1['tolerant_v5_1']['raw']['W']} / "
          f"T {c1['tolerant_v5_1']['raw']['T']} / L {c1['tolerant_v5_1']['raw']['L']}, Holm W {c1['tolerant_v5_1']['holm']['W']} / "
          f"T {c1['tolerant_v5_1']['holm']['T']} / L {c1['tolerant_v5_1']['holm']['L']}.", ""]
    L += ["Ba ứng viên có IS thấp nhất từng cell (IS, cov):", ""]
    for row in t1["rows"]:
        L.append(f"- T{row['T']} {cn(row['kind'], row['rate'])}: " + "; ".join(
            f"{m} {row['stats'][m]['IS']:.2f} ({row['stats'][m]['cov']:.3f})" for m in row["top3"]) +
            f" — {row['n_candidates']} ứng viên đủ điều kiện")
    L.append("")
    # ------------------------------------------------------------------ table 2
    t2 = R["t2"]
    st = t2["stats"]
    comp2 = {(c["a"], c["T"], c["kind"], c["rate"]): c for c in t2["comps"]}
    meths = ["tolerant_v4c", "tolerant_v5_1", "fullvar_cal", "pselect_cal"]
    L += ["## Bảng 2a. Ablation: IS (coverage) theo cell", "",
          "| T | cell | v4 | v4c | v5_1 | fullvar_cal | pselect_cal |", "|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            L.append(f"| {T} | {cn(kind, rate)} | " + " | ".join(ic(st[f"{m}|{T}|{kind}|{rate}"])
                                                       for m in ["tolerant_v4"] + meths) + " |")
    L += ["", f"## Bảng 2b. Ablation: method − v4, IS [95% CI] thô/Holm (Holm trên {t2['comps'][0]['holm_family_size']})", "",
          "| T | cell | v4c − v4 | v5_1 − v4 | fullvar_cal − v4 | pselect_cal − v4 |", "|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            L.append(f"| {T} | {cn(kind, rate)} | " + " | ".join(
                f"{d(comp2[(m, T, kind, rate)])} {cls(comp2[(m, T, kind, rate)])}" for m in meths) + " |")
    L.append("")
    L.append("Đếm trên 21 cell (W = method tốt hơn v4): " + "; ".join(
        f"{SHORT.get(m, m)} thô W {t2['counts'][m]['raw']['W']} / T {t2['counts'][m]['raw']['T']} / L {t2['counts'][m]['raw']['L']}, "
        f"Holm W {t2['counts'][m]['holm']['W']} / T {t2['counts'][m]['holm']['T']} / L {t2['counts'][m]['holm']['L']}"
        for m in meths) + ".")
    L.append("")
    # ------------------------------------------------------------------ table 3
    t3 = R["t3"]["cells"]
    fc = R["t3"]["family_counts"]
    L += ["## Bảng 3a. Coverage trên affected pair (dC ≥ 0.05), cell missing/reversed", "",
          "| T | cell | n | v4 | oracle raw | oracle_cal | v4 − oracle_cal [95% CI] | thô/Holm(12) | v4 − oracle raw [95% CI] | thô/Holm(12) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            if kind not in ("missing", "reversed"):
                continue
            e = t3[f"{T}|{kind}|{rate}|affected"]
            L.append(f"| {T} | {cn(kind, rate)} | {e['n']} | {e['cov_v4']:.3f} | {e['cov_oraw']:.3f} | {e['cov_ocal']:.3f} | "
                     f"{d3(e['g_ocal'])} | {cls(e['g_ocal'])} | {d3(e['g_oraw'])} | {cls(e['g_oraw'])} |")
    L += ["", "Đếm (W = v4 cover nhiều hơn, L = ít hơn): " + "; ".join(
        f"{k}: thô W {v['raw']['W']} / T {v['raw']['T']} / L {v['raw']['L']}, Holm W {v['holm']['W']} / T {v['holm']['T']} / L {v['holm']['L']}"
        for k, v in fc.items() if k.startswith("affected")) + ".", ""]
    L += ["## Bảng 3b. Coverage trên unaffected pair (dC < 0.05)", "",
          "| T | cell | n | v4 | oracle raw | oracle_cal | v4 − oracle_cal [95% CI] | thô/Holm(21) | v4 − oracle raw [95% CI] | thô/Holm(21) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            e = t3[f"{T}|{kind}|{rate}|unaffected"]
            L.append(f"| {T} | {cn(kind, rate)} | {e['n']} | {e['cov_v4']:.3f} | {e['cov_oraw']:.3f} | {e['cov_ocal']:.3f} | "
                     f"{d3(e['g_ocal'])} | {cls(e['g_ocal'])} | {d3(e['g_oraw'])} | {cls(e['g_oraw'])} |")
    L += ["", "Đếm: " + "; ".join(
        f"{k}: thô W {v['raw']['W']} / T {v['raw']['T']} / L {v['raw']['L']}, Holm W {v['holm']['W']} / T {v['holm']['T']} / L {v['holm']['L']}"
        for k, v in fc.items() if k.startswith("unaffected")) + ".", ""]
    nul = R["t3"]["null"]
    L += ["## Bảng 3c. Null pair (|C| ≤ 0.1): tỷ lệ interval chứa 0 và IS trung bình", "",
          "| T | cell | n | v4 chứa 0 | oracle raw chứa 0 | v4 IS null | oracle raw IS null |", "|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            a, o = nul[f"tolerant_v4|{T}|{kind}|{rate}"], nul[f"oracle|{T}|{kind}|{rate}"]
            L.append(f"| {T} | {cn(kind, rate)} | {a['n_null']} | {a['share_contains0']:.4f} | {o['share_contains0']:.4f} | "
                     f"{a['IS_null']:.2f} | {o['IS_null']:.4f} |")
    L.append("")
    # ------------------------------------------------------------------ table 4
    P = json.load(open(ROOT / "results" / "ext_metrics_pairs" / "rq41_pairs.json"))
    L += ["## Bảng 4a. RQ4.1: sai số cường độ và độ trễ theo role (pair-level, median trên pair)", "",
          "| T | cell | role | n | abs plugin | abs v4 | abs oracle | rel plugin | rel v4 | mean-lag plugin | mean-lag v4 | mean-lag oracle | peak plugin | peak v4 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            roles = ["untouched"] if kind == "none" else ["damaged", "downstream"]
            for role in roles:
                g = lambda m: P.get(f"role|{T}|{kind}|{rate}|{role}|{m}")
                pl, v4, orc = g("plugin"), g("tolerant_v4"), g("oracle")
                if pl is None:
                    continue
                f = lambda x, k: "–" if x is None or x.get(k) is None or (isinstance(x.get(k), float) and np.isnan(x[k])) else f"{x[k]:.3f}"
                L.append(f"| {T} | {cn(kind, rate)} | {role} | {pl['n']} | {f(pl, 'abs')} | {f(v4, 'abs')} | {f(orc, 'abs')} | "
                         f"{f(pl, 'rel')} | {f(v4, 'rel')} | {f(pl, 'mlag')} | {f(v4, 'mlag')} | {f(orc, 'mlag')} | "
                         f"{f(pl, 'peak')} | {f(v4, 'peak')} |")
    L.append("")
    t4 = R["t4_lag0"]
    L += ["## Bảng 4b. Coverage của v4 trên cặp có cạnh bị xoá: lag 0 so với lag 1–2", "",
          "| T | cell | cov lag 0 (n) | cov lag 1–2 (n) | lag0 − lag12 [95% CI] | p hai phía | thô/Holm(6) |", "|---|---|---|---|---|---|---|"]
    for c in t4["rows"]:
        L.append(f"| {c['T']} | missing-{c['rate']} | {c['cov_lag0']:.3f} ({c['n_lag0']}) | {c['cov_lag12']:.3f} ({c['n_lag12']}) | "
                 f"{d3(c)} | {c['p2']:.3f} | {cls(c)} |")
    L += ["", f"Đếm (L = lag 0 cover kém hơn có ý nghĩa): thô L {t4['raw']['L']} / T {t4['raw']['T']}, Holm L {t4['holm']['L']} / "
          f"T {t4['holm']['T']}.", ""]
    # ------------------------------------------------------------------ table 5
    t5 = R["t5"]
    st5 = t5["stats"]
    comp5 = {(c["a"], c["b"], c["T"], c["kind"], c["rate"]): c for c in t5["comps"]}
    pts = ["plugin", "inflate", "bagging", "lp_allpast"]
    L += ["## Bảng 5a. RQ4.2: coverage / median width / IS", "",
          "| T | cell | oracle | plugin | inflate | bagging | lp_allpast | v4 | v5_1 |", "|---|---|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            cells = []
            for m in ["oracle"] + pts + ["tolerant_v4", "tolerant_v5_1"]:
                s = st5[f"{m}|{T}|{kind}|{rate}"]
                cells.append("—" if s is None or s["n_ok"] < 54 else f"{s['cov']:.3f} / {s['width_median']:.2f} / {s['IS']:.2f}")
            L.append(f"| {T} | {cn(kind, rate)} | " + " | ".join(cells) + " |")
    L += ["", f"## Bảng 5b. RQ4.2: module − method báo một điểm, IS [95% CI] thô/Holm (Holm trên {t5['comps'][0]['holm_family_size']})", "",
          "| T | cell | v4 − plugin | v4 − inflate | v4 − bagging | v4 − lp_allpast | v5_1 − inflate |", "|---|---|---|---|---|---|---|"]
    for T in TS:
        for kind, rate in CELLS:
            cells = []
            for a, b in [("tolerant_v4", p) for p in pts] + [("tolerant_v5_1", "inflate")]:
                c = comp5.get((a, b, T, kind, rate))
                cells.append("—" if c is None else f"{d(c)} {cls(c)}")
            L.append(f"| {T} | {cn(kind, rate)} | " + " | ".join(cells) + " |")
    L += ["", "Đếm trên các cell có so sánh: " + "; ".join(
        f"{k}: thô W {v['raw']['W']} / T {v['raw']['T']} / L {v['raw']['L']}, Holm W {v['holm']['W']} / T {v['holm']['T']} / L {v['holm']['L']}"
        for k, v in t5["counts"].items()) + ".", ""]
    # width ratio v4/plugin
    L += ["Tỷ số median width v4 / plugin theo cell (mô tả):", ""]
    rat = []
    for T in TS:
        for kind, rate in CELLS:
            a, p = st5[f"tolerant_v4|{T}|{kind}|{rate}"], st5[f"plugin|{T}|{kind}|{rate}"]
            rat.append(f"T{T} {cn(kind, rate)} {a['width_median'] / p['width_median']:.2f}")
    L += ["; ".join(rat), ""]
    # ------------------------------------------------------------------ table 6 (cited, not recomputed)
    FX = json.load(open(ROOT / "results" / "ext_revlag3_flagextra" / "flag_extra.json"))["round2"]
    HV = {r["label"]: r for r in json.load(open(ROOT / "results" / "ext_verify3_revlag3" / "holm_inv_width.json"))["round2"]["rows"]}
    L += ["## Bảng 6. RQ4.4: flag cố định so với rel_width và 1/width (fresh D-07, seed_base 30261102; tolerant_v4)", "",
          "| tập | n | miss rate | AUROC p̂ [CI] | AUROC rel_width | AUROC 1/width [CI] | p̂ − 1/width [CI] | Holm(9) p̂ > 1/width | Holm(9) 1/width > p̂ | flagged | ratio [CI] |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in FX:
        h = HV.get(r["label"])
        hp = "—" if h is None else f"{h['holm9']:.4f}"
        hi = "—" if h is None else f"{h['holm9_inv']:.4f}"
        L.append(f"| {r['label'].replace('|', '-')} | {r['n']} | {r['miss_rate']:.3f} | {r['auc_p']:.3f} [{r['auc_p_ci'][0]:.3f}, {r['auc_p_ci'][1]:.3f}] | "
                 f"{r['auc_rel']:.3f} | {r['auc_inv']:.3f} [{r['auc_inv_ci'][0]:.3f}, {r['auc_inv_ci'][1]:.3f}] | "
                 f"{r['d_inv']:+.3f} [{r['d_inv_ci'][0]:+.3f}, {r['d_inv_ci'][1]:+.3f}] | {hp} | {hi} | {r['share']:.3f} | "
                 f"{r['ratio']:.2f} [{r['ratio_ci'][0]:.2f}, {r['ratio_ci'][1]:.2f}] |")
    L.append("")
    (OUT / "tables.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
