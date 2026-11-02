"""Verifier (revlag3): affected-pair coverage of the new methods vs v4 when each method's
interval is rescaled about its midpoint so that its coverage on ALL non-null pairs of the cell
equals v4's (D-07H probe runs only; descriptive, truth used only for evaluation)."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag3")); sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_rev import wide
from analyze_lag import load, covered
out = {}
for run, new in (("ext_verify3_revlag3/rev_invalid_copy", ["tolerant_v4R", "tolerant_v4R_mix", "tolerant_v4Rmap"]),
                 ):
    df, methods, cells = load(run)
    W = wide(df, ["tolerant_v4", "oracle"] + new)
    for cname in ("reversed|0.2", "reversed|0.5"):
        for T in (80, 150):
            s = W[(W.cname == cname) & (W["T"] == T)]
            aff = s.dC >= 0.05
            cv4 = covered(s.lo_tolerant_v4, s.hi_tolerant_v4, s.C_t)
            row = dict(cov_all_v4=float(cv4.mean()), cov_aff_v4=float(cv4[aff].mean()), n_aff=int(aff.sum()))
            for m in new:
                mid = (s[f"lo_{m}"] + s[f"hi_{m}"]) / 2; half = (s[f"hi_{m}"] - s[f"lo_{m}"]) / 2
                dist = np.abs(s.C_t - mid)
                grid = np.arange(0.5, 3.0, 0.005)
                covs = np.array([(dist <= g * half).mean() for g in grid])
                g = grid[np.argmax(covs >= cv4.mean())]
                c = dist <= g * half
                row[m] = dict(scale=round(float(g), 3), cov_all=float(c.mean()), cov_aff=float(c[aff].mean()),
                              d_aff=float(c[aff].mean() - cv4[aff].mean()),
                              cov_all_raw=float(covered(s[f"lo_{m}"], s[f"hi_{m}"], s.C_t).mean()),
                              medw_ratio=float(np.median(2 * g * half) / np.median(s.hi_tolerant_v4 - s.lo_tolerant_v4)))
            out[f"{run} {cname} T{T}"] = row
json.dump(out, open(ROOT / "results/ext_verify3_revlag3/matched_width_d07.json", "w"), indent=1)
for k, v in out.items():
    print(k, "v4 all %.3f aff %.3f n_aff %d" % (v["cov_all_v4"], v["cov_aff_v4"], v["n_aff"]))
    for m, r in v.items():
        if isinstance(r, dict):
            print("   %-18s scale %.3f raw_all %.3f -> all %.3f aff %.3f d_aff %+.3f medw/v4 %.3f" % (m, r["scale"], r["cov_all_raw"], r["cov_all"], r["cov_aff"], r["d_aff"], r["medw_ratio"]))
