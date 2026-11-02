# Bảng bản thảo Paper 4 (R3-8, hướng `tables`)

**Trạng thái.** Mọi số ở đây là **exploratory, chỉ trên D-07 development** (seed_base 20261102), lấy từ các row đã lưu của vòng 1–3. Hướng này **không chạy thí nghiệm mới** nào (không gọi runner, không đọc bank). Chỉ tính lại thống kê từ `runs.jsonl` / `pairs.npz` đã có, và trích số từ file kết quả của các hướng khác. Không đụng P4-H1, P4-H2 hay confirmatory split. Không dùng số P4-H1 nào, kể cả số đã lưu trong `results/ext_metrics_rq41/tables.md`.

Mỗi bảng ghi đường dẫn file nguồn ngay bên dưới. Số do hướng này tính nằm trong `results/ext_tables_main/` (script `experiments/ext/tables/build_tables.py`).

---

## 0. Định nghĩa ghi trước (viết lúc 2026-11-02T07:03Z, trước khi tính bất kỳ số nào của mục 1–6)

Phần này cố định cách tính. Sau khi có số, phần này không sửa; mọi lệch sẽ được ghi ở mục "Lệch so với định nghĩa".

**0.1 Ghép cặp và bootstrap (dùng cho bảng 1, 2, 5).**
- Đơn vị: (topology, replicate, T, kind, rate). IS của một run là `iscore_nonnull_mean`. Hiệu A − B tính trên các run mà cả hai `status == ok`.
- Ước lượng: trung bình hiệu trên mọi run ghép được. CI 95%: cluster bootstrap theo 20 topology, percentile, **B = 20000**, **một ma trận chỉ số chung** `default_rng(20261102).integers(0, 20, (B, 20))` cho mọi so sánh. p hai phía như analyzer của baselines3: p_W = (1 + #{boot ≥ 0})/(B + 1), p_L = (1 + #{boot ≤ 0})/(B + 1), p2 = min(1, 2·min(p_W, p_L)).
- Phân lớp: "thô" theo CI (W nếu cận trên < 0, L nếu cận dưới > 0, còn lại T). "Holm" theo Holm step-down hai phía α = 0.05 trên **toàn bộ family của bảng đó**. Mọi số đếm cell đều báo cả thô lẫn Holm.
- Coverage: pooled trên non-null pair. Mẫu số lấy `n_nonnull` của unit (từ bất kỳ row ok nào của unit đó). Run thất bại tính là không cover pair nào.
- Kiểm tra trước khi dùng: row `tolerant_v4` của mọi nguồn phải trùng nhau (cùng `iscore_nonnull_mean` và `n_covered_nonnull`) ở mọi unit chung. Nguồn nào lệch thì bị loại khỏi ghép cặp.

**0.2 Bảng 1: envelope theo cell.**
- Cell: T ∈ {40, 80, 150} × {none, extra-0.2, extra-0.5, missing-0.2, missing-0.5, reversed-0.2, reversed-0.5} (21 cell; cell none được thêm để đầy đủ).
- Tập baseline ứng viên: mọi baseline có row đã lưu trên realisation của grid a2:
  - `plugin`, `inflate`, `bagging`, `lp_allpast`, `ida_union`, `bvar_minnesota` (a2_baselines);
  - `pselect_union` (a2b_pselect);
  - `pselect_cal`, `bvar_cal`, `ida_cal`, `fullvar_cal` (ext_redteam_calbase);
  - `targeted_lp`, `targeted_lp_cal` (ext_tlp_eval);
  - `pselect_union_v2`, `pselect_union_v2_cal`, `bvar_minnesota_v2`, `bvar_minnesota_v2_cal` (ext_baselines2_eval);
  - `pselect_union_c2`, `ida_union_c2`, `bvar_minnesota_c2` (ext_v4c_eval);
  - `tlp2_db`, `tlp2_db_p3`, `tlp2_lp_cal` (ext_tlp2_t40/t80a/t80b/t80c/t150a/t150b/t150c/t150d; seed theo nội dung, data và skeleton trùng grid a2);
  - `pselect_union_v3`, `pselect_union_v3_cal` (ext_baselines3_eval, chỉ T80/150 missing).
- Ưu tiên nguồn: ở T80/150 missing, row mới của ext_baselines3_eval thay cho row đã lưu của `pselect_cal`, `fullvar_cal`, `targeted_lp`, `targeted_lp_cal`, `bvar_minnesota_v2_cal` (theo verifier R3-1, điểm (d)).
- Loại khỏi tập ứng viên: `oracle` (biết truth), mọi `tolerant_*` (module), `tlp2_db90` (mức danh nghĩa 90%), các baseline `_raw/_calT/_calT1` của ext_auto5_fair (chế độ không đọc stated kind, khác chế độ thông tin).
- Một ứng viên chỉ được xét ở một cell nếu có ≥ 54/60 run ok.
- X = ứng viên có IS trung bình thấp nhất trong cell. X90 = ứng viên có IS thấp nhất trong số ứng viên có coverage ≥ 0.90.
- So sánh: `tolerant_v4` − X và `tolerant_v5_1` − X; thêm `tolerant_v4` − X90 và `tolerant_v5_1` − X90 khi X90 ≠ X. Family Holm = mọi so sánh đó trên 21 cell. Việc chọn X là post hoc theo chính dữ liệu D-07, nên bảng này **mô tả**, không phải test xác nhận. Bảng 1a trích nguyên văn family ghi trước của R3-1 (results/ext_baselines3_eval) cho 4 cell T80/150 missing.
- Cột budget: số draw mỗi lần gọi theo thiết kế method (hoặc `info_n_draws` trung bình nếu row có ghi), và giây mỗi lần gọi từ results/ext_baselines3_budget/timing.json (chỉ có ở T80/150 cho các method của R3-1). Ô không đo được ghi "—".

**0.3 Bảng 2: ablation.** Method {`tolerant_v4c`, `tolerant_v5_1`, `fullvar_cal`, `pselect_cal`} − `tolerant_v4` trên 21 cell, dùng row đã lưu (ext_v4c_eval, ext_v51_eval, ext_redteam_calbase) ở mọi cell để nhất quán. Family Holm 84. Báo thêm IS và coverage từng method.

**0.4 Bảng 3: coverage theo affected / unaffected / null.**
- Nguồn pair-level: results/ext_revlag_lag/pairs.npz (oracle và `tolerant_v4`, cùng seed với a2_baselines; identity đã kiểm ở results/ext_revlag_lag/validity.txt).
- affected = non-null pair có dC ≥ 0.05; unaffected = dC < 0.05 (như revlag). oracle_cal = interval oracle nới quanh midpoint theo hệ số 1.4/1.3/1.2 ở T40/80/150 (như revlag).
- g = cov(v4) − cov(ref) trên cùng pair. CI và p: cluster bootstrap theo topology giống analyzer revlag (B = 2000, seed 20261103, ma trận trọng số chung), p hai phía = min(1, 2·min(P(boot ≤ 0), P(boot ≥ 0))), sàn 1/B.
- Family Holm riêng cho bốn nhóm: (affected, oracle_cal) 12 cell missing/reversed; (affected, oracle raw) 12 cell; (unaffected, oracle_cal) 21 cell; (unaffected, oracle raw) 21 cell.
- Null pair: coverage = Σ `n_covered_null` / Σ `n_null` từ row a2_baselines của `tolerant_v4` và `oracle`. Không có interval từng null pair của oracle, nên **không có cột oracle_cal cho null pair** và không test.

**0.5 Bảng 4: RQ4.1.** Trích từ results/ext_metrics_pairs/rq41_pairs.json (phần A, theo role): median |sai số|, median sai số tương đối, median sai số mean-lag, peak-lag hit, cho `plugin`, `tolerant_v4` và `oracle`. Không test, không đếm cell trong bảng này. Riêng khoảng cách coverage lag 0 với lag 1–2 trên cặp có cạnh bị xoá (role damaged, cell missing) của `tolerant_v4`: tính lại từ results/ext_revlag_lag/pairs.npz bằng bootstrap như 0.4, Holm trên 6 cell (T40/80/150 × missing-0.2/0.5). Số đếm báo cả thô lẫn Holm.

**0.6 Bảng 5: RQ4.2 theo interval score.** Method báo một điểm P = {`plugin`, `inflate`, `bagging`, `lp_allpast`} (a2_baselines). Module: `tolerant_v4` (a2_baselines), `tolerant_v5_1` (ext_v51_eval). Báo coverage, width (median qua run của `width_kept`), IS. So sánh v4 − P và v5_1 − P ở 21 cell (bỏ cặp nào có < 54/60 run ok). Family Holm = toàn bộ so sánh của bảng.

**0.7 Bảng 6: RQ4.4.** Trích từ results/ext_revlag_fresh/flag_eval.md, results/ext_revlag3_flagextra/flag_extra.md (mã hoá stated của vòng 2), và Holm(9) của verifier vòng 3 ở results/ext_verify3_revlag3/holm_inv_width.json. Không test mới. "GES all T" là hợp của ba tập GES theo T nên nằm ngoài family Holm(9); ghi rõ điều này.

**0.8 Những gì bảng không làm.** Không có số AUROC cho `tolerant_auto3` hay `tolerant_v5_1` (R3-9 chưa có kết quả). Không có kết quả R3-4 hợp lệ trên D-07.

---

## Kết quả

(phần dưới được viết sau khi chạy script)

Script chạy lúc 2026-11-02T07:04Z–07:30Z (sau khi băm mục 0 lúc 07:03:33Z, `results/ext_tables_main/prereg_sha256.txt`). Không có run mới. Lệnh tái lập:

```
python3 experiments/ext/tables/build_tables.py      # -> results/ext_tables_main/tables.json
python3 experiments/ext/tables/render_tables.py     # -> results/ext_tables_main/tables.md
python3 experiments/ext/tables/check_skeletons.py   # -> results/ext_tables_main/checks_skeletons.json
```

**Kiểm tra ghép cặp (mục 0.1).** Row `tolerant_v4` trùng tuyệt đối với a2_baselines ở 1260/1260 unit cho a2b_pselect, ext_redteam_calbase, ext_tlp_eval, ext_baselines2_eval, ext_v4c_eval, ext_v51_eval; 240/240 cho ext_baselines3_eval; 420/420 cho ext_tlp2_t40, 180/180 cho ext_tlp2_t80a và 60/60 cho ext_tlp2_t150a. Row `tolerant_v5_1` của ext_baselines3_eval trùng ext_v51_eval 240/240. Năm run tlp2 lọc cell (t80b, t80c, t150b, t150c, t150d) lệch 120/120 row v4. Đây là bug E1: stream bootstrap của built-in đi theo c_idx. Skeleton hỏng của mọi run này thì trùng 100% với grid a2 (`results/ext_tables_main/checks_skeletons.json`), và data trùng theo công thức seed (seed unit = seed_base + 1000 × chỉ số topology + replicate, không phụ thuộc danh sách T hay cell). Vì vậy row `tlp2_*` (seed theo nội dung) được ghép với row v4 của a2. Xem "Lệch so với định nghĩa" mục L2. Nguồn: `results/ext_tables_main/tables.json` (khoá `checks`).

---

## 1. Envelope baseline mạnh nhất theo cell, kèm compute budget

Bảng 1a là family **ghi trước** của R3-1, được trích nguyên văn. Đây là bảng chính cho claim baseline ở T ≥ 80 trên cell thiếu cạnh. Bảng 1b là envelope **post hoc** trên cả 21 cell, chỉ để mô tả. Bảng 1c ghi budget tính toán.

### Bảng 1a. Family ghi trước của R3-1 (T80/150 missing; Holm 0.05 trên 56; B = 4000)

| T | cell | v4 IS (cov) | v5_1 IS (cov) | baseline mạnh nhất X | X IS (cov) | v4 − X [95% CI] | thô/Holm | v5_1 − X [95% CI] | thô/Holm |
|---|---|---|---|---|---|---|---|---|---|
| 80 | missing-0.2 | 3.28 (0.959) | 2.84 (0.949) | pselect_union_v3_cal | 3.36 (0.936) | -0.09 [-0.27, +0.10] | T/T | -0.52 [-0.67, -0.37] | W/W |
| 80 | missing-0.5 | 3.37 (0.957) | 3.10 (0.951) | pselect_union_v3_cal | 3.40 (0.943) | -0.03 [-0.20, +0.14] | T/T | -0.30 [-0.44, -0.15] | W/W |
| 150 | missing-0.2 | 2.06 (0.968) | 1.76 (0.966) | pselect_union_v3_cal | 1.91 (0.962) | +0.15 [+0.04, +0.25] | L/T | -0.15 [-0.23, -0.07] | W/W |
| 150 | missing-0.5 | 2.22 (0.962) | 1.99 (0.968) | pselect_union_v3_cal | 2.00 (0.967) | +0.22 [+0.14, +0.30] | L/L | -0.01 [-0.08, +0.05] | T/T |

Đếm trên 28 so sánh mỗi method (7 baseline × 4 cell): v4 Holm W 19 / T 8 / L 1 (thô theo CI: W 24 / L 2); v5_1 Holm W 27 / T 1 / L 0 (thô: W 27 / L 0).

Nguồn: `results/ext_baselines3_eval/analysis.json` (khoá `result`, `verdicts`), `results/ext_baselines3_eval/rule_check.md`. Verifier vòng 3 đã tái lập toàn bộ 56 so sánh (`results/ext_verify3_baselines3/recompute_B4000.json`). Overlay Holm 0.025 với B = 4000 không bác được so sánh nào (khuyết tật analyzer đã công bố). Bản B = 20000 (mô tả) cho v4 W 19 / T 8 / L 1 và v5_1 W 27 / T 1 / L 0 ở mức 0.025: `results/ext_baselines3_eval/describe.md`.


### Bảng 1c. Compute budget mỗi lần gọi

| method | draw mỗi lần gọi | giây/lần gọi T80 | T150 |
|---|---|---|---|
| tolerant_v4 | 199 refit (repair/orientation rút lại mỗi draw) | 0.56 | 0.66 |
| tolerant_v5_1 | 199 refit (re-selection lag mỗi draw) | 1.27 | 1.44 |
| pselect_union_v3(_cal) | 16 graph, 32 orientation member × 199; trung bình 6368 (T80), 6368 (T150) | 8.34 | 11.42 |
| pselect_union_v2(_cal) | cap 4 graph; trung bình 316 / 319 / 319 draw (T40/80/150) | — | — |
| pselect_cal (đo giờ); pselect_union, pselect_union_c2 (cùng công thức, không đo) | ≤ 16 graph × max(10, 199 // số graph) | 0.28 | 0.36 |
| fullvar_cal | 199 refit | 0.51 | 0.61 |
| targeted_lp(_cal) (đo giờ); tlp2_lp_cal (cùng draw, không đo) | 199 draw VAR-sieve một tầng | 0.31 | 0.40 |
| tlp2_db_p3 (đo giờ); tlp2_db (p = 4, không đo) | MSDB 200 × 100 | 5.14 | 6.03 |
| bvar_minnesota_v2(_cal) (đo giờ); bvar_minnesota, bvar_cal, bvar_minnesota_c2 (không đo) | 199 posterior draw | 0.09 | 0.08 |
| ida_union, ida_cal, ida_union_c2 | ≤ 16 member × max(10, 199 // số member) | — | — |
| plugin, inflate, bagging | 199 (inflate dùng lại draw của plugin) | — | — |
| lp_allpast | 0 (Newey–West giải tích) | — | — |

Nguồn: giây mỗi lần gọi là median của 6 lần gọi trong một process trên D-07H development (load 5–11), lấy từ `results/ext_baselines3_budget/timing.json`. Số draw của `pselect_union_v2/v3` là trung bình `info_n_draws` trong `results/ext_baselines2_eval/runs.jsonl` và `results/ext_baselines3_eval/runs.jsonl`. Các ô "—" **không có số đo** nào trong repo (xem mục 8). Baseline mạnh nhất ở T80/150 missing dùng 6368/199 = 32 lần số draw của v5_1, và 8.34/1.27 = 6.6 lần (T80), 11.42/1.44 = 7.9 lần (T150) thời gian mỗi lần gọi.


### Bảng 1b. Envelope post hoc trên 21 cell (B = 20000; Holm 0.05 trên 44 so sánh)

| T | cell | v4 IS (cov) | v5_1 IS (cov) | X (nguồn) | X IS (cov) | budget X: draw; s/gọi | v4 − X [95% CI] | thô/Holm | v5_1 − X [95% CI] | thô/Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | none | 4.39 (0.935) | 4.37 (0.920) | bvar_minnesota_v2_cal (baselines2_eval) | 3.73 (0.920) | 199; — | +0.66 [+0.18, +1.19] | L/T | +0.64 [+0.14, +1.23] | L/T |
| 40 | extra-0.2 | 4.72 (0.912) | 4.63 (0.914) | bvar_minnesota_v2_cal (baselines2_eval) | 3.81 (0.930) | 199; — | +0.91 [+0.25, +1.76] | L/L | +0.81 [+0.22, +1.60] | L/L |
| 40 | extra-0.5 | 4.86 (0.919) | 4.81 (0.920) | bvar_minnesota_v2_cal (baselines2_eval) | 3.88 (0.929) | 199; — | +0.97 [+0.41, +1.74] | L/L | +0.93 [+0.43, +1.59] | L/L |
| 40 | missing-0.2 | 7.77 (0.983) | 4.84 (0.922) | targeted_lp_cal (tlp_eval) | 4.75 (0.953) | 199; — | +3.01 [+2.63, +3.42] | L/L | +0.08 [-0.31, +0.50] | T/T |
| 40 | missing-0.5 | 7.53 (0.978) | 5.09 (0.939) | tlp2_lp_cal (tlp2_t40) | 4.84 (0.950) | 199; — | +2.69 [+2.37, +3.02] | L/L | +0.25 [-0.02, +0.53] | T/T |
| 40 | reversed-0.2 | 4.78 (0.921) | 4.70 (0.928) | bvar_minnesota_v2_cal (baselines2_eval) | 3.98 (0.949) | 199; — | +0.80 [+0.18, +1.57] | L/T | +0.72 [+0.17, +1.39] | L/T |
| 40 | reversed-0.5 | 4.78 (0.921) | 4.74 (0.920) | bvar_minnesota_v2_cal (baselines2_eval) | 4.63 (0.903) | 199; — | +0.15 [-0.32, +0.67] | T/T | +0.12 [-0.33, +0.59] | T/T |
| 80 | none | 2.50 (0.933) | 2.53 (0.939) | bvar_minnesota_v2_cal (baselines2_eval) | 2.50 (0.922) | 199; 0.09 | +0.00 [-0.14, +0.15] | T/T | +0.04 [-0.11, +0.18] | T/T |
| 80 | extra-0.2 | 2.53 (0.946) | 2.53 (0.927) | inflate (a2_baselines) | 2.50 (0.945) | 199; — | +0.03 [-0.01, +0.08] | T/T | +0.03 [-0.04, +0.12] | T/T |
| 80 | extra-0.5 | 2.65 (0.948) | 2.67 (0.925) | inflate (a2_baselines) | 2.63 (0.942) | 199; — | +0.02 [-0.03, +0.08] | T/T | +0.04 [-0.03, +0.12] | T/T |
| 80 | missing-0.2 | 3.28 (0.959) | 2.84 (0.949) | pselect_union_v3_cal (baselines3_eval) | 3.36 (0.936) | 6368; 8.34 | -0.09 [-0.27, +0.10] | T/T | -0.52 [-0.66, -0.37] | W/W |
| 80 | missing-0.5 | 3.37 (0.957) | 3.10 (0.951) | pselect_union_v3_cal (baselines3_eval) | 3.40 (0.943) | 6368; 8.34 | -0.03 [-0.19, +0.14] | T/T | -0.30 [-0.44, -0.15] | W/W |
| 80 | reversed-0.2 | 2.79 (0.948) | 2.79 (0.941) | ida_cal (redteam_calbase) | 2.91 (0.954) | ≤16 × max(10, 199 // m); — | -0.12 [-0.24, -0.00] | W/T | -0.12 [-0.26, +0.02] | T/T |
| 80 | reversed-0.5 | 2.97 (0.929) | 3.05 (0.918) | bvar_minnesota_v2_cal (baselines2_eval) | 3.71 (0.902) | 199; 0.09 | -0.75 [-1.00, -0.52] | W/W | -0.67 [-0.93, -0.43] | W/W |
| 150 | none | 1.56 (0.964) | 1.57 (0.963) | bvar_minnesota_v2 (baselines2_eval) | 1.55 (0.939) | 199; 0.08 | +0.02 [-0.08, +0.10] | T/T | +0.03 [-0.05, +0.09] | T/T |
| 150 | extra-0.2 | 1.58 (0.965) | 1.60 (0.963) | inflate (a2_baselines) | 1.59 (0.963) | 199; — | -0.01 [-0.03, +0.01] | T/T | +0.01 [-0.01, +0.03] | T/T |
| 150 | extra-0.5 | 1.66 (0.967) | 1.68 (0.963) | inflate (a2_baselines) | 1.66 (0.964) | 199; — | +0.00 [-0.03, +0.03] | T/T | +0.02 [-0.01, +0.05] | T/T |
| 150 | missing-0.2 | 2.06 (0.968) | 1.76 (0.966) | pselect_union_v3_cal (baselines3_eval) | 1.91 (0.962) | 6368; 11.42 | +0.15 [+0.04, +0.25] | L/T | -0.15 [-0.24, -0.07] | W/W |
| 150 | missing-0.5 | 2.22 (0.962) | 1.99 (0.968) | pselect_union_v3_cal (baselines3_eval) | 2.00 (0.967) | 6368; 11.42 | +0.22 [+0.14, +0.30] | L/L | -0.01 [-0.08, +0.05] | T/T |
| 150 | reversed-0.2 | 1.89 (0.970) | 1.83 (0.959) | bagging (a2_baselines) | 2.10 (0.903) | ≤199; — | -0.21 [-0.35, -0.07] | W/W | -0.27 [-0.41, -0.15] | W/W |
| 150 | reversed-0.5 | 2.02 (0.959) | 2.03 (0.943) | bagging (a2_baselines) | 2.53 (0.866) | ≤199; — | -0.52 [-0.80, -0.26] | W/W | -0.50 [-0.74, -0.28] | W/W |
| 150 | reversed-0.5 (X90) | | | bvar_minnesota_v2_cal (baselines2_eval) | 3.05 (0.927) | 199; 0.08 | -1.03 [-1.25, -0.84] | W/W | -1.02 [-1.22, -0.83] | W/W |

Đếm (22 so sánh mỗi module: 21 cell với X, thêm 1 cell với X90): v4 thô W 5 / T 9 / L 8, Holm W 4 / T 13 / L 5; v5_1 thô W 7 / T 11 / L 4, Holm W 7 / T 13 / L 2.

Ba ứng viên có IS thấp nhất từng cell (IS, cov):

- T40 none: bvar_minnesota_v2_cal 3.73 (0.920); bvar_minnesota_v2 4.04 (0.872); bvar_minnesota_c2 4.23 (0.935) — 21 ứng viên đủ điều kiện
- T40 extra-0.2: bvar_minnesota_v2_cal 3.81 (0.930); bvar_cal 4.32 (0.933); bvar_minnesota_c2 4.32 (0.918) — 21 ứng viên đủ điều kiện
- T40 extra-0.5: bvar_minnesota_v2_cal 3.88 (0.929); bvar_cal 4.38 (0.939); bvar_minnesota_c2 4.39 (0.930) — 21 ứng viên đủ điều kiện
- T40 missing-0.2: targeted_lp_cal 4.75 (0.953); tlp2_lp_cal 4.86 (0.965); targeted_lp 5.15 (0.864) — 21 ứng viên đủ điều kiện
- T40 missing-0.5: tlp2_lp_cal 4.84 (0.950); targeted_lp_cal 5.02 (0.935); bvar_minnesota_v2_cal 5.51 (0.910) — 21 ứng viên đủ điều kiện
- T40 reversed-0.2: bvar_minnesota_v2_cal 3.98 (0.949); bvar_minnesota_v2 4.75 (0.834); bvar_minnesota_c2 4.76 (0.958) — 21 ứng viên đủ điều kiện
- T40 reversed-0.5: bvar_minnesota_v2_cal 4.63 (0.903); tlp2_lp_cal 5.31 (0.956); targeted_lp_cal 5.35 (0.953) — 21 ứng viên đủ điều kiện
- T80 none: bvar_minnesota_v2_cal 2.50 (0.922); inflate 2.50 (0.936); ida_union_c2 2.54 (0.934) — 23 ứng viên đủ điều kiện
- T80 extra-0.2: inflate 2.50 (0.945); bvar_minnesota_v2_cal 2.53 (0.941); ida_union_c2 2.54 (0.952) — 23 ứng viên đủ điều kiện
- T80 extra-0.5: inflate 2.63 (0.942); bvar_minnesota_v2_cal 2.66 (0.935); ida_cal 2.71 (0.947) — 23 ứng viên đủ điều kiện
- T80 missing-0.2: pselect_union_v3_cal 3.36 (0.936); fullvar_cal 3.44 (0.960); targeted_lp 3.46 (0.939) — 25 ứng viên đủ điều kiện
- T80 missing-0.5: pselect_union_v3_cal 3.40 (0.943); pselect_union_v3 3.58 (0.965); fullvar_cal 3.86 (0.950) — 25 ứng viên đủ điều kiện
- T80 reversed-0.2: ida_cal 2.91 (0.954); ida_union 2.92 (0.909); ida_union_c2 2.93 (0.956) — 23 ứng viên đủ điều kiện
- T80 reversed-0.5: bvar_minnesota_v2_cal 3.71 (0.902); ida_cal 3.74 (0.903); bagging 3.82 (0.819) — 23 ứng viên đủ điều kiện
- T150 none: bvar_minnesota_v2 1.55 (0.939); inflate 1.57 (0.963); plugin 1.58 (0.930) — 23 ứng viên đủ điều kiện
- T150 extra-0.2: inflate 1.59 (0.963); plugin 1.59 (0.933); bvar_minnesota_v2 1.62 (0.934) — 23 ứng viên đủ điều kiện
- T150 extra-0.5: inflate 1.66 (0.964); plugin 1.66 (0.928); bvar_minnesota_v2 1.67 (0.934) — 23 ứng viên đủ điều kiện
- T150 missing-0.2: pselect_union_v3_cal 1.91 (0.962); pselect_union_v3 2.15 (0.986); pselect_union_v2 2.15 (0.965) — 25 ứng viên đủ điều kiện
- T150 missing-0.5: pselect_union_v3_cal 2.00 (0.967); pselect_union_v2 2.29 (0.967); pselect_union_v2_cal 2.29 (0.967) — 25 ứng viên đủ điều kiện
- T150 reversed-0.2: bagging 2.10 (0.903); ida_union 2.25 (0.931); bvar_minnesota_v2_cal 2.47 (0.980) — 23 ứng viên đủ điều kiện
- T150 reversed-0.5: bagging 2.53 (0.866); bvar_minnesota_v2_cal 3.05 (0.927); pselect_union_c2 3.11 (0.942) — 23 ứng viên đủ điều kiện

Nguồn: `results/ext_tables_main/tables.json` (khoá `t1`), `results/ext_tables_main/tables.md`, số đếm theo T ở `results/ext_tables_main/t1_counts_damaged.json`. Row lấy từ `results/{a2_baselines, a2b_pselect, ext_redteam_calbase, ext_tlp_eval, ext_baselines2_eval, ext_v4c_eval, ext_v51_eval, ext_baselines3_eval, ext_tlp2_t40, ext_tlp2_t80a, ext_tlp2_t80b, ext_tlp2_t80c, ext_tlp2_t150a, ext_tlp2_t150b, ext_tlp2_t150c, ext_tlp2_t150d}/runs.jsonl`. Bốn cell T80/150 missing trùng điểm ước lượng với bảng 1a; CI lệch tối đa 0.01 vì B khác nhau.

**Đếm trên 18 damaged cell** (19 so sánh mỗi module, gồm thêm một so sánh với X90 ở T150 reversed-0.5; Holm trên family 44, tính cả cell none):
- `tolerant_v4`: thô W 5 / T 7 / L 7; Holm W 4 / T 10 / L 5. Theo cell (Holm): tốt hơn ở 3/18 (T80 reversed-0.5, T150 reversed-0.2/0.5), thua ở 5/18 (T40 extra-0.2/0.5 so với `bvar_minnesota_v2_cal`; T40 missing-0.2/0.5 so với TLP đã calibrate; T150 missing-0.5 so với `pselect_union_v3_cal`), hòa ở 10/18.
- `tolerant_v5_1`: thô W 7 / T 9 / L 3; Holm W 7 / T 10 / L 2. Theo cell (Holm): tốt hơn ở 6/18 (T80 missing-0.2/0.5, T80 reversed-0.5, T150 missing-0.2, T150 reversed-0.2/0.5), thua ở 2/18 (T40 extra-0.2/0.5, so với `bvar_minnesota_v2_cal`), hòa ở 10/18.
- Theo T (Holm): ở T40, v4 L 4/6 và v5_1 L 2/6; ở T80, v4 W 1/6, L 0 và v5_1 W 3/6, L 0; ở T150 (7 so sánh), v4 W 3, L 1 và v5_1 W 4, L 0.
- Cả 21 cell (22 so sánh): v4 thô W 5 / T 9 / L 8, Holm W 4 / T 13 / L 5; v5_1 thô W 7 / T 11 / L 4, Holm W 7 / T 13 / L 2.

**Cần đọc kèm:**
1. Chọn X theo IS thấp nhất **trên chính dữ liệu D-07** nghiêng về phía baseline (winner's curse). Kết quả vì vậy bảo thủ cho "thắng" và dễ dãi cho "thua" của module.
2. `pselect_union_v3(_cal)` (pselect đủ budget) **chỉ được chạy ở T80/150 missing**. Ở cell extra/reversed và ở T40, envelope chỉ có bản pselect thiếu budget (`pselect_union_v2`, khoảng 316–319 draw mỗi lần gọi) và bản vòng 1 (`pselect_cal`, `pselect_union`, `pselect_union_c2`). Các cell đó **chưa được so với pselect đủ budget**. `tlp2_db_p3` cũng không có ở T40.
3. Ngoài 4 cell T80/150 missing, row của `pselect_cal`, `fullvar_cal`, `bvar_cal`, `ida_cal`, `targeted_lp(_cal)` là row đã lưu từ trước khi runner đổi stream tag (B1). Đây là realisation hợp lệ (cùng data, cùng skeleton), nhưng không tái lập bit-for-bit với runner hiện tại.
4. Ở T150 reversed, X là `bagging` với coverage 0.903/0.866. Hàng X90 cho reversed-0.5 dùng `bvar_minnesota_v2_cal` (0.927).
5. Ở cell extra khi T ≥ 80, X là `inflate` hoặc `bvar_minnesota_v2_cal`, và cả hai module hòa nó (|Δ| ≤ 0.04). Ở các cell này, v4 chính là plugin được nới width, giống hệt cách làm của `inflate`.
6. Ở T40 extra, `bvar_minnesota_v2_cal` (prior Minnesota) tốt hơn cả hai module sau Holm. Đây là thất bại thật của module ở T nhỏ khi skeleton chỉ có cạnh thừa.

**Câu cho paper (exploratory, D-07 development, thay câu ở synthesis_round2 mục 2.1):**
> Ở T ≥ 80 trên cell thiếu cạnh, baseline mạnh nhất là bản pselect đủ budget do nhóm chuyển thể, `pselect_union_v3_cal` (6368 draw mỗi lần gọi, gấp 32 lần số draw và 6.6–7.9 lần thời gian của `tolerant_v5_1`). `tolerant_v5_1` có interval score thấp hơn nó, có ý nghĩa sau Holm trên 56 so sánh, ở 3/4 cell (−0.52 [−0.67, −0.37], −0.30 [−0.44, −0.15], −0.15 [−0.23, −0.07]), và hòa ở T150 missing-0.5 (−0.01 [−0.08, +0.05]). `tolerant_v4` hòa ở T80 (−0.09, −0.03) và thua ở T150 missing-0.5 (+0.22 [+0.14, +0.30]). Trên envelope post hoc của mọi baseline đã lưu, ở 18 damaged cell T = 40/80/150, `tolerant_v5_1` tốt hơn baseline mạnh nhất ở 6/18 cell, thua ở 2/18 (T40 extra-0.2/0.5, so với BVAR Minnesota đã calibrate) và hòa ở 10/18 (Holm trên 44).

Điều kiện đi kèm: "hòa/không thua" là quan sát, không phải non-inferiority có margin. Baseline mạnh nhất là bản chuyển thể của nhóm, và calibration hai phía của nó cũng do nhóm thêm vào. Mọi số chỉ là D-07 development.

---

## 2. Ablation: v4 / v4c / v5_1 / fullvar_cal / pselect_cal

Các bước của ablation:
- `fullvar_cal`: mọi lag của mọi biến cùng cạnh cùng kỳ của skeleton; không repair, không rút chiều; calibrate theo stated kind.
- `tolerant_v4`: skeleton cùng contemporaneous repair và orientation draw; mở mọi lag khi khai báo có cạnh thiếu; width calibrate một phía, frozen.
- `tolerant_v4c`: v4 với calibration hai phía (pre-scale 0.5).
- `tolerant_v5_1`: targeted lag opening đã de-dup, re-selection trong mỗi draw, cộng calibration hai phía.
- `pselect_cal`: adjacency selection của vòng 1, đã calibrate.

Ở cell missing, `fullvar_cal` − v4 tách riêng phần đóng góp của repair + orientation. Ở cell không thiếu cạnh, nó đo cái giá của việc mở mọi lag khi không cần.

### Bảng 2a. Ablation: IS (coverage) theo cell

| T | cell | v4 | v4c | v5_1 | fullvar_cal | pselect_cal |
|---|---|---|---|---|---|---|
| 40 | none | 4.39 (0.935) | 4.33 (0.923) | 4.37 (0.920) | 8.11 (0.978) | 6.61 (0.955) |
| 40 | extra-0.2 | 4.72 (0.912) | 4.59 (0.913) | 4.63 (0.914) | 8.41 (0.984) | 6.90 (0.957) |
| 40 | extra-0.5 | 4.86 (0.919) | 4.78 (0.921) | 4.81 (0.920) | 9.53 (0.984) | 6.92 (0.971) |
| 40 | missing-0.2 | 7.77 (0.983) | 6.98 (0.958) | 4.84 (0.922) | 7.84 (0.972) | 7.74 (0.965) |
| 40 | missing-0.5 | 7.53 (0.978) | 6.82 (0.956) | 5.09 (0.939) | 7.76 (0.954) | 7.46 (0.968) |
| 40 | reversed-0.2 | 4.78 (0.921) | 4.71 (0.932) | 4.70 (0.928) | 8.07 (0.977) | 7.06 (0.964) |
| 40 | reversed-0.5 | 4.78 (0.921) | 4.74 (0.931) | 4.74 (0.920) | 8.21 (0.970) | 7.09 (0.961) |
| 80 | none | 2.50 (0.933) | 2.47 (0.929) | 2.53 (0.939) | 3.14 (0.941) | 3.38 (0.940) |
| 80 | extra-0.2 | 2.53 (0.946) | 2.48 (0.940) | 2.53 (0.927) | 3.14 (0.952) | 3.39 (0.943) |
| 80 | extra-0.5 | 2.65 (0.948) | 2.67 (0.933) | 2.67 (0.925) | 3.14 (0.946) | 3.35 (0.940) |
| 80 | missing-0.2 | 3.28 (0.959) | 3.23 (0.952) | 2.84 (0.949) | 3.50 (0.963) | 3.96 (0.958) |
| 80 | missing-0.5 | 3.37 (0.957) | 3.37 (0.950) | 3.10 (0.951) | 3.82 (0.952) | 4.13 (0.941) |
| 80 | reversed-0.2 | 2.79 (0.948) | 2.78 (0.930) | 2.79 (0.941) | 3.49 (0.948) | 3.84 (0.951) |
| 80 | reversed-0.5 | 2.97 (0.929) | 3.01 (0.916) | 3.05 (0.918) | 3.89 (0.936) | 4.15 (0.933) |
| 150 | none | 1.56 (0.964) | 1.56 (0.967) | 1.57 (0.963) | 1.99 (0.971) | 2.05 (0.976) |
| 150 | extra-0.2 | 1.58 (0.965) | 1.59 (0.964) | 1.60 (0.963) | 1.97 (0.967) | 2.03 (0.977) |
| 150 | extra-0.5 | 1.66 (0.967) | 1.68 (0.961) | 1.68 (0.963) | 2.01 (0.969) | 2.00 (0.975) |
| 150 | missing-0.2 | 2.06 (0.968) | 2.04 (0.968) | 1.76 (0.966) | 2.59 (0.980) | 2.62 (0.980) |
| 150 | missing-0.5 | 2.22 (0.962) | 2.18 (0.968) | 1.99 (0.968) | 2.91 (0.961) | 2.89 (0.952) |
| 150 | reversed-0.2 | 1.89 (0.970) | 1.86 (0.966) | 1.83 (0.959) | 2.69 (0.974) | 2.68 (0.977) |
| 150 | reversed-0.5 | 2.02 (0.959) | 2.03 (0.948) | 2.03 (0.943) | 3.16 (0.947) | 3.16 (0.942) |

### Bảng 2b. Ablation: method − v4, IS [95% CI] thô/Holm (Holm trên 84)

| T | cell | v4c − v4 | v5_1 − v4 | fullvar_cal − v4 | pselect_cal − v4 |
|---|---|---|---|---|---|
| 40 | none | -0.06 [-0.14, +0.06] T/T | -0.02 [-0.16, +0.13] T/T | +3.72 [+2.92, +4.44] L/L | +2.22 [+1.60, +2.77] L/L |
| 40 | extra-0.2 | -0.14 [-0.29, -0.03] W/T | -0.10 [-0.22, +0.01] T/T | +3.69 [+2.56, +4.66] L/L | +2.18 [+1.28, +2.94] L/L |
| 40 | extra-0.5 | -0.08 [-0.25, +0.05] T/T | -0.04 [-0.17, +0.05] T/T | +4.67 [+3.52, +5.76] L/L | +2.06 [+1.32, +2.67] L/L |
| 40 | missing-0.2 | -0.79 [-0.99, -0.58] W/W | -2.93 [-3.45, -2.36] W/W | +0.07 [-0.07, +0.23] T/T | -0.02 [-0.40, +0.33] T/T |
| 40 | missing-0.5 | -0.71 [-0.88, -0.54] W/W | -2.44 [-2.85, -2.04] W/W | +0.23 [-0.04, +0.54] T/T | -0.07 [-0.46, +0.31] T/T |
| 40 | reversed-0.2 | -0.08 [-0.26, +0.06] T/T | -0.08 [-0.25, +0.06] T/T | +3.29 [+2.25, +4.17] L/L | +2.27 [+1.54, +2.90] L/L |
| 40 | reversed-0.5 | -0.04 [-0.15, +0.05] T/T | -0.04 [-0.13, +0.04] T/T | +3.43 [+2.60, +4.19] L/L | +2.31 [+1.80, +2.78] L/L |
| 80 | none | -0.03 [-0.10, +0.04] T/T | +0.03 [-0.02, +0.09] T/T | +0.64 [+0.41, +0.86] L/L | +0.88 [+0.69, +1.05] L/L |
| 80 | extra-0.2 | -0.05 [-0.11, +0.01] T/T | +0.00 [-0.06, +0.08] T/T | +0.61 [+0.37, +0.85] L/L | +0.86 [+0.70, +1.02] L/L |
| 80 | extra-0.5 | +0.02 [-0.04, +0.09] T/T | +0.02 [-0.04, +0.08] T/T | +0.49 [+0.30, +0.68] L/L | +0.70 [+0.56, +0.83] L/L |
| 80 | missing-0.2 | -0.05 [-0.10, +0.00] T/T | -0.43 [-0.54, -0.33] W/W | +0.22 [+0.12, +0.33] L/L | +0.68 [+0.49, +0.87] L/L |
| 80 | missing-0.5 | -0.00 [-0.07, +0.07] T/T | -0.27 [-0.39, -0.14] W/W | +0.45 [+0.31, +0.59] L/L | +0.76 [+0.60, +0.91] L/L |
| 80 | reversed-0.2 | -0.02 [-0.06, +0.03] T/T | +0.00 [-0.05, +0.06] T/T | +0.70 [+0.45, +0.96] L/L | +1.05 [+0.87, +1.23] L/L |
| 80 | reversed-0.5 | +0.04 [-0.04, +0.12] T/T | +0.08 [+0.01, +0.15] L/T | +0.92 [+0.70, +1.15] L/L | +1.18 [+0.97, +1.44] L/L |
| 150 | none | +0.00 [-0.02, +0.02] T/T | +0.01 [-0.02, +0.04] T/T | +0.43 [+0.31, +0.55] L/L | +0.48 [+0.37, +0.61] L/L |
| 150 | extra-0.2 | +0.01 [-0.02, +0.03] T/T | +0.02 [-0.01, +0.05] T/T | +0.39 [+0.27, +0.51] L/L | +0.45 [+0.36, +0.54] L/L |
| 150 | extra-0.5 | +0.02 [-0.01, +0.05] T/T | +0.02 [-0.00, +0.04] T/T | +0.35 [+0.26, +0.45] L/L | +0.35 [+0.26, +0.45] L/L |
| 150 | missing-0.2 | -0.02 [-0.04, +0.01] T/T | -0.30 [-0.36, -0.24] W/W | +0.53 [+0.43, +0.65] L/L | +0.56 [+0.41, +0.72] L/L |
| 150 | missing-0.5 | -0.04 [-0.07, -0.01] W/T | -0.23 [-0.30, -0.16] W/W | +0.70 [+0.58, +0.82] L/L | +0.68 [+0.54, +0.81] L/L |
| 150 | reversed-0.2 | -0.03 [-0.06, +0.00] T/T | -0.07 [-0.10, -0.03] W/W | +0.80 [+0.67, +0.94] L/L | +0.79 [+0.69, +0.90] L/L |
| 150 | reversed-0.5 | +0.01 [-0.04, +0.07] T/T | +0.02 [-0.04, +0.08] T/T | +1.15 [+0.96, +1.35] L/L | +1.14 [+0.94, +1.37] L/L |

Đếm trên 21 cell (W = method tốt hơn v4): v4c thô W 4 / T 17 / L 0, Holm W 2 / T 19 / L 0; v5_1 thô W 7 / T 13 / L 1, Holm W 7 / T 14 / L 0; fullvar_cal thô W 0 / T 2 / L 19, Holm W 0 / T 2 / L 19; pselect_cal thô W 0 / T 2 / L 19, Holm W 0 / T 2 / L 19.

Nguồn: `results/ext_tables_main/tables.json` (khoá `t2`), row từ `results/ext_v4c_eval/runs.jsonl`, `results/ext_v51_eval/runs.jsonl`, `results/ext_redteam_calbase/runs.jsonl`. Đối chiếu: v4c − v4 ở T40 missing (−0.79, −0.71) khớp `results/ext_v4c_eval/ruling.md`. v5_1 − v4 ở T40 missing (−2.93, −2.44) khớp `results/ext_v51_eval/ruling.md`. Ở T80/150 missing (−0.43, −0.27, −0.30, −0.23) khớp `results/ext_baselines3_eval/describe.md`. Ở 4 cell T80/150 missing, row đã lưu của `pselect_cal`/`fullvar_cal` lệch row mới của ext_baselines3_eval tối đa 0.08 về IS trung bình (cùng point estimate, khác draw bootstrap; caveat 2 của R3-1). Theo mục 0.3, bảng 2 dùng row đã lưu; bảng 1 dùng row mới.

**Đọc bảng (W = method tốt hơn v4):**
- **Calibration hai phía một mình** (v4c − v4): Holm W 2/21 (T40 missing-0.2/0.5), L 0/21; thô W 4/21. Nó chỉ có tác dụng ở T40 missing, đúng chỗ factor v4 bị kẹt ở sàn 1.0.
- **Targeted opening đã de-dup + calibration hai phía** (v5_1 − v4): Holm W 7/21 (6 cell missing và T150 reversed-0.2), L 0/21; thô có 1 L (T80 reversed-0.5, +0.08 [+0.01, +0.15]). Phần v5_1 hơn v4c ở cell missing (v5_1 − v4c, ghép cặp miễn phí) nằm ở `results/ext_v51fix_pairs/pairs.md`: 6/6 cell missing, Holm 6/6.
- **Repair + orientation** (`fullvar_cal` − v4): Holm L 19/21 và T 2/21 (T40 missing-0.2/0.5). Ở T80/150 missing, chênh +0.22 đến +0.70 (với row mới của R3-1, v4 − `fullvar_cal` là −0.17 đến −0.73: `results/ext_baselines3_eval/rule_check.md`). Lợi thế của v4 so với "mở mọi lag" ở cell thiếu cạnh khi T ≥ 80 vì vậy đến từ repair + orientation. Ở T40 missing thì không có lợi thế này.
- **Adjacency selection vòng 1** (`pselect_cal` − v4): Holm L 19/21, T 2/21 (T40 missing).

**Câu cho paper:**
> Trong ablation, contemporaneous repair cùng orientation draw là phần mang lợi thế của module so với việc mở mọi lag (`fullvar_cal` tệ hơn v4 ở 19/21 cell sau Holm, hòa ở T40 missing). Calibration hai phía chỉ có tác dụng ở T40 missing (−0.79, −0.71; 2/21 cell sau Holm). Targeted lag opening đã de-dup giảm IS ở cả 6 cell missing (−2.93 đến −0.23) mà không làm tệ cell nào sau Holm (0/21).

---

## 3. Coverage trên affected / unaffected / null pair, với oracle raw và oracle_cal

Cách đọc: affected = non-null pair có dC ≥ 0.05. Ở cell none/extra không có cạnh thật nào bị hỏng, nên mọi pair đều là unaffected. `oracle_cal` là oracle nới quanh midpoint bằng factor của plugin ở cell none (1.4/1.3/1.2). Cột g = cov(v4) − cov(ref) trên cùng pair; W nghĩa là v4 cover nhiều hơn, L là ít hơn.

### Bảng 3a. Coverage trên affected pair (dC ≥ 0.05), cell missing/reversed

| T | cell | n | v4 | oracle raw | oracle_cal | v4 − oracle_cal [95% CI] | thô/Holm(12) | v4 − oracle raw [95% CI] | thô/Holm(12) |
|---|---|---|---|---|---|---|---|---|---|
| 40 | missing-0.2 | 668 | 0.984 | 0.894 | 0.963 | +0.021 [+0.004, +0.040] | W/T | +0.090 [+0.067, +0.115] | W/W |
| 40 | missing-0.5 | 1303 | 0.977 | 0.882 | 0.955 | +0.021 [+0.007, +0.040] | W/W | +0.095 [+0.076, +0.118] | W/W |
| 40 | reversed-0.2 | 232 | 0.819 | 0.879 | 0.961 | -0.142 [-0.219, -0.080] | L/L | -0.060 [-0.164, +0.028] | T/T |
| 40 | reversed-0.5 | 564 | 0.867 | 0.863 | 0.931 | -0.064 [-0.099, -0.026] | L/L | +0.004 [-0.034, +0.041] | T/T |
| 80 | missing-0.2 | 668 | 0.970 | 0.918 | 0.961 | +0.009 [-0.007, +0.026] | T/T | +0.052 [+0.031, +0.070] | W/W |
| 80 | missing-0.5 | 1303 | 0.959 | 0.903 | 0.958 | +0.001 [-0.015, +0.017] | T/T | +0.056 [+0.037, +0.073] | W/W |
| 80 | reversed-0.2 | 232 | 0.862 | 0.879 | 0.944 | -0.082 [-0.108, -0.056] | L/L | -0.017 [-0.066, +0.035] | T/T |
| 80 | reversed-0.5 | 564 | 0.863 | 0.878 | 0.945 | -0.082 [-0.117, -0.050] | L/L | -0.014 [-0.055, +0.029] | T/T |
| 150 | missing-0.2 | 668 | 0.973 | 0.942 | 0.972 | +0.001 [-0.017, +0.022] | T/T | +0.031 [+0.010, +0.055] | W/W |
| 150 | missing-0.5 | 1303 | 0.965 | 0.943 | 0.976 | -0.012 [-0.025, +0.004] | T/T | +0.021 [+0.004, +0.040] | W/T |
| 150 | reversed-0.2 | 232 | 0.909 | 0.957 | 0.978 | -0.069 [-0.106, -0.037] | L/L | -0.047 [-0.089, -0.008] | L/T |
| 150 | reversed-0.5 | 564 | 0.906 | 0.947 | 0.970 | -0.064 [-0.092, -0.038] | L/L | -0.041 [-0.066, -0.018] | L/L |

Đếm (W = v4 cover nhiều hơn, L = ít hơn): affected|ocal: thô W 2 / T 4 / L 6, Holm W 1 / T 5 / L 6; affected|oraw: thô W 6 / T 4 / L 2, Holm W 5 / T 6 / L 1.

### Bảng 3b. Coverage trên unaffected pair (dC < 0.05)

| T | cell | n | v4 | oracle raw | oracle_cal | v4 − oracle_cal [95% CI] | thô/Holm(21) | v4 − oracle raw [95% CI] | thô/Holm(21) |
|---|---|---|---|---|---|---|---|---|---|
| 40 | none | 1854 | 0.935 | 0.880 | 0.952 | -0.017 [-0.037, +0.000] | T/T | +0.055 [+0.035, +0.070] | W/W |
| 40 | extra-0.2 | 1854 | 0.912 | 0.880 | 0.952 | -0.040 [-0.066, -0.019] | L/L | +0.032 [+0.008, +0.051] | W/W |
| 40 | extra-0.5 | 1854 | 0.919 | 0.880 | 0.952 | -0.033 [-0.058, -0.011] | L/T | +0.039 [+0.014, +0.060] | W/W |
| 40 | missing-0.2 | 1186 | 0.982 | 0.872 | 0.946 | +0.036 [+0.015, +0.063] | W/W | +0.110 [+0.090, +0.133] | W/W |
| 40 | missing-0.5 | 551 | 0.982 | 0.875 | 0.944 | +0.038 [+0.012, +0.065] | W/T | +0.107 [+0.078, +0.135] | W/W |
| 40 | reversed-0.2 | 1622 | 0.935 | 0.880 | 0.951 | -0.015 [-0.033, +0.001] | T/T | +0.055 [+0.038, +0.069] | W/W |
| 40 | reversed-0.5 | 1290 | 0.945 | 0.887 | 0.961 | -0.016 [-0.032, +0.001] | T/T | +0.058 [+0.038, +0.077] | W/W |
| 80 | none | 1854 | 0.933 | 0.899 | 0.955 | -0.023 [-0.041, -0.008] | L/L | +0.033 [+0.014, +0.050] | W/W |
| 80 | extra-0.2 | 1854 | 0.946 | 0.899 | 0.955 | -0.009 [-0.026, +0.005] | T/T | +0.047 [+0.029, +0.064] | W/W |
| 80 | extra-0.5 | 1854 | 0.948 | 0.899 | 0.955 | -0.008 [-0.026, +0.008] | T/T | +0.049 [+0.028, +0.065] | W/W |
| 80 | missing-0.2 | 1186 | 0.953 | 0.889 | 0.952 | +0.001 [-0.012, +0.014] | T/T | +0.064 [+0.046, +0.088] | W/W |
| 80 | missing-0.5 | 551 | 0.953 | 0.891 | 0.949 | +0.004 [-0.019, +0.028] | T/T | +0.062 [+0.029, +0.100] | W/W |
| 80 | reversed-0.2 | 1622 | 0.961 | 0.902 | 0.957 | +0.004 [-0.011, +0.016] | T/T | +0.059 [+0.045, +0.070] | W/W |
| 80 | reversed-0.5 | 1290 | 0.958 | 0.909 | 0.960 | -0.002 [-0.015, +0.012] | T/T | +0.050 [+0.033, +0.066] | W/W |
| 150 | none | 1854 | 0.964 | 0.943 | 0.975 | -0.011 [-0.025, +0.005] | T/T | +0.021 [+0.006, +0.038] | W/W |
| 150 | extra-0.2 | 1854 | 0.965 | 0.943 | 0.975 | -0.010 [-0.023, +0.005] | T/T | +0.022 [+0.008, +0.037] | W/W |
| 150 | extra-0.5 | 1854 | 0.967 | 0.943 | 0.975 | -0.009 [-0.023, +0.007] | T/T | +0.023 [+0.008, +0.039] | W/W |
| 150 | missing-0.2 | 1186 | 0.965 | 0.944 | 0.977 | -0.013 [-0.024, -0.001] | L/T | +0.020 [+0.006, +0.036] | W/W |
| 150 | missing-0.5 | 551 | 0.956 | 0.944 | 0.973 | -0.016 [-0.035, +0.002] | T/T | +0.013 [-0.011, +0.037] | T/T |
| 150 | reversed-0.2 | 1622 | 0.978 | 0.941 | 0.975 | +0.004 [-0.010, +0.020] | T/T | +0.037 [+0.023, +0.053] | W/W |
| 150 | reversed-0.5 | 1290 | 0.982 | 0.942 | 0.978 | +0.005 [-0.005, +0.015] | T/T | +0.040 [+0.027, +0.055] | W/W |

Đếm: unaffected|ocal: thô W 2 / T 15 / L 4, Holm W 1 / T 18 / L 2; unaffected|oraw: thô W 20 / T 1 / L 0, Holm W 20 / T 1 / L 0.

### Bảng 3c. Null pair (|C| ≤ 0.1): tỷ lệ interval chứa 0 và IS trung bình

| T | cell | n | v4 chứa 0 | oracle raw chứa 0 | v4 IS null | oracle raw IS null |
|---|---|---|---|---|---|---|
| 40 | none | 9066 | 0.9964 | 0.9996 | 1.89 | 0.0031 |
| 40 | extra-0.2 | 9066 | 0.9927 | 0.9996 | 1.95 | 0.0031 |
| 40 | extra-0.5 | 9066 | 0.9927 | 0.9996 | 2.28 | 0.0031 |
| 40 | missing-0.2 | 9066 | 0.9819 | 0.9996 | 4.78 | 0.0031 |
| 40 | missing-0.5 | 9066 | 0.9885 | 0.9996 | 4.85 | 0.0031 |
| 40 | reversed-0.2 | 9066 | 0.9980 | 0.9996 | 1.93 | 0.0031 |
| 40 | reversed-0.5 | 9066 | 0.9983 | 0.9996 | 1.99 | 0.0031 |
| 80 | none | 9066 | 0.9951 | 0.9986 | 0.87 | 0.0024 |
| 80 | extra-0.2 | 9066 | 0.9944 | 0.9986 | 0.97 | 0.0024 |
| 80 | extra-0.5 | 9066 | 0.9917 | 0.9986 | 1.14 | 0.0024 |
| 80 | missing-0.2 | 9066 | 0.9925 | 0.9986 | 2.03 | 0.0024 |
| 80 | missing-0.5 | 9066 | 0.9927 | 0.9986 | 2.08 | 0.0024 |
| 80 | reversed-0.2 | 9066 | 0.9982 | 0.9986 | 0.96 | 0.0024 |
| 80 | reversed-0.5 | 9066 | 0.9981 | 0.9986 | 0.96 | 0.0024 |
| 150 | none | 9066 | 0.9864 | 0.9986 | 0.56 | 0.0013 |
| 150 | extra-0.2 | 9066 | 0.9859 | 0.9986 | 0.62 | 0.0013 |
| 150 | extra-0.5 | 9066 | 0.9863 | 0.9986 | 0.73 | 0.0013 |
| 150 | missing-0.2 | 9066 | 0.9805 | 0.9986 | 1.32 | 0.0013 |
| 150 | missing-0.5 | 9066 | 0.9805 | 0.9986 | 1.36 | 0.0013 |
| 150 | reversed-0.2 | 9066 | 0.9949 | 0.9986 | 0.65 | 0.0013 |
| 150 | reversed-0.5 | 9066 | 0.9962 | 0.9986 | 0.66 | 0.0013 |

Nguồn: `results/ext_tables_main/tables.json` (khoá `t3`), tính từ `results/ext_revlag_lag/pairs.npz` (pair-level, cùng seed với a2_baselines; identity ở `results/ext_revlag_lag/validity.txt`) và `results/ext_revlag_lag/nullpairs.jsonl` (bảng 3c). Đối chiếu: 6 cell reversed và 6 cell missing của bảng 3a khớp từng số với `results/ext_revlag_lag/analysis_a.md` (θ = 0.05; ví dụ T80 reversed-0.2: 0.862 / 0.944, g −0.082 [−0.108, −0.056]). Tỷ lệ false signal (1 − cột "chứa 0") khớp phần D của `results/ext_metrics_pairs/rq41_pairs.md` trong sai số làm tròn.

**Đọc bảng:**
- **Affected, so với oracle_cal:** v4 cover ít hơn ở 6/12 cell, thô và Holm(12), gồm cả 6 cell reversed (−0.142 đến −0.064). v4 cover nhiều hơn ở T40 missing (thô 2/12, Holm 1/12). Ở T ≥ 80 missing là hòa (4/4).
- **Affected, so với oracle raw:** v4 cover nhiều hơn ở 6/12 cell thô (mọi cell missing), Holm 5/12. v4 cover ít hơn ở T150 reversed: thô 2/12, Holm 1/12 (reversed-0.5).
- **Unaffected:** so với oracle_cal, thô W 2 / T 15 / L 4 và Holm W 1 / T 18 / L 2 (L ở T40 extra-0.2 và T80 none). So với oracle raw, v4 cover nhiều hơn ở 20/21 cell, thô và Holm.
- **Null pair:** interval của v4 chứa 0 ở 0.9805–0.9983 null pair, của oracle raw ở 0.9986–0.9996. IS trung bình trên null pair của v4 là 0.56–4.85, của oracle ≈ 0 (0.0013–0.0031), vì oracle biết các cặp không nối. Không có cột oracle_cal cho null pair (mục 0.4).

**Câu cho paper (X1, giữ như synthesis vòng 2, thêm phần unaffected/null):**
> Trên các pair bị ảnh hưởng bởi cạnh đảo (dC ≥ 0.05), `tolerant_v4` cover 0.82–0.87 ở T ≤ 80 và 0.91 ở T150, so với 0.93–0.98 của một oracle biết hướng đúng được widen về cùng mức width (thấp hơn có ý nghĩa ở 6/6 cell reversed sau Holm). Trên pair không bị ảnh hưởng, v4 ngang oracle cùng mức width (18/21 cell hòa sau Holm). Trên pair bị ảnh hưởng bởi cạnh thiếu, v4 ngang hoặc cao hơn oracle đó. Chưa test xong xem gap ở cạnh đảo có giảm được bằng cách xử lý reversal tốt hơn hay không.

Về R3-4: chưa có kết quả hợp lệ (`docs/ext/revlag3.md`). Verifier vòng 3 có một phân tích post hoc trên bản sao của run không hợp lệ (dùng truth, không có CI): ở cùng mức coverage tổng thể, `tolerant_v4R` tăng coverage affected +0.034 (rev-0.2, T80) và +0.039 (rev-0.2, T150) (`results/ext_verify3_revlag3/matched_width_d07.json`). Không được trích số này như kết quả.

---

## 4. RQ4.1: đặc trưng sai số (strength tuyệt đối và tương đối, lag)

Cách đọc:
- `abs` = median |Ĉ − C|; `rel` = median |Ĉ − C|/|C|.
- `mean-lag` = median |sai số mean lag|; `peak` = tỷ lệ peak lag đúng trong số pair giữ lại.
- Role: damaged = pair có cạnh trực tiếp bị hỏng; downstream = pair có đường đi qua cạnh hỏng; untouched = còn lại (chỉ ghi ở cell none).
- Bảng này chỉ mô tả, không test.

### Bảng 4a. RQ4.1: sai số cường độ và độ trễ theo role (pair-level, median trên pair)

| T | cell | role | n | abs plugin | abs v4 | abs oracle | rel plugin | rel v4 | mean-lag plugin | mean-lag v4 | mean-lag oracle | peak plugin | peak v4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | none | untouched | 1854 | 0.423 | 0.423 | 0.260 | 0.396 | 0.396 | 0.318 | 0.318 | 0.108 | 0.619 | 0.619 |
| 40 | extra-0.2 | damaged | 37 | 0.409 | 0.409 | 0.135 | 0.844 | 0.844 | 0.615 | 0.615 | 0.075 | 0.459 | 0.459 |
| 40 | extra-0.2 | downstream | 475 | 0.493 | 0.493 | 0.265 | 0.490 | 0.490 | 0.365 | 0.365 | 0.102 | 0.602 | 0.602 |
| 40 | extra-0.5 | damaged | 87 | 0.434 | 0.434 | 0.162 | 0.862 | 0.862 | 0.528 | 0.528 | 0.062 | 0.333 | 0.333 |
| 40 | extra-0.5 | downstream | 857 | 0.543 | 0.543 | 0.269 | 0.517 | 0.517 | 0.381 | 0.381 | 0.109 | 0.547 | 0.547 |
| 40 | missing-0.2 | damaged | 239 | 1.259 | 0.776 | 0.326 | 1.000 | 0.626 | 0.920 | 0.374 | 0.143 | 0.165 | 0.356 |
| 40 | missing-0.2 | downstream | 461 | 0.692 | 0.902 | 0.234 | 0.961 | 1.030 | 0.386 | 0.533 | 0.064 | 0.456 | 0.323 |
| 40 | missing-0.5 | damaged | 655 | 1.342 | 0.871 | 0.319 | 1.000 | 0.602 | 1.191 | 0.378 | 0.139 | 0.117 | 0.383 |
| 40 | missing-0.5 | downstream | 665 | 0.701 | 0.852 | 0.206 | 1.000 | 1.059 | 0.390 | 0.530 | 0.062 | 0.426 | 0.313 |
| 40 | reversed-0.2 | damaged | 73 | 0.901 | 0.847 | 0.340 | 0.735 | 0.704 | 0.937 | 0.937 | 0.194 | 0.027 | 0.027 |
| 40 | reversed-0.2 | downstream | 166 | 0.654 | 0.630 | 0.259 | 0.687 | 0.655 | 0.403 | 0.403 | 0.110 | 0.482 | 0.482 |
| 40 | reversed-0.5 | damaged | 193 | 0.970 | 0.720 | 0.337 | 0.716 | 0.580 | 0.998 | 0.998 | 0.210 | 0.016 | 0.016 |
| 40 | reversed-0.5 | downstream | 389 | 0.701 | 0.614 | 0.261 | 0.795 | 0.666 | 0.405 | 0.405 | 0.104 | 0.447 | 0.447 |
| 80 | none | untouched | 1854 | 0.270 | 0.270 | 0.176 | 0.249 | 0.249 | 0.227 | 0.227 | 0.081 | 0.728 | 0.728 |
| 80 | extra-0.2 | damaged | 37 | 0.335 | 0.335 | 0.134 | 0.595 | 0.595 | 0.493 | 0.493 | 0.045 | 0.459 | 0.459 |
| 80 | extra-0.2 | downstream | 475 | 0.296 | 0.296 | 0.189 | 0.291 | 0.291 | 0.264 | 0.264 | 0.085 | 0.743 | 0.743 |
| 80 | extra-0.5 | damaged | 87 | 0.271 | 0.271 | 0.131 | 0.437 | 0.437 | 0.439 | 0.439 | 0.054 | 0.506 | 0.506 |
| 80 | extra-0.5 | downstream | 857 | 0.337 | 0.337 | 0.186 | 0.303 | 0.303 | 0.257 | 0.257 | 0.081 | 0.679 | 0.679 |
| 80 | missing-0.2 | damaged | 239 | 1.256 | 0.451 | 0.186 | 1.000 | 0.344 | 0.939 | 0.233 | 0.096 | 0.137 | 0.628 |
| 80 | missing-0.2 | downstream | 461 | 0.569 | 0.440 | 0.157 | 0.907 | 0.479 | 0.304 | 0.349 | 0.051 | 0.472 | 0.477 |
| 80 | missing-0.5 | damaged | 655 | 1.315 | 0.484 | 0.199 | 1.000 | 0.362 | 1.041 | 0.243 | 0.103 | 0.100 | 0.620 |
| 80 | missing-0.5 | downstream | 665 | 0.639 | 0.405 | 0.141 | 1.000 | 0.497 | 0.337 | 0.350 | 0.045 | 0.476 | 0.492 |
| 80 | reversed-0.2 | damaged | 73 | 0.823 | 0.728 | 0.220 | 0.617 | 0.515 | 0.926 | 0.926 | 0.160 | 0.027 | 0.027 |
| 80 | reversed-0.2 | downstream | 166 | 0.503 | 0.456 | 0.208 | 0.513 | 0.501 | 0.357 | 0.357 | 0.091 | 0.518 | 0.518 |
| 80 | reversed-0.5 | damaged | 193 | 0.878 | 0.581 | 0.247 | 0.656 | 0.452 | 0.849 | 0.849 | 0.176 | 0.047 | 0.047 |
| 80 | reversed-0.5 | downstream | 389 | 0.563 | 0.462 | 0.191 | 0.628 | 0.510 | 0.343 | 0.343 | 0.084 | 0.488 | 0.488 |
| 150 | none | untouched | 1854 | 0.178 | 0.178 | 0.124 | 0.161 | 0.161 | 0.163 | 0.163 | 0.054 | 0.818 | 0.818 |
| 150 | extra-0.2 | damaged | 37 | 0.196 | 0.196 | 0.065 | 0.310 | 0.310 | 0.350 | 0.350 | 0.015 | 0.730 | 0.730 |
| 150 | extra-0.2 | downstream | 475 | 0.196 | 0.196 | 0.123 | 0.190 | 0.190 | 0.173 | 0.173 | 0.049 | 0.821 | 0.821 |
| 150 | extra-0.5 | damaged | 87 | 0.203 | 0.203 | 0.076 | 0.363 | 0.363 | 0.291 | 0.291 | 0.021 | 0.667 | 0.667 |
| 150 | extra-0.5 | downstream | 857 | 0.209 | 0.209 | 0.129 | 0.188 | 0.188 | 0.183 | 0.183 | 0.055 | 0.789 | 0.789 |
| 150 | missing-0.2 | damaged | 239 | 1.261 | 0.248 | 0.141 | 1.000 | 0.190 | 1.085 | 0.182 | 0.071 | 0.126 | 0.720 |
| 150 | missing-0.2 | downstream | 461 | 0.461 | 0.268 | 0.122 | 0.865 | 0.301 | 0.259 | 0.250 | 0.035 | 0.549 | 0.625 |
| 150 | missing-0.5 | damaged | 655 | 1.326 | 0.269 | 0.145 | 1.000 | 0.209 | 0.872 | 0.176 | 0.077 | 0.147 | 0.704 |
| 150 | missing-0.5 | downstream | 665 | 0.597 | 0.239 | 0.094 | 1.000 | 0.301 | 0.265 | 0.263 | 0.030 | 0.541 | 0.627 |
| 150 | reversed-0.2 | damaged | 73 | 0.687 | 0.594 | 0.139 | 0.558 | 0.446 | 0.946 | 0.946 | 0.143 | 0.014 | 0.014 |
| 150 | reversed-0.2 | downstream | 166 | 0.443 | 0.377 | 0.140 | 0.458 | 0.413 | 0.279 | 0.279 | 0.051 | 0.560 | 0.560 |
| 150 | reversed-0.5 | damaged | 193 | 0.800 | 0.453 | 0.146 | 0.606 | 0.325 | 0.861 | 0.861 | 0.137 | 0.052 | 0.052 |
| 150 | reversed-0.5 | downstream | 389 | 0.463 | 0.349 | 0.127 | 0.575 | 0.387 | 0.330 | 0.330 | 0.057 | 0.535 | 0.535 |

Nguồn: `results/ext_metrics_pairs/rq41_pairs.json` (khoá `role|T|kind|rate|role|method`), bản đọc được ở `results/ext_metrics_pairs/rq41_pairs.md` phần A. Pair-level rerun khớp a2_baselines/a2b_pselect tuyệt đối (`results/ext_metrics_pairs/check.txt`). Bản sao đã render: `results/ext_tables_main/tables.md`.


### Bảng 4b. Coverage của v4 trên cặp có cạnh bị xoá: lag 0 so với lag 1–2

| T | cell | cov lag 0 (n) | cov lag 1–2 (n) | lag0 − lag12 [95% CI] | p hai phía | thô/Holm(6) |
|---|---|---|---|---|---|---|
| 40 | missing-0.2 | 0.962 (79) | 0.981 (160) | -0.019 [-0.057, +0.017] | 0.312 | T/T |
| 40 | missing-0.5 | 0.943 (193) | 0.978 (462) | -0.035 [-0.072, -0.001] | 0.041 | L/T |
| 80 | missing-0.2 | 0.924 (79) | 0.969 (160) | -0.045 [-0.143, +0.024] | 0.291 | T/T |
| 80 | missing-0.5 | 0.912 (193) | 0.961 (462) | -0.049 [-0.096, -0.007] | 0.019 | L/T |
| 150 | missing-0.2 | 0.949 (79) | 0.956 (160) | -0.007 [-0.055, +0.035] | 0.804 | T/T |
| 150 | missing-0.5 | 0.938 (193) | 0.970 (462) | -0.032 [-0.059, -0.005] | 0.013 | L/T |

Đếm (L = lag 0 cover kém hơn có ý nghĩa): thô L 3 / T 3, Holm L 0 / T 6.

Nguồn: `results/ext_tables_main/tables.json` (khoá `t4_lag0`), tính từ `results/ext_revlag_lag/pairs.npz`. Điểm ước lượng khớp phần C của `results/ext_metrics_pairs/rq41_pairs.md`. CI lệch ≤ 0.004 do seed bootstrap khác.

**Bảng 4c. Lag output dưới reversal: `tolerant_v4L` so với `tolerant_v4`** (trích; damaged pair, cell reversed)

| T | cell | n | peak hit v4 | peak hit v4L | Δ [95% CI] | p Holm(4) | run fresh (seed 30261102) |
|---|---|---|---|---|---|---|---|
| 80 | reversed-0.2 | 73 | 0.027 | 0.110 | +0.082 [+0.026, +0.154] | 0.0020 | không tái lập: +0.026 [0.000, 0.066], Holm p 0.128 |
| 150 | reversed-0.2 | 73 | 0.014 | 0.123 | +0.110 [+0.041, +0.188] | 0.0020 | — |
| 80 | reversed-0.5 | 193 | 0.047 | 0.347 | +0.301 [+0.231, +0.373] | 0.0020 | — |
| 150 | reversed-0.5 | 193 | 0.052 | 0.321 | +0.269 [+0.205, +0.345] | 0.0020 | — |

Nguồn: `results/ext_revlag_lag/analysis_b.md` (L1, L2; mean-lag error của damaged pair ở phần "Báo kèm"), `results/ext_revlag_fresh/analysis_b.md` (L1 trên run fresh: 3/4, KHÔNG ĐẠT), `results/ext_verify2_revlag/recheck_bc.md`. L2: 0/21 cell tệ hơn, thô và Holm. Lag interval của v4L cover 0.66–0.76 (`results/ext_revlag_lag/analysis_b.md`, cột cuối), nên không được báo như interval trung thực.

**Đọc bảng 4:**
- **Cạnh thiếu, cách báo một điểm (plugin):** trên damaged pair, abs 1.256–1.342 và rel 1.000 ở mọi T, vì hiệu ứng mất đường đi bị báo bằng 0. Mean-lag error 0.872–1.191 so với 0.163–0.318 trên untouched pair ở cell none. Sai số này **không giảm theo T**.
- **Module (v4) trên damaged pair của cell missing:** abs giảm theo T, 0.776/0.871 (T40), 0.451/0.484 (T80), 0.248/0.269 (T150). Mean-lag error 0.176–0.378 và peak hit 0.356–0.720.
- **Cái giá ở T40:** trên downstream pair của cell missing ở T40, abs của v4 lớn hơn plugin (0.902 so với 0.692; 0.852 so với 0.701). Từ T80, v4 thấp hơn.
- **Cạnh đảo:** lag output của v4 trùng plugin (mean-lag 0.849–0.998, peak hit 0.014–0.052 trên damaged pair), vì không có repair candidate. Strength error của v4 thấp hơn plugin (abs 0.453–0.847 so với 0.687–0.970). Báo lag từ structural draws (v4L) nâng peak hit lên 0.110–0.347 (bảng 4c), vẫn xa oracle.
- **Cạnh thừa:** v4 trùng plugin về điểm ước lượng (cùng fit, chỉ khác width). Sai số trên damaged pair chủ yếu nằm ở rel (0.310–0.862) và lag (0.291–0.615), giảm theo T.
- **Lag 0 so với lag 1–2 trên cạnh bị xoá (bảng 4b):** chênh −0.007 đến −0.049. CI loại 0 ở 3/6 cell thô (2/4 ở T ≥ 80), **0/6 sau Holm**. Câu "v4 cover pair lag 0 bị xoá kém hơn khoảng 0.03–0.05" chỉ được viết kèm "không có ý nghĩa sau Holm".

---

## 5. RQ4.2 phát biểu lại theo interval score

Plan hỏi: interval gộp bất định cấu trúc có độ phủ đúng mức danh nghĩa và **hẹp hơn** cách báo một điểm không. Bảng 5a cho thấy module **rộng hơn** plugin ở mọi cell (tỷ số median width v4/plugin 1.20–3.61; mô tả, không test), vì plugin under-cover nặng. RQ4.2 vì vậy phải phát biểu lại: ở coverage ≥ 0.90, module có interval score thấp hơn cách báo một điểm không.

### Bảng 5a. RQ4.2: coverage / median width / IS

| T | cell | oracle | plugin | inflate | bagging | lp_allpast | v4 | v5_1 |
|---|---|---|---|---|---|---|---|---|
| 40 | none | 0.880 / 1.47 / 2.72 | 0.862 / 2.14 / 4.74 | 0.934 / 2.99 / 4.43 | 0.858 / 2.10 / 4.74 | — | 0.935 / 2.96 / 4.39 | 0.920 / 2.77 / 4.37 |
| 40 | extra-0.2 | 0.880 / 1.47 / 2.72 | 0.846 / 2.19 / 5.22 | 0.930 / 3.06 / 4.67 | 0.890 / 2.70 / 4.68 | — | 0.912 / 2.91 / 4.72 | 0.914 / 2.91 / 4.63 |
| 40 | extra-0.5 | 0.880 / 1.47 / 2.72 | 0.853 / 2.49 / 5.24 | 0.924 / 3.24 / 4.71 | 0.900 / 2.95 / 4.78 | — | 0.919 / 3.20 / 4.86 | 0.920 / 3.21 / 4.81 |
| 40 | missing-0.2 | 0.880 / 1.47 / 2.72 | 0.654 / 1.85 / 11.80 | 0.918 / 15.74 / 19.82 | 0.702 / 1.98 / 9.91 | — | 0.983 / 6.60 / 7.77 | 0.922 / 3.29 / 4.84 |
| 40 | missing-0.5 | 0.880 / 1.47 / 2.72 | 0.353 / 1.79 / 28.21 | 0.543 / 16.27 / 31.24 | 0.526 / 2.13 / 15.73 | — | 0.978 / 6.45 / 7.53 | 0.939 / 3.79 / 5.09 |
| 40 | reversed-0.2 | 0.880 / 1.47 / 2.72 | 0.823 / 2.19 / 5.86 | 0.926 / 3.50 / 5.12 | 0.841 / 2.22 / 5.33 | — | 0.921 / 3.11 / 4.78 | 0.928 / 3.10 / 4.70 |
| 40 | reversed-0.5 | 0.880 / 1.47 / 2.72 | 0.780 / 2.11 / 7.06 | 0.926 / 3.80 / 5.71 | 0.829 / 2.30 / 5.54 | — | 0.921 / 3.21 / 4.78 | 0.920 / 3.28 / 4.74 |
| 80 | none | 0.899 / 1.03 / 1.68 | 0.869 / 1.43 / 2.78 | 0.936 / 1.85 / 2.50 | 0.872 / 1.40 / 2.76 | 0.839 / 2.59 / 5.70 | 0.933 / 1.83 / 2.50 | 0.939 / 1.85 / 2.53 |
| 80 | extra-0.2 | 0.899 / 1.03 / 1.68 | 0.883 / 1.43 / 2.73 | 0.945 / 1.86 / 2.50 | 0.912 / 2.05 / 3.12 | 0.835 / 2.59 / 5.79 | 0.946 / 1.86 / 2.53 | 0.927 / 1.73 / 2.53 |
| 80 | extra-0.5 | 0.899 / 1.03 / 1.68 | 0.880 / 1.54 / 2.89 | 0.942 / 2.00 / 2.63 | 0.913 / 2.12 / 3.35 | 0.836 / 2.56 / 5.75 | 0.948 / 1.99 / 2.65 | 0.925 / 1.88 / 2.67 |
| 80 | missing-0.2 | 0.899 / 1.03 / 1.68 | 0.647 / 1.32 / 11.68 | 0.893 / 11.70 / 15.73 | 0.672 / 1.35 / 10.20 | 0.836 / 2.60 / 5.69 | 0.959 / 2.59 / 3.28 | 0.949 / 2.19 / 2.84 |
| 80 | missing-0.5 | 0.899 / 1.03 / 1.68 | 0.337 / 1.30 / 28.78 | 0.507 / 11.02 / 28.79 | 0.434 / 1.46 / 19.91 | 0.838 / 2.59 / 5.72 | 0.957 / 2.69 / 3.37 | 0.951 / 2.42 / 3.10 |
| 80 | reversed-0.2 | 0.899 / 1.03 / 1.68 | 0.820 / 1.40 / 3.80 | 0.943 / 2.24 / 3.04 | 0.849 / 1.47 / 3.22 | 0.827 / 2.68 / 6.22 | 0.948 / 2.12 / 2.79 | 0.941 / 2.05 / 2.79 |
| 80 | reversed-0.5 | 0.899 / 1.03 / 1.68 | 0.740 / 1.41 / 5.75 | 0.941 / 3.09 / 4.02 | 0.819 / 1.54 / 3.82 | 0.807 / 2.81 / 7.54 | 0.929 / 2.08 / 2.97 | 0.918 / 2.03 / 3.05 |
| 150 | none | 0.943 / 0.78 / 1.02 | 0.930 / 1.07 / 1.58 | 0.963 / 1.28 / 1.57 | 0.931 / 1.06 / 1.58 | 0.908 / 1.63 / 2.66 | 0.964 / 1.28 / 1.56 | 0.963 / 1.26 / 1.57 |
| 150 | extra-0.2 | 0.943 / 0.78 / 1.02 | 0.933 / 1.07 / 1.59 | 0.963 / 1.29 / 1.59 | 0.962 / 1.85 / 2.32 | 0.908 / 1.63 / 2.67 | 0.965 / 1.33 / 1.58 | 0.963 / 1.34 / 1.60 |
| 150 | extra-0.5 | 0.943 / 0.78 / 1.02 | 0.928 / 1.13 / 1.66 | 0.964 / 1.36 / 1.66 | 0.954 / 1.97 / 2.53 | 0.907 / 1.66 / 2.69 | 0.967 / 1.38 / 1.66 | 0.963 / 1.37 / 1.68 |
| 150 | missing-0.2 | 0.943 / 0.78 / 1.02 | 0.656 / 0.99 / 11.47 | 0.864 / 8.29 / 13.17 | 0.671 / 1.01 / 10.28 | 0.902 / 1.64 / 2.74 | 0.968 / 1.69 / 2.06 | 0.966 / 1.46 / 1.76 |
| 150 | missing-0.5 | 0.943 / 0.78 / 1.02 | 0.328 / 1.00 / 29.07 | 0.489 / 8.96 / 28.34 | 0.386 / 1.09 / 22.19 | 0.900 / 1.63 / 2.88 | 0.962 / 1.76 / 2.22 | 0.968 / 1.60 / 1.99 |
| 150 | reversed-0.2 | 0.943 / 0.78 / 1.02 | 0.858 / 1.07 / 2.96 | 0.965 / 2.04 / 2.58 | 0.903 / 1.16 / 2.10 | 0.880 / 1.77 / 3.51 | 0.970 / 1.53 / 1.89 | 0.959 / 1.44 / 1.83 |
| 150 | reversed-0.5 | 0.943 / 0.78 / 1.02 | 0.743 / 1.07 / 5.12 | 0.946 / 2.67 / 3.40 | 0.866 / 1.16 / 2.53 | 0.838 / 1.80 / 4.74 | 0.959 / 1.58 / 2.02 | 0.943 / 1.49 / 2.03 |

### Bảng 5b. RQ4.2: module − method báo một điểm, IS [95% CI] thô/Holm (Holm trên 154)

| T | cell | v4 − plugin | v4 − inflate | v4 − bagging | v4 − lp_allpast | v5_1 − inflate |
|---|---|---|---|---|---|---|
| 40 | none | -0.35 [-0.91, +0.09] T/T | -0.03 [-0.18, +0.08] T/T | -0.35 [-0.85, +0.05] T/T | — | -0.05 [-0.15, +0.05] T/T |
| 40 | extra-0.2 | -0.49 [-0.95, -0.11] W/T | +0.05 [-0.06, +0.17] T/T | +0.04 [-0.15, +0.23] T/T | — | -0.05 [-0.12, +0.03] T/T |
| 40 | extra-0.5 | -0.38 [-0.69, -0.11] W/T | +0.15 [+0.01, +0.35] L/T | +0.08 [-0.21, +0.45] T/T | — | +0.10 [+0.02, +0.19] L/T |
| 40 | missing-0.2 | -4.04 [-5.20, -2.86] W/W | -12.05 [-13.24, -11.02] W/W | -2.14 [-3.29, -1.03] W/W | — | -14.98 [-16.19, -13.82] W/W |
| 40 | missing-0.5 | -20.68 [-22.35, -18.96] W/W | -23.71 [-25.58, -21.95] W/W | -8.20 [-9.77, -6.62] W/W | — | -26.15 [-28.06, -24.36] W/W |
| 40 | reversed-0.2 | -1.08 [-1.88, -0.42] W/W | -0.34 [-0.64, -0.15] W/W | -0.55 [-1.04, -0.13] W/T | — | -0.42 [-0.83, -0.16] W/W |
| 40 | reversed-0.5 | -2.28 [-3.21, -1.46] W/W | -0.93 [-1.24, -0.68] W/W | -0.76 [-1.23, -0.35] W/W | — | -0.97 [-1.29, -0.71] W/W |
| 80 | none | -0.28 [-0.44, -0.13] W/W | -0.00 [-0.05, +0.06] T/T | -0.26 [-0.45, -0.09] W/T | -3.20 [-3.72, -2.68] W/W | +0.03 [-0.02, +0.09] T/T |
| 80 | extra-0.2 | -0.20 [-0.40, -0.03] W/T | +0.03 [-0.01, +0.08] T/T | -0.60 [-0.71, -0.48] W/W | -3.26 [-3.77, -2.76] W/W | +0.03 [-0.04, +0.12] T/T |
| 80 | extra-0.5 | -0.24 [-0.40, -0.10] W/W | +0.02 [-0.03, +0.08] T/T | -0.71 [-0.79, -0.62] W/W | -3.11 [-3.56, -2.65] W/W | +0.04 [-0.03, +0.12] T/T |
| 80 | missing-0.2 | -8.41 [-9.27, -7.55] W/W | -12.45 [-13.33, -11.66] W/W | -6.93 [-7.75, -6.13] W/W | -2.41 [-2.85, -2.00] W/W | -12.89 [-13.74, -12.09] W/W |
| 80 | missing-0.5 | -25.41 [-26.83, -23.98] W/W | -25.42 [-27.20, -23.70] W/W | -16.54 [-17.95, -15.12] W/W | -2.35 [-2.77, -1.96] W/W | -25.68 [-27.49, -23.95] W/W |
| 80 | reversed-0.2 | -1.00 [-1.41, -0.63] W/W | -0.25 [-0.43, -0.10] W/W | -0.43 [-0.62, -0.25] W/W | -3.43 [-3.87, -3.00] W/W | -0.25 [-0.45, -0.08] W/T |
| 80 | reversed-0.5 | -2.78 [-3.42, -2.17] W/W | -1.05 [-1.26, -0.86] W/W | -0.86 [-1.13, -0.59] W/W | -4.57 [-5.12, -4.05] W/W | -0.98 [-1.20, -0.75] W/W |
| 150 | none | -0.01 [-0.08, +0.04] T/T | -0.01 [-0.03, +0.02] T/T | -0.02 [-0.10, +0.05] T/T | -1.10 [-1.38, -0.82] W/W | +0.00 [-0.03, +0.03] T/T |
| 150 | extra-0.2 | -0.01 [-0.08, +0.05] T/T | -0.01 [-0.03, +0.01] T/T | -0.73 [-0.82, -0.66] W/W | -1.09 [-1.36, -0.82] W/W | +0.01 [-0.01, +0.03] T/T |
| 150 | extra-0.5 | -0.01 [-0.07, +0.05] T/T | +0.00 [-0.03, +0.03] T/T | -0.87 [-0.98, -0.76] W/W | -1.03 [-1.30, -0.77] W/W | +0.02 [-0.01, +0.05] T/T |
| 150 | missing-0.2 | -9.42 [-10.39, -8.47] W/W | -11.11 [-11.89, -10.39] W/W | -8.22 [-9.11, -7.35] W/W | -0.68 [-0.89, -0.47] W/W | -11.41 [-12.22, -10.66] W/W |
| 150 | missing-0.5 | -26.86 [-28.38, -25.33] W/W | -26.12 [-27.85, -24.43] W/W | -19.97 [-21.41, -18.53] W/W | -0.67 [-0.92, -0.41] W/W | -26.35 [-28.12, -24.62] W/W |
| 150 | reversed-0.2 | -1.07 [-1.77, -0.56] W/W | -0.69 [-0.91, -0.51] W/W | -0.21 [-0.35, -0.07] W/T | -1.62 [-2.16, -1.19] W/W | -0.75 [-0.98, -0.57] W/W |
| 150 | reversed-0.5 | -3.11 [-3.91, -2.37] W/W | -1.38 [-1.62, -1.17] W/W | -0.52 [-0.80, -0.26] W/W | -2.72 [-3.41, -2.13] W/W | -1.36 [-1.58, -1.16] W/W |

Đếm trên các cell có so sánh: tolerant_v4-plugin: thô W 17 / T 4 / L 0, Holm W 14 / T 7 / L 0; tolerant_v4-inflate: thô W 12 / T 8 / L 1, Holm W 12 / T 9 / L 0; tolerant_v4-bagging: thô W 17 / T 4 / L 0, Holm W 14 / T 7 / L 0; tolerant_v4-lp_allpast: thô W 14 / T 0 / L 0, Holm W 14 / T 0 / L 0; tolerant_v5_1-plugin: thô W 18 / T 3 / L 0, Holm W 14 / T 7 / L 0; tolerant_v5_1-inflate: thô W 12 / T 8 / L 1, Holm W 11 / T 10 / L 0; tolerant_v5_1-bagging: thô W 18 / T 3 / L 0, Holm W 15 / T 6 / L 0; tolerant_v5_1-lp_allpast: thô W 14 / T 0 / L 0, Holm W 14 / T 0 / L 0.

Tỷ số median width v4 / plugin theo cell (mô tả):

T40 none 1.38; T40 extra-0.2 1.33; T40 extra-0.5 1.29; T40 missing-0.2 3.56; T40 missing-0.5 3.61; T40 reversed-0.2 1.42; T40 reversed-0.5 1.52; T80 none 1.28; T80 extra-0.2 1.30; T80 extra-0.5 1.29; T80 missing-0.2 1.97; T80 missing-0.5 2.08; T80 reversed-0.2 1.52; T80 reversed-0.5 1.48; T150 none 1.20; T150 extra-0.2 1.23; T150 extra-0.5 1.22; T150 missing-0.2 1.71; T150 missing-0.5 1.77; T150 reversed-0.2 1.43; T150 reversed-0.5 1.48

Nguồn: `results/ext_tables_main/tables.json` (khoá `t5`), row từ `results/a2_baselines/runs.jsonl` (oracle, plugin, inflate, bagging, lp_allpast, v4) và `results/ext_v51_eval/runs.jsonl` (v5_1). Cột width là median qua run của `width_kept`. `lp_allpast` ở T40 có < 54/60 run ok, nên bị bỏ (14 so sánh, khoá `skipped`). Bảng 5b chỉ in 5 trong 8 cặp so sánh; cả 8 cặp (thêm v5_1 − plugin, − bagging, − lp_allpast) nằm trong `tables.json` và được đếm dưới đây. Coverage, width và IS của plugin/inflate/bagging/v4 khớp `results/ext_metrics_rq41/tables.md` (phần D-07 development).

**Đếm (W = module tốt hơn):**

| so sánh | số cell | thô W / T / L | Holm(154) W / T / L |
|---|---|---|---|
| v4 − plugin | 21 | 17 / 4 / 0 | 14 / 7 / 0 |
| v4 − inflate | 21 | 12 / 8 / 1 | 12 / 9 / 0 |
| v4 − bagging | 21 | 17 / 4 / 0 | 14 / 7 / 0 |
| v4 − lp_allpast | 14 (T ≥ 80) | 14 / 0 / 0 | 14 / 0 / 0 |
| v5_1 − plugin | 21 | 18 / 3 / 0 | 14 / 7 / 0 |
| v5_1 − inflate | 21 | 12 / 8 / 1 | 11 / 10 / 0 |
| v5_1 − bagging | 21 | 18 / 3 / 0 | 15 / 6 / 0 |
| v5_1 − lp_allpast | 14 (T ≥ 80) | 14 / 0 / 0 | 14 / 0 / 0 |

Nguồn đếm: `results/ext_tables_main/tables.json` (khoá `t5.counts`).

**Đọc bảng:**
- Ở cell missing và reversed, module có IS thấp hơn mọi cách báo một điểm sau Holm, trừ bốn so sánh chỉ thắng thô: v4 − bagging ở T40 reversed-0.2 và T150 reversed-0.2, v5_1 − bagging ở T40 reversed-0.2, và v5_1 − inflate ở T80 reversed-0.2. Ngoài cell missing/reversed, v4 chỉ thắng plugin sau Holm ở T80 none và T80 extra-0.5.
- Ở cell none/extra, v4 hòa `inflate` ở mọi T. Đây là điều tự nhiên, vì ở các cell đó v4 chính là plugin được nới width. Ngoại lệ là T40 extra-0.5: v4 tệ hơn thô +0.15 [+0.01, +0.35], hòa sau Holm.
- `inflate` không cứu được cạnh thiếu: coverage 0.489–0.543 ở missing-0.5, và IS 28.3–31.2.

**Câu cho paper (thay "hẹp hơn"):**
> Cách báo một điểm trên skeleton đã cho under-cover khi skeleton thiếu cạnh (plugin 0.33–0.66). Nới rộng interval của nó không cứu được hiệu ứng đã mất (`inflate` 0.49–0.54 ở missing-0.5). Module trả interval rộng hơn plugin (median width gấp 1.20–3.61 lần) nhưng giữ coverage 0.91–0.98, và có interval score thấp hơn plugin ở 14/21 cell, thấp hơn `inflate` ở 12/21 cell (Holm trên 154 so sánh, không cell nào tệ hơn). Mọi cell thắng `inflate` là cell missing hoặc reversed. Ở skeleton đúng và skeleton chỉ thừa cạnh, nó ngang `inflate`.

---

## 6. RQ4.4: flag cố định, so với 1/width

### Bảng 6. RQ4.4: flag cố định so với rel_width và 1/width (fresh D-07, seed_base 30261102; tolerant_v4)

| tập | n | miss rate | AUROC p̂ [CI] | AUROC rel_width | AUROC 1/width [CI] | p̂ − 1/width [CI] | Holm(9) p̂ > 1/width | Holm(9) 1/width > p̂ | flagged | ratio [CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| clean T80/150 | 26082 | 0.047 | 0.730 [0.694, 0.763] | 0.657 | 0.658 [0.622, 0.699] | +0.072 [+0.037, +0.107] | 0.0045 | 1.0000 | 0.082 | 4.32 [3.42, 5.50] |
| clean T40 | 13041 | 0.072 | 0.824 [0.782, 0.862] | 0.590 | 0.808 [0.766, 0.846] | +0.015 [+0.005, +0.025] | 0.0240 | 1.0000 | 0.193 | 7.95 [5.84, 10.89] |
| GES all T | 5589 | 0.049 | 0.738 [0.710, 0.766] | 0.559 | 0.701 [0.666, 0.735] | +0.037 [+0.016, +0.059] | — | — | 0.045 | 5.01 [3.70, 6.47] |
| GES T40 | 1863 | 0.021 | 0.715 [0.600, 0.816] | 0.310 | 0.763 [0.659, 0.857] | -0.048 [-0.070, -0.026] | 1.0000 | 0.0045 | 0.027 | 9.17 [2.96, 15.41] |
| GES T80 | 1863 | 0.043 | 0.740 [0.688, 0.801] | 0.661 | 0.675 [0.608, 0.751] | +0.066 [+0.037, +0.095] | 0.0045 | 1.0000 | 0.067 | 5.61 [3.30, 8.87] |
| GES T150 | 1863 | 0.084 | 0.708 [0.659, 0.760] | 0.735 | 0.559 [0.508, 0.607] | +0.149 [+0.120, +0.182] | 0.0045 | 1.0000 | 0.042 | 3.76 [2.68, 5.37] |
| latent1 T80/150 | 11178 | 0.052 | 0.657 [0.614, 0.705] | 0.545 | 0.641 [0.615, 0.672] | +0.016 [-0.023, +0.057] | 0.7540 | 1.0000 | 0.073 | 3.12 [2.30, 4.23] |
| latent3 T80/150 | 11178 | 0.071 | 0.596 [0.548, 0.649] | 0.491 | 0.619 [0.596, 0.643] | -0.023 [-0.065, +0.019] | 1.0000 | 0.8820 | 0.064 | 2.85 [2.05, 3.90] |
| noise0.1 T80/150 | 11178 | 0.085 | 0.717 [0.683, 0.752] | 0.612 | 0.689 [0.660, 0.718] | +0.029 [+0.006, +0.053] | 0.0240 | 1.0000 | 0.096 | 3.45 [2.82, 4.21] |
| noise0.3 T80/150 | 11178 | 0.186 | 0.687 [0.664, 0.711] | 0.562 | 0.710 [0.692, 0.731] | -0.023 [-0.040, -0.003] | 1.0000 | 0.1160 | 0.133 | 2.28 [1.97, 2.64] |
| clean T80/150 none-0.0 | 3726 | 0.047 | 0.701 [0.635, 0.758] | 0.637 | 0.641 [0.575, 0.711] | +0.060 [+0.005, +0.111] | — | — | 0.086 | 3.26 [2.15, 4.77] |
| clean T80/150 extra-0.2 | 3726 | 0.048 | 0.701 [0.659, 0.747] | 0.646 | 0.625 [0.569, 0.686] | +0.077 [+0.030, +0.125] | — | — | 0.098 | 3.12 [2.31, 4.33] |
| clean T80/150 extra-0.5 | 3726 | 0.051 | 0.712 [0.671, 0.752] | 0.639 | 0.640 [0.587, 0.695] | +0.072 [+0.029, +0.114] | — | — | 0.085 | 3.15 [2.12, 4.57] |
| clean T80/150 missing-0.2 | 3726 | 0.038 | 0.707 [0.661, 0.751] | 0.650 | 0.632 [0.579, 0.688] | +0.074 [+0.010, +0.146] | — | — | 0.052 | 5.04 [3.13, 7.50] |
| clean T80/150 missing-0.5 | 3726 | 0.038 | 0.696 [0.655, 0.744] | 0.656 | 0.620 [0.558, 0.681] | +0.076 [+0.028, +0.136] | — | — | 0.051 | 4.98 [3.01, 7.27] |
| clean T80/150 reversed-0.2 | 3726 | 0.052 | 0.769 [0.718, 0.813] | 0.714 | 0.690 [0.622, 0.750] | +0.079 [+0.043, +0.118] | — | — | 0.095 | 4.71 [3.32, 6.36] |
| clean T80/150 reversed-0.5 | 3726 | 0.058 | 0.785 [0.722, 0.829] | 0.721 | 0.720 [0.670, 0.753] | +0.065 [+0.016, +0.109] | — | — | 0.105 | 6.06 [3.90, 8.55] |

Nguồn: `results/ext_revlag3_flagextra/flag_extra.json` (khoá `round2`, mã hoá stated của vòng 2) và bản đọc được `results/ext_revlag3_flagextra/flag_extra.md`. Phán quyết F1–F4 lấy từ `results/ext_revlag_fresh/flag_eval.md`. Hai cột Holm(9) là p một phía sau Holm trên 9 tập, do verifier vòng 3 tính (`results/ext_verify3_revlag3/holm_inv_width.json`). Tám hàng có "—" ở cột Holm là ngoài family: "GES all T" là hợp của ba tập GES theo T, còn 7 hàng cuối là các cell con của clean T80/150, chỉ để mô tả. Với mã hoá stated như lúc train (lệch ở 219/39123 hàng), F1–F4 không đổi và ratio 4.32 thành 4.33 (`results/ext_revlag3_flagextra/flag_extra.md`, bảng thứ hai).

**Đọc bảng:**
- **Rule F1–F4** (đăng ký trước, comparator rel_width): ĐẠT 5/5 điều kiện, Holm 5/5.
- **So với 1/width** (comparator mạnh hơn, không đăng ký trước): CI loại 0 ở 7/9 tập. 5 tập nghiêng về p̂ (clean T80/150, clean T40, GES T80, GES T150, noise0.1) và 2 tập nghiêng về 1/width (GES T40, noise0.3). Sau Holm(9): p̂ tốt hơn ở 5/9, 1/width tốt hơn ở 1/9 (GES T40; noise0.3 có p Holm 0.116).
- Ở clean T40, phần p̂ hơn 1/width chỉ là +0.015 [+0.005, +0.025]: gần như toàn bộ khả năng phân biệt ở T40 đến từ width.
- Flag được train và test trên cùng 20 topology D-07, chỉ khác seed.

**Câu cho paper:**
> Một flag logistic cố định (width, relative width, stated damage), train trên một run D-07 và test trên một run D-07 mới (cùng topology, seed mới), đạt AUROC 0.730 [0.694, 0.763] ở T80/150. Mức này cao hơn score đơn giản 1/width (0.658; chênh +0.072 [+0.037, +0.107]). Flag đánh dấu 8.2% pair, với miss-rate gấp 4.32 lần [3.42, 5.50]. Ở T40, AUROC 0.824 gần như hoàn toàn đến từ width (1/width: 0.808). Trên 9 tập kiểm tra, flag tốt hơn 1/width ở 5/9 và kém hơn ở 1/9 (GES T40), Holm trên 9.

**Không có:** AUROC cho `tolerant_auto3` và `tolerant_v5_1` (R3-9 chưa có số; run `ext_revlag3_flag` không hoàn tất).

---

## 7. Lệch so với định nghĩa ghi trước

- **L1 (null pair, mục 0.4).** Row của a2_baselines không có trường `n_null`/`n_covered_null`, vì chúng được tạo bởi bản runner cũ. Bảng 3c vì vậy dùng `results/ext_revlag_lag/nullpairs.jsonl` (cùng seed), với đại lượng "tỷ lệ interval chứa 0" thay cho "coverage của C thật". Hai đại lượng trùng nhau khi C thật của null pair bằng 0 đúng, và khác nhau khi 0 < |C| ≤ 0.1. Đây là một thay đổi định nghĩa, làm sau khi thấy trường bị thiếu. Không có test nào dựa trên nó.
- **L2 (mục 0.1 so với 0.2).** Mục 0.1 nói nguồn có row v4 lệch thì bị loại khỏi ghép cặp. Mục 0.2 lại liệt kê các run tlp2 làm nguồn. Năm run tlp2 lọc cell lệch 120/120 row v4 vì E1 (stream bootstrap của built-in), trong khi skeleton (100%) và data (công thức seed) trùng. Tôi theo mục 0.2 và giữ row `tlp2_*`. Theo cách đọc chặt của 0.1, row `tlp2_*` của năm run đó bị loại. Điều này **không đổi** X, X90 hay top-3 của cell nào: ở T80/150, không phiên bản tlp2 nào lọt top-3 (bảng 1b), còn ở T40 nguồn là ext_tlp2_t40, có v4 trùng 420/420.
- **L3.** Chỉ sửa cách trình bày của renderer (nhãn method trong bảng 1c, thêm cột budget vào 1b, thêm bảng 6). Không đổi số.

---

## 8. Số không truy được (hoặc không tồn tại)

- Giây mỗi lần gọi ở T40 cho mọi method, và ở T80/150 cho `ida_*`, `plugin`, `inflate`, `bagging`, `pselect_union_v2(_cal)`, `pselect_union`, `*_c2`, `tlp2_db`, `tlp2_lp_cal`, `bvar_cal`, `bvar_minnesota`: không có số đo nào trong repo. Bảng 1b/1c ghi "—".
- Coverage của oracle_cal trên null pair: không tính được từ dữ liệu đã lưu (chỉ có tổng theo run).
- AUROC của flag cho auto3/v5_1 (R3-9): chưa có.
- Verdict R3-4 (reversal comparator) trên D-07: chưa có run hợp lệ.
- Holm cho tập "GES all T" của RQ4.4: nằm ngoài family của verifier.
- Bảng 1b ở cell extra/reversed và ở T40 không có `pselect_union_v3(_cal)`, vì chưa ai chạy nó ở các cell đó.

## 9. File của hướng này

- Doc: `docs/ext/bang_ban_thao.md`.
- Script: `experiments/ext/tables/build_tables.py`, `experiments/ext/tables/render_tables.py`, `experiments/ext/tables/check_skeletons.py`.
- Kết quả: `results/ext_tables_main/{tables.json, tables.md, t1_counts_damaged.json, checks_skeletons.json, prereg_sha256.txt}`.
- Append R3-6 (một lần): `docs/ext/revlag.md`, mục "Sửa sau kiểm chứng vòng 2". Đây là doc duy nhất trong danh sách R3-6 chưa có heading đó lúc kiểm tra (khoảng 07:02Z, kiểm lại ngay trước khi append). Mọi doc khác trong danh sách (baselines2, redteam, v51, narrow, auto5, v4c, eiv2, tlp2) đã có heading, mỗi doc đúng một lần.
