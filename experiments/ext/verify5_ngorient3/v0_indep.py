"""Skeptic: independent re-implementation of NG-A v3 evidence from the spec (docs/ext/r5ngorient3.md 3.1)
and an independent V0 slice (own law samplers, own seed). Also compares to the module's ng_evidence3."""
import itertools, json, math, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from paper4.ext_r5ngorient3 import ng_evidence3 as theirs

A4 = (math.gamma(.25) / math.gamma(.75)) ** 2
def Gsup(u): return -np.log(np.cosh(np.pi * u / 2))
def Gsub(u): return -(u ** 4) / A4
def z(v):
    v = np.asarray(v, float); c = v - v.mean(); s = np.sqrt((c * c).mean()); return c / s
def mine(xr, yr):
    x, y = z(xr), z(yr); m = len(x)
    sk = [np.mean(x**3), np.mean(y**3)]; ek = [np.mean(x**4) - 3, np.mean(y**4) - 3]
    pj = [math.exp(-m * (s*s/6 + k*k/24) / 2) for s, k in zip(sk, ek)]
    if not (1 - (1 - min(pj)) ** 2 < 0.10): return 0.5, False
    S = m * (sk[0]**2 + sk[1]**2) / 6; K = m * (ek[0]**2 + ek[1]**2) / 24
    skew = S >= K
    sgn = [(-1. if s < 0 else 1.) for s in sk] if skew else [1., 1.]
    gx = Gsup if ek[0] >= 0 else Gsub; gy = Gsup if ek[1] >= 0 else Gsub
    xr, yr = np.asarray(xr, float), np.asarray(yr, float)
    def st(idx):
        a, b = sgn[0] * z(xr[idx]), sgn[1] * z(yr[idx]); r = np.mean(a * b)
        if skew: return r * np.mean(a*a*b - a*b*b)
        s = math.sqrt(1 - r*r); ryx = (b - r*a)/s; rxy = (a - r*b)/s
        return np.mean(gx(a) - gx(rxy) + gy(ryx) - gy(b))
    R = st(np.arange(m))
    reps = np.array([st(np.setdiff1d(np.arange(m), blk)) for blk in np.array_split(np.arange(m), 10)])
    se = math.sqrt(9/10 * ((reps - reps.mean())**2).sum())
    p = 0.5 * math.erfc(-(R/se) / math.sqrt(2))
    return min(max(p, .05), .95), True

def draw(rng, law, m):
    if law == "laplace": return rng.laplace(0, 1/math.sqrt(2), m)
    if law == "t5": return rng.standard_t(5, m) * math.sqrt(3/5)
    if law == "sexp+": return rng.exponential(1, m) - 1
    if law == "sexp-": return 1 - rng.exponential(1, m)
    if law == "unif": return rng.uniform(-math.sqrt(3), math.sqrt(3), m)
    if law == "gauss": return rng.normal(size=m)
W = {"laplace": .25, "t5": .25, "sexp+": .125, "sexp-": .125, "unif": .25}
rng = np.random.default_rng(99112233)
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 400
out = {}; maxdiff = 0.0
for b, m in [(0.6, 148), (0.6, 400)]:
    num = den = 0.0; pairs = {}
    for c, n in itertools.product(W, W):
        op = wr = 0
        for _ in range(REPS):
            x = draw(rng, c, m); y = b * x + draw(rng, n, m)
            p, g = mine(x, y)
            t = theirs(x, y)
            maxdiff = max(maxdiff, abs(t["p"] - p)); assert t["gate"] == g
            op += g; wr += p < 0.5
        pairs[f"{c}->{n}"] = wr / op if op else 0.0
        num += W[c]*W[n]*wr; den += W[c]*W[n]*op
    out[f"b{b}_m{m}"] = {"mix_wrong_cond": num/den, "worst": max(pairs.items(), key=lambda kv: kv[1]), "pairs": pairs}
gg = []
for b, m in [(0.6, 148), (0.3, 400)]:
    ps = [mine(rng.normal(size=m), None) if False else None for _ in range(0)]
    op = 0; sp = 0.0
    for _ in range(REPS):
        x = rng.normal(size=m); y = b*x + rng.normal(size=m); p, g = mine(x, y); op += g; sp += p
    gg.append({"b": b, "m": m, "gate_open": op/REPS, "mean_p": sp/REPS})
out["gauss"] = gg; out["max_abs_p_diff_vs_module"] = maxdiff; out["reps"] = REPS; out["seed"] = 99112233
Path(ROOT/"results/ext_verify5_ngorient3/v0_indep.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if k != "b0.6_m148" and k != "b0.6_m400" else {kk: vv for kk, vv in v.items() if kk != "pairs"}) for k, v in out.items()}, indent=1))
