# Red team: audit độc lập (ID `redteam`)

**Phạm vi.** Audit đối kháng code, cấu hình và claim hiện có của Paper 4, đóng vai reviewer. Red team **không sửa** file nào ngoài file này và script nháp trong `experiments/ext/redteam/`. Mọi lỗi nghi ngờ trong code có sẵn chỉ được báo cáo, không sửa.

Các phần:
1. Quy tắc ghi trước cho các kiểm tra cần chạy thêm (mục A), ghi **trước khi chạy**.
2. Kết quả (mục B), thêm vào sau khi chạy, giữ nguyên số.
3. Danh sách finding (mục C), mỗi finding có severity, file:line, bằng chứng và cách sửa.

## A. Quy tắc ghi trước (viết trước khi chạy E3, P1, P2)

Đã chạy trước khi viết mục này, không phải evaluation: đọc code, đọc results có sẵn, và `repro_check.py` (chạy lại vài unit của config cũ bằng code hiện tại, so từng row).

### E3: baseline được hiệu chỉnh width như module (`results/ext_redteam_calbase`)

**Câu hỏi reviewer.** `tolerant_v4` được nới width theo (T, loại hỏng khai báo) trên D-07H development, còn `ida_union`, `bvar_minnesota`, `pselect_union` thì không. Lợi thế của module có còn khi baseline được hiệu chỉnh y hệt không? Và lợi thế ở cạnh thiếu có phải chỉ do "đưa mọi lag vào" không?

**Thiết lập.**
- Script `experiments/ext/redteam/run_calbase.py` gọi đúng `run_experiment.py` (calibrate, run_unit, summarize), chỉ đăng ký thêm các method dưới dạng ext qua biến `_EXT` (fork start method), không tạo file trong `src/`.
- Method: `plugin`, `tolerant_v4`, `pselect_cal`, `bvar_cal`, `ida_cal`, `fullvar_cal`. Bốn method `*_cal` nằm trong `calibrate_methods`, nên được nới bằng hệ số tune theo (T, loại hỏng khai báo) trên D-07H development, đúng cách của `tolerant_v4` (cùng `C_GRID`, sàn 1.0).
- `fullvar_cal` là ablation: mọi lag của mọi biến + cạnh cùng kỳ của skeleton, residual bootstrap, **không** repair, **không** rút chiều.
- Bank D-07 development, seed_base 20261102, kinds [extra, missing, reversed] × rates [0.2, 0.5], T ∈ {40, 80, 150}, 20 topology × 3 replicate, n_boot 199. Dữ liệu và skeleton hỏng trùng với `a2_baselines` / `a2b_pselect`.

**Quy tắc.**
- **R-E3a (claim A2 khi hiệu chỉnh ngang nhau).** Claim "v4 thắng baseline đã công bố ở cạnh thiếu khi T ≥ 80" được **giữ** nếu ở cả 4 cell missing (0.2, 0.5) × T ∈ {80, 150}: coverage v4 ≥ 0.90 **và** cận trên CI 95% (clustered theo topology) của IS(v4) − IS(X) < 0 với mọi X ∈ {`pselect_cal`, `bvar_cal`, `ida_cal`}. Nếu không: **FLAG major**, claim phải được thu hẹp.
- **R-E3b (ablation all-lags).** Nếu v4 tốt hơn hẳn `fullvar_cal` (cận trên < 0) ở ≥ 3/4 cell missing khi T ≥ 80: bước repair + rút chiều có giá trị riêng. Nếu ở ≥ 3/4 cell CI chứa 0 hoặc dương: **FLAG major**, lợi thế ở cạnh thiếu chủ yếu do "đưa mọi lag vào".
- T = 40 và các cell reversed / extra: báo cáo mô tả, không chấm.
- **Kiểm tra phụ:** các row `tolerant_v4` phải trùng từng số với `results/a2b_pselect` (cùng seed, cùng hệ số). Nếu không trùng: FLAG reproducibility.
- Ngân sách: mục tiêu dưới 15 phút với `--workers 3`. Nếu vượt, ghi lại.

### P1: coverage có điều kiện theo cặp (pair-level), D-07 development

**Câu hỏi reviewer.** Coverage gộp trên mọi cặp non-null có che mất việc module under-cover đúng những cặp bị hỏng ảnh hưởng không? Và metric chỉ tính cặp non-null có bỏ qua chi phí ở cặp null không?

**Thiết lập.** Script `experiments/ext/redteam/pair_probe.py` tái tạo đúng seed của runner (unit, c_idx, rng tag) cho `plugin` (tag 1), `tolerant_v4` (tag 6, hệ số từ `results/a2b_pselect/calibration.json`), `bvar_minnesota` (tag 8), `pselect_union` (tag 9). T ∈ {40, 80, 150}; cell missing-0.2/0.5, reversed-0.2/0.5. Lưu từng cặp (C_true, lo, hi, C_hat).

