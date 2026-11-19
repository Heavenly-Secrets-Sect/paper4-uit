"""Generate the LaTeX tables of the topology-level study from the stored result files (no number is typed by hand).
Run from docs/latex/tables:  python make_tables.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = HERE.parents[2] / "results"


def fmt(x, d=3):
    return f"{x:.{d}f}".replace(".", ".")


def write(name, text):
    (HERE / name).write_text(text, encoding="utf-8")


# 1. confirmatory guarantee: per lag
rows = []
for lag in (1, 2, 3):
    d = json.loads((R / f"ext_p4h8_test_lag{lag}/test_eval.json").read_text())["rows"]
    cells = sorted({r["cell"] for r in d})
    fin = [c for c in cells if any(r["cell"] == c and r["variant"] == "marginal b0.1" for r in d)]
    ab = len(cells) - len(fin)
    g = lambda c, v: [r for r in d if r["cell"] == c and r["variant"] == v][0]
    hits = {v: np.mean([g(c, v)["hit"] for c in fin]) for v in ("pooled", "marginal b0.1", "PAC b0.1")}
    reach = sum(g(c, "marginal b0.1")["ci"][1] >= 0.90 for c in fin)
    wr = np.mean([g(c, "marginal b0.1")["width"] for c in fin]) / np.mean([g(c, "pooled")["width"] for c in fin])
    isr = np.mean([g(c, "marginal b0.1")["IS"] for c in fin]) / np.mean([g(c, "pooled")["IS"] for c in fin])
    rows.append(f"{lag} & {len(fin)} & {ab} & {fmt(hits['pooled'])} & {fmt(hits['marginal b0.1'])} & {fmt(hits['PAC b0.1'])} & "
                f"{reach}/{len(fin)} & {fmt(wr, 2)} & {fmt(isr, 2)} \\\\")
write("tab_guarantee.tex", "\\begin{tabular}{cccccccccc}\n\\toprule\n"
      "Lag & Ô có hệ số & Ô từ chối & \\multicolumn{3}{c}{Tỉ lệ topology thỏa điều kiện} & Ô đạt $0.90$ & Độ rộng & IS\\\\\n"
      " & & & luật cũ & biên & PAC & & (biên/cũ) & (biên/cũ)\\\\\n\\midrule\n" + "\n".join(rows).replace("\\\\\n", " \\\\\n") + "\n\\bottomrule\n\\end{tabular}\n")

# 2. equal-guarantee comparison
c = json.loads((R / "ext_p4h8_cmp/test_eval.json").read_text())["cells"]
M = [("tolerant_v5_1", "STRIDE"), ("pselect_union_v3", "PSel-U"), ("pselect_cal", "PSel"), ("fullvar_cal", "Full VAR"),
     ("targeted_lp_cal", "TLP"), ("bvar_minnesota_v2_cal", "BVAR")]
KN = {"none": "Không hỏng", "extra": "Thừa", "missing": "Thiếu", "reversed": "Đảo"}
lines = []
for T in ("40", "150"):
    for k in ("none", "extra", "missing", "reversed"):
        vals = {m: c.get(f"{m}|{T}|{k}") for m, _ in M}
        ok = {m: v for m, v in vals.items() if v and not v["abstain"] and v["ci"][1] >= 0.90}
        best = min(ok, key=lambda m: ok[m]["IS"]) if ok else None
        cell = []
        for m, _ in M:
            v = vals[m]
            s = "--" if (v is None or v["abstain"]) else fmt(v["IS"], 2)
            if v and not v["abstain"] and v["ci"][1] < 0.90:
                s += "$^{*}$"
            if m == best:
                s = "\\textbf{" + s + "}"
            cell.append(s)
        lines.append(f"{T} & {KN[k]} & " + " & ".join(cell) + " \\\\")
write("tab_cmp.tex", "\\begin{tabular}{llcccccc}\n\\toprule\n$T$ & Loại hỏng & " + " & ".join(n for _, n in M) + " \\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")

# 3. flag v2 by T group and lag
fl = json.loads((R / "ext_p4h8_flag_v2/test_eval_v2.json").read_text())
lines = []
for lag in (1, 2, 3):
    for g in ("T 19-30", "T 40", "T 80-150"):
        r = fl.get(f"lag{lag}|{g}")
        if r:
            lines.append(f"{lag} & {g.replace('T ', '').replace('-', '--')} & {fmt(r['new'])} & {fmt(r['old'])} & {fmt(r['neg_width'])} & "
                         f"{r['diff']:+.3f} [{r['ci'][0]:+.3f}; {r['ci'][1]:+.3f}] \\\\".replace(".", "."))
write("tab_flag.tex", "\\begin{tabular}{clcccc}\n\\toprule\nLag & $T$ & Cờ mới & Cờ cũ & $-$độ rộng & Hiệu mới $-$ cũ [KTC 95\\%]\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")

# 4. flag v2 per scenario, lag 1
KN2 = {"none": "Không hỏng", "extra": "Thừa", "missing": "Thiếu", "reversed": "Đảo"}
lines = []
for T in (19, 30, 40, 80, 150):
    row = [str(T)]
    for k in ("none", "extra", "missing", "reversed"):
        if k == "none":
            r = fl.get(f"lag1|{T}|none|-")
            row.append(f"{fmt(r['new'])} / {fmt(r['old'])}" if r else "--")
        else:
            parts = []
            for lv in ("low", "high"):
                r = fl.get(f"lag1|{T}|{k}|{lv}")
                parts.append(f"{fmt(r['new'])} / {fmt(r['old'])}" if r else "--")
            row.append("; ".join(parts))
    lines.append(" & ".join(row) + " \\\\")
write("tab_flag_scn.tex", "\\begin{tabular}{lcccc}\n\\toprule\n$T$ & Không hỏng & Thừa (20\\%; 50\\%) & Thiếu (20\\%; 50\\%) & Đảo (20\\%; 50\\%)\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")

# 5. violations (lag 1)
lines = []
for nm, p in [("Gaussian sạch", "ext_p4h8_test_lag1"), ("Student-$t_4$", "ext_p4h8_noise_t4_lag1"), ("Laplace", "ext_p4h8_noise_laplace_lag1"),
              ("Sai số đo 10\\%", "ext_p4h8_noise_me10_lag1"), ("Sai số đo 30\\%", "ext_p4h8_noise_me30_lag1")]:
    d = json.loads((R / p / "test_eval.json").read_text())["rows"]
    h = {v: [r for r in d if r["variant"] == v] for v in ("pooled", "marginal b0.1", "PAC b0.1")}
    m = h["marginal b0.1"]
    lines.append(f"{nm} & {fmt(np.mean([r['hit'] for r in h['pooled']]))} & {fmt(np.mean([r['hit'] for r in m]))} & "
                 f"{fmt(np.mean([r['hit'] for r in h['PAC b0.1']]))} & {fmt(min(r['hit'] for r in m), 2)}--{fmt(max(r['hit'] for r in m), 2)} & "
                 f"{fmt(np.mean([r['pooled_cov'] for r in m]))} \\\\")
write("tab_violation.tex", "\\begin{tabular}{lccccc}\n\\toprule\nKịch bản & \\multicolumn{3}{c}{Tỉ lệ topology thỏa điều kiện} & Khoảng giữa các ô (biên) & Coverage cặp (biên)\\\\\n"
      " & luật cũ & biên & PAC & & \\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")

# 6. panel-calibrated simulation
ps = json.loads((R / "ext_case_study/panel_calibrated_sim.json").read_text())["rows"]
lines = []
for case, nm in [("none-0.0", "Không hỏng"), ("missing-0.2", "Thiếu 20\\%"), ("missing-0.5", "Thiếu 50\\%")]:
    for meth, mn in [("plugin", "RB dùng nguyên skeleton"), ("srci", "STRIDE")]:
        rs = [r for r in ps if r["case"] == case and r["method"] == meth]
        ok = [r for r in rs if r["status"] == "ok"]
        cov = sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok)
        hit = np.mean([(1 - r["n_covered_nonnull"] / r["n_nonnull"]) <= 0.10 for r in ok])
        lines.append(f"{nm} & {mn} & {len(ok)}/{len(rs)} & {fmt(cov)} & {fmt(hit)} & {fmt(np.median([r['width_kept'] for r in ok]), 2)} \\\\")
write("tab_panelsim.tex", "\\begin{tabular}{llcccc}\n\\toprule\nKhai báo & Phương pháp & Fit thành công & Coverage cặp & Lần sinh có $\\le10\\%$ cặp trượt & Độ rộng trung vị\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
# 7. real panel (case study): pairs between observed variables and the illustrative bank pairs
rp = json.loads((R / "ext_case_study/real_panel_srci.json").read_text())["results"]
LAB = {"macro_policy_rate_pct": "lãi suất chính sách", "stock_return_qoq_pct": "lợi suất cổ phiếu (QoQ)",
       "stock_avg_daily_trade_value_vnd": "giá trị giao dịch bình quân ngày", "macro_gdp_yoy_pct": "tăng trưởng GDP (YoY)",
       "macro_cpi_avg_pct": "CPI bình quân", "stock_avg_daily_volume_cp": "khối lượng giao dịch bình quân ngày",
       "bank_npl_ratio": "tỉ lệ nợ xấu", "bank_roe_ratio": "ROE ngân hàng", "bank_car_ratio": "tỉ lệ an toàn vốn (CAR)", "bank_ldr_ratio": "tỉ lệ cho vay/huy động (LDR)"}
lines, seen = [], []
for r in rp:
    key = (r.get("cause"), r.get("effect"))
    if r.get("status") == "ok" and key not in seen:
        seen.append(key)
for key in seen:
    cs = [r for r in rp if r.get("cause") == key[0] and r.get("effect") == key[1]]
    real = cs[0]["real"]
    cells = []
    for st in ("none-0.0", "missing-0.2", "missing-0.5"):
        rs = [r for r in cs if r["stated"] == st]
        lo, hi, C = (np.median([x[k] for x in rs]) for k in ("lo", "hi", "C"))
        cells.append(f"{C:+.2f} [{lo:+.2f}; {hi:+.2f}]")
    lines.append(f"{LAB[key[0]]} $\\to$ {LAB[key[1]]} & {'thật' if real else 'minh họa'} & " + " & ".join(cells) + " \\\\")
write("tab_realpanel.tex", "\\begin{tabular}{llccc}\n\\toprule\nCặp (nguyên nhân $\\to$ kết quả) & Dữ liệu & Không hỏng & Thiếu 20\\% & Thiếu 50\\%\\\\\n\\midrule\n" + "\n".join(lines).replace(".", ".") + "\n\\bottomrule\n\\end{tabular}\n")
# 8. STRIDE without the stated damage
au = json.loads((R / "ext_p4h8_auto/test_eval.json").read_text())
lines = []
for T in ("40", "150"):
    for k in ("none", "extra", "missing", "reversed"):
        r = au.get(f"{T}|{k}")
        if not r:
            continue
        f = lambda d: f"{d[0]:+.2f} [{d[1]:+.2f}; {d[2]:+.2f}]"
        lines.append(f"{T} & {KN[k]} & {fmt(r['hit'], 2)} & {fmt(r['IS'], 2)} & {fmt(r['IS_srci'], 2)} & {fmt(r['IS_bvar'], 2)} & {f(r['d_srci'])} & {f(r['d_bvar'])} \\\\")
write("tab_auto.tex", "\\begin{tabular}{llccccrr}\n\\toprule\n$T$ & Loại hỏng & Tỉ lệ topology & IS (không khai báo) & IS (\\ours{}) & IS (BVAR) & Hiệu so với \\ours{} & Hiệu so với BVAR\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
print("tables written")
