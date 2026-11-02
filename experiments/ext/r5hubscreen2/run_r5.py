"""Driver of round 5 component B, ``hubscreen`` v2 (docs/ext/r5hubscreen2.md). Imports the runner's helpers
and the methods; never edits existing files.

Two subcommands:

  calibrate --config experiments/configs/ext_r5hubscreen2_cal.json
      D-07H development, units seed_base + 500 000 + 1000 * topology + replicate (the runner's calibration
      units). Fits ONLY tolerant_v5_1_hs2 (the only factor re-tuned in round 5 is f_red). Keeps the reduced
      runs and tunes f_red(T, kind) with the runner's rule; fallback chain fixed in advance (as round 4):
      >= MIN_RED reduced runs at (T, kind) -> that key; else pooled over kinds at T; else pooled over every
      calibration T; else f_v51(T, kind). Writes results/<name>/{calibration.json, cal_counts.json, manifest.json}.

  main --config experiments/configs/ext_r5hubscreen2_{p2,g}.json
      D-07 development, units seed_base + 1000 * topology + replicate, data rng([unit, 2, T]), skeletons
      run_experiment.unit_skeletons with the layout [extra, missing, reversed] x [0.2, 0.5] (same c_idx as the
      runner). Method stream rng([unit, 3, T, c_idx, tag]): tag ext_seed("tolerant_v5_1") for tolerant_v5_1,
      tolerant_v5_1_hs2 and tolerant_v5_1_hs (round 4 v1); tag 1 for plugin_hs (as round 4).
      Factors (no re-tuning in this run):
        f_v51(T, kind): results/ext_r4hubscreen_lag2/calibration.json["v51"] (round 4; T40 there = frozen file),
                        overridden by experiments/ext/v51/frozen_v4_v51.json where that file has the key;
        f_red(T, kind): this round's calibration (calibrate subcommand);
        v1 two factors: f_v51 / results/ext_r4hubscreen_lag2/calibration.json["red"];
        plugin_hs_cal:  results/ext_r4hubscreen_lag2/calibration.json["plugin_hs"] (round 4, as defined there).
      Methods written (subset by cfg["methods"]):
        tolerant_v5_1      raw x f_v51
        tolerant_v5_1_hs2  raw x f_v51 if no reduction in the run (and f_v51 exists), else raw x f_red
        tolerant_v5_1_hs   raw x f_v51 / f_red_r4 (round 4 rule)            [descriptive]
        plugin_hs_cal      plugin_hs raw x round-4 factor                     [P2c comparator]
      Extra row fields: hs_reduced, v51_status, hs_status, raw_ident_v51 (hs2 raw C/lo/hi bit-identical to
      v5_1 raw, both ok), raw_ident_v1 (hs2 vs v1), hs1_reduced, plugin_hs_status.

Run: python experiments/ext/r5hubscreen2/run_r5.py calibrate --config ... --workers 3
"""
from __future__ import annotations

import argparse
import hashlib
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
from paper4.ext_r5hubscreen2 import tolerant_v5_1_hs2  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

MIN_RED = 3
LAYOUT = {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}
KINDS = ("none", "extra", "missing", "reversed")
R4_CAL = "results/ext_r4hubscreen_lag2/calibration.json"
FROZEN_V51 = "experiments/ext/v51/frozen_v4_v51.json"
FORBIDDEN = ("P4-H1", "P4-H2")


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def _scale(res, c, name):
    out = M.calibrate_width(res, c, name)
    if res.status == "ok":
        out.info = {**res.info, "c": c}
    return out


def _same(a, b):
    return (a.status == "ok" and b.status == "ok" and np.array_equal(a.C, b.C)
            and np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi))


