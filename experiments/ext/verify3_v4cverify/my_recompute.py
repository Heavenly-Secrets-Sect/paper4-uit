"""Skeptic recompute (verify3_v4cverify). Written from docs/ext/v4c.md sec 4 text only."""
import json, numpy as np, collections, sys
def load(d, rename=None):
    out={}
    for l in open(f'results/{d}/runs.jsonl'):
        r=json.loads(l); m=r['method']
        out[(m,r['topology'],r['replicate'],r['T'],r['kind'],float(r['rate']))]=r
    return out
E=load('ext_v4c_eval'); A2=load('a2_baselines'); PS=load('a2b_pselect'); CB=load('ext_redteam_calbase')
topos=sorted({k[1] for k in E}); reps=sorted({k[2] for k in E})
CELLS=[]
for T in [40,80,150]:
    CELLS.append((T,'none',0.0))
    for k in ['extra','missing','reversed']:
        for r in [0.2,0.5]: CELLS.append((T,k,r))
def get(src,m,t,rep,T,k,r): return src[(m,t,rep,T,k,r)]
def arrays(srcM,m,srcX,x,T,k,r):
    # per topology: list of (isM,isX), coverage pooled for M
    a=np.full((len(topos),len(reps),2),np.nan); cn=0; nn=0; cnX=0
    for i,t in enumerate(topos):
        for j,rep in enumerate(reps):
            rm=get(srcM,m,t,rep,T,k,r); rx=get(srcX,x,t,rep,T,k,r)
            cn+=rm['n_covered_nonnull']; nn+=rm['n_nonnull']; cnX+=rx['n_covered_nonnull']
            if rm['status']=='ok' and rx['status']=='ok':
                a[i,j]=[rm['iscore_nonnull_mean'],rx['iscore_nonnull_mean']]
    return a, cn/nn, cnX/nn
def boot(a, seed=20261102, B=2000, idx=None):
    rng=np.random.default_rng(seed)
    n=a.shape[0]
    if idx is None: idx=rng.integers(0,n,size=(B,n))
    sm=np.nansum(a[...,0],axis=1); sx=np.nansum(a[...,1],axis=1); cnt=np.sum(~np.isnan(a[...,0]),axis=1)
    SM=sm[idx].sum(1); SX=sx[idx].sum(1); C=cnt[idx].sum(1)
    mM=SM/C; mX=SX/C
    return mM-mX, mM/mX
def point(a):
    m=~np.isnan(a[...,0]); return a[...,0][m].mean(), a[...,1][m].mean()
def holm(ps, alpha):
    order=np.argsort(ps); rej=np.zeros(len(ps),bool)
    for rank,i in enumerate(order):
        if ps[i] <= alpha/(len(ps)-rank): rej[i]=True
        else: break
    return rej
res={}
seeds=[20261102]+list(range(1,31))
# Rule A C1
c1=[];
for T in [80,150]:
    for (TT,k,r) in CELLS:
        if TT!=T: continue
        a,cM,cX=arrays(E,'tolerant_v4c',E,'tolerant_v4',T,k,r)
        mM,mX=point(a); c1.append(dict(cell=f'T{T} {k}-{r}',ratio=mM/mX,a=a))
print('C1 ratios', [round(c['ratio'],4) for c in c1], 'pass', sum(0.97<=c['ratio']<=1.03 for c in c1))
tost_counts=[]
for s in seeds:
    ps=[]
    for c in c1:
        d,ra=boot(c['a'],seed=s); B=len(ra)
        p=max((1+np.sum(ra<=0.97))/(B+1),(1+np.sum(ra>=1.03))/(B+1)); ps.append(p)
    tost_counts.append(int(holm(np.array(ps),0.05).sum()))
print('TOST Holm count per seed', collections.Counter(tost_counts), 'seed20261102:',tost_counts[0])
# C2
c2=[]
for r in [0.2,0.5]:
    a,cM,cX=arrays(E,'tolerant_v4c',E,'tolerant_v4',40,'missing',r)
    mM,mX=point(a)
    ups=[]; pss=[]
    for s in seeds:
        d,_=boot(a,seed=s); ups.append(np.percentile(d,97.5)); pss.append((1+np.sum(d>=0))/(len(d)+1))
    d,_=boot(a)
    c2.append(dict(r=r,covv4c=cM,covv4=cX,IS=(mM,mX),diff=mM-mX,ci=(np.percentile(d,2.5),np.percentile(d,97.5)),max_upper=max(ups),max_p=max(pss)))
