"""Independent recomputation of r4kilianbab numbers from runs.jsonl (verifier, not candidate)."""
import json, sys
from collections import defaultdict
import numpy as np
ROOT = "/Users/kietnt/Desktop/Workspace/Paper4_UIT"
def load(n): return [json.loads(l) for l in open(f"{ROOT}/results/{n}/runs.jsonl")]
rows = load("ext_r4kilianbab_eval"); old = load("ext_v51_eval")
REF="tolerant_v5_1"; K1,KBC,K0="r4kilianbab_bab","r4kilianbab_babbc","r4kilianbab_babraw"
CELLS=[("none",0.0)]+[(k,r) for k in ("extra","missing","reversed") for r in (0.2,0.5)]
ALL=[(T,k,r) for T in (40,80,150) for k,r in CELLS]
PRIM=[(T,k,r) for T in (40,80) for k in ("missing","reversed") for r in (0.2,0.5)]
OTHER=[c for c in ALL if c not in PRIM]
out={}
# pairing: compare every numeric field of v5_1 rows
def kk(r): return (r["topology"],r["replicate"],r["T"],r["kind"],r["rate"])
A={kk(r):r for r in rows if r["method"]==REF}; Bo={kk(r):r for r in old if r["method"]==REF}
nd=0; fields_checked=set()
for k in A:
    a,b=A[k],Bo.get(k)
    if b is None: nd+=1; continue
    same=True
    for f,v in b.items():
        if isinstance(v,(int,float)) and not isinstance(v,bool) and f in a:
            fields_checked.add(f)
            if a[f] is None or abs(a[f]-v)>1e-12: same=False
        elif f in a and a[f]!=v: same=False
    nd+= (not same)
out["pairing"]={"n_new":len(A),"n_old":len(Bo),"n_diff_allfields":nd,"n_fields":len(fields_checked)}
idx={(kk(r),r["method"]):r for r in rows}
def cell(m,c):
    g=[r for r in rows if r["method"]==m and (r["T"],r["kind"],r["rate"])==c]
    ok=[r for r in g if r["status"]=="ok"]
    return {"n":len(g),"n_ok":len(ok),"cov":sum(r["n_covered_nonnull"] for r in ok)/sum(r["n_nonnull"] for r in ok),
            "IS":float(np.mean([r["iscore_nonnull_mean"] for r in ok])),
            "t0":sum(r.get("x_n_miss_toward0",0) for r in ok),"aw":sum(r.get("x_n_miss_away",0) for r in ok)}
def paired(m,c,B=20000,seed=20261104):
    d=defaultdict(list)
    for (k,meth),r in idx.items():
        if meth!=m or k[2:]!=c or r["status"]!="ok": continue
        o=idx.get((k,REF))
        if o and o["status"]=="ok": d[k[0]].append(r["iscore_nonnull_mean"]-o["iscore_nonnull_mean"])
    t=sorted(d); s=np.array([sum(d[x]) for x in t]); n=np.array([len(d[x]) for x in t])
    rng=np.random.default_rng(seed); p=rng.integers(0,len(t),(B,len(t)))
    bt=s[p].sum(1)/n[p].sum(1)
    return {"est":s.sum()/n.sum(),"lo":float(np.quantile(bt,.025)),"hi":float(np.quantile(bt,.975)),
            "pl":(1+(bt>=0).sum())/(B+1),"pg":(1+(bt<=0).sum())/(B+1),"npairs":int(n.sum()),"ncl":len(t)}
def holm(p,a=0.05):
    o=np.argsort(p); m=len(p); rej=[False]*m
    for i,j in enumerate(o):
        if p[j]<=a/(m-i): rej[j]=True
        else: break
    return rej
