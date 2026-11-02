"""Skeptic check (exploratory, D-07H development, seed 999, uncalibrated, none cell):
the bootstrap re-estimates r on y*, and r_boot is biased low vs r_used (runs.jsonl: 0.061 vs 0.114
at noise0.3 T80). Does that shift the percentile interval towards 0 relative to the point estimate?
Compare the percentile interval with the basic (reflected) interval from the same draws."""
import sys; sys.path.insert(0, "src")
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import paper4.ext_eiv as E
from paper4.generator import GeneratorConfig, add_measurement_noise, build_dynamic_sem
from paper4.skeleton import true_skeleton
from paper4.topology import load_bank
from paper4.metrics import truth_effects, interval_score
store = {}
orig = E.percentile_interval
def cap(draws, alpha=0.05):
    store["d"] = draws; return orig(draws, alpha)
E.percentile_interval = cap
gen = GeneratorConfig(); topos = load_bank("D-07H", "development")[:int(sys.argv[2]) if len(sys.argv) > 2 else 6]
T = int(sys.argv[1]) if len(sys.argv) > 1 else 150
for ratio in (0.0, 0.3):
    acc = {"pct": [0, 0, []], "basic": [0, 0, []]}; shift = []; rr = []
    for t_idx, topo in enumerate(topos):
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([999, t_idx]))
        sk = true_skeleton(sem)
        x = sem.simulate(T, np.random.default_rng([999, t_idx, T, 1]))
        y = add_measurement_noise(x, ratio, np.random.default_rng([999, t_idx, T, 2]))
        res = E.tolerant_eiv(y, sk, 2, 4, 99, np.random.default_rng([999, t_idx, 5]))
        if res.status != "ok":
            continue
        _, C, _, _ = truth_effects(sem, 4)
        nn = ~np.eye(sem.n, dtype=bool) & (np.abs(C) > 0.1)
        d = store["d"]; lo, hi = res.lo, res.hi; pt = res.C
        blo, bhi = 2 * pt - hi, 2 * pt - lo
        mid = np.median(d, axis=0)
        # shift of the bootstrap median towards 0, relative to the point estimate, in units of |pt|
        shift.append(np.median(((np.abs(pt) - np.abs(mid)) / np.maximum(np.abs(pt), 1e-9))[nn]))
        rr.append((res.info["r_used"], res.info["r_boot_mean"]))
        for k, (a, b) in {"pct": (lo, hi), "basic": (blo, bhi)}.items():
            acc[k][0] += int(((C >= a) & (C <= b))[nn].sum()); acc[k][1] += int(nn.sum())
            acc[k][2].append(interval_score(a, b, C)[nn].mean())
    print(f"T={T} ratio={ratio}: r_used/r_boot {np.mean([a for a,_ in rr]):.3f}/{np.mean([b for _,b in rr]):.3f}; "
          f"median shrink of boot median vs point {np.mean(shift):+.3f}; "
          + "; ".join(f"{k} cov {v[0]/v[1]:.3f} IS {np.mean(v[2]):.2f}" for k, v in acc.items()), flush=True)
