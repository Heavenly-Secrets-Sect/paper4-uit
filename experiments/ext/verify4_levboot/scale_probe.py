"""Verifier probe on D-07H development ONLY: is the recursive-design residual bootstrap of tolerant_v5_1
invariant to a common rescaling of the residual pool? If yes, 'pool variance x1.5-1.9 but raw coverage unchanged'
says nothing about leverage. Also: per-equation (non-uniform) rescale, and leverage vs explicit hat matrix."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import run_experiment as R
from paper4 import estimator as E
from paper4 import ext_r4levboot as L
from paper4.ext_v51 import tolerant_v5_1
from paper4.generator import GeneratorConfig, build_dynamic_sem
from paper4.skeleton import damage, true_skeleton
from paper4.topology import load_bank
GEN = dict(q0=0.3, cross_coef=(0.3, 0.8), self_coef=(0.2, 0.6), noise_var=(0.5, 1.5), rho_max=0.9, burn_in=200)
SEED = 88_000_000

def sim_scaled(scale_fn):
    cache = {}
    def simulate(fit, data, rng):
        if id(fit) not in cache:
            cache.clear()
            r = fit.residuals; m = len(r)
            pool = (r - r.mean(0)) * np.sqrt(m / np.maximum(fit.dof, 1.0))
            cache[id(fit)] = (fit, pool * scale_fn(pool.shape[1]))
        pool = cache[id(fit)][1]
        T, n = data.shape; p = fit.B.shape[0] - 1
        A = np.linalg.inv(np.eye(n) - fit.B[0])
        draws = pool[rng.integers(0, len(pool), size=T - p)]
        x = np.zeros_like(data); x[:p] = data[:p]
        for t in range(p, T):
            acc = fit.intercept + draws[t - p]
            for k in range(1, p + 1):
                acc = acc + fit.B[k] @ x[t - k]
            x[t] = A @ acc
        return x
    return simulate

def run(data, skel, lag, rngf, sim):
    st = {}
    with L.bootstrap_hooks(sim, st):
        return tolerant_v5_1(data, skel, lag, 4, 199, rngf())

out = []
topos = load_bank("D-07H", "development")[:6]
lag = 2
gen = GeneratorConfig(lag_max=lag, **GEN)
hat_dev = 0.0
for t_idx, topo in enumerate(topos):
    unit = SEED + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lg, e[1], e[0]]) for e, lg in sem.edge_lag.items()}
    for T in (40, 80):
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, (kind, rate) in enumerate([("none", 0.0), ("missing", 0.2), ("reversed", 0.2)]):
            k_idx = {"none": 0, "missing": 1, "reversed": 2}[kind]
            skel = R.public(damage(truth, kind, rate, np.random.default_rng([unit, 1, k_idx]), sem.edge_lag, coef))
            rngf = lambda: np.random.default_rng([unit, 3, T, c_idx, 7])
            base = run(data, skel, lag, rngf, sim_scaled(lambda n: 1.0))
            ref = tolerant_v5_1(data, skel, lag, 4, 199, rngf())
            rec = {"topo": topo.id, "T": T, "kind": kind, "status": base.status}
            if base.status != "ok":
                out.append(rec); continue
            rec["self_check_maxdiff_vs_v51"] = float(max(np.abs(base.lo - ref.lo).max(), np.abs(base.hi - ref.hi).max()))
            off = ~np.eye(sem.n, dtype=bool)
            w0 = (base.hi - base.lo)[off]
            for nm, fn in [("x1.30_all", lambda n: 1.30), ("x3.0_all", lambda n: 3.0),
                           ("rand_eq_0.8-1.6", lambda n: np.random.default_rng(unit + T).uniform(0.8, 1.6, n))]:
                r2 = run(data, skel, lag, rngf, sim_scaled(fn))
                if r2.status == "ok":
                    w = (r2.hi - r2.lo)[off]
                    rec[nm] = {"median_width_ratio": float(np.median(w / np.where(w0 > 0, w0, np.nan))),
                               "mean_width_ratio": float(np.nanmean(w / np.where(w0 > 0, w0, np.nan)))}
                else:
                    rec[nm] = {"status": r2.status}
            # leverage vs explicit hat matrix on the data fit (plain fit with the skeleton's parent terms)
            from paper4.estimator import fit_equations, parent_terms
            terms = [parent_terms(skel, j, lag) for j in range(sem.n)]
            fit = fit_equations(data, terms, lag)
            if fit.status == "ok":
                h = L.leverages(fit, data); rows = np.arange(lag, T)
                for j in range(sem.n):
                    X = np.column_stack([np.ones(len(rows))] + [data[rows - lg, i] for i, lg in terms[j]])
                    Hm = X @ np.linalg.pinv(X.T @ X) @ X.T
                    hat_dev = max(hat_dev, float(np.abs(np.diag(Hm) - h[:, j]).max()))
            out.append(rec)
            print(json.dumps(rec), flush=True)
summ = {}
for nm in ("x1.30_all", "x3.0_all", "rand_eq_0.8-1.6"):
    v = [r[nm]["median_width_ratio"] for r in out if nm in r and "median_width_ratio" in r[nm]]
    summ[nm] = {"n": len(v), "min": min(v), "median": float(np.median(v)), "max": max(v)}
summ["self_check_maxdiff_vs_v51"] = max(r.get("self_check_maxdiff_vs_v51", 0) for r in out)
summ["leverage_vs_explicit_hat_maxdev"] = hat_dev
print(json.dumps(summ, indent=1))
d = ROOT / "results" / "ext_verify4_levboot"; d.mkdir(parents=True, exist_ok=True)
(d / "scale_probe.json").write_text(json.dumps({"summary": summ, "records": out}, indent=1))
