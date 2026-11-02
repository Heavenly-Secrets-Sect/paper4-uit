"""Driver of round 5 ID "v52": ``tolerant_v5_2`` (src/paper4/ext_r5v52.py) vs ``tolerant_v5_1`` (docs/ext/r5v52.md).

Imports the runner's helpers, component A's shock laws (experiments/ext/r4ngorient/laws.py), the round-1 pair
helper delta_C (experiments/ext/revlag/run_pairs.py) and component B's factor table (experiments/ext/r5hubscreen2/
run_r5.py: f_v51_table, _scale); never edits existing files.

Per unit (topology x replicate), exactly as the runner, run_ng.py (A) and run_r5.py (B):
  unit = seed_base + unit_offset + 1000 * topology_index + replicate   (unit_offset 0 for evaluation)
  SEM rng([unit, 0]); skeletons run_experiment.unit_skeletons with layout [extra, missing, reversed] x [0.2, 0.5]
  (c_idx = position in that layout, none = 0); latent scenario add_latent(sem, k, rng([unit, 5]), n_children);
  data: shock "gauss" -> sem_s.simulate(T, rng([unit, 2, T])); shock "ng_mix" -> laws.simulate(sem, T,
  rng([unit, 2, T]), laws.node_laws("ng_mix", unit, n)); then add_measurement_noise(data, meas_noise, rng([unit, 6, T])).
Method streams rng([unit, 3, T, c_idx, tag]): tag ext_seed("tolerant_v5_1") for tolerant_v5_1 AND tolerant_v5_2
(common random numbers, as A and B); tag 1 for plugin_hs (as round 4 / B).

Width factors (no re-tuning anywhere in this driver):
  f_v51(T, kind): run_r5.f_v51_table() = round-4 v5_1 factors for T < 40 overridden by
                  experiments/ext/v51/frozen_v4_v51.json (all keys at T 40/80/150);
  f_red(T, kind): cfg["red_calibration"] = results/ext_r5v52_cal/calibration.json, tuned by THIS driver's
                  calibration phase on tolerant_v5_2's own reduced runs (the only re-tuned factor of round 5);
  f_red_B       : cfg["red_calibration_B"] = component B's f_red (results/ext_r5hubscreen2_cal/calibration.json),
                  only for the descriptive row tolerant_v5_2_fredB (same raw run, other f_red);
  plugin_hs_cal : results/ext_r4hubscreen_lag2/calibration.json["plugin_hs"] (round 4, as B).
  tolerant_v5_1 = raw x f_v51;  tolerant_v5_2 = raw x (f_red if hs_reduced or f_v51 missing else f_v51).

Calibration phase (cfg "phase": "calibration"): D-07H development, units seed_base + unit_offset + 500 000 +
1000 * topology + replicate (the runner's calibration units), data sem.simulate(T, rng([unit, 2, T])), fits ONLY
tolerant_v5_2 on v5_1's stream, keeps its reduced ok runs and picks f_red(T, kind) with run_r5.factor and run_r5's
fallback chain (MIN_RED = 3). Writes results/<name>/{calibration.json, cal_counts.json, manifest.json}.

Rows: runner's ``evaluate`` + topology, replicate, T, kind, rate, k, scenario, shock, fac, sec, and on every row of
the cell the v5_2 run facts: hs_* (reduction log), v51_status, v52_status, raw_ident_v51 (v5_2 raw C/lo/hi
bit-identical to v5_1 raw, both ok), gate_eval / gate_open (draws), data_gate_eval / data_gate_open, no_gate.
pairs.npz: non-null pairs (C_t, C_e, lo, hi, dC) for tolerant_v5_1 and tolerant_v5_2.

Guard: refuses any bank containing "P4-H1" or "P4-H2" and any split other than development.
Run: python experiments/ext/r5v52/run_v52.py --config experiments/configs/ext_r5v52_<x>.json --workers 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
for p in ("src", "experiments", "experiments/ext/r4ngorient", "experiments/ext/revlag", "experiments/ext/r5hubscreen2"):
    sys.path.insert(0, str(ROOT / p))

import laws  # noqa: E402  (experiments/ext/r4ngorient/laws.py, unchanged)
import run_r5  # noqa: E402  (experiments/ext/r5hubscreen2/run_r5.py, unchanged)
from run_experiment import ext_seed, generator_config, public, unit_skeletons  # noqa: E402
from run_pairs import delta_C  # noqa: E402  (experiments/ext/revlag/run_pairs.py, unchanged)
from paper4 import methods as M  # noqa: E402
from paper4.ext_r4hubscreen import plugin_hs  # noqa: E402
from paper4.ext_r5v52 import tolerant_v5_2  # noqa: E402
from paper4.ext_v51 import tolerant_v5_1  # noqa: E402
from paper4.generator import add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

LAYOUT = {"kinds": ["extra", "missing", "reversed"], "rates": [0.2, 0.5]}
FORBIDDEN = ("P4-H1", "P4-H2")
PCOLS = ("topo", "rep", "T", "cell", "method", "j", "i", "C_t", "C_e", "lo", "hi", "dC")
METHOD_IDX = {"tolerant_v5_1": 0, "tolerant_v5_2": 1}
HS_KEYS = ("hs_reduced", "hs_eq_data", "hs_eq_total", "hs_trunc_eq_data", "hs_trunc_eq_total", "hs_contemp_dropped",
           "hs_fit_fail", "hs_screen_fail", "hs_draws_reduced", "hs_draws_total", "hs_ev_reduced", "hs_ev_eq_total",
           "hs_ev_fit_fail")
DEPS = ["src/paper4/ext_r5v52.py", "src/paper4/ext_r5ngorient3.py", "src/paper4/ext_r5hubscreen2.py",
        "src/paper4/ext_r4ngorient.py", "src/paper4/ext_r4hubscreen.py", "src/paper4/ext_v51.py",
        "src/paper4/ext_narrow.py", "src/paper4/methods.py", "src/paper4/estimator.py",
        "experiments/ext/r4ngorient/laws.py", "experiments/ext/r5hubscreen2/run_r5.py",
        "experiments/ext/revlag/run_pairs.py", "experiments/run_experiment.py", "experiments/ext/r5v52/run_v52.py"]


def sha(p) -> str:
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def same_raw(a, b) -> bool:
    return (a.status == "ok" and b.status == "ok" and np.array_equal(a.C, b.C)
            and np.array_equal(a.lo, b.lo) and np.array_equal(a.hi, b.hi))


def gate_summary(diag: dict | None) -> dict:
    if not diag:
        return {"gate_eval": 0, "gate_open": 0, "data_gate_eval": 0, "data_gate_open": 0, "no_gate": True}
    data = list(diag.get("data_cands", [])) + list(diag.get("data_pool", []))
    ge, go = diag.get("n_gate_draws", [0, 0])
    dgo = sum(1 for r in data if r[2])
    return {"gate_eval": int(ge), "gate_open": int(go), "data_gate_eval": len(data), "data_gate_open": int(dgo),
            "no_gate": bool(go == 0 and dgo == 0)}


def run_unit(args):
    warnings.filterwarnings("ignore")
    cfg, topo, t_idx, rep, fac = args
    gen = generator_config(cfg)
    H, lag, n_boot, tau = cfg["H"], gen.lag_max, cfg["n_boot"], cfg["tau_effect"]
    unit = cfg["seed_base"] + cfg.get("unit_offset", 0) + 1000 * t_idx + rep
    R = np.random.default_rng
    sem = build_dynamic_sem(topo, gen, R([unit, 0]))
    skels = unit_skeletons(sem, unit, dict(cfg, damage=LAYOUT))
    _, C_t, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_t) > tau)
    jj, ii = np.nonzero(nonnull)
    sc = cfg.get("scenario") or {"name": "clean"}
    sem_s = add_latent(sem, sc.get("latent", 0), R([unit, 5]), n_children=sc.get("latent_children", 3))
    shock = cfg.get("shock", "gauss")
    node_law = laws.node_laws(shock, unit, sem.n)
    want = {(k, float(r)) for k, r in cfg["cells"]}
    methods = cfg["methods"]
    tag51 = ext_seed("tolerant_v5_1")
    rows = []
    pc = {k: [] for k in PCOLS}
    for T in cfg["T"]:
        if shock == "gauss":
            data = sem_s.simulate(T, R([unit, 2, T]))
        else:
            if sem_s is not sem:
                raise SystemExit("latent scenario only with gauss shock")
            data = laws.simulate(sem, T, R([unit, 2, T]), node_law)
        data = add_measurement_noise(data, sc.get("meas_noise", 0.0), R([unit, 6, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if (kind, float(rate)) not in want:
                continue
            rng = lambda tag: R([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)
            wk = M.width_key(skel.damage)
            raw, sec = {}, {}
            for name in methods:
                t0 = time.perf_counter()
                if name == "tolerant_v5_1":
                    raw[name] = tolerant_v5_1(data, skel, lag, H, n_boot, rng(tag51))
                elif name == "tolerant_v5_2":
                    raw[name] = tolerant_v5_2(data, skel, lag, H, n_boot, rng(tag51))
                elif name == "plugin_hs_cal":
                    raw[name] = plugin_hs(data, skel, lag, H, n_boot, rng(1))
                elif name == "tolerant_v5_2_fredB":      # descriptive: same raw run, component B's f_red
                    continue
                else:
                    raise SystemExit(f"unknown method {name}")
                sec[name] = round(time.perf_counter() - t0, 3)
            v52, v51 = raw["tolerant_v5_2"], raw.get("tolerant_v5_1")
            gs = gate_summary(v52.info.pop("ng_diag", None) if v52.info else None)
            red = int(v52.info.get("hs_reduced", 0))
            fv, fr = fac["v51"].get(f"{T}|{wk}"), fac["red"].get(f"{T}|{wk}")
            fac_used = {"tolerant_v5_1": fv, "tolerant_v5_2": fr if (red or fv is None) else fv,
                        "plugin_hs_cal": fac["plugin_hs"].get(f"{T}|{wk}")}
            if "tolerant_v5_2_fredB" in methods:
                raw["tolerant_v5_2_fredB"] = v52
                sec["tolerant_v5_2_fredB"] = sec["tolerant_v5_2"]
                fac_used["tolerant_v5_2_fredB"] = fac["red_B"].get(f"{T}|{wk}") if (red or fv is None) else fv
            base = {"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T, "kind": kind, "rate": rate,
                    "k": skel.damage.get("k", 0), "lag_max": lag, "scenario": sc["name"], "shock": shock,
                    "n_nonnull_truth": int(nonnull.sum()),
                    **{k: v52.info.get(k) for k in HS_KEYS}, **gs,
                    "v52_status": v52.status, "v51_status": v51.status if v51 is not None else None,
                    "raw_ident_v51": bool(v51 is not None and same_raw(v52, v51))}
            for name in methods:
                res = run_r5._scale(raw[name], fac_used[name], name)
                row = evaluate(sem_s, res, H, tau_effect=tau)
                row.update(base)
                row.update({"fac": fac_used[name], "sec": sec[name]})
                rows.append(row)
                if name in METHOD_IDX and res.status == "ok":
                    dC = delta_C(sem, full, H)
                    k = len(jj)
                    vals = {"topo": [t_idx] * k, "rep": [rep] * k, "T": [T] * k, "cell": [c_idx] * k,
                            "method": [METHOD_IDX[name]] * k, "j": jj, "i": ii, "C_t": C_t[jj, ii],
                            "C_e": res.C[jj, ii], "lo": res.lo[jj, ii], "hi": res.hi[jj, ii], "dC": dC[jj, ii]}
                    for key in PCOLS:
                        pc[key].extend(np.asarray(vals[key]).tolist())
    return {"rows": rows, "pairs": pc}


def run_cal_unit(args):
    """Calibration unit (D-07H development): fit ONLY tolerant_v5_2, keep its reduced ok runs (as run_r5.calibrate)."""
    warnings.filterwarnings("ignore")
    cfg, topo, t_idx, rep = args
    gen = generator_config(cfg)
    H, lag, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + cfg.get("unit_offset", 0) + 500_000 + 1000 * t_idx + rep
    R = np.random.default_rng
    sem = build_dynamic_sem(topo, gen, R([unit, 0]))
    skels = unit_skeletons(sem, unit, dict(cfg, damage=LAYOUT))
    _, C_t, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_t) > cfg["tau_effect"])
    want = {(k, float(r)) for k, r in cfg["cells"]}
    tag51 = ext_seed("tolerant_v5_1")
    out = []
    for T in cfg["T"]:
        data = sem.simulate(T, R([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            if (kind, float(rate)) not in want:
                continue
            skel = public(full)
            res = tolerant_v5_2(data, skel, lag, H, n_boot, R([unit, 3, T, c_idx, tag51]))
            red = int(res.info.get("hs_reduced", 0))
            rec = {"T": T, "kind": kind, "k": skel.damage.get("k", 0), "status": res.status, "red": red,
                   "dist": None, "half": None}
            if res.status == "ok" and red:
                mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                rec["dist"], rec["half"] = np.abs(C_t - mid)[nonnull].tolist(), half[nonnull].tolist()
            out.append(rec)
    return out


def calibrate(cfg, workers, out):
    """f_red(T, kind) of tolerant_v5_2 with run_r5's rule and fallback chain (MIN_RED reduced runs at (T, kind);
    else pooled over kinds at T; else pooled over every calibration T and kind; else f_v51)."""
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep) for t_idx, topo in enumerate(topos) for rep in range(cfg["replicates"])]
    t0 = time.perf_counter()
    recs = []
    with ProcessPoolExecutor(workers) as pool:
        for o in pool.map(run_cal_unit, jobs):
            recs.extend(o)
    groups, status = {}, {}
    for r in recs:
        key = f"{r['T']}|{M.width_key({'kind': r['kind'], 'k': r['k']})}"
        st = status.setdefault(key, {})
        st[f"{r['status']}|red{r['red']}"] = st.get(f"{r['status']}|red{r['red']}", 0) + 1
        if r["dist"] is None:
            continue
        for g in (("red", key), ("red_T", str(r["T"])), ("red_all", "all")):
            gg = groups.setdefault(g, [[], [], 0])
            gg[0] += r["dist"]
            gg[1] += r["half"]
            gg[2] += 1
    counts = {f"{a}|{b}": g[2] for (a, b), g in groups.items()}
    fv, _ = run_r5.f_v51_table()
    red, srcs = {}, {}
    for T in cfg["fill_T"]:
        for wk in ("none", "extra", "missing", "reversed"):
            key = f"{T}|{wk}"
            if counts.get(f"red|{key}", 0) >= run_r5.MIN_RED:
                g, s = groups[("red", key)], "T,kind"
            elif counts.get(f"red_T|{T}", 0) >= run_r5.MIN_RED:
                g, s = groups[("red_T", str(T))], "T pooled over kinds"
            elif counts.get("red_all|all", 0) >= run_r5.MIN_RED:
                g, s = groups[("red_all", "all")], "pooled over every calibration T and kind"
            else:
                g, s = None, "f_v51 (no reduced calibration run)"
            if g is not None:
                red[key], srcs[key] = run_r5.factor(g[0], g[1]), s
            elif key in fv:
                red[key], srcs[key] = fv[key], s
    (out / "calibration.json").write_text(json.dumps({"red": red}, indent=1), encoding="utf-8")
    (out / "cal_counts.json").write_text(json.dumps({"counts": counts, "red_source": srcs, "status": status}, indent=1),
                                         encoding="utf-8")
    return {"seconds": round(time.perf_counter() - t0, 1), "n_records": len(recs), "n_units": len(jobs),
            "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topos]}


def guard(cfg):
    if any(f in cfg["bank"] for f in FORBIDDEN):
        raise SystemExit(f"forbidden bank {cfg['bank']}")
    if cfg["split"] != "development":
        raise SystemExit("only development splits")


def load_factors(cfg) -> dict:
    r4 = json.loads((ROOT / run_r5.R4_CAL).read_text(encoding="utf-8"))
    fv, fv_src = run_r5.f_v51_table()
    red = json.loads((ROOT / cfg["red_calibration"]).read_text(encoding="utf-8"))["red"]
    out = {"v51": fv, "red": red, "plugin_hs": r4["plugin_hs"], "v51_source": fv_src,
           "sha256": {run_r5.R4_CAL: sha(run_r5.R4_CAL), run_r5.FROZEN_V51: sha(run_r5.FROZEN_V51),
                      cfg["red_calibration"]: sha(cfg["red_calibration"])}}
    if cfg.get("red_calibration_B"):
        out["red_B"] = json.loads((ROOT / cfg["red_calibration_B"]).read_text(encoding="utf-8"))["red"]
        out["sha256"][cfg["red_calibration_B"]] = sha(cfg["red_calibration_B"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    guard(cfg)
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    if cfg.get("phase") == "calibration":
        info = calibrate(cfg, a.workers, out)
        man = {"config": cfg, **info, "workers": a.workers, "python": sys.executable, "numpy": np.__version__,
               "deps_sha256": {p: sha(p) for p in DEPS},
               "config_sha256": sha(Path(a.config).resolve().relative_to(ROOT))}
        (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
        print(f"calibration: {info['n_records']} records in {info['seconds']} s -> {out}")
        return
    fac = load_factors(cfg)
    (out / "factors_used.json").write_text(json.dumps(fac, indent=1), encoding="utf-8")
    topos = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, fac) for t_idx, topo in enumerate(topos) for rep in range(cfg["replicates"])]
    t0 = time.perf_counter()
    rows, pc = [], {k: [] for k in PCOLS}
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(run_unit, jobs):
            rows.extend(res["rows"])
            for k, v in res["pairs"].items():
                pc[k].extend(v)
    secs = round(time.perf_counter() - t0, 1)
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=float) + "\n")
    np.savez_compressed(out / "pairs.npz", methods=np.array(list(METHOD_IDX)),
                        **{k: np.asarray(v, dtype=float) for k, v in pc.items()})
    man = {"config": cfg, "seconds": secs, "n_units": len(jobs), "n_rows": len(rows), "workers": a.workers,
           "python": sys.executable, "numpy": np.__version__, "platform": platform.platform(),
           "deps_sha256": {p: sha(p) for p in DEPS}, "config_sha256": sha(Path(a.config).resolve().relative_to(ROOT)),
           "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topos]}
    (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"{len(rows)} rows, {len(jobs)} units in {secs} s -> {out}")


if __name__ == "__main__":
    main()
