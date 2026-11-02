"""R2-3b: published baselines width-calibrated per T only (pooled over every calibration cell,
none included; the stated damage kind is never read), docs/ext/auto5.md section 2.

Phase "calibration": the runner's calibration units (D-07H development, seed_base + 500000 + 1000 *
topology + replicate, the config's calibration kinds/rates plus none). Phase "eval": D-07
development with the seeds of a2_baselines / a2b_pselect. Every baseline is fitted with exactly the
runner's bootstrap stream (rng([unit, 3, T, c_idx, tag]), tag plugin 1, ida_union 7,
bvar_minnesota 8, pselect_union 9), so its raw interval equals the stored a2 row; this is checked.

For every run and baseline the raw interval is kept as (|C_true - midpoint|, half width, lost) on the
non-null pairs; a factor c scales the interval about its midpoint, and coverage and interval score
are recomputed exactly as metrics.evaluate does. Factors per (baseline, T):
  _calT  : two-sided grid 0.5..5.0 step 0.05 (primary: the baseline may also narrow)
  _calT1 : one-sided grid 1.0..10.0 step 0.1 (as tolerant_auto3 and the runner)
target min(0.95, max coverage - 0.005) as in run_experiment.calibrate.

Run: python experiments/ext/auto5/fair_baselines.py --config experiments/configs/ext_auto5_fair.json --workers 3
Writes results/ext_auto5_fair/{calibration.json, runs.jsonl, pairing_check.json, manifest.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from run_experiment import generator_config, public, unit_skeletons  # noqa: E402
from paper4 import methods as M  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import interval_score, truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

TAGS = {"plugin": 1, "ida_union": 7, "bvar_minnesota": 8, "pselect_union": 9}
GRID2 = np.round(np.arange(0.5, 5.0001, 0.05), 2)
GRID1 = np.round(np.arange(1.0, 10.0001, 0.1), 2)


def factor(dist, half, grid) -> float:
    cov = np.array([(dist <= c * half).mean() for c in grid])
    target = min(1 - M.ALPHA, cov.max() - 0.005)
    return float(grid[np.argmax(cov >= target)])


def score(rec: dict, c: float) -> dict:
    d, h, lost = rec["dist"], rec["half"], rec["lost"]
    inside = d <= c * h
    iscore = 2 * c * h + (2 / M.ALPHA) * np.maximum(d - c * h, 0)
    kept = ~lost
    return {"n_nonnull": int(len(d)), "n_covered_nonnull": int(inside.sum()), "n_lost": int(lost.sum()),
            "n_kept": int(kept.sum()), "n_covered_kept": int(inside[kept].sum()),
            "iscore_nonnull_mean": float(iscore.mean()) if len(d) else None,
            "width_kept": float(np.median(2 * c * h[kept])) if kept.any() else None}


def unit_job(args):
    cfg, phase, t_idx, rep = args
    gen = generator_config(cfg)
    lag_max, H, n_boot = gen.lag_max, cfg["H"], cfg["n_boot"]
    if phase == "calibration":
        cal = cfg["calibration"]
        topo = load_bank(cal["bank"], cal["split"])[t_idx]
        ccfg = dict(cfg, damage={"kinds": cal["kinds"], "rates": cal["rates"]})
        unit = cfg["seed_base"] + 500_000 + 1000 * t_idx + rep
    else:
        topo = load_bank(cfg["bank"], cfg["split"])[t_idx]
        ccfg = cfg
        unit = cfg["seed_base"] + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, ccfg)
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    out = []
    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), full) in enumerate(skels.items()):
            skel = public(full)
            for m in cfg["methods"]:
                res = getattr(M, m)(data, skel, lag_max, H, n_boot, np.random.default_rng([unit, 3, T, c_idx, TAGS[m]]))
                rec = {"phase": phase, "method": m, "topology": topo.id, "profile": topo.profile, "replicate": rep,
                       "T": T, "kind": kind, "rate": rate, "status": res.status}
                if res.status == "ok":
                    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                    rec.update({"dist": np.abs(C_true - mid)[nonnull], "half": half[nonnull],
                                "lost": (res.C == 0.0)[nonnull],
                                "raw_is_exact": float(np.mean(interval_score(res.lo, res.hi, C_true)[nonnull]))})
                out.append(rec)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    assert cfg["calibration"]["bank"] == "D-07H" and cfg["calibration"]["split"] == "development"
    assert cfg["bank"] == "D-07" and cfg["split"] == "development"
    out_dir = ROOT / "results" / cfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    cal = cfg["calibration"]
    n_cal = len(load_bank(cal["bank"], cal["split"])[: cal.get("max_topologies") or None])
    n_ev = len(load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None])
    jobs = [(cfg, "calibration", t, r) for t in range(n_cal) for r in range(cal["replicates"])]
    with ProcessPoolExecutor(args.workers) as pool:
        cal_recs = [r for o in pool.map(unit_job, jobs) for r in o]
    pooled = defaultdict(lambda: ([], []))
    for r in cal_recs:
        if r["status"] == "ok":
            pooled[(r["method"], r["T"])][0].append(r["dist"])
            pooled[(r["method"], r["T"])][1].append(r["half"])
    table = {}
    for (m, T), (d, h) in sorted(pooled.items()):
        d, h = np.concatenate(d), np.concatenate(h)
        table[f"{m}_calT|{T}"] = factor(d, h, GRID2)
        table[f"{m}_calT1|{T}"] = factor(d, h, GRID1)
        table[f"_coverage_at_1|{m}|{T}"] = float((d <= h).mean())
    (out_dir / "calibration.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
    t_cal = time.perf_counter() - start
    print(f"calibration done in {t_cal:.1f} s", flush=True)

    jobs = [(cfg, "eval", t, r) for t in range(n_ev) for r in range(cfg["replicates"])]
    with ProcessPoolExecutor(args.workers) as pool:
        ev_recs = [r for o in pool.map(unit_job, jobs) for r in o]
    rows = []
    for r in ev_recs:
        base = {k: r[k] for k in ("method", "topology", "profile", "replicate", "T", "kind", "rate", "status")}
        if r["status"] != "ok":
            for suffix in ("_raw", "_calT", "_calT1"):
                rows.append({**base, "method": r["method"] + suffix})
            continue
        for suffix, c in (("_raw", 1.0), ("_calT", table[f"{r['method']}_calT|{r['T']}"]),
                          ("_calT1", table[f"{r['method']}_calT1|{r['T']}"])):
            rows.append({**base, "method": r["method"] + suffix, "c_T": c, **score(r, c)})
    with open(out_dir / "runs.jsonl", "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    # pairing check: raw interval score must equal the stored a2 rows
    stored = {}
    for name in ("a2_baselines", "a2b_pselect"):
        for line in open(ROOT / "results" / name / "runs.jsonl", encoding="utf-8"):
            s = json.loads(line)
            if s["method"] in TAGS and s["status"] == "ok":
                stored.setdefault((s["method"], s["topology"], s["replicate"], s["T"], s["kind"], s["rate"]),
                                  s["iscore_nonnull_mean"])
    check = defaultdict(lambda: [0, 0, 0.0])
    for row in rows:
        if row["method"].endswith("_raw") and row["status"] == "ok":
            m = row["method"][:-4]
            ref = stored.get((m, row["topology"], row["replicate"], row["T"], row["kind"], row["rate"]))
            if ref is not None:
                check[m][1] += 1
                diff = abs(ref - row["iscore_nonnull_mean"])
                check[m][2] = max(check[m][2], diff)
                check[m][0] += diff < 1e-6
    check = {m: {"identical": v[0], "compared": v[1], "max_abs_diff": v[2]} for m, v in check.items()}
    (out_dir / "pairing_check.json").write_text(json.dumps(check, indent=2), encoding="utf-8")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "seconds_calibration": round(t_cal, 1),
                "n_rows": len(rows), "n_calibration_runs": len(cal_recs)}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(check, indent=2))
    print(f"{len(rows)} rows in {manifest['seconds']} s -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
