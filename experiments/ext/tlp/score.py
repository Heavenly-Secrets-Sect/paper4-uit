"""Apply the pre-registered descriptive rules of docs/ext/tlp.md to results/<name>/runs.jsonl.

R1: tolerant_v4 beats targeted_lp in a damaged cell if v4 pooled coverage >= 0.90 and the upper
    95% CI bound (topology-clustered bootstrap, 1000 resamples, as paired_table) of the mean
    paired interval-score difference (v4 - targeted_lp) is < 0.
R1-rev, R2 (vs targeted_lp_cal), R3 (undamaged), and descriptive TLP vs plugin / lp_allpast.
Usage: python experiments/ext/tlp/score.py results/ext_tlp_eval
"""
import json
import sys
from collections import defaultdict

import numpy as np


def load(path):
    return [json.loads(line) for line in open(f"{path}/runs.jsonl", encoding="utf-8")]


def pooled_cov(rows, m, T, kind, rate):
    g = [r for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind and r["rate"] == rate
         and r["status"] == "ok"]
    d = sum(r["n_nonnull"] for r in g)
    return (sum(r["n_covered_nonnull"] for r in g) / d if d else float("nan")), len(g)


def mean_is(rows, m, T, kind, rate):
    v = [r["iscore_nonnull_mean"] for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind
         and r["rate"] == rate and r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None]
    return float(np.mean(v)) if v else float("nan")


def paired(rows, a, b, T, kind, rate, n_resample=1000, seed=0):
    idx = {(r["topology"], r["replicate"], r["method"]): r for r in rows
           if r["T"] == T and r["kind"] == kind and r["rate"] == rate and r["status"] == "ok"
           and r.get("iscore_nonnull_mean") is not None}
    diffs = defaultdict(list)
    for (topo, rep, m), r in idx.items():
        if m == a and (topo, rep, b) in idx:
            diffs[topo].append(r["iscore_nonnull_mean"] - idx[(topo, rep, b)]["iscore_nonnull_mean"])
    if not diffs:
        return None
    topos = list(diffs)
    est = np.mean([v for t in topos for v in diffs[t]])
    rng = np.random.default_rng(seed)
    boots = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in diffs[topos[i]]])
             for _ in range(n_resample)]
    lo, hi = np.quantile(boots, (0.025, 0.975))
    return est, lo, hi, sum(len(v) for v in diffs.values())


def mean_info(rows, m, T, kind, rate, key):
    v = [r[key] for r in rows if r["method"] == m and r["T"] == T and r["kind"] == kind and r["rate"] == rate
         and r["status"] == "ok" and r.get(key) is not None]
    return float(np.mean(v)) if v else float("nan")


def main(path):
    rows = load(path)
    Ts = sorted({r["T"] for r in rows})
    damaged = sorted({(r["kind"], r["rate"]) for r in rows if r["kind"] != "none"})
    out = []
    for ref in ("targeted_lp", "targeted_lp_cal"):
        if not any(r["method"] == ref for r in rows):
            continue
        out.append(f"\n## tolerant_v4 vs {ref}\n")
        out.append("| T | damage | rate | cov v4 | cov ref | IS v4 | IS ref | diff v4-ref [95% CI] | verdict |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        wins, losses = defaultdict(int), defaultdict(int)
        for T in Ts:
            for kind, rate in [("none", 0.0)] + damaged:
                cv, _ = pooled_cov(rows, "tolerant_v4", T, kind, rate)
                cr, _ = pooled_cov(rows, ref, T, kind, rate)
                p = paired(rows, "tolerant_v4", ref, T, kind, rate)
                if p is None:
                    verdict, ptxt = "n/a", "–"
                else:
                    est, lo, hi, npair = p
                    ptxt = f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}]"
                    if kind == "none":
                        verdict = "(undamaged, R3)"
                    elif cv >= 0.90 and hi < 0:
                        verdict = "v4 wins"; wins[kind] += 1; wins[T] += 1; wins["all"] += 1
                    elif cr >= 0.90 and lo > 0:
                        verdict = "ref wins"; losses[kind] += 1; losses[T] += 1; losses["all"] += 1
                    else:
                        verdict = "tie"
                out.append(f"| {T} | {kind} | {rate:.1f} | {cv:.3f} | {cr:.3f} | {mean_is(rows, 'tolerant_v4', T, kind, rate):.2f} | "
                           f"{mean_is(rows, ref, T, kind, rate):.2f} | {ptxt} | {verdict} |")
        out.append(f"\nv4 wins: {wins['all']}/{len(Ts) * len(damaged)} damaged cells; "
                   + ", ".join(f"{k}: {wins[k]}" for k in ["extra", "missing", "reversed"] + Ts)
                   + f". {ref} wins: {losses['all']} (" + ", ".join(f"{k}: {losses[k]}" for k in ["extra", "missing", "reversed"] + Ts) + ")")
    out.append("\n## targeted_lp against its components (mean paired IS difference, 95% CI) and weight on LP\n")
    out.append("| T | damage | rate | cov TLP | IS TLP | TLP - plugin | TLP - lp_allpast | mean v (h>=1) | p_lp |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for T in Ts:
        for kind, rate in [("none", 0.0)] + damaged:
            c, _ = pooled_cov(rows, "targeted_lp", T, kind, rate)
            cells = []
            for b in ("plugin", "lp_allpast"):
                p = paired(rows, "targeted_lp", b, T, kind, rate)
                cells.append("–" if p is None else f"{p[0]:+.2f} [{p[1]:+.2f}, {p[2]:+.2f}]")
            out.append(f"| {T} | {kind} | {rate:.1f} | {c:.3f} | {mean_is(rows, 'targeted_lp', T, kind, rate):.2f} | "
                       f"{cells[0]} | {cells[1]} | {mean_info(rows, 'targeted_lp', T, kind, rate, 'info_v_mean'):.3f} | "
                       f"{mean_info(rows, 'targeted_lp', T, kind, rate, 'info_p_lp'):.1f} |")
    shr = [r.get("info_var_shrunk") for r in rows if r["method"] == "targeted_lp" and r["status"] == "ok"]
    out.append(f"\nBootstrap VAR shrunk to radius 0.98 in {sum(bool(s) for s in shr)}/{len(shr)} targeted_lp runs.")
    for T in Ts:
        s = [r.get("info_var_shrunk") for r in rows if r["method"] == "targeted_lp" and r["status"] == "ok" and r["T"] == T]
        out.append(f"- T = {T}: {sum(bool(x) for x in s)}/{len(s)}")
    txt = "\n".join(out)
    print(txt)
    open(f"{path}/tlp_rules.md", "w", encoding="utf-8").write("# Rules of docs/ext/tlp.md applied\n" + txt + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
