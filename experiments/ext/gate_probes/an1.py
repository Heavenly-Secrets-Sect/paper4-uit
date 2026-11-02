import pickle, numpy as np
from collections import defaultdict
R = pickle.load(open('probe.pkl','rb'))
cells = [('none',0.0),('extra',0.2),('extra',0.5),('missing',0.2),('missing',0.5),('reversed',0.2),('reversed',0.5)]
print('rejection rate at 0.05 (minp / fisher / sidak) and 0.10 minp')
for T in [40,80,150]:
    for c in cells:
        g=[r for r in R if r['T']==T and r['cell']==c and r['p_minp'] is not None]
        f=lambda k,a: np.mean([r[k]<=a for r in g])
        print(T, c, len(g), f('p_minp',.05), f('p_fisher',.05), f('p_sidak',.05), f('p_minp',.10), 'true miss', np.mean([r['true']['missing'] for r in g]))
