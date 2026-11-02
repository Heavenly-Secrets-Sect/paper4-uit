# So sánh chính với baseline envelope đủ budget (ID `baselines3`, vòng 3, mục R3-1)

**Phạm vi.** Tiếp nối `baselines2`. Làm đúng R3-1 trong docs/ext/synthesis_round2.md: (1) module mới `src/paper4/ext_baselines3.py` với `pselect_union_v3` đúng như R2-1 yêu cầu (≥ 199 draw mỗi graph được chọn, cap 16 graph, adjacency test trong structural equation, cặp chọn lại không có hướng được union qua cả hai hướng kèm contemporaneous term) và bản width-calibrated `pselect_union_v3_cal`; (2) ghi rule trước, rồi chạy D-07 development cho `tolerant_v4` và `tolerant_v5_1` so với envelope {`pselect_union_v3`, `pselect_union_v3_cal`, `pselect_cal`, `fullvar_cal`, `targeted_lp_cal`, `tlp2_db_p3`, `bvar_minnesota_v2_cal`} ở T 80/150 × missing 0.2/0.5, Holm trên toàn family; (3) ghi budget tính toán của mọi method; (4) viết frozen spec P4-H2 (P7). Mọi kết quả D-07 ở đây là **exploratory, D-07 development** (seed_base 20261102). Calibration và design probe chỉ trên D-07H development. Không chạy P4-H2, P4-H1 hay split confirmatory nào; không chạy config P4-H2 nào.

Không sửa file có sẵn nào (ngoài phần append được phép vào baselines2.md và redteam.md). File mới: `src/paper4/ext_baselines3.py`, `experiments/configs/ext_baselines3_{cal,eval,p4h2}.json`, `experiments/ext/baselines3/*`, `results/ext_baselines3_*`, file này.

## 1. Thiết kế (cố định trước khi chạy D-07)

### 1.1 `pselect_union_v3`

Mọi method chỉ nhận data và public skeleton. `pselect_union_v3` **không đọc stated damage**: các working skeleton được dựng với damage rỗng, và random stream là hash của (family, data, pairs, orientation, lag_max, H, n_boot), không có `skel.damage` (bản v2 có hash cả stated damage). Timing script kiểm tra: xoá stated damage thì interval giống hệt ở 12/12 lần gọi (`results/ext_baselines3_budget/timing.json`, `checks`).

1. Selection: như `pselect_union_v2` (`diagnose.structural_pvalues`, p → z hai phía, chọn khi z > 1.96; 100 selection có nhiễu N(0, 1) cộng vào mọi z).
2. Graph giữ lại: graph không nhiễu cộng các graph nhiễu thường gặp nhất, tối đa **cap = 16** (v2: 4).
3. Cặp được chọn mà skeleton không có hướng: mỗi graph có cặp như vậy được fit trong **hai orientation member antithetic** (một orientation ngẫu nhiên và bản lật toàn bộ; hướng tạo cycle thì lấy hướng kia), tức mỗi cặp được fit theo cả hai hướng với contemporaneous term.
4. Budget: **mỗi member nhận đủ n_boot = 199 residual-bootstrap draw**, nên mỗi graph có ≥ 199 draw (398 khi có hai member). Interval mỗi member là percentile 2.5/97.5 của draw của chính nó (cùng kiểu với `plugin` và module; v2 dùng normal interval vì chỉ có 40–50 draw). Member có ít hơn max(10, 49) draw hợp lệ thì bị bỏ.
5. Interval báo cáo = union (min lo, max hi) qua mọi member của mọi graph. Point estimate = cumulative(mean IRF) qua các member của graph không nhiễu.

Trên 12 lần gọi ở D-07H (timing): luôn 16 graph × 2 member = 6368 draw mỗi lần gọi, 8.3 s (T80) và 11.4 s (T150) median, một process.

### 1.2 `pselect_union_v3_cal` (two-sided)

Cùng raw interval (chung cache, chung draw), pre-scale 0.5 quanh midpoint, rồi runner nới bằng factor theo (T, stated kind) từ lưới 1.0–10, tức factor hiệu dụng 0.5–5. Lý do: union qua 16 graph × 2 member over-cover (probe của verifier vòng 2 cho bản cap 16: 0.971/0.957 ở T80), và lưới chỉ widen được (E2) sẽ kẹt nó ở 1.0. Bản two-sided cho phép calibration làm hẹp, nên đây là phiên bản fair mạnh nhất của baseline này. Timing script kiểm tra: midpoint của `_cal` trùng raw, half-width đúng 0.5 lần ở 12/12 lần gọi.

Calibration (D-07H development, run `ext_baselines3_cal`, chỉ calibration phase, các cell none/missing-0.2/missing-0.5 với kinds list a2 để giữ nguyên skeleton và vị trí cell; 06:11:21Z–06:17:41Z): `pselect_union_v3_cal|80|missing` = 1.7 (hiệu dụng 0.85), `|150|missing` = 1.6 (hiệu dụng 0.80); `|80|none` 1.7, `|150|none` 1.6 (`results/ext_baselines3_cal/calibration.json`).

### 1.3 `pselect_cal`, `fullvar_cal` đăng ký trong module

Hai baseline của red team vòng 1 (`results/ext_redteam_calbase`) trước đây chỉ có qua `_EXT` injection của `experiments/ext/redteam/run_calbase.py`. Module mới đăng ký chúng với **cùng tên, cùng code estimator** (chỉ thêm `info` `seconds`/`n_draws`), nên runner cho cùng stream tag (`ext_seed(name)`) và cùng row ở cùng vị trí cell. Việc này cho phép một frozen spec duy nhất chạy cả envelope. Run D-07 dưới đây kiểm tra điều này (regression check, mục 3.4).

