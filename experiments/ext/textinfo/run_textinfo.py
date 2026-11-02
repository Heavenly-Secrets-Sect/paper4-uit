"""Driver for the text-informed module (direction "textinfo").

Simulated topologies carry no text, so the side information is SYNTHETIC with controlled quality:

- one N(0, 1) noise value per node pair, drawn once per (unit, damage kind) and shared by every
  quality level and every rate (common random numbers, so comparisons across quality are paired);
- a damaged pair (from the PRIVATE damage log: missing pairs for ``suspicion``, extra or reversed
  pairs for ``doubt``) gets its noise shifted by delta(a) = sqrt(2) * Phi^-1(a), so the AUROC of the
  score against the true damage is exactly a in expectation (binormal model, equal variances);
- sign hints on skeleton pairs: the true coefficient sign of a true edge, flipped with probability
  ``sign_error``; a random sign on an extra (null) pair.

The side information is generated OUTSIDE the method from the private log and attached to the
damaged skeleton under ``skel.damage["text"]``. The method never sees the log or the truth.

Everything else follows experiments/run_experiment.py (imported, not modified): the same unit seeds,
dynamic SEMs, damaged skeletons (nested rates), data streams and evaluation. ``tolerant_v4`` is
reproduced exactly as the runner builds it (tolerant_v3 widened by its own factor per (T, stated
kind), tuned on the calibration bank with the runner's grid and target). The text methods listed in
``calibrate_methods`` get their own factor per (T, stated kind), tuned the same way on the
calibration bank, pooled over damage rates AND over the quality levels, so that the factor carries
no information about the quality of the text.

Run:
  python experiments/ext/textinfo/run_textinfo.py --config experiments/configs/ext_textinfo_<x>.json \
      --phase calibration --workers 3
  python experiments/ext/textinfo/run_textinfo.py --config experiments/configs/ext_textinfo_<x>.json \
      --phase main --calibration results/ext_textinfo_<cal>/calibration.json --workers 3
"""
from __future__ import annotations

import argparse
import json
import math
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

from run_experiment import C_GRID, generator_config, paired_table, unit_skeletons  # noqa: E402

from paper4 import methods as M  # noqa: E402
from paper4.ext_textinfo import METHODS as TEXT_METHODS, _norm_ppf, pair_key  # noqa: E402
from paper4.generator import build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

MAX_WORKERS = 3
# One random stream for every text method and quality level (common random numbers), and it is the
# stream the runner gives tolerant_v3 (tag 6). Hence a variant whose text or opening plays no role in
# a cell gives exactly the same result as another one (the driver copies it, see ``_reuse_key``), and
# on cells with nothing stated missing or reversed every text method equals tolerant_v3 draw for
# draw, so its calibrated factor and its result equal tolerant_v4's.
METHOD_TAG = 6


def delta_for(a: float) -> float:
    return math.sqrt(2) * _norm_ppf(a) if a != 0.5 else 0.0


def synthetic_text(skel, kind: str, sem, a: float, noise: np.ndarray, sign_u: np.ndarray,
                   sign_null: np.ndarray, sign_error: float) -> dict:
    """Side information of quality a for one damaged skeleton (see module doc)."""
    n = skel.n
    idx = {(u, v): t for t, (u, v) in enumerate((u, v) for u in range(n) for v in range(u + 1, n))}
    damaged = {tuple(sorted(e["pair"])) for e in skel.log}
    d = delta_for(a)
    doubt, suspicion, sign = {}, {}, {}
    true_coef = {}
    for (i, j), lag in sem.edge_lag.items():
        true_coef[tuple(sorted((i, j)))] = float(sem.B[lag, j, i])
    for (u, v), t in idx.items():
        key = pair_key(u, v)
        if skel.is_adjacent(u, v):
            pos = kind in ("extra", "reversed") and (u, v) in damaged
            doubt[key] = float(noise[t] + (d if pos else 0.0))
            s = np.sign(true_coef[(u, v)]) if (u, v) in true_coef else sign_null[t]
            if sign_u[t] < sign_error:
                s = -s
            sign[key] = int(s)
        else:
            pos = kind == "missing" and (u, v) in damaged
            suspicion[key] = float(noise[t] + (d if pos else 0.0))
    return {"doubt": doubt, "suspicion": suspicion, "sign": sign, "quality": a}


def auroc(scores: dict, positives: set) -> float | None:
    pos = [s for k, s in scores.items() if k in positives]
    neg = [s for k, s in scores.items() if k not in positives]
    if not pos or not neg:
        return None
    return float(np.mean([(p > q) + 0.5 * (p == q) for p in pos for q in neg]))


def _reuse_key(name: str, a, stated: dict) -> tuple:
    """Two (method, quality) runs with the same key are identical given the shared random stream.
    - nothing stated missing or reversed: every variant is v3 on the skeleton's own terms;
    - nothing stated missing: the opening plays no role, so textinfo_all = textinfo (same a);
    - nothing stated reversed and nothing missing: text plays no role at all."""
    if name == "textinfo_sign":
        return (name, a)
    uses_text = name != "textinfo_null" and a is not None
    if stated["missing"] == 0 and stated["reversed"] == 0:
        return ("plain",)
    if stated["missing"] == 0:
        return ("rev", a if uses_text else None)
    return (name, a if uses_text else None)


