"""Confirmatory rule of tolerant_v5_1 on P4-H2 (docs/ext/v51.md, "Frozen spec for P4-H2").
Frozen before the run; applies C1-C3 mechanically to results/ext_v51_p4h2 (tolerant_v4 vs tolerant_v5_1,
same run, paired). Do not change after the run.

Run (only after the single sealed run): python experiments/ext/v51/rule_p4h2.py
  -> results/ext_v51_p4h2/ruling.md, ruling.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DAMAGED, RES, cell_stats, fmt_p, holm, index, load, paired  # noqa: E402

RUN, M, REF = "ext_v51_p4h2", "tolerant_v5_1", "tolerant_v4"


def main():
    rows = load(RUN)
    idx = index(rows)
    out = [f"# {RUN}: confirmatory ruling of {M} (experiments/ext/v51/rule_p4h2.py)", ""]
    fails = {m: sum(1 for r in rows if r["method"] == m and r["status"] != "ok") for m in (M, REF)}
    out.append(f"Failed runs: {fails}")
    S = lambda T, k, r, m=M: cell_stats(rows, m, T, k, r)  # noqa: E731
    P = lambda T, k, r: paired(idx, M, REF, T, k, r)  # noqa: E731
    c1, c1p = [], []
    for rate in (0.2, 0.5):
        s, p = S(40, "missing", rate), P(40, "missing", rate)
        ok = s["cov"] >= 0.90 and p["hi"] < 0
        c1.append(ok); c1p.append(p["p_less"] if s["cov"] >= 0.90 else 1.0)
        out.append(f"- C1 T=40 missing-{rate}: cov {s['cov']:.3f}, IS {s['IS']:.3f} vs v4 {S(40, 'missing', rate, REF)['IS']:.3f}, "
                   f"v5_1 − v4 {fmt_p(p)} (p {p['p_less']:.4f}) -> {'PASS' if ok else 'FAIL'}")
    c2, c2w = [], []
    for T in (80, 150):
        for kind, rate in DAMAGED:
            s, v, p = S(T, kind, rate), S(T, kind, rate, REF), P(T, kind, rate)
            ok = s["cov"] >= 0.90 and s["IS"] <= 1.05 * v["IS"]
            c2.append(ok); c2w.append(p["p_greater"])
            out.append(f"- C2 T={T} {kind}-{rate}: cov {s['cov']:.3f}, IS {s['IS']:.3f} vs v4 {v['IS']:.3f} "
                       f"(ratio {s['IS'] / v['IS']:.3f}); v5_1 − v4 {fmt_p(p)} -> {'PASS' if ok else 'FAIL'}")
    c3, c3w = [], []
    for T, kind, rate in [(40, "none", 0.0), (80, "none", 0.0), (150, "none", 0.0)] + [(40, k, r) for k in ("extra", "reversed") for r in (0.2, 0.5)]:
        s, v, p = S(T, kind, rate), S(T, kind, rate, REF), P(T, kind, rate)
        ok = s["IS"] <= 1.05 * v["IS"]
        c3.append(ok); c3w.append(p["p_greater"])
        out.append(f"- C3 T={T} {kind}-{rate}: IS {s['IS']:.3f} vs v4 {v['IS']:.3f} (ratio {s['IS'] / v['IS']:.3f}); "
                   f"v5_1 − v4 {fmt_p(p)} -> {'PASS' if ok else 'FAIL'}")
    c1h, c2h, c3h = holm(c1p), holm(c2w), holm(c3w)
    verdict = all(c1) and all(c2) and all(c3)
    out += ["", f"C1 {sum(c1)}/2 (Holm {sum(c1h)}/2); C2 {sum(c2)}/12 (significantly worse than v4 after Holm {sum(c2h)}/12); "
                f"C3 {sum(c3)}/7 (significantly worse after Holm {sum(c3h)}/7)",
            f"-> **{M} {'CONFIRMED' if verdict else 'NOT CONFIRMED'} on P4-H2** "
            f"(Holm version of C1: {'CONFIRMED' if all(c1h) and all(c2) and all(c3) else 'NOT CONFIRMED'})"]
    (RES / RUN / "ruling.md").write_text("\n".join(out) + "\n")
    (RES / RUN / "ruling.json").write_text(json.dumps({"C1": c1, "C1_holm": c1h, "C2": c2, "C2_worse_holm": c2h, "C3": c3,
                                                        "C3_worse_holm": c3h, "verdict": verdict, "failed_runs": fails}, indent=1))
    print("\n".join(out))


if __name__ == "__main__":
    main()