### 1.4 Wrapper `experiments/ext/baselines3/run_cells.py`

Chạy runner gốc nhưng chỉ tính các cell được liệt kê, **giữ nguyên vị trí cell** (bug E1): ở cell không liệt kê, mọi method trả về `skipped_cell` mà không tính gì, và row của cell đó bị bỏ khỏi output. Vì vậy cell được tính dùng đúng draw của một run full grid cùng kinds list. Hệ quả: (a) trên D-07 các row ghép được với row đã lưu của a2 grid; (b) trên P4-H2, row v4 và v5_1 của P7 sẽ **trùng** row của `ext_v51_p4h2` (P1) ở cùng cell, nên P1 và P7 dùng chung một realisation v4. Wrapper còn: `skip_calibration` (mọi factor lấy từ frozen file, kiểm tra đủ key trước khi chạy), `expected_modules` (abort nếu method được đăng ký bởi module khác, chống E4), và ghi `baselines3_manifest.json` (interpreter, numpy, số worker, sha256 của các module và của frozen file, các key frozen đã dùng; giảm nhẹ E5/E6).

### 1.5 Frozen calibration chung

`experiments/ext/baselines3/frozen_calibration_p7.json` (tune trên D-07H development, không key nào từ D-07 hay P4-H2):
- `mod|*` = `experiments/calibration/tolerant_v4_frozen.json` nguyên văn;
- `tolerant_v5_1|*` = `experiments/ext/v51/frozen_v4_v51.json` (80|missing 2.6, 150|missing 2.3; hiệu dụng ×0.5);
- `pselect_cal|*`, `fullvar_cal|*` = `results/ext_redteam_calbase/calibration.json` (missing: 1.3/1.3 và 1.4/1.6 ở T80/T150);
- `targeted_lp_cal|*` = `results/ext_tlp_eval/calibration.json` (1.1/1.3);
- `bvar_minnesota_v2_cal|*` = `results/ext_baselines2_eval/calibration.json` (2.8/2.7);
- `pselect_union_v3_cal|*` = `results/ext_baselines3_cal/calibration.json` (1.7/1.6, hiệu dụng ×0.5).

## 2. Các lần chạy trước khi ghi rule (công bố)

Không có lần chạy nào trên D-07 trước khi ghi mục 3. Trước đó chỉ có trên D-07H development:
- `experiments/ext/baselines3/timing.py` → `results/ext_baselines3_budget/timing.json`: 3 topology D-07H × T 80/150 × missing 0.2/0.5, mỗi method một lần gọi, một process (load average 5.1 → 7.0). Mục đích: budget và kiểm tra cache/blindness. Không xem coverage hay IS.
- `ext_baselines3_cal` (calibration only, mục 1.2). Chỉ xem factor.

## 3. Rule ghi trước (viết trước khi chạy `ext_baselines3_eval`)

### 3.1 Run

`python experiments/ext/baselines3/run_cells.py --config experiments/configs/ext_baselines3_eval.json --workers 3`. Bank D-07 development, seed_base 20261102, 20 topology × 3 replicate, T ∈ {80, 150}, kinds list [extra, missing, reversed] × rate {0.2, 0.5} (để skeleton, data và vị trí cell giống a2 grid), chỉ tính cell missing-0.2 và missing-0.5, n_boot 199, H 4. Method: `tolerant_v4`, `tolerant_v5_1`, `pselect_union_v3`, `pselect_union_v3_cal`, `pselect_cal`, `fullvar_cal`, `targeted_lp` (cần để `targeted_lp_cal` đi đúng đường cache như ở `ext_tlp_eval`; chỉ mô tả), `targeted_lp_cal`, `bvar_minnesota_v2_cal`. Không chạy calibration phase: mọi factor lấy từ `frozen_calibration_p7.json`. Ước tính khoảng 35–45 phút với 3 worker (giới hạn R3-1 là 60 phút).

`tlp2_db_p3` **không chạy lại**: nó dùng content seed (data, skeleton, lag_max, H, tag), không phụ thuộc vị trí cell hay stream của runner, và data/skeleton của D-07 giống hệt. Row lấy từ `results/ext_tlp2_t80b` và `results/ext_tlp2_t150c`. Điều kiện trước: `experiments/ext/baselines3/spot_tlp2.py` tính lại `tlp2_db_p3` trên 3 topology × replicate 0 × T 80/150 × missing 0.2/0.5 (12 lần gọi) và phải trùng từng số (`iscore_nonnull_mean`, `n_covered_nonnull`) với row đã lưu. Nếu có mismatch: chạy lại `tlp2_db_p3` trên D-07 bằng một config riêng (cùng wrapper), trước khi chấm, và công bố.

**Ghép cặp / regression.** Mọi method khác lấy từ run mới. Analyzer kiểm tra và báo số mismatch (status, `iscore_nonnull_mean`, `n_covered_nonnull`) giữa row mới và row đã lưu: v4 và `bvar_minnesota_v2_cal` so với `ext_baselines2_eval`; `tolerant_v5_1` so với `ext_v51_eval`; `pselect_cal`, `fullvar_cal` so với `ext_redteam_calbase`; `targeted_lp`, `targeted_lp_cal` so với `ext_tlp_eval`. Kỳ vọng 0 mismatch. Mismatch không đổi verdict (verdict luôn dùng row mới), nhưng phải công bố và giải thích.

### 3.2 Thống kê (`experiments/ext/baselines3/analyze.py`, viết trước khi chạy)