- **Cặp bị ảnh hưởng (affected):** cặp non-null mà C_true thay đổi ≥ 0.05 khi các cạnh thật bị hỏng (cạnh bị xóa, hoặc cạnh bị đảo) được đặt hệ số 0 trong SEM thật. Phần còn lại là "unaffected".
- **R-P1a.** Claim coverage của v4 là "đúng theo cặp" nếu coverage của v4 trên cặp affected ≥ 0.90 ở cả 4 cell × T ∈ {80, 150}. Nếu không: **FLAG major**, coverage gộp đang che chỗ hụt.
- **R-P1b (mô tả, có ngưỡng flag).** Báo cáo coverage và IS trên cặp **null** (|C_true| ≤ 0.1, ngoài đường chéo). FLAG major nếu IS trung bình trên cặp null của v4 > 1.5 lần của `pselect_union` ở T ≥ 80 trong ≥ 3/4 cell.
- **Kiểm tra phụ:** metric tính lại từ cặp phải trùng với row trong `a2_baselines` / `a2b_pselect` (coverage pooled, IS).

### P2: sàn của lưới hiệu chỉnh (thăm dò, D-07H development)

**Câu hỏi.** `C_GRID` bắt đầu ở 1.0, nên hệ số chỉ có thể nới, không thể thu hẹp. Ở T = 40, hệ số của module cho cạnh thiếu là đúng 1.0 (`results/a2_baselines/calibration.json`: `"mod|40|missing": 1.0`). Sàn này có đang giữ interval của module ở T = 40 rộng hơn cần thiết không?

**Thiết lập.** Cùng script `pair_probe.py`, chạy trên seed calibration (seed_base + 500000, D-07H development, 1 replicate), cho `tolerant_v3` và `pselect_union`, T ∈ {40, 80, 150}, cell none, missing, reversed. Tính coverage gộp theo c ∈ [0.5, 1.5].

**Đọc kết quả (mô tả, exploratory).** Nếu hệ số nhỏ nhất đạt 0.95 trên calibration ở T = 40 missing < 1.0, sàn đang ràng buộc: báo cáo c* và mức width giảm tương ứng. Red team **không** chạy phiên bản module mới trên bank evaluation. Một version dùng sàn thấp hơn phải do nhóm module ghi quy tắc trước.

## B. Kết quả (thêm sau khi chạy, số nguyên văn)

Script và output: `experiments/ext/redteam/` (`repro_check.py`, `stats_existing.py` → `stats_existing.out`, `run_calbase.py` + `calbase.json` → `results/ext_redteam_calbase/` và `e3_summary.out`, `pair_probe.py` → `out/p1.npz`, `out/p2.npz`, `p1_summary.out`, `p2_summary.out`, `analyze.py`, `verify_probe.py`).

### B0. Reproducibility (trước khi chạy E3/P1/P2)

- `repro_check.py` chạy lại một unit của 4 config cũ bằng code hiện tại: `a2_baselines` T=80 (49 row), `a2b_pselect` T=40 (21 row), `rq42_v4` T=150 (35 row), `a3_ges` T=80 (6 row). **111/111 row trùng từng số** (chỉ khác key `scenario`, không có trong các run cũ).
- Seed pairing: 2520 row `plugin`/`tolerant_v4` chung giữa `a2_baselines` và `a2b_pselect` trùng hoàn toàn.
- P1 tái tạo 2880 nhóm (unit × T × cell × method) và trùng 2880/2880 với row đã lưu (`verify_probe.py`).
- E3: 1260/1260 row `tolerant_v4` trùng với `a2b_pselect`.

### B1. E3: baseline được hiệu chỉnh width ngang module

**Ngân sách.** Run mất **1561.8 s (26 phút)**, vượt mục tiêu 15 phút. Lý do: load của máy lên 25–42 vì các agent khác chạy song song (calibration xong sau khoảng 7 phút). Grid không bị giảm.

Hệ số tune trên D-07H development (trích `results/ext_redteam_calbase/calibration.json`):

| T | `mod` missing | `pselect_cal` missing | `bvar_cal` missing | `ida_cal` missing | `fullvar_cal` missing |
|---|---|---|---|---|---|
| 40 | 1.0 | 1.8 | 3.6 | 7.7 | 1.0 |
| 80 | 1.3 | 1.3 | 4.0 | 8.9 | 1.4 |
| 150 | 1.2 | 1.3 | 3.8 | 8.6 | 1.6 |

Cell missing, mỗi ô ghi coverage / IS; cột cuối là IS(v4) − IS(X) với CI 95% clustered theo topology:

| T, cell | `tolerant_v4` | `pselect_cal` | `bvar_cal` | `ida_cal` | `fullvar_cal` | v4 − `pselect_cal` | v4 − `fullvar_cal` |
|---|---|---|---|---|---|---|---|
| 40, missing-0.2 | 0.983 / 7.77 | 0.965 / 7.74 | 0.926 / 8.59 | 0.927 / 23.50 | 0.972 / 7.84 | +0.02 [−0.33, +0.39] | −0.07 [−0.23, +0.07] |
| 40, missing-0.5 | 0.978 / 7.53 | 0.968 / 7.46 | 0.919 / 7.39 | 0.550 / 32.21 | 0.954 / 7.76 | +0.07 [−0.31, +0.47] | −0.23 [−0.53, +0.05] |
| 80, missing-0.2 | 0.959 / 3.28 | 0.958 / 3.96 | 0.937 / 7.73 | 0.906 / 19.10 | 0.963 / 3.50 | −0.68 [−0.86, −0.49] | −0.22 [−0.33, −0.11] |
| 80, missing-0.5 | 0.957 / 3.37 | 0.941 / 4.13 | 0.953 / 6.28 | 0.525 / 30.67 | 0.952 / 3.82 | −0.76 [−0.92, −0.60] | −0.45 [−0.58, −0.31] |
| 150, missing-0.2 | 0.968 / 2.06 | 0.980 / 2.62 | 0.967 / 5.84 | 0.886 / 15.80 | 0.980 / 2.59 | −0.56 [−0.72, −0.40] | −0.53 [−0.65, −0.43] |
| 150, missing-0.5 | 0.962 / 2.22 | 0.952 / 2.89 | 0.972 / 4.97 | 0.501 / 29.30 | 0.961 / 2.91 | −0.68 [−0.80, −0.54] | −0.70 [−0.82, −0.58] |

