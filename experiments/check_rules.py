"""Apply the decision rules of docs/decision_rules.md to a finished run.

Run:  python experiments/check_rules.py results/<name> --module tolerant
Prints each condition with the numbers behind it and the verdict (retained / rejected).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

LENIENT, STRICT = 0.90, 0.93


def load(run_dir: Path) -> list[dict]:
    with open(run_dir / "runs.jsonl", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def cell_stats(rows):
    """(T, kind, rate, method) -> pooled coverage, mean interval score, per-topology paired IS."""
    groups = defaultdict(list)
    for r in rows:
        if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None:
            groups[(r["T"], r["kind"], r["rate"], r["method"])].append(r)
    stats = {}
    for key, g in groups.items():
        cov = sum(r["n_covered_nonnull"] for r in g) / max(1, sum(r["n_nonnull"] for r in g))
        stats[key] = {"cov": cov, "is": float(np.mean([r["iscore_nonnull_mean"] for r in g])), "rows": g}
    return stats


def paired_upper(stats, key_a, key_b, n_resample=2000, seed=0) -> tuple[float, float]:
    """Mean IS difference a - b and the upper end of its 95% topology-clustered bootstrap interval."""
    a = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in stats[key_a]["rows"]}
    b = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in stats[key_b]["rows"]}
    by_topo = defaultdict(list)
    for unit in a.keys() & b.keys():
        by_topo[unit[0]].append(a[unit] - b[unit])
    topos = list(by_topo)
    rng = np.random.default_rng(seed)
    est = float(np.mean([d for t in topos for d in by_topo[t]]))
    boots = [np.mean([d for i in rng.choice(len(topos), len(topos)) for d in by_topo[topos[i]]])
             for _ in range(n_resample)]
    return est, float(np.quantile(boots, 0.975))


def passes(stats, T, kind, rate, module, threshold) -> tuple[bool, str]:
    key, ref = (T, kind, rate, module), (T, kind, rate, "plugin")
    if key not in stats or ref not in stats:
        return False, "missing"
    est, upper = paired_upper(stats, key, ref)
    ok = stats[key]["cov"] >= threshold and upper < 0
    return ok, f"cov {stats[key]['cov']:.3f}, dIS vs plugin {est:+.2f} (upper {upper:+.2f})"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir")
    parser.add_argument("--module", default="tolerant")
    args = parser.parse_args(argv)
    stats = cell_stats(load(Path(args.run_dir)))
    m = args.module
    Ts = sorted({k[0] for k in stats})
    damaged = sorted({(k[1], k[2]) for k in stats if k[1] != "none"})

    print(f"# Decision rules for `{m}` on {args.run_dir}\n")
    print("## Condition 1: passes missing-0.2 and reversed-0.2 at T = 80 and 150 (lenient 0.90; strict 0.93 shown)")
    c1 = True
    for T in (80, 150):
        for kind in ("missing", "reversed"):
            ok, msg = passes(stats, T, kind, 0.2, m, LENIENT)
            strict, _ = passes(stats, T, kind, 0.2, m, STRICT)
            c1 &= ok
            print(f"- T={T} {kind}-0.2: {'PASS' if ok else 'FAIL'} (strict {'pass' if strict else 'fail'}); {msg}")

    print("\n## Condition 2: undamaged IS no worse than plugin by more than 10%")
    c2 = True
    for T in Ts:
        a, b = stats.get((T, "none", 0.0, m)), stats.get((T, "none", 0.0, "plugin"))
        if not a or not b:
            continue
        ratio = a["is"] / b["is"]
        c2 &= ratio <= 1.10
        print(f"- T={T}: IS {a['is']:.2f} vs plugin {b['is']:.2f} (ratio {ratio:.2f}) {'ok' if ratio <= 1.10 else 'FAIL'}")

    print("\n## Condition 3: at some T, lower mean IS than lp_allpast on at least half of the damaged cells")
    c3 = False
    for T in Ts:
        wins = total = 0
        for kind, rate in damaged:
            a, b = stats.get((T, kind, rate, m)), stats.get((T, kind, rate, "lp_allpast"))
            if a and b:
                total += 1
                wins += a["is"] < b["is"]
        if total:
            c3 |= wins >= total / 2
            print(f"- T={T}: wins {wins}/{total}")
        else:
            print(f"- T={T}: lp_allpast infeasible, not counted")

    verdict = "RETAINED" if (c1 and c2 and c3) else "REJECTED"
    print(f"\n**Verdict: {verdict}** (condition 1 {'met' if c1 else 'not met'}, 2 {'met' if c2 else 'not met'}, 3 {'met' if c3 else 'not met'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
