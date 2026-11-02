import numpy as np, json
z=np.load('results/ext_p4h1_rq41_main/pairs.npz'); d={k:z[k] for k in z.files}
M=list(d['methods']); C=list(d['cells'])
print('min|C_t|',np.abs(d['C_t']).min(), 'counts per method',[int((d['method']==i).sum()) for i in range(4)])
cov=((d['lo']<=d['C_t'])&(d['C_t']<=d['hi'])).astype(float)
rel=np.abs(d['C_e']-d['C_t'])/np.abs(d['C_t'])
ml=np.where(np.isfinite(d['ml_e'])&np.isfinite(d['ml_t']),np.abs(d['ml_e']-d['ml_t']),np.nan)
def sel(T,c,m,role=None):
    s=(d['T']==T)&(d['cell']==C.index(c))&(d['method']==M.index(m))
    if role is not None: s&=d['role']==role
    return s
out={}
print('a')
for T in(40,80,150):
  for r in('0.2','0.5'):
    v=[np.median(rel[sel(T,f'{k}|{r}','plugin',2)]) for k in('missing','reversed','extra')]
    print(T,r,np.round(v,3),v[0]>v[1]>v[2], [len(set(d['topo'][sel(T,f'{k}|{r}','plugin',2)])) for k in('missing','reversed','extra')])
print('b',[round(cov[sel(T,'missing|0.5','plugin')].mean(),3) for T in(40,80,150)])
print('c')
for m in('tolerant_v4','tolerant_v5_1'):
  for T in(40,80,150):
    for r in('0.2','0.5'):
      s=sel(T,f'missing|{r}',m,2);p=sel(T,f'missing|{r}','plugin',2)
      print(m,T,r,round(np.median(rel[s]),3),round(np.median(rel[p]),3),round(cov[s].mean(),3),s.sum())
print('d')
for k in('missing','reversed','extra'):
  for r in('0.2','0.5'):
    a=[ml[sel(T,f'{k}|{r}','plugin',2)] for T in(40,150)]
    a=[np.median(x[np.isfinite(x)]) for x in a]; print(k,r,round(a[1]/a[0],3))