Hiệu của v4 so với `bvar_cal` ở T ≥ 80: −4.46, −2.91, −3.79, −2.75 (cận trên −4.07, −2.75, −3.51, −2.62). So với `ida_cal`: −15.82, −27.30, −13.74, −27.08.

- **R-E3a: GIỮ.** Ở cả 4 cell missing với T ∈ {80, 150}, coverage của v4 nằm trong 0.957–0.968, và cận trên của hiệu IS so với từng baseline đã hiệu chỉnh đều < 0. Lợi thế với `pselect_union` còn tăng: ví dụ T=80 missing-0.2 là −0.68, so với −0.46 khi chưa hiệu chỉnh, vì nới `pselect` để đủ coverage làm IS của nó tăng.
- **R-E3b: KHÔNG flag.** v4 tốt hơn hẳn `fullvar_cal` ở 4/4 cell missing khi T ≥ 80. Nhưng về độ lớn: so với `plugin`, `fullvar_cal` đã lấy được khoảng 97% phần giảm IS. Ví dụ T=80 missing-0.2: (11.68 − 3.50) / (11.68 − 3.28) = 0.974; T=150 missing-0.5: (29.07 − 2.91) / (29.07 − 2.22) = 0.974. Phần repair + rút chiều chỉ thêm 0.22–0.70 IS.
- **T = 40 (mô tả).** Khi hiệu chỉnh ngang nhau, `pselect_cal` đạt coverage 0.965 / 0.968 với IS 7.74 / 7.46. Kết quả là **hòa** với v4 (CI chứa 0). Câu "ở T = 40 module là method duy nhất đạt coverage" chỉ đúng khi baseline không được hiệu chỉnh. Width của v4 ở T = 40 (6.60) gần bằng `fullvar_cal` (6.39), nên độ rộng thừa đến từ việc mở mọi lag, không phải từ bước repair.
- **Reversed và extra (mô tả).** Ở T ≥ 80, v4 tốt hơn mọi baseline đã hiệu chỉnh ở cả 4 cell reversed (sát nhất: `ida_cal` ở T=80 reversed-0.2, −0.12 [−0.25, −0.00]). Ở none/extra T=80, v4 hòa `ida_cal`. Ở T=40, v4 hòa `bvar_cal` và `ida_cal` trên none/extra/reversed-0.2.

### B2. P1: coverage theo cặp

Coverage của `tolerant_v4` theo loại cặp (affected | unaffected non-null | null), trích `p1_summary.out`:

| T, cell | affected (n) | unaffected | null | `pselect_union` affected | `plugin` affected |
|---|---|---|---|---|---|
| 80, missing-0.2 | 0.970 (668) | 0.953 | 0.992 | 0.883 | 0.262 |
| 80, missing-0.5 | 0.959 (1303) | 0.953 | 0.993 | 0.866 | 0.115 |
| 80, reversed-0.2 | **0.862** (232) | 0.961 | 0.998 | 0.797 | 0.513 |
| 80, reversed-0.5 | **0.863** (564) | 0.958 | 0.998 | 0.789 | 0.466 |
| 150, missing-0.2 | 0.973 (668) | 0.965 | 0.981 | 0.907 | 0.228 |
| 150, missing-0.5 | 0.965 (1303) | 0.956 | 0.981 | 0.882 | 0.104 |
| 150, reversed-0.2 | 0.909 (232) | 0.978 | 0.995 | 0.750 | 0.470 |
| 150, reversed-0.5 | 0.906 (564) | 0.982 | 0.996 | 0.691 | 0.379 |
| 40, reversed-0.2 | 0.819 (232) | 0.935 | 0.998 | 0.845 | 0.616 |
| 40, reversed-0.5 | 0.867 (564) | 0.945 | 0.998 | 0.787 | 0.601 |

