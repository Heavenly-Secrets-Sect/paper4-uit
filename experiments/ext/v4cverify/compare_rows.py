"""R3-7 (v4cverify): row-by-row comparison of the 2-unit reruns (--workers 3) with the
--workers 6 run results/ext_v4c_eval, and of the two interpreters with each other.

Usage: python experiments/ext/v4cverify/compare_rows.py
Writes results/ext_v4cverify_recompute/compare_rows.txt (and .json).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
OUT = R / "ext_v4cverify_recompute"
KEY = ("method", "topology", "replicate", "T", "kind", "rate", "scenario")


def load(run):
    d = {}
    for line in open(R / run / "runs.jsonl", encoding="utf-8"):
        r = json.loads(line)
        d[tuple(r[k] for k in KEY)] = r
    return d


def cmp_rows(a: dict, b: dict) -> dict:
    """a: rerun rows; b: reference rows. Every key of a must exist in b; every field compared."""
    n = identical = 0
    missing = []
    max_abs = max_rel = 0.0
    worst = None
    diff_fields = {}
    for k, ra in a.items():
        rb = b.get(k)
        if rb is None:
            missing.append(k)
            continue
        n += 1
        if ra == rb:
            identical += 1
            continue
        for f in set(ra) | set(rb):
            va, vb = ra.get(f), rb.get(f)
            if va == vb:
                continue
            diff_fields[f] = diff_fields.get(f, 0) + 1
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
                if isinstance(va, float) and isinstance(vb, float) and math.isnan(va) and math.isnan(vb):
                    continue
                ad = abs(va - vb)
                rd = ad / max(abs(vb), 1e-300)
                if ad > max_abs:
                    max_abs, worst = ad, (k, f, va, vb)
                max_rel = max(max_rel, rd)
            else:
                worst = worst or (k, f, va, vb)
    return {"n_compared": n, "n_identical": identical, "n_missing_in_ref": len(missing),
            "fields_differing": diff_fields, "max_abs_diff": max_abs, "max_rel_diff": max_rel,
            "worst": [str(x) for x in worst] if worst else None}


def cmp_cal(a, b):
    ca = json.loads((R / a / "calibration.json").read_text())
    cb = json.loads((R / b / "calibration.json").read_text())
    keys = set(ca) | set(cb)
    diff = {k: [ca.get(k), cb.get(k)] for k in sorted(keys) if ca.get(k) != cb.get(k)}
    return {"n_keys": len(keys), "n_diff": len(diff), "diff": diff,
            "bytes_identical": (R / a / "calibration.json").read_bytes() == (R / b / "calibration.json").read_bytes()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref = load("ext_v4c_eval")
    res = {}
    runs = [r for r in ("ext_v4cverify_rerun_w3", "ext_v4cverify_rerun_w3_clt") if (R / r / "runs.jsonl").exists()]
    for run in runs:
        rows = load(run)
        man = json.loads((R / run / "manifest.json").read_text())
        res[run] = {"n_rows": len(rows), "seconds": man["seconds"],
                    "units": sorted({(k[1], k[2]) for k in rows}),
                    "vs_ext_v4c_eval_rows": cmp_rows(rows, ref),
                    "vs_ext_v4c_eval_calibration": cmp_cal(run, "ext_v4c_eval")}
        sk_a = [json.loads(l) for l in open(R / run / "skeletons.jsonl")]
        sk_b = [json.loads(l) for l in open(R / "ext_v4c_eval" / "skeletons.jsonl")]
        sk_b = [s for s in sk_b if (s["topology"], s["replicate"]) in {(x["topology"], x["replicate"]) for x in sk_a}]
        res[run]["skeletons_identical"] = sk_a == sk_b
    if len(runs) == 2:
        res["conda_vs_clt_rows"] = cmp_rows(load(runs[1]), load(runs[0]))
        res["conda_vs_clt_calibration"] = cmp_cal(runs[1], runs[0])
    (OUT / "compare_rows.json").write_text(json.dumps(res, indent=1, default=str))
    lines = ["# R3-7 row comparison (experiments/ext/v4cverify/compare_rows.py)"]
    for k, v in res.items():
        lines.append(f"\n## {k}\n{json.dumps(v, indent=1, default=str)}")
    (OUT / "compare_rows.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