def run_unit(args):
    cfg, topo, t_idx, rep, phase, fac = args
    warnings.filterwarnings("ignore")
    gen = generator_config(cfg)
    H, lag, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, dict(cfg, damage=LAYOUT))
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    want = {(k, float(r)) for k, r in cfg["cells"]}
    methods = cfg.get("methods", [])
    out = []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if (kind, float(rate)) not in want:
                continue
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)
            wk = M.width_key(skel.damage)
            tag51 = ext_seed("tolerant_v5_1")
            hs2 = tolerant_v5_1_hs2(data, skel, lag, H, n_boot, rng(tag51))
            red = int(hs2.info.get("hs_reduced", 0))
            base = {"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind,
                    "rate": rate, "k": skel.damage.get("k", 0), "lag_max": lag, "n_nonnull_truth": int(nonnull.sum()),
                    "hs_reduced": red, "hs_status": hs2.status,
                    **{k: hs2.info.get(k) for k in ("hs_eq_data", "hs_eq_total", "hs_trunc_eq_data", "hs_trunc_eq_total",
                                                    "hs_contemp_dropped", "hs_fit_fail", "hs_screen_fail",
                                                    "hs_draws_reduced", "hs_draws_total")}}
            if phase == "calibration":
                if hs2.status == "ok" and red:
                    mid, half = (hs2.lo + hs2.hi) / 2, (hs2.hi - hs2.lo) / 2
                    out.append({**base, "dist": np.abs(C_true - mid)[nonnull].tolist(), "half": half[nonnull].tolist()})
                else:
                    out.append({**base, "dist": None, "half": None})
                continue
            raw = {"tolerant_v5_1_hs2": hs2}
            if "tolerant_v5_1" in methods:
                raw["tolerant_v5_1"] = tolerant_v5_1(data, skel, lag, H, n_boot, rng(tag51))
            if "tolerant_v5_1_hs" in methods:
                raw["tolerant_v5_1_hs"] = tolerant_v5_1_hs(data, skel, lag, H, n_boot, rng(tag51))
            if "plugin_hs_cal" in methods:
                raw["plugin_hs"] = plugin_hs(data, skel, lag, H, n_boot, rng(1))
            v51 = raw.get("tolerant_v5_1")
            v1 = raw.get("tolerant_v5_1_hs")
            base.update({"v51_status": v51.status if v51 else None,
                         "raw_ident_v51": bool(v51 is not None and _same(hs2, v51)),
                         "raw_ident_v1": bool(v1 is not None and _same(hs2, v1)),
                         "hs1_reduced": int(v1.info.get("hs_reduced", 0)) if v1 is not None else None,
                         "hs1_status": v1.status if v1 is not None else None,
                         "plugin_hs_status": raw["plugin_hs"].status if "plugin_hs" in raw else None})
            fv = fac["v51"].get(f"{T}|{wk}")
            fr = fac["red"].get(f"{T}|{wk}")
            final = {"tolerant_v5_1_hs2": _scale(hs2, fr if (red or fv is None) else fv, "tolerant_v5_1_hs2")}
            if v51 is not None:
                final["tolerant_v5_1"] = _scale(v51, fv, "tolerant_v5_1")
            if v1 is not None:
                r1 = int(v1.info.get("hs_reduced", 0))
                fr1 = fac["red_r4"].get(f"{T}|{wk}")
                final["tolerant_v5_1_hs"] = _scale(v1, fr1 if (r1 or fv is None) else fv, "tolerant_v5_1_hs")
            if "plugin_hs" in raw:
                final["plugin_hs_cal"] = _scale(raw["plugin_hs"], fac["plugin_hs"].get(f"{T}|{wk}"), "plugin_hs_cal")
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


def f_v51_table():
    r4 = json.loads((ROOT / R4_CAL).read_text(encoding="utf-8"))
    fz = json.loads((ROOT / FROZEN_V51).read_text(encoding="utf-8"))
    tab = dict(r4["v51"])
    src = {k: "round4 calibration.json v51" for k in tab}
    for k, v in fz.items():
        if k.startswith("tolerant_v5_1|"):
            key = k.split("|", 1)[1]
            tab[key] = v
            src[key] = "frozen_v4_v51.json"
    return tab, src


