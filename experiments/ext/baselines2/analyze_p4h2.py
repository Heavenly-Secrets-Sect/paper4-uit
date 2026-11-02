"""Confirmatory analysis for the frozen P4-H2 run of R2-1 (docs/ext/baselines2.md, "Frozen spec for P4-H2").

Written on 2026-11-02 after the D-07 development result, BEFORE any P4-H2 use. Not run on P4-H2 by the author.

Usage:  python experiments/ext/baselines2/analyze_p4h2.py [--results results/ext_baselines2_p4h2]
(The --results flag exists only so the code could be dry-run on results/ext_baselines2_eval; the rule is
evaluated on results/ext_baselines2_p4h2.)

Statistics (identical to analyze.py): coverage pooled over non-null pairs of ok runs; paired IS difference
v4 - X per (topology, replicate) run; estimate = mean; 95% percentile CI from B = 4000 cluster-bootstrap resamples
of topologies (numpy default_rng(20261102), one stream, comparisons in the fixed order below); one-sided
p for "v4 better" = (1 + #{bootstrap mean >= 0}) / (B + 1).

C1 (primary, decides the claim): T = 80, cells missing-0.2 and missing-0.5, X in {pselect_union_v2,
    pselect_union_v2_cal}: 4 comparisons. PASS iff in all 4: v4 coverage >= 0.90 AND the comparison is rejected
    by Holm step-down at family level 0.025 one-sided across the 4. The CI-only count is reported next to it.
C2 (secondary, decides nothing): same test for X = bvar_minnesota_v2_cal at T in {80, 150} x 2 missing cells,
    Holm across its 4.
D  (descriptive, no verdict): T = 150 missing cells against pselect_union_v2(_cal): estimate, CI, two-sided p.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import B, cluster_boot, holm, load  # noqa: E402

V4 = "tolerant_v4"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/ext_baselines2_p4h2")
    args = ap.parse_args(argv)
    out = ROOT / args.results
    rows = load(out / "runs.jsonl")
    rng = np.random.default_rng(20261102)
    idx = {(r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r
           for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}

    def cov(T, rate, m):
        g = [r for r in rows if (r["T"], r["kind"], r["rate"], r["method"]) == (T, "missing", rate, m) and r["status"] == "ok"]
        return sum(r["n_covered_nonnull"] for r in g) / sum(r["n_nonnull"] for r in g), float(np.mean([r["iscore_nonnull_mean"] for r in g])), len(g)

    def paired(T, rate, m):
        per = defaultdict(list)
        for (tp, rep, t, k, rt, meth), r in idx.items():
            if (t, k, rt, meth) == (T, "missing", rate, m):
                b = idx.get((tp, rep, t, k, rt, V4))
                if b is not None:
                    per[tp].append(b["iscore_nonnull_mean"] - r["iscore_nonnull_mean"])
        est, lo, hi, boots = cluster_boot(per, rng)
        return {"est": est, "lo": lo, "hi": hi, "p_v4_better": (1 + int((boots >= 0).sum())) / (B + 1),
                "p_two_sided": min(1.0, 2 * min((1 + int((boots >= 0).sum())) / (B + 1), (1 + int((boots <= 0).sum())) / (B + 1)))}

    res, lines = {}, [f"# Confirmatory analysis ({args.results})", ""]
    families = {"C1": [(80, r, X) for X in ("pselect_union_v2", "pselect_union_v2_cal") for r in (0.2, 0.5)],
                "C2": [(T, r, "bvar_minnesota_v2_cal") for T in (80, 150) for r in (0.2, 0.5)],
                "D": [(150, r, X) for X in ("pselect_union_v2", "pselect_union_v2_cal") for r in (0.2, 0.5)]}
    for fam, comps in families.items():
        d = {c: paired(*c) for c in comps}
        rej = holm({c: d[c]["p_v4_better"] for c in comps}, 0.025)
        lines += [f"## {fam}", "", "| T | cell | X | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p one-sided | p two-sided | CI pass | Holm pass |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        n_ci = n_h = 0
        for (T, rate, X) in comps:
            c4, i4, _ = cov(T, rate, V4)
            cx, ix, _ = cov(T, rate, X)
            ci_ok = c4 >= 0.90 and d[(T, rate, X)]["hi"] < 0
            h_ok = c4 >= 0.90 and rej[(T, rate, X)]
            n_ci += ci_ok
            n_h += h_ok
            e = d[(T, rate, X)]
            res[f"{fam}|{T}|{rate}|{X}"] = {**e, "v4_cov": c4, "IS_v4": i4, "IS_X": ix, "cov_X": cx, "ci_pass": ci_ok, "holm_pass": h_ok}
            lines.append(f"| {T} | missing-{rate} | {X} | {c4:.3f} | {i4:.2f} | {ix:.2f} | {cx:.3f} | {e['est']:+.2f} [{e['lo']:+.2f}, {e['hi']:+.2f}] | "
                         f"{e['p_v4_better']:.4f} | {e['p_two_sided']:.4f} | {'pass' if ci_ok else 'FAIL'} | {'pass' if h_ok else 'FAIL'} |")
        if fam != "D":
            verdict = "PASS" if n_h == len(comps) else "FAIL"
            res[f"{fam}|verdict"] = {"holm": verdict, "n_holm": n_h, "n_ci": n_ci, "of": len(comps)}
            lines += ["", f"**{fam}: {verdict}** (Holm over {len(comps)}: {n_h}/{len(comps)}; CI only: {n_ci}/{len(comps)})", ""]
        else:
            lines += ["", "D is descriptive: no verdict.", ""]
    (out / "confirmatory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "confirmatory.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
