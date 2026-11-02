"""D2 (docs/ext/auto3fix.md 1.3): how fragile is the P2 verdict? Descriptive, stored D-07 rows only.

Cluster bootstrap over topologies (2000 resamples, seed 0) of the D-07 dry-run rows
(results/ext_gate_auto3 + results/ext_auto5_a1). The same topology indices are drawn for both runs
(on P4-H2 the two configs also share their 20 topologies). Each resample is ruled with exactly the
corrected rule of check_p4h2_v2.py. Output: results/ext_auto3fix_fragility/{fragility.json, fragility.md}.
Reading: P(CONFIRMED) if P4-H2 were 20 topologies drawn like D-07 and D-07 performance were the
truth -- optimistic (D-07 helped select auto3; no D-07H/D-07/P4-H2 shift; same bootstrap seeds).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_p4h2_v2 as C  # noqa: E402

ROOT = C.ROOT
N, SEED = 2000, 0


def main():
    A = C.build(C.Run(ROOT / "results/ext_gate_auto3"), C.Run(ROOT / "results/ext_auto5_a1"))
    full = C.evaluate(A)
    nt = len(next(iter(A["cov"].values()))["num"])
    rng = np.random.default_rng(SEED)
    n_conf, cond_fail, cell_fail = 0, Counter(), Counter()
    only_c1_rev = 0
    cov_r = []
    for _ in range(N):
        pick = rng.integers(0, nt, nt)
        E = C.evaluate(A, pick)
        n_conf += E["rule_holds"]
        for k, v in E["R"].items():
            cond_fail[k] += not v
        failed_cells = [C.cell_name(ck) for part in ("C1", "C2", "C3", "L1") for ck, x in E[part].items() if not x["ok"]]
        for c in failed_cells:
            cell_fail[c] += 1
        if failed_cells == ["clean|80|reversed|0.5"]:
            only_c1_rev += 1
        cov_r.append(E["C1"][("clean", 80, "reversed", 0.5)]["cov"])
    cov_r = np.array(cov_r)
    J = {"n_boot": N, "seed": SEED, "full_sample_rule_holds": full["rule_holds"],
         "p_confirmed": n_conf / N, "p_fail_condition": {k: cond_fail[k] / N for k in ("C1", "C2", "C3", "L1")},
         "p_fail_cell": {k: v / N for k, v in sorted(cell_fail.items(), key=lambda kv: -kv[1])},
         "p_fail_only_T80_reversed_0.5": only_c1_rev / N,
         "T80_reversed_0.5": {"cov_full": full["C1"][("clean", 80, "reversed", 0.5)]["cov"],
                              "p_cov_le_0.90": float(np.mean(cov_r <= 0.90)),
                              "p_cov_lt_0.90": float(np.mean(cov_r < 0.90)),
                              "q025_q50_q975": [float(x) for x in np.quantile(cov_r, (0.025, 0.5, 0.975))]}}
    out = ROOT / "results" / "ext_auto3fix_fragility"
    out.mkdir(parents=True, exist_ok=True)
    (out / "fragility.json").write_text(json.dumps(J, indent=1), encoding="utf-8")
    L = ["# D2: fragility of the P2 verdict (descriptive; topology bootstrap of stored D-07 rows)", "",
         f"- full sample: {'CONFIRMED' if full['rule_holds'] else 'NOT CONFIRMED'} (corrected rule)",
         f"- P(CONFIRMED) over {N} topology resamples: {J['p_confirmed']:.3f}",
         "- P(condition fails): " + ", ".join(f"{k} {v:.3f}" for k, v in J["p_fail_condition"].items()),
         "- P(cell fails), cells failing in >= 0.5% of resamples: " + ", ".join(f"{k} {v:.3f}" for k, v in J["p_fail_cell"].items() if v >= 0.005),
         f"- P(T80 reversed-0.5 is the only failing cell): {J['p_fail_only_T80_reversed_0.5']:.3f}",
         f"- T80 reversed-0.5 coverage: full {J['T80_reversed_0.5']['cov_full']:.3f}; bootstrap 2.5/50/97.5%: "
         + " / ".join(f"{x:.3f}" for x in J["T80_reversed_0.5"]["q025_q50_q975"])
         + f"; P(cov < 0.90) {J['T80_reversed_0.5']['p_cov_lt_0.90']:.3f}",
         "", "Optimistic: D-07 helped select auto3; no shift between D-07H, D-07 and P4-H2; P4-H2 uses name-based bootstrap seeds (the D-07 auto3 rows used round-1 seeds)."]
    (out / "fragility.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
