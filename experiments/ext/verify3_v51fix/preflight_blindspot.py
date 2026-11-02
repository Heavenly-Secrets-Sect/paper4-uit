"""Shows that preflight_p4h2.py does not detect a patch of paper4.methods.calibrate_width / tolerant_v3 /
width_key (used by the runner for both methods / the v4 reference), as an unpinned ext_* module could do
at import. In-memory only; no file in src/ is touched."""
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
import paper4.methods as M
orig = M.calibrate_width
def evil_cw(res, c, name):  # same signature; would e.g. alter widths silently
    return orig(res, c, name)
M.calibrate_width = evil_cw
M.tolerant_v3 = (lambda f: (lambda *a, **k: f(*a, **k)))(M.tolerant_v3)
spec = importlib.util.spec_from_file_location("pf", ROOT / "experiments/ext/v51fix/preflight_p4h2.py")
pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)
rc = pf.main(["--out", str(ROOT / "results/ext_verify3_v51fix/preflight_blindspot.json")])
print("preflight exit code with patched calibrate_width and tolerant_v3:", rc)