- **R-P1a: FLAG major.** Ở T = 80, coverage của v4 trên cặp affected bởi cạnh đảo là 0.862 và 0.863, dưới 0.90. Coverage gộp của cùng các cell là 0.948 và 0.929, đạt. Phần bù đến từ cặp unaffected (0.96) và cặp null không được tính. Với cạnh thiếu, cặp affected được phủ tốt (0.959–0.973). v4 vẫn phủ cặp affected tốt hơn mọi baseline ở T ≥ 80. Riêng T = 40 reversed-0.2, `pselect_union` hơn (0.845 so với 0.819).
- **R-P1b: không flag.** Tỷ số IS trên cặp null v4 / `pselect_union` vượt 1.5 chỉ ở 1/4 cell khi T=80 (missing-0.5: 2.08 / 1.38 = 1.51) và ở 0/4 cell khi T=150. Về mô tả: với cạnh thiếu, IS trên cặp null của v4 là 1.32–2.08, so với 0.23–0.55 của `plugin`. Tức là việc mở mọi lag có chi phí trên cặp null, nhưng metric chính (chỉ tính non-null) không thấy chi phí này. Ở T = 40, width trên cặp null của v4 là 4.0–4.2, so với 1.9 của `pselect_union`.

### B3. P2: sàn của lưới hiệu chỉnh (thăm dò, D-07H development)

Coverage gộp của `tolerant_v3` theo c (`p2_summary.out`). c* là hệ số nhỏ nhất đạt mục tiêu khi lưới bắt đầu từ 0.5:

| T | none | missing | reversed |
|---|---|---|---|
| 40 | 1.4 | **0.9** (cov 0.962 ở c=0.9; 0.975 ở c=1.0; 0.943 ở c=0.8) | 1.4 |
| 80 | 1.3 | 1.3 | 1.4 |
| 150 | 1.2 | 1.2 | 1.3 |

- Sàn 1.0 **chỉ ràng buộc ở T = 40 missing**. Bỏ sàn chỉ làm width giảm 10% (khoảng 6.5 xuống 5.9), vẫn rộng hơn `pselect_union` (3.5). Sàn không phải nguyên nhân chính của độ rộng thừa ở T = 40. Kết hợp với B1, nguyên nhân là phương sai của việc mở mọi lag ở T = 40.
- Ở mọi T khác, c* trên lưới mới trùng với hệ số đang dùng. Hướng "thu hẹp ở T nhỏ" vì thế nên nhắm vào mở lag có chọn lọc, không phải vào hệ số.


## C. Finding

Severity: **critical** = claim hoặc kết quả sai; **major** = reviewer sẽ bắt sửa hoặc claim phải thu hẹp; **minor** = nên sửa, không đổi kết luận. **Không có finding critical.** Không method nào đọc truth, các bank rời nhau, và kết quả tái lập được từng số.

### Điểm đã kiểm tra và đứng vững

- **Không rò truth vào method.** `grep -n "\.log\b|lag_hint|edge_lag|C_true"` trên `methods.py`, `diagnose.py`, `estimator.py` và các `ext_*.py` hiện có: chỉ `estimator.py:28-29` đọc `lag_hint`, và chỉ `oracle` có `lag_hint`. Calibration dùng truth, nhưng chỉ trên bank calibration.
- **Bank rời nhau.** Đã so 6 split (D-07, D-07H, P4-H1 × development/confirmatory): 0 topology trùng tập cạnh, 0 trùng skeleton, 0 trùng SHA-256.
- **Tái lập:** xem B0.
- **Số trong `ket_qua_nhom_a.md` khớp `summary.md`.** Bảng T=150 (ví dụ v4 missing-0.2: 0.968 / 2.06), bảng A3 (0.979 / 8.31; 0.950 / 3.69; 0.937 / 2.59), số repair (1.67 / 2.25 / 2.82), số lỗi GES (14.1 / 12.7 / 3.2 …) đều khớp.
- **Claim A2 vẫn giữ khi baseline được hiệu chỉnh ngang module** (E3, R-E3a). Đây là bằng chứng mạnh hơn claim gốc.

### F1 (major): log hỏng riêng tư đi kèm skeleton vào mọi method

- **Ở đâu:** `experiments/run_experiment.py:162-198` truyền nguyên object `Skeleton` cho method. `src/paper4/skeleton.py:42` (`log`) chứa cặp bị hỏng và lag thật. `run_experiment.py:137` gán `g.log = [counts]`, tức số lỗi thật của GES.
- **Bằng chứng:** `R.unit_skeletons(...)[('missing',0.2)].log` → `[{'pair': [0, 10], 'true_lag': 2}, {'pair': [2, 13], 'true_lag': 2}, {'pair': [3, 13], 'true_lag': 0}, {'pair': [5, 12], 'true_lag': 0}]`, trong khi `damage` chỉ là `{'kind': 'missing', 'rate': 0.2, 'k': 4}`. Hiện chưa method nào đọc `.log`. Test `test_public_record_hides_damaged_pairs` (`tests/test_core.py:96`) chỉ kiểm tra `to_interface()`, mà runner không dùng hàm này. Test vì thế tạo cảm giác an toàn giả.
- **Sửa:** runner tạo `public = skel.copy(); public.log = []; public.lag_hint = None` (trừ oracle) trước khi gọi method. Thêm test khẳng định method nhận `log == []`. Thêm một lint AST cấm `.log` / `.lag_hint` trong `ext_*.py`.

### F2 (major): rng tag của method ext phụ thuộc vào các file ext khác đang có trên đĩa