def guard(cfg):
    for b in (cfg["bank"], cfg.get("calibration", {}).get("bank", "")):
        if any(f in b for f in FORBIDDEN):
            raise SystemExit(f"forbidden bank {b}")
    if cfg["split"] != "development":
        raise SystemExit("only development splits")


def calibrate_cmd(cfg, workers):
    guard(cfg)
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, "calibration", None) for t_idx, topo in enumerate(topos)
            for rep in range(cfg["replicates"])]
    recs = []
    with ProcessPoolExecutor(workers) as pool:
        for o in pool.map(run_unit, jobs):
            recs.extend(o)
    groups = defaultdict(lambda: [[], [], 0])
    status = defaultdict(lambda: defaultdict(int))
    for r in recs:
        key = f"{r['T']}|{M.width_key({'kind': r['kind'], 'k': r['k']})}"
        status[key][f"{r['hs_status']}|red{r['hs_reduced']}"] += 1
        if r["dist"] is None:
            continue
        for g in (("red", key), ("red_T", str(r["T"])), ("red_all", "all")):
            groups[g][0] += r["dist"]
            groups[g][1] += r["half"]
            groups[g][2] += 1
    fv, _ = f_v51_table()
    red, srcs, counts = {}, {}, {f"{a}|{b}": g[2] for (a, b), g in groups.items()}
    for T in cfg["fill_T"]:
        for wk in KINDS:
            key = f"{T}|{wk}"
            if counts.get(f"red|{key}", 0) >= MIN_RED:
                g, s = groups[("red", key)], "T,kind"
            elif counts.get(f"red_T|{T}", 0) >= MIN_RED:
                g, s = groups[("red_T", str(T))], "T pooled over kinds"
            elif counts.get("red_all|all", 0) >= MIN_RED:
                g, s = groups[("red_all", "all")], "pooled over every calibration T and kind"
            else:
                g, s = None, "f_v51 (no reduced calibration run)"
            if g is not None:
                red[key], srcs[key] = factor(g[0], g[1]), s
            elif key in fv:
                red[key], srcs[key] = fv[key], s
    (out / "calibration.json").write_text(json.dumps({"red": red}, indent=1), encoding="utf-8")
    (out / "cal_counts.json").write_text(json.dumps({"counts": counts, "red_source": srcs,
                                                     "status": {k: dict(v) for k, v in status.items()}}, indent=1),
                                         encoding="utf-8")
    man = {"config": cfg, "seconds": round(time.perf_counter() - t0, 1), "n_records": len(recs), "workers": workers,
           "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topos]}
    (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"calibration: {len(recs)} records in {man['seconds']} s -> {out}")


def main_cmd(cfg, workers):
    guard(cfg)
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    r4 = json.loads((ROOT / R4_CAL).read_text(encoding="utf-8"))
    fv, fv_src = f_v51_table()
    calp = ROOT / cfg["red_calibration"]
    fac = {"v51": fv, "red": json.loads(calp.read_text(encoding="utf-8"))["red"],
           "red_r4": r4["red"], "plugin_hs": r4["plugin_hs"]}
    (out / "factors_used.json").write_text(json.dumps({**fac, "v51_source": fv_src, "sha256": {
        R4_CAL: sha(R4_CAL), FROZEN_V51: sha(FROZEN_V51), cfg["red_calibration"]: sha(cfg["red_calibration"])}},
        indent=1), encoding="utf-8")
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, "main", fac) for t_idx, topo in enumerate(topos) for rep in range(cfg["replicates"])]
    rows = []
    with ProcessPoolExecutor(workers) as pool:
        for o in pool.map(run_unit, jobs):
            rows.extend(o)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    man = {"config": cfg, "seconds": round(time.perf_counter() - t0, 1), "n_rows": len(rows), "workers": workers,
           "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topos]}
    (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"{len(rows)} rows in {man['seconds']} s -> {out}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["calibrate", "main"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    (calibrate_cmd if a.cmd == "calibrate" else main_cmd)(cfg, a.workers)


if __name__ == "__main__":
    main()
