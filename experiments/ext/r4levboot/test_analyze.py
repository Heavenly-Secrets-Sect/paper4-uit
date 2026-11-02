"""Known-truth tests of analyze.py (synthetic rows; no data bank touched).

Run: python experiments/ext/r4levboot/test_analyze.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as A  # noqa: E402


def row(m, topo, rep, T, kind, rate, IS, cov, nn=40, status="ok", raw=None):
    r = {"method": m, "status": status, "topology": topo, "replicate": rep, "T": T, "kind": kind, "rate": rate}
    if status == "ok":
        r.update({"iscore_nonnull_mean": IS, "n_covered_nonnull": cov, "n_nonnull": nn, "width_kept": 1.0})
        if raw is not None:
            r.update({"raw_n_covered_nonnull": raw, "raw_iscore_nonnull_mean": IS, "raw_width_kept": 1.0})
    return r


def main():
    ok = True
    # T1 Holm: classic example
    rej = A.holm([0.01, 0.04, 0.03, 0.005], alpha=0.05)
    ok &= rej == [True, False, False, True]
    print("T1 holm", rej)
    # T2 paired: constant difference -1 in every unit -> est -1, CI [-1, -1], p minimal
    rows = []
    for t in range(20):
        for rp in range(3):
            rows += [row("ref", f"t{t}", rp, 40, "missing", 0.2, 5.0, 38, raw=36),
                     row("arm", f"t{t}", rp, 40, "missing", 0.2, 4.0, 38, raw=38)]
    C = A.Cells(rows)
    p = C.paired("arm", "ref", (40, "missing", 0.2))
    ok &= abs(p["est"] + 1) < 1e-12 and abs(p["lo"] + 1) < 1e-12 and p["p2"] <= 2 / (A.B + 1) + 1e-12 and p["n"] == 60
    print("T2 paired", p)
    # T3 raw coverage difference: (38 - 36) / 40 = 0.05
    d = C.raw_cov_diff("arm", "ref", (40, "missing", 0.2))
    ok &= abs(d["est"] - 0.05) < 1e-12
    print("T3 raw diff", d)
    # T4 ITT coverage: one failed arm run counts its 40 non-null pairs as uncovered
    rows2 = list(rows)
    rows2 = [r for r in rows2 if not (r["method"] == "arm" and r["topology"] == "t0" and r["replicate"] == 0)]
    rows2.append(row("arm", "t0", 0, 40, "missing", 0.2, None, None, status="bootstrap_failed"))
    s = A.Cells(rows2).stats("arm", (40, "missing", 0.2))
    ok &= s["fail"] == 1 and abs(s["cov_itt"] - 38 * 59 / 2400) < 1e-12
    print("T4 itt", s["fail"], s["cov_itt"], 38 * 59 / 2400)
    # T5 symmetric noise: p two-sided not small
    rng = np.random.default_rng(0)
    rows3 = []
    for t in range(20):
        e = rng.normal()
        rows3 += [row("ref", f"t{t}", 0, 80, "none", 0.0, 3.0, 38), row("arm", f"t{t}", 0, 80, "none", 0.0, 3.0 + e, 38)]
    p3 = A.Cells(rows3).paired("arm", "ref", (80, "none", 0.0))
    ok &= p3["p2"] > 0.05
    print("T5 null p", p3)
    print("ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
