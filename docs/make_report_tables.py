"""Build the LaTeX tables (booktabs + multirow) used by bao_cao_phan_hoi_thay_2026-11-15.md.

Reads only result files under results/ and writes docs/report_tables/*.tex.
Run from the repository root or docs/: python3 docs/make_report_tables.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "report_tables"
KN = {"none": "Không hỏng", "extra": "Thừa cạnh", "missing": "Thiếu cạnh", "reversed": "Đảo cạnh"}
ORDER = ["none", "extra", "missing", "reversed"]
fm = lambda x: x.replace(".", ",")


def longtable(colspec, header, body, caption, label):
    cap = "\\caption{" + caption + "}\\label{" + label + "}\\\\\n"
    return ("{\\small\n\\begin{longtable}{" + colspec + "}\n" + cap + "\\toprule\n" + header + " \\\\\n\\midrule\n\\endfirsthead\n"
            "\\toprule\n" + header + " \\\\\n\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n" + body + "\n\\end{longtable}\n}\n")


def plain(colspec, header, body, caption, label):
    """Short table that must not be split across pages."""
    return ("\\begin{table}[H]\n\\centering\n\\caption{" + caption + "}\\label{" + label + "}\n{\\small\n\\begin{tabular}{" + colspec + "}\n\\toprule\n" + header + " \\\\\n\\midrule\n"
            + body + "\n\\bottomrule\n\\end{tabular}\n}\n\\end{table}\n")


def mr(n, text):
    return f"\\multirow{{{n}}}{{*}}{{{text}}}"


def guarantee():
    body = []
    lags = (1, 2, 3)
    for li, lag in enumerate(lags):
        d = {}
        for line in open(ROOT / f"results/ext_p4h8_test_lag{lag}/test_eval.md"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if c[0] == "tolerant_v5_1" and c[3] in ("pooled", "marginal b0.1", "PAC b0.1"):
                d[(int(c[1]), c[2], c[3])] = c
        Ts = sorted({t for t, _, _ in d})
        for ti, T in enumerate(Ts):
            for ki, k in enumerate(ORDER):
                old, mg, pc = d[(T, k, "pooled")], d[(T, k, "marginal b0.1")], d[(T, k, "PAC b0.1")]
                if mg[4] == "abstain":
                    vals = ["từ chối", fm(old[5]), "---", "---", "---"]
                else:
                    ci = re.findall(r"[\d.]+", mg[6])
                    vals = [fm(mg[4]), fm(old[5]), f"{fm(mg[5])} [{fm(ci[0])}; {fm(ci[1])}]", fm(pc[5]),
                            "có" if float(ci[1]) >= 0.90 else "không"]
                c1 = mr(len(Ts) * 4, lag) if (ti == 0 and ki == 0) else ""
                c2 = mr(4, T) if ki == 0 else ""
                body.append(" & ".join([c1, c2, KN[k]] + vals) + (" \\\\*" if ki < 3 else " \\\\"))
            if ti < len(Ts) - 1:
                body.append("\\cmidrule(l){2-8}")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = ("Lag & T & Loại hỏng & Hệ số $c$ (biên) & Luật cũ & Biên [CI 95\\%] & PAC & Chạm 0,90")
    return longtable("llllrrrc", header, "\n".join(body),
                     "Tỉ lệ topology đạt ngưỡng theo từng ô (lag, $T$, loại hỏng), trên 550 topology kiểm tra. Mục tiêu là $0{,}90$.", "tab:guarantee")


def flag():
    res = (ROOT / "results/ext_p4h8_flag_v2/test_eval_v2.md").read_text()
    lv = {"-": "0", "low": "0,2", "high": "0,5"}
    body = []
    lags = (1, 2, 3)
    for li, lag in enumerate(lags):
        blk = res.split(f"## Lag {lag} ")[1].split("\n## Lag")[0]
        d = {}
        for T, k, l, n, o in re.findall(r"^\| (\d+) \| (\w+) \| (\S+) \| \d+ \| [\d.]+ \| ([\d.]+) \| ([\d.]+) \|", blk, flags=re.M):
            d[(int(T), k, l)] = (fm(n), fm(o))
        Ts = sorted({t for t, _, _ in d})
        for ti, T in enumerate(Ts):
            first = True
            for k in ORDER:
                levels = [l for l in ("-", "low", "high") if (T, k, l) in d]
                for si, l in enumerate(levels):
                    c1 = mr(len(Ts) * 7, lag) if (ti == 0 and first) else ""
                    c2 = mr(7, T) if first else ""
                    c3 = mr(len(levels), KN[k]) if si == 0 else ""
                    n, o = d[(T, k, l)]
                    last = (k == ORDER[-1] and si == len(levels) - 1)
                    body.append(" & ".join([c1, c2, c3, lv[l], n, o]) + (" \\\\" if last else " \\\\*"))
                    first = False
                if k != ORDER[-1]:
                    body.append("\\cmidrule(l){3-6}")
            if ti < len(Ts) - 1:
                body.append("\\cmidrule(l){2-6}")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = "Lag & T & Loại hỏng & Mức hỏng & Cờ mới & Cờ cũ"
    return longtable("lllccc", header, "\n".join(body),
                     "AUROC của cờ mới và cờ cũ theo từng lag, $T$, loại hỏng và mức hỏng.", "tab:flag")


def comparison(col, boldmin, caption, label):
    meths = [("SRCI", "STRIDE (ours)"), ("BVAR-Minnesota", "BVAR-Minnesota"), ("PSel-Union (32x)", "PSel-Union"),
             ("PSel", "PSel"), ("Full VAR", "Full VAR"), ("TLP", "TLP")]
    d = {}
    for line in open(ROOT / "results/ext_p4h8_cmp/test_eval.md"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 9 and c[0].isdigit():
            d[(int(c[0]), c[1], c[2])] = c
    body = []
    for ti, T in enumerate((40, 150)):
        for ki, k in enumerate(ORDER):
            vals, ok = [], []
            for m, _ in meths:
                c = d[(T, k, m)]
                vals.append(c[col].split()[0])
                ok.append(c[8] == "yes")
            best = min((float(v), i) for i, v in enumerate(vals) if ok[i])[1] if boldmin else -1
            cells = []
            for i, v in enumerate(vals):
                t = fm(v) + ("" if ok[i] else "$^{\\dagger}$")
                cells.append(f"\\textbf{{{t}}}" if i == best else t)
            body.append(" & ".join([mr(4, T) if ki == 0 else "", KN[k]] + cells) + " \\\\")
        if ti == 0:
            body.append("\\midrule")
    header = "T & Loại hỏng & " + " & ".join(n for _, n in meths)
    return plain("llrrrrrr", header, "\n".join(body), caption, label)


def compact_table(colspec, header, body, caption, label):
    return ("\\begin{table}[H]\n\\centering\n\\caption{" + caption + "}\\label{" + label + "}\n{\\footnotesize\n\\setlength{\\tabcolsep}{3.5pt}\n"
            "\\begin{tabular}{" + colspec + "}\n\\toprule\n" + header + "\n\\midrule\n" + body + "\n\\bottomrule\n\\end{tabular}\n}\n\\end{table}\n")


def guarantee_compact():
    body = []
    lags = (1, 2, 3)
    for li, lag in enumerate(lags):
        d = {}
        for line in open(ROOT / f"results/ext_p4h8_test_lag{lag}/test_eval.md"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if c[0] == "tolerant_v5_1" and c[3] in ("pooled", "marginal b0.1", "PAC b0.1"):
                d[(int(c[1]), c[2], c[3])] = c
        Ts = sorted({t for t, _, _ in d})
        for ti, T in enumerate(Ts):
            cells = []
            for k in ORDER:
                old, mg, pc = d[(T, k, "pooled")], d[(T, k, "marginal b0.1")], d[(T, k, "PAC b0.1")]
                if mg[4] == "abstain":
                    cells.append(f"{fm(old[5])} / từ chối")
                else:
                    ci = re.findall(r"[\d.]+", mg[6])
                    mark = "" if float(ci[1]) >= 0.90 else "$^{\\dagger}$"
                    cells.append(f"{fm(old[5])} / {fm(mg[5])}{mark} / {fm(pc[5])}")
            c1 = mr(len(Ts), lag) if ti == 0 else ""
            body.append(" & ".join([c1, str(T)] + cells) + " \\\\")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = "Lag & $T$ & Không hỏng & Thừa cạnh & Thiếu cạnh & Đảo cạnh \\\\"
    cap = ("Tỉ lệ topology đạt ngưỡng trên 550 topology kiểm tra (mục tiêu $0{,}90$). Mỗi ô gồm ba số: luật cũ / phiên bản biên / phiên bản PAC. "
           "$^{\\dagger}$: cận trên của khoảng tin cậy 95\\% của phiên bản biên thấp hơn $0{,}90$. ``từ chối'': không có hệ số hữu hạn nên không đưa ra bảo đảm. "
           "Hệ số $c$ và khoảng tin cậy từng ô nằm ở Phụ lục.")
    return compact_table("llcccc", header, "\n".join(body), cap, "tab:guarantee-compact")


def flag_compact():
    res = (ROOT / "results/ext_p4h8_flag_v2/test_eval_v2.md").read_text()
    body = []
    lags = (1, 2, 3)
    for li, lag in enumerate(lags):
        blk = res.split(f"## Lag {lag} ")[1].split("\n## Lag")[0]
        d = {}
        for T, k, l, n, o in re.findall(r"^\| (\d+) \| (\w+) \| (\S+) \| \d+ \| [\d.]+ \| ([\d.]+) \| ([\d.]+) \|", blk, flags=re.M):
            d[(int(T), k, l)] = f"{fm(n)}/{fm(o)}"
        Ts = sorted({t for t, _, _ in d})
        for ti, T in enumerate(Ts):
            cells = [d[(T, "none", "-")]]
            for k in ("extra", "missing", "reversed"):
                cells += [d[(T, k, "low")], d[(T, k, "high")]]
            c1 = mr(len(Ts), lag) if ti == 0 else ""
            body.append(" & ".join([c1, str(T)] + cells) + " \\\\")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = ("\\multirow{2}{*}{Lag} & \\multirow{2}{*}{$T$} & Không hỏng & \\multicolumn{2}{c}{Thừa cạnh} & \\multicolumn{2}{c}{Thiếu cạnh} & \\multicolumn{2}{c}{Đảo cạnh} \\\\\n"
              "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\\cmidrule(l){8-9}\n & & & 0,2 & 0,5 & 0,2 & 0,5 & 0,2 & 0,5 \\\\")
    cap = ("AUROC của cờ mới / cờ cũ theo lag, $T$, loại hỏng và mức hỏng (0,2 hoặc 0,5). "
           "Các ô lag 2 với $T=30$ và lag 3 với $T=40$ không có vì phương pháp từ chối bảo đảm.")
    return compact_table("llccccccc", header, "\n".join(body), cap, "tab:flag-compact")


OUT.mkdir(exist_ok=True)
(OUT / "guarantee.tex").write_text(guarantee())
(OUT / "flag.tex").write_text(flag())
(OUT / "guarantee_compact.tex").write_text(guarantee_compact())
(OUT / "flag_compact.tex").write_text(flag_compact())
(OUT / "cmp_is.tex").write_text(comparison(7, True, "Interval score trung bình ở lag 1 (càng thấp càng tốt). In đậm là giá trị thấp nhất trong các phương pháp đạt mức đảm bảo; $^{\\dagger}$ là phương pháp không đạt mức đảm bảo ở ô đó.", "tab:cmp-is"))
(OUT / "cmp_hit.tex").write_text(comparison(4, False, "Tỉ lệ topology đạt ngưỡng của các phương pháp ở lag 1 (mục tiêu $0{,}90$).", "tab:cmp-hit"))
print("wrote", sorted(p.name for p in OUT.glob("*.tex")))