S={(m,c):cell(m,c) for m in (REF,K1,KBC,K0,"oracle") for c in ALL}
P={(m,c):paired(m,c) for m in (K1,KBC,K0) for c in ALL}
# alt seed robustness
P2={(m,c):paired(m,c,seed=1) for m in (K1,KBC) for c in PRIM+[(80,"reversed",0.5)]}
res={}
for arm in (K1,KBC):
    pl=[P[(arm,c)]["pl"] for c in PRIM]; pg=[P[(arm,c)]["pg"] for c in PRIM]
    pgo=[P[(arm,c)]["pg"] for c in OTHER]
    rl,rg,rgo=holm(pl),holm(pg),holm(pgo)
    wins=sum(rl[i] and S[(arm,c)]["cov"]>=.9 and S[(arm,c)]["n_ok"]>=S[(REF,c)]["n_ok"] for i,c in enumerate(PRIM))
    ratio=[S[(arm,c)]["IS"]/S[(REF,c)]["IS"] for c in OTHER]
    res[arm]={"wins_holm":wins,"wins_raw":sum(p<=.05 for p in pl),"primary_worse_holm":sum(rg),"primary_worse_raw":sum(p<=.05 for p in pg),
      "other_ratio_gt105":sum(r>1.05 for r in ratio),"other_worse_holm":sum(rgo),"other_worse_raw":sum(p<=.05 for p in pgo),
      "cov_primary_ok":all(S[(arm,c)]["cov"]>=.9 for c in PRIM),
      "other_cov_fail":sum(not(S[(arm,c)]["cov"]>=.9 or S[(REF,c)]["cov"]<.9) for c in OTHER),
      "nok_ge_ref_all":all(S[(arm,c)]["n_ok"]>=S[(REF,c)]["n_ok"] for c in ALL),
      "trip_pg":P[(arm,(80,"reversed",0.5))]["pg"],"trip_holm":rg[PRIM.index((80,"reversed",0.5))],
      "primary":{f"{c}":[round(S[(REF,c)]["IS"],3),round(S[(arm,c)]["IS"],3),round(P[(arm,c)]["est"],3),round(P[(arm,c)]["lo"],3),round(P[(arm,c)]["hi"],3),round(S[(arm,c)]["cov"],3),round(S[(REF,c)]["cov"],3)] for c in PRIM},
      "primary_alt_seed_pg":{f"{c}":P2[(arm,c)]["pg"] for c in PRIM},
      "other_ratio":{f"{c}":round(r,4) for c,r in zip(OTHER,ratio)}}
res[K0]={"cov_fail":[ (f"{c}",round(S[(K0,c)]["cov"],3)) for c in ALL if S[(K0,c)]["cov"]<.9],
         "nonineq":sum(P[(K0,c)]["hi"]<0.05*S[(REF,c)]["IS"] for c in PRIM),
         "primary_dIS":{f"{c}":[round(P[(K0,c)]["est"],3),round(P[(K0,c)]["hi"],3),round(0.05*S[(REF,c)]["IS"],3)] for c in PRIM}}
fam=[P[(a,c)]["pl"] for a in (K1,KBC) for c in PRIM]; res["overlay_rej"]=sum(holm(fam))
res["miss_share_toward0"]={f"{c}":{m:round(S[(m,c)]["t0"]/max(1,S[(m,c)]["t0"]+S[(m,c)]["aw"]),3) for m in (REF,K1,"oracle")} for c in PRIM}
res["n_ok"]={f"{c}":{m:S[(m,c)]["n_ok"] for m in (REF,K1,KBC,K0)} for c in ALL}
# radius & shrink
for T in (40,80,150):
    g=[r for r in rows if r["method"]==K1 and r["T"]==T and r["status"]=="ok"]
    res[f"radius_T{T}"]=[round(np.mean([r["info_bab_radius_raw"] for r in g]),3),round(np.mean([r["info_bab_radius_c"] for r in g]),3)]
    res[f"draw_shrunk_T{T}"]=[round(min(np.mean([r["info_bab_share_draws_shrunk"] for r in g if (r["kind"],r["rate"])==c]) for c in CELLS),3),
                              round(max(np.mean([r["info_bab_share_draws_shrunk"] for r in g if (r["kind"],r["rate"])==c]) for c in CELLS),3)]
    res[f"data_shrunk_T{T}"]=[round(min(np.mean([r["info_bab_data_flag"]==1 for r in g if (r["kind"],r["rate"])==c]) for c in CELLS),3),
                              round(max(np.mean([r["info_bab_data_flag"]==1 for r in g if (r["kind"],r["rate"])==c]) for c in CELLS),3)]
out["res"]=res
json.dump(out,open(f"{ROOT}/results/ext_verify4_kilianbab/recompute.json","w"),indent=1,default=str)
print(json.dumps(out,indent=1,default=str))
