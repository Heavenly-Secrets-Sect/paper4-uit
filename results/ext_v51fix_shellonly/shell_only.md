# v51 round-2 numbers that existed only in shell output (experiments/ext/v51fix/shell_only.py)

## Verbatim from transcripts

### timing_run_D07H_attempt1

- when: 2026-11-01T19:47:56Z (tool result logged 19:48:00.955Z)
- transcript: `~/.claude/projects/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/subagents/workflows/wf_ccca4e91-1dd/agent-a7558e999131276cc.jsonl`
- what: probe_tau.py (buggy targeted variant, ext_narrow.tolerant_sel) on D-07H development, 1 topology x 1 replicate, T = 40 and 200, n_boot 99; inside the probe sample. Printed before the tau procedure was written (19:48:30Z).

```
T=40 ratio 1.27 [1.26,1.28] c* {'targeted': 1.2, 'all': 0.85} d -3.596 [-3.596,-3.596] (0.2: -2.257, 0.5: -4.934) fail {'targeted': 0, 'all': 0} sec {'targeted': 0.590297459, 'all': 0.2471837085}
T=200 ratio 6.61 [6.55,6.66] c* {'targeted': 1.8, 'all': 1.4} d +0.151 [+0.151,+0.151] (0.2: -0.095, 0.5: +0.398) fail {'targeted': 0, 'all': 0} sec {'targeted': 0.8714890415000001, 'all': 0.39938058350000016}
T* = 40; tau = 3.9383; T* = 40, next probed T = 200: tau = midpoint of their mean ratios; 4 s
```

### dedup_sanity_check_D07H_resume

- when: 2026-11-02T02:23:49Z (tool result logged 02:23:52.575Z)
- transcript: `~/.claude/projects/-Users-kietnt-Desktop-Workspace-UIT-NCKH-aDuy/2f8361ac-f8f9-48a7-901f-7ac732921a60/subagents/workflows/wf_ccca4e91-1dd/agent-aecea0233cf01bed2.jsonl`
- what: scratchpad script (not kept): ext_v51.tolerant_sel_dd vs ext_narrow.tolerant_sel on D-07H development, 3 topologies (syn_dag_00..02), T = 40, missing-0.5, n_boot 49, seed 9 990 000 + topology index (outside the probe sample). Columns: status buggy, status dedup, info of dedup, max |difference of lower bounds|.

```
syn_dag_00 ok ok {'n_repair': 2, 'n_open': 33, 'n_open_boot_mean': 36.714285714285715, 'n_reversal_pool': None, 'n_dup_terms_data': 8, 'n_dup_terms_total': 976} 1.9812739982548677
syn_dag_01 ok ok {'n_repair': 4, 'n_open': 33, 'n_open_boot_mean': 40.91836734693877, 'n_reversal_pool': None, 'n_dup_terms_data': 12, 'n_dup_terms_total': 800} 2.5059199522991333
syn_dag_02 ok ok {'n_repair': 1, 'n_open': 33, 'n_open_boot_mean': 35.265306122448976, 'n_reversal_pool': None, 'n_dup_terms_data': 4, 'n_dup_terms_total': 692} 1.6906078152537543
```

## Seconds per fit, probe_tau2 (D-07H development, n_boot 199, shared CPU)

| T | targeted | all |
|---|---|---|
| 40 | 1.87 | 0.86 |
| 60 | 2.00 | 0.96 |
| 80 | 2.11 | 1.01 |
| 100 | 2.23 | 1.07 |
| 120 | 2.33 | 1.10 |
| 150 | 2.53 | 1.23 |
| 200 | 2.89 | 1.39 |

T 40–150: targeted 1.87–2.53 s, all-lag 0.86–1.23 s per fit (this is the source of '1.9–2.5 s per fit' in docs/ext/v51.md).

## Duplicated terms removed by the de-duplication, ext_v51_eval missing cells (tolerant_v5_1)

| cell | runs | data fit: min–max (mean) | runs with any | summed over draws: min–max (mean) |
|---|---|---|---|---|
| 40|missing|0.2 | 60 | 0–16 (3.1) | 28 | 700–2268 (1504) |
| 40|missing|0.5 | 60 | 0–32 (8.7) | 50 | 1396–6876 (3152) |
| 80|missing|0.2 | 60 | 0–16 (5.2) | 45 | 1416–3080 (2386) |
| 80|missing|0.5 | 60 | 0–44 (13.7) | 57 | 2260–8304 (4956) |
| 150|missing|0.2 | 60 | 0–16 (6.4) | 50 | 1352–3184 (2619) |
| 150|missing|0.5 | 60 | 4–44 (16.7) | 60 | 2468–8752 (5993) |

Per run (data fit): 0–44; cell means: 3.1–16.7; runs with any duplicate on the data fit: 290/360; with any duplicate over the draws: 360/360.