def calib_factor(calib: dict, name: str, T: int, damage: dict):
    c = calib.get(f"{name}|{T}|{M.width_key(damage)}")
    if c is None and name == "textinfo_sign":  # pruning acts on textinfo's own draws: textinfo's factor
        c = calib.get(f"textinfo|{T}|{M.width_key(damage)}")
    return c


def run_unit(args) -> dict:
    warnings.filterwarnings("ignore", category=RuntimeWarning)  # overflow in explosive bootstrap draws (v3 too)
    cfg, topo, t_idx, rep, calib, phase = args
    gen = generator_config(cfg)
    H, lag_max, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])
    n_pairs = sem.n * (sem.n - 1) // 2
    kinds = ["none"] + cfg["damage"]["kinds"]
    noise = {k: np.random.default_rng([unit, 77, k_idx]).normal(size=n_pairs) for k_idx, k in enumerate(kinds)}
    srng = np.random.default_rng([unit, 78])
    sign_u, sign_null = srng.random(n_pairs), srng.choice((-1.0, 1.0), size=n_pairs)
    qualities = cfg["qualities"]
    text_methods = [m for m in cfg["methods"] if m in TEXT_METHODS]
    quality_methods = set(cfg.get("quality_methods", []))
    rows, pairs, auc_rows = [], [], []

    for T in cfg["T"]:
        data = sem.simulate(T, np.random.default_rng([unit, 2, T]))
        for c_idx, ((kind, rate), skel) in enumerate(skels.items()):
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            results = {}
            if "plugin" in cfg["methods"] and phase == "main":
                results["plugin"] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
            if "tolerant_v4" in cfg["methods"]:
                v3 = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                if phase == "calibration":
                    results["tolerant_v3"] = v3
                else:
                    results["tolerant_v4"] = M.calibrate_width(
                        v3, calib.get(f"mod|{T}|{M.width_key(skel.damage)}"), "tolerant_v4")
            cache = {}
            stated = M.stated_counts(skel.damage)
            for name in text_methods:
                variants = qualities if name in quality_methods else [None]
                for a in variants:
                    label = name if a is None else f"{name}@a{a}"
                    rkey = _reuse_key(name, a, stated)
                    s = skel.copy()
                    s.damage = dict(skel.damage)
                    if a is not None:
                        s.damage["text"] = synthetic_text(skel, kind, sem, a, noise[kind], sign_u, sign_null,
                                                          cfg["sign_error"])
                        if T == cfg["T"][0]:
                            dmg = {pair_key(*sorted(e["pair"])) for e in skel.log}
                            auc_rows.append({"kind": kind, "rate": rate, "a": a,
                                             "auc_doubt": auroc(s.damage["text"]["doubt"], dmg),
                                             "auc_suspicion": auroc(s.damage["text"]["suspicion"], dmg)})
                    if rkey in cache:
                        raw = cache[rkey]
                    else:
                        raw = cache[rkey] = TEXT_METHODS[name](data, s, lag_max, H, n_boot, rng(METHOD_TAG))
                    if phase == "main":
                        raw = M.calibrate_width(raw, calib_factor(calib, name, T, skel.damage), label)
                    results[label] = (name, raw)
            for label, res in results.items():
                base_name, res = res if isinstance(res, tuple) else (label, res)
                if phase == "calibration":
                    if kind not in ("none", "extra", "missing", "reversed") or res.status != "ok":
                        continue
                    key = "mod" if base_name == "tolerant_v3" else base_name
                    mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                    pairs.append({"cell": f"{key}|{T}|{M.width_key(skel.damage)}",
                                  "dist": (np.abs(C_true - mid)[nonnull]).tolist(),
                                  "half": half[nonnull].tolist()})
                    continue
                row = evaluate(sem, res, H, tau_effect=cfg["tau_effect"])
                row.update({"method": label, "topology": topo.id, "profile": topo.profile, "replicate": rep,
                            "T": T, "kind": kind, "rate": rate, "k": skel.damage.get("k", 0), "scenario": "clean"})
                rows.append(row)
    return {"rows": rows, "pairs": pairs, "auc": auc_rows}


def calibrate(cfg: dict, workers: int) -> dict:
    cal = cfg["calibration"]
    topologies = load_bank(cal["bank"], cal["split"])[: cal.get("max_topologies") or None]
    ccfg = dict(cfg, replicates=cal["replicates"])
    jobs = [(ccfg, topo, t_idx, rep, {}, "calibration")
            for t_idx, topo in enumerate(topologies) for rep in range(cal["replicates"])]
    by_cell = defaultdict(lambda: ([], []))
    with ProcessPoolExecutor(workers) as pool:
        for out in pool.map(run_unit, jobs):
            for p in out["pairs"]:
                by_cell[p["cell"]][0].extend(p["dist"])
                by_cell[p["cell"]][1].extend(p["half"])
    result = {}
    for cell, (dist, half) in sorted(by_cell.items()):
        dist, half = np.array(dist), np.array(half)
        cov = np.array([(dist <= c * half).mean() for c in C_GRID])
        target = min(1 - M.ALPHA, cov.max() - 0.005)  # as the runner
        result[cell] = float(C_GRID[np.argmax(cov >= target)])
    return result


