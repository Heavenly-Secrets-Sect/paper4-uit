import json
from collections import defaultdict
from pathlib import Path
import numpy as np
RES=Path("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results")
REF="tolerant_v5_1"; VAR={"A":"tolerant_v5_1_leadlag","D":"tolerant_v5_1_leadlag_skel"}
def load(n): return [json.loads(l) for l in open(RES/n/"runs.jsonl")]
K=lambda r:(r.get("scenario","clean"),r["topology"],r["replicate"],r["T"],r["kind"],r["rate"])
def bym(rows):
    D=defaultdict(dict)
    for r in rows: D[r["method"]][K(r)]=r
    return D
ev=bym(load("ext_r4leadlag_eval_clean")+load("ext_r4leadlag_eval_latent")+load("ext_r4leadlag_eval_noise"))
dc=bym(load("ext_r4leadlag_decomp_latent")+load("ext_r4leadlag_decomp_clean"))
# decomp non-missing identity and missing-cell exact identity share
for t,m in VAR.items():
    nm=[k for k in dc[m] if k[4]!="missing"]
    same=sum(dc[m][k]["iscore_nonnull_mean"]==ev[REF][k]["iscore_nonnull_mean"] for k in nm)
    ms=[k for k in dc[m] if k[4]=="missing"]
    same_m=sum(abs(dc[m][k]["iscore_nonnull_mean"]-ev[REF][k]["iscore_nonnull_mean"])<1e-12 for k in ms)
    lab0=sum((dc[m][k].get("info_gate_draw_labelled_mean") or 0)==0 and (dc[m][k].get("info_gate_n_labelled") or 0)==0 for k in ms)
    print(t,"decomp non-missing identical",same,"/",len(nm),"| missing rows identical to v51",same_m,"/",len(ms),"| rows with zero labels data+draws",lab0)
def holm(ps,a=.05):
    o=np.argsort(ps); rej=[False]*len(ps)
    for i,j in enumerate(o):
        if ps[j]<=a/(len(ps)-i): rej[j]=True
        else: break
    return rej
def pstat(Dm,Dr,keys,seed=999,B=20000):
    d=defaultdict(list)
    for k in keys: d[k[1]].append(Dm[k]["iscore_nonnull_mean"]-Dr[k]["iscore_nonnull_mean"])
    tp=list(d); s=np.array([sum(d[t]) for t in tp]); c=np.array([len(d[t]) for t in tp])
    rng=np.random.default_rng(seed); pk=rng.integers(0,len(tp),(B,len(tp))); b=s[pk].sum(1)/c[pk].sum(1)
    return s.sum()/c.sum(), np.quantile(b,.025), np.quantile(b,.975), min(1,2*min((1+(b>=0).sum())/(B+1),(1+(b<=0).sum())/(B+1)))
CELLS=[(sc,T,r) for sc in ("latent1","latent3") for r in (.2,.5) for T in (80,150)]+[("clean",150,.2),("clean",150,.5)]
for t,m in VAR.items():
    res=[]
    for sc,T,r in CELLS:
        keys=sorted(k for k in ev[REF] if k[0]==sc and k[3]==T and k[4]=="missing" and k[5]==r)
        g=pstat(dc[m],ev[REF],keys); f=pstat(ev[m],dc[m],keys); res.append((sc,T,r,g,f))
    hg=holm([x[3][3] for x in res]); hf=holm([x[4][3] for x in res])
    print(t,"gate Holm rej",sum(hg),"factor Holm rej",sum(hf))
    for x,a,b in zip(res,hg,hf): print("  ",x[:3],"gate %+.3f [%+.3f,%+.3f] p=%.4f"%x[3],"H" if a else "","| factor %+.3f [%+.3f,%+.3f] p=%.4f"%x[4],"H" if b else "")
# AUROC
def auroc(p,n):
    p,n=np.asarray(p),np.asarray(n); return float((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean())
for t,m in VAR.items():
    for T in (80,150):
        items=[]
        for k,r in ev[m].items():
            if k[0] in("latent1","latent3") and k[3]==T and k[4]=="missing":
                for e,c in zip(r.get("info_gate_p") or [], r.get("cls_gate_p") or []):
                    if c=="C": items.append((k[1],1,-e[3]))
                    elif c in("E0","EL"): items.append((k[1],0,-e[3]))
        pos=[s for _,y,s in items if y]; neg=[s for _,y,s in items if not y]
        by=defaultdict(list)
        for tp,y,s in items: by[tp].append((y,s))
        tps=list(by); rng=np.random.default_rng(5); bs=[]
        for _ in range(2000):
            pk=rng.integers(0,len(tps),len(tps)); P=[s for i in pk for y,s in by[tps[i]] if y]; N=[s for i in pk for y,s in by[tps[i]] if not y]
            if P and N: bs.append(auroc(P,N))
        # also share of ties among pos/neg (pQ==1 or identical)
        print(t,T,"AUROC %.3f [%.3f, %.3f] npos %d nneg %d"%(auroc(pos,neg),*np.quantile(bs,(.025,.975)),len(pos),len(neg)),
              "| median p_Q C %.3f edges %.3f"%(np.median([-s for s in pos]),np.median([-s for s in neg])))
# confusion latent T80/150
for t,m in VAR.items():
    for lab,scs,Ts in [("latent T80/150",("latent1","latent3"),(80,150)),("clean",("clean",),(40,80,150))]:
        tab=defaultdict(lambda:[0,0]); dl=[]
        for k,r in ev[m].items():
            if k[0] in scs and k[3] in Ts and k[4]=="missing":
                for e,c in zip(r.get("info_gate_p") or [], r.get("cls_gate_p") or []):
                    tab[c][1]+=1; tab[c][0]+=int(e[3]<.05)
                dl.append(r.get("info_gate_draw_labelled_mean") or 0)
        print(t,lab,dict(tab),"per draw %.2f"%np.mean(dl))
# cochild coverage at T150
for sc in ("latent1","latent3"):
    for r_ in (.2,.5):
        keys=[k for k in ev[REF] if k[0]==sc and k[3]==150 and k[4]=="missing" and k[5]==r_]
        o=[]
        for m in ("oracle",REF,VAR["A"],VAR["D"]):
            n=sum(ev[m][k]["cc_n"] for k in keys if k in ev[m]); c=sum(ev[m][k]["cc_n_cov"] for k in keys if k in ev[m])
            o.append("%s %.3f"%(m[-6:],c/n if n else float('nan')))
        print("cochild cov",sc,r_,o)
