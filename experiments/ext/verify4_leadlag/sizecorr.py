import sys, json
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/experiments/ext/verify4_leadlag")
sys.path.insert(0, "/Users/kietnt/Desktop/Workspace/Paper4_UIT/src")
import numpy as np
from knowntruth import sim  # noqa (re-runs module top-level; acceptable cost)
from paper4.ext_r4leadlag import haugh_q
out = {}
for T in (80, 150, 1000):
    M = 4 if T <= 80 else 6
    n = 1000 if T < 1000 else 300
    rng = np.random.default_rng(42 + T)
    def Qs(**kw):
        a, d = [], []
        for _ in range(n):
            A, Dd = sim(T, rng=rng, **kw); a.append(haugh_q(*A, M)[0]); d.append(haugh_q(*Dd, M)[0])
        return np.array(a), np.array(d)
    a0, d0 = Qs(phi=0.0, lag_u=0, lag_v=0, conf=False, edge=True)
    qa, qd = np.quantile(a0, .95), np.quantile(d0, .95)
    for name, kw in {"conf phi0.8 lag0/lag0": dict(phi=0.8, lag_u=0, lag_v=0, conf=True, edge=False),
                     "conf phi0.8 lag0/lag2": dict(phi=0.8, lag_u=0, lag_v=2, conf=True, edge=False)}.items():
        a1, d1 = Qs(**kw)
        auc_a = float((a1[:, None] > a0[None, :]).mean()); auc_d = float((d1[:, None] > d0[None, :]).mean())
        print(f"T={T} {name}: A-like mean Q null {a0.mean():.2f} (nominal df {2*M}) conf {a1.mean():.2f}; size-corrected power {np.mean(a1>qa):.3f}; AUROC {auc_a:.3f} | D-like null mean {d0.mean():.2f}, power {np.mean(d1>qd):.3f}, AUROC {auc_d:.3f}")
        out[f"T{T}|{name}"] = dict(A_null_meanQ=float(a0.mean()), df=2*M, A_conf_meanQ=float(a1.mean()), A_power=float(np.mean(a1>qa)), A_auroc=auc_a,
                                   D_null_meanQ=float(d0.mean()), D_power=float(np.mean(d1>qd)), D_auroc=auc_d)
json.dump(out, open("/Users/kietnt/Desktop/Workspace/Paper4_UIT/results/ext_verify4_leadlag/sizecorr.json", "w"), indent=1)
