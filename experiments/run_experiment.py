"""Run a damage x T x method grid and summarise it.

For every topology x replicate (a "unit"): draw one dynamic SEM (the truth). For every T:
simulate data. For every damage cell: fit every method on the same data and score it. Damaged
skeletons are drawn once per (unit, kind) with nested rates and reused across T, so comparisons
between cells and between methods are paired.

If the config lists the ``inflate`` method, a calibration phase first tunes its constant c per
(T, kind, rate) on the calibration bank, which must not overlap the evaluation topologies.

Optional config keys (plan section 9 and the A-group extensions):
- ``scenarios``: list of {"name", "latent", "latent_children", "meas_noise"}. Each scenario adds
  hidden common causes and/or measurement noise to the data of the main phase (generator.py).
  Calibration always uses clean data, so the frozen module meets these deviations unprepared.
- ``calibrate_methods``: extension methods whose interval is widened by a factor tuned per
  (T, stated damage kind) on the calibration bank, exactly as for ``tolerant_v4``.
- ``frozen_calibration``: path (from the repo root) of a JSON of width factors that override the
  re-tuned ones, e.g. experiments/calibration/tolerant_v4_frozen.json for the frozen module.
- ``learned``: {"algorithm": "ges"} adds a cell whose skeleton is learned by the GES of Paper 2 on
  an independent series of the same length (learned.py). Its stated damage is the mean error count
  of GES on the calibration bank at that T.

Run:  python experiments/run_experiment.py --config experiments/configs/<name>.json
Writes results/<name>/runs.jsonl, skeletons.jsonl, calibration.json, summary.md, manifest.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paper4 import methods as M  # noqa: E402
from paper4.generator import GeneratorConfig, add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, truth_effects  # noqa: E402
from paper4.skeleton import damage, true_skeleton  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

C_GRID = np.round(np.arange(1.0, 10.01, 0.1), 2)


def generator_config(cfg: dict) -> GeneratorConfig:
    return GeneratorConfig(**{k: tuple(v) if isinstance(v, list) else v for k, v in cfg["generator"].items()})


def cells(cfg: dict) -> list[tuple[str, float]]:
    learned = [("ges", 0.0)] if cfg.get("learned") else []
    return [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]] + learned


_EXT = None


def ext_methods() -> dict:
    """Methods registered by ``src/paper4/ext_*.py``. Each module defines
    ``METHODS = {name: fn}`` with ``fn(data, skel, lag_max, H, n_boot, rng) -> MethodResult``.
    A method sees only the data and the (possibly damaged) skeleton with its stated damage."""
    global _EXT
    if _EXT is None:
        import importlib
        import pkgutil
        import warnings

        import paper4
        _EXT = {}
        for mod in sorted(pkgutil.iter_modules(paper4.__path__), key=lambda m: m.name):
            if mod.name.startswith("ext_"):
                try:  # a broken extension must not stop runs that do not use it
                    _EXT.update(importlib.import_module(f"paper4.{mod.name}").METHODS)
                except Exception as exc:  # noqa: BLE001
                    warnings.warn(f"extension {mod.name} not loaded: {exc!r}")
    return _EXT


def ext_seed(name: str) -> int:
    """Bootstrap stream tag of an extension method: fixed by its name, so adding or removing other
    extension modules does not change its results (it used to be its position in the list)."""
    return 1000 + zlib.crc32(name.encode()) % 1_000_000


def public(skel):
    """The skeleton as the shared interface passes it on (plan section 7): pairs, orientation and
    stated damage. The private damage log and the oracle's lag hints are removed, so no method can
    read them even by accident."""
    pub = skel.copy()
    pub.log, pub.lag_hint = [], None
    return pub


def scenarios(cfg: dict) -> list[dict]:
    return cfg.get("scenarios") or [{"name": "clean"}]


def unit_skeletons(sem, unit_seed: int, cfg: dict) -> dict:
    truth = true_skeleton(sem)
    coef = {e: float(sem.B[lag, e[1], e[0]]) for e, lag in sem.edge_lag.items()}
    out = {}
    for k_idx, kind in enumerate(["none"] + cfg["damage"]["kinds"]):
        rates = [0.0] if kind == "none" else cfg["damage"]["rates"]
        for rate in rates:
            # same stream for every rate of a kind -> nested damage
            out[(kind, rate)] = damage(truth, kind, rate, np.random.default_rng([unit_seed, 1, k_idx]),
                                       sem.edge_lag, coef)
    return out


def run_unit(args) -> dict:
    cfg, topo, t_idx, rep, calib_c, phase = args
    calib_c = calib_c or {}
    gen = generator_config(cfg)
    H, lag_max, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    unit = cfg["seed_base"] + (500_000 if phase == "calibration" else 0) + 1000 * t_idx + rep
    sem = build_dynamic_sem(topo, gen, np.random.default_rng([unit, 0]))
    skels = unit_skeletons(sem, unit, cfg)
    oracle_skel = true_skeleton(sem, with_lags=True)
    if phase == "calibration":
        methods = (["plugin"] + (["tolerant_v3"] if "tolerant_v4" in cfg["methods"] else [])
                   + list(cfg.get("calibrate_methods", [])))
    else:
        methods = cfg["methods"]
    rows, pairs, skel_log = [], [], []
    # Latent nodes have no observed parents, so the truth of observed pairs is the same in every scenario.
    _, C_true, _, _ = truth_effects(sem, H)
    nonnull = ~np.eye(sem.n, dtype=bool) & (np.abs(C_true) > cfg["tau_effect"])

    for (kind, rate), skel in skels.items():
        skel_log.append({"topology": topo.id, "replicate": rep, "kind": kind, "rate": rate,
                         "damage": skel.damage, "log": skel.log})
    for sc in (scenarios(cfg) if phase == "main" else [{"name": "clean"}]):
        # same latent stream in every scenario -> latent nodes are nested across scenarios
        sem_s = add_latent(sem, sc.get("latent", 0), np.random.default_rng([unit, 5]),
                           n_children=sc.get("latent_children", 3))
        if sem_s is not sem:
            skel_log.append({"topology": topo.id, "replicate": rep, "scenario": sc["name"],
                             "latent_edges": sem_s.meta["latent_edges"]})
        _run_scenario(cfg, sc, sem, sem_s, skels, oracle_skel, methods, calib_c, phase, unit, topo, rep,
                      C_true, nonnull, rows, pairs, skel_log)
    return {"rows": rows, "pairs": pairs, "skeletons": skel_log}


def _learned_cell(cfg, sem_s, sc, T, unit, calib_c, phase):
    """GES skeleton learned on an independent series (plan 5.2: no double dipping), with its true
    error counts in the private log and the calibration-bank mean counts as the stated damage."""
    from paper4.learned import damage_counts, ges_skeleton
    learn = sem_s.simulate(T, np.random.default_rng([unit, 4, T]))
    learn = add_measurement_noise(learn, sc.get("meas_noise", 0.0), np.random.default_rng([unit, 7, T]))
    g = ges_skeleton(learn)
    counts = damage_counts(g, true_skeleton(sem_s))
    g.damage = dict(calib_c.get("ges_damage", {}).get(str(T), {})) if phase == "main" else {}
    g.log = [counts]
    return g, counts


def _run_scenario(cfg, sc, sem, sem_s, skels, oracle_skel, methods, calib_c, phase, unit, topo, rep,
                  C_true, nonnull, rows, pairs, skel_log):
    gen = sem.config
    H, lag_max, n_boot = cfg["H"], gen.lag_max, cfg["n_boot"]
    for T in cfg["T"]:
        data = sem_s.simulate(T, np.random.default_rng([unit, 2, T]))
        data = add_measurement_noise(data, sc.get("meas_noise", 0.0), np.random.default_rng([unit, 6, T]))
        cells_T = dict(skels)
        if cfg.get("learned"):
            g, counts = _learned_cell(cfg, sem_s, sc, T, unit, calib_c, phase)
            cells_T[("ges", 0.0)] = g
            if phase == "calibration":
                pairs.append({"cell": f"ges_damage|{T}", "counts": counts})
            else:
                skel_log.append({"topology": topo.id, "replicate": rep, "scenario": sc["name"], "T": T,
                                 "kind": "ges", "damage": g.damage, "log": g.log})
        oracle_res = None
        for c_idx, ((kind, rate), full) in enumerate(cells_T.items()):
            rng = lambda tag: np.random.default_rng([unit, 3, T, c_idx, tag])  # noqa: E731
            skel = public(full)   # what every method may see; ``full`` keeps the private log for scoring
            results = {}
            if "plugin" in methods or "inflate" in methods:
                results["plugin"] = M.plugin(data, skel, lag_max, H, n_boot, rng(1))
            if "inflate" in methods:
                results["inflate"] = M.inflate(results["plugin"], calib_c.get(f"{T}|{kind}|{rate}"))
            if "oracle" in methods:
                if oracle_res is None:  # the oracle ignores the skeleton: fit once per T
                    oracle_res = M.oracle(data, oracle_skel, lag_max, H, n_boot, rng(2))
                results["oracle"] = oracle_res
            if "lp_allpast" in methods:
                results["lp_allpast"] = M.lp_allpast(data, skel, lag_max, H)
            if "bagging" in methods:
                results["bagging"] = M.bagging(data, skel, lag_max, H, n_boot, rng(3))
            if "soft" in methods:
                results["soft"] = M.soft(data, skel, lag_max, H, n_boot, rng(4))
            if "tolerant" in methods:
                results["tolerant"] = M.tolerant(data, skel, lag_max, H, n_boot, rng(5))
            if "tolerant_v3" in methods or "tolerant_v3_cal" in methods:
                results["tolerant_v3"] = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
            if "tolerant_v4" in methods:
                if "tolerant_v3" not in results:
                    results["tolerant_v3"] = M.tolerant_v3(data, skel, lag_max, H, n_boot, rng(6))
                results["tolerant_v4"] = M.calibrate_width(
                    results["tolerant_v3"], calib_c.get(f"mod|{T}|{M.width_key(skel.damage)}"), "tolerant_v4")
            if "tolerant_v3_cal" in methods:
                results["tolerant_v3_cal"] = M.calibrate_width(results["tolerant_v3"], calib_c.get(f"{T}|none|0.0"),
                                                               "tolerant_v3_cal")
            if "ida_union" in methods:
                results["ida_union"] = M.ida_union(data, skel, lag_max, H, n_boot, rng(7))
            if "bvar_minnesota" in methods:
                results["bvar_minnesota"] = M.bvar_minnesota(data, skel, lag_max, H, n_boot, rng(8))
            if "pselect_union" in methods:
                results["pselect_union"] = M.pselect_union(data, skel, lag_max, H, n_boot, rng(9))
            if "tolerant_auto" in methods:
                results["tolerant_auto"] = _tolerant_auto(data, skel, sem_s, lag_max, H, n_boot, rng(10), calib_c, T)
            ext = ext_methods()
            for name in sorted(ext):
                if name in methods:
                    raw = ext[name](data, skel, lag_max, H, n_boot, rng(ext_seed(name)))
                    if name in cfg.get("calibrate_methods", []) and phase == "main":
                        raw = M.calibrate_width(raw, calib_c.get(f"{name}|{T}|{M.width_key(skel.damage)}"), name)
                    results[name] = raw
            missing = [m for m in methods if m not in results]
            if missing:
                raise KeyError(f"unknown method(s) {missing}: not built in and not registered by an ext_* module")
            for name in methods:
                res = results[name]
                row = evaluate(sem_s, res, H, tau_effect=cfg["tau_effect"])
                row.update({"topology": topo.id, "profile": topo.profile, "replicate": rep, "T": T,
                            "kind": kind, "rate": rate, "k": skel.damage.get("k", 0), "scenario": sc["name"]})
                if kind == "ges":
                    row.update({f"true_{key}": v for key, v in full.log[0].items()})
                rows.append(row)
            if phase == "main" and cfg.get("misstated"):
                rows.extend(misstated_rows(cfg, sem_s, data, skel, kind, rate, results, calib_c, T, H, lag_max,
                                           n_boot, rng, topo, rep))
            if phase == "calibration":
                cal_cells = [("plugin", f"{T}|{kind}|{rate}")]
                if "tolerant_v3" in methods and kind in ("none", "extra", "missing", "reversed"):
                    # module width factor per (T, stated kind), pooled over rates: the module knows the stated kind
                    cal_cells.append(("tolerant_v3", f"mod|{T}|{M.width_key(skel.damage)}"))
                if kind in ("none", "extra", "missing", "reversed"):
                    for name in cfg.get("calibrate_methods", []):
                        cal_cells.append((name, f"{name}|{T}|{M.width_key(skel.damage)}"))
                for name, cell in cal_cells:
                    res = results[name]
                    if res.status == "ok":
                        mid, half = (res.lo + res.hi) / 2, (res.hi - res.lo) / 2
                        pairs.append({"cell": cell, "dist": (np.abs(C_true - mid)[nonnull]).tolist(),
                                      "half": half[nonnull].tolist()})


def _tolerant_auto(data, skel, sem_s, lag_max, H, n_boot, rng, calib_c, T):
    """B1: module v4 with the damage estimated from the data (diagnose.py) instead of declared."""
    from paper4.diagnose import estimate_damage
    from paper4.learned import damage_counts
    est = estimate_damage(data, skel, lag_max)
    if est is None:
        return M._failed("tolerant_auto", "undiagnosable")
    s = skel.copy()
    s.damage = est
    res = M.tolerant(data, s, lag_max, H, n_boot, rng, target_reversal=True, name="tolerant_auto")
    res = M.calibrate_width(res, calib_c.get(f"mod|{T}|{M.width_key(est)}"), "tolerant_auto")
    true = damage_counts(skel, true_skeleton(sem_s))
    res.info.update({**{f"est_{k}": est[k] for k in true}, **{f"true_{k}": v for k, v in true.items()}})
    return res


def misstated_rows(cfg, sem, data, skel, kind, rate, results, calib_c, T, H, lag_max, n_boot, rng, topo, rep):
    """Refit the damage-reading methods with a wrong stated damage.

    Damaged cells: stated k = floor(true k * factor + 0.5) for each factor (0 = damage not
    declared). Undamaged cell: false alarms, i.e. a stated damage kind and k on a correct skeleton.
    Rows are named ``<method>@x<factor>`` or ``<method>@alarm-<kind><k>``."""
    ms = cfg["misstated"]
    variants = []
    if kind == "none":
        for f_kind, f_k in ms.get("false_alarm", []):
            variants.append((f"alarm-{f_kind}{f_k}", {"kind": f_kind, "rate": None, "k": int(f_k)}))
    else:
        for f in ms.get("factors", []):
            variants.append((f"x{f}", {**skel.damage, "k": int(np.floor(skel.damage["k"] * f + 0.5))}))
    out = []
    for v_idx, (tag, stated) in enumerate(variants):
        s = skel.copy()
        s.damage = stated
        res = M.tolerant_v3(data, s, lag_max, H, n_boot, rng(100 + v_idx))
        for name in ms["methods"]:
            r = res if name == "tolerant_v3" else M.calibrate_width(res, calib_c.get(f"{T}|none|0.0"), name)
            row = evaluate(sem, r, H, tau_effect=cfg["tau_effect"])
            row.update({"method": f"{name}@{tag}", "topology": topo.id, "profile": topo.profile, "replicate": rep,
                        "T": T, "kind": kind, "rate": rate, "k": skel.damage.get("k", 0), "k_stated": stated["k"]})
            out.append(row)
    return out


def calibrate(cfg: dict, workers: int) -> dict:
    cal = cfg["calibration"]
    topologies = load_bank(cal["bank"], cal["split"])[: cal.get("max_topologies") or None]
    ccfg = dict(cfg, replicates=cal["replicates"])
    if "kinds" in cal:  # calibrate on other damage kinds than the evaluation uses
        ccfg["damage"] = {"kinds": cal["kinds"], "rates": cal.get("rates", cfg["damage"]["rates"])}
    jobs = [(ccfg, topo, t_idx, rep, None, "calibration")
            for t_idx, topo in enumerate(topologies) for rep in range(cal["replicates"])]
    by_cell = defaultdict(lambda: ([], []))
    ges_counts = defaultdict(list)
    with ProcessPoolExecutor(workers) as pool:
        for out in pool.map(run_unit, jobs):
            for p in out["pairs"]:
                if "counts" in p:
                    ges_counts[p["cell"].split("|")[1]].append(p["counts"])
                    continue
                by_cell[p["cell"]][0].extend(p["dist"])
                by_cell[p["cell"]][1].extend(p["half"])
    result = {}
    if ges_counts:  # stated damage of the learned cell: mean GES error counts on the calibration bank
        result["ges_damage"] = {T: {key: int(np.floor(np.mean([c[key] for c in cs]) + 0.5))
                                    for key in ("missing", "extra", "reversed")} for T, cs in ges_counts.items()}
    for cell, (dist, half) in by_cell.items():
        dist, half = np.array(dist), np.array(half)
        cov = np.array([(dist <= c * half).mean() for c in C_GRID])
        target = min(1 - M.ALPHA, cov.max() - 0.005)  # lost pairs cap what any c can reach
        result[cell] = float(C_GRID[np.argmax(cov >= target)])
    return result


def summarize(rows: list[dict], cfg: dict) -> str:
    groups = defaultdict(list)
    sc_order = {sc["name"]: i for i, sc in enumerate(scenarios(cfg))}
    for r in rows:
        groups[(r.get("scenario", "clean"), r["T"], r["kind"], r["rate"], r["method"])].append(r)
    base_order = {m: i for i, m in enumerate(cfg["methods"])}
    order = defaultdict(lambda: len(base_order))
    for r in rows:
        m = r["method"]
        order[m] = base_order.get(m, len(base_order) + base_order.get(m.split("@")[0], 0) * 100 + len(m))
    kind_order = {k: i for i, k in enumerate(["none"] + cfg["damage"]["kinds"] + ["ges"])}
    keys = sorted(groups, key=lambda g: (sc_order.get(g[0], 0), g[1], kind_order[g[2]], g[3], order[g[4]]))

    def pooled(g, num, den):
        d = sum(r.get(den, 0) for r in g)
        return sum(r.get(num, 0) for r in g) / d if d else float("nan")

    def med(g, key):
        v = [r[key] for r in g if r.get(key) is not None]
        return float(np.median(v)) if v else float("nan")

    def mean(g, key):
        v = [r[key] for r in g if r.get(key) is not None]
        return float(np.mean(v)) if v else float("nan")

    lines = [
        f"# {cfg['name']}", "", cfg["purpose"], "",
        f"Bank {cfg['bank']} / {cfg['split']}; {cfg['replicates']} replicates per topology; H = {cfg['H']}, "
        f"lag_max = {cfg['generator']['lag_max']}, n_boot = {cfg['n_boot']}, nominal coverage 0.95.",
        "",
        "- `cov` pools non-null pairs over runs; lost pairs (estimate exactly 0) count as uncovered. `cov kept` excludes them.",
        "- `IS` is the mean interval score of non-null pairs (Gneiting-Raftery, lower is better).",
        "- `width` is the median interval width over kept non-null pairs; `lost` the share of non-null pairs with estimate 0.",
        "",
        "| scenario | T | damage | rate | method | ok | cov | cov kept | width | IS | abs err | lost | lag err |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key in keys:
        g = groups[key]
        ok = [r for r in g if r["status"] == "ok"]
        sc, T, kind, rate, m = key
        lines.append(
            f"| {sc} | {T} | {kind} | {rate:.1f} | {m} | {len(ok)}/{len(g)} | {pooled(ok, 'n_covered_nonnull', 'n_nonnull'):.3f} | "
            f"{pooled(ok, 'n_covered_kept', 'n_kept'):.3f} | {med(ok, 'width_kept'):.3f} | {mean(ok, 'iscore_nonnull_mean'):.2f} | "
            f"{med(ok, 'C_abs_err_nonnull'):.3f} | {pooled(ok, 'n_lost', 'n_nonnull'):.3f} | {med(ok, 'mean_lag_abs_err'):.3f} |")
    for ref in cfg.get("paired_references", ["plugin"]):
        lines += ["", paired_table(rows, cfg, reference=ref)]
    return "\n".join(lines) + "\n"


def paired_table(rows: list[dict], cfg: dict, reference: str = "plugin", n_resample: int = 1000) -> str:
    """Mean paired difference in interval score (method minus reference) per (T, cell), with a
    95% bootstrap interval that resamples topologies (runs of one topology are dependent)."""
    if reference not in cfg["methods"]:
        return ""
    index = {(r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"], r["method"]): r
             for r in rows if r["status"] == "ok" and r.get("iscore_nonnull_mean") is not None}
    rng = np.random.default_rng(0)
    lines = [f"## Interval score difference vs `{reference}` (negative = better), 95% CI clustered by topology", "",
             "| scenario | T | damage | rate | " + " | ".join(m for m in cfg["methods"] if m != reference) + " |",
             "|---|---|---|---|" + "---|" * (len(cfg["methods"]) - 1)]
    for sc, T, (kind, rate) in [(sc["name"], T, c) for sc in scenarios(cfg) for T in cfg["T"] for c in cells(cfg)]:
        cells_out = []
        for m in cfg["methods"]:
            if m == reference:
                continue
            diffs = defaultdict(list)
            for (s_, topo, rep, t, k, r, meth), row in index.items():
                if s_ == sc and meth == m and t == T and k == kind and r == rate:
                    ref = index.get((s_, topo, rep, t, k, r, reference))
                    if ref:
                        diffs[topo].append(row["iscore_nonnull_mean"] - ref["iscore_nonnull_mean"])
            if not diffs:
                cells_out.append("–")
                continue
            topos = list(diffs)
            est = np.mean([v for t_ in topos for v in diffs[t_]])
            boots = []
            for _ in range(n_resample):
                pick = rng.choice(len(topos), len(topos))
                boots.append(np.mean([v for i in pick for v in diffs[topos[i]]]))
            lo, hi = np.quantile(boots, (0.025, 0.975))
            cells_out.append(f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}]")
        lines.append(f"| {sc} | {T} | {kind} | {rate:.1f} | " + " | ".join(cells_out) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out = ROOT / "results" / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()

    calib_c = {}
    if {"inflate", "tolerant_v3_cal", "tolerant_v4"} & set(cfg["methods"]) or cfg.get("calibrate_methods"):
        calib_c = calibrate(cfg, args.workers)
    if cfg.get("frozen_calibration"):
        # Width factors of a frozen method (e.g. tolerant_v4's "mod|T|kind") are read from a fixed file
        # instead of being re-tuned in every run, which made "frozen v4" drift between configs.
        frozen = json.loads((ROOT / cfg["frozen_calibration"]).read_text(encoding="utf-8"))
        calib_c.update({k: v for k, v in frozen.items() if not k.startswith("_")})
    if calib_c:
        (out / "calibration.json").write_text(json.dumps(calib_c, indent=2), encoding="utf-8")

    topologies = load_bank(cfg["bank"], cfg["split"])[: cfg.get("max_topologies") or None]
    jobs = [(cfg, topo, t_idx, rep, calib_c, "main")
            for t_idx, topo in enumerate(topologies) for rep in range(cfg["replicates"])]
    rows, skels = [], []
    with ProcessPoolExecutor(args.workers) as pool:
        for res in pool.map(run_unit, jobs):
            rows.extend(res["rows"])
            skels.extend(res["skeletons"])

    with open(out / "runs.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(out / "skeletons.jsonl", "w", encoding="utf-8") as fh:
        for s in skels:
            fh.write(json.dumps(s) + "\n")
    (out / "summary.md").write_text(summarize(rows, cfg), encoding="utf-8")
    manifest = {"config": cfg, "seconds": round(time.perf_counter() - start, 1), "n_rows": len(rows),
                "topologies": [{"id": t.id, "profile": t.profile, "sha256": t.sha256} for t in topologies]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(rows)} rows in {manifest['seconds']} s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
