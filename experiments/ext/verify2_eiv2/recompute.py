"""Independent recomputation of the eiv2 rule numbers from runs.jsonl (own code, several bootstrap seeds)."""
import json, sys
from collections import defaultdict
import numpy as np
R = "results/ext_eiv2_eval/runs.jsonl"
rows = [json.loads(l) for l in open(R)]
print(f"# source {R}: {len(rows)} rows; statuses:", {m: sum(r['status']=='ok' for r in rows if r['method']==m) for m in sorted({r['method'] for r in rows})})
g = defaultdict(list)
for r in rows: g[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)
CELLS = [(T, k) for T in (80, 150) for k in ("none", "missing", "reversed")]
def cov(rs): return sum(r["n_covered_nonnull"] for r in rs if r["status"]=="ok") / sum(r["n_nonnull"] for r in rs if r["status"]=="ok")
def IS(rs): return np.mean([r["iscore_nonnull_mean"] for r in rs if r["status"]=="ok"])
def holm(p, a=0.05):
    p = np.asarray(p); o = np.argsort(p); m = len(p); rej = np.zeros(m, bool)
    for k, i in enumerate(o):
        if p[i] <= a/(m-k): rej[i] = True
        else: break
    return rej
# arrays per topology for cluster bootstrap
def topo_arrays(rs):
    d = defaultdict(lambda: [0, 0])
    for r in rs:
        if r["status"]=="ok": d[r["topology"]][0] += r["n_covered_nonnull"]; d[r["topology"]][1] += r["n_nonnull"]
    t = sorted(d); return t, np.array([d[x][0] for x in t]), np.array([d[x][1] for x in t])
print("\n## Condition 1: coverage of tolerant_eiv2 (noise cells)")
covs = []
for sc in ("noise0.1", "noise0.3"):
    for T, k in CELLS:
        c = cov(g[(sc, T, k, "tolerant_eiv2")]); covs.append(((sc, T, k), c))
        print(f"  {sc} T{T} {k}: {c:.4f} {'PASS' if c>=0.90 else 'FAIL'}  (n runs {len(g[(sc,T,k,'tolerant_eiv2')])})")
print(f"  pass {sum(c>=0.90 for _, c in covs)}/12")
for seed in (0, 1, 2, 12345):
    rng = np.random.default_rng(seed); ph, pl = [], []
    for (sc, T, k), c in covs:
        t, a, b = topo_arrays(g[(sc, T, k, "tolerant_eiv2")])
        idx = rng.integers(0, len(t), (4000, len(t)))
        bs = a[idx].sum(1) / b[idx].sum(1)
        ph.append((bs <= 0.9).mean()); pl.append((bs >= 0.9).mean())
    print(f"  seed {seed} B=4000: Holm above {holm(ph).sum()}/12, below {holm(pl).sum()}/12; unadj above {(np.array(ph)<0.05).sum()}, below {(np.array(pl)<0.05).sum()}; p_below(T80 rev n0.3) {pl[8]:.3f}")
print("\n## Condition 2: clean IS ratio eiv2 / v4")
for T, k in CELLS:
    a, b = IS(g[("clean", T, k, "tolerant_eiv2")]), IS(g[("clean", T, k, "tolerant_v4")])
    print(f"  T{T} {k}: {a:.3f}/{b:.3f} = {a/b:.3f}")
