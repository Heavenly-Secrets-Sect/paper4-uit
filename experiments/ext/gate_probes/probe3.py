import sys, json, pickle
SP='/private/tmp/claude-501/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/scratchpad'
sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/src'); sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments'); sys.path.insert(0, SP)
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from run_experiment import generator_config, unit_skeletons
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
from paper4.metrics import truth_effects
from paper4.learned import damage_counts, ges_skeleton
from paper4.skeleton import true_skeleton
from paper4 import methods as M
import loadcand
G = loadcand.load(SP + '/ext_gate_candidate.py')
cfg = json.load(open('/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/configs/b1v2_auto.json'))
GESD = json.load(open('/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/b1v2_auto/calibration.json'))['ges_damage']
NB = 99
def rec(res, C_true, nonnull):
    if res.status != 'ok': return None
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return {'dist': np.abs(C_true - mid)[nonnull], 'half': half[nonnull], 'lost': (res.C == 0)[nonnull], 'info': res.info,
            'abserr': float(np.median(np.abs(res.C - C_true)[nonnull]))}
def job(t_idx):
    topo = load_bank('D-07H', 'development')[t_idx]
    unit = cfg['seed_base'] + 500000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, generator_config(cfg), np.random.default_rng([unit, 0]))
    sk = unit_skeletons(sem, unit, cfg)
    _, C_true, _, _ = truth_effects(sem, 4)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > 0.1)
    truth = true_skeleton(sem)
    out = []
    for T in cfg['T']:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        cells = dict(sk)
        g = ges_skeleton(sem.simulate(T, np.random.default_rng([unit, 4, T])))
        g.damage = dict(GESD[str(T)])
        cells[('ges', 0.0)] = g
        for c_idx, (cell, s) in enumerate(cells.items()):
            rng = lambda tag: np.random.default_rng([unit, 13, T, c_idx, tag])
            r = {'topo': t_idx, 'T': T, 'cell': cell, 'true': damage_counts(s, truth), 'diag': G.diagnose_gate(data, s, 2)}
            for fp in [0.0, 0.1, 0.2]:
                for st in ['closed', 'open']:
                    r[f'{st}_{fp}'] = rec(G.auto3_raw(data, s, 2, 4, NB, rng(int(fp*10)*2 + (st=='open')), flip_prob=fp, force_state=st), C_true, nonnull)
            if cell == ('ges', 0.0):
                r['v3'] = rec(M.tolerant_v3(data, s, 2, 4, NB, rng(50)), C_true, nonnull)
            out.append(r)
    return out
if __name__ == '__main__':
    with ProcessPoolExecutor(3) as pool:
        allr = [x for o in pool.map(job, range(20)) for x in o]
    pickle.dump(allr, open(SP + '/probe3.pkl', 'wb'))
    print(len(allr))
