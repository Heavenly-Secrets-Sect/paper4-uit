import pickle, sys, numpy as np
from collections import defaultdict
R = pickle.load(open(sys.argv[1] if len(sys.argv)>1 else 'probe.pkl','rb'))
cells = [('none',0.0),('extra',0.2),('extra',0.5),('missing',0.2),('missing',0.5),('reversed',0.2),('reversed',0.5)]
CG = np.round(np.arange(1.0, 10.01, 0.1), 2)
def factor(recs):
    d = np.concatenate([x['dist'] for x in recs]); h = np.concatenate([x['half'] for x in recs])
    cov = np.array([(d <= c*h).mean() for c in CG]); tgt = min(0.95, cov.max()-0.005)
    return float(CG[np.argmax(cov >= tgt)])
def score(recs, c):
    d = np.concatenate([x['dist'] for x in recs]); h = np.concatenate([x['half'] for x in recs])
    lost = np.concatenate([x['lost'] for x in recs])
    cov = ((d <= c*h) & ~lost).mean()
    IS = np.mean([np.mean(2*c*x['half'] + 40*np.maximum(x['dist']-c*x['half'],0)) for x in recs])
    return cov, IS
def wkey(cell): return cell[0]
def v4(R):
    fac = {}
    for T in [40,80,150]:
        for k in ['none','extra','missing','reversed']:
            fac[(T,k)] = factor([r['v3'] for r in R if r['T']==T and r['cell'][0]==k and r['v3']])
    return lambda r: (r['v3'], fac[(r['T'], r['cell'][0])])
def composite(R, gk, a, openkey):
    def st(r): return 'open' if (r[gk] is not None and r[gk] <= a) else 'closed'
    fac = {}
    for T in [40,80,150]:
        for s in ['closed','open']:
            recs = [r['closed' if s=='closed' else openkey] for r in R if r['T']==T and st(r)==s]
            recs = [x for x in recs if x]
            fac[(T,s)] = factor(recs) if recs else None
    return lambda r: (r['closed' if st(r)=='closed' else openkey], fac[(r['T'], st(r))]), fac
variants = {'v4': (v4(R), None)}
for gk in ['p_sidak','r_sidak','r_boot']:
    for a in [0.05, 0.10, 0.2]:
        for ok in ['open_max','open_bh','open_all']:
            f, fac = composite(R, gk, a, ok)
            variants[f'{gk}@{a}/{ok}'] = (f, fac)
sel = sys.argv[2].split(',') if len(sys.argv)>2 else list(variants)
res = {}
for name in sel:
    f, fac = variants[name]
    line = []
    for T in [40,80,150]:
        for c in cells:
            g = [f(r) for r in R if r['T']==T and r['cell']==c]
            g = [(x, cc) for x, cc in g if x]
            cov = np.mean([((x['dist'] <= cc*x['half']) & ~x['lost']).mean() for x,cc in g])
            # pooled
            num = sum(((x['dist'] <= cc*x['half']) & ~x['lost']).sum() for x,cc in g); den = sum(len(x['dist']) for x,cc in g)
            IS = np.mean([np.mean(2*cc*x['half'] + 40*np.maximum(x['dist']-cc*x['half'],0)) for x,cc in g])
            res[(name,T,c)] = (num/den, IS)
print('factors:', {k: v[1] for k, v in variants.items() if k in sel and v[1]})
hdr = 'T cell'.ljust(22) + ''.join(n[-22:].rjust(24) for n in sel)
print(hdr)
for T in [40,80,150]:
    for c in cells:
        print(f'{T} {c[0]}-{c[1]}'.ljust(22) + ''.join(f'{res[(n,T,c)][0]:.3f}/{res[(n,T,c)][1]:6.2f}'.rjust(24) for n in sel))
