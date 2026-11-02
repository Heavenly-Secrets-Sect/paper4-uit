# Hướng "r4lfdropen" (vòng 4): mở lag theo xác suất bằng local fdr hai nhóm, pi0 cố định theo số cạnh thiếu khai báo

**Trạng thái.** Exploratory, chỉ D-07 development (seed_base 20261102, ghép cặp với `results/ext_v51_eval`). Calibration và probe chỉ trên D-07H development. Không chạm P4-H1, P4-H2 (cả hai split) hay bất kỳ confirmatory split nào. Không gọi LLM. Không commit.

**File.**
- Code: `src/paper4/ext_r4lfdropen.py` (method `tolerant_v5_1_lfdr`; chỉ import từ `ext_v51`, `ext_narrow`, `methods`, `estimator`, không sửa module nào).
- Script: `experiments/ext/r4lfdropen/` (`test_known_truth.py`, `probe_d07h.py`, `run_driver.py`, `analyze.py`, `frozen_base.json`).
- Config: `experiments/configs/ext_r4lfdropen_{eval,latent,scen,lag1,lag4,smoke_d07h}.json`.
- Kết quả: `results/ext_r4lfdropen_*`.

---

## 0. Nguồn và ý tưởng

- **Efron, Tibshirani, Storey, Tusher (2001), JASA 96(456):1151–1160, doi:10.1198/016214501753382129.** Two-groups model f(z) = pi0·f0(z) + (1 − pi0)·f1(z). Local false discovery rate lfdr(z) = pi0·f0(z)/f(z) là posterior probability của null khi biết z. Ở đây dùng theoretical null f0 = N(0, 1) trên z = Phi^-1(1 − p).
- **Scott, Berger (2010), Ann. Statist. 38(5):2587–2619, doi:10.1214/10-AOS792.** Multiplicity adjustment trong variable selection đi qua prior inclusion probability. Bài báo cho thấy fully Bayes và empirical Bayes có thể khác nhau đáng kể ngay cả khi ước lượng EB hội tụ. Ở bài toán của mình, inclusion probability **không phải ước lượng**: nó được cố định bằng thông tin người dùng khai báo (k cạnh thiếu), nên pi0 = 1 − k/m đóng vai trò prior inclusion đã biết. Tức là không có bước EB cho pi0, chỉ có EM cho f1. Opening theo xác suất trong từng bootstrap draw là một dạng model averaging trên tập lag block được mở.
- **Kilian (2001), J. Forecasting 20(3):161–179.** Chọn lag thiếu (underfitting) làm IRF interval hẹp giả tạo. Vì vậy giữ một sàn: luôn mở top k cặp.

Mình chỉ đọc được abstract và tóm tắt của hai bài đầu (toàn văn bị paywall). Định nghĩa lfdr và two-groups model là chuẩn và khớp với tóm tắt.

