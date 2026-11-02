"""V0 unit test of NG-A v3 (docs/ext/r5ngorient3.md, section 4.1). Pre-registered; runs before any bank run.

2-variable LiNGAM x -> y: x = e1, y = b x + e2, e1 and e2 independent, unit variance, laws from the ORDERED pairs
of the six options {laplace, t5, skewexp+, skewexp-, uniform, gauss} (36 pairs; skewexp+/- have a fixed sign),
b in {0.3, 0.6}, m in {78, 148, 400}, 500 replicates per (cause law, noise law, b, m), seed 70261104.
ng_evidence3(x, y) is called with x the cause. correct = p > 0.5, wrong = p < 0.5 (a closed gate gives p = 0.5
exactly: neither). Conditional wrong rate of a pair = n_wrong / n_gate_open (0 when the gate never opens).
ng_mix weights of a law: laplace 1/4, t5 1/4, skewexp+ 1/8, skewexp- 1/8, uniform 1/4; the mixture over the
25 non-Gaussian ordered pairs weights (cause, noise) by the product. Mixture conditional wrong rate =
sum_w w n_wrong / sum_w w n_open (= P(wrong | gate open) under the ng_mix law mixture).

Criteria (all decisive):
 C1  mixture conditional wrong rate at m 148, b 0.6 <= 0.10;
 C2  every one of the 25 non-Gaussian ordered pairs: conditional wrong rate at m 400, b 0.6 <= 0.30;
 C3  mixture conditional wrong rate at m 400, b 0.6 <= the one at m 148, b 0.6;
 C4  gauss -> gauss, in each of the 6 (b, m): gate-open rate <= 0.12 and mean p in [0.48, 0.52];
 C5  |p(a x, c y) - p(x, y)| <= 1e-9 and identical gate, a, c = exp(U(-3, 3)), on every replicate of every cell.
V0 PASS iff C1-C5 all hold.
Reported only: unconditional rates, every b and m, pairs involving a Gaussian law, negative scale,
antisymmetry p(y, x) = 1 - p(x, y), form/family shares, and v2's ng_evidence on the same samples.

Writes results/ext_r5ngorient3_v0/{v0.json, v0.md}.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "r4ngorient"))
import laws  # noqa: E402
from paper4.ext_r4ngorient import ng_evidence as ng_v2  # noqa: E402
from paper4.ext_r5ngorient3 import ng_evidence3  # noqa: E402

OPTS = [("laplace", 1.0), ("t5", 1.0), ("skewexp", 1.0), ("skewexp", -1.0), ("uniform", 1.0), ("gauss", 1.0)]
W = {("laplace", 1.0): 0.25, ("t5", 1.0): 0.25, ("skewexp", 1.0): 0.125, ("skewexp", -1.0): 0.125,
     ("uniform", 1.0): 0.25}
BS = (0.3, 0.6)
MS = (78, 148, 400)
REPS = 500
SEED = 70261104


def lname(o):
    return o[0] + ("" if o[0] != "skewexp" else ("+" if o[1] > 0 else "-"))


def main():
    t0 = time.perf_counter()
    rng = np.random.default_rng(SEED)
    cells = []
    max_dp, gate_mis, max_dp_neg, max_anti = 0.0, 0, 0.0, 0.0
    for b in BS:
        for m in MS:
            for cz, nz in itertools.product(OPTS, OPTS):
                c = {"cause": lname(cz), "noise": lname(nz), "b": b, "m": m, "ng_pair": cz in W and nz in W,
                     "w": W.get(cz, 0.0) * W.get(nz, 0.0)}
                acc = {"v3": [0, 0, 0, 0.0], "v2": [0, 0, 0, 0.0]}     # open, correct, wrong, sum p
                forms = {}
                for _ in range(REPS):
                    x = laws.sample(rng, cz[0], m, cz[1])
                    e = laws.sample(rng, nz[0], m, nz[1])
                    y = b * x + e
                    a, cc = np.exp(rng.uniform(-3, 3, size=2))
                    ev = ng_evidence3(x, y)
                    ev2 = ng_v2(x, y)
                    for key, r in (("v3", ev), ("v2", ev2)):
                        acc[key][0] += int(r["gate"])
                        acc[key][1] += int(r["p"] > 0.5)
                        acc[key][2] += int(r["p"] < 0.5)
                        acc[key][3] += r["p"]
                    fk = ev["form"] + (":" + ev["fam"] if ev["fam"] else "")
                    forms[fk] = forms.get(fk, 0) + 1
                    evs = ng_evidence3(a * x, cc * y)
                    max_dp = max(max_dp, abs(evs["p"] - ev["p"]))
                    gate_mis += int(evs["gate"] != ev["gate"])
                    evn = ng_evidence3(-a * x, cc * y)
                    max_dp_neg = max(max_dp_neg, abs(evn["p"] - ev["p"]))
                    evr = ng_evidence3(y, x)
                    max_anti = max(max_anti, abs(evr["p"] - (1 - ev["p"])))
                for key in ("v3", "v2"):
                    n_open, n_c, n_w, sp = acc[key]
                    c[key] = {"n_open": n_open, "n_correct": n_c, "n_wrong": n_w, "gate_open": n_open / REPS,
                              "correct": n_c / REPS, "wrong": n_w / REPS, "wrong_cond": n_w / n_open if n_open else 0.0,
                              "correct_cond": n_c / n_open if n_open else None, "mean_p": sp / REPS}
                c["forms_v3"] = forms
                cells.append(c)

    def get(cause, noise, b, m):
        return next(c for c in cells if (c["cause"], c["noise"], c["b"], c["m"]) == (cause, noise, b, m))

    def mix(b, m, key="v3"):
        cs = [c for c in cells if c["ng_pair"] and c["b"] == b and c["m"] == m]
        sw_w = sum(c["w"] * c[key]["n_wrong"] for c in cs)
        sw_o = sum(c["w"] * c[key]["n_open"] for c in cs)
        sw_c = sum(c["w"] * c[key]["n_correct"] for c in cs)
        return {"wrong_cond": sw_w / sw_o if sw_o else 0.0, "wrong_uncond": sw_w / REPS,
                "correct_uncond": sw_c / REPS, "gate_open": sw_o / REPS}

    mixtab = {f"{key}|b{b}|m{m}": mix(b, m, key) for key in ("v3", "v2") for b in BS for m in MS}
    c1v = mixtab["v3|b0.6|m148"]["wrong_cond"]
    c1 = c1v <= 0.10
    ng400 = [c for c in cells if c["ng_pair"] and c["b"] == 0.6 and c["m"] == 400]
    worst = max(ng400, key=lambda c: c["v3"]["wrong_cond"])
    c2 = all(c["v3"]["wrong_cond"] <= 0.30 for c in ng400)
    c3v = (mixtab["v3|b0.6|m400"]["wrong_cond"], c1v)
    c3 = c3v[0] <= c3v[1]
    gs = [get("gauss", "gauss", b, m) for b in BS for m in MS]
    c4 = all(c["v3"]["gate_open"] <= 0.12 and 0.48 <= c["v3"]["mean_p"] <= 0.52 for c in gs)
    c5 = max_dp <= 1e-9 and gate_mis == 0
    PASS = bool(c1 and c2 and c3 and c4 and c5)
    out = {"seed": SEED, "reps": REPS, "seconds": round(time.perf_counter() - t0, 1), "cells": cells, "mixture": mixtab,
           "C1": {"value": c1v, "pass": bool(c1)},
           "C2": {"worst_pair": [worst["cause"], worst["noise"]], "worst_wrong_cond": worst["v3"]["wrong_cond"],
                  "n_over": sum(c["v3"]["wrong_cond"] > 0.30 for c in ng400), "pass": bool(c2)},
           "C3": {"m400": c3v[0], "m148": c3v[1], "pass": bool(c3)},
           "C4": {"cells": [{"b": c["b"], "m": c["m"], "gate_open": c["v3"]["gate_open"], "mean_p": c["v3"]["mean_p"]}
                            for c in gs], "pass": bool(c4)},
           "C5": {"max_abs_dp": max_dp, "gate_mismatches": gate_mis, "pass": bool(c5)},
           "reported": {"max_abs_dp_negative_scale": max_dp_neg, "max_antisymmetry_error": max_anti},
           "PASS": PASS}
    res = ROOT / "results" / "ext_r5ngorient3_v0"
    res.mkdir(parents=True, exist_ok=True)
    (res / "v0.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    ok = lambda f: "ĐẠT" if f else "KHÔNG ĐẠT"  # noqa: E731
    L = ["# V0: unit test NG-A v3 (sinh bởi experiments/ext/r5ngorient3/v0_unit_test.py)", "",
         f"500 rep mỗi ô, seed {SEED}, {out['seconds']} s. Sai chiều có điều kiện = n(p < 0.5) / n(gate mở). "
         "Hỗn hợp ng_mix: trọng số laplace 1/4, t5 1/4, skewexp+ 1/8, skewexp− 1/8, uniform 1/4, tích theo (cause, noise).", "",
         "## Tiêu chí (quyết định)", "",
         f"- C1 sai chiều có điều kiện, hỗn hợp ng_mix, m 148, b 0.6 = {c1v:.4f} (≤ 0.10) -> {ok(c1)}",
         f"- C2 cặp non-Gaussian tệ nhất ở m 400, b 0.6: {worst['cause']} → {worst['noise']} = "
         f"{worst['v3']['wrong_cond']:.4f} (≤ 0.30); số cặp vượt: {out['C2']['n_over']}/25 -> {ok(c2)}",
         f"- C3 hỗn hợp m 400 = {c3v[0]:.4f} ≤ m 148 = {c3v[1]:.4f} -> {ok(c3)}",
         "- C4 gauss → gauss: " + "; ".join(f"b {c['b']} m {c['m']}: gate {c['v3']['gate_open']:.3f}, mean p {c['v3']['mean_p']:.3f}"
                                           for c in gs) + f" -> {ok(c4)}",
         f"- C5 max |Δp| thang dương = {max_dp:.2e}, gate lệch {gate_mis} -> {ok(c5)}",
         f"- Báo thêm: max |Δp| thang âm = {max_dp_neg:.2e}; max |p(y,x) − (1 − p(x,y))| = {max_anti:.2e}",
         f"- **V0: {'PASS' if PASS else 'FAIL'}**", "",
         "## Hỗn hợp ng_mix theo b, m (v3 và v2 trên cùng mẫu; v2 chỉ để so sánh)", "",
         "| bản | b | m | gate mở | đúng (không điều kiện) | sai (không điều kiện) | sai có điều kiện |", "|---|---|---|---|---|---|---|"]
    for key in ("v3", "v2"):
        for b in BS:
            for m in MS:
                t = mixtab[f"{key}|b{b}|m{m}"]
                L.append(f"| {key} | {b} | {m} | {t['gate_open']:.3f} | {t['correct_uncond']:.3f} | {t['wrong_uncond']:.3f} | "
                         f"{t['wrong_cond']:.3f} |")
    L += ["", "## Từng cặp law có thứ tự", "",
          "| cause | noise | b | m | v3 gate mở | v3 đúng | v3 sai | v3 sai có đk | v3 mean p | v2 sai có đk | dạng v3 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        fm = ", ".join(f"{k} {v}" for k, v in sorted(c["forms_v3"].items()))
        L.append(f"| {c['cause']} | {c['noise']} | {c['b']} | {c['m']} | {c['v3']['gate_open']:.3f} | {c['v3']['correct']:.3f} | "
                 f"{c['v3']['wrong']:.3f} | {c['v3']['wrong_cond']:.3f} | {c['v3']['mean_p']:.3f} | {c['v2']['wrong_cond']:.3f} | {fm} |")
    (res / "v0.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
