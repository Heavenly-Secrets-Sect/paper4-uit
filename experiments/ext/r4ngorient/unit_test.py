"""Unit test gate of r4ngorient (docs/ext/r4ngorient.md, section 5.1). Run before any bank run.

2-variable LiNGAM x -> y (x = e1, y = b x + e2, e1, e2 iid of one unit-variance law; skewexp draws
its sign per variable and replicate), b in {0.3, 0.6}, m in {38, 78, 148}, 500 replicates, seed
20261104. Calls paper4.ext_r4ngorient.ng_evidence(x, y) with x the cause.

(i)   correct-direction rate = share of p > 0.5 (closed gate = not correct) >= 0.80 at m 148, b 0.6
      for laplace and skewexp;
(ii)  gauss: gate-open rate <= 0.12 and mean p in [0.48, 0.52] in every (b, m);
(iii) |p(a x, c y) - p(x, y)| <= 1e-9 and same gate for a, c = exp(U(-3, 3)) on every replicate.
Reported only: negative scales, antisymmetry p(y, x) = 1 - p(x, y), t10, gate-open rate and
correct rate given an open gate.

Writes results/ext_r4ngorient_unittest/{unit_test.json, unit_test.md}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import laws  # noqa: E402
from paper4.ext_r4ngorient import ng_evidence  # noqa: E402

LAWS = ("laplace", "t5", "skewexp", "uniform", "gauss", "t10")
BS = (0.3, 0.6)
MS = (38, 78, 148)
REPS = 500


def main():
    rng = np.random.default_rng(20261104)
    out = {"cells": []}
    max_dp_pos, max_dp_neg, max_anti, gate_mis = 0.0, 0.0, 0.0, 0
    for law in LAWS:
        for b in BS:
            for m in MS:
                ps, gates = [], []
                for _ in range(REPS):
                    s1 = 1.0 if rng.random() < 0.5 else -1.0
                    s2 = 1.0 if rng.random() < 0.5 else -1.0
                    x = laws.sample(rng, law, m, s1)
                    y = b * x + laws.sample(rng, law, m, s2)
                    ev = ng_evidence(x, y)
                    ps.append(ev["p"])
                    gates.append(ev["gate"])
                    a, c = np.exp(rng.uniform(-3, 3, size=2))
                    ev2 = ng_evidence(a * x, c * y)
                    max_dp_pos = max(max_dp_pos, abs(ev2["p"] - ev["p"]))
                    gate_mis += int(ev2["gate"] != ev["gate"])
                    ev3 = ng_evidence(-a * x, c * y)
                    max_dp_neg = max(max_dp_neg, abs(ev3["p"] - ev["p"]))
                    ev4 = ng_evidence(y, x)
                    max_anti = max(max_anti, abs(ev4["p"] - (1 - ev["p"])))
                ps, gates = np.array(ps), np.array(gates)
                cell = {"law": law, "b": b, "m": m, "correct_rate": float(np.mean(ps > 0.5)),
                        "wrong_rate": float(np.mean(ps < 0.5)), "gate_open": float(gates.mean()),
                        "correct_given_open": float(np.mean(ps[gates] > 0.5)) if gates.any() else None,
                        "mean_p": float(ps.mean())}
                out["cells"].append(cell)
    get = lambda law, b, m: next(c for c in out["cells"] if (c["law"], c["b"], c["m"]) == (law, b, m))  # noqa: E731
    r_i = {law: get(law, 0.6, 148)["correct_rate"] for law in ("laplace", "skewexp")}
    ok_i = all(v >= 0.80 for v in r_i.values())
    sign_flip_needed = all(get(l_, 0.6, 148)["correct_rate"] < 0.5 for l_ in ("laplace", "skewexp"))
    gs = [get("gauss", b, m) for b in BS for m in MS]
    ok_ii = all(c["gate_open"] <= 0.12 and 0.48 <= c["mean_p"] <= 0.52 for c in gs)
    ok_iii = max_dp_pos <= 1e-9 and gate_mis == 0
    out.update({"i": {"rates": r_i, "pass": ok_i, "sign_flip_needed": sign_flip_needed},
                "ii": {"cells": gs, "pass": ok_ii},
                "iii": {"max_abs_dp_positive_scale": max_dp_pos, "gate_mismatches": gate_mis, "pass": ok_iii},
                "reported": {"max_abs_dp_negative_scale": max_dp_neg, "max_antisymmetry_error": max_anti},
                "PASS": bool(ok_i and ok_ii and ok_iii)})
    res = ROOT / "results" / "ext_r4ngorient_unittest"
    res.mkdir(parents=True, exist_ok=True)
    (res / "unit_test.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# Unit test gate r4ngorient (sinh bởi experiments/ext/r4ngorient/unit_test.py)", "",
         f"500 rep mỗi ô, seed 20261104. Đúng chiều = p > 0.5 (gate đóng = không đúng).", "",
         "| law | b | m | gate mở | đúng chiều | sai chiều | đúng | gate mở | mean p |", "|---|---|---|---|---|---|---|---|---|"]
    for c in out["cells"]:
        cg = "-" if c["correct_given_open"] is None else f"{c['correct_given_open']:.3f}"
        L.append(f"| {c['law']} | {c['b']} | {c['m']} | {c['gate_open']:.3f} | {c['correct_rate']:.3f} | "
                 f"{c['wrong_rate']:.3f} | {cg} | {c['mean_p']:.3f} |")
    L += ["", f"- (i) đúng chiều ở m 148, b 0.6: {r_i} -> {'ĐẠT' if ok_i else 'KHÔNG ĐẠT'}"
          f"{' (dấu ngược: cần đảo quy ước một lần)' if sign_flip_needed else ''}",
          f"- (ii) Gaussian: gate mở ≤ 0.12 và mean p ∈ [0.48, 0.52] ở cả 6 ô -> {'ĐẠT' if ok_ii else 'KHÔNG ĐẠT'}",
          f"- (iii) max |Δp| thang dương = {max_dp_pos:.2e}, gate lệch {gate_mis} -> {'ĐẠT' if ok_iii else 'KHÔNG ĐẠT'}",
          f"- Báo thêm: max |Δp| thang âm = {max_dp_neg:.2e}; max |p(y,x) − (1 − p(x,y))| = {max_anti:.2e}",
          f"- **Unit test: {'PASS' if out['PASS'] else 'FAIL'}**"]
    (res / "unit_test.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
