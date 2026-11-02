"""Independent recomputation (skeptic) of r4leadlag rule numbers."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT"); RES = ROOT/"results"
OUT = RES/"ext_verify4_leadlag"
REF="tolerant_v5_1"; VAR={"A":"tolerant_v5_1_leadlag","D":"tolerant_v5_1_leadlag_skel"}
def load(n): return [json.loads(l) for l in open(RES/n/"runs.jsonl")]
rows = load("ext_r4leadlag_eval_clean")+load("ext_r4leadlag_eval_latent")+load("ext_r4leadlag_eval_noise")
K=lambda r:(r.get("scenario","clean"),r["topology"],r["replicate"],r["T"],r["kind"],r["rate"])
D=defaultdict(dict)
for r in rows: D[r["method"]][K(r)]=r
print({m:len(v) for m,v in D.items()})
print("failed:",{m:sum(r["status"]!="ok" for r in v.values()) for m,v in D.items()})
# V1
for t,m in VAR.items():
    tot=same=0
    for k,r in D[REF].items():
        if k[4]=="missing": continue
        x=D[m].get(k); tot+=1
        if x and x["status"]==r["status"]=="ok" and x["iscore_nonnull_mean"]==r["iscore_nonnull_mean"] and x["n_covered_nonnull"]==r["n_covered_nonnull"]: same+=1
    print("V1",t,same,"/",tot)
# pairing with stored
for st in ["ext_v51_eval","ext_v51_a1","ext_v51_a1t40"]:
    S={K(r):r for r in load(st) if r["method"]==REF}
    sh=[k for k in S if k in D[REF]]
    eq=sum(abs(S[k]["iscore_nonnull_mean"]-D[REF][k]["iscore_nonnull_mean"])<1e-12 and S[k]["n_covered_nonnull"]==D[REF][k]["n_covered_nonnull"] for k in sh)
    print("pair",st,eq,"/",len(sh),"stored v51 rows",len(S))
def cell(sc,T,rate): return sorted(k for k in D[REF] if k[0]==sc and k[3]==T and k[4]=="missing" and k[5]==rate)
def stat(m,keys,B=20000,seed=777):
    d=defaultdict(list)
    for k in keys: d[k[1]].append(D[m][k]["iscore_nonnull_mean"]-D[REF][k]["iscore_nonnull_mean"])
    tp=list(d); s=np.array([sum(d[t]) for t in tp]); c=np.array([len(d[t]) for t in tp])
    est=s.sum()/c.sum(); rng=np.random.default_rng(seed); pk=rng.integers(0,len(tp),(B,len(tp)))
    b=s[pk].sum(1)/c[pk].sum(1)
    p=min(1,2*min((1+(b>=0).sum())/(B+1),(1+(b<=0).sum())/(B+1)))
    cov=sum(D[m][k]["n_covered_nonnull"] for k in keys)/sum(D[m][k]["n_nonnull"] for k in keys)
    covr=sum(D[REF][k]["n_covered_nonnull"] for k in keys)/sum(D[REF][k]["n_nonnull"] for k in keys)
    ism=np.mean([D[m][k]["iscore_nonnull_mean"] for k in keys]); isr=np.mean([D[REF][k]["iscore_nonnull_mean"] for k in keys])
    return dict(est=est,lo=np.quantile(b,.025),hi=np.quantile(b,.975),p=p,cov=cov,covref=covr,ratio=ism/isr,isref=isr,n=int(c.sum()))
def holm(ps,a=.05):
    o=np.argsort(ps); rej=[False]*len(ps)
    for i,j in enumerate(o):
        if ps[j]<=a/(len(ps)-i): rej[j]=True
        else: break
    return rej
PRIM=[(sc,T,r) for sc in ("latent1","latent3") for r in (.2,.5) for T in (80,150)]
NOH=[("clean",T,r) for T in (40,80,150) for r in (.2,.5)]+[(sc,40,r) for sc in ("latent1","latent3") for r in (.2,.5)]
out={}
allp=[]
for t,m in VAR.items():
    P=[stat(m,cell(*c)) for c in PRIM]; rj=holm([x["p"] for x in P])
    wins=[c for c,x,r in zip(PRIM,P,rj) if r and x["est"]<0 and x["cov"]>=.9]
    print(t,"PRIMARY wins",len(wins),wins,"holm rej",sum(rj))
    for c,x,r in zip(PRIM,P,rj): print("  ",c,{k:round(float(v),4) for k,v in x.items()},"HOLM" if r else "")
    N=[stat(m,cell(*c)) for c in NOH]; rjn=holm([x["p"] for x in N])
    print(t,"NOHARM holm rej",sum(rjn))
    for c,x,r in zip(NOH,N,rjn): print("  ",c,{k:round(float(v),4) for k,v in x.items()},"HOLM" if r else "")
    allp+= [(t,c,x) for c,x in zip(PRIM,P)]
    out[t]={"primary":{str(c):x for c,x in zip(PRIM,P)},"primary_holm":rj,"wins":[str(w) for w in wins],
            "noharm":{str(c):x for c,x in zip(NOH,N)},"noharm_holm":rjn}
rj16=holm([x["p"] for _,_,x in allp])
w16=[(t,c) for (t,c,x),r in zip(allp,rj16) if r and x["est"]<0 and x["cov"]>=.9]
print("overlay16 wins",len(w16),w16)
out["overlay16"]=[str(w) for w in w16]
json.dump(out,open(OUT/"recompute.json","w"),indent=1,default=float)
