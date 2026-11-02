"""Design check of r5ngorient3 (docs/ext/r5ngorient3.md, section 3.3), run BEFORE registration: sign of the
"lik" statistic of ng_evidence3 at m = 10^6 (no gate, no jackknife, form forced) for the 50 ordered non-Gaussian law
pairs x b in {0.3, 0.6}. Catches a sign or derivation error; says nothing about finite-sample rates. Seed 999."""
import sys, math, itertools
import numpy as np
from pathlib import Path
R=str(Path(__file__).resolve().parents[3])
sys.path.insert(0,R+'/src'); sys.path.insert(0,R+'/experiments/ext/r4ngorient')
import laws
from paper4.ext_r5ngorient3 import g_super, g_sub, _fam
rng=np.random.default_rng(999)
opts=[("laplace",1),("t5",1),("skewexp",1),("skewexp",-1),("uniform",1)]
m=1_000_000
def pop(x,y):
    x=(x-x.mean())/x.std(); y=(y-y.mean())/y.std()
    ekx=np.mean(x**4)-3; eky=np.mean(y**4)-3
    skx=np.mean(x**3); sky=np.mean(y**3)
    S=(skx**2+sky**2)/6; K=(ekx**2+eky**2)/24
    rho=np.mean(x*y); s=math.sqrt(1-rho*rho)
    (gx,fx),(gy,fy)=_fam(ekx),_fam(eky)
    r_yx=(y-rho*x)/s; r_xy=(x-rho*y)/s
    Rl=np.mean(gx(x)-gx(r_xy)+gy(r_yx)-gy(y))
    return Rl, fx+"/"+fy, "skew" if S>=K else "lik"
for b in (0.3,0.6):
    for (lx,sx),(le,se) in itertools.product(opts,opts):
        x=laws.sample(rng,lx,m,sx); y=b*x+laws.sample(rng,le,m,se)
        Rl,fam,form=pop(x,y)
        flag="" if Rl>0 else "  <-- WRONG SIGN"
        print(f"b{b} {lx}{'+' if sx>0 else '-'} -> {le}{'+' if se>0 else '-'}: R_lik={Rl:+.5f} fam={fam} form*={form}{flag}")