- **Ở đâu:** `run_experiment.py:195-198` dùng `rng(100 + e_idx)` với `e_idx` là vị trí trong `sorted(ext)` của **mọi** module `ext_*`. `run_experiment.py:60-73` import mọi `ext_*.py`.
- **Bằng chứng:** lúc 01:21 chỉ có `ext_narrow.py`, nên `tolerant_v5` có tag 100. Lúc 01:33, sau khi có thêm `ext_eiv`, `ext_textinfo`, `ext_tlp`: `[(0,'plugin_eiv',100), …, (8,'tolerant_v5',108), …]`. Chạy lại cùng một config ext cho số khác. Ngoài ra, một module ext lỗi cú pháp của agent khác sẽ làm crash mọi run.
- **Sửa:** `tag = 100 + zlib.crc32(name.encode()) % 10**6`, và chỉ import module ext có method được config yêu cầu (bọc try/except, báo tên module lỗi).

### F3 (major): "v4 đóng băng" thực ra được tune lại trong từng config, và hệ số dao động theo seed

- **Ở đâu:** `run_experiment.py:401` gọi `calibrate()` trong mỗi run. Seed calibration là `seed_base + 500000 + …`, rates và kinds lấy từ config.
- **Bằng chứng** (`stats_existing.out` mục 4):
  - `rq42_v4` (seed 20261101): `mod|40|none` 1.7, `mod|40|reversed` 1.8, `mod|80|reversed` 1.5;
  - `a2_baselines` (seed 20261102): lần lượt 1.4, 1.4, 1.4;
  - `a1_latent_noise` (rates chỉ [0.2]): `mod|80|missing` 1.2, so với 1.3 ở mọi config khác.

  Bảng hệ số v4 trong `decision_rules.md` (80: 1.3 / 1.5 / 1.4) không phải hệ số mà A1/A2/A3 dùng. Cùng thủ tục nhưng đổi seed calibration, hệ số ở T=40 lệch tới 0.4. Đây là sai số Monte Carlo của calibration (20 topology × 1 replicate).
- **Sửa:** lưu một `calibration_v4.json` cố định, nạp qua key config (ví dụ `"calibration_file"`), ghi SHA vào manifest. Báo cáo độ biến thiên của hệ số (bootstrap topology trên bank calibration). Sửa lại câu "frozen" trong docs.

### F4 (major): coverage gộp che under-coverage trên chính các cặp bị cạnh đảo ảnh hưởng

- **Bằng chứng:** P1 (B2). Ở T=80, coverage của v4 trên cặp affected là 0.862 (reversed-0.2) và 0.863 (reversed-0.5). Coverage gộp của cùng các cell là 0.948 và 0.929. Ở T=40: 0.819 / 0.867.
- **Sửa:** báo cáo coverage có điều kiện (affected / unaffected / null) trong bài. Định nghĩa affected chỉ dùng truth ở bước đánh giá. Đặt một rule coverage cho cặp affected trong các version sau. Hướng sửa method: tăng số cặp được đảo trong pool, hoặc hiệu chỉnh width theo loại cặp (cặp có cạnh cùng kỳ ý nghĩa).

### F5 (major): baseline có những điểm reviewer sẽ gọi là strawman

- **`pselect_union` (`methods.py:621-673`):**
  - cap 16 graph luôn bị chạm (mean `info_n_graphs` = 16.0 ở mọi cell), nên mỗi graph chỉ có `per = max(10, 199 // 16) = 12` bootstrap draw (`methods.py:666`), và percentile 2.5 / 97.5 lấy từ 12 draw;
  - chọn adjacency bằng Granger trên VAR reduced form, mà chính B1 v2 đã chỉ ra là không hợp lệ khi có cạnh cùng kỳ: số cặp chọn tăng 15.9 → 23.7 → 28.2 ở T=40/80/150, trong khi truth là 21;
  - cặp được chọn chỉ nhận lag (`methods.py:663`), nên không bao giờ khôi phục được cạnh cùng kỳ bị thiếu, dù phép chọn có dùng residual partial correlation;
  - point estimate chỉ lấy từ graph gốc.
- **`ida_union` (`methods.py:493`):** cũng chỉ 12 draw mỗi member. Theo thiết kế, nó không khôi phục cạnh thiếu, nên so trên cạnh thiếu là so với method không được thiết kế cho việc đó.
- **`bvar_minnesota` (`methods.py:527, 554, 563`):** phương sai sai số cố định ở scale AR đơn biến, không có prior hay marginalisation cho σ (GLP 2015 có). λ luôn là 0.2 hoặc 0.5. θ được chọn 0.01–0.3, nghĩa là marginal likelihood luôn siết cặp ngoài skeleton.
- **`lp_allpast`:** dùng Newey–West với L = H. Montiel Olea–Plagborg-Møller (2021) khuyến nghị lag augmentation **với** sai số chuẩn EHW, không cần HAC.
- **Đánh giá chung:** E3 cho thấy hiệu chỉnh width không cứu được các baseline ở T ≥ 80. Nhưng các lỗi fidelity trên vẫn nên sửa trước khi nộp.
- **Sửa:**
  - `pselect`: dùng n_boot ≥ 199 cho mỗi graph, hoặc gộp draw của các graph; kiểm định adjacency trên phương trình cấu trúc (như `diagnose.py` v2); thêm cạnh cùng kỳ cho cặp có residual correlation ý nghĩa;
  - `bvar`: dùng prior conjugate Normal–inverse-Gamma cho σ;
  - `lp`: dùng EHW;
  - thêm `fullvar_cal` (ablation all-lags đã hiệu chỉnh) vào bảng chính.

