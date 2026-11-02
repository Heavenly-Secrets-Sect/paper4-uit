"""R3-4, "more orientation draws" arm (revlag3), descriptive, NO new data: on the round-2 run
results/ext_revlag_lag (D-07 development, seed_base 20261102), tolerant_v4 and tolerant_v4L compute
C(H) and the interval with the SAME algorithm on independent random streams (identity check of
round 2), so |C_v4 - C_v4L| / sqrt(2) estimates the Monte Carlo sd of the module's centre with 199
draws. If that sd is small next to the centring error |C_v4 - C_true| on affected pairs, more
orientation draws (which only shrink Monte Carlo error) cannot close the gap.
Also: coverage of the averaged centre-and-interval (mean of the two lo, of the two hi; a proxy for
398 draws) on affected pairs, vs v4. Cluster bootstrap as analyze_lag (seed 20261103).
Run:  python experiments/ext/revlag3/mc_draws.py     Writes results/ext_revlag3_mcdraws/mc_draws.{md,json}.
"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/ext/revlag"))
from analyze_lag import Boot, ci, covered, load, paired  # noqa: E402


def main():
    df, methods, cells = load("ext_revlag_lag")
    m = paired(df, "tolerant_v4L", "tolerant_v4")  # a = v4L, b = v4
    boot = Boot(df.topo.unique())
    out = ROOT / "results/ext_revlag3_mcdraws"; out.mkdir(parents=True, exist_ok=True)
    L = ["# R3-4: Monte Carlo error of the v4 centre vs its centring error (ext_revlag_lag, affected pairs dC >= 0.05)", "",
         "| cell | T | n | median MC sd of C (|C_v4 − C_v4L|/√2) | median |C_v4 − C_true| | ratio | cov v4 | cov v4L | "
         "cov avg(v4, v4L) | delta avg − v4 [CI] |", "|---|---|---|---|---|---|---|---|---|---|"]
    res = []
    for cname in ("reversed|0.2", "reversed|0.5"):
        for T in (40, 80, 150):
            s = m[(m.cname == cname) & (m["T"] == T) & (m.dC >= 0.05)]
            mc = np.abs(s.C_e_b - s.C_e_a) / np.sqrt(2)
            err = np.abs(s.C_e_b - s.C_t)
            c4 = covered(s.lo_b, s.hi_b, s.C_t); cL = covered(s.lo_a, s.hi_a, s.C_t)
            ca = covered((s.lo_a + s.lo_b) / 2, (s.hi_a + s.hi_b) / 2, s.C_t)
            d, rd = boot.ratio(s.topo.values, (ca - c4).values)
            r = dict(cell=cname, T=T, n=len(s), mc_sd_med=float(mc.median()), err_med=float(err.median()),
                     ratio=float(mc.median() / err.median()), cov_v4=float(c4.mean()), cov_v4L=float(cL.mean()),
                     cov_avg=float(ca.mean()), d=d, ci=ci(rd))
            res.append(r)
            L.append(f"| {cname} | {T} | {len(s)} | {r['mc_sd_med']:.4f} | {r['err_med']:.3f} | {r['ratio']:.3f} | "
                     f"{r['cov_v4']:.3f} | {r['cov_v4L']:.3f} | {r['cov_avg']:.3f} | {d:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] |")
    (out / "mc_draws.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "mc_draws.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else o))
    print("\n".join(L))


if __name__ == "__main__":
    main()
