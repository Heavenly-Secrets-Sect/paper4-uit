"""Apply the pre-registered B1 rule (docs/ext/gate.md, section 4) to results/ext_gate_auto3.

Run: python experiments/ext/gate/check_gate.py results/ext_gate_auto3
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main(path: str) -> int:
    rows = [json.loads(line) for line in open(Path(path) / "runs.jsonl", encoding="utf-8")]
    g = defaultdict(list)
    for r in rows:
        g[(r["T"], r["kind"], r["rate"], r["method"])].append(r)

    def cov(T, k, rt, m):
        ok = [r for r in g[(T, k, rt, m)] if r["status"] == "ok"]
        return sum(r["n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok)

    def IS(T, k, rt, m):
        return float(np.mean([r["iscore_nonnull_mean"] for r in g[(T, k, rt, m)] if r["status"] == "ok"]))

    def n_ok(T, k, rt, m):
        return f"{sum(r['status'] == 'ok' for r in g[(T, k, rt, m)])}/{len(g[(T, k, rt, m)])}"

    A = "tolerant_auto3"
    cells = [("none", 0.0), ("extra", 0.2), ("extra", 0.5), ("missing", 0.2), ("missing", 0.5),
             ("reversed", 0.2), ("reversed", 0.5), ("ges", 0.0)]
    print("## Gate open rate and damage estimate per cell (tolerant_auto3)\n")
    print("| T | cell | ok | gate open | mean n_repair | mean true missing (GES) |")
    print("|---|---|---|---|---|---|")
    for T in (40, 80, 150):
        for k, rt in cells:
            rs = [r for r in g[(T, k, rt, A)] if r["status"] == "ok"]
            op = np.mean([r["info_state"] == "open" for r in rs])
            nr = np.mean([r["info_n_repair"] for r in rs])
            tm = np.mean([r["true_missing"] for r in rs]) if k == "ges" else float("nan")
            print(f"| {T} | {k} {rt} | {n_ok(T, k, rt, A)} | {op:.2f} | {nr:.2f} | {tm:.1f} |")

    print("\n## Rule\n")
    c1 = []
    for T in (80, 150):
        for k in ("missing", "reversed"):
            for rt in (0.2, 0.5):
                c = cov(T, k, rt, A)
                c1.append(c >= 0.90)
                print(f"C1 T={T} {k} {rt}: coverage {c:.3f} {'ok' if c >= 0.90 else 'FAIL'}")
    c2 = {}
    for T in (40, 80, 150):
        a, v = IS(T, "none", 0.0, A), IS(T, "none", 0.0, "tolerant_v4")
        c2[T] = a / v <= 1.35
        print(f"C2 T={T} none: IS {a:.3f} vs v4 {v:.3f}, ratio {a / v:.3f} {'ok' if c2[T] else 'FAIL'}")
    c3 = []
    for T in (80, 150):
        c, a, v = cov(T, "ges", 0.0, A), IS(T, "ges", 0.0, A), IS(T, "ges", 0.0, "tolerant_v4")
        ok = c >= 0.90 and a <= 1.10 * v
        c3.append(ok)
        print(f"C3 T={T} ges: coverage {c:.3f}, IS {a:.3f} vs bound {1.10 * v:.3f} (v4 {v:.3f}) {'ok' if ok else 'FAIL'}")
    strict = all(c1) and all(c2.values()) and all(c3)
    lenient = all(c1) and c2[80] and c2[150] and all(c3)
    print(f"\nC1 {'holds' if all(c1) else 'fails'}; C2 (T=40,80,150) {'holds' if all(c2.values()) else 'fails'} "
          f"[T=80,150 only: {'holds' if c2[80] and c2[150] else 'fails'}]; C3 {'holds' if all(c3) else 'fails'}")
    print(f"VERDICT (pre-registered strict reading): {'RETAINED' if strict else 'REJECTED'}; "
          f"lenient reading (C2 at T=80,150): {'retained' if lenient else 'rejected'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