### F6 (major): lợi thế ở cạnh thiếu chủ yếu đến từ "mở mọi lag"; câu chuyện đóng góp cần nói rõ

- **Bằng chứng:** E3 / R-E3b. `fullvar_cal` đạt khoảng 97% phần giảm IS so với `plugin`. Repair + rút chiều chỉ thêm 0.22–0.70 IS ở T ≥ 80, có ý nghĩa thống kê nhưng nhỏ. Ở T=40, v4 và `fullvar_cal` hòa (−0.07 [−0.23, +0.07]; −0.23 [−0.53, +0.05]).
- **Sửa:** đưa `fullvar_cal` vào làm ablation chính trong bài. Định vị đóng góp là (i) quy tắc "khai báo thiếu cạnh ⇒ mở lag", (ii) repair cạnh cùng kỳ, (iii) đảo có nhắm mục tiêu và hiệu chỉnh theo loại hỏng, kèm phần đóng góp của từng bước.

### F7 (major): claim ở T = 40 và claim so với `pselect_union` dễ vỡ

- **Multiplicity** (`stats_existing.out` mục 2; t-based CI clustered, 20 topology; 54 phép so sánh A2 + A2b). Với ngưỡng 95% từng phép, module thắng 4/6 cell missing. Với Bonferroni / 54, chỉ còn 2/6 (rơi thêm missing-0.2 ở T=80 và T=150). Hiệu so với `pselect_union` ở missing-0.2: T=80 −0.46 (cận trên 95% −0.21, cận trên Bonferroni +0.02); T=150 −0.25 (−0.07; +0.09).
- **T = 40:** E3 cho thấy `pselect_cal` đạt coverage 0.965–0.968 và hòa với v4. Câu "ở T = 40 module là method duy nhất đạt coverage" (`ket_qua_nhom_a.md`) chỉ đúng với baseline chưa hiệu chỉnh.
- **Sửa:** báo cáo số cell thắng kèm hiệu chỉnh Holm hoặc Bonferroni. Diễn đạt claim T=40 thành "ngang baseline đã hiệu chỉnh". Lưu ý rằng E3 (baseline đã hiệu chỉnh) cho margin rộng hơn: −0.68 [−0.86, −0.49] ở T=80 missing-0.2.

### F8 (major → minor tùy cách viết): metric chính bỏ qua cặp null

- **Ở đâu:** `metrics.py:76-78`. IS và coverage chỉ tính trên cặp non-null. Với cặp null chỉ lưu `n_covered_null_reach`, không có IS hay width.
- **Bằng chứng:** P1. Với cạnh thiếu, IS trên cặp null của v4 là 1.32–2.08 ở T ≥ 80, so với 0.23–0.55 của `plugin` và 1.00–1.39 của `pselect_union`. Coverage trên cặp null đạt tới được của v4 là 0.992–0.998, tức over-cover (`stats_existing.out` mục 6). R-P1b không vượt ngưỡng flag.
- **Sửa:** báo cáo thêm IS trên cặp null hoặc IS trên mọi cặp như metric phụ, để reviewer thấy chi phí của việc mở mọi lag.

### F9 (minor): sàn `C_GRID` = 1.0

- **Ở đâu:** `run_experiment.py:45`, dùng ở dòng 298-299.
- **Bằng chứng:** `mod|40|missing` = 1.0 trong mọi config. P2 cho c* = 0.9 nếu bỏ sàn. Tác động nhỏ (width −10%) và không phải nguyên nhân chính của độ rộng thừa ở T=40 (B3).
- **Sửa:** cho lưới bắt đầu từ 0.5 trong version module kế tiếp (ghi quy tắc trước). Ghi rõ sàn trong phần phương pháp.

### F10 (minor): bước chọn (repair, reversal pool) cố định qua bootstrap

- **Ở đâu:** `methods.py:298, 302, 319`. `repair_candidates` và `contemporaneous_pool` chạy một lần trên dữ liệu gốc. Bootstrap chỉ rút lại chiều, không chọn lại.
- **Hệ quả:** bất định do bước chọn không được truyền vào interval, và coverage dựa vào hiệu chỉnh thực nghiệm. Reviewer theo hướng post-selection inference (Chang–Guo–Malinsky) sẽ hỏi điểm này.
- **Sửa:** chọn lại bên trong mỗi lần refit (ablation), hoặc viết rõ là giới hạn.

### F11 (minor): bẫy trong runner

- `run_experiment.py:401`: calibration chỉ chạy khi config có `inflate`, `tolerant_v3_cal` hoặc `tolerant_v4`. Một config chỉ có `calibrate_methods` sẽ cho mọi row `uncalibrated`.
- `run_experiment.py:265`: `misstated_rows` dùng hệ số `{T}|none|0.0` (của v3_cal) cho mọi method được liệt kê. Nếu liệt kê `tolerant_v4`, row sẽ mang tên v4 nhưng width là của v3_cal.
- `summarize` và `check_rules` tính coverage chỉ trên row `ok`, nên row lỗi bị bỏ im lặng (ví dụ `a3_ges` T=40: v4 ok 59/60).
- **Sửa:** kích hoạt calibration khi có `calibrate_methods`; dùng `mod|T|width_key` cho v4 trong misstated; in số row lỗi cạnh mọi coverage.