- Family F = method m ∈ {`tolerant_v4`, `tolerant_v5_1`} × baseline X ∈ {`pselect_union_v3`, `pselect_union_v3_cal`, `pselect_cal`, `fullvar_cal`, `targeted_lp_cal`, `tlp2_db_p3`, `bvar_minnesota_v2_cal`} × cell c ∈ {T80, T150} × {missing-0.2, missing-0.5}: **56 so sánh**.
- Coverage của m ở cell c: pooled trên non-null pair của mọi run; run mà m thất bại tính mọi non-null pair là không cover (số non-null pair lấy từ row v4 cùng run). Failure rate của m được báo theo cell.
- d = IS(m) − IS(X) theo từng run (topology, replicate) mà cả hai ok; ước lượng = trung bình. Cluster bootstrap theo 20 topology, B = 4000, **một ma trận index chung** cho mọi so sánh (rng `default_rng(20261102)`), CI 95% percentile. p một phía cho "m tốt hơn": p_W = (1 + #{boot ≥ 0})/(B + 1); cho "X tốt hơn": p_L = (1 + #{boot ≤ 0})/(B + 1); p hai phía = min(1, 2 min(p_W, p_L)).
- **Holm** step-down trên 56 p hai phía, mức 0.05. So sánh bị bác bỏ với d < 0 là **W**, với d > 0 là **L**, còn lại **T**. Song song báo phân loại theo CI thô (W nếu cận trên < 0, L nếu cận dưới > 0). Verdict chính thức dùng Holm.

### 3.3 Rule (mỗi m ∈ {v4, v5_1} chấm riêng; chấm theo Holm, báo kèm số đếm thô)

- **E-cell(m, c)**: m "thắng envelope ở cell c" khi coverage(m, c) ≥ 0.90, failure rate của m ở c ≤ 2%, và cả 7/7 so sánh của cell c là W.
- **E-full(m)**: E-cell đúng ở 4/4 cell.
- **E-noloss(m)**: 0/28 so sánh của m là L.
- **E-major(m)**: số W ≥ 15/28.

Câu được phép viết (chọn nhánh đầu tiên đúng):
- (a) E-full → "m có interval score thấp hơn mọi baseline đã thử, kể cả `pselect_union_v3` đủ budget (16 graph, 199 draw mỗi member) và bản two-sided calibrated, ở 4/4 cell thiếu cạnh khi T ≥ 80 (Holm trên 56)".
- (b) E-noloss và ít nhất một E-cell → "không baseline nào có interval score thấp hơn m có ý nghĩa; m thắng baseline mạnh nhất ở các cell {liệt kê}, và thắng W/28 so sánh".
- (c) E-noloss, không E-cell → "không thua; thắng W/28 so sánh" (viết "phần lớn" chỉ khi E-major).
- (d) có L → "m thua X ở cell …" với từng L; claim "không baseline nào tốt hơn" bị rút ở các cell đó.

"Không thua" là quan sát, không phải non-inferiority có margin; không được viết "non-inferior".

### 3.4 Mô tả (không chấm)

Budget mỗi method (draw, giây mỗi lần gọi, từ timing D-07H và từ `info_seconds` của run D-07 khi có); baseline mạnh nhất theo IS trong từng cell (tổng thể và trong các baseline có coverage ≥ 0.90); v5_1 − v4 trực tiếp; `pselect_union_v3(_cal)` so với `pselect_union_v2(_cal)` (row lưu ở `ext_baselines2_eval`, ghép qua row v4); `targeted_lp` thô; số graph/member/draw của v3.

### 3.5 Cách chọn hypothesis cho P4-H2 (cam kết trước, áp dụng máy móc sau khi có kết quả D-07)

Spec P7 trên P4-H2 kiểm tra, cho mỗi m: W_D07(m) = tập các so sánh **W theo Holm trên D-07** của m. P7 CONFIRMED cho m khi và chỉ khi: (i) coverage(m) ≥ 0.90 ở 4/4 cell; (ii) failure rate của m ≤ 2% ở mỗi cell; (iii) mọi so sánh trong W_D07(m) là W theo Holm trên 56 trên P4-H2; (iv) 0/28 so sánh của m là L theo Holm trên 56. Nếu W_D07(m) rỗng thì (iii) bỏ trống và P7 cho m chỉ là kiểm tra falsification (i), (ii), (iv). Câu paper trên P4-H2 = nhánh (a)–(d) của mục 3.3 áp lên kết quả P4-H2, nhưng chỉ được nói "xác nhận" cho các so sánh trong W_D07(m). Overlay Bonferroni của lead (synthesis_round2 mục 3.3, hai primary spec có p-value: P1 C1 và P7) = cùng phép chấm với Holm ở mức 0.025 hai phía; verdict chính thức vẫn là mức 0.05.

## 4. Kết quả

### 4.0 Run và kiểm tra trước khi chấm

- Rule (mục 3) và `analyze.py` được ghi lúc 13:19:27 / 13:20:31 (+07) = 06:19:27Z / 06:20:31Z; sha256 lưu trong `results/ext_baselines3_eval/prereg_sha256.txt` (doc e0a0d710…b5c8, analyze.py 6d24f176…0d40). Run D-07 bắt đầu 06:22:03Z, kết thúc 06:37:57Z, **954.4 s**, 2160 row, mọi status ok, 3 worker, `/usr/bin/python3` (CLT, numpy 2.0.2) (`results/ext_baselines3_eval/{run.log, manifest.json, baselines3_manifest.json}`). Không có gián đoạn, không chạy lại. Mục 1–3 của doc này không đổi sau khi chạy: phần trước "### 4.0" cộng dòng giữ chỗ cũ "(Thêm sau khi chạy.)" cho đúng sha256 e0a0d710…b5c8 đã lưu.
- Spot check `tlp2_db_p3` (điều kiện trước của mục 3.1): **12/12 trùng từng số** với row đã lưu (`results/ext_baselines3_eval/spot_tlp2.json`). Vì vậy dùng row đã lưu, không chạy lại.
- Regression (nguyên văn từ `rule_check.md`): `tolerant_v4` vs ext_baselines2_eval: 0/240, `bvar_minnesota_v2_cal` vs ext_baselines2_eval: 0/240, `tolerant_v5_1` vs ext_v51_eval: 0/240, `pselect_cal` vs ext_redteam_calbase: **240/240**, `fullvar_cal` vs ext_redteam_calbase: **240/240**, `targeted_lp` vs ext_tlp_eval: **240/240**, `targeted_lp_cal` vs ext_tlp_eval: **240/240**.
  - Giải thích (kiểm sau khi chấm, `experiments/ext/baselines3/describe.py` và lệnh in trong phiên): hai run lưu này chạy lúc 01:44–01:52 ngày 02/11, **trước** khi runner đổi stream tag của ext method từ `rng(100 + vị trí)` sang `ext_seed(tên)` (bug B1, docs/decision_rules.md mục "B1: seeds of extension methods"). Point estimate của `pselect_cal` và `fullvar_cal` trùng 60/60 ở mọi cell (estimator tất định), chỉ draw bootstrap khác. TLP có trọng số phụ thuộc moment bootstrap nên point estimate cũng khác. IS trung bình mới so với cũ lệch tối đa 0.08 (ví dụ `pselect_cal` T80 missing-0.2: 3.88 so với 3.96; `targeted_lp_cal` T80 missing-0.5: 3.95 so với 4.02). Đúng như mục 3.1, verdict dùng row mới; row cũ **không** tái lập được với runner hiện tại. Các số envelope của baselines2 (vòng 2) dựa trên row cũ của các method này.
  - Hệ quả có lợi: v4 và v5_1 trùng 0/240 mismatch với row đã lưu, nên wrapper giữ vị trí cell đúng như thiết kế.

### 4.1 Bảng rule (nguyên văn từ `results/ext_baselines3_eval/rule_check.md`, B = 4000)

| m | X | T | cell | cov m | IS m | IS X | cov X | m - X [95% CI] | p2 | raw | Holm 0.05 | Holm 0.025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.50 | 0.960 | -0.22 [-0.37, -0.05] | 0.0200 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.36 | 0.936 | -0.09 [-0.27, +0.10] | 0.3504 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.88 | 0.961 | -0.60 [-0.79, -0.42] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.44 | 0.960 | -0.17 [-0.26, -0.08] | 0.0010 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.2 | 0.959 | 3.28 | 3.51 | 0.956 | -0.23 [-0.42, -0.05] | 0.0130 | W | T | T |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.2 | 0.959 | 3.28 | 3.95 | 0.858 | -0.67 [-0.96, -0.40] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.959 | 3.28 | 4.86 | 0.958 | -1.58 [-1.91, -1.26] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 80 | missing-0.5 | 0.957 | 3.37 | 3.58 | 0.965 | -0.21 [-0.37, -0.02] | 0.0245 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.40 | 0.943 | -0.03 [-0.20, +0.14] | 0.7453 | T | T | T |
| tolerant_v4 | pselect_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.07 | 0.944 | -0.70 [-0.86, -0.55] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.86 | 0.950 | -0.49 [-0.65, -0.33] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 80 | missing-0.5 | 0.957 | 3.37 | 3.95 | 0.925 | -0.58 [-0.78, -0.39] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 80 | missing-0.5 | 0.957 | 3.37 | 5.47 | 0.797 | -2.10 [-2.53, -1.71] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.58 | 0.958 | -1.21 [-1.42, -0.99] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.15 | 0.986 | -0.09 [-0.16, -0.02] | 0.0070 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.2 | 0.968 | 2.06 | 1.91 | 0.962 | +0.15 [+0.04, +0.25] | 0.0085 | L | T | T |
| tolerant_v4 | pselect_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.56 | 0.981 | -0.50 [-0.62, -0.39] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.58 | 0.981 | -0.52 [-0.63, -0.42] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.978 | -0.29 [-0.38, -0.19] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.2 | 0.968 | 2.06 | 2.34 | 0.915 | -0.29 [-0.44, -0.14] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.968 | 2.06 | 3.71 | 0.968 | -1.65 [-1.88, -1.44] | 0.0005 | W | W | T |
| tolerant_v4 | pselect_union_v3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.32 | 0.991 | -0.11 [-0.18, -0.03] | 0.0065 | W | T | T |
| tolerant_v4 | pselect_union_v3_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.00 | 0.967 | +0.22 [+0.14, +0.30] | 0.0005 | L | L | T |
| tolerant_v4 | pselect_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.86 | 0.955 | -0.65 [-0.82, -0.48] | 0.0005 | W | W | T |
| tolerant_v4 | fullvar_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.95 | 0.962 | -0.73 [-0.85, -0.62] | 0.0005 | W | W | T |
| tolerant_v4 | targeted_lp_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.59 | 0.960 | -0.38 [-0.50, -0.26] | 0.0005 | W | W | T |
| tolerant_v4 | tlp2_db_p3 | 150 | missing-0.5 | 0.962 | 2.22 | 2.99 | 0.869 | -0.78 [-0.94, -0.60] | 0.0005 | W | W | T |
| tolerant_v4 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.962 | 2.22 | 3.63 | 0.962 | -1.42 [-1.58, -1.27] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.50 | 0.960 | -0.66 [-0.79, -0.52] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.36 | 0.936 | -0.52 [-0.67, -0.37] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.88 | 0.961 | -1.04 [-1.20, -0.88] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.44 | 0.960 | -0.60 [-0.75, -0.47] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.2 | 0.949 | 2.84 | 3.51 | 0.956 | -0.66 [-0.86, -0.47] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.2 | 0.949 | 2.84 | 3.95 | 0.858 | -1.11 [-1.35, -0.86] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.2 | 0.949 | 2.84 | 4.86 | 0.958 | -2.02 [-2.33, -1.72] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 80 | missing-0.5 | 0.951 | 3.10 | 3.58 | 0.965 | -0.48 [-0.62, -0.32] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.40 | 0.943 | -0.30 [-0.44, -0.15] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.07 | 0.944 | -0.97 [-1.13, -0.81] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.86 | 0.950 | -0.76 [-0.94, -0.58] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 80 | missing-0.5 | 0.951 | 3.10 | 3.95 | 0.925 | -0.85 [-1.03, -0.67] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 80 | missing-0.5 | 0.951 | 3.10 | 5.47 | 0.797 | -2.36 [-2.75, -2.02] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 80 | missing-0.5 | 0.951 | 3.10 | 4.58 | 0.958 | -1.48 [-1.68, -1.28] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.15 | 0.986 | -0.39 [-0.44, -0.33] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.2 | 0.966 | 1.76 | 1.91 | 0.962 | -0.15 [-0.23, -0.07] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.56 | 0.981 | -0.80 [-0.90, -0.71] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.58 | 0.981 | -0.82 [-0.93, -0.72] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.978 | -0.58 [-0.70, -0.46] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.2 | 0.966 | 1.76 | 2.34 | 0.915 | -0.58 [-0.74, -0.43] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.2 | 0.966 | 1.76 | 3.71 | 0.968 | -1.95 [-2.17, -1.73] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.32 | 0.991 | -0.34 [-0.41, -0.26] | 0.0005 | W | W | T |
| tolerant_v5_1 | pselect_union_v3_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.00 | 0.967 | -0.01 [-0.08, +0.05] | 0.7788 | T | T | T |
| tolerant_v5_1 | pselect_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.86 | 0.955 | -0.87 [-1.06, -0.71] | 0.0005 | W | W | T |
| tolerant_v5_1 | fullvar_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.95 | 0.962 | -0.96 [-1.08, -0.85] | 0.0005 | W | W | T |
| tolerant_v5_1 | targeted_lp_cal | 150 | missing-0.5 | 0.968 | 1.99 | 2.59 | 0.960 | -0.61 [-0.77, -0.44] | 0.0005 | W | W | T |
| tolerant_v5_1 | tlp2_db_p3 | 150 | missing-0.5 | 0.968 | 1.99 | 2.99 | 0.869 | -1.01 [-1.20, -0.79] | 0.0005 | W | W | T |
| tolerant_v5_1 | bvar_minnesota_v2_cal | 150 | missing-0.5 | 0.968 | 1.99 | 3.63 | 0.962 | -1.65 [-1.79, -1.51] | 0.0005 | W | W | T |

**tolerant_v4** (nguyên văn): coverage >= 0.90 in 4/4 cells; failure rates 0/60 ở cả 4 cell; Holm 0.05 over 56: W 19 / T 8 / L 1 (of 28); E-cell: tất cả False; E-full False, E-noloss False, E-major True → statement **(d) có so sánh thua**; losses: `pselect_union_v3_cal @ T150 missing-0.5`; raw CI counts: W 24 / L 2 (of 28); Bonferroni overlay (Holm 0.025): W 0 / T 28 / L 0, statement c.

**tolerant_v5_1** (nguyên văn): coverage >= 0.90 in 4/4 cells; failure rates 0/60 ở cả 4 cell; Holm 0.05 over 56: W 27 / T 1 / L 0 (of 28); E-cell: {80|0.2: True, 80|0.5: True, 150|0.2: True, 150|0.5: False}; E-full False, E-noloss True, E-major True → statement **(b) không thua; thắng envelope ở một số cell**; losses: none; raw CI counts: W 27 / L 0 (of 28); Bonferroni overlay (Holm 0.025): W 0 / T 28 / L 0, statement c.

### 4.2 Verdict theo rule

- **`tolerant_v4`: nhánh (d).** Câu được phép viết: "`tolerant_v4` thua `pselect_union_v3_cal` ở T150 missing-0.5 (IS 2.22 so với 2.00; +0.22 [+0.14, +0.30], qua Holm trên 56)". Claim "không baseline nào tốt hơn v4" (synthesis_round2 mục 2.1) **bị rút ở cell đó**. Không có E-cell nào: ở T80, v4 hòa `pselect_union_v3_cal` (−0.09 [−0.27, +0.10]; −0.03 [−0.20, +0.14]) và chỉ thắng `pselect_union_v3` thô ở mức không hiệu chỉnh (−0.22, −0.21; p 0.020, 0.0245; không qua Holm). Ở T150 missing-0.2, v4 tệ hơn `pselect_union_v3_cal` ở mức không hiệu chỉnh (+0.15 [+0.04, +0.25], p 0.0085, không qua Holm). Với 5 baseline còn lại (`pselect_cal`, `fullvar_cal`, `targeted_lp_cal` trừ T80 missing-0.2, `tlp2_db_p3`, `bvar_minnesota_v2_cal`), v4 thắng qua Holm: 19/28.
- **`tolerant_v5_1`: nhánh (b).** Câu được phép viết: "không baseline nào có interval score thấp hơn `tolerant_v5_1` có ý nghĩa; v5_1 thắng baseline mạnh nhất ở T80 missing-0.2, T80 missing-0.5 và T150 missing-0.2, và thắng 27/28 so sánh (Holm trên 56); ở T150 missing-0.5 nó hòa `pselect_union_v3_cal` (−0.01 [−0.08, +0.05])". Coverage 0.949–0.968.
- **Overlay Bonferroni (Holm 0.025): 0/28 W cho cả hai — đây là lỗi thiết kế của analyzer, không phải kết quả.** Với B = 4000, p hai phía nhỏ nhất là 2/4001 = 5.0e-4, lớn hơn ngưỡng Holm đầu tiên 0.025/56 = 4.5e-4, nên overlay không thể bác bỏ gì. Tôi phát hiện sau khi chấm; verdict chính (Holm 0.05) không bị ảnh hưởng (ngưỡng đầu 8.9e-4 > 5.0e-4). Sensitivity mô tả với B = 20000 (cùng seed; `results/ext_baselines3_eval/describe.md` mục 1): v4 Holm 0.05 W 20 / T 7 / L 1, Holm 0.025 W 19 / T 8 / L 1, cùng loss; v5_1 W 27 / T 1 / L 0 ở cả hai mức, cùng 3 E-cell. Một so sánh đổi lớp giữa B = 4000 và 20000: v4 − `pselect_union_v3` ở T150 missing-0.5, T → W. Rule D-07 vẫn là bản B = 4000; spec P4-H2 dùng B = 20000 (mục 6).

### 4.3 Mô tả (không chấm; `results/ext_baselines3_eval/describe.md`)

- **Baseline mạnh nhất ở cả 4 cell là `pselect_union_v3_cal`** (IS 3.36 / 3.40 / 1.91 / 2.00, coverage 0.936 / 0.943 / 0.962 / 0.967). Calibration two-sided làm hẹp nó (factor hiệu dụng 0.85 ở T80, 0.80 ở T150). Bản thô over-cover (0.960–0.991).
- **Budget đủ thì pselect mạnh hơn hẳn bản v2 ở T80:** v3 − v2 = −0.91 [−1.42, −0.45] và −0.98 [−1.41, −0.61]; ở T150 hòa (−0.01, +0.03). `_cal` của v3 tốt hơn v2 cả ở T150 (−0.24, −0.29). Điều này xác nhận cảnh báo của verifier vòng 2: biên lớn ở T80 của v4 so với `pselect_union_v2` (−1.14, −1.19) chủ yếu do comparator thiếu budget.
- **v5_1 − v4** (ghép cặp cùng run): −0.43 [−0.55, −0.33], −0.27 [−0.40, −0.14], −0.30 [−0.36, −0.24], −0.23 [−0.30, −0.16] ở T80 m0.2 / T80 m0.5 / T150 m0.2 / T150 m0.5.
- `targeted_lp` thô (ngoài family): v4 − X = −0.18 [−0.39, +0.01] ở T80 missing-0.2 (vòng 2, với row cũ: −0.20 [−0.39, −0.02]); −0.74, −0.18, −0.45 ở ba cell còn lại.
- `pselect_union_v3` trên D-07: luôn 16 graph × 32 member, 32/32 member ok, 6368 draw mỗi lần gọi; trung bình 18.2 (T80) / 22.9 (T150) pair được chọn (truth 21), trong đó 9.3 / 10.8 pair không hướng.

**Budget mỗi lần gọi** (median, một process trên D-07H, `results/ext_baselines3_budget/timing.json`; `info_seconds` = median trong run D-07 với 3 worker song song):

| method | draw mỗi lần gọi | s/call T80 | s/call T150 | info_seconds D-07 T80 / T150 |
|---|---|---|---|---|
| tolerant_v4 | 199 bootstrap refit (repair/orientation vẽ lại mỗi draw) | 0.56 | 0.66 | — |
| tolerant_v5_1 | 199 bootstrap refit, chọn lại lag mỗi draw | 1.27 | 1.44 | — |
| pselect_union_v3(_cal) | 199 mỗi member × 32 member = 6368 | 8.34 | 11.42 | 7.21 / 10.42 |
| pselect_cal | ≤ 16 graph × max(10, 199 // 16) = 12 draw | 0.28 | 0.36 | 0.24 / 0.34 |
| fullvar_cal | 199 bootstrap refit | 0.51 | 0.61 | 0.48 / 0.60 |
| targeted_lp(_cal) | 199 VAR-sieve draw một tầng (`_cal` dùng chung) | 0.31 | 0.40 | — |
| tlp2_db_p3 | MSDB B1 = 200 × B2 = 100 | 5.14 | 6.03 | — (spot check 3.7–5.2 s) |
| bvar_minnesota_v2(_cal) | 199 posterior draw (`_cal` dùng chung) | 0.09 | 0.08 | — |

Vậy `tolerant_v5_1` đạt nhánh (b) với 199 draw và khoảng 1.3–1.4 s mỗi lần gọi, trong khi baseline mạnh nhất dùng 6368 draw và 8–11 s.

## 5. Câu cho paper sau R3-1 (exploratory, D-07 development)

> Trên các cell thiếu cạnh ở T ≥ 80, chúng tôi so sánh với một envelope gồm bảy baseline đã calibrate hoặc đủ budget, mạnh nhất là post-selection union (Chang–Guo–Malinsky) với 16 graph, adjacency test trong structural equation, cạnh chọn lại được fit theo cả hai hướng, 199 bootstrap draw mỗi member (6368 draw mỗi lần gọi) và calibration width hai chiều. `tolerant_v5_1` có interval score thấp hơn mọi baseline ở 3/4 cell và 27/28 so sánh (Holm trên 56), coverage 0.949–0.968; ở T150 missing-0.5 nó hòa baseline mạnh nhất (−0.01 [−0.08, +0.05]). Module of record hiện tại `tolerant_v4` không thắng baseline mạnh nhất ở cell nào: hòa ở T80 và **thua** ở T150 missing-0.5 (+0.22 [+0.14, +0.30]).

Điều kiện đi kèm:
- (i) Đây là kết quả D-07, bank đã dùng nhiều lần cho dòng v5. v5_1 thắng ở đây không thay được P4-H2.
- (ii) Baseline mạnh nhất là bản chuyển thể của nhóm (calibration hai chiều do nhóm thêm, để công bằng). Bảng chính phải có cột budget như trên.
- (iii) "Hòa / không thua" là quan sát, không phải non-inferiority có margin.
- (iv) Câu vòng 2 "không baseline nào đã thử có interval score thấp hơn v4 ở cell nào" (synthesis_round2 mục 2.1) **sai** với baseline đủ budget và phải xoá.

## 6. Frozen spec P7 for P4-H2 (CHƯA chạy)

Ghi xong lúc 06:43Z ngày 02/11/2026 (manifest `frozen_utc` 06:43:04Z), sau kết quả D-07 ở mục 4 và trước mọi sử dụng P4-H2. Không chạy thử, không chạy một phần.

- **Câu hỏi:** trên bank sạch, `tolerant_v4` và `tolerant_v5_1` có giữ được các trận thắng D-07 trước envelope bảy baseline, và không thua baseline nào, ở T 80/150 × missing 0.2/0.5?
- **Method và module:** `tolerant_v4` (built-in, `methods.py`), `tolerant_v5_1` (`src/paper4/ext_v51.py`, TAU = 6.6083, + `ext_narrow.py`), `pselect_union_v3`, `pselect_union_v3_cal`, `pselect_cal`, `fullvar_cal` (`src/paper4/ext_baselines3.py`), `targeted_lp` + `targeted_lp_cal` (`src/paper4/ext_tlp.py`; `targeted_lp` chỉ để `_cal` đi đúng đường cache, ngoài family), `tlp2_db_p3` (`src/paper4/ext_tlp2.py`), `bvar_minnesota_v2_cal` (`src/paper4/ext_baselines2.py`).
- **Config:** `experiments/configs/ext_baselines3_p4h2.json` = config D-07 (`ext_baselines3_eval.json`) với đúng bốn khác biệt: `name`, `purpose`, `bank`/`split` = P4-H2/confirmatory, và thêm `tlp2_db_p3` vào `methods` và `expected_modules`. Kinds list [extra, missing, reversed], chỉ tính missing-0.2/0.5 (vị trí cell giữ nguyên), T [80, 150], 3 replicate, n_boot 199, H 4, seed_base 20261102, `skip_calibration`.
- **Frozen calibration chung:** `experiments/ext/baselines3/frozen_calibration_p7.json` (mục 1.5; `mod|*` = `tolerant_v4_frozen.json`, mọi factor từ D-07H development). Không chạy calibration phase; wrapper kiểm tra đủ key trước khi chạy.
- **Analyzer:** `experiments/ext/baselines3/analyze_p4h2.py` (dùng hàm của `analyze.py`), W_D07 trong `experiments/ext/baselines3/p7_win_set.json` (v4: 19 so sánh, v5_1: 27). Khác biệt duy nhất so với phân tích D-07: **B = 20000** thay cho 4000, để overlay Holm 0.025 có thể bác bỏ (mục 4.2). Dry run trên row D-07 (`results/ext_baselines3_dryrun_p4h2/ruling_dryrun.md`, chỉ để test pipeline): validity PASS; v4 NOT CONFIRMED (fail (iv), loss vs `pselect_union_v3_cal` T150 m0.5); v5_1 CONFIRMED (27/27, không L), ở cả hai mức. Fault test (`fault_tests.txt`): thiếu cell → NOT CONFIRMED không crash; 4/60 run fail → (ii) fail; c_T sai → validity FAIL.
- **Lệnh (chạy đúng một lần, sau khi người dùng duyệt R3-0):**
  1. `/Users/kietnt/miniconda3/bin/python experiments/ext/baselines3/run_cells.py --config experiments/configs/ext_baselines3_p4h2.json --workers 3`
  2. `/Users/kietnt/miniconda3/bin/python experiments/ext/baselines3/analyze_p4h2.py` → `results/ext_baselines3_p4h2/ruling.{md,json}`

  Interpreter miniconda (numpy 2.5.4) trùng P1 v2 (`ext_v51fix_p4h2`). Run D-07 dùng CLT python (numpy 2.0.2); kiểm tra trên một unit D-07H cho output **giống hệt** (max |Δ| = 0) cho v3, `pselect_union_v3`, v5_1 (`results/ext_baselines3_budget/interpreter_check.json`). Điều kiện: `results/ext_baselines3_p4h2/` chưa tồn tại; nếu run bị cắt trước khi có `runs.jsonl` thì chạy lại một lần, giữ nguyên config, và công bố.
- **Thời gian dự kiến với `--workers 3`:** run D-07 cùng pipeline không có `tlp2_db_p3` mất 954 s; `tlp2_db_p3` thêm 480 lần gọi × khoảng 4–6 s / 3 worker ≈ 11–16 phút. Tổng **khoảng 30 phút** (tới khoảng 45 phút nếu máy bị chia nhiều); không có calibration phase; analyzer khoảng 1 phút. Số row mong đợi: 2400 (10 method × 4 cell × 60).
- **Spec manifest:** `experiments/ext/baselines3/p4h2_spec_files.json` (28 file với vai trò và sha256 lúc freeze, gồm `experiments/run_experiment.py`, `run_cells.py`, config, frozen file, win set, hai analyzer, mọi module method và `src/paper4/{methods,estimator,metrics,generator,skeleton,effects,topology,diagnose,__init__}.py`, cùng các file nguồn của factor; liệt kê thêm 9 module ext khác mà runner import). Lead hash lại toàn bộ ngay trước run. Manifest P4-H2 của bank không được mở ở đây.

**Rule xác nhận (nguyên văn từ docstring của analyze_p4h2.py, giống mục 3.5).** P7 CONFIRMED cho m ∈ {`tolerant_v4`, `tolerant_v5_1`} khi và chỉ khi: (i) pooled coverage(m) ≥ 0.90 ở 4/4 cell (run m thất bại tính mọi non-null pair là không cover); (ii) failure rate của m ≤ 2% ở mỗi cell và mọi validity check đạt (đúng config P4-H2, đúng 60 row mỗi (method, cell), `info_c_T` khớp frozen file, `method_modules` khớp `expected_modules`); (iii) mọi so sánh trong W_D07(m) là W theo Holm hai phía 0.05 trên family 56 so sánh trên P4-H2; (iv) 0/28 so sánh của m là L theo cùng Holm. Overlay Bonferroni: cùng phép chấm với Holm 0.025, báo cạnh. Câu paper = nhánh (a)–(d) của mục 3.3 áp lên kết quả P4-H2; chỉ được nói "xác nhận" cho các so sánh trong W_D07(m).

**Ghi trước để đọc kết quả:**
- Theo dry run D-07, phần v4 của P7 gần như chắc chắn NOT CONFIRMED do (iv). Đây là một falsification test: nó kiểm câu "v4 không thua baseline nào". Phần quyết định claim baseline chính của paper là phần v5_1, gắn với cam kết module of record của synthesis_round2 mục 3.1 (nếu P1 CONFIRMED thì module of record đổi sang v5_1).
- Mỗi m là một intersection-union test bên trong P7; Holm trên 56 là bảo thủ hơn mức cần cho IUT, giữ vì R3-1 yêu cầu.
- **Bug E1 (không sửa, theo quyết định của người dùng):** P7 dùng wrapper giữ vị trí cell của kinds list a2 và cùng seed_base, nên row `tolerant_v4` và `tolerant_v5_1` của P7 phải **trùng** row của `ext_v51fix_p4h2` (P1 v2) ở cùng cell; analyzer báo số mismatch (tolerance 1e-8, chỉ thông tin, không đổi verdict). Trên D-07 điều này đã được kiểm: 0/240 mismatch cho cả v4 và v5_1 so với run a2-grid đã lưu. Hệ quả còn lại của E1: (a) không config P4-H2 nào khác (P2, P3/P4, P5) có cùng realisation với P7 trừ khi cùng kinds list, cùng seed_base và cùng cách giữ vị trí cell; (b) nếu ai chạy P7 bằng runner trực tiếp hoặc bằng wrapper lọc cell kiểu `tlp2/run_cells.py`, c_idx sẽ dịch và row của v4, v5_1, `pselect_cal`, `fullvar_cal`, `targeted_lp(_cal)` sẽ là realisation khác, không ghép được với P1 (verdict của P7 vẫn hợp lệ vì mọi so sánh ghép cặp trong chính run); (c) `pselect_union_v3(_cal)`, `tlp2_db_p3` và `bvar_minnesota_v2_cal` dùng content seed nên không phụ thuộc E1.
- Multiplicity giữa các spec: P7 là primary (synthesis_round2 mục 3.3); overlay Bonferroni ở trên dành cho việc đó.
- Nếu P7-v5_1 NOT CONFIRMED: claim baseline của paper chỉ còn exploratory (D-07), viết theo mục 5 với điều kiện (i).

## 7. Bug / nhận xét (chỉ báo, không sửa file có sẵn)

- **Row đã lưu của `pselect_cal`, `fullvar_cal` (ext_redteam_calbase) và `targeted_lp(_cal)` (ext_tlp_eval) không tái lập được với runner hiện tại** (240/240 mismatch; stream tag B1 cũ). Mọi so sánh ghép cặp vòng 2 dùng các row này (envelope của baselines2, phần (a) của v51) là một realisation Monte Carlo khác; chênh IS trung bình ≤ 0.08. Bảng R3-8 nên dùng row của `ext_baselines3_eval` cho các method này ở 4 cell missing T ≥ 80.
- **Độ phân giải p bootstrap:** mọi analyzer dùng p = (1 + #)/(B + 1) với Holm trên family lớn cần B > 2m/α. Với B = 4000 thì family > 100 so sánh ở 0.05 (hoặc > 50 ở 0.025) không thể bác bỏ gì. Các spec khác dùng overlay Bonferroni nên kiểm điều này.
- `experiments/ext/baselines3/interp_check.py` có đường dẫn repo tuyệt đối (script kiểm tra một lần, không thuộc spec).
- Runner (E4) import mọi ext module; P7 chặn ghi đè tên bằng `expected_modules`. `pselect_cal`/`fullvar_cal` lần đầu được đăng ký trong `src/` (trước đây chỉ có qua `_EXT` injection); không module nào khác đăng ký các tên này lúc freeze.

## 8. Tóm tắt file

Code: `src/paper4/ext_baselines3.py`; `experiments/ext/baselines3/{run_cells.py, timing.py, spot_tlp2.py, analyze.py, describe.py, analyze_p4h2.py, make_manifest.py, interp_check.py, frozen_calibration_p7.json, p7_win_set.json, p4h2_spec_files.json}`. Config: `experiments/configs/ext_baselines3_{cal,eval,p4h2}.json` (p4h2: FROZEN, NOT RUN). Kết quả: `results/ext_baselines3_budget/{timing.json, interpreter_check.json}`, `results/ext_baselines3_cal/{calibration.json, calibration_run.json}`, `results/ext_baselines3_eval/{runs.jsonl, rule_check.md, analysis.json, describe.md, describe.json, spot_tlp2.json, prereg_sha256.txt, run.log, manifest.json, baselines3_manifest.json}`, `results/ext_baselines3_dryrun_p4h2/{ruling_dryrun.md, ruling_dryrun.json, fault_tests.txt}`. R3-6: đã append một lần vào docs/ext/baselines2.md và docs/ext/redteam.md (heading "Sửa sau kiểm chứng vòng 2").
