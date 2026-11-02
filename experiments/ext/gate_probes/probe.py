"""Exploratory probe on D-07H development (the calibration units of b1v2_auto)."""
import sys, json, pickle
sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/src'); sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments'); sys.path.insert(0, '/private/tmp/claude-501/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/scratchpad')
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from run_experiment import generator_config, unit_skeletons
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
from paper4.metrics import truth_effects
from paper4.learned import damage_counts
from paper4.skeleton import true_skeleton
from paper4 import methods as M
import gate_core as G
cfg = json.load(open('/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/configs/b1v2_auto.json'))
NB = 99

def rec(res, C_true, nonnull):
    if res.status != 'ok':
        return None
    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
    return {'dist': np.abs(C_true - mid)[nonnull], 'half': half[nonnull], 'lost': (res.C == 0)[nonnull], 'info': res.info,
            'abserr': float(np.median(np.abs(res.C - C_true)[nonnull]))}

def job(t_idx):
    topo = load_bank('D-07H', 'development')[t_idx]
    gen = generator_config(cfg)
    unit = cfg['seed_base'] + 500000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    sk = unit_skeletons(sem, unit, cfg)
    _, C_true, _, _ = truth_effects(sem, 4)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > 0.1)
    out = []
    truth = true_skeleton(sem)
    for T in cfg['T']:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, (cell, s) in enumerate(sk.items()):
            rng = lambda tag: np.random.default_rng([unit, 9, T, c_idx, tag])
            r = {'topo': t_idx, 'T': T, 'cell': cell, 'true': damage_counts(s, truth)}
            b = s.copy(); b.damage = {}
            try:
                pg, p, pc, po = G.gate(data, b, 2, rng(1), 99, 'minp')
                pf, *_ = G.gate(data, b, 2, rng(2), 99, 'fisher')
                pa, *_ = G.gate(data, b, 2, rng(3), 0, 'minp')
                r.update(p_minp=pg, p_fisher=pf, p_sidak=pa)
            except Exception as e:
                r.update(p_minp=None, p_fisher=None, p_sidak=None)
            r['closed'] = rec(G.auto3_raw(data, s, 2, 4, NB, rng(4), alpha_gate=-1), C_true, nonnull)
            r['open_max'] = rec(G.auto3_raw(data, s, 2, 4, NB, rng(5), alpha_gate=2), C_true, nonnull)
            r['open_bh'] = rec(G.auto3_raw(data, s, 2, 4, NB, rng(6), alpha_gate=2, budget='bh'), C_true, nonnull)
            r['open_all'] = rec(G.auto3_raw(data, s, 2, 4, NB, rng(7), alpha_gate=2, open_all=True), C_true, nonnull)
            r['v3'] = rec(M.tolerant_v3(data, s, 2, 4, NB, rng(8)), C_true, nonnull)
            out.append(r)
    return out

if __name__ == '__main__':
    with ProcessPoolExecutor(3) as pool:
        allr = [x for o in pool.map(job, range(20)) for x in o]
    pickle.dump(allr, open('/private/tmp/claude-501/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/scratchpad/probe.pkl', 'wb'))
    print(len(allr))
