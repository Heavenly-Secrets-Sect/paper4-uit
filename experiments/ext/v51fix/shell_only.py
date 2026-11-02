"""R3-2 (docs/ext/v51fix.md 1.D): write into results/ the round-2 numbers of direction v51 that existed
only in shell output, with their source, and recompute the per-run range of duplicated terms.

Sources: the two round-2 v51 transcripts (attempt 1 and resume) cited in
results/ext_verify2_v51/timeline.json; values are copied verbatim from the tool outputs there.
Recomputed: per-run ranges from results/ext_v51_eval/runs.jsonl; per-fit timings from
results/ext_v51_probe/probe_tau2.json (field "sec").

Run: python experiments/ext/v51fix/shell_only.py -> results/ext_v51fix_shellonly/{shell_only.json, shell_only.md}
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "ext_v51fix_shellonly"
TRANSCRIPT_DIR = ("~/.claude/projects/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/"
                  "subagents/workflows/wf_ccca4e91-1dd/")

VERBATIM = {
    "timing_run_D07H_attempt1": {
        "when_utc": "2026-11-01T19:47:56Z (tool result logged 19:48:00.955Z)",
        "transcript": TRANSCRIPT_DIR + "agent-a7558e999131276cc.jsonl",
        "what": "probe_tau.py (buggy targeted variant, ext_narrow.tolerant_sel) on D-07H development, 1 topology x 1 replicate, "
                "T = 40 and 200, n_boot 99; inside the probe sample. Printed before the tau procedure was written (19:48:30Z).",
        "output_verbatim": [
            "T=40 ratio 1.27 [1.26,1.28] c* {'targeted': 1.2, 'all': 0.85} d -3.596 [-3.596,-3.596] (0.2: -2.257, 0.5: -4.934) "
            "fail {'targeted': 0, 'all': 0} sec {'targeted': 0.590297459, 'all': 0.2471837085}",
            "T=200 ratio 6.61 [6.55,6.66] c* {'targeted': 1.8, 'all': 1.4} d +0.151 [+0.151,+0.151] (0.2: -0.095, 0.5: +0.398) "
            "fail {'targeted': 0, 'all': 0} sec {'targeted': 0.8714890415000001, 'all': 0.39938058350000016}",
            "T* = 40; tau = 3.9383; T* = 40, next probed T = 200: tau = midpoint of their mean ratios; 4 s"],
        "numbers": {"d40": -3.596, "d200": 0.151, "d40_rate0.2": -2.257, "d40_rate0.5": -4.934, "d200_rate0.2": -0.095,
                    "d200_rate0.5": 0.398, "tau_of_this_smoke_run": 3.9383},
    },
    "dedup_sanity_check_D07H_resume": {
        "when_utc": "2026-11-02T02:23:49Z (tool result logged 02:23:52.575Z)",
        "transcript": TRANSCRIPT_DIR + "agent-aecea0233cf01bed2.jsonl",
        "what": "scratchpad script (not kept): ext_v51.tolerant_sel_dd vs ext_narrow.tolerant_sel on D-07H development, "
                "3 topologies (syn_dag_00..02), T = 40, missing-0.5, n_boot 49, seed 9 990 000 + topology index (outside the "
                "probe sample). Columns: status buggy, status dedup, info of dedup, max |difference of lower bounds|.",
        "output_verbatim": [
            "syn_dag_00 ok ok {'n_repair': 2, 'n_open': 33, 'n_open_boot_mean': 36.714285714285715, 'n_reversal_pool': None, "
            "'n_dup_terms_data': 8, 'n_dup_terms_total': 976} 1.9812739982548677",
            "syn_dag_01 ok ok {'n_repair': 4, 'n_open': 33, 'n_open_boot_mean': 40.91836734693877, 'n_reversal_pool': None, "
            "'n_dup_terms_data': 12, 'n_dup_terms_total': 800} 2.5059199522991333",
            "syn_dag_02 ok ok {'n_repair': 1, 'n_open': 33, 'n_open_boot_mean': 35.265306122448976, 'n_reversal_pool': None, "
            "'n_dup_terms_data': 4, 'n_dup_terms_total': 692} 1.6906078152537543"],
        "numbers": {"dup_terms_data": [8, 12, 4], "dup_terms_total": [976, 800, 692], "max_abs_lo_diff": [1.981, 2.506, 1.691]},
    },
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"verbatim_from_transcripts": VERBATIM}
    # per-fit timing, probe_tau2 (D-07H development, shared CPU)
    p2 = json.loads((ROOT / "results/ext_v51_probe/probe_tau2.json").read_text())["report"]
    res["probe_tau2_seconds_per_fit"] = {T: p2[T]["sec"] for T in p2}
    tg = [p2[T]["sec"]["targeted"] for T in ("40", "60", "80", "100", "120", "150")]
    al = [p2[T]["sec"]["all"] for T in ("40", "60", "80", "100", "120", "150")]
    res["probe_tau2_seconds_per_fit_range_T40_150"] = {"targeted": [min(tg), max(tg)], "all": [min(al), max(al)]}
    # per-run duplicated terms, ext_v51_eval
    per = defaultdict(list)
    tot = defaultdict(list)
    for line in open(ROOT / "results/ext_v51_eval/runs.jsonl"):
        r = json.loads(line)
        if r["method"] == "tolerant_v5_1" and r["kind"] == "missing" and r["status"] == "ok":
            per[(r["T"], r["rate"])].append(r["info_n_dup_terms_data"])
            tot[(r["T"], r["rate"])].append(r["info_n_dup_terms_total"])
    cells = {}
    for k in sorted(per):
        v, w = per[k], tot[k]
        cells[f"{k[0]}|missing|{k[1]}"] = {"n_runs": len(v), "data_min": min(v), "data_max": max(v),
                                           "data_mean": sum(v) / len(v), "runs_with_dup_data": sum(x > 0 for x in v),
                                           "total_min": min(w), "total_max": max(w), "total_mean": sum(w) / len(w)}
    allv = [x for v in per.values() for x in v]
    allw = [x for v in tot.values() for x in v]
    res["ext_v51_eval_dup_terms"] = {"per_cell": cells, "per_run_data_range": [min(allv), max(allv)],
                                     "cell_mean_data_range": [min(c["data_mean"] for c in cells.values()),
                                                              max(c["data_mean"] for c in cells.values())],
                                     "per_run_total_range": [min(allw), max(allw)],
                                     "runs_with_any_dup_data": f"{sum(x > 0 for x in allv)}/{len(allv)}",
                                     "runs_with_any_dup_total": f"{sum(x > 0 for x in allw)}/{len(allw)}"}
    (OUT / "shell_only.json").write_text(json.dumps(res, indent=1))
    d = res["ext_v51_eval_dup_terms"]
    md = ["# v51 round-2 numbers that existed only in shell output (experiments/ext/v51fix/shell_only.py)", "",
          "## Verbatim from transcripts", ""]
    for k, v in VERBATIM.items():
        md += [f"### {k}", "", f"- when: {v['when_utc']}", f"- transcript: `{v['transcript']}`", f"- what: {v['what']}", "", "```"]
        md += v["output_verbatim"] + ["```", ""]
    md += ["## Seconds per fit, probe_tau2 (D-07H development, n_boot 199, shared CPU)", "",
           "| T | targeted | all |", "|---|---|---|"]
    md += [f"| {T} | {s['targeted']:.2f} | {s['all']:.2f} |" for T, s in res["probe_tau2_seconds_per_fit"].items()]
    r = res["probe_tau2_seconds_per_fit_range_T40_150"]
    md += ["", f"T 40–150: targeted {r['targeted'][0]:.2f}–{r['targeted'][1]:.2f} s, all-lag {r['all'][0]:.2f}–{r['all'][1]:.2f} s per fit "
           "(this is the source of '1.9–2.5 s per fit' in docs/ext/v51.md).", "",
           "## Duplicated terms removed by the de-duplication, ext_v51_eval missing cells (tolerant_v5_1)", "",
           "| cell | runs | data fit: min–max (mean) | runs with any | summed over draws: min–max (mean) |", "|---|---|---|---|---|"]
    for k, c in cells.items():
        md.append(f"| {k} | {c['n_runs']} | {c['data_min']}–{c['data_max']} ({c['data_mean']:.1f}) | {c['runs_with_dup_data']} | "
                  f"{c['total_min']}–{c['total_max']} ({c['total_mean']:.0f}) |")
    md += ["", f"Per run (data fit): {d['per_run_data_range'][0]}–{d['per_run_data_range'][1]}; cell means: "
           f"{d['cell_mean_data_range'][0]:.1f}–{d['cell_mean_data_range'][1]:.1f}; runs with any duplicate on the data fit: "
           f"{d['runs_with_any_dup_data']}; with any duplicate over the draws: {d['runs_with_any_dup_total']}."]
    (OUT / "shell_only.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[-12:]))


if __name__ == "__main__":
    main()
