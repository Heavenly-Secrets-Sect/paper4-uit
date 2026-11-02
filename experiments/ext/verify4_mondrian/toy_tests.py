"""Known-truth toy tests of ext_r4mondrian helpers + bit-identity of the wrapper on a few real cases."""
import json, math, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
from paper4 import ext_r4mondrian as X, ext_v51, methods as M
out = {}
# 1. arrival: chain 0 -lag1-> 1 -lag0-> 2 -lag2-> 3 ; 3 isolated from 0 back; H=4
terms = [[(0, 1)], [(1, 1), (0, 1)], [(2, 1), (1, 0)], [(3, 1), (2, 2)]]
A = X.arrival([terms], 4, 4)[0]
exp = np.array([[0, 1, 1, 3], [5, 0, 0, 2], [5, 5, 0, 2], [5, 5, 5, 0]])
out["arrival_ok"] = bool((A == exp).all()); out["arrival"] = A.tolist()
# path longer than H capped: 0->1 lag 3, 1->2 lag 3, H=4 -> 0->2 = 6 capped at 5
A2 = X.arrival([[[], [(0, 3)], [(1, 3)]]], 3, 4)[0]
out["arrival_cap_ok"] = int(A2[0, 2]) == 5 and int(A2[0, 1]) == 3
# 2. conformal_q: N=19 -> rank ceil(20*.95)=19 -> max; N=18 -> rank ceil(19*.95)=19>18 -> inf; N=100 -> rank 96
out["cq19"] = X.conformal_q(np.arange(1, 20)) == 19
out["cq18_inf"] = math.isinf(X.conformal_q(np.arange(1, 19)))
out["cq100"] = X.conformal_q(np.arange(1, 101)) == 96
# 3. marginal coverage simulation for iid scores (sanity of the q rule): N=200 cal, many reps
rng = np.random.default_rng(0); cov = []
for _ in range(4000):
    s = np.abs(rng.standard_normal(201)); q = X.conformal_q(s[:200]); cov.append(s[200] <= q)
out["iid_marginal_cov"] = float(np.mean(cov))
# 3b. clustered scores: 20 clusters x 60 pairs, cluster random scale -> pooled pair-level q, test on new cluster
cov = []; condcov = []
for _ in range(2000):
    sc = np.exp(0.4 * rng.standard_normal(21))
    s = np.abs(rng.standard_normal((21, 60))) * sc[:, None]
    q = X.conformal_q(s[:20].ravel()); cv = (s[20] <= q).mean(); cov.append(cv)
out["clustered_marginal_cov"] = float(np.mean(cov)); out["clustered_cov_sd_given_cal"] = float(np.std(cov))
# 4. merge rule
t = X.build_q_table({(40, "x"): (np.arange(1, 101) / 10, np.r_[np.ones(30, bool), np.zeros(70, bool)])})
out["merge_ok"] = t["40|x|R"]["merged"] and t["40|x|R"]["q"] == t["40|x|all"]["q"]
json.dump(out, open(ROOT / "results/ext_verify4_mondrian/toy_tests.json", "w"), indent=1)
print(json.dumps(out, indent=1))
