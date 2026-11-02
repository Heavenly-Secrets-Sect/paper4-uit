"""Driver of direction r4hubscreen (docs/ext/r4hubscreen.md). Imports the runner's functions and never
edits them; it exists because the candidate needs two width factors per (T, stated kind): v5_1's factor
on runs where no equation is reduced (so the output is exactly v5_1's), and a factor tuned on the
reduced calibration runs otherwise. The runner keys factors by (method, T, stated kind) only.

Seeds and layout are the runner's, so rows pair with stored runner runs:
- unit = seed_base (+ 500 000 in calibration) + 1000 * topology index + replicate;
- data = sem.simulate(T, rng([unit, 2, T])); skeletons = run_experiment.unit_skeletons(sem, unit, cfg)
  with cfg["damage"] = the LAYOUT kinds/rates (default [extra, missing, reversed] x [0.2, 0.5], as
  ext_v51_eval / a2_baselines), so damaged skeletons and the cell index c_idx are those of the stored runs;
- only the cells listed in cfg["cells"] are fitted; method stream rng([unit, 3, T, c_idx, tag]) with
  tag 1 for plugin and plugin_hs and ext_seed("tolerant_v5_1") for tolerant_v5_1 AND tolerant_v5_1_hs
  (same stream: identical output when nothing is reduced).

Methods evaluated (main phase):
- tolerant_v5_1          raw x f_v51(T, kind)   (f_v51 from the frozen file when it has the key, else tuned here)
- tolerant_v5_1_hs       CANDIDATE: raw x f_v51(T, kind) if no reduction happened in the run, else raw x f_red(T, kind)
- tolerant_v5_1_hs1      secondary: raw x one factor tuned on all candidate calibration runs
- plugin                 raw percentile interval
- plugin_cal             plugin x factor per (T, kind, rate) (the runner's ``inflate``)
- plugin_hs_cal          secondary always-runnable reference: plugin with CSIS reduction x factor per (T, kind)

Factor = the runner's rule: smallest c on C_GRID (1.0..10, step 0.1) with pooled coverage of non-null
pairs >= min(0.95, max coverage - 0.005). f_red fallback (pre-registered): if fewer than MIN_RED reduced
calibration runs at (T, kind), pool the reduced runs over kinds at T; if still fewer, pool over every T of
the config; if none, f_v51. If f_v51 is missing at (T, kind) (v5_1 completed no calibration run),
non-reduced candidate runs use the f_red chain.

Run: python experiments/ext/r4hubscreen/run_r4.py --config experiments/configs/ext_r4hubscreen_lag2.json --workers 3
Writes results/<name>/{runs.jsonl, calibration.json, cal_counts.json, manifest.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
from run_experiment import C_GRID, ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.ext_r4hubscreen import plugin_hs, tolerant_v5_1_hs  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

MIN_RED = 3
LAYOUT = {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}


def _scale(res, c, name):
    out = M.calibrate_width(res, c, name)
    if res.status == "ok":
        out.info = {**res.info, "c": c}
    return out


def run_unit(args):
    cfg, topo, t_idx, rep, phase, fac = args
    warnings.filterwarnings("ignore")
    gen = generator_config(cfg)
    H, lag, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    lay = dict(cfg, damage=cfg.get("layout", LAYOUT))
    skels = unit_skeletons(sem, unit, lay)
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    want = {(k, float(r)) for k, r in cfg["cells"]}
    out = []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if (kind, float(rate)) not in want:
                continue
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)
            wk = M.width_key(skel.damage)
            raw = {"plugin": M.plugin(data, skel, lag, H, n_boot, rng(1)),
                   "plugin_hs": plugin_hs(data, skel, lag, H, n_boot, rng(1)),
                   "tolerant_v5_1": tolerant_v5_1(data, skel, lag, H, n_boot, rng(ext_seed("tolerant_v5_1"))),
                   "tolerant_v5_1_hs": tolerant_v5_1_hs(data, skel, lag, H, n_boot, rng(ext_seed("tolerant_v5_1")))}
            red = int(raw["tolerant_v5_1_hs"].info.get("hs_reduced", 0))
            base = {"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind,
                    "rate": rate, "k": skel.damage.get("k", 0), "lag_max": lag, "n_nonnull_truth": int(nonnull.sum()),
                    "hs_reduced": red, "v51_status": raw["tolerant_v5_1"].status,
                    "plugin_status": raw["plugin"].status}
            if phase == "calibration":
                for name, res in raw.items():
                    if res.status != "ok":
                        continue
                    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                    out.append({**base, "method": name, "dist": np.abs(C_true - mid)[nonnull].tolist(),
                                "half": half[nonnull].tolist()})
                continue
            f = fac
            fv = f["v51"].get(f"{T}|{wk}")
            fr = f["red"].get(f"{T}|{wk}")
            final = {
                "tolerant_v5_1": _scale(raw["tolerant_v5_1"], fv, "tolerant_v5_1"),
                "tolerant_v5_1_hs": _scale(raw["tolerant_v5_1_hs"], fr if red or fv is None else fv, "tolerant_v5_1_hs"),
                "tolerant_v5_1_hs1": _scale(raw["tolerant_v5_1_hs"], f["hs_all"].get(f"{T}|{wk}"), "tolerant_v5_1_hs1"),
                "plugin": raw["plugin"],
                "plugin_cal": _scale(raw["plugin"], f["plugin"].get(f"{T}|{kind}|{rate}"), "plugin_cal"),
                "plugin_hs_cal": _scale(raw["plugin_hs"], f["plugin_hs"].get(f"{T}|{wk}"), "plugin_hs_cal"),
            }
            for name, res in final.items():
                row = evaluate(sem, res, H, tau_effect=cfg["tau_effect"])
                row.update(base)
                out.append(row)
    return out


def factor(dist, half):
    dist, half = np.array(dist), np.array(half)
    cov = np.array([(dist <= c * half).mean() for c in C_GRID])
    target = min(1 - M.ALPHA, cov.max() - 0.005)
    return float(C_GRID[np.argmax(cov >= target)])


def calibrate(cfg, workers):
    cal = cfg["calibration"]
    topos = load_bank(cal["bank"], cal["split"])[: cal.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, "calibration", None) for t_idx, topo in enumerate(topos)
            for rep in range(cal["replicates"])]
    recs = []
    with ProcessPoolExecutor(workers) as pool:
        for o in pool.map(run_unit, jobs):
            recs.extend(o)
    groups = defaultdict(lambda: ([], [], 0))

    def add(key, r):
        d, h, n = groups[key]
        groups[key] = (d + r["dist"], h + r["half"], n + 1)

    for r in recs:
        T, wk = r["T"], M.width_key({"kind": r["kind"], "k": r["k"]})
        m = r["method"]
        if m == "tolerant_v5_1":
            add(("v51", f"{T}|{wk}"), r)
        elif m == "tolerant_v5_1_hs":
            add(("hs_all", f"{T}|{wk}"), r)
            if r["hs_reduced"]:
                add(("red", f"{T}|{wk}"), r)
                add(("red_T", f"{T}"), r)
                add(("red_all", "all"), r)
        elif m == "plugin":
            add(("plugin", f"{T}|{r['kind']}|{r['rate']}"), r)
        elif m == "plugin_hs":
            add(("plugin_hs", f"{T}|{wk}"), r)
    fac = {k: {} for k in ("v51", "hs_all", "red", "plugin", "plugin_hs")}
    counts = {}
    for (fam, key), (d, h, n) in groups.items():
        counts[f"{fam}|{key}"] = n
        if fam in fac and d:
            fac[fam][key] = factor(d, h)
    tuned_v51 = dict(fac["v51"])
    frozen = {}
    if cfg.get("frozen_v51"):
        fz = json.loads((ROOT / cfg["frozen_v51"]).read_text(encoding="utf-8"))
        for key in list(fac["v51"]) + [f"{T}|{k}" for T in cfg["T"] for k in ("none", "extra", "missing", "reversed")]:
            fk = f"tolerant_v5_1|{key}"
            if fk in fz:
                frozen[key] = fz[fk]
                fac["v51"][key] = fz[fk]
    # f_red with the pre-registered fallback chain
    red_final, red_src = {}, {}
    for T in cfg["T"]:
        for wk in ("none", "extra", "missing", "reversed"):
            key = f"{T}|{wk}"
            if counts.get(f"red|{key}", 0) >= MIN_RED:
                red_final[key], red_src[key] = fac["red"][key], "T,kind"
            elif counts.get(f"red_T|{T}", 0) >= MIN_RED:
                g = groups[("red_T", f"{T}")]
                red_final[key], red_src[key] = factor(g[0], g[1]), "T pooled over kinds"
            elif counts.get("red_all|all", 0) >= MIN_RED:
                g = groups[("red_all", "all")]
                red_final[key], red_src[key] = factor(g[0], g[1]), "pooled over T and kinds"
            elif key in fac["v51"]:
                red_final[key], red_src[key] = fac["v51"][key], "f_v51 (no reduced calibration run)"
    fac["red"] = red_final
    return fac, {"counts": counts, "red_source": red_src, "v51_tuned_in_run": tuned_v51, "v51_frozen_used": frozen}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    fac, meta = calibrate(cfg, a.workers)
    t_cal = time.perf_counter() - t0
    (out / "calibration.json").write_text(json.dumps(fac, indent=1), encoding="utf-8")
    (out / "cal_counts.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, "main", fac) for t_idx, topo in enumerate(topos) for rep in range(cfg["replicates"])]
    rows = []
    with ProcessPoolExecutor(a.workers) as pool:
        for o in pool.map(run_unit, jobs):
            rows.extend(o)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    man = {"config": cfg, "seconds_calibration": round(t_cal, 1), "seconds_total": round(time.perf_counter() - t0, 1),
           "n_rows": len(rows), "workers": a.workers,
           "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topos]}
    (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"{len(rows)} rows in {man['seconds_total']} s (calibration {man['seconds_calibration']} s) -> {out}")


if __name__ == "__main__":
    main()
