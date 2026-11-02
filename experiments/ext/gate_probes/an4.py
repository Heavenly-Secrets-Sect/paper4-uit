import pickle, numpy as np
R = pickle.load(open('probe_merged.pkl','rb'))
fac = {(40, 'closed'): 1.9, (40, 'open'): 1.1, (80, 'closed'): 1.5, (80, 'open'): 1.3, (150, 'closed'): 1.6, (150, 'open'): 1.4}
for T in [80,150]:
  for c in [('reversed',0.2),('reversed',0.5),('none',0.0)]:
    for s in ['closed','open']:
        g=[r for r in R if r['T']==T and r['cell']==c and (('open' if r['r_sidak']<=0.05 else 'closed')==s)]
        x=[r['open_all' if s=='open' else 'closed'] for r in g]
        if not x: continue
        cc=fac[(T,s)]
        cov=sum(((y['dist']<=cc*y['half'])&~y['lost']).sum() for y in x)/sum(len(y['dist']) for y in x)
        print(T,c,s,len(g),round(cov,3), 'rev', np.mean([r['true']['reversed'] for r in g]))
