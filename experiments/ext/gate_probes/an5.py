import pickle, numpy as np
R = pickle.load(open('probe3.pkl','rb')); R1 = pickle.load(open('probe.pkl','rb'))
v3 = {(r['topo'], r['T'], r['cell']): r['v3'] for r in R1}
for r in R:
    if r['cell'] != ('ges', 0.0): r['v3'] = v3[(r['topo'], r['T'], r['cell'])]
cells = [('none',0.0),('extra',0.2),('extra',0.5),('missing',0.2),('missing',0.5),('reversed',0.2),('reversed',0.5),('ges',0.0)]
CG = np.round(np.arange(1.0, 10.01, 0.1), 2)
def factor(recs):
    d = np.concatenate([x['dist'] for x in recs]); h = np.concatenate([x['half'] for x in recs])
    cov = np.array([(d <= c*h).mean() for c in CG]); tgt = min(0.95, cov.max()-0.005)
    return float(CG[np.argmax(cov >= tgt)])
CAL = [r for r in R if r['cell'][0] != 'ges']
# v4
fac4 = {(T,k): factor([r['v3'] for r in CAL if r['T']==T and r['cell'][0]==k and r['v3']]) for T in [40,80,150] for k in ['none','extra','missing','reversed']}
def f4(r): return r['v3'], fac4[(r['T'], 'missing' if r['cell'][0]=='ges' else r['cell'][0])]
def mk(a, fp):
    st = lambda r: 'open' if (r['diag']['p_gate'] is not None and r['diag']['p_gate'] <= a) else 'closed'
    fac = {}
    for T in [40,80,150]:
        for s in ['closed','open']:
            recs = [r[f'{s}_{fp}'] for r in CAL if r['T']==T and st(r)==s and r[f'{s}_{fp}']]
            fac[(T,s)] = factor(recs) if recs else 1.0
    return (lambda r: (r[f'{st(r)}_{fp}'], fac[(r['T'], st(r))])), fac
V = {'v4': (f4, fac4)}
for a in [0.05, 0.1]:
    for fp in [0.0, 0.1, 0.2]:
        V[f'a{a}_f{fp}'] = mk(a, fp)
sel = list(V)
res = {}
for n, (f, fac) in V.items():
    for T in [40,80,150]:
        for c in cells:
            g = [f(r) for r in R if r['T']==T and r['cell']==c]; g = [(x,cc) for x,cc in g if x]
            num = sum(((x['dist'] <= cc*x['half']) & ~x['lost']).sum() for x,cc in g); den = sum(len(x['dist']) for x,cc in g)
            IS = np.mean([np.mean(2*cc*x['half'] + 40*np.maximum(x['dist']-cc*x['half'],0)) for x,cc in g])
            res[(n,T,c)] = (num/den, IS, np.mean([x['abserr'] for x,cc in g]))
for n,(f,fac) in V.items(): print(n, fac)
print('T cell'.ljust(16) + ''.join(n.rjust(15) for n in sel))
for T in [40,80,150]:
    for c in cells:
        print(f'{T} {c[0]}-{c[1]}'.ljust(16) + ''.join(f'{res[(n,T,c)][0]:.3f}/{res[(n,T,c)][1]:5.2f}'.rjust(15) for n in sel))
print('ratios none IS vs v4; GES IS ratio')
for n in sel[1:]:
    print(n, [round(res[(n,T,('none',0.0))][1]/res[('v4',T,('none',0.0))][1],3) for T in [40,80,150]], [round(res[(n,T,('ges',0.0))][1]/res[('v4',T,('ges',0.0))][1],3) for T in [40,80,150]])
# gate open rate on GES
for T in [40,80,150]:
    g=[r for r in R if r['T']==T and r['cell']==('ges',0.0)]
    print('GES', T, 'open@0.1', np.mean([r['diag']['p_gate'] is not None and r['diag']['p_gate']<=0.1 for r in g]), 'undiag', sum(r['diag']['p_gate'] is None for r in g), 'true miss', np.mean([r['true']['missing'] for r in g]), 'storey', np.mean([r['diag']['k_storey'] for r in g]), 'bh', np.mean([r['diag']['n_bh'] for r in g]))
