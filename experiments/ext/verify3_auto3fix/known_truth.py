"""Skeptic check (verify3_auto3fix): known-truth synthetic rows fed to check_p4h2_v2.py.

Builds small synthetic main/latent run directories in a scratch dir (no simulation, no bank), with
n_nonnull = 10 per unit and hand-set covered counts / IS values, then applies the analyzer's
build/evaluate/integrity functions and compares with hand-computed expectations.
Usage: python experiments/ext/verify3_auto3fix/known_truth.py SCRATCH_DIR
Writes results/ext_verify3_auto3fix/known_truth.json
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ext" / "auto3fix"))
import check_p4h2_v2 as C  # noqa: E402

WIDTH = json.loads(C.WIDTH.read_text())
FROZEN = json.loads(C.FROZEN.read_text())
CFG1 = json.loads(C.CFG1.read_text())
CFG2 = json.loads(C.CFG2.read_text())
TOPOS = [f"t{i:02d}" for i in range(20)]
NN = 10


def row(method, topo, rep, sc, T, kind, rate, covered=9, iscore=1.0, k=3, status="ok"):
    r = {"method": method, "topology": topo, "replicate": rep, "scenario": sc, "T": T, "kind": kind,
         "rate": rate, "k": 0 if kind in ("none",) else k, "status": status}
    if status != "ok":
        return r
    r.update({"n_nonnull": NN, "n_covered_nonnull": covered, "iscore_nonnull_mean": iscore})
    if method == "tolerant_auto3":
        r.update({"info_state": "closed", "info_c_T": WIDTH[f"closed|{T}"]})
    if method == "tolerant_v4":
        if kind == "ges":
            r["info_c_T"] = FROZEN[f"mod|{T}|none"]
        else:
            wk = "none" if r["k"] == 0 else kind
            r["info_c_T"] = FROZEN[f"mod|{T}|{wk}"]
    return r


def base_rows(cfg, scen):
    rows = []
    cells = C_cells(cfg)
    for t in TOPOS:
        for rep in range(3):
            for sc in scen:
                for T in cfg["T"]:
                    for kind, rate in cells:
                        for m in cfg["methods"]:
                            rows.append(row(m, t, rep, sc, T, kind, rate, covered=10, iscore=1.0))
    return rows


def C_cells(cfg):
    learned = [("ges", 0.0)] if cfg.get("learned") else []
    return [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]] + learned


def write(d: Path, cfg, rows):
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps({"config": cfg, "topologies": [{"id": t} for t in TOPOS]}))
    with open(d / "runs.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def analyse(work, main_rows, lat_rows, dry=True, cfg1=CFG1, cfg2=CFG2):
    write(work / "main", cfg1, main_rows)
    write(work / "lat", cfg2, lat_rows)
    m, l = C.Run(work / "main"), C.Run(work / "lat")
    E = C.evaluate(C.build(m, l))
    I = C.integrity(m, l, dry)
    return E, I


def edit(rows, pred, fn, limit):
    n, out = 0, []
    for r in rows:
        if n < limit and pred(r):
            n += 1
            r2 = fn(r)
            if r2 is not None:
                out.append(r2)
        else:
            out.append(r)
    return out


def main(scratch):
    work = Path(scratch)
    M0 = base_rows(CFG1, ["clean"])
    L0 = base_rows(CFG2, ["clean", "latent1"])
    res = {}
    is_cell = lambda T, k, r, m="tolerant_auto3", sc="clean": (lambda x: x["method"] == m and x["scenario"] == sc and x["T"] == T and x["kind"] == k and x["rate"] == r)  # noqa: E731
    fail = lambda x: {**{k: x[k] for k in ("method", "topology", "replicate", "scenario", "T", "kind", "rate", "k")}, "status": "underdetermined"}  # noqa: E731

    # K0: all ok, all covered -> CONFIRMED, cov 1.0, ratio 1.0
    E, I = analyse(work / "k0", M0, L0)
    res["K0_all_ok"] = {"rule": E["rule_holds"], "integrity": all(c["ok"] for c in I), "exp": True}

    # K1: exact boundary: every auto3 unit in T80 rev-0.5 covers 9/10 -> cov 0.90 -> pass (>=)
    Mk = edit(M0, is_cell(80, "reversed", 0.5), lambda x: {**x, "n_covered_nonnull": 9}, 10**9)
    E, _ = analyse(work / "k1", Mk, L0)
    x = E["C1"][("clean", 80, "reversed", 0.5)]
    res["K1_cov_exactly_0.90"] = {"cov": x["cov"], "ok": x["ok"], "exp_ok": True}

    # K2: 3 failed auto3 runs in T150 rev-0.2, rest 10/10 -> cov 570/600 = 0.95, bad 3 -> pass
    Mk = edit(M0, is_cell(150, "reversed", 0.2), fail, 3)
    E, I = analyse(work / "k2", Mk, L0)
    x = E["C1"][("clean", 150, "reversed", 0.2)]
    res["K2_3_failed"] = {"cov": x["cov"], "n_bad": x["n_bad"], "ok": x["ok"], "exp": [0.95, 3, True]}

    # K3: 4 failed -> cov 560/600 = 0.9333 >= 0.90 but bad 4 > 3 -> fail by the cap alone
    Mk = edit(M0, is_cell(150, "reversed", 0.2), fail, 4)
    E, _ = analyse(work / "k3", Mk, L0)
    x = E["C1"][("clean", 150, "reversed", 0.2)]
    res["K3_4_failed"] = {"cov": x["cov"], "n_bad": x["n_bad"], "ok": x["ok"], "rule": E["rule_holds"], "exp": [0.9333, 4, False, False]}

    # K4: 4 absent (deleted) rows -> same as K3
    Mk = edit(M0, is_cell(150, "reversed", 0.2), lambda x: None, 4)
    E, _ = analyse(work / "k4", Mk, L0)
    x = E["C1"][("clean", 150, "reversed", 0.2)]
    res["K4_4_absent"] = {"cov": x["cov"], "n_bad": x["n_bad"], "ok": x["ok"], "exp": [0.9333, 4, False]}

    # K5: one unit (t00, rep 0) has no ok row at all in main run -> denominator undefined -> ruled cells fail
    Mk = [fail(r) if (r["topology"] == "t00" and r["replicate"] == 0) else r for r in M0]
    E, I = analyse(work / "k5", Mk, L0)
    res["K5_unit_without_ok_row"] = {"C1": E["R"]["C1"], "C2": E["R"]["C2"], "C3": E["R"]["C3"], "undef": E["C1"][("clean", 80, "missing", 0.2)]["undefined"],
                                     "n_bad": E["C1"][("clean", 80, "missing", 0.2)]["n_bad"], "exp": "C1 False (undefined=1), C2 True (59 pairs >= 57), C3 False"}

    # K6: IS paired: v4 fails on 3 units at T80 none -> 57 pairs pass; 4 -> 56 pairs fail
    for nfail, exp in ((3, True), (4, False)):
        Mk = edit(M0, is_cell(80, "none", 0.0, m="tolerant_v4"), fail, nfail)
        E, _ = analyse(work / f"k6_{nfail}", Mk, L0)
        x = E["C2"][("clean", 80, "none", 0.0)]
        res[f"K6_v4_fail_{nfail}"] = {"n_pair": x["n_pair"], "ok": x["ok"], "exp_ok": exp}

    # K7: IS ratio: auto3 IS = 1.35 exactly on every unit at T40 none -> pass; 1.36 -> fail
    for v, exp in ((1.35, True), (1.36, False)):
        Mk = edit(M0, is_cell(40, "none", 0.0), lambda x, v=v: {**x, "iscore_nonnull_mean": v}, 10**9)
        E, _ = analyse(work / f"k7_{v}", Mk, L0)
        x = E["C2"][("clean", 40, "none", 0.0)]
        res[f"K7_ratio_{v}"] = {"ratio": x["ratio"], "ok": x["ok"], "exp_ok": exp}

    # K8: paired ratio differs from unpaired when a v4 unit with high IS fails
    Mk = edit(M0, is_cell(80, "ges", 0.0), lambda x: {**x, "iscore_nonnull_mean": 2.0}, 1)  # auto3 t00 rep0 IS=2
    Mk = edit(Mk, is_cell(80, "ges", 0.0, m="tolerant_v4"), fail, 1)                       # v4 t00 rep0 fails
    E, _ = analyse(work / "k8", Mk, L0)
    x = E["C3"][("clean", 80, "ges", 0.0)]
    res["K8_paired_vs_unpaired"] = {"ratio_paired": x["ratio"], "ratio_unpaired": x["ratio_unpaired"], "exp": [1.0, (61 / 60) / 1.0]}

    # K9: latent1 L1 cell with coverage 0.85 -> L1 fails; clean rows of config 2 are not ruled
    Lk = edit(L0, is_cell(80, "missing", 0.2, sc="latent1"), lambda x: {**x, "n_covered_nonnull": 8}, 45)  # (45*8+15*10)/600 = 0.85
    E, _ = analyse(work / "k9", M0, Lk)
    x = E["L1"][("latent1", 80, "missing", 0.2)]
    res["K9_L1_cov_0.85"] = {"cov": x["cov"], "ok": x["ok"], "exp": [0.85, False]}
    Lk = edit(L0, is_cell(80, "missing", 0.2, sc="clean"), lambda x: {**x, "n_covered_nonnull": 0}, 10**9)
    E, _ = analyse(work / "k9b", M0, Lk)
    res["K9b_config2_clean_not_ruled"] = {"rule": E["rule_holds"], "exp": True}

    # K10: I1 in non-dry mode: P4-H2 manifest config == frozen config -> ok; any drift -> fail
    E, I = analyse(work / "k10", M0, L0, dry=False)
    res["K10_I1_identical"] = {"I1": I[0]["ok"], "exp": True}
    c1b = copy.deepcopy(CFG1)
    c1b["n_boot"] = 200
    E, I = analyse(work / "k10b", M0, L0, dry=False, cfg1=c1b)
    res["K10b_I1_drift"] = {"I1": I[0]["ok"], "exp": False}

    # K11: I4: v4 row at reversed with stated k = 0 must use the 'none' factor
    Mk = edit(M0, is_cell(80, "reversed", 0.2, m="tolerant_v4"), lambda x: {**x, "k": 0, "info_c_T": FROZEN["mod|80|none"]}, 1)
    _, I = analyse(work / "k11", Mk, L0)
    res["K11_I4_k0_none"] = {"I4": I[3]["ok"], "exp": True}
    Mk = edit(M0, is_cell(80, "reversed", 0.2, m="tolerant_v4"), lambda x: {**x, "info_c_T": 9.9}, 1)
    _, I = analyse(work / "k11b", Mk, L0)
    res["K11b_I4_wrong_factor"] = {"I4": I[3]["ok"], "exp": False}

    # K12: duplicate row -> I2 fails
    _, I = analyse(work / "k12", M0 + [M0[0]], L0)
    res["K12_duplicate"] = {"I2": I[1]["ok"], "exp": False}

    # K13: auto3 width trace wrong -> I3 fails
    Mk = edit(M0, is_cell(80, "none", 0.0), lambda x: {**x, "info_c_T": 1.0}, 1)
    _, I = analyse(work / "k13", Mk, L0)
    res["K13_I3_wrong_width"] = {"I3": I[2]["ok"], "exp": False}

    out = ROOT / "results" / "ext_verify3_auto3fix"
    out.mkdir(parents=True, exist_ok=True)
    (out / "known_truth.json").write_text(json.dumps(res, indent=1, default=str))
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1])