print("\n## Paired IS eiv2 - v4, seed 1, B=4000; Holm within each scenario")
for sc in ("clean", "noise0.1", "noise0.3"):
    res = []
    for T, k in CELLS:
        ref = {(r["topology"], r["replicate"]): r["iscore_nonnull_mean"] for r in g[(sc, T, k, "tolerant_v4")] if r["status"]=="ok"}
        d = defaultdict(list)
        for r in g[(sc, T, k, "tolerant_eiv2")]:
            if r["status"]=="ok": d[r["topology"]].append(r["iscore_nonnull_mean"] - ref[(r["topology"], r["replicate"])])
        t = sorted(d); s = np.array([sum(d[x]) for x in t]); nn = np.array([len(d[x]) for x in t])
        idx = np.random.default_rng(1).integers(0, len(t), (4000, len(t)))
        bs = s[idx].sum(1)/nn[idx].sum(1); est = s.sum()/nn.sum()
        p = min(1, 2*min((bs<=0).mean(), (bs>=0).mean())); res.append((T, k, est, *np.quantile(bs, [.025, .975]), p))
    rej = holm([x[-1] for x in res])
    print(f"  {sc}: " + "; ".join(f"T{T} {k} {e:+.2f} [{lo:+.2f},{hi:+.2f}]{'*' if h else ''}" for (T, k, e, lo, hi, p), h in zip(res, rej)))
    print(f"    better(Holm) {sum(h and x[2]<0 for x,h in zip(res,rej))}/6, worse(Holm) {sum(h and x[2]>0 for x,h in zip(res,rej))}/6")
print("\n## Null pairs: median C_abs_spurious eiv2 vs v4, and mean iscore_null_mean")
hi_c = hi_i = 0
for sc in ("clean", "noise0.1", "noise0.3"):
    for T, k in CELLS:
        m = {}
        for meth in ("tolerant_v4", "tolerant_eiv2"):
            rs = [r for r in g[(sc, T, k, meth)] if r["status"]=="ok"]
            m[meth] = (np.median([r["C_abs_spurious"] for r in rs if r["C_abs_spurious"] is not None]), np.mean([r["iscore_null_mean"] for r in rs if r["iscore_null_mean"] is not None]))
        hi_c += m["tolerant_eiv2"][0] > m["tolerant_v4"][0]; hi_i += m["tolerant_eiv2"][1] > m["tolerant_v4"][1]
        if (sc, T, k) in {("noise0.3", 80, "none"), ("noise0.3", 150, "none"), ("clean", 80, "missing")}:
            print(f"  {sc} T{T} {k}: |C| {m['tolerant_v4'][0]:.3f} -> {m['tolerant_eiv2'][0]:.3f}; IS0 {m['tolerant_v4'][1]:.3f} -> {m['tolerant_eiv2'][1]:.3f}")
print(f"  median |C| higher in {hi_c}/18; iscore_null_mean higher in {hi_i}/18")
print("\n## r_hat")
for sc in ("clean", "noise0.1", "noise0.3"):
    for T in (80, 150):
        v = np.array([r["info_r_hat"] for (s, t, k, m), rs in g.items() if s==sc and t==T and m=="tolerant_eiv2" for r in rs if r["status"]=="ok"])
        print(f"  {sc} T{T}: {v.mean():.3f} ({v.std():.3f}) n={len(v)}")
# hetero reproducibility
h = [json.loads(l) for l in open("results/ext_eiv2_hetero/runs.jsonl")]
key = lambda r: (r["scenario"], r["T"], r["kind"], r["method"], r["topology"], r["replicate"])
ev = {key(r): r for r in rows if r["scenario"]=="noise0.3"}
shared = [r for r in h if key(r) in ev]
print(f"\n## hetero: {len(h)} rows; shared noise0.3 rows {len(shared)}; identical {sum(json.dumps(r, sort_keys=True)==json.dumps(ev[key(r)], sort_keys=True) for r in shared)}")
hg = defaultdict(list)
for r in h: hg[(r["scenario"], r["T"], r["kind"], r["method"])].append(r)
for m in ("tolerant_v4", "tolerant_eiv", "tolerant_eiv2"):
    cs = [cov(hg[("het0.3", T, k, m)]) for T, k in CELLS]
    cn = [cov(hg[("noise0.3", T, k, m)]) for T, k in CELLS]
    print(f"  {m}: het0.3 cov>=0.90 {sum(c>=0.9 for c in cs)}/6 range {min(cs):.3f}-{max(cs):.3f}; noise0.3 cov<0.90 in {sum(c<0.9 for c in cn)}/6")
