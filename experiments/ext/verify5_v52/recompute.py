import json, importlib.util, sys
import numpy as np
from collections import defaultdict
ROOT='/Users/kietnt/Desktop/Workspace/Paper4_UIT/'
def L(n,p):
    s=importlib.util.spec_from_file_location(n,ROOT+p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
Bm=L('b','experiments/ext/r5hubscreen2/analyze.py')
rows=lambda s:[json.loads(l) for l in open(ROOT+f'results/ext_r5v52_{s}/runs.jsonl')]
out={}
p2=rows('p2')
# P2c independent
idx=defaultdict(dict)
for r in p2: idx[(r['T'],r['kind'])].setdefault(r['method'],{})[(r['topology'],r['replicate'])]=r
pc=[]
for i,(T,k) in enumerate([(19,'missing'),(19,'reversed'),(19,'extra'),(25,'missing'),(25,'reversed'),(25,'extra')]):
    a=idx[(T,k)]['tolerant_v5_2']; b=idx[(T,k)]['plugin_hs_cal']
    keys=[u for u,r in a.items() if r['v51_status']!='ok' and r['status']=='ok' and b[u]['status']=='ok']
    ma=np.mean([a[u]['iscore_nonnull_mean'] for u in keys]); mb=np.mean([b[u]['iscore_nonnull_mean'] for u in keys])
    cl=len({u[0] for u in keys})
    pc.append({'cell':f'{T}|{k}','n':len(keys),'clusters':cl,'ratio':ma/mb,'ma':ma,'mb':mb})
out['P2c_indep']=pc
# P2a/b
p2ab=[]
for (T,k),d in sorted(idx.items()):
    a=d['tolerant_v5_2']; n=len(a); okn=sum(r['status']=='ok' for r in a.values())
    itt=sum(r.get('n_covered_nonnull',0) or 0 for r in a.values())/sum(r['n_nonnull_truth'] for r in a.values())
    p2ab.append((T,k,okn,n,round(itt,4)))
out['P2ab']=p2ab
# lag0 dropped and counts across all runsets
tot=defaultdict(int)
for s in ('ngmix','gauss','p2','latent1','noise01'):
    for r in rows(s):
        if r['method']!='tolerant_v5_2': continue
        tot['rows']+=1; tot['contemp']+=r.get('hs_contemp_dropped') or 0
        tot[s+'_red']+=r.get('hs_reduced') or 0; tot[s+'_gate']+= not r['no_gate']
        if r['v51_status']=='ok':
            tot['v51ok']+=1; tot['changed']+= not r['raw_ident_v51']
        tot['factor_neq_noRed']+= (r.get('hs_reduced')==0 and r['status']=='ok' and r['fac'] is not None and False)
out['totals']=dict(tot)
# max IS ratio no-harm a, b
def cellratio(s,cells):
    res=[]
    rr=rows(s); d=defaultdict(dict)
    for r in rr: d[(r['T'],r['kind'],float(r['rate']))].setdefault(r['method'],{})[(r['topology'],r['replicate'])]=r
    for key in cells:
        a=d[key]['tolerant_v5_2']; b=d[key]['tolerant_v5_1']
        ks=[u for u in a if a[u]['status']=='ok' and b[u]['status']=='ok']
        res.append((key, np.mean([a[u]['iscore_nonnull_mean'] for u in ks])/np.mean([b[u]['iscore_nonnull_mean'] for u in ks])))
    return res
CELLS=[('none',0.0),('extra',0.2),('extra',0.5),('missing',0.2),('missing',0.5),('reversed',0.2),('reversed',0.5)]
G=[(T,k,r) for T in (40,80,150) for k,r in CELLS]
ga=cellratio('gauss',G); out['noharm_a_ratio_range']=[min(x[1] for x in ga),max(x[1] for x in ga)]
prim=[(T,k,r) for T in (80,150) for k in ('missing','reversed') for r in (0.2,0.5)]
nb=cellratio('ngmix',[c for c in G if c not in prim]); out['noharm_b_ratio_max']=max(x[1] for x in nb)
p1=cellratio('ngmix',prim); out['P1_rel_mean']=float(np.mean([x[1]-1 for x in p1]))
json.dump(out,open(ROOT+'results/ext_verify5_v52/recompute.json','w'),indent=1,default=float)
print(json.dumps(out,indent=1,default=float))