print('C2',c2)
# Part B pair (b): v4 vs ida_cal (E3)
BX={'pselect_union':('pselect_cal','pselect_union_c2'),'ida_union':('ida_cal','ida_union_c2'),'bvar_minnesota':('bvar_cal','bvar_minnesota_c2')}
def pairstats(srcM,m,srcX,x,seed):
    out=[]
    for (T,k,r) in CELLS:
        a,cM,cX=arrays(srcM,m,srcX,x,T,k,r); mM,mX=point(a)
        d,_=boot(a,seed=seed); lo,up=np.percentile(d,[2.5,97.5]); p=(1+np.sum(d>=0))/(len(d)+1)
        cls='W' if (cM>=0.9 and up<0) else ('L' if lo>0 else 'T')
        out.append(dict(cell=(T,k,r),cls=cls,p=p,cov=cM,up=up,diff=mM-mX))
    ps=np.array([o['p'] for o in out]); rej=holm(ps,0.025)
    hw=sum(1 for o,rj in zip(out,rej) if rj and o['cov']>=0.9)
    hw_nm=sum(1 for o,rj in zip(out,rej) if rj and o['cov']>=0.9 and o['cell'][1]!='missing')
    return out,hw,hw_nm
pairs={'a':{'pselect_union':(PS,'pselect_union'),'ida_union':(A2,'ida_union'),'bvar_minnesota':(A2,'bvar_minnesota')},
       'b':{x:(CB,BX[x][0]) for x in BX},'c':{x:(E,BX[x][1]) for x in BX},'d':{x:(E,BX[x][1]) for x in BX}}
summary={}
for p,dd in pairs.items():
    m='tolerant_v4c' if p=='d' else 'tolerant_v4'
    for x,(src,xn) in dd.items():
        out,hw,hwnm=pairstats(E,m,src,xn,20261102)
        c=collections.Counter(o['cls'] for o in out); cnm=collections.Counter(o['cls'] for o in out if o['cell'][1]!='missing')
        summary[f'{p}|{x}']=dict(W=c['W'],T=c['T'],L=c['L'],Wnm=cnm['W'],Tnm=cnm['T'],Lnm=cnm['L'],holmW=hw,holmW_nm=hwnm)
        print(p,x,summary[f'{p}|{x}'])
# seed sensitivity of (b) ida holm
hs=[]
for s in seeds:
    _,hw,hwnm=pairstats(E,'tolerant_v4',CB,'ida_cal',s); hs.append((hw,hwnm))
print('(b) ida holm across seeds', collections.Counter(hs))
# D6: X_c2 vs X_cal, ex-missing, 15 cells x3 =45
better=0; worse=0; ps=[]; info=[]
for x in BX:
    for (T,k,r) in CELLS:
        if k=='missing': continue
        a,_,_=arrays(E,BX[x][1],CB,BX[x][0],T,k,r)
        d,_=boot(a); lo,up=np.percentile(d,[2.5,97.5]); p=(1+np.sum(d>=0))/(len(d)+1)
        better+=up<0; worse+=lo>0; ps.append(p); info.append((x,T,k,r,round(up,4)))
rej=holm(np.array(ps),0.025)
print('D6 better',better,'worse',worse,'holm better',int(rej.sum()))
print('ida T80 extra-0.2 upper', [i for i in info if i[0]=='ida_union' and i[1]==80 and i[2]=='extra'])
json.dump(dict(c1=[dict(cell=c['cell'],ratio=c['ratio']) for c in c1],tost_counts=tost_counts,c2=c2,partB=summary,b_ida_holm_seeds=[list(h) for h in hs],D6=dict(better=better,worse=worse,holm=int(rej.sum()))),open('results/ext_verify3_v4cverify/my_recompute.json','w'),indent=1,default=float)
