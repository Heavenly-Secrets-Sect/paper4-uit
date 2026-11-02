"""Is M0's D-07 miscoverage explained by calibration-bank variability (training-conditional) rather than
failure of a marginal guarantee? Resample D-07H topologies (rep 0) with replacement, recompute q_M0 per (T, kind),
apply to D-07 pairs; report mean and 2.5/97.5% of D-07 coverage per (T, kind). Also a 'swap' check:
calibrate on D-07 rep 0, evaluate on D-07H reps 1-2."""
import json, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
KINDS = ["none", "extra", "missing", "reversed"]
C = dict(np.load(ROOT / "results/ext_r4mondrian_cal/pairs.npz")); P = dict(np.load(ROOT / "results/ext_r4mondrian_eval/pairs.npz"))
sC = np.abs(C["C_t"] - C["mid"]) / C["h"]; sP = np.abs(P["C_t"] - P["mid"]) / P["h"]
def cq(x):
    x = np.sort(x); k = math.ceil((len(x) + 1) * .95 - 1e-9); return x[k - 1] if k <= len(x) else np.inf
rng = np.random.default_rng(7); out = {}
for T in (40, 80, 150):
    for kc, kind in enumerate(KINDS):
        mc = (C["T"] == T) & (C["stated"] == kc) & (C["rep"] == 0); mp = (P["T"] == T) & (P["stated"] == kc)
        topo = C["topo"][mc]; s = sC[mc]; ids = np.unique(topo); by = [s[topo == t] for t in ids]
        covs, qs = [], []
        for _ in range(2000):
            pick = rng.integers(0, len(ids), len(ids)); q = cq(np.concatenate([by[i] for i in pick]))
            qs.append(q); covs.append((sP[mp] <= q).mean())
        q0 = cq(s); c0 = (sP[mp] <= q0).mean()
        # swap: calibrate on D-07 rep0, test on D-07H reps 1,2
        md = mp & (P["rep"] == 0); mh = (C["T"] == T) & (C["stated"] == kc) & (C["rep"] > 0)
        qd = cq(sP[md]); swap = (sC[mh] <= qd).mean()
        # within-bank holdout: D-07H rep0 -> D-07H reps 1-2 ; D-07 rep0 -> D-07 reps 1-2
        within_H = (sC[mh] <= q0).mean(); within_D = (sP[mp & (P["rep"] > 0)] <= qd).mean()
        out[f"{T}|{kind}"] = {"q_rep0": round(float(q0), 4), "D07_cov_at_q_rep0": round(float(c0), 4),
                              "D07_cov_over_cal_resamples_mean": round(float(np.mean(covs)), 4),
                              "D07_cov_resample_2.5_97.5": [round(float(x), 4) for x in np.quantile(covs, [.025, .975])],
                              "q_resample_2.5_97.5": [round(float(x), 3) for x in np.quantile(qs, [.025, .975])],
                              "swap_D07rep0_to_D07Hrep12": round(float(swap), 4),
                              "D07Hrep0_to_D07Hrep12": round(float(within_H), 4), "D07rep0_to_D07rep12": round(float(within_D), 4)}
        print(T, kind, out[f"{T}|{kind}"])
json.dump(out, open(ROOT / "results/ext_verify4_mondrian/calboot.json", "w"), indent=1)
