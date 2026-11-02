"""Design probe of the lead-lag gate on D-07H development only (no bootstrap, no interval).

For every D-07H development topology x 3 replicates (unit seeds of the calibration stream,
seed_base + 500000 + 1000 * t_idx + rep) x scenario {clean, latent1, latent3, noise0.1} x T {40, 80, 150}
x stated missing-0.2/0.5: the data-level step (3) of tolerant_v5_1 (targeted opening, fit f0, BH list),
and the gate on every BH-significant pair, for three variants:
  A  design: Haugh Q on the f0 residuals, lags {-M..M} \\ {0}, M = 4 (T <= 80) / 6, p < 0.05;
  B  A after AR(2) prewhitening of each residual series (Haugh's original two-step procedure);
  C  A with M = 2.
  D  A on the residuals of the skeleton-only structural fit (no opened lag blocks), as in screen_pairs.
  E  A restricted to the lags not absorbed by the opened blocks, |l| in {lag_max+1..M} (chi2 with 2(M-2) df).
Truth classes (worker.classify): E0, EL, C, CE, N. Reports flag rates by class, AUROC of p_Q for
C vs E0 (BH-significant pairs), and the composition of the repaired set with and without the gate.

Run: python experiments/ext/r4leadlag/probe.py --workers 3  -> results/ext_r4leadlag_probe/{probe.json, probe.md}
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import worker as W  # noqa: E402

RE = W.RE
from paper4 import ext_r4leadlag as LL  # noqa: E402
from paper4.estimator import fit_equations, parent_terms  # noqa: E402
from paper4.ext_narrow import opened_terms, select_open  # noqa: E402
from paper4.generator import add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.methods import stated_counts  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

CFG = json.loads((W.ROOT / "experiments" / "configs" / "ext_r4leadlag_eval_latent.json").read_text())
SCEN = [("clean", 0, 0.0), ("latent1", 1, 0.0), ("latent3", 3, 0.0), ("noise0.1", 0, 0.1)]
TS = [40, 80, 150]
RATES = [0.2, 0.5]
OUT = W.ROOT / "results" / "ext_r4leadlag_probe"


def prewhiten(r: np.ndarray, p: int = 2) -> np.ndarray:
    X = np.column_stack([np.ones(len(r) - p)] + [r[p - k: len(r) - k] for k in range(1, p + 1)])
    y = r[p:]
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]


def q_far(ru, rv, M, lag_max):
    m = len(ru)
    rho = LL.cross_corr(ru, rv, M)
    q = m * sum((m / (m - abs(l))) * rho[l] ** 2 for l in rho if abs(l) > lag_max)
    return LL.chi2_sf_even(q, 2 * (M - lag_max))


def unit_job(args):
    t_idx, rep = args
    topo = load_bank("D-07H", "development")[t_idx]
    gen = RE.generator_config(CFG)
    unit = CFG["seed_base"] + 500_000 + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    out = []
    for sc, nl, noise in SCEN:
        sem_s = add_latent(sem, nl, np.random.default_rng([unit, 5]))
        cc = W._cochild(sem_s)
        for T in TS:
            data = sem_s.simulate(T, np.random.default_rng([unit, 2, T]))
            data = add_measurement_noise(data, noise, np.random.default_rng([unit, 6, T]))
            for rate in RATES:
                skel = RE.public(damage(truth, "missing", rate, np.random.default_rng([unit, 1, 1]), sem.edge_lag, coef))
                k = stated_counts(skel.damage)["missing"]
                try:
                    op = select_open(data, skel, 2, k, 3.0, 0.10)
                except ValueError:
                    out.append({"sc": sc, "T": T, "rate": rate, "status": "underdetermined"})
                    continue
                terms = [list(dict.fromkeys(opened_terms(skel, op, j, 2))) for j in range(skel.n)]
                f0 = fit_equations(data, terms, 2)
                if f0.status != "ok":
                    out.append({"sc": sc, "T": T, "rate": rate, "status": f0.status})
                    continue
                R = f0.residuals
                fs = fit_equations(data, [parent_terms(skel, j, 2) for j in range(skel.n)], 2)
                RS = fs.residuals
                ranked = LL.bh_ranked(R, skel)
                M = LL.gate_M(T)
                cands = []
                for p0, u, v in ranked:
                    pa = LL.haugh_q(R[:, u], R[:, v], M)[1]
                    pb = LL.haugh_q(prewhiten(R[:, u]), prewhiten(R[:, v]), M)[1]
                    pc = LL.haugh_q(R[:, u], R[:, v], 2)[1]
                    pd = LL.haugh_q(RS[:, u], RS[:, v], M)[1]
                    pe = q_far(R[:, u], R[:, v], M, 2)
                    cands.append({"u": u, "v": v, "p0": p0, "pA": pa, "pB": pb, "pC": pc, "pD": pd, "pE": pe,
                                  "cls": W.classify(sem_s, u, v, cc)})
                sets = {}
                for var in ("none", "A", "B", "C", "D", "E"):
                    rep_ = []
                    for c in cands:
                        if len(rep_) == k:
                            break
                        if var != "none" and c["p" + var] < LL.ALPHA_GATE:
                            continue
                        rep_.append(c["cls"])
                    sets[var] = rep_
                out.append({"sc": sc, "T": T, "rate": rate, "status": "ok", "k": k, "cands": cands, "sets": sets,
                            "unit": unit, "topology": topo.id})
    return out


def auroc(pos, neg):
    """P(score_pos > score_neg) + 0.5 P(tie), score = -p (smaller p = more 'confounded')."""
    if not pos or not neg:
        return None
    pos, neg = -np.array(pos), -np.array(neg)
    gt = (pos[:, None] > neg[None, :]).mean()
    eq = (pos[:, None] == neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    n_topo = len(load_bank("D-07H", "development"))
    jobs = [(t, r) for t in range(n_topo) for r in range(3)]
    recs = []
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(unit_job, jobs):
            recs.extend(res)
    OUT.mkdir(parents=True, exist_ok=True)
    summ = {}
    lines = ["# r4leadlag design probe (D-07H development; generated by experiments/ext/r4leadlag/probe.py)", "",
             "Flag rate = share of BH-significant pairs labelled confounded (p_Q < 0.05). Classes: E0 true contemporaneous "
             "edge missing from the skeleton, EL true lagged edge missing, C co-child (not an edge), CE co-child and edge, N neither.",
             "Repaired composition: mean number of C / E0 pairs in the repaired set per run (none = v5_1, A/B/C = gated).", "",
             "| scen | T | runs | BH/run | n E0 | n C | n N | flag E0 A/B/C/D/E | flag C A/B/C/D/E | flag N A | AUROC C vs E0 A/B/C/D/E | rep C none/A/B/C/D/E | rep E0 none/A/B/C/D/E | runs changed A |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sc, _, _ in SCEN:
        for T in TS:
            g = [r for r in recs if r["sc"] == sc and r["T"] == T and r["status"] == "ok"]
            by = defaultdict(lambda: defaultdict(list))
            for r in g:
                for c in r["cands"]:
                    for var in "ABCDE":
                        by[c["cls"]][var].append(c["p" + var])
            fl = {cl: {var: (float(np.mean(np.array(by[cl][var]) < 0.05)) if by[cl][var] else None) for var in "ABCDE"}
                  for cl in ("E0", "EL", "C", "CE", "N")}
            au = {var: auroc(by["C"][var], by["E0"][var]) for var in "ABCDE"}
            comp = {var: {cl: float(np.mean([s["sets"][var].count(cl) for s in g])) if g else None for cl in ("C", "E0", "N", "EL")}
                    for var in ("none", "A", "B", "C", "D", "E")}
            changed = float(np.mean([s["sets"]["A"] != s["sets"]["none"] for s in g])) if g else None
            nbh = float(np.mean([len(r["cands"]) for r in g])) if g else None
            summ[f"{sc}|{T}"] = {"runs": len(g), "of": len([r for r in recs if r["sc"] == sc and r["T"] == T]),
                                 "bh_per_run": nbh, "n": {cl: len(by[cl]["A"]) for cl in ("E0", "EL", "C", "CE", "N")},
                                 "flag": fl, "auroc_C_vs_E0": au, "repaired": comp, "changed_A": changed}

            def f(x):
                return "–" if x is None else f"{x:.2f}"
            lines.append(f"| {sc} | {T} | {len(g)} | {f(nbh)} | {len(by['E0']['A'])} | {len(by['C']['A'])} | {len(by['N']['A'])} | "
                         + "/".join(f(fl['E0'][v]) for v in "ABCDE") + " | " + "/".join(f(fl['C'][v]) for v in "ABCDE")
                         + f" | {f(fl['N']['A'])} | " + "/".join(f(au[v]) for v in "ABCDE") + " | "
                         + "/".join(f(comp[v]['C']) for v in ("none", "A", "B", "C", "D", "E")) + " | "
                         + "/".join(f(comp[v]['E0']) for v in ("none", "A", "B", "C", "D", "E")) + f" | {f(changed)} |")
    (OUT / "probe.json").write_text(json.dumps(summ, indent=1))
    (OUT / "probe.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
