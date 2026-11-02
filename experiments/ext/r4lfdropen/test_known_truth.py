"""Known-truth and identity tests for ext_r4lfdropen (no D-07 data; synthetic or D-07H development only).

T1  EM with pi0 fixed recovers mu, s of a simulated two-groups mixture (m = 4000, pi0 = 0.9, N(3, 1)).
T2  P formula equals the design's closed form 1 - pi0 phi(z) / (pi0 phi(z) + (1 - pi0) phi((z - mu)/s)/s).
T3  Edge cases: m = 0, m = 1 (pi0 = 1 -> P = 0), k >= m (pi0 = 1/m), s floor 0.5.
T4  select_open_lfdr: forced top-k floor, data rule P >= 0.5, Bernoulli draws with P = 0/1 limits.
T5  split_streams: runner-tagged generator -> main stream equals v5_1's stream; other generators untouched.
T6  Identity with tolerant_v5_1 when no missing edge is stated (none / extra / reversed), and the
    targeted branch differs only through step (2): with the selection monkeypatched to v5_1's rule
    the candidate reproduces v5_1 exactly (D-07H development topology, runner seeds of the calibration phase).
Run: /Users/kietnt/miniconda3/bin/python experiments/ext/r4lfdropen/test_known_truth.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import run_experiment as RE  # noqa: E402
from paper4 import ext_narrow, ext_r4lfdropen as L, ext_v51  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

out = {}


def check(name, cond, detail=""):
    out[name] = {"pass": bool(cond), "detail": detail}
    print(("PASS " if cond else "FAIL ") + name, detail)


# T1
rng = np.random.default_rng(1)
m, pi0, mu, s = 4000, 0.9, 3.0, 1.0
z = np.where(rng.random(m) < pi0, rng.normal(0, 1, m), rng.normal(mu, s, m))
from scipy.stats import norm as _n  # noqa: E402  (test only)
p = _n.sf(z)
P, em = L.lfdr_posterior(p, int(round((1 - pi0) * m)))
check("T1_em_recovers", abs(em["mu"] - mu) < 0.15 and abs(em["s"] - s) < 0.15, f"mu {em['mu']:.3f} s {em['s']:.3f} it {em['iters']}")

# T2
zc = np.array([L._ND.inv_cdf(1 - min(max(x, 1e-12), 1 - 1e-12)) for x in p])
pi0f = em["pi0"]
closed = 1 - pi0f * L._phi(zc) / (pi0f * L._phi(zc) + (1 - pi0f) * L._phi((zc - em["mu"]) / em["s"]) / em["s"])
check("T2_closed_form", np.max(np.abs(closed - P)) < 1e-12, f"max diff {np.max(np.abs(closed - P)):.2e}")

# T3
P0, e0 = L.lfdr_posterior([], 3)
P1, e1 = L.lfdr_posterior([1e-9], 3)
P2, e2 = L.lfdr_posterior([1e-9, 0.5, 0.9], 10)
P3, e3 = L.lfdr_posterior(list(np.linspace(0.01, 0.99, 50)), 2)
check("T3_edges", len(P0) == 0 and e1["pi0"] == 1.0 and P1[0] == 0 and abs(e2["pi0"] - 1 / 3) < 1e-12 and e3["s"] >= 0.5,
      f"pi0(m=3,k=10) {e2['pi0']:.3f}; s(flat) {e3['s']:.3f}; P(flat max) {P3.max():.3f}")

# T4 on a D-07H development topology (calibration-phase seeds)
cfg = json.loads((ROOT / "experiments/configs/ext_v51_eval.json").read_text())
topos = load_bank("D-07H", "development")
gen = RE.generator_config(cfg)
unit = cfg["seed_base"] + 500_000 + 0
sem = build_dynamic_sem(topos[0], gen, np.random.default_rng([unit, 0]))
ccfg = dict(cfg, damage={"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]})
skels = RE.unit_skeletons(sem, unit, ccfg)
data = sem.simulate(40, np.random.default_rng([unit, 2, 40]))
sk = RE.public(skels[("missing", 0.2)])
k = sk.damage["k"]
op, tests, P, em = L.select_open_lfdr(data, sk, 2, k, None)
topk = [(u, v) for _, u, v in tests[:k]]
rule = topk + [(tests[i][1], tests[i][2]) for i in range(k, len(tests)) if P[i] >= 0.5]
ok_floor = op[:k] == topk and op == rule
class _One:  # Bernoulli limits: random() always 0 -> every P > 0 taken; always 1 -> none taken
    def __init__(self, v): self.v = v
    def random(self, n): return np.full(n, self.v)
opA, *_ = L.select_open_lfdr(data, sk, 2, k, _One(0.0))
opB, *_ = L.select_open_lfdr(data, sk, 2, k, _One(1.0))
check("T4_select", ok_floor and opB == topk and len(opA) == k + int((P[k:] > 0).sum()),
      f"m {len(tests)} k {k} open_data {len(op)} v5_1 K {len(ext_narrow.select_open(data, sk, 2, k, 3.0, 0.10))} mu {em['mu']:.2f} s {em['s']:.2f}")

# T5
tag_own, tag_ref = RE.ext_seed(L.NAME), RE.ext_seed(L.REF_NAME)
check("T5_tags", tag_own == L._stream_tag(L.NAME) and tag_ref == L._stream_tag(L.REF_NAME), f"{tag_own} {tag_ref}")
g = np.random.default_rng([unit, 3, 40, 3, tag_own])
main, bern, crn = L.split_streams(g)
ref = np.random.default_rng([unit, 3, 40, 3, tag_ref])
check("T5_crn", crn and main.random() == ref.random() and bern is g, "")
g2 = np.random.default_rng(7)
m2, b2, c2 = L.split_streams(g2)
check("T5_fallback", (not c2) and m2 is g2 and b2 is not g2, "")

# T6 identity
same = []
for c_idx, cell in enumerate(skels):
    if cell[0] == "missing":
        continue
    s_pub = RE.public(skels[cell])
    a = ext_v51.tolerant_v5_1(data, s_pub, 2, 4, 49, np.random.default_rng([unit, 3, 40, c_idx, tag_ref]))
    b = L.tolerant_v5_1_lfdr(data, s_pub, 2, 4, 49, np.random.default_rng([unit, 3, 40, c_idx, tag_own]))
    same.append(all(np.array_equal(getattr(a, f), getattr(b, f)) for f in ("C", "lo", "hi")))
check("T6_identity_nonmissing", all(same) and len(same) == 5, f"{sum(same)}/{len(same)}")

# T6b: with step (2) forced to v5_1's rule, the targeted branch equals v5_1 exactly
orig = L.select_open_lfdr
L.select_open_lfdr = lambda x, s_, lm, kk, br: (ext_narrow.select_open(x, s_, lm, kk, 3.0, 0.10), [(0.5, 0, 1)], np.zeros(1), {"pi0": 1.0, "mu": None, "s": None, "iters": 0})
same_b = []
for c_idx, cell in enumerate(skels):
    if cell[0] != "missing":
        continue
    s_pub = RE.public(skels[cell])
    a = ext_v51.tolerant_v5_1(data, s_pub, 2, 4, 49, np.random.default_rng([unit, 3, 40, c_idx, tag_ref]))
    b = L.tolerant_v5_1_lfdr(data, s_pub, 2, 4, 49, np.random.default_rng([unit, 3, 40, c_idx, tag_own]))
    same_b.append(all(np.array_equal(getattr(a, f), getattr(b, f)) for f in ("C", "lo", "hi")))
L.select_open_lfdr = orig
check("T6b_only_step2_differs", all(same_b) and len(same_b) == 2, f"{sum(same_b)}/{len(same_b)}")

(ROOT / "results/ext_r4lfdropen_tests").mkdir(parents=True, exist_ok=True)
(ROOT / "results/ext_r4lfdropen_tests/known_truth.json").write_text(json.dumps(out, indent=2))
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
