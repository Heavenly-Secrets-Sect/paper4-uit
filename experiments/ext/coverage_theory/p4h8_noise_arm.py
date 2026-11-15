"""P4-H8 exploratory arm: the same topologies and frozen factors, but non-Gaussian innovations (violation of the
clean-Gaussian assumption; NOT part of the guarantee). Protocol: docs/ext/p4h8_spec.md, section "Violations".

Only the innovation law changes (unit variance in every case): t4 (Student-t, 4 degrees of freedom) and laplace; me10 and me30 add classical measurement noise (variance 10% and 30% of each column) to Gaussian-innovation data.
The unit dump has the same format as p4h7_units.py, so p4h7_test_eval.py evaluates it with the frozen factors:

    python experiments/ext/coverage_theory/p4h8_noise_arm.py --law t4 --lag 1 --T 19,30,40,80,150 --out results/ext_p4h8_noise_t4_lag1/units.json
    cd experiments/ext/coverage_theory && python p4h7_test_eval.py --dir ../../../results/ext_p4h8_noise_t4_lag1 \
        --frozen experiments/calibration/p4h8_frozen_lag1.json --expected-runs
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(REPO / "experiments"), str(HERE)]
import run_experiment as R  # noqa: E402
from p4h7_units import build_cfg  # noqa: E402
from paper4.topology import load_bank  # noqa: E402


def draw(law, rng, size):
    if law == "t4":
        return rng.standard_t(4, size=size) / np.sqrt(2.0)       # var(t4) = 2
    if law == "laplace":
        return rng.laplace(0.0, 1.0 / np.sqrt(2.0), size=size)   # var = 2 b^2 = 1
    return rng.normal(size=size)


def install(law):
    from paper4.generator import DynamicSEM, add_measurement_noise
    if law.startswith("me"):  # classical measurement noise on the observed series, variance = ratio * var(column)
        ratio = int(law[2:]) / 100.0
        orig = DynamicSEM.simulate

        def simulate_me(self, T, rng):
            return add_measurement_noise(orig(self, T, rng), ratio, rng)

        DynamicSEM.simulate = simulate_me
        return

    def simulate(self, T, rng):
        n, p = self.n_all, self.lag_max
        A = np.linalg.inv(np.eye(n) - self.B[0])
        sd = np.sqrt(self.noise_var)
        total = T + self.config.burn_in
        x = np.zeros((total + p, n))
        for t in range(p, total + p):
            acc = draw(law, rng, n) * sd
            for k in range(1, p + 1):
                acc += self.B[k] @ x[t - k]
            x[t] = A @ acc
        return x[p + self.config.burn_in:, : self.n]

    DynamicSEM.simulate = simulate


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, choices=["t4", "laplace", "me10", "me30"])
    ap.add_argument("--bank", default="P4-H8")
    ap.add_argument("--split", default="test", choices=["design", "test"])
    ap.add_argument("--lag", type=int, default=1)
    ap.add_argument("--T", default="19,30,40,80,150")
    ap.add_argument("--seed-base", type=int, default=20261116)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-topologies", type=int, default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = build_cfg(a.split, a.T, a.seed_base, a.lag, "0.2,0.5")
    topologies = load_bank(a.bank, a.split)[: a.max_topologies]
    ccfg = dict(cfg, replicates=1)
    jobs = [(ccfg, topo, t_idx, 0, None, "calibration") for t_idx, topo in enumerate(topologies)]
    t0, units = time.perf_counter(), []
    with ProcessPoolExecutor(a.workers, initializer=install, initargs=(a.law,)) as pool:
        for i, out in enumerate(pool.map(R.run_unit, jobs)):
            for p in out["pairs"]:
                if "counts" in p or not p["cell"].startswith("tolerant_v5_1|"):
                    continue
                units.append({"unit": topologies[i].id, "profile": topologies[i].profile, "cell": p["cell"],
                              "dist": p["dist"], "half": p["half"]})
            if i % 50 == 0:
                print(i, round(time.perf_counter() - t0), "s", flush=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"bank": a.bank, "split": a.split, "lag": a.lag, "T": cfg["T"], "n_units": len(topologies),
                               "seed_base": a.seed_base, "law": a.law, "records": units}))
    print("done", len(units), "records", round(time.perf_counter() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
