import pickle, numpy as np
R = pickle.load(open('probe.pkl','rb')); P2 = pickle.load(open('probe2.pkl','rb'))
for r in R: r.update(P2[(r['topo'], r['T'], r['cell'])])
pickle.dump(R, open('probe_merged.pkl','wb'))
cells = [('none',0.0),('extra',0.2),('extra',0.5),('missing',0.2),('missing',0.5),('reversed',0.2),('reversed',0.5)]
keys = ['p_sidak','r_sidak','r_boot','a_boot']
for a in [0.05, 0.2]:
  print('alpha', a, keys)
  for T in [40,80,150]:
    for c in cells:
        g=[r for r in R if r['T']==T and r['cell']==c]
        print(T, c, [round(np.mean([(r[k] is not None and r[k]<=a) for r in g]),2) for k in keys], 'undiag', [sum(r[k] is None for r in g) for k in keys])
