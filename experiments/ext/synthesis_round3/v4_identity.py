"""Descriptive reproducibility check after the P4-H2 run (docs/ext/synthesis_round3.md, section 3.6).

Bug E1 (built-in seeds follow the cell position) is not fixed. The plan predicts:
  * tolerant_v4 rows of ext_auto3fix_p4h2_auto3 (P2 config 1) equal those of ext_v51fix_p4h2 (P1) in every
    shared (topology, replicate, T, kind, rate) cell, clean scenario, non-GES;
  * tolerant_v4 and tolerant_v5_1 rows of ext_baselines3_p4h2 (P7) equal those of P1 at T80/150 missing.
A mismatch is a reproducibility finding to disclose; it never changes any verdict (every confirmatory test
pairs rows within its own run).

Usage: python experiments/ext/synthesis_round3/v4_identity.py [--p1 RUN] [--p2 RUN] [--p7 RUN] [--out DIR]
(defaults are the P4-H2 run names; pass D-07 run names to self-test).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT")
FIELDS = ("status", "iscore_nonnull_mean", "n_covered_nonnull", "n_nonnull", "info_c_T")


def load(run: str, method: str) -> dict:
    out = {}
    p = REPO / "results" / run / "runs.jsonl"
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        r = json.loads(line)
        if r.get("method") != method or r.get("scenario", "clean") != "clean" or r.get("kind") == "ges":
            continue
        key = (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
        out[key] = r
    return out


def same(a: dict, b: dict) -> bool:
    for f in FIELDS:
        x, y = a.get(f), b.get(f)
        if isinstance(x, float) and isinstance(y, float):
            if abs(x - y) > 1e-8:
                return False
        elif x != y:
            return False
    return True


def compare(ref_run: str, run: str, method: str) -> dict:
    a, b = load(ref_run, method), load(run, method)
    shared = sorted(set(a) & set(b))
    mism = [k for k in shared if not same(a[k], b[k])]
    return {"ref": ref_run, "run": run, "method": method, "n_ref": len(a), "n_run": len(b),
            "n_shared": len(shared), "n_mismatch": len(mism), "first_mismatches": [list(k) for k in mism[:5]]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p1", default="ext_v51fix_p4h2")
    ap.add_argument("--p2", default="ext_auto3fix_p4h2_auto3")
    ap.add_argument("--p7", default="ext_baselines3_p4h2")
    ap.add_argument("--out", default="results/ext_synthesis_round3_p4h2_v4identity")
    a = ap.parse_args()
    res = [compare(a.p1, a.p2, "tolerant_v4"), compare(a.p1, a.p7, "tolerant_v4"), compare(a.p1, a.p7, "tolerant_v5_1")]
    out = REPO / a.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "v4_identity.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    for r in res:
        print(f"{r['method']}: {r['run']} vs {r['ref']}: shared {r['n_shared']}, mismatch {r['n_mismatch']}")


if __name__ == "__main__":
    main()
