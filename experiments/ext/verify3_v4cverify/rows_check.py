import json,sys
def load(p):
    return [json.loads(l) for l in open(p)]
orig=load('results/ext_v4c_eval/runs.jsonl')
print('orig rows',len(orig), 'keys', sorted(orig[0].keys()))
def key(r): return (r['method'],r['topology'],r.get('replicate'),r['T'],r.get('kind'),r.get('rate'))
O={}
for r in orig: O.setdefault(key(r),[]).append(r)
print('dup keys', sum(len(v)>1 for v in O.values()))
out={}
for d in ['results/ext_v4cverify_rerun_w3','results/ext_v4cverify_rerun_w3_clt']:
    rows=load(d+'/runs.jsonl')
    ident=0; diff=[]
    for r in rows:
        o=O.get(key(r))
        if o and json.dumps(o[0],sort_keys=True)==json.dumps(r,sort_keys=True): ident+=1
        else: diff.append(key(r))
    units=sorted({(r['topology'],r.get('replicate')) for r in rows})
    cal=open(d+'/calibration.json','rb').read()==open('results/ext_v4c_eval/calibration.json','rb').read()
    sk_o={json.loads(l)['topology'] if 'topology' in json.loads(l) else i: l for i,l in enumerate(open('results/ext_v4c_eval/skeletons.jsonl'))}
    out[d]=dict(n=len(rows),identical=ident,diff=diff[:5],units=units,cal_bytes_equal=cal)
    print(d,out[d])
json.dump(out,open('results/ext_verify3_v4cverify/rows_check.json','w'),indent=1,default=str)
