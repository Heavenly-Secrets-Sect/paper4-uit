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


def longtable(colspec, header, body):
    return ("{\\small\n\\begin{longtable}{" + colspec + "}\n\\toprule\n" + header + " \\\\\n\\midrule\n\\endfirsthead\n"
            "\\toprule\n" + header + " \\\\\n\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n" + body + "\n\\end{longtable}\n}\n")


def plain(colspec, header, body):
    """Short table that must not be split across pages."""
    return ("\\begin{center}\n{\\small\n\\begin{tabular}{" + colspec + "}\n\\toprule\n" + header + " \\\\\n\\midrule\n"
            + body + "\n\\bottomrule\n\\end{tabular}\n}\n\\end{center}\n")


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
                body.append(" & ".join([c1, c2, KN[k]] + vals) + " \\\\")
            if ti < len(Ts) - 1:
                body.append("\\cmidrule(l){2-8}")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = ("Lag & T & Loại hỏng & Hệ số (biên) & Luật cũ & Biên [CI 95\\%] & PAC & Chạm 0,90")
    return longtable("llllrrrc", header, "\n".join(body))


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
                    body.append(" & ".join([c1, c2, c3, lv[l], n, o]) + " \\\\")
                    first = False
                if k != ORDER[-1]:
                    body.append("\\cmidrule(l){3-6}")
            if ti < len(Ts) - 1:
                body.append("\\cmidrule(l){2-6}")
        if li < len(lags) - 1:
            body.append("\\midrule")
    header = "Lag & T & Loại hỏng & Mức hỏng & Cờ mới & Cờ cũ"
    return longtable("lllccc", header, "\n".join(body))


def comparison(col, boldmin):
    meths = [("SRCI", "STRIDE"), ("BVAR-Minnesota", "BVAR-Minnesota"), ("PSel-Union (32x)", "PSel-Union"),
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
    return plain("llrrrrrr", header, "\n".join(body))


OUT.mkdir(exist_ok=True)
(OUT / "guarantee.tex").write_text(guarantee())
(OUT / "flag.tex").write_text(flag())
(OUT / "cmp_is.tex").write_text(comparison(7, True))
(OUT / "cmp_hit.tex").write_text(comparison(4, False))
print("wrote", sorted(p.name for p in OUT.glob("*.tex")))
