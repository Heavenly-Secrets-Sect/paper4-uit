"""Independent recomputation of the levboot ruling from raw runs.jsonl (verifier; does not import analyze.py)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

def multipletests(p, alpha, method):
    p=np.asarray(p); m=len(p); o=np.argsort(p); rej=np.zeros(m,bool)
    for i,j in enumerate(o):
        if p[j] <= alpha/(m-i): rej[j]=True
        else: break
    return (rej,)

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
def load(n): return [json.loads(l) for l in open(RES / n / "runs.jsonl")]
g = load("ext_r4levboot_g"); gw = load("ext_r4levboot_gw"); ev = load("ext_v51_eval")
K = lambda r: (r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])
out = {}
# pairing
a = {K(r): r for r in g if r["method"] == "tolerant_v5_1"}
b = {K(r): r for r in ev if r["method"] == "tolerant_v5_1"}
same = sum(1 for k in a if k in b and a[k]["status"] == b[k]["status"] and
           (a[k]["status"] != "ok" or (a[k]["iscore_nonnull_mean"] == b[k]["iscore_nonnull_mean"] and a[k]["n_covered_nonnull"] == b[k]["n_covered_nonnull"] and a[k]["width_kept"] == b[k]["width_kept"])))
out["pairing"] = [len(a), len(b), len(set(a) & set(b)), same]
# also check seed_base of ext_v51_eval
out["v51_eval_seed_base"] = json.load(open(RES / "ext_v51_eval/manifest.json"))["config"]["seed_base"]
rows = g + [r for r in gw if r["method"] != "tolerant_v5_1"]
by = defaultdict(dict)
for r in rows: by[K(r)][r["method"]] = r
cells = [(T, k, r) for T in (40, 80, 150) for (k, r) in [("none", 0.0)] + [(k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]]
ARMS = ["r4levboot_L2", "r4levboot_L3", "r4levboot_W3"]
SEEDFIX = 20261104
def paired(m, c, B=20000):
    d = defaultdict(list)
    for k, u in by.items():
        if k[2:] == c and m in u and u[m]["status"] == "ok" and u["tolerant_v5_1"]["status"] == "ok":
            d[k[0]].append(u[m]["iscore_nonnull_mean"] - u["tolerant_v5_1"]["iscore_nonnull_mean"])
    t = list(d); s = np.array([sum(d[x]) for x in t]); n = np.array([len(d[x]) for x in t])
    rng = np.random.default_rng(SEEDFIX); pk = rng.integers(0, len(t), (B, len(t))); bs = s[pk].sum(1) / n[pk].sum(1)
    p = min(1, 2 * min((1 + (bs <= 0).sum()) / (B + 1), (1 + (bs >= 0).sum()) / (B + 1)))
    return s.sum() / n.sum(), np.quantile(bs, .025), np.quantile(bs, .975), p, int(n.sum()), len(t)
def stat(m, c):
    us = [u for k, u in by.items() if k[2:] == c and m in u]
    ok = [u[m] for u in us if u[m]["status"] == "ok"]
    nn = sum(u["tolerant_v5_1"]["n_nonnull"] for u in us)
    return dict(n=len(us), fail=len(us) - len(ok), cov=sum(r["n_covered_nonnull"] for r in ok) / nn,
                IS=np.mean([r["iscore_nonnull_mean"] for r in ok]),
                raw=sum(r["raw_n_covered_nonnull"] for r in ok) / sum(r["n_nonnull"] for r in ok),
                h=np.mean([r["info_lev_mean"] for r in ok]), gt09=np.mean([r["info_lev_share_gt09"] for r in ok]),
                eqmax=np.mean([r["info_lev_eq_mean_max"] for r in ok]), pv=np.mean([r["info_pool_var_ratio"] for r in ok]),
                tries=sum(r["info_boot_tries"] for r in ok), succ=sum(r["info_boot_succ"] for r in ok))
primary = [(40, k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)] + [(80, "missing", 0.2), (80, "missing", 0.5)]
rest = [c for c in cells if c not in primary]
P = {(a_, c): paired(a_, c) for a_ in ARMS for c in cells}
S = {(m, c): stat(m, c) for m in ["tolerant_v5_1"] + ARMS for c in cells}
fam = [(a_, c) for a_ in ARMS for c in primary]
rej = multipletests([P[x][3] for x in fam], 0.05, "holm")[0]
lines = []
lines.append(f"pairing v5_1 g vs ext_v51_eval: n_g {len(a)} n_eval {len(b)} common {len(set(a)&set(b))} identical {same}; eval seed_base {out['v51_eval_seed_base']}")
lines.append(f"Primary Holm rejections: {rej.sum()}/24; worse-direction {sum(1 for x, r in zip(fam, rej) if r and P[x][0] > 0)}")
for a_ in ARMS:
    rr = [r for x, r in zip(fam, rej) if x[0] == a_]
    lines.append(f"  {a_}: primary rejects {sum(rr)}/8; wins {sum(1 for x, r in zip(fam, rej) if x[0]==a_ and r and P[x][0]<0)}")
    rh = multipletests([P[(a_, c)][3] for c in rest], 0.05, "holm")[0]
    lines.append(f"  {a_}: no-harm Holm rejects {rh.sum()}/13 (worse {sum(1 for c, r in zip(rest, rh) if r and P[(a_, c)][0] > 0)}); IS ratio>1.05 in {sum(1 for c in rest if S[(a_,c)]['IS']/S[('tolerant_v5_1',c)]['IS']>1.05)}")
for c in cells:
    s0 = S[("tolerant_v5_1", c)]
    lines.append(f"T{c[0]} {c[1]}-{c[2]}: v5_1 cov {s0['cov']:.3f} IS {s0['IS']:.3f} raw {s0['raw']:.3f} h {s0['h']:.3f} gt09 {s0['gt09']:.4f} eqmax {s0['eqmax']:.2f} fail {s0['fail']} tries-succ {s0['tries']-s0['succ']}")
    for a_ in ARMS:
        s = S[(a_, c)]; p = P[(a_, c)]
        lines.append(f"    {a_[10:]}: dIS {p[0]:+.3f} [{p[1]:+.3f},{p[2]:+.3f}] p {p[3]:.4f} n {p[4]} topo {p[5]} | cov {s['cov']:.3f} rawcov-diff {s['raw']-s0['raw']:+.3f} pv {s['pv']:.2f} fail {s['fail']} tries-succ {s['tries']-s['succ']}")
txt = "\n".join(lines); print(txt)
(RES / "ext_verify4_levboot" / "recompute_seed20261104.txt").write_text(txt + "\n")
