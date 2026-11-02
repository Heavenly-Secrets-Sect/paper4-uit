"""Verifier: known-truth checks of ng_evidence (independent seeds), incl. sign vs exact LR and failure modes."""
import sys, json, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments/ext/r4ngorient"))
from paper4.ext_r4ngorient import ng_evidence
import laws

rng = np.random.default_rng(777001)
out = {}
def exact_lr(x, y, law):
    # exact log-lik ratio x->y minus y->x under a known Laplace density for standardized sources (LiNGAM, HS 2013 eq LR)
    x = (x - x.mean()) / x.std(); y = (y - y.mean()) / y.std()
    rho = np.mean(x * y)
    G = lambda u: -np.sqrt(2) * np.abs(u)  # log Laplace unit var (up to const)
    s = math.sqrt(1 - rho ** 2)
    lxy = np.mean(G(x) + G((y - rho * x) / s))
    lyx = np.mean(G(y) + G((x - rho * y) / s))
    return lxy - lyx

def cell(lawx, lawe, b, m, reps=1000, sx=1.0, se=1.0):
    corr = wrong = gate = 0; agree = []
    for _ in range(reps):
        x = laws.sample(rng, lawx, m, sx)
        e = laws.sample(rng, lawe, m, se)
        y = b * x + e
        ev = ng_evidence(x, y)
        gate += ev["gate"]; corr += ev["p"] > 0.5; wrong += ev["p"] < 0.5
        if lawx == lawe == "laplace" and ev["gate"]:
            agree.append(np.sign(ev["R"]) == np.sign(exact_lr(x, y, "laplace")))
    return {"gate": gate / reps, "correct": corr / reps, "wrong": wrong / reps,
            "agree_exactLR_given_gate": float(np.mean(agree)) if agree else None}

for law in ("laplace", "t5", "uniform", "gauss"):
    for m in (78, 148):
        out[f"{law}|{law}|b0.6|m{m}"] = cell(law, law, 0.6, m)
# skew: same-sign vs opposite-sign skew of cause and noise
for m in (148, 400):
    out[f"skewexp(+)|skewexp(+)|m{m}"] = cell("skewexp", "skewexp", 0.6, m, sx=1, se=1)
    out[f"skewexp(+)|skewexp(-)|m{m}"] = cell("skewexp", "skewexp", 0.6, m, sx=1, se=-1)
    # caveat: symmetric cause, skewed effect noise
    out[f"laplace|skewexp|m{m}"] = cell("laplace", "skewexp", 0.6, m)
    out[f"uniform|skewexp|m{m}"] = cell("uniform", "skewexp", 0.6, m)
    out[f"skewexp|laplace|m{m}"] = cell("skewexp", "laplace", 0.6, m)
    out[f"gauss|laplace|m{m}"] = cell("gauss", "laplace", 0.6, m)
    out[f"laplace|gauss|m{m}"] = cell("laplace", "gauss", 0.6, m)
    out[f"uniform|laplace|m{m}"] = cell("uniform", "laplace", 0.6, m)
for k, v in out.items():
    print(k, v)
(ROOT / "results/ext_verify4_ngorient/t1_evidence.json").write_text(json.dumps(out, indent=1))
