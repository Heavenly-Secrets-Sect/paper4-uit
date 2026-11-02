"""Independent recomputation (skeptic) of the narrow direction's cited numbers from runs.jsonl."""
import json, sys
from collections import defaultdict
import numpy as np
R = '/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/'
def load(name):
    return [json.loads(l) for l in open(R + name + '/runs.jsonl')]
def tab(rows):
    d = defaultdict(dict)
    for r in rows:
        d[(r['method'], r['T'], r['kind'], r['rate'])][(r['topology'], r['replicate'], r.get('scenario'))] = r
    return d
def stats(d, m, T, k, rt):
    g = d.get((m, T, k, rt), {})
    ok = [r for r in g.values() if r['status'] == 'ok' and r.get('iscore_nonnull_mean') is not None]
    if not ok: return None
    cov = sum(r['n_covered_nonnull'] for r in ok) / sum(r['n_nonnull'] for r in ok)
    return cov, float(np.mean([r['iscore_nonnull_mean'] for r in ok])), len(ok), len(g)
def pdiff(d, a, b, T, k, rt, B=2000, seed=1):
    A, Bm = d.get((a, T, k, rt), {}), d.get((b, T, k, rt), {})
    by = defaultdict(list)
    for key, r in A.items():
        o = Bm.get(key)
        if o and r['status'] == 'ok' and o['status'] == 'ok' and r.get('iscore_nonnull_mean') is not None and o.get('iscore_nonnull_mean') is not None:
            by[key[0]].append(r['iscore_nonnull_mean'] - o['iscore_nonnull_mean'])
    t = list(by); rng = np.random.default_rng(seed)
    est = np.mean([v for x in t for v in by[x]])
    bs = [np.mean([v for i in rng.choice(len(t), len(t)) for v in by[t[i]]]) for _ in range(B)]
    return est, *np.quantile(bs, [.025, .975])
which = sys.argv[1]
if which == 'eval':
    ev = load('ext_narrow_eval'); old = load('a2b_pselect')
    # pairing
    a = {(r['topology'], r['replicate'], r['T'], r['kind'], r['rate']): r for r in ev if r['method'] == 'tolerant_v4'}
    b = {(r['topology'], r['replicate'], r['T'], r['kind'], r['rate']): r for r in old if r['method'] == 'tolerant_v4'}
    same = sum(1 for k in a if k in b and a[k]['status'] == b[k]['status'] and a[k].get('iscore_nonnull_mean') == b[k].get('iscore_nonnull_mean') and a[k].get('width_kept') == b[k].get('width_kept'))
    print('pairing v4 identical (IS & width exact):', same, len(a), len(b))
    d = tab(ev + [r for r in old if r['method'] in ('plugin', 'pselect_union')])
    cnt5 = cnt4 = 0
    for T in (40, 80, 150):
        for k in ('none', 'extra', 'missing', 'reversed'):
            for rt in ((0.0,) if k == 'none' else (0.2, 0.5)):
                s4, s5, sp = stats(d, 'tolerant_v4', T, k, rt), stats(d, 'tolerant_v5', T, k, rt), stats(d, 'pselect_union', T, k, rt)
                p54 = pdiff(d, 'tolerant_v5', 'tolerant_v4', T, k, rt)
                p5p = pdiff(d, 'tolerant_v5', 'pselect_union', T, k, rt)
                p4p = pdiff(d, 'tolerant_v4', 'pselect_union', T, k, rt)
                if k != 'none':
                    cnt5 += s5[0] >= .9 and p5p[2] < 0; cnt4 += s4[0] >= .9 and p4p[2] < 0
                print(f"{T} {k}-{rt}: v4 {s4[0]:.3f}/{s4[1]:.3f} n{s4[2]}/{s4[3]} | v5 {s5[0]:.3f}/{s5[1]:.3f} n{s5[2]}/{s5[3]} | ps {sp[0]:.3f}/{sp[1]:.2f} | ratio {s5[1]/s4[1]:.3f} | v5-v4 {p54[0]:+.2f} [{p54[1]:+.2f},{p54[2]:+.2f}] | v5-ps {p5p[0]:+.2f} [{p5p[1]:+.2f},{p5p[2]:+.2f}] | v4-ps upper {p4p[2]:+.2f}")
    print('A2b count v5', cnt5, 'v4', cnt4)
else:
    rows = load(which)
    d = tab(rows)
    cells = sorted({(r['T'], r['kind'], r['rate']) for r in rows})
    c54 = c5p = big = 0
    for T, k, rt in cells:
        s4, s5, sp = (stats(d, m, T, k, rt) for m in ('tolerant_v4', 'tolerant_v5', 'pselect_union'))
        if None in (s4, s5, sp): continue
        p54 = pdiff(d, 'tolerant_v5', 'tolerant_v4', T, k, rt); p5p = pdiff(d, 'tolerant_v5', 'pselect_union', T, k, rt)
        if k != 'none':
            c54 += s5[0] >= .9 and p54[2] < 0; c5p += s5[0] >= .9 and p5p[2] < 0; big += s5[1] > 1.05 * s4[1]
        print(f"{T} {k}-{rt}: ps {sp[0]:.3f}/{sp[1]:.2f} | v4 {s4[0]:.3f}/{s4[1]:.2f} n{s4[2]}/{s4[3]} | v5 {s5[0]:.3f}/{s5[1]:.2f} n{s5[2]}/{s5[3]} | v5-v4 {p54[0]:+.2f} [{p54[1]:+.2f},{p54[2]:+.2f}] | v5-ps {p5p[0]:+.2f} [{p5p[1]:+.2f},{p5p[2]:+.2f}]")
    print('beats v4', c54, 'beats ps', c5p, 'IS>1.05xv4', big)
