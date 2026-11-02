"""Skeptic check of results/ext_eiv_a1noise: independent recomputation of cited numbers."""
import json, sys
from collections import defaultdict
import numpy as np
rows=[json.loads(l) for l in open("results/ext_eiv_a1noise/runs.jsonl")]
g=defaultdict(list)
for r in rows: g[(r["scenario"],r["T"],r["kind"],r["method"])].append(r)
def cov(rs): ok=[r for r in rs if r["status"]=="ok"]; return sum(r["n_covered_nonnull"] for r in ok)/sum(r["n_nonnull"] for r in ok)
def covmean(rs): return np.mean([r["coverage_nonnull"] for r in rs if r["status"]=="ok"])
def IS(rs): return np.mean([r["iscore_nonnull_mean"] for r in rs if r["status"]=="ok"])
def nullcov(rs):
    d=sum(r["n_null_reach"] for r in rs); return sum(r["n_covered_null_reach"] for r in rs)/d if d else float('nan')
def spur(rs):
    v=[r["C_abs_spurious"] for r in rs if r.get("C_abs_spurious") is not None]; return np.mean(v) if v else float('nan')
rng=np.random.default_rng(1)
def clus(sc,T,k,a,b,B=4000):
    A={ (r["topology"],r["replicate"]):r["iscore_nonnull_mean"] for r in g[(sc,T,k,a)]}
    Bm={ (r["topology"],r["replicate"]):r["iscore_nonnull_mean"] for r in g[(sc,T,k,b)]}
    d=defaultdict(list)
    for key in A: d[key[0]].append(A[key]-Bm[key])
    tops=list(d); arr=[np.array(d[t]) for t in tops]
    est=np.mean(np.concatenate(arr))
    bs=[]
    for _ in range(B):
        idx=rng.integers(0,len(tops),len(tops)); bs.append(np.mean(np.concatenate([arr[i] for i in idx])))
    return est,np.percentile(bs,2.5),np.percentile(bs,97.5)
def covci(sc,T,k,m,B=4000):
    d=defaultdict(lambda:[0,0])
    for r in g[(sc,T,k,m)]: d[r["topology"]][0]+=r["n_covered_nonnull"]; d[r["topology"]][1]+=r["n_nonnull"]
    a=np.array(list(d.values()),float); bs=[]
    for _ in range(B):
        i=rng.integers(0,len(a),len(a)); bs.append(a[i,0].sum()/a[i,1].sum())
    return np.percentile(bs,2.5),np.percentile(bs,97.5)
print("scenario T kind | v4 cov/IS | eiv cov/IS (pooled) | eiv cov per-run mean | eiv cov 95% topo-CI | nullcov v4/eiv | spur v4/eiv")
for sc in ("clean","noise0.1","noise0.3"):
  for T in (80,150):
    for k in ("none","missing","reversed"):
      v=g[(sc,T,k,"tolerant_v4")]; e=g[(sc,T,k,"tolerant_eiv")]
      lo,hi=covci(sc,T,k,"tolerant_eiv")
      print(f"{sc} {T} {k} | {cov(v):.3f}/{IS(v):.2f} | {cov(e):.3f}/{IS(e):.2f} | {covmean(e):.3f} | [{lo:.3f},{hi:.3f}] | {nullcov(v):.3f}/{nullcov(e):.3f} | {spur(v):.3f}/{spur(e):.3f}")
print("\nPaired IS eiv - v4 and eiv - plugin (cluster bootstrap by topology)")
for sc in ("clean","noise0.1","noise0.3"):
  for T in (80,150):
    for k in ("none","missing","reversed"):
      a=clus(sc,T,k,"tolerant_eiv","tolerant_v4"); b=clus(sc,T,k,"tolerant_eiv","plugin")
      print(f"{sc} {T} {k}: vs v4 {a[0]:+.2f} [{a[1]:+.2f},{a[2]:+.2f}]  vs plugin {b[0]:+.2f} [{b[1]:+.2f},{b[2]:+.2f}]")
print("\nr_hat / r_used / r_boot_mean by scenario,T")
for sc in ("clean","noise0.1","noise0.3"):
  for T in (80,150):
    e=[r for (s,t,k,m),rs in g.items() if s==sc and t==T and m=="tolerant_eiv" for r in rs]
    ks=[x for x in e[0] if x.startswith("info")]
    vals={kk:np.mean([r[kk] for r in e if r.get(kk) is not None]) for kk in ks if isinstance(e[0][kk],(int,float))}
    print(sc,T,{kk:round(float(v),3) for kk,v in vals.items()})