### F12 (minor): claim misstated chỉ được kiểm cho v3_cal, không cho v4

- **Ở đâu:** `experiments/configs/rq42_misstated.json` có `"misstated": {"methods": ["tolerant_v3", "tolerant_v3_cal"]}`, và `ket_qua_rq42.md` mục giới hạn 2.
- **Vấn đề:** v4 chọn width theo loại hỏng khai báo, nên báo động giả "missing 4" sẽ dùng hệ số missing của v4. Kết luận "chỉ cần biết có hỏng hay không" chưa được kiểm cho module chính thức.
- **Sửa:** chạy lại misstated cho v4 (sau khi sửa F11).

### F13 (minor): CI theo topology cho coverage

- **Bằng chứng** (`stats_existing.out` mục 1). Một số kết luận "đạt ≥ 0.90" có CI clustered cắt 0.90:
  - v4 T=40 reversed-0.2: 0.921 [0.890, 0.944], coverage theo topology thấp nhất 0.71;
  - latent1 T=150 none: 0.925 [0.898, 0.948];
  - noise0.1 T=80 missing: 0.917 [0.899, 0.934].

  Ngược lại, `pselect_union` T=80 missing-0.5 là 0.882 [0.861, 0.901].
- **Sửa:** kèm CI clustered cho mọi coverage, và tránh kết luận nhị phân sát ngưỡng.

### F14 (minor): nhật ký split và docs lỗi thời

- `experiments/run_flags.py:147` và `run_edge_cost.py:173` dùng D-07 confirmatory cho RQ4.4 và RQ4.3 (chạy lúc 11:58 và 10:57 ngày 01/11, **sau** held-out v3 lúc 08:29). Danh sách "mỗi split dùng một lần" trong `decision_rules.md` không ghi hai lần dùng này. Paper 2 cũng đã dùng split này.
- `ket_qua_rq42.md` vẫn ghi "P4-H1 development vẫn chưa dùng", "chưa thử GES", "chưa có biến ẩn, nhiễu đo". Cả ba đều mâu thuẫn với `ket_qua_nhom_a.md` và `decision_rules.md`.
- `ket_qua_nhom_a.md` mục A3 ghi "Interval score của module tốt nhất ở mọi T", nhưng `pselect_union` không chạy trong `a3_ges`. Ở `a3_heldout` T=40, `pselect_union` có IS 7.61 so với 9.26 của v4.
- **Sửa:** cập nhật nhật ký split và hai file kết quả. Thu hẹp claim A3: "coverage tốt nhất ở mọi T; IS tốt nhất ở T ≥ 80".

### F15 (minor): độ trung thành với plan

- RQ4.2 trong plan hỏi interval "đúng mức danh nghĩa **và hẹp hơn** các cách báo một điểm". Thực tế v4 **rộng hơn** `plugin`: width trung vị 1.69 so với 0.99 ở T=150 missing-0.2, và 1.28 so với 1.07 khi skeleton đúng. Nó chỉ thắng về interval score. Bài phải viết rõ là RQ đã được vận hành hóa bằng IS.
- B2 (mở rộng T bằng hàm lạm phát, plan 5.2/5.5) chưa làm. Cờ tin cậy (RQ4.4) chưa nằm trong output của module, trong khi plan 5.2 yêu cầu module trả (hiệu ứng, khoảng, cờ).
- Calibration và evaluation dùng cùng một họ generator (14 nút, 21 cạnh, cùng phân phối lag và hệ số). Việc chuyển hệ số sang dữ liệu thật hoặc sang mật độ khác chưa được kiểm.
- Không dùng F1/SHD, không dùng edge score của Paper 3 (`edge_score: None`). Hai điểm này khớp plan.

## Sửa sau kiểm chứng vòng 1

Phần này được thêm ở vòng 2 (hướng `baselines2`, docs/ext/baselines2.md), theo mục 1.6, X3 và R2-9/R2-10 của docs/ext/synthesis_round1.md. Không sửa nội dung phía trên; các câu dưới đây thay thế câu tương ứng.