def summarize(rows: list[dict], cfg: dict, labels: list[str], auc_rows: list[dict]) -> str:
    groups = defaultdict(list)
    for r in rows:
        groups[(r["T"], r["kind"], r["rate"], r["method"])].append(r)
    kind_order = {k: i for i, k in enumerate(["none"] + cfg["damage"]["kinds"])}
    order = {m: i for i, m in enumerate(labels)}
    keys = sorted(groups, key=lambda g: (g[0], kind_order[g[1]], g[2], order.get(g[3], 99)))

    def pooled(g, num, den):
        d = sum(r.get(den, 0) for r in g)
        return sum(r.get(num, 0) for r in g) / d if d else float("nan")

    def mean(g, key):
        v = [r[key] for r in g if r.get(key) is not None]
        return float(np.mean(v)) if v else float("nan")

    def med(g, key):
        v = [r[key] for r in g if r.get(key) is not None]
        return float(np.median(v)) if v else float("nan")

    lines = [f"# {cfg['name']}", "", cfg["purpose"], "",
             f"Bank {cfg['bank']} / {cfg['split']}; {cfg['replicates']} replicates per topology; H = {cfg['H']}, "
             f"lag_max = {cfg['generator']['lag_max']}, n_boot = {cfg['n_boot']}; seed_base {cfg['seed_base']}; "
             f"text qualities (AUROC) {cfg['qualities']}, sign error {cfg['sign_error']}.", "",
             "`textinfo@aX` = text-informed module fed synthetic side information of AUROC X. "
             "`textinfo_null` = same machinery, text ignored. `n_open` = mean opened off-skeleton lag blocks.", "",
             "| T | damage | rate | method | ok | cov | width | IS | lost | n_open |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for key in keys:
        g = groups[key]
        ok = [r for r in g if r["status"] == "ok"]
        T, kind, rate, m = key
        lines.append(f"| {T} | {kind} | {rate:.1f} | {m} | {len(ok)}/{len(g)} | "
                     f"{pooled(ok, 'n_covered_nonnull', 'n_nonnull'):.3f} | {med(ok, 'width_kept'):.3f} | "
                     f"{mean(ok, 'iscore_nonnull_mean'):.3f} | {pooled(ok, 'n_lost', 'n_nonnull'):.3f} | "
                     f"{mean(ok, 'info_n_open'):.1f} |")
    tcfg = dict(cfg, methods=labels)
    for ref in ("tolerant_v4", "textinfo_null"):
        if ref in labels:
            lines += ["", paired_table(rows, tcfg, reference=ref)]
    if auc_rows:
        lines += ["", "## Realised AUROC of the synthetic side information (first T, all units)", "",
                  "| damage | rate | a | AUROC doubt | AUROC suspicion |", "|---|---|---|---|---|"]
        g2 = defaultdict(list)
        for r in auc_rows:
            g2[(r["kind"], r["rate"], r["a"])].append(r)
        for (kind, rate, a), g in sorted(g2.items(), key=lambda x: (kind_order[x[0][0]], x[0][1], x[0][2])):
            lines.append(f"| {kind} | {rate:.1f} | {a} | {mean(g, 'auc_doubt'):.3f} | {mean(g, 'auc_suspicion'):.3f} |")
    return "\n".join(lines) + "\n"


def method_labels(cfg: dict) -> list[str]:
    out = []
    for m in cfg["methods"]:
        if m in cfg.get("quality_methods", []):
            out += [f"{m}@a{a}" for a in cfg["qualities"]]
        else:
            out.append(m)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True)
    parser.add_argument("--phase", choices=("calibration", "main"), required=True)
    parser.add_argument("--calibration", help="calibration.json for the main phase")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    args = parser.parse_args(argv)
    workers = min(args.workers, MAX_WORKERS)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    assert cfg["name"].startswith("ext_textinfo_")
    assert not (cfg["bank"] == "P4-H1" or cfg["split"] != "development"), "development splits only"
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    if args.phase == "calibration":
        calib = calibrate(cfg, workers)
        (out / "calibration.json").write_text(json.dumps(calib, indent=2), encoding="utf-8")
        print(f"calibration in {time.perf_counter() - start:.1f} s -> {out}")
        return 0
    calib = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib, "main")
            for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    rows, aucs = [], []
    with ProcessPoolExecutor(workers) as pool:
        for res in pool.map(run_unit, jobs):
            rows.extend(res["rows"])
            aucs.extend(res["auc"])
    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    labels = method_labels(cfg)
    (out / "summary.md").write_text(summarize(rows, cfg, labels, aucs), encoding="utf-8")
    manifest = {"config": cfg, "calibration_file": args.calibration, "calibration": calib,
                "seconds": round(time.perf_counter() - start, 1), "n_rows": len(rows),
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
