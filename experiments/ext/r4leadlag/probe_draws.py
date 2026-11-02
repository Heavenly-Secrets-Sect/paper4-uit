"""Design probe 2 (D-07H development only): data-level vs draw-level labels of variants A and D.

10 D-07H development topologies x replicate 0 (calibration-stream unit seeds), scenarios clean / latent1 /
latent3, T 80 / 150, stated missing-0.5, n_boot 49, through worker.run_unit_ll (the runner's own unit loop).
Reports the mean number of pairs labelled on the data and per bootstrap draw, the share of draws with
any label, and the BH list length per draw.

Run: python experiments/ext/r4leadlag/probe_draws.py -> results/ext_r4leadlag_probe/probe_draws.{json,md}
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import worker as W  # noqa: E402
from paper4.topology import load_bank  # noqa: E402

OUT = W.ROOT / "results" / "ext_r4leadlag_probe"


def job(t_idx):
    cfg = json.loads((W.ROOT / "experiments" / "configs" / "ext_r4leadlag_eval_latent.json").read_text())
    cfg = dict(cfg, T=[80, 150], damage={"kinds": ["missing"], "rates": [0.5]}, n_boot=49,
               methods=["tolerant_v5_1_leadlag", "tolerant_v5_1_leadlag_skel"], calibrate_methods=[],
               scenarios=[{"name": "clean"}, {"name": "latent1", "latent": 1}, {"name": "latent3", "latent": 3}],
               seed_base=cfg["seed_base"] + 500_000)   # calibration stream of D-07H (as probe.py)
    topo = load_bank("D-07H", "development")[t_idx]
    return W.run_unit_ll((cfg, topo, t_idx, 0, {}, "main"))["rows"]


def main():
    rows = []
    with ProcessPoolExecutor(3) as pool:
        for r in pool.map(job, range(10)):
            rows.extend(r)
    res, lines = {}, ["| scen | T | variant | labelled on data | labelled per draw | draws with a label | BH per draw | repaired per draw |",
                      "|---|---|---|---|---|---|---|---|"]
    for sc in ("clean", "latent1", "latent3"):
        for T in (80, 150):
            for m in ("tolerant_v5_1_leadlag", "tolerant_v5_1_leadlag_skel"):
                g = [r for r in rows if r["scenario"] == sc and r["T"] == T and r["method"] == m and r["kind"] == "missing"
                     and r["status"] == "ok"]
                v = {k: float(np.mean([r[f"info_{k}"] for r in g])) for k in
                     ("gate_n_labelled", "gate_draw_labelled_mean", "gate_draw_any_label_share", "gate_draw_bh_mean",
                      "gate_draw_repaired_mean")}
                res[f"{sc}|{T}|{m}"] = {**v, "runs": len(g)}
                lines.append(f"| {sc} | {T} | {'A' if m.endswith('leadlag') else 'D'} | " + " | ".join(f"{v[k]:.2f}" for k in v) + " |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "probe_draws.json").write_text(json.dumps(res, indent=1))
    (OUT / "probe_draws.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
