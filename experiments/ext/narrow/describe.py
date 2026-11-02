"""Descriptive summary of a frozen-v5 check (ext_narrow_ges, ext_narrow_structured): per cell coverage / IS
/ width of each method, paired IS differences of tolerant_v5 against tolerant_v4 and pselect_union, and the
counts pre-registered in docs/ext/narrow.md. Also checks the tolerant_v4 rows against an earlier run with
the same seeds when one is given.

Run: python experiments/ext/narrow/describe.py ext_narrow_ges [--same-as a3_ges]
Writes results/<name>/describe.md
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paired import RES, cell_stats, index, load, paired  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--same-as")
    a = ap.parse_args()
    rows = load(a.name)
    idx = index(rows)
    out = [f"# {a.name}: descriptive summary (experiments/ext/narrow/describe.py)", ""]
    if a.same_as:
        for m in ("tolerant_v4", "plugin"):
            i1 = index([r for r in rows if r["method"] == m])
            i2 = index([r for r in load(a.same_as) if r["method"] == m])
            com = set(i1) & set(i2)
            same = sum(1 for k in com if abs(i1[k]["iscore_nonnull_mean"] - i2[k]["iscore_nonnull_mean"]) < 1e-12)
            out.append(f"{m} rows identical to {a.same_as}: {same}/{len(com)} (of {len(i1)} here)")
        out.append("")
    methods = [m for m in ("plugin", "pselect_union", "tolerant_v4", "tolerant_v5") if any(r["method"] == m for r in rows)]
    cells = sorted({(r["T"], r["kind"], r["rate"]) for r in rows}, key=lambda c: (c[0], c[1] != "none", c[1], c[2]))
    out += ["| T | cell | " + " | ".join(methods) + " | v5 - v4 | v5 - pselect_union |", "|---|---|" + "---|" * (len(methods) + 2)]
    n_v4 = n_ps = n_worse = n_dam = 0
    for T, kind, rate in cells:
        cs = []
        for m in methods:
            s = cell_stats(rows, m, T, kind, rate)
            cs.append("–" if s is None else f"{s['cov']:.3f} / {s['IS']:.2f} / {s['width']:.2f}" + ("" if s["n"] == s["of"] else f" [{s['n']}/{s['of']}]"))
        p4 = paired(idx, "tolerant_v5", "tolerant_v4", T, kind, rate)
        pp = paired(idx, "tolerant_v5", "pselect_union", T, kind, rate)
        f = lambda p: "–" if p is None else f"{p[0]:+.2f} [{p[1]:+.2f}, {p[2]:+.2f}]"  # noqa: E731
        out.append(f"| {T} | {kind}-{rate} | " + " | ".join(cs) + f" | {f(p4)} | {f(pp)} |")
        if kind != "none":
            n_dam += 1
            s5, s4 = cell_stats(rows, "tolerant_v5", T, kind, rate), cell_stats(rows, "tolerant_v4", T, kind, rate)
            n_v4 += bool(p4 and s5["cov"] >= 0.90 and p4[2] < 0)
            n_ps += bool(pp and s5["cov"] >= 0.90 and pp[2] < 0)
            n_worse += s5["IS"] > 1.05 * s4["IS"]
    out += ["", f"Damaged cells: {n_dam}. v5 cov >= 0.90 and upper CI(v5 - v4) < 0: {n_v4}. "
            f"v5 cov >= 0.90 and upper CI(v5 - pselect_union) < 0: {n_ps}. v5 IS > 1.05 x v4 IS: {n_worse}."]
    (RES / a.name / "describe.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
