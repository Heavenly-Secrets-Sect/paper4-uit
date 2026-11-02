"""R3-7: bootstrap-seed sensitivity of the cells where my recompute and analyze.py disagree
(borderline): (b) ida_union T150 extra-0.5 under Holm(21), and D6 ida_union T80 extra-0.2
(c2 - cal upper bound < 0). Also C2 upper bounds (verdict-relevant). 50 seeds.
Writes results/ext_v4cverify_recompute/seed_sensitivity.txt."""
import importlib.util
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rc", HERE / "recompute.py"); rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
fam = [(T, k, r) for T in rc.TS for (k, r) in rc.CELLS]
n_holm = n_d6 = 0; c2hi = []; famholm = []; c1tost = []
seeds = range(1, 51)
for sd in seeds:
    rc.IDX = np.random.default_rng(sd).integers(0, len(rc.TOPOS), size=(rc.B, len(rc.TOPOS)))
    res = [rc.paired("v4", "ida_union_cal", T, k, r) for (T, k, r) in fam]
    cov = [rc.coverage("v4", T, k, r) for (T, k, r) in fam]
    rej = rc.holm([s["p_less"] for s in res], 0.025)
    i = fam.index((150, "extra", 0.5))
    n_holm += bool(rej[i]); famholm.append(sum(bool(x and c >= 0.9) for x, c in zip(rej, cov)))
    d6 = rc.paired("ida_union_c2", "ida_union_cal", 80, "extra", 0.2)
    n_d6 += d6["ci"][1] < 0
    c2hi.append(max(rc.paired("v4c", "v4", 40, "missing", r)["ci"][1] for r in (0.2, 0.5)))
    c1 = [rc.paired("v4c", "v4", T, k, r) for T in (80, 150) for (k, r) in rc.CELLS]
    c1tost.append(sum(rc.holm([s["p_tost"] for s in c1], 0.05)))
L = [f"seeds 1..50 (B = 2000 each)",
     f"(b) ida_union T150 extra-0.5 rejected by Holm(21): {n_holm}/50",
     f"(b) ida_union W_holm count over 21 cells: min {min(famholm)} max {max(famholm)}; distribution {dict(zip(*np.unique(famholm, return_counts=True)))}",
     f"D6 ida_union T80 extra-0.2 upper < 0: {n_d6}/50",
     f"C2 max upper bound over the 2 cells: max over seeds {max(c2hi):.3f}",
     f"C1 TOST Holm count: min {min(c1tost)} max {max(c1tost)}; distribution {dict(zip(*np.unique(c1tost, return_counts=True)))}"]
(rc.OUT / "seed_sensitivity.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))
