"""verify3_tlp3: known-truth tests of experiments/ext/tlp3/analyze_p4h2.py (analyse/decide/holm) on
synthetic rows. No bank is read. Writes results/ext_verify3_tlp3/known_truth.json."""
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("A", ROOT / "experiments/ext/tlp3/analyze_p4h2.py")
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)

def holm_ref(p):
    p = np.asarray(p); m = len(p); o = np.argsort(p); adj = np.empty(m); cur = 0
    for r, i in enumerate(o):
        cur = max(cur, (m - r) * p[i]); adj[i] = min(1, cur)
    return adj

out = {}
rng = np.random.default_rng(1)
mx = 0
for _ in range(2000):
    p = rng.uniform(0, 0.2, 12); p[rng.integers(0, 12, 3)] = p[0]  # ties
    mx = max(mx, np.abs(A.holm(p) - holm_ref(p)).max())
out["holm_max_abs_diff_vs_ref"] = float(mx)

CELLS = [("none", 0.0)] + A.DAMAGED
def make_rows(effect, xcov=None, fail=None, n_topo=20, reps=3, sd=0.3, seed=0):
    """effect[(T,kind,rate,X)] = mean of IS(v4)-IS(X) (default -1). xcov: (T,kind,rate,X)->covered share."""
    g = np.random.default_rng(seed); rows = []
    for t in range(n_topo):
        tre = g.normal(0, 0.2)
        for rp in range(reps):
            for T in A.TS:
                for kind, rate in CELLS:
                    base = 3 + g.normal(0, 0.5)
                    for m in [A.REF] + A.VERSIONS:
                        r = {"topology": f"t{t}", "replicate": rp, "T": T, "kind": kind, "rate": rate, "method": m,
                             "scenario": "clean"}
                        if fail and (t, rp, T, kind, rate, m) in fail:
                            r["status"] = "failed"; rows.append(r); continue
                        if m == A.REF:
                            isc, cv = base, 19
                        else:
                            e = effect.get((T, kind, rate, m), -1.0)
                            isc = base - (e + tre + g.normal(0, sd)); cv = 19
                            if xcov and (T, kind, rate, m) in xcov: cv = int(round(20 * xcov[(T, kind, rate, m)]))
                        r.update({"status": "ok", "iscore_nonnull_mean": isc, "n_nonnull": 20,
                                  "n_covered_nonnull": cv, "width_kept": 1.0})
                        rows.append(r)
    return rows

def run(rows, n_topo=20):
    units = [(f"t{t}", rp) for t in range(n_topo) for rp in range(3)]
    res = A.analyse(rows, units, "test"); v, per = A.decide(res)
    return v, {X: {k: per[X][k] for k in per[X] if k != "cells"} for X in per}, res

cases = {}
v, c, _ = run(make_rows({})); cases["all_v4_better_by_1"] = {"expect": "CONFIRMED-A", "got": v, "counts": c}
eff = {(80, "missing", 0.2, "tlp2_db"): 0.0, (150, "extra", 0.5, "tlp2_db"): 0.0}
v, c, _ = run(make_rows(eff)); cases["two_ties_one_X"] = {"expect": "CONFIRMED-A' (10 wins)", "got": v, "counts": c}
eff = {(T, "missing", r, "tlp2_db"): 0.0 for T in (80, 150) for r in (0.2, 0.5)}
v, c, _ = run(make_rows(eff)); cases["four_ties_one_X"] = {"expect": "NOT CONFIRMED (8 wins)", "got": v, "counts": c}
# X better (positive d) in one cell but with X coverage 0.80 -> X wins pure view only
eff = {(80, "reversed", 0.5, "targeted_lp"): 1.0}; xc = {(80, "reversed", 0.5, "targeted_lp"): 0.80}
v, c, _ = run(make_rows(eff, xcov=xc)); cases["X_wins_pure_only"] = {"expect": "NOT CONFIRMED", "got": v, "counts": c}
# raw win but not Holm: small effects so that per-cell p ~0.01-0.04
eff = {(T, k, r, "tlp2_db_p3"): -0.12 for T in A.TS for k, r in A.DAMAGED}
v, c, res = run(make_rows(eff, sd=0.3, seed=3))
ps = [res["cells"][f"{T}|{k}|{r}"]["comps"]["tlp2_db_p3"]["p"] for T in A.TS for k, r in A.DAMAGED]
cases["small_effects_tlp2_db_p3"] = {"note": "raw gate wins vs Holm-passed should differ", "got": v, "counts": c["tlp2_db_p3"],
                                     "raw_p": ps}
# failures: 7 failed v4 runs in one cell -> 53 pairs < 54 -> incomplete
fail = {(t, 0, 150, "extra", 0.2, A.REF) for t in range(7)}
v, c, res = run(make_rows({}, fail=fail))
cases["7_v4_failures"] = {"expect": "NOT CONFIRMED (incomplete ...)", "got": v,
                          "v4_cov_150_extra_0.2": res["cells"]["150|extra|0.2"]["methods"][A.REF]["cov"], "expected_cov": 53 * 19 / (60 * 20)}
# all four methods fail for 6 units in one cell: does coverage count them as uncovered?
fail = {(t, 0, 80, "extra", 0.2, m) for t in range(6) for m in [A.REF] + A.VERSIONS}
v, c, res = run(make_rows({}, fail=fail))
cases["6_units_all_methods_fail"] = {"got": v, "v4_cov": res["cells"]["80|extra|0.2"]["methods"][A.REF]["cov"],
                                     "cov_if_failed_counted_uncovered": 54 * 19 / (60 * 20), "n_pairs": res["cells"]["80|extra|0.2"]["comps"]["targeted_lp"]["n_pairs"]}
out["cases"] = cases
p = ROOT / "results/ext_verify3_tlp3"; p.mkdir(parents=True, exist_ok=True)
(p / "known_truth.json").write_text(json.dumps(out, indent=2, default=str))
print(json.dumps(out, indent=1, default=str))
