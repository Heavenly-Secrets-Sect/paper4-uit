import sys, json, pickle
SP='/private/tmp/claude-501/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/scratchpad'
sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/src'); sys.path.insert(0, '/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments'); sys.path.insert(0, SP)
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from run_experiment import generator_config, unit_skeletons
from paper4.generator import build_dynamic_sem
from paper4.topology import load_bank
import gate2
cfg = json.load(open('/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/configs/b1v2_auto.json'))
def job(t_idx):
    topo = load_bank('D-07H', 'development')[t_idx]
    unit = cfg['seed_base'] + 500000 + 1000 * t_idx
    sem = build_dynamic_sem(topo, generator_config(cfg), np.random.default_rng([unit, 0]))
    sk = unit_skeletons(sem, unit, cfg)
    out = {}
    for T in cfg['T']:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, (cell, s) in enumerate(sk.items()):
            b = s.copy(); b.damage = {}
            r = {}
            for key, tests, ng in [('r_sidak','restricted',0), ('r_boot','restricted',99), ('a_boot','alllag',99)]:
                try:
                    r[key] = gate2.gate_p(data, b, 2, np.random.default_rng([unit, 11, T, c_idx]), tests, ng)[0]
                except Exception:
                    r[key] = None
            out[(t_idx, T, cell)] = r
    return out
if __name__ == '__main__':
    res = {}
    with ProcessPoolExecutor(3) as pool:
        for o in pool.map(job, range(20)): res.update(o)
    pickle.dump(res, open(SP + '/probe2.pkl', 'wb'))