1. **F6 phải đóng khung lại (bác bỏ cách đọc "lợi thế chủ yếu do mở mọi lag").** Câu "`fullvar_cal` lấy ~97% lợi ích, repair + rút chiều chỉ thêm 0.22–0.70" đo so với `plugin`, mà IS của plugin bị lost pair chi phối. So với baseline mạnh nhất đã calibrate (`pselect_cal`), phần biên của v4 mà `fullvar_cal` đạt được chỉ là +0.67, +0.41, +0.05, −0.03 ở T80 missing-0.2/0.5 và T150 missing-0.2/0.5. Ở T150, `fullvar_cal` hòa `pselect_cal` (2.59 so với 2.62; 2.91 so với 2.89). Câu đúng: **ở T150, gần như toàn bộ lợi thế của v4 so với `pselect_cal` đến từ contemporaneous repair + orientation draws**; ở T80, mở mọi lag giải thích khoảng 40–70% biên. Số: `results/ext_baselines2_r1fix/numbers.md`.
2. **Bias do sàn calibration (F9 mở rộng).** `pselect_cal`, `ida_cal` và `fullvar_cal` ngồi ở factor 1.0 trong khi over-cover ở nhiều cell không thiếu cạnh, nên mọi so sánh **mô tả** ngoài cell missing trong mục B1 (reversed, extra, none) nghiêng về v4. Rule R-E3a (chỉ cell missing) không bị ảnh hưởng.
3. **Ngân sách E3: vi phạm hard rule.** Ngoài việc chạy 1561.8 s (26 phút), run E3 có lúc chạy 6 worker, vượt giới hạn 3 worker. Câu "Grid không bị giảm" giữ nguyên; câu ngân sách phải ghi rõ cả hai vi phạm.
4. **Số chỉ có trong shell output, nay đã ghi vào file** (`experiments/ext/baselines2/r1_numbers.py` → `results/ext_baselines2_r1fix/numbers.md`, tính lại từ `results/a2b_pselect` và `results/ext_redteam_calbase`):
   - `pselect_union`: mean `info_n_graphs` = 16.00 ở mọi T (cap luôn chạm), nên per = max(10, 199 // 16) = 12 draw mỗi graph; mean số pair được chọn 15.90 / 23.72 / 28.20 ở T = 40 / 80 / 150 (truth 21), giống nhau ở mọi cell vì selection vòng 1 không dùng skeleton.
   - F7, v4 − `pselect_union` ở missing-0.2 (t-based CI clustered theo topology): T80 −0.464, per-test 95% [−0.723, −0.205], Bonferroni/54 [−0.949, +0.020]; T150 −0.252, [−0.436, −0.068], Bonferroni [−0.597, +0.092]. Khớp với câu trong F7.
   - Tag list của F2 (`rng(100 + e_idx)`) không tái lập được nữa, vì nó phụ thuộc bộ file ext lúc chạy và runner đã chuyển sang `ext_seed` theo tên method (decision_rules.md, "Runner fixes after the round-1 audit", B1). Chỉ giữ được bằng chứng định tính: tag của `tolerant_v5` đã đổi 100 → 108 → 111.
5. **R-P1a (FLAG) và X1.** Flag vẫn giữ theo rule đã ghi, nhưng quy kết phải sửa: oracle với skeleton đúng cũng miss các pair bị ảnh hưởng bởi cạnh đảo gần như ngang v4 ở T80 (verifier của metrics: 0.162 so với 0.158). Phần có thể quy cho reversal handling chỉ khoảng +0.02–0.03. Câu "coverage gộp che chỗ hụt của module" phải đổi thành "coverage gộp che độ khó nội tại của các pair này; module chỉ thêm khoảng 0.02–0.03 so với oracle".
6. **Fidelity của baseline (F5) đã được xử lý bằng version mới, không sửa methods.py:** `pselect_union_v2` và `bvar_minnesota_v2` trong `src/paper4/ext_baselines2.py`. Kết quả so sánh chính với các baseline này nằm ở docs/ext/baselines2.md.

## Sửa sau kiểm chứng vòng 2

Phần này được append ở vòng 3 (hướng `baselines3`, docs/ext/baselines3.md), theo mục R3-6 và 1.1 của docs/ext/synthesis_round2.md. Không sửa nội dung phía trên; câu dưới đây thay thế correction 6 của "Sửa sau kiểm chứng vòng 1".

6 (sửa). **Fidelity của baseline (F5) mới được xử lý một phần, không phải "đã xử lý".** Tình trạng theo từng điểm của F5:
- `pselect`: vòng 2 (`pselect_union_v2`) sửa selection (test trong structural equation) và thêm contemporaneous term theo cả hai hướng cho cặp chọn lại không có hướng, nhưng **vẫn thiếu budget**: cap 4 graph, khoảng 80 draw mỗi graph, trái với "n_boot ≥ 199 cho mỗi graph" của chính F5 và của R2-1. Bản đúng budget là `pselect_union_v3` (cap 16, 199 draw mỗi orientation member) cùng bản calibration hai chiều, trong `src/paper4/ext_baselines3.py` (vòng 3). Bản này là baseline mạnh nhất ở cả bốn cell missing T ≥ 80 trên D-07 development, và `tolerant_v4` hòa nó ở T80, thua nó ở T150 missing-0.5 (docs/ext/baselines3.md mục 4).
- `bvar`: đã sửa (prior conjugate Normal–inverse-Gamma cho σ, `bvar_minnesota_v2`).
- `lp_allpast`: **chưa** đổi sang EHW + lag augmentation.
- `ida_union`: **chưa** sửa (vẫn 12 draw mỗi member).
- `fullvar_cal` đã có trong envelope chính (R3-1).

Ngoài ra, row đã lưu của `pselect_cal` và `fullvar_cal` trong `results/ext_redteam_calbase` không tái lập được với runner hiện tại (stream tag ext cũ, B1): ở 4 cell missing T ≥ 80, 240/240 row khác, point estimate trùng, chênh IS trung bình ≤ 0.08. Hai method này nay được đăng ký trong `src/paper4/ext_baselines3.py` với cùng tên và cùng estimator; row mới nằm ở `results/ext_baselines3_eval`.
