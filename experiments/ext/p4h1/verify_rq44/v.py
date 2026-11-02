import numpy as np, json
from scipy.stats import rankdata
fz=json.load(open('experiments/ext/revlag/frozen_flag.json'))
def load(r,off):
    z=np.load(f'results/{r}/pairs.npz'); 
    d={k:z[k] for k in z.files}
    d['topo']=d['topo']+off; return d
a,b=load('ext_p4h1_rq44_dev',0),load('ext_p4h1_rq44_conf',100)
print('methods',a['methods'],'min|C_t|',min(abs(a['C_t']).min(),abs(b['C_t']).min()))
R={k:np.concatenate([a[k],b[k]]) for k in ['topo','T','cell','C_t','C_e','lo','hi','stated','rep']}
def score(r):
    w=r['hi']-r['lo']; rw=w/(abs(r['C_e'])+1e-9)
    X=np.column_stack([np.log1p(np.maximum(rw,0)),np.log1p(np.maximum(w,0)),((r['lo']<=0)&(0<=r['hi'])).astype(float),np.log(r['T']),(r['stated']==2)*1.,(r['stated']==3)*1.,(r['stated']==1)*1.])
    Z=(X-fz['mu'])/fz['sd']; return 1/(1+np.exp(-(fz['weights'][0]+Z@np.array(fz['weights'][1:]))))
def auc(s,y):
    r=rankdata(s); n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
rng=np.random.default_rng(1)
for name,m in [('hi',R['T']>=80),('lo',R['T']==40)]:
    r={k:v[m] for k,v in R.items()}
    y=(~((r['lo']<=r['C_t'])&(r['C_t']<=r['hi']))).astype(int)
    p=score(r); w=r['hi']-r['lo']; rw=w/(abs(r['C_e'])+1e-9)
    fl=p>0.1
    print(name,len(y),y.mean(),'auc',auc(p,y),'rel',auc(rw,y),'inv',auc(1/np.maximum(w,1e-12),y),'flag',fl.mean(),y[fl].mean(),y[~fl].mean(),y[fl].mean()/y[~fl].mean())
    tp=np.unique(r['topo']); idx={t:np.where(r['topo']==t)[0] for t in tp}
    A=[];D=[];Q=[]
    for _ in range(300):
        s=rng.choice(tp,len(tp)); ii=np.concatenate([idx[t] for t in s])
        yy=y[ii]; A.append(auc(p[ii],yy)); D.append(A[-1]-auc(rw[ii],yy)); f=fl[ii]
        Q.append(yy[f].mean()/yy[~f].mean())
    print(' CI auc',np.percentile(A,[2.5,97.5]),'d',np.percentile(D,[2.5,97.5]),'ratio',np.percentile(Q,[2.5,97.5]),'ntopo',len(tp))
