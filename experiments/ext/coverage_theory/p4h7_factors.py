"""P4-H7 factors: unit-level order statistics from the unit dump (protocol: docs/ext/p4h7_spec.md).

Per (T, stated kind) cell and per beta, the unit score is S = max over the damage rates of the exact run
score S_r(beta) = the (m+1)-th largest rho in the run, with m = floor(beta * n) misses allowed and
rho = |C_true - mid| / half (rho = inf if half = 0 and dist > 0). A run that failed to fit has no record
and counts as a miss at every finite factor (S = inf). The factor is exact (no grid); it multiplies the
half-width of the interval after the fixed pre-scale. Rounded UP to 3 decimals.

Marginal factor : k0 = ceil((N + 1) * (1 - delta)) -th smallest unit score, delta = 0.10.
PAC factor      : smallest k0 with Beta(k0, N + 1 - k0).cdf(1 - delta) <= alpha, alpha = 0.05
                  (with confidence 1 - alpha over the calibration draw, a new topology satisfies S <= factor
                  with probability >= 1 - delta). Needs N >= 59.
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta as beta_dist


def run_score(dist, half, beta):
    d, h = np.array(dist), np.array(half)
    rho = np.where(h > 0, d / np.where(h > 0, h, 1), np.where(d > 0, np.inf, 0.0))
    n = len(rho)
    m = int(math.floor(beta * n + 1e-12))
    if m >= n:
        return 0.0
    return float(np.sort(rho)[::-1][m])


def pac_k0(n, delta, alpha):
    for k in range(1, n + 1):
        if beta_dist.cdf(1 - delta, k, n + 1 - k) <= alpha:
            return k
    return None


def expected_runs(meta):
    """Per unit and cell, how many damage runs the unit contributes: one run per stated-damage skeleton, filed under
    the cell of its strongest stated damage kind (a draw with k = 0, e.g. reversed at a low rate, belongs to 'none').
    A missing record in a cell where runs were expected is then a genuine fit failure. Deterministic function of the
    unit, replayed from the runner's own seeds."""
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root / "src"), str(root / "experiments"), str(Path(__file__).resolve().parent)]
    import run_experiment as R
    from p4h7_units import build_cfg
    from paper4 import methods as M
    from paper4.generator import build_dynamic_sem
    from paper4.topology import load_bank
    import numpy as np
    cfg = build_cfg(meta["split"], ",".join(map(str, meta["T"])), meta["seed_base"], meta["lag"], "0.2,0.5")
    gen = R.generator_config(cfg)
    exp = collections.defaultdict(lambda: collections.defaultdict(int))  # (T-free) key -> unit -> count
    for t_idx, topo in enumerate(load_bank(meta["bank"], meta["split"])[: meta.get("n_units")]):
        unit_seed = meta["seed_base"] + 500_000 + 1000 * t_idx
        sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit_seed, 0]))
        for (kind, rate), skel in R.unit_skeletons(sem, unit_seed, cfg).items():
            exp[M.width_key(skel.damage)][topo.id] += 1
    return exp


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--delta", type=float, default=0.10)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expected-runs", action="store_true", help="count a missing record as a failure only where a run was expected (P4-H8 rule)")
    ap.add_argument("--frozen-out", default=None, help="write the factor table used by p4h7_test_eval.py")
    a = ap.parse_args(argv)
    d = json.loads(Path(a.units).read_text())
    exp = expected_runs(d) if a.expected_runs else None
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in d["records"]:
        by[r["cell"]][r["unit"]].append(r)
    result, lines = {}, ["| cell | N | runs/unit | beta | median S | q90 S | max S | marginal factor | PAC factor | frozen v5.1 |",
                         "|---|---|---|---|---|---|---|---|---|---|"]
    frozen = json.loads((Path(__file__).resolve().parents[3] / "results/ext_region51_lag1/calibration.json").read_text())
    grid = np.round(np.arange(1.0, 10.01, 0.1), 2)  # run_experiment.C_GRID
    for cell in sorted(by, key=lambda c: (int(c.split("|")[1]), c)):
        kind = cell.split("|")[2]
        dist = np.array([x for rs in by[cell].values() for r in rs for x in r["dist"]])
        half = np.array([x for rs in by[cell].values() for r in rs for x in r["half"]])
        cov = np.array([(dist <= c * half).mean() for c in grid])  # the shipped rule: pooled pair-level grid quantile
        result[f"{cell}|pooled"] = float(grid[np.argmax(cov >= min(0.95, cov.max() - 0.005))])
        need = 1 if kind == "none" else 2
        units = by[cell]
        for beta in (0.05, 0.10):
            if exp is None:
                scores = np.array([max(run_score(r["dist"], r["half"], beta) for r in rs) if len(rs) >= need else np.inf
                                   for rs in units.values()])
            else:
                scores = np.array([max([run_score(r["dist"], r["half"], beta) for r in units.get(u, [])] or [0.0])
                                   if len(units.get(u, [])) >= c else np.inf for u, c in exp[kind].items() if c > 0])
            n = len(scores)
            s = np.sort(scores)
            k_m = math.ceil((n + 1) * (1 - a.delta))
            k_p = pac_k0(n, a.delta, a.alpha)
            fm = float(s[k_m - 1]) if k_m <= n else math.inf
            fp = float(s[k_p - 1]) if k_p else None
            up = lambda x: None if x is None else (x if math.isinf(x) else math.ceil(x * 1000) / 1000)
            result[f"{cell}|beta{beta}"] = {"N": n, "marginal": up(fm), "pac": up(fp), "k_marginal": k_m, "k_pac": k_p,
                                            "frac_inf": float((~np.isfinite(scores)).mean())}
            lines.append(f"| {cell} | {n} | {need} | {beta} | {np.median(scores):.2f} | {np.quantile(scores, 0.9):.2f} | "
                         f"{scores.max():.2f} | {up(fm)} | {up(fp)} | {frozen.get(cell, '-')} |")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=2))
    if a.frozen_out:
        Path(a.frozen_out).write_text(json.dumps(
            {"_note": "P4-H7 frozen width factors from the calibration split (docs/ext/p4h7_spec.md). Keys: "
                      "cell|beta<b> -> {marginal, pac}; cell|pooled -> shipped pooled pair-level rule recomputed on the same split.",
             "delta": a.delta, "alpha": a.alpha, "factors": result}, indent=2))
    Path(a.out).with_suffix(".md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
