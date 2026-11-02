import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
d = json.load(open(ROOT / 'results/ext_revlag3_flagextra/flag_extra.json'))
def holm(ps):
    m=len(ps); o=sorted(range(m), key=lambda i: ps[i]); out=[0]*m; run=0
    for r,i in enumerate(o):
        run=max(run, min(1,(m-r)*ps[i])); out[i]=run
    return out
res = {}
for enc in ('round2','train'):
    rows=[r for r in d[enc] if r['label'] in ('clean T80/150','clean T40','GES T40','GES T80','GES T150','latent1 T80/150','latent3 T80/150','noise0.1 T80/150','noise0.3 T80/150')]
    p_pos=[r['p_dinv_le0'] for r in rows]          # H0: p_hat <= 1/width
    p_neg=[1-r['p_dinv_le0']+1/2000 for r in rows]   # approx H0: p_hat >= 1/width
    hp=holm(p_pos); hn=holm(p_neg)
    out=[]
    for r,a,b,c,e in zip(rows,p_pos,hp,p_neg,hn):
        out.append(dict(label=r['label'], d_inv=r['d_inv'], ci=r['d_inv_ci'], p_one_sided_phat_better=a, holm9=b, p_one_sided_inv_better_approx=c, holm9_inv=e))
        print(f"{enc:7s} {r['label']:18s} {r['d_inv']:+.3f} [{r['d_inv_ci'][0]:+.3f},{r['d_inv_ci'][1]:+.3f}] p {a:.4f} holm {b:.4f} | inv-better p {c:.4f} holm {e:.4f}")
    res[enc]=dict(rows=out, n_phat_better_holm=sum(b<0.05 for b in hp), n_inv_better_holm=sum(e<0.05 for e in hn),
                  n_point_phat_better=sum(r['d_inv']>0 for r in rows), n_sets=len(rows))
    print(enc, {k:v for k,v in res[enc].items() if k!='rows'})
json.dump(res, open(ROOT/'results/ext_verify3_revlag3/holm_inv_width.json','w'), indent=1)
