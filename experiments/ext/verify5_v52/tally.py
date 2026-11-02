import json
from collections import Counter
R='/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/'
rows=json.load(open(R+'ext_verify5_v52/identity_sample.json'))
st={}
for s in ('p2','ngmix','gauss'):
    for l in open(R+f'ext_r5v52_{s}/runs.jsonl'):
        r=json.loads(l)
        st[(s,r['topology'],r['replicate'],r['T'],r['kind'],float(r['rate']),r['method'])]=r
c={'noRed->ngA3':[0,0],'noGate->hs2':[0,0],'both->v51':[0,0],'stored52':[0,0],'stored51':[0,0],'restored':[0,0],'contemp':0,'redflag_eq_hs2':[0,0]}
bad=[]
for r in rows:
    nr = r['red']==0 and r['evred']==0
    if nr:
        c['noRed->ngA3'][0]+=1; c['noRed->ngA3'][1]+=r['eq_ngA3']
        if not r['eq_ngA3']: bad.append(('ngA3',r))
    if r['no_gate']:
        c['noGate->hs2'][0]+=1; c['noGate->hs2'][1]+=r['eq_hs2']
        c['redflag_eq_hs2'][0]+=1; c['redflag_eq_hs2'][1]+= r['red']==r['hs2_red']
        if not r['eq_hs2']: bad.append(('hs2',r))
    if nr and r['no_gate']:
        c['both->v51'][0]+=1; c['both->v51'][1]+=r['eq_v51']
    c['restored'][0]+=1; c['restored'][1]+=r['restored']
    c['contemp']+=r['contemp_dropped']
    if r['cfg']!='latent1':
        k=(r['cfg'],r['topology'],r['replicate'],r['T'],r['kind'],float(r['rate']))
        s52=st.get(k+('tolerant_v5_2',)); s51=st.get(k+('tolerant_v5_1',))
        c['stored52'][0]+=1; c['stored52'][1]+= (s52 is not None and s52.get('iscore_nonnull_mean')==r['IS52'] and s52['status']==r['v52'] and s52['hs_reduced']==r['red'] and s52['no_gate']==r['no_gate'])
        c['stored51'][0]+=1; c['stored51'][1]+= (s51 is not None and s51.get('iscore_nonnull_mean')==r['IS51'])
print(c)
print(Counter((r['cfg'],r['red'],r['no_gate'],r['v52'],r['v51']) for r in rows))
for b in bad: print(b)
json.dump(c,open(R+'ext_verify5_v52/identity_tally.json','w'),indent=1)
