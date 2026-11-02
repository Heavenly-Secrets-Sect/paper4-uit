import json,numpy as np
from collections import defaultdict
from scipy.stats import spearmanr
def load(p):
    d=defaultdict(list);m={}
    for l in open(p):
        r=json.loads(l);lc='c' if r['edge_lag']==0 else 'l'
        d[(r['kind'],lc,r['role'])].append((r['split'],r['topology'],r['rel_shift']));m[r['topology']]=r['profile']
    return d,m
N,mn=load('results/ext_p4h1_rq43/pairs.jsonl');O,_=load('results/rq43_edge_cost/pairs.jsonl')
rows=[('missing','c'),('missing','l'),('reversed','c')];roles=['on_path','into_source','into_target','other']
def med(d,c,f=lambda x:True):
    v=[x[2] for x in d[c] if f(x)];return np.median(v) if v else np.nan
cells=[(k,l,r) for k,l in rows for r in roles]
pn={c:med(N,c) for c in cells};po={c:med(O,c) for c in cells}
for c in cells:print(c,round(pn[c],3),round(po[c],3),len(N[c]),len({x[1] for x in N[c]}))
for k,l in rows:
    on=pn[(k,l,'on_path')];print(k,l,[round(on/pn[(k,l,r)],2) if pn[(k,l,r)]>0 else 'inf' for r in roles[1:]])
dv={c:med(N,c,lambda x:x[0]=='development') for c in cells};cv={c:med(N,c,lambda x:x[0]=='confirmatory') for c in cells}
er={c:med(N,c,lambda x:mn[x[1]]=='erdos_renyi') for c in cells};hb={c:med(N,c,lambda x:mn[x[1]]!='erdos_renyi') for c in cells}
s=lambda a,b:spearmanr([a[c] for c in cells],[b[c] for c in cells]).statistic
print(s(dv,cv),s(er,hb),s(pn,po))
print(len(O[('missing','c','on_path')]), {x[1] for x in O[('missing','c','on_path')]}.__len__())
