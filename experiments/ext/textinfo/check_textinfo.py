"""Apply the pre-registered rule of docs/ext/textinfo.md (section 5) to the textinfo runs.

Run:  python experiments/ext/textinfo/check_textinfo.py results/ext_textinfo_t80 results/ext_textinfo_t150
Writes results/ext_textinfo_verdict/verdict.md and prints it.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DAMAGED = [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
CELLS = [("none", 0.0)] + DAMAGED
REF = "tolerant_v4"


def load(dirs):
    rows = []
    for d in dirs:
        with open(Path(d) / "runs.jsonl", encoding="utf-8") as fh:
            rows += [json.loads(line) for line in fh]
    return rows


def index(rows):
    idx = {}
    for r in rows:
        if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None:
            idx[(r["method"], r["T"], r["kind"], r["rate"], r["topology"], r["replicate"])] = r
    return idx


def cell_stats(rows, method, T, kind, rate):
    g = [r for r in rows if r["method"] == method and r["T"] == T and r["kind"] == kind and r["rate"] == rate
         and r["status"] == "ok"]
    if not g:
        return None
    cov = sum(r["n_covered_nonnull"] for r in g) / sum(r["n_nonnull"] for r in g)
    return {"cov": cov, "IS": float(np.mean([r["iscore_nonnull_mean"] for r in g])), "n": len(g)}


def paired(idx, m, ref, T, kind, rate, n_resample=1000, seed=0):
    diffs = defaultdict(list)
    for (meth, t, k, r, topo, rep), row in idx.items():
        if meth == m and t == T and k == kind and r == rate:
            other = idx.get((ref, t, k, r, topo, rep))
            if other:
                diffs[topo].append(row["iscore_nonnull_mean"] - other["iscore_nonnull_mean"])
    if not diffs:
        return None
    topos = list(diffs)
    est = float(np.mean([v for t in topos for v in diffs[t]]))
    rng = np.random.default_rng(seed)
    boots = [np.mean([v for i in rng.choice(len(topos), len(topos)) for v in diffs[topos[i]]])
             for _ in range(n_resample)]
    lo, hi = np.quantile(boots, (0.025, 0.975))
    return est, float(lo), float(hi)


def verdict(rows, idx, family, Ts):
    lines = [f"### `{family}`", "", "Condition 1 (a = 0.9): cells with upper CI < 0 and coverage >= 0.90.", "",
             "| T | damage | rate | cov | IS | v4 IS | diff vs v4 [95% CI] | win |", "|---|---|---|---|---|---|---|---|"]
    wins = 0
    for T in Ts:
        for kind, rate in DAMAGED:
            m = f"{family}@a0.9"
            s, s0 = cell_stats(rows, m, T, kind, rate), cell_stats(rows, REF, T, kind, rate)
            p = paired(idx, m, REF, T, kind, rate)
            win = bool(s and p and p[2] < 0 and s["cov"] >= 0.90)
            wins += win
            lines.append(f"| {T} | {kind} | {rate} | {s['cov']:.3f} | {s['IS']:.3f} | {s0['IS']:.3f} | "
                         f"{p[0]:+.3f} [{p[1]:+.3f}, {p[2]:+.3f}] | {'yes' if win else 'no'} |")
    c1 = wins >= 6
    lines += ["", f"Wins: **{wins} / {len(Ts) * len(DAMAGED)}** (need >= 6) -> condition 1 {'MET' if c1 else 'NOT met'}.",
              "", "Condition 2 (a = 0.5): IS ratio to v4 in every cell <= 1.05.", "",
              "| T | damage | rate | IS a=0.5 | v4 IS | ratio | ok |", "|---|---|---|---|---|---|---|"]
    c2 = True
    for T in Ts:
        for kind, rate in CELLS:
            s, s0 = cell_stats(rows, f"{family}@a0.5", T, kind, rate), cell_stats(rows, REF, T, kind, rate)
            ratio = s["IS"] / s0["IS"]
            ok = ratio <= 1.05
            c2 &= ok
            lines.append(f"| {T} | {kind} | {rate} | {s['IS']:.3f} | {s0['IS']:.3f} | {ratio:.3f} | {'yes' if ok else 'NO'} |")
    lines += ["", f"Condition 2 {'MET' if c2 else 'NOT met'}.", "",
              f"**Verdict for `{family}`: {'RETAINED' if c1 and c2 else 'REJECTED'}.**", ""]
    return lines, c1 and c2


def descriptive(rows, idx, Ts, qualities):
    lines = ["## Descriptive (not part of the verdict)", "",
             "### S1: text vs no text (`textinfo@a0.9` minus `textinfo_null`), missing and reversed cells", "",
             "| T | damage | rate | diff [95% CI] |", "|---|---|---|---|"]
    n1 = 0
    for T in Ts:
        for kind, rate in DAMAGED[2:]:
            p = paired(idx, "textinfo@a0.9", "textinfo_null", T, kind, rate)
            if p:
                n1 += p[2] < 0
                lines.append(f"| {T} | {kind} | {rate} | {p[0]:+.3f} [{p[1]:+.3f}, {p[2]:+.3f}] |")
    lines += ["", f"Cells with upper CI < 0: {n1} / {len(Ts) * 4}.", "",
              "### S2: mean IS difference vs v4 by text quality (coverage in brackets)", "",
              "| T | damage | rate | method | " + " | ".join(f"a={a}" for a in qualities) + " | monotone |",
              "|---|---|---|---|" + "---|" * (len(qualities) + 1)]
    for fam in ("textinfo", "textinfo_all"):
        for T in Ts:
            for kind, rate in DAMAGED[2:]:
                vals, cells = [], []
                for a in qualities:
                    p = paired(idx, f"{fam}@a{a}", REF, T, kind, rate)
                    s = cell_stats(rows, f"{fam}@a{a}", T, kind, rate)
                    vals.append(p[0])
                    cells.append(f"{p[0]:+.3f} ({s['cov']:.3f})")
                mono = all(vals[i + 1] <= vals[i] for i in range(len(vals) - 1))
                lines.append(f"| {T} | {kind} | {rate} | {fam} | " + " | ".join(cells) + f" | {'yes' if mono else 'no'} |")
    lines += ["", "### `textinfo_null` (targeted opening, no text) vs v4", "",
              "| T | damage | rate | cov | diff vs v4 [95% CI] |", "|---|---|---|---|---|"]
    for T in Ts:
        for kind, rate in DAMAGED[2:]:
            p = paired(idx, "textinfo_null", REF, T, kind, rate)
            s = cell_stats(rows, "textinfo_null", T, kind, rate)
            lines.append(f"| {T} | {kind} | {rate} | {s['cov']:.3f} | {p[0]:+.3f} [{p[1]:+.3f}, {p[2]:+.3f}] |")
    return lines


def main(argv):
    dirs = argv or [str(ROOT / "results/ext_textinfo_t80"), str(ROOT / "results/ext_textinfo_t150")]
    rows = load(dirs)
    idx = index(rows)
    Ts = sorted({r["T"] for r in rows})
    qualities = sorted({float(r["method"].split("@a")[1]) for r in rows if "@a" in r["method"]})
    out = ["# ext_textinfo verdict (pre-registered rule, docs/ext/textinfo.md section 5)", "",
           f"Inputs: {', '.join(dirs)}. Reference `{REF}`. Paired CIs resample topologies (1000 draws).", ""]
    for fam in ("textinfo", "textinfo_all"):
        lines, _ = verdict(rows, idx, fam, Ts)
        out += lines
    out += descriptive(rows, idx, Ts, qualities)
    text = "\n".join(out) + "\n"
    d = ROOT / "results" / "ext_textinfo_verdict"
    d.mkdir(parents=True, exist_ok=True)
    (d / "verdict.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
