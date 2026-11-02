"""Apply the pre-registered rule of round 4 "levboot" (docs/ext/r4levboot.md, section 3) to
results/ext_r4levboot_g, and describe the lag_max 1 / 4 runs. Mechanical; no tuning.

Run: python experiments/ext/r4levboot/analyze.py [--run ext_r4levboot_g] [--describe-only]
Writes results/<run>/ruling.md and ruling.json.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
REF = "tolerant_v5_1"
ARMS = ["r4levboot_L2", "r4levboot_L3", "r4levboot_W3"]
B = 20000
SEED = 20261104
ALPHA = 0.05


def load(name):
    return [json.loads(line) for line in open(RES / name / "runs.jsonl")]


def key(r):
    return (r.get("scenario", "clean"), r["topology"], r["replicate"], r["T"], r["kind"], r["rate"])


def check_identical(rows_a, rows_b, method):
    a = {key(r): r for r in rows_a if r["method"] == method}
    b = {key(r): r for r in rows_b if r["method"] == method}
    common = set(a) & set(b)
    same = 0
    for k in common:
        x, y = a[k], b[k]
        if x["status"] != y["status"]:
            continue
        if x["status"] != "ok" or (abs(x["iscore_nonnull_mean"] - y["iscore_nonnull_mean"]) < 1e-12
                                   and x["n_covered_nonnull"] == y["n_covered_nonnull"]):
            same += 1
    return {"n_a": len(a), "n_b": len(b), "common": len(common), "identical": same,
            "ok": len(common) > 0 and same == len(common)}


def holm(pvals, alpha=ALPHA):
    order = np.argsort(pvals)
    m = len(pvals)
    rej = [False] * m
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            rej[i] = True
        else:
            break
    return rej


class Cells:
    def __init__(self, rows):
        self.rows = rows
        self.by = defaultdict(dict)        # (T, kind, rate) -> {(topo, rep): {method: row}}
        self.nonnull = {}
        for r in rows:
            c = (r["T"], r["kind"], r["rate"])
            self.by[c].setdefault((r["topology"], r["replicate"]), {})[r["method"]] = r
            if r["status"] == "ok" and "n_nonnull" in r:
                self.nonnull[(c, r["topology"], r["replicate"])] = r["n_nonnull"]

    def stats(self, m, c):
        units = self.by[c]
        g = [u[m] for u in units.values() if m in u]
        ok = [r for r in g if r["status"] == "ok"]
        if not g:
            return None
        nn_itt = sum(self.nonnull.get((c, t, rp), 0) for (t, rp), u in units.items() if m in u)
        cov_itt = sum(r["n_covered_nonnull"] for r in ok) / nn_itt if nn_itt else float("nan")
        out = {"n": len(ok), "of": len(g), "fail": len(g) - len(ok), "cov_itt": cov_itt,
               "cov_ok": sum(r["n_covered_nonnull"] for r in ok) / max(sum(r["n_nonnull"] for r in ok), 1) if ok else float("nan"),
               "IS": float(np.mean([r["iscore_nonnull_mean"] for r in ok])) if ok else float("nan"),
               "width": float(np.median([r["width_kept"] for r in ok if r.get("width_kept") is not None])) if ok else float("nan")}
        raw = [r for r in ok if "raw_n_covered_nonnull" in r]
        if raw:
            out["raw_cov"] = sum(r["raw_n_covered_nonnull"] for r in raw) / sum(r["n_nonnull"] for r in raw)
            out["raw_IS"] = float(np.mean([r["raw_iscore_nonnull_mean"] for r in raw]))
            out["raw_width"] = float(np.median([r["raw_width_kept"] for r in raw if r.get("raw_width_kept") is not None]))
        for k in ("info_lev_mean", "info_lev_max", "info_lev_share_gt09", "info_lev_share_floored",
                  "info_lev_eq_mean_max", "info_pool_var_ratio", "info_c_T"):
            v = [r[k] for r in ok if r.get(k) is not None]
            out[k] = float(np.mean(v)) if v else None
        tries = sum(r.get("info_boot_tries", 0) for r in g)
        succ = sum(r.get("info_boot_succ", 0) for r in g)
        out["boot_tries"], out["boot_succ"] = tries, succ
        out["boot_fail_rate"] = (tries - succ) / tries if tries else None
        return out

    def paired(self, m, ref, c, field="iscore_nonnull_mean", seed=SEED):
        d = defaultdict(list)
        for (t, rp), u in self.by[c].items():
            if m in u and ref in u and u[m]["status"] == "ok" and u[ref]["status"] == "ok":
                d[t].append(u[m][field] - u[ref][field])
        if not d:
            return None
        topos = list(d)
        sums = np.array([np.sum(d[t]) for t in topos])
        cnts = np.array([len(d[t]) for t in topos])
        est = float(sums.sum() / cnts.sum())
        rng = np.random.default_rng(seed)
        picks = rng.integers(0, len(topos), size=(B, len(topos)))
        bs = sums[picks].sum(1) / cnts[picks].sum(1)
        lo, hi = np.quantile(bs, (0.025, 0.975))
        p_le = (1 + int((bs <= 0).sum())) / (B + 1)
        p_ge = (1 + int((bs >= 0).sum())) / (B + 1)
        return {"est": est, "lo": float(lo), "hi": float(hi), "p2": min(1.0, 2 * min(p_le, p_ge)), "n": int(cnts.sum())}

    def raw_cov_diff(self, m, ref, c, seed=SEED):
        """Raw (factor-free) pooled coverage difference arm − ref, ratio estimator by topology."""
        num_m, num_r, den = defaultdict(int), defaultdict(int), defaultdict(int)
        for (t, rp), u in self.by[c].items():
            if m in u and ref in u and u[m]["status"] == "ok" and u[ref]["status"] == "ok" \
                    and "raw_n_covered_nonnull" in u[m] and "raw_n_covered_nonnull" in u[ref]:
                num_m[t] += u[m]["raw_n_covered_nonnull"]
                num_r[t] += u[ref]["raw_n_covered_nonnull"]
                den[t] += u[m]["n_nonnull"]
        if not den:
            return None
        topos = list(den)
        a = np.array([num_m[t] for t in topos]); b = np.array([num_r[t] for t in topos]); n = np.array([den[t] for t in topos])
        est = float((a.sum() - b.sum()) / n.sum())
        rng = np.random.default_rng(seed)
        picks = rng.integers(0, len(topos), size=(B, len(topos)))
        bs = (a[picks].sum(1) - b[picks].sum(1)) / n[picks].sum(1)
        lo, hi = np.quantile(bs, (0.025, 0.975))
        return {"est": est, "lo": float(lo), "hi": float(hi)}


def fp(p):
    return "–" if p is None else f"{p['est']:+.3f} [{p['lo']:+.3f}, {p['hi']:+.3f}]"


def describe(C: Cells, cells, cal, prescale=0.5):
    methods = [REF] + [a for a in ARMS if any(a in u for u in C.by[cells[0]].values())]
    out = ["## Width factors (effective = runner factor x 0.5)", "",
           "| T | kind | " + " | ".join(methods) + " |", "|---|---|" + "---|" * len(methods)]
    Ts = sorted({c[0] for c in cells})
    for T in Ts:
        for k in ("none", "extra", "missing", "reversed"):
            vals = [cal.get(f"{m}|{T}|{k}") for m in methods]
            if all(v is None for v in vals):
                continue
            out.append(f"| {T} | {k} | " + " | ".join("–" if v is None else f"{v * prescale:.2f}" for v in vals) + " |")
    out += ["", "## Cells: ITT coverage / IS / width [failed runs]", "",
            "| T | cell | " + " | ".join(methods) + " |", "|---|---|" + "---|" * len(methods)]
    S = {}
    for c in cells:
        cs = []
        for m in methods:
            s = C.stats(m, c)
            S[(m, c)] = s
            cs.append("–" if s is None else f"{s['cov_itt']:.3f} / {s['IS']:.3f} / {s['width']:.2f}" + (f" [{s['fail']}]" if s["fail"] else ""))
        out.append(f"| {c[0]} | {c[1]}-{c[2]} | " + " | ".join(cs) + " |")
    out += ["", "## Raw percentile interval (pre-scale and width factor removed): coverage / IS / width", "",
            "| T | cell | " + " | ".join(methods) + " | " + " | ".join(f"raw cov {a[10:]} − v5_1 [95% CI]" for a in methods[1:]) + " |",
            "|---|---|" + "---|" * (2 * len(methods) - 1)]
    for c in cells:
        cs = []
        for m in methods:
            s = S[(m, c)]
            cs.append("–" if not s or "raw_cov" not in s else f"{s['raw_cov']:.3f} / {s['raw_IS']:.2f} / {s['raw_width']:.2f}")
        for a in methods[1:]:
            cs.append(fp(C.raw_cov_diff(a, REF, c)))
        out.append(f"| {c[0]} | {c[1]}-{c[2]} | " + " | ".join(cs) + " |")
    out += ["", "## Leverage profile of the data fit and bootstrap failure rate (mean over ok runs)", "",
            "lev_mean / share h>0.9 / share floored (1-h<0.05) / max per-equation mean h / pool variance ratio vs RSS/dof / failure rate (tries−succ)/tries", "",
            "| T | cell | " + " | ".join(methods) + " |", "|---|---|" + "---|" * len(methods)]
    for c in cells:
        cs = []
        for m in methods:
            s = S[(m, c)]
            if not s or s.get("info_lev_mean") is None:
                cs.append("–")
                continue
            fr = s["boot_fail_rate"]
            cs.append(f"{s['info_lev_mean']:.3f} / {s['info_lev_share_gt09']:.4f} / {s['info_lev_share_floored']:.4f} / "
                      f"{s['info_lev_eq_mean_max']:.3f} / {s['info_pool_var_ratio']:.2f} / "
                      + ("–" if fr is None else f"{fr:.4f}"))
        out.append(f"| {c[0]} | {c[1]}-{c[2]} | " + " | ".join(cs) + " |")
    return out, S, methods


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="ext_r4levboot_g")
    ap.add_argument("--describe-only", action="store_true")
    ap.add_argument("--pair-with", default="ext_v51_eval")
    ap.add_argument("--merge", nargs="*", default=["ext_r4levboot_gw"],
                    help="runs whose arm rows are added (same seeds; their own reference rows, if any, are dropped)")
    args = ap.parse_args()
    rows = load(args.run)
    merged = {}
    for extra in args.merge or []:
        if (RES / extra / "runs.jsonl").exists():
            ex = [r for r in load(extra) if r["method"] != REF]
            merged[extra] = sorted({r["method"] for r in ex})
            rows += ex
    C = Cells(rows)
    cfg = json.loads((RES / args.run / "manifest.json").read_text())["config"]
    cells = [(T, k, r) for T in cfg["T"] for (k, r) in [("none", 0.0)] + [(k, r) for k in cfg["damage"]["kinds"] for r in cfg["damage"]["rates"]]]
    cal = json.loads((RES / args.run / "calibration.json").read_text())
    for extra in merged:
        ce = json.loads((RES / extra / "calibration.json").read_text())
        cal.update({k: v for k, v in ce.items() if k.split("|")[0] in merged[extra]})
    out = [f"# {args.run}: round 4 levboot (generated by experiments/ext/r4levboot/analyze.py)", ""]
    res = {"run": args.run, "merged": merged}
    if merged:
        out += [f"Merged arm rows: {merged}", ""]
    if args.pair_with and (RES / args.pair_with / "runs.jsonl").exists():
        chk = check_identical(rows, load(args.pair_with), REF)
        res["pairing"] = chk
        out += [f"Pairing of {REF} rows with results/{args.pair_with}: {chk['identical']}/{chk['common']} identical "
                f"({chk['n_a']} vs {chk['n_b']} rows) -> **{chk['ok']}**", ""]
    d, S, methods = describe(C, cells, cal)
    out += d
    # paired IS for all cells
    P = {(a, c): C.paired(a, REF, c) for a in methods[1:] for c in cells}
    out += ["", f"## Paired IS difference arm − {REF}, 95% CI clustered by topology (B = {B}, seed {SEED}), two-sided p", "",
            "| T | cell | " + " | ".join(methods[1:]) + " |", "|---|---|" + "---|" * (len(methods) - 1)]
    for c in cells:
        out.append(f"| {c[0]} | {c[1]}-{c[2]} | " + " | ".join(
            "–" if P[(a, c)] is None else f"{fp(P[(a, c)])} (p {P[(a, c)]['p2']:.4f}, n {P[(a, c)]['n']})" for a in methods[1:]) + " |")
    res["paired"] = {f"{a}|{c[0]}|{c[1]}|{c[2]}": P[(a, c)] for a in methods[1:] for c in cells}
    res["stats"] = {f"{m}|{c[0]}|{c[1]}|{c[2]}": S[(m, c)] for m in methods for c in cells}
    if args.describe_only:
        _write(args.run, out, res)
        return
    # ---------------- pre-registered rule (docs/ext/r4levboot.md section 3) ----------------
    primary = [(40, k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)] + [(80, "missing", 0.2), (80, "missing", 0.5)]
    rest = [c for c in cells if c not in primary]
    out += ["", "## Pre-registered rule", "", f"Primary family: {len(ARMS)} arms x {len(primary)} cells = {len(ARMS) * len(primary)} two-sided tests, Holm {ALPHA}.",
            f"No-harm family per arm: {len(rest)} cells, Holm {ALPHA} (worsening = rejected with est > 0).", ""]
    fam = [(a, c) for a in ARMS for c in primary]
    rej = holm([P[x]["p2"] if P[x] else 1.0 for x in fam])
    rejd = dict(zip(fam, rej))
    verdict = {}
    for a in ARMS:
        wins, cov_ok, lines = 0, True, []
        for c in primary:
            p, s, s0 = P[(a, c)], S[(a, c)], S[(REF, c)]
            fail_ok = s is not None and s0 is not None and s["fail"] <= s0["fail"] + 1
            win = bool(rejd[(a, c)] and p and p["est"] < 0 and s["cov_itt"] >= 0.90 and fail_ok)
            wins += win
            cov_ok &= bool(s and s["cov_itt"] >= 0.90 and fail_ok)
            lines.append(f"- T{c[0]} {c[1]}-{c[2]}: dIS {fp(p)} p {p['p2'] if p else float('nan'):.5f} Holm-reject {rejd[(a, c)]}; "
                         f"cov {s['cov_itt']:.3f} (v5_1 {s0['cov_itt']:.3f}); fails {s['fail']} (v5_1 {s0['fail']}) -> {'WIN' if win else '-'}")
        rr = holm([P[(a, c)]["p2"] if P[(a, c)] else 1.0 for c in rest])
        harm_lines, harm = [], False
        for c, rj in zip(rest, rr):
            p, s, s0 = P[(a, c)], S[(a, c)], S[(REF, c)]
            ratio = s["IS"] / s0["IS"]
            bad = []
            if ratio > 1.05:
                bad.append("IS ratio > 1.05")
            if rj and p["est"] > 0:
                bad.append("Holm-significant worsening")
            if s0["cov_itt"] >= 0.90 and s["cov_itt"] < 0.90:
                bad.append("coverage < 0.90 where v5_1 >= 0.90")
            if s["fail"] > s0["fail"] + 1:
                bad.append("more failures")
            harm |= bool(bad)
            harm_lines.append(f"- T{c[0]} {c[1]}-{c[2]}: ratio {ratio:.3f}, dIS {fp(p)} Holm-reject {rj}, cov {s['cov_itt']:.3f} (v5_1 {s0['cov_itt']:.3f}), fails {s['fail']}/{s0['fail']}"
                              + (f" -> HARM ({'; '.join(bad)})" if bad else ""))
        retained = wins >= 2 and cov_ok and not harm
        # secondary descriptive claim
        t40 = [(40, k, r) for k in ("extra", "missing", "reversed") for r in (0.2, 0.5)]
        rc = [C.raw_cov_diff(a, REF, c) for c in t40]
        n_sec = sum(1 for x in rc if x and x["est"] >= 0.02)
        verdict[a] = {"wins": wins, "of": len(primary), "cov_all_primary": cov_ok, "harm": harm, "retained": retained,
                      "secondary_raw_cov_ge_0.02": n_sec, "secondary_claim": n_sec >= 4}
        out += [f"### {a}", "", *lines, "", f"No-harm ({len(rest)} cells; Holm rejections {sum(rr)}/{len(rest)}):", *harm_lines, "",
                f"**{a}: wins {wins}/{len(primary)} (Holm over {len(fam)}), coverage >= 0.90 in all primary: {cov_ok}, harm: {harm} -> "
                f"{'RETAINED (exploratory)' if retained else 'NOT RETAINED'}**", "",
                f"Secondary (descriptive): raw coverage − v5_1 raw coverage >= 0.02 in {n_sec}/6 T40 damaged cells -> "
                f"claim 'leverage explains part of the factor' {'MADE' if n_sec >= 4 else 'NOT MADE'}", ""]
    ret = [a for a in ARMS if verdict[a]["retained"]]
    if ret:
        best = sorted(ret, key=lambda a: (-verdict[a]["wins"], np.mean([S[(a, c)]["IS"] for c in primary])))[0]
    else:
        best = None
    res["verdict"] = verdict
    res["candidate"] = best
    out += [f"**Candidate levboot: {'RETAINED (exploratory) with arm ' + best if best else 'NOT RETAINED'}**"]
    # predictions (descriptive)
    out += ["", "## Predictions of the brief (descriptive, not part of the verdict)", ""]
    for a in ARMS:
        for kd in ("missing", "reversed"):
            f0 = cal.get(f"{REF}|40|{kd}"); f1 = cal.get(f"{a}|40|{kd}")
            if f0 and f1:
                out.append(f"- {a} T40 {kd}: effective factor {f1 * 0.5:.2f} vs v5_1 {f0 * 0.5:.2f} (drop {(f0 - f1) * 0.5:+.2f}; predicted >= 0.10)")
    _write(args.run, out, res)


def _write(run, out, res):
    (RES / run / "ruling.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (RES / run / "ruling.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