**Giả thuyết (của ứng viên).** K = max(3k, #p<0.10) của v5_1 mở quá nhiều ở T = 40/80; phần lớn trong 3k block là nhiễu, và block nào mở cũng làm tăng variance. Opening theo xác suất giữ các block có bằng chứng mạnh gần như luôn mở, còn block biên chỉ mở trong một phần các draw. Dự đoán: IS thấp hơn ở các cell missing tại T = 40 và 80; trung tính ở T = 150; số block mở trung bình giảm ít nhất 30% ở T = 40.

---

## 1. Thiết kế đã cài đặt

Chỉ bước (2) trong nhánh targeted của `tolerant_v5_1` thay đổi, tức nhánh có stated missing > 0 và r < TAU; ở T ≤ 150, n = 14 nhánh này luôn được chọn. Các nhánh khác gọi đúng code của v5_1.

1. Lấy combined Sidak p của m cặp ngoài skeleton từ `ext_narrow.screen_pairs` (không đổi), clip vào [1e-12, 1 − 1e-12], rồi tính z = Phi^-1(1 − p).
2. pi0 = 1 − min(k, m − 1)/m. Fit f1 = N(mu, s²) bằng EM với pi0 cố định: khởi tạo mu = 2.5, s = 1; sàn s = 0.5; tối đa 200 vòng hoặc dừng khi max(|Δmu|, |Δs|) < 1e-6.
3. P_i = 1 − pi0·phi(z_i) / (pi0·phi(z_i) + (1 − pi0)·phi((z_i − mu)/s)/s).
4. Tập mở gồm top min(k, m) cặp theo p (sàn k, thay cho 3k), cộng thêm mỗi cặp còn lại với xác suất P_i:
   - trên data fit: mở khi P_i ≥ 0.5;
   - trong mỗi bootstrap draw: rút Bernoulli(P_i), với P tính lại từ screen của chính draw đó.
5. Term được de-dup như `tolerant_sel_dd`. Phần còn lại (repair BH với chiều ngẫu nhiên, reversal draws, bootstrap 199 draw, percentile, PRESCALE 0.5) giữ nguyên từng dòng.
6. Width factor (T, missing) được tune lại trên D-07H development bằng chính calibration của runner.

Log mỗi run (`info_*`): `n_open` (trên data), `n_open_boot_mean`, `lfdr_mu/s/pi0/m`, tập mở trên data, P của từng cặp trên data, và tần suất mở từng cặp qua các draw. P của các cặp thật sự bị thiếu và recall được analyzer tính sau từ `skeletons.jsonl`. Method không đọc truth.

### Các điểm tinh chỉnh trước khi đăng ký (kèm lý do)

- **R1. Random stream (common random numbers).** Runner seed mỗi ext method bằng `[unit, 3, T, c_idx, tag(name)]`. Nếu giữ nguyên, method mới sẽ không bao giờ trùng v5_1 ở các cell không có missing, do khác stream chứ không do khác method. Method nhận ra đúng cấu trúc seed đó (tag của chính nó) và seed lại main stream bằng tag của v5_1. Generator gốc chỉ được dùng cho các Bernoulli draw. Seed không chứa truth (chỉ unit, T và vị trí cell). Với generator khác, main stream là generator được đưa vào, còn Bernoulli stream được spawn từ seed sequence của nó. Hệ quả: tính hợp lệ (V1) kiểm được từng bit, và hiệu IS ở các cell missing có phương sai nhỏ hơn.
- **R2. Width factor ở các kind khác missing.** Ở none/extra/reversed, ứng viên trùng v5_1 từng bit (test T6), nên factor của nó cho các kind đó lấy đúng factor frozen của v5_1 (`experiments/ext/r4lfdropen/frozen_base.json` = `experiments/ext/v51/frozen_v4_v51.json` cộng 9 key này). Chỉ `tolerant_v5_1_lfdr|T|missing` được tune trong run eval. Factor re-tune thô của cả hai method (trước khi áp frozen) được lưu vào `calibration_raw.json` để đối chiếu.
- **R3. Đếm cell.** Grid a2 (lag_max 2, T ∈ {40, 80, 150}, none + {extra, missing, reversed} × {0.2, 0.5}) có 21 cell: 6 cell missing và **15** cell không missing (3 none, 6 extra, 6 reversed), không phải 13 như task ghi. Kiểm tra hợp lệ áp trên cả 15 cell.
- **R4. Thống kê.** p hai phía từ cluster bootstrap theo topology (định nghĩa ở mục 2). Coverage gộp trên các run ok. Thêm trần failure ≤ 3/60 mỗi cell, để một method thất bại nhiều không thể "thắng" nhờ loại run.
- **R5. Probe D-07H (công bố đầy đủ, không đổi thiết kế vì nó).** `probe_d07h.py` chạy trên 6 topology D-07H development (`results/ext_r4lfdropen_probe/probe.json`):
  - Trên data fit, ứng viên gần như chỉ mở đúng sàn k: trung bình 4.0 so với 12.3 của v5_1 ở T40 m0.2, và 12.0 so với 33.0 ở T40 m0.5.
  - Số block mở trung bình qua các draw là 6.4 so với 23.8.
  - Recall cặp thiếu thật trên data thấp hơn: 0.375 so với 0.542 ở T40 m0.2, 0.79 so với 0.96 ở T80 m0.2, 0.83 so với 0.92 ở T150 m0.2.
  - Half-width thô khoảng 0.70–0.83 lần v5_1.

  Smoke test qua driver (2 topology D-07H, `results/ext_r4lfdropen_smoke_analysis/ruling.md`) gợi ý factor T40 missing tăng (2.9 so với 2.1) và T40 m0.2 tệ hơn. Đây chỉ là 2 topology, trên bank calibration, nên không phải bằng chứng. Thiết kế được giữ đúng như ứng viên đề ra.

Test known-truth (`experiments/ext/r4lfdropen/test_known_truth.py`, `results/ext_r4lfdropen_tests/known_truth.json`): 9/9 PASS.
- EM khôi phục mu = 2.95, s = 0.94 (thật: 3, 1).
- P khớp công thức đóng (sai khác 1.7e-16).
- Các trường hợp biên đúng (m = 0, m = 1, k ≥ m, sàn s).
- Sàn top-k và luật P ≥ 0.5 đúng; giới hạn Bernoulli với P = 0/1 đúng.
- Stream: main stream trùng stream của v5_1.
- T6: trùng v5_1 từng bit ở 5/5 cell không missing.
- T6b: khi ép bước (2) về luật của v5_1, nhánh targeted trùng v5_1 từng bit (2/2), nên chỉ bước (2) khác.

---

## 2. Quy tắc (ghi trước khi chạy D-07)

**Run.**
- **Eval:** `ext_r4lfdropen_eval`, grid a2, D-07 development, 20 topology × 3 replicate, n_boot 199, seed_base 20261102. Methods: `oracle`, `tolerant_v5_1` (factor frozen), `tolerant_v5_1_lfdr`.
- **No-harm:** `ext_r4lfdropen_latent`, latent1 × {none, missing-0.2} × T {40, 80, 150}, cùng bank và seed. Factor lấy từ `results/ext_r4lfdropen_eval/calibration.json`.

**Hợp lệ.**
- **V1 (bắt buộc).** Mọi row của `tolerant_v5_1_lfdr` ở 15 cell không missing của eval (900 row), và ở cell none của run latent (180 row), phải trùng row `tolerant_v5_1` cùng khoá ở **mọi** trường (status, mọi metric, `info_c_T`), trừ tên method và key `info_lfdr_crn`. Phép so sánh dùng `same_row` trong analyze.py: mọi key của row ứng viên phải bằng chính xác. Nếu không đạt, verdict là INVALID.
- **V2 (ghép cặp, công bố).** Row `tolerant_v5_1` của eval trùng toàn bộ trường với `results/ext_v51_eval` (1260 row).
- **V3 (ghép cặp, công bố).** Row `tolerant_v5_1` của run latent trùng với `results/ext_v51_a1` (T80/150) và `results/ext_v51_a1t40` (T40) ở latent1 × {none, missing-0.2}.

  V2 hoặc V3 trượt thì được công bố như một phát hiện về reproducibility; verdict vẫn tính trên cặp trong cùng run.

**Primary (6 cell).** missing-0.2 và missing-0.5 × T {40, 80, 150}.
- dIS = trung bình hiệu IS (lfdr − v5_1) trên các run mà cả hai method đều ok.
- Cluster bootstrap theo topology: B = 20000, `default_rng(20261104)` khởi tạo lại cho mỗi cell; một bootstrap mean là tổng hiệu trên các topology được rút chia cho số run.
- CI 95% theo percentile.
- p_less = (1 + #{d* ≥ 0})/(B + 1), p_greater = (1 + #{d* ≤ 0})/(B + 1), p2 = min(1, 2·min(p_less, p_greater)).
- Holm ở mức 0.05 trên 6 cell.
- Một cell là **WIN** nếu Holm bác, dIS < 0 và coverage của lfdr ≥ 0.90. Cell là **LOSS** nếu Holm bác và dIS > 0.

**No-harm (3 cell latent1 × missing-0.2).** Mỗi cell phải thoả cả bốn điều kiện:
- (a) coverage lfdr ≥ 0.90 nếu v5_1 có coverage ≥ 0.90 (nếu v5_1 < 0.90 thì không yêu cầu);
- (b) tỷ số IS trung bình lfdr/v5_1 ≤ 1.05;
- (c) không có worsening đáng kể sau Holm (Holm 0.05 trên 3 cell, p2, dIS > 0);
- (d) failure lfdr ≤ 3/60.

**Verdict.**
- **RETAINED (exploratory)** khi tất cả các điều kiện sau đều đúng:
  - V1 đạt;
  - WIN ≥ 2/6;
  - coverage lfdr ≥ 0.90 ở cả 6 cell primary;
  - failure lfdr ≤ 3/60 ở mỗi cell primary;
  - no-harm đạt ở cả 3 cell.
- **INVALID** nếu V1 trượt.
- **NOT RETAINED** trong mọi trường hợp còn lại.

Mọi đếm được báo kèm số đếm sau Holm và số đếm theo CI thô. Verdict do `experiments/ext/r4lfdropen/analyze.py` tính máy móc. Không đổi quy tắc sau khi có kết quả; một bản thiết kế lại là một version mới, đi kèm quy tắc mới.

**Thứ cấp (chỉ mô tả, không ảnh hưởng verdict).**
- Bảng factor (v5_1 frozen, v5_1 re-tune thô, lfdr).
- Phân phối số block mở trên data và qua các draw, kèm mức giảm so với v5_1.
- Kiểm tra dự đoán "giảm ≥ 30% ở T40" và "trung tính ở T150".
- Recall của cặp thiếu thật: lfdr trên data và trung bình qua các draw; v5_1 trên data, tính lại bằng screen tất định trên data sinh lại. Kèm mean P của cặp thật.
- Kiểm tra tập mở đã log so với tính lại.
- Oracle để tham chiếu.
- Bảng 21 cell (Holm trên 21).
- Run phụ, chỉ mô tả, Holm trong từng family:
  - `ext_r4lfdropen_scen`: latent3, noise 0.1, noise 0.3 × missing-0.2 × T {40, 80, 150}; factor lấy từ eval;
  - `ext_r4lfdropen_lag1` (T 25/40) và `ext_r4lfdropen_lag4` (T 80/150): missing 0.2/0.5; **cả hai method được calibrate lại trong run đó** trên D-07H development, vì chưa có factor frozen cho lag_max 1/4.

  Run phụ chỉ chạy nếu còn thời gian; nếu bỏ sẽ ghi rõ.

**Lệnh** (interpreter `/Users/kietnt/miniconda3/bin/python`, numpy 2.5.4, cwd = repo root):
```
python experiments/ext/r4lfdropen/run_driver.py --config experiments/configs/ext_r4lfdropen_eval.json --workers 3
python experiments/ext/r4lfdropen/run_driver.py --config experiments/configs/ext_r4lfdropen_latent.json --workers 3 --frozen-from results/ext_r4lfdropen_eval/calibration.json
python experiments/ext/r4lfdropen/analyze.py
```
Hash của doc này (mục 0–2), analyzer, module và config được ghi vào `results/ext_r4lfdropen_prereg/prereg_sha256.txt` trước run eval.

---

## 3. Kết quả

(append sau khi chạy)

### 3.0 Thời gian và sự cố (ghi sau khi chạy, 2026-11-02)

- Pre-registration được hash lúc 12:18:05Z (`results/ext_r4lfdropen_prereg/prereg_sha256.txt`). Run eval chạy 12:18–12:39Z (1290.6 s, 3780 row). Run latent mất 378.5 s (720 row). Các run phụ: scen 1119.6 s (2160 row), lag1 533.8 s (1080 row), lag4 582.4 s (1080 row). Tất cả chạy với `--workers 3`; máy bị chia với các agent khác (load average 43–68), nên eval vượt mốc 20 phút nhưng dưới 30 phút. Không run nào phải chạy lại, không row nào thất bại (0/60 ở mọi cell của cả hai method).
- Mục 0–2 của doc này không đổi sau khi chạy: sha256 vẫn là `bb85fd62…766a`.
- **Bug của analyzer, đã sửa sau khi xem trước kết quả eval, trước run latent.** Bản `analyze.py` đã hash lúc đăng ký (lưu tại `results/ext_r4lfdropen_prereg/analyze_at_prereg.py`) **không** bỏ key `info_lfdr_crn` khi so V1, trái với text quy tắc ở mục 2. Vì vậy V1 báo 0/900 trùng. Mình kiểm từng trường: đúng 900/900 row khác nhau duy nhất ở key `info_lfdr_crn` và không ở trường nào khác. Analyzer được sửa đúng theo text quy tắc (`IGNORE = {method, info_lfdr_crn}`, và so trên hợp các key của cả hai row, tức là chặt hơn). Ngưỡng, cell và mọi tiêu chí khác không đổi. Bản sửa không thể làm thay đổi verdict theo hướng có lợi: bản cũ cho INVALID, bản mới cho NOT RETAINED.

### 3.1 Verdict (nguyên văn `results/ext_r4lfdropen_analysis/ruling.md`)

"Verdict: **NOT RETAINED**". Summary: `{"V1_pass": true, "wins_holm": 0, "wins_raw_ci": 0, "of": 6, "losses_holm": 5, "cov_all_primary_ge_090": true, "fail_ceiling_primary": true, "noharm_pass": false, "noharm_cells_pass": 1, "noharm_worse_holm": 2}`

**Hợp lệ: đạt cả ba.**
- V1: eval 900/900 row trùng, latent cell none 180/180.
- V2: v5_1 trùng `ext_v51_eval` 1260/1260 ở mọi trường.
- V3: v5_1 trùng `ext_v51_a1` 240/240 và `ext_v51_a1t40` 120/120.
- Factor re-tune thô của v5_1 trùng factor frozen ở 12/12 key.
- Tập mở đã log trùng kết quả tính lại tất định ở 360/360 run.

**Primary** (lfdr − v5_1; B = 20000, seed 20261104; Holm 0.05 trên 6): **WIN 0/6** (Holm 0/6, CI thô 0/6). **LOSS 5/6** (Holm 5/6).

| T | rate | cov lfdr | cov v5_1 | cov oracle | IS lfdr | IS v5_1 | dIS [95% CI] | p2 | Holm |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 0.2 | 0.953 | 0.922 | 0.880 | 5.461 | 4.837 | +0.623 [+0.279, +0.946] | 0.0006 | LOSS |
| 40 | 0.5 | 0.950 | 0.939 | 0.880 | 5.559 | 5.090 | +0.469 [+0.252, +0.695] | 0.0001 | LOSS |
| 80 | 0.2 | 0.953 | 0.949 | 0.899 | 3.022 | 2.842 | +0.180 [+0.038, +0.313] | 0.0149 | LOSS |
| 80 | 0.5 | 0.936 | 0.951 | 0.899 | 3.547 | 3.100 | +0.447 [+0.248, +0.649] | 0.0001 | LOSS |
| 150 | 0.2 | 0.963 | 0.966 | 0.943 | 1.781 | 1.759 | +0.023 [−0.063, +0.133] | 0.705 | – |
| 150 | 0.5 | 0.954 | 0.968 | 0.943 | 2.263 | 1.986 | +0.277 [+0.117, +0.464] | 0.0001 | LOSS |

**No-harm** (latent1 × missing-0.2; Holm 0.05 trên 3): **đạt 1/3, worsening có ý nghĩa sau Holm 2/3.**
- T40: tỷ số IS 1.129, +0.662 [+0.433, +0.879]. Trượt.
- T80: tỷ số 1.049, +0.156 [+0.091, +0.222]. Trượt vì worsening có ý nghĩa sau Holm.
- T150: tỷ số 1.031, +0.067 [−0.065, +0.212]. Đạt.
- Coverage 0.955 / 0.953 / 0.944, so với 0.939 / 0.953 / 0.956 của v5_1.

### 3.2 Thứ cấp (mô tả)

**Dự đoán của ứng viên.**
- "Số block mở giảm ≥ 30% ở T40": **đúng.** Trên data fit giảm 66% (13.0 → 4.4) ở m0.2 và 64% (33.2 → 11.9) ở m0.5. Qua các draw giảm 70% và 55%.
- "IS thấp hơn ở T40/80": **sai**, IS tệ hơn ở cả 4 cell.
- "Trung tính ở T150": chỉ đúng ở m0.2. Ở m0.5 thì tệ hơn sau Holm.

**Cơ chế** (`results/ext_r4lfdropen_analysis/mechanism.json`, `secondary.json`):
- Trước calibration, interval của lfdr hẹp hơn đúng như kỳ vọng. Median width thô bằng 0.82 / 0.75 lần v5_1 ở T40 m0.2/m0.5, 0.91 / 0.90 ở T80, 0.92 / 0.94 ở T150.
- Nhưng vì mở ít hơn, recall của cặp thiếu thật trên data giảm: 0.642 → 0.421 và 0.805 → 0.547 ở T40; 0.887 → 0.704 và 0.923 → 0.748 ở T80; 0.983 → 0.896 và 0.979 → 0.902 ở T150. Recall trung bình qua các draw còn thấp hơn: 0.392 / 0.523 / 0.659 / 0.711 / 0.863 / 0.875. P trung bình của cặp thật chỉ 0.32–0.48 ở T40.
- Ở 83% / 80% run tại T40, data fit chỉ mở đúng sàn k. Hiếm có cặp nào ngoài sàn đạt P ≥ 0.5.
- Cặp bị sót tạo ra những lần trượt lớn. Để giữ coverage, width factor (T, missing) tune trên D-07H phải tăng: 2.3 → 3.6 ở T40, 2.6 → 3.0 ở T80, 2.3 → 2.4 ở T150. Sau calibration, width ở T40 lại **rộng hơn** v5_1: 1.29 / 1.17 lần.
- Median sai số tuyệt đối gần như không đổi (0.52 so với 0.55 ở T40 m0.2), nên phần thua đến từ đuôi của các cặp bị sót. Đây đúng là rủi ro Kilian (2001) nêu: underfitting làm hẹp interval giả tạo. Calibration bù lại nhưng bù đều cho mọi cặp, nên mất nhiều hơn phần được.
- Ở các cell không missing, 15/15 cell có hiệu đúng bằng 0 (cùng output).

**Run phụ** (mô tả; Holm 0.05 trong từng family). Gộp lại, lfdr tệ hơn có ý nghĩa ở **13/17** cell và tốt hơn ở **0/17**.

| Run | Cell | lfdr tệ hơn sau Holm | Ghi chú |
|---|---|---|---|
| scen latent3 | T40/80/150 × m0.2 | 2/3 | +0.690, +0.259; T150 +0.091 không đáng kể |
| scen noise0.1 | T40/80/150 × m0.2 | 2/3 | +0.491, +0.317; T150 +0.044 không đáng kể |
| scen noise0.3 | T40/80/150 × m0.2 | 2/3 | T40 −0.020 [−0.498, +0.369] hoà, với coverage 0.909 so với 0.850; T80 +0.568, T150 +0.373. Cả hai method đều under-cover ở T80/150 (0.84 / 0.77–0.79), giới hạn nhiễu đo đã biết |
| lag1 (calibrate trong run) | T25/40 × m0.2/0.5 | 3/4 | factor lfdr 3.3 so với 2.6–2.7 của v5_1 |
| lag4 (calibrate trong run) | T80/150 × m0.2/0.5 | 4/4 | +0.622, +0.664, +0.166, +0.202; factor 3.5 / 2.5 so với 2.2 / 2.2 |

### 3.3 Kết luận

`tolerant_v5_1_lfdr` **NOT RETAINED**. Không có frozen spec, và không chạy held-out nào.

Bài học cho thiết kế: với sàn k và pi0 cố định bằng k/m, EM gần như dồn toàn bộ khối lượng của f1 vào chính top-k cặp, nên opening theo xác suất thực tế gần như chỉ còn "mở top k". Ở T nhỏ, chỉ có 40–65% cặp thiếu thật nằm trong top k, vì bằng chứng gián tiếp (cặp không nối nhưng bị ảnh hưởng bởi cạnh thiếu) chiếm chỗ. Cái giá của việc bỏ sót lớn hơn cái lợi về variance. Kết quả này ủng hộ việc giữ K = max(3k, #p<0.10) của v5_1: mở thừa có giá rẻ, còn bỏ sót thì đắt.

Một version mới (cần quy tắc mới) chỉ đáng thử nếu sàn được giữ ở 3k, còn phần xác suất chỉ áp cho các cặp vượt sàn. Version đó gần với v5_1 hiện tại, nên lợi ích kỳ vọng nhỏ.

**Không phát hiện bug nào trong module có sẵn.** Một quan sát: `ext_narrow.select_open` cho tập mở trung bình qua các draw (22.7 ở T40 m0.2) lớn hơn nhiều so với trên data (13.0), tức là trong các bootstrap draw có nhiều cặp đạt p < 0.10 hơn. Đây là hành vi đã có của v5_1, không phải lỗi.
