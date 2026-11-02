# TLP vòng 2: double bootstrap faithful và `targeted_lp_cal` không phụ thuộc cache (ID `tlp2`, mục R2-8)

**Trạng thái.** Baseline, rule mô tả (descriptive), exploratory trên D-07 development. Tiếp nối hướng `tlp` của vòng 1 ([tlp.md](tlp.md)). Code: [src/paper4/ext_tlp2.py](../../src/paper4/ext_tlp2.py) (module mới; `ext_tlp.py` của vòng 1 không bị sửa, chỉ được import). Không đụng P4-H2, P4-H1 hay confirmatory split nào. Không gọi LLM.

## 0. Lần chạy bị ngắt và việc tiếp tục

Lần thử đầu của vòng 2 bị ngắt vì usage limit khoảng 02:50 ngày 2026-11-02. Trước khi bị ngắt, nó đã tạo:
- `src/paper4/ext_tlp2.py` (phương pháp `tlp2_db`, `tlp2_db90`, `tlp2_lp_cal`);
- [experiments/ext/tlp2/check_impl.py](../../experiments/ext/tlp2/check_impl.py) → `results/ext_tlp2_checks/check_impl.json` (D-07H development);
- probe thiết kế `ext_tlp2_probe` (D-07H development, 6 topology, T = 80) → `results/ext_tlp2_probe/` (có `summary.md`, tức là chạy xong).

Lần đó **chưa chạy gì trên D-07** và chưa ghi rule. Lần này (sau khi resume) giữ nguyên các file trên, thêm phương pháp `tlp2_db_p3` vào `ext_tlp2.py` (module chưa được đánh giá; ba phương pháp cũ không đổi) và một smoke test trên D-07H (mục 3).

## 1. Hai việc của R2-8

**(a) Double bootstrap faithful.** Synthesis vòng 1 (mục 1.3) ghi: probe double bootstrap của vòng 1 "không faithful" (B2 = 49, p = 3, mức 95%), và ở T80 none nó tốt hơn bản single-level có ý nghĩa (−0.59 [−1.14, −0.18]), cỡ bằng biên thắng của v4 ở T80 none/extra. Câu hỏi: kết luận "v4 thắng TLP ở T ≥ 80" có còn đứng khi TLP được làm đúng như bài không?

**(b) Cache của `targeted_lp_cal`.** Ở vòng 1, `targeted_lp_cal` lấy kết quả của `targeted_lp` qua cache module-level, nên phụ thuộc thứ tự gọi của runner (synthesis, mục 5). `tlp2_lp_cal` tự tính mỗi lần gọi.

## 2. Các phương pháp (đều chỉ thấy data, public skeleton; không đọc stated damage, trừ việc runner calibrate width theo stated kind cho `tlp2_lp_cal`)

| Tên | Là gì | So với vòng 1 |
|---|---|---|
| `tlp2_db` | MSDB của Nemtyrev & Boldea: B1 = 200, B2 = 100 (đúng bài), interval eq. 27–28 ở **mức 95%** | Bỏ D1 (single-level), D3 (p = 3), D6 (mẫu LP chung). **p = 2q = 4** khi LP ở horizon cuối còn ≥ 5 residual dof (khớp (p, q) = (8, 4) của phần thực nghiệm và p − q = 2 của simulation chính (10, 8)); ở T = 40 chỉ p = 1 khả thi. Mẫu LP riêng theo horizon (t = p..T−1−h) như stacked regression của bài |
| `tlp2_db90` | Cùng tính toán với `tlp2_db` (dùng chung kết quả), interval ở **mức 90% của bài** | Chỉ để mô tả: coverage so với danh nghĩa 0.90, width, IS ở α = 0.10. Không vào rule (IS ở α = 0.05 không phải proper score cho interval 90%) |
| `tlp2_db_p3` | Như `tlp2_db` nhưng p = lag_max + 1 = 3 (p của vòng 1, `ext_tlp._lp_lags`) | Sensitivity: tách ảnh hưởng của p khỏi ảnh hưởng của double bootstrap. Chỉ chạy ở T ≥ 80 (ở T = 40 cả hai đều p = 1, tức là cùng estimator) |
| `tlp2_lp_cal` | `ext_tlp.targeted_lp` không đổi (single-level, B = 199), seed theo nội dung input, không cache; runner nới width theo (T, stated kind) trên D-07H như v4 | Thay `targeted_lp_cal`. Không phải phương pháp đã công bố |
| `targeted_lp` | Bản vòng 1, chạy lại | Seed giờ cố định theo tên (`ext_seed`), nên số không trùng bit-for-bit với vòng 1 |

Giữ nguyên từ vòng 1 (bài không nói hoặc bối cảnh buộc): target = plug-in SVAR trên skeleton (q = lag_max = 2); shock nhận dạng theo cha cùng kỳ trong skeleton; unit structural shock; C(H) = Σ_h β^TLP_h với weight riêng theo (h, cặp); v chặn trong [0, 1]; bootstrap DGP = VAR(q) không ràng buộc, moving block dài round(T^{1/3}), residual rescale, companion radius chặn ở 0.98; trong tầng 2, weight của TLP dùng moment tầng 2 của chính mẫu tầng 1 đó (D7).

**Seed và cache.** Mọi phương pháp `tlp2_*` lấy bootstrap từ generator seed theo **nội dung** input (bytes của data, skeleton, lag_max, H, tag của phương pháp), không theo stream của runner. `tlp2_db` và `tlp2_db90` dùng chung một cache, nhưng cache miss cho đúng kết quả cũ (đã kiểm). `tlp2_lp_cal` không dùng cache.

## 3. Kiểm tra trước khi ghi rule (D-07H development, không phải bank đánh giá)

**Implementation** (`results/ext_tlp2_checks/check_impl.json`):
- SVAR batch so với `ext_tlp.var_responses`: sai khác tối đa 1.5e−14.
- T = 20000, skeleton đúng: LP theo horizon so với truth tối đa 0.033; SVAR so với truth 0.029; LP theo horizon so với LP mẫu chung 0.0003.
- Cache: `tlp2_db90` gọi lạnh (cache trống) trùng hệt khi gọi sau `tlp2_db`; `tlp2_lp_cal` gọi theo hai thứ tự khác nhau với hai rng khác nhau cho interval trùng hệt.
- Thời gian một lần gọi MSDB (B1 = 200, B2 = 100): 3.3 s (T = 40, p = 1), 7.0 s (T = 80, p = 4), 9.1 s (T = 150, p = 4).
- Tỷ số width 90%/95% (trung vị) 0.78.

**Probe thiết kế `ext_tlp2_probe`** (6 topology, 1 replicate, T = 80; `results/ext_tlp2_probe/summary.md`). Cov / IS:

| T80 | `targeted_lp` | `tlp2_db` | `tlp2_db90` | db − single [CI 95%] |
|---|---|---|---|---|
| none | 0.920 / 4.47 | 0.900 / 5.11 | 0.836 / 5.99 | +0.64 [−0.26, +1.67] |
| extra 0.5 | 0.896 / 4.81 | 0.891 / 4.90 | 0.836 / 5.78 | +0.09 [−1.31, +1.65] |
| missing 0.5 | 0.866 / 5.45 | 0.816 / 6.05 | 0.687 / 8.47 | +0.60 [−1.02, +2.22] |

Đọc: với p = 4, bản faithful không tốt hơn bản single ở 6 topology này, ngược hướng với probe vòng 1 (p = 3, B2 = 49: −0.59 ở T80 none). Vì vậy thêm `tlp2_db_p3`.

**Smoke test `ext_tlp2_smoke`** (2 topology D-07H, T = 80, cell none và reversed 0.5; `results/ext_tlp2_smoke/summary.md`): kiểm tra driver lọc cell [experiments/ext/tlp2/run_cells.py](../../experiments/ext/tlp2/run_cells.py) và hệ số frozen của v4 (nạp đúng `mod|80|*` = 1.3/1.3/1.3/1.4). Ở 2 topology đó `tlp2_db_p3` có IS thấp hơn `targeted_lp` (−0.53 ở none). **Công bố:** quyết định chạy `tlp2_db_p3` ở **mọi** cell T ≥ 80 (thay vì chỉ T80 none/extra như dự định lúc thêm nó) được đưa ra sau khi thấy smoke test này.

## 4. Thiết kế đánh giá

- **Bank:** D-07 development, seed_base 20261102, 20 topology × 3 replicate, H = 4, n_boot = 199. Danh sách kinds giữ nguyên [extra, missing, reversed] để skeleton hỏng và data trùng với a2_baselines / ext_tlp_eval.
- **Calibration** của `tlp2_lp_cal`: D-07H development, khối calibration của a3_ges. v4 dùng `experiments/calibration/tolerant_v4_frozen.json`.
- **Driver** `run_cells.py`: chạy runner không đổi, chỉ bỏ những cell không nằm trong `only_cells` ở phase main (skeleton vẫn sinh với đủ danh sách kinds, nên seed và pairing không đổi). Lý do: MSDB tốn 3–9 s mỗi lần gọi; cả grid 21 cell × 60 run × (db + db_p3) quá 20 phút cho một run. **Grid được chia thành 8 run, mỗi run ước tính ≤ 15 phút**, không bỏ cell nào:

| Config | T | Cell | Phương pháp |
|---|---|---|---|
| `ext_tlp2_t40` | 40 | 7 cell | v4, targeted_lp, tlp2_lp_cal, tlp2_db, tlp2_db90 |
| `ext_tlp2_t80a` | 80 | none, extra 0.2/0.5 | như trên + tlp2_db_p3 |
| `ext_tlp2_t80b` | 80 | missing 0.2/0.5 | như trên + tlp2_db_p3 |
| `ext_tlp2_t80c` | 80 | reversed 0.2/0.5 | như trên + tlp2_db_p3 |
| `ext_tlp2_t150a` | 150 | none | như trên + tlp2_db_p3 |
| `ext_tlp2_t150b` | 150 | extra 0.2/0.5 | như trên + tlp2_db_p3 |
| `ext_tlp2_t150c` | 150 | missing 0.2/0.5 | như trên + tlp2_db_p3 |
| `ext_tlp2_t150d` | 150 | reversed 0.2/0.5 | như trên + tlp2_db_p3 |

Thứ tự chạy: t80a, t80b, t40, t150c (các cell R2-8 bắt buộc: T80 none/extra và missing ở mọi T), rồi t80c, t150a, t150b, t150d. Nếu một run bị ngắt trước khi có `summary.md`, chạy lại đúng config đó và ghi lại ở đây.

Scorer: [experiments/ext/tlp2/score.py](../../experiments/ext/tlp2/score.py) → `results/ext_tlp2_rules/rules.md`, `rules.json`. Mọi số trong mục 6 lấy từ hai file này.

## 5. Quy tắc ghi trước (ghi trước khi chạy bất kỳ config nào trên D-07)

Ghi xong lúc 2026-11-02T02:28Z (09:28 giờ máy). Run đầu tiên trên D-07 (`ext_tlp2_t80a`) khởi chạy sau thời điểm này.

Đây là rule mô tả: không giữ hay loại phương pháp nào. Nó quyết định câu nào paper được phép viết.

**Thống kê mỗi cell.** Với mỗi cell (T, kind, rate) và mỗi phiên bản X ∈ {`targeted_lp`, `tlp2_db`, `tlp2_db_p3`, `tlp2_lp_cal`}: d = trung bình hiệu IS ghép cặp (v4 − X) qua các run; CI 95% percentile và p-value hai phía từ bootstrap resample topology (10000 lần, seed 0); p = 2·min(P*(d* ≤ 0), P*(d* ≥ 0)), sàn 1/10000. Coverage = coverage gộp trên cặp non-null (cặp lost tính là không phủ).

**Hai view, cùng báo cáo:**
- *Gate view* (như R1 vòng 1): v4 thắng nếu cov(v4) ≥ 0.90 và cận trên CI < 0; X thắng nếu cov(X) ≥ 0.90 và cận dưới CI > 0; còn lại hòa.
- *Pure-IS view*: như trên, bỏ hai điều kiện coverage.

**Holm.** Trong mỗi (phiên bản, view, họ), họ = (i) 12 cell hỏng ở T ≥ 80; (ii) mọi cell hỏng đã chạy cho phiên bản đó (18; 12 với `tlp2_db_p3`). Một lần thắng "qua Holm" nếu hướng đúng, Holm-adjusted p < 0.05, và (gate view) điều kiện coverage đạt. Báo số thắng thô và số thắng qua Holm.

**Cell không hỏng** (T = 40/80/150): báo cáo verdict từng cell theo hai view, không vào họ Holm.

**Claim A — câu "v4 thắng TLP ở T ≥ 80"**, xét trên các phiên bản TLP đã công bố {`targeted_lp`, `tlp2_db`, `tlp2_db_p3`}:
- **A (không điều kiện)** nếu với **mỗi** phiên bản: v4 thắng 12/12 cell hỏng T ≥ 80 theo gate view, **cả 12 qua Holm**, và 0 cell thua theo pure-IS view.
- **A' (có điều kiện)** nếu không đạt A nhưng với mỗi phiên bản: v4 thắng ≥ 10/12 theo gate view, 0 cell thua theo cả hai view. Câu được phép: "v4 thắng TLP ở phần lớn cell T ≥ 80 (min k/12 qua các phiên bản), không thua cell nào".
- **Không được hỗ trợ** nếu không đạt A'. Khi đó chỉ được báo số đếm.
- **Thiếu** nếu một run không hoàn thành; khi đó claim dựa trên các cell có, ghi rõ.

**Claim B** (cùng tiêu chí, riêng `tlp2_lp_cal`): "v4 thắng cả TLP đã calibrate width ở T ≥ 80". Báo riêng, vì đây là chuyển thể của nhóm.

**Câu hỏi handicap** (R2-8): trong mỗi cell, `tlp2_db` (và `tlp2_db_p3`) "tốt hơn" `targeted_lp` nếu cov ≥ 0.90 và cận trên CI của (X − targeted_lp) < 0; "tệ hơn" nếu cận dưới > 0. Đặc biệt báo T80 none/extra.

**Kiểm tra pairing (ghi trước):** IS từng run của v4 phải trùng với `results/ext_tlp_eval/runs.jsonl` ở mọi run ghép được (v4 frozen, cùng data và skeleton). Nếu không trùng, kết quả vẫn báo nhưng ghi rõ lỗi pairing.

**Dự đoán (không phải rule):**
- v4 thắng `targeted_lp` 12/12 cell hỏng T ≥ 80 (như vòng 1), và thắng `tlp2_db` 12/12.
- `tlp2_db` có coverage < 0.90 ở cell missing 0.5 (probe: 0.816).
- `tlp2_db_p3` tốt hơn `targeted_lp` ở T80 none (vòng 1 và smoke), nhưng v4 vẫn thắng nó ở T80 none/extra; v4 thắng nó ≥ 10/12.
- Ở T = 40, `tlp2_db` không tốt hơn `targeted_lp` (verifier vòng 1: +0.42 ở T40 none).

## 6. Gián đoạn lần 2 và chạy lại (ghi trước khi chạy lại, 2026-11-02T03:31Z)

Lần thử thứ hai cũng bị ngắt vì usage limit lúc khoảng 03:24Z (10:24 giờ máy), giữa run `ext_tlp2_t80c` (log: [experiments/ext/tlp2/logs/run_all.log](../../experiments/ext/tlp2/logs/run_all.log)). Trạng thái lúc đó:
- Đã xong, có `summary.md` và `runs.jsonl`: `ext_tlp2_t80a`, `ext_tlp2_t80b`, `ext_tlp2_t40`, `ext_tlp2_t150c`. Dùng nguyên, không chạy lại.
- `ext_tlp2_t80c`: chỉ có `calibration.json`, không có `runs.jsonl`/`summary.md`, tức là không có kết quả. Chạy lại **đúng config đó, không đổi gì** (rule ở mục 5 không đổi).
- Chưa chạy: `ext_tlp2_t150a`, `ext_tlp2_t150b`, `ext_tlp2_t150d`. Chạy theo thứ tự đã ghi.

Lần resume này chưa xem `summary.md` của bốn run đã xong trước khi khởi chạy phần còn lại (chỉ kiểm tra file nào tồn tại). Log của phần chạy lại: `experiments/ext/tlp2/logs/run_resume.log`. Các dòng còn lại trong log là `RuntimeWarning` của numpy matmul (dòng nguồn bị in ra sau khi lọc chữ "warning"); chúng có ở mọi run, kể cả các run đã xong.

## 7. Kết quả (ghi sau khi chạy; rule ở mục 5 không đổi)

**Hoàn thành.** Đủ 8 run, 7140 dòng, 0 fail, 0 trùng (`results/ext_tlp2_rules/rules.md`, `rules.json`, sinh bởi `score.py` không đổi). Thời gian: t80c 9 phút (chạy lại sau gián đoạn, mục 6), t150a 6 phút, t150d 11 phút. **t150b kéo dài 95 phút wall-clock** (03:45Z → 05:20Z) vì máy vào sleep do pin 2% từ 10:56 đến 12:15 giờ máy (`pmset -g log`); thời gian tính thật khoảng 16 phút. Không có run nào bị chạy lại ngoài t80c.

### 7.1 Lỗi pairing (kiểm tra ghi trước, mục 5): KHÔNG đạt, kèm nguyên nhân

`tolerant_v4` trùng `ext_tlp_eval` ở **660/1260** run. 600 run lệch đều nằm ở các cell T80/T150 missing, reversed và T150 extra. Nguyên nhân là **lỗi của driver của chính hướng này** ([run_cells.py](../../experiments/ext/tlp2/run_cells.py)), không phải của runner: runner seed bootstrap của method built-in và ext method dùng rng runner bằng `rng([unit, 3, T, c_idx, tag])`, trong đó `c_idx` là **vị trí** của cell trong dict skeleton (`experiments/run_experiment.py:180–181`). Driver bỏ các cell không chạy khỏi dict, nên `c_idx` của các cell phía sau bị dịch. Data, skeleton và hệ số width frozen của v4 không đổi; chỉ bootstrap draw của v4 (và của `targeted_lp`) ở các cell đó là draw mới. Các phương pháp `tlp2_*` seed theo nội dung nên không bị ảnh hưởng. Docstring của `run_cells.py` ("same seeds") vì vậy sai; file không được sửa vì các run đã dùng nó. Cell trùng bit-for-bit: mọi cell T40, T80 none/extra, T150 none (cell đứng đầu thứ tự, hoặc config chạy đủ cell).

Độ lớn của nhiễu Monte Carlo này (`results/ext_tlp2_rules_v4r1/v4_seed_noise.json`): trung bình |ΔIS| từng run của v4 là 0.06–0.15, trung bình có dấu theo cell nằm trong [−0.036, +0.043].

**Phân tích độ nhạy (thêm sau khi thấy lỗi pairing, không phải rule):** [score_v4r1.py](../../experiments/ext/tlp2/score_v4r1.py) chấm lại đúng rule đó sau khi thay mọi dòng v4 bằng dòng v4 của `ext_tlp_eval` (cùng data, skeleton, hệ số; draw của vòng 1) → `results/ext_tlp2_rules_v4r1/rules.md`, `rules.json` (pairing 1260/1260).

### 7.2 Số đếm cell (copy từ `results/ext_tlp2_rules/rules.md`)

| version | view | family | cells | v4 wins | v4 wins (Holm) | X wins | X wins (Holm) | ties |
|---|---|---|---|---|---|---|---|---|
| targeted_lp | gate | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| targeted_lp | gate | all | 18 | 13 | 11 | 0 | 0 | 5 |
| targeted_lp | pure | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| targeted_lp | pure | all | 18 | 13 | 11 | 2 | 2 | 3 |
| tlp2_db | gate | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_db | gate | all | 18 | 14 | 14 | 0 | 0 | 4 |
| tlp2_db | pure | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_db | pure | all | 18 | 14 | 14 | 2 | 2 | 2 |
| tlp2_db_p3 | gate | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_db_p3 | gate | all | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_db_p3 | pure | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_db_p3 | pure | all | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_lp_cal | gate | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_lp_cal | gate | all | 18 | 13 | 12 | 2 | 2 | 3 |
| tlp2_lp_cal | pure | T>=80 | 12 | 12 | 12 | 0 | 0 | 0 |
| tlp2_lp_cal | pure | all | 18 | 13 | 12 | 2 | 2 | 3 |

Verbatim:

> ## Claim A (published TLP versions, T >= 80): **A (unqualified)**
> `{"targeted_lp": {"gate": 12, "gate_holm": 12, "n": 12, "losses_gate": 0, "losses_pure": 0}, "tlp2_db": {"gate": 12, "gate_holm": 12, "n": 12, "losses_gate": 0, "losses_pure": 0}, "tlp2_db_p3": {"gate": 12, "gate_holm": 12, "n": 12, "losses_gate": 0, "losses_pure": 0}}`
> Claim B (calibrated adaptation tlp2_lp_cal, T >= 80): **A (unqualified)** `{"tlp2_lp_cal": {"gate": 12, "gate_holm": 12, "n": 12, "losses_gate": 0, "losses_pure": 0}}`

Hai cell X thắng ở họ "all" đều là T40 missing 0.2/0.5: `targeted_lp` và `tlp2_db` chỉ thắng theo pure-IS (coverage 0.868/0.828 và 0.848/0.793, dưới 0.90); `tlp2_lp_cal` thắng theo cả hai view (coverage 0.965/0.950, IS 4.86/4.84 so với v4 7.77/7.53).

**Độ nhạy (v4 draw vòng 1):** Claim A hạ xuống **A'**. `targeted_lp` còn 11/12 (11 qua Holm), vì T80 missing 0.2 thành hòa: v4 − targeted_lp = −0.18 [−0.38, +0.02], p = 0.076 (bản chính: −0.22 [−0.42, −0.02], p = 0.030; vòng 1 với cả hai draw vòng 1: −0.20 [−0.37, −0.01]). `tlp2_db` và `tlp2_db_p3` vẫn 12/12 qua Holm, `tlp2_lp_cal` vẫn 12/12. Không phiên bản nào thắng v4 ở cell T ≥ 80 theo view nào, ở cả hai cách chấm.

### 7.3 Câu hỏi handicap (R2-8)

Hiệu IS (X − targeted_lp), "tốt hơn" = cov(X) ≥ 0.90 và cận trên CI < 0:
- `tlp2_db` (faithful, p = 2q = 4, B2 = 100): **tốt hơn 0/21 cell, tệ hơn 15/21**. Ở T80 none/extra nó tệ hơn +0.71 đến +0.81. Double bootstrap faithful với p của bài không làm TLP mạnh lên; nó làm TLP yếu đi.
- `tlp2_db_p3` (MSDB với p = 3 của vòng 1): tốt hơn 5/14 (T80 none −0.23 [−0.41, −0.02], extra 0.2 −0.19, extra 0.5 −0.19; T150 none −0.07; T150 extra 0.5 −0.05), tệ hơn 6/14 (mọi cell missing; reversed 0.5). Tín hiệu −0.59 của probe vòng 1 ở T80 none có cùng hướng nhưng nhỏ hơn khoảng ba lần trên 20 topology. Dù vậy v4 vẫn thắng `tlp2_db_p3` ở T80 none/extra: −0.37 [−0.54, −0.20], −0.41 [−0.59, −0.22], −0.33 [−0.50, −0.16].
- Ở mức danh nghĩa 90% của bài, `tlp2_db90` có coverage 0.71–0.91; chỉ T150 none/extra đạt ≥ 0.90.

### 7.4 Đối chiếu dự đoán

Cả bốn dự đoán đều đúng: v4 thắng `targeted_lp` và `tlp2_db` 12/12 (bản chính); `tlp2_db` có coverage < 0.90 ở missing 0.5 (0.825 ở T80, 0.864 ở T150); `tlp2_db_p3` tốt hơn `targeted_lp` ở T80 none nhưng v4 vẫn thắng nó 12/12; ở T40, `tlp2_db` không tốt hơn `targeted_lp` (none +0.13 [−0.07, +0.34]).

### 7.5 Câu paper được phép viết

Theo rule, bản chính cho phép claim A, nhưng nó dựa trên một cell sát biên (T80 missing 0.2 so với `targeted_lp`) mà kết luận đổi theo bootstrap seed của chính v4. **Câu khuyến nghị là câu A' (an toàn ở cả hai cách chấm):**

> Ở T ≥ 80, `tolerant_v4` có interval score thấp hơn Targeted Local Projections (Nemtyrev & Boldea 2026) ở 12/12 cell bị hỏng so với bản double bootstrap đúng bài (B1 = 200, B2 = 100, p = 2q) và bản double bootstrap với p = q + 1, và ở 11–12/12 cell so với bản bootstrap một tầng; mọi lần thắng đều qua Holm trong 12 cell. TLP không tốt hơn ở cell nào, dù có hay không có cổng coverage ≥ 0.90. Dùng double bootstrap đúng bài không làm TLP mạnh lên: bản đó tệ hơn bản một tầng ở 15/21 cell. Ở T = 40 thì không có câu "v4 thắng": TLP có IS thấp hơn ở hai cell thiếu cạnh nhưng under-cover (0.79–0.87), còn bản TLP được calibrate width thắng v4 ở hai cell đó.

Mọi kết quả đều exploratory, trên D-07 development.

## 8. Frozen spec for P4-H2 (chỉ là đề xuất, KHÔNG chạy)

TLP là **baseline**, không phải phương pháp của Paper 4. Đây là ứng viên để biến câu baseline ở 7.5 thành câu confirmatory, nếu orchestrator muốn đưa nó vào run niêm phong.

- **Phương pháp:** `tolerant_v4` (frozen), `targeted_lp` (module `src/paper4/ext_tlp.py`, không đổi), `tlp2_db` và `tlp2_db_p3` (module `src/paper4/ext_tlp2.py`, trạng thái hiện tại). Không có phương pháp calibrate (`tlp2_lp_cal` là chuyển thể, không đưa vào).
- **Config:** [experiments/configs/ext_tlp2_p4h2.json](../../experiments/configs/ext_tlp2_p4h2.json). `"bank": "P4-H2"`, `"split": "confirmatory"`, T = [80, 150], đủ kinds [extra, missing, reversed] × rates [0.2, 0.5] cùng none, 3 replicate, H = 4, n_boot = 199, seed_base 20261102, `"frozen_calibration": "experiments/calibration/tolerant_v4_frozen.json"`, khối calibration D-07H development (bắt buộc vì runner calibrate khi có `tolerant_v4`; hệ số của v4 sau đó bị file frozen ghi đè).
- **Lệnh:** `python3 experiments/run_experiment.py --config experiments/configs/ext_tlp2_p4h2.json --workers 3`. Chạy **trực tiếp bằng runner, không qua `run_cells.py`** (lỗi `c_idx`, mục 7.1). Chi phí ước tính theo số đo ở đây (MSDB khoảng 7–9 s một lần gọi, 2 phiên bản MSDB): khoảng 6 phút cho mỗi cell trên 60 run, tức là khoảng 80 phút cho 14 cell nếu P4-H2 cùng cỡ D-07 (20 topology × 3). Run này vượt ngân sách 20 phút; nó chỉ chạy một lần.
- **Chấm:** `python3 experiments/ext/tlp2/score.py --runs p4h2 --out results/ext_tlp2_p4h2_rules`, không đổi code. Kiểm tra pairing với `ext_tlp_eval` sẽ là 0/0 vì khác bank; bỏ qua mục đó.
- **Rule confirmatory (ghi trước, giống hệt mục 5, giới hạn ở họ T ≥ 80):** với mỗi X ∈ {`targeted_lp`, `tlp2_db`, `tlp2_db_p3`} và mỗi cell trong 12 cell hỏng ở T ∈ {80, 150}: d = trung bình hiệu IS ghép cặp (v4 − X); CI 95% percentile và p hai phía từ bootstrap theo topology (10000 lần, seed 0). Gate view: v4 thắng nếu cov(v4) ≥ 0.90 và cận trên < 0; X thắng nếu cov(X) ≥ 0.90 và cận dưới > 0. Pure-IS view: như trên, bỏ điều kiện coverage. Holm trong 12 cell cho mỗi (X, view).
  - **Xác nhận mạnh (A):** với mỗi X, v4 thắng 12/12 theo gate view, cả 12 qua Holm (p_Holm < 0.05), và 0 cell X thắng theo pure-IS view.
  - **Xác nhận (A'):** không đạt A nhưng với mỗi X, v4 thắng ≥ 10/12 theo gate view (đếm cả số qua Holm) và 0 cell X thắng theo cả hai view.
  - **Không xác nhận:** các trường hợp còn lại. Khi đó paper chỉ báo số đếm.
  - Yêu cầu là "với mỗi X" (intersection-union), nên không cần hiệu chỉnh thêm giữa ba phiên bản.

**Ghi chú thời gian** (`results/ext_tlp2_rules/run_timing.json`): các run của lần thử hai mất t80a 22 phút (vượt nhẹ ngân sách khoảng 20 phút, vì có 3 cell × 2 bản MSDB), t80b 12, t40 11, t150c 11 phút. Luôn dùng `--workers 3`.

## Sửa sau kiểm chứng vòng 2

Append một lần (R3-6, owner `tlp3`, 2026-11-02). Phần trên không sửa. Nguồn: synthesis vòng 2 (mục 1.7, bảng 3.2 dòng P5, mục 6), `results/ext_verify2_tlp2/`, `results/ext_tlp3_checks/`.

1. **Câu về double bootstrap (mục 7.3 và 7.5) bị lẫn yếu tố.** `tlp2_db` đổi cùng lúc ba thứ: double bootstrap, p từ 3 lên 2q = 4, và mẫu LP theo horizon. Câu "Dùng double bootstrap đúng bài không làm TLP mạnh lên: bản đó tệ hơn bản một tầng ở 15/21 cell" vì vậy **không được** đọc là hiệu ứng của riêng double bootstrap. Bản tách riêng double bootstrap (`tlp2_db_p3`, p = q + 1) **tốt hơn** `targeted_lp` ở 5/14 cell (T80 none −0.23 [−0.41, −0.02], extra 0.2 −0.19, extra 0.5 −0.19, T150 none, T150 extra 0.5) và tệ hơn ở 6/14. Thiệt hại của `tlp2_db` chủ yếu đến từ p = 4. Câu thay thế:
   > Cấu hình đúng bài (MSDB, B1 = 200, B2 = 100, p = 2q) tệ hơn bản bootstrap một tầng ở 15/21 cell; MSDB với p = q + 1 tốt hơn bản một tầng ở cell sạch/extra nhưng tệ hơn ở mọi cell missing; v4 vẫn thắng mọi phiên bản ở mọi cell hỏng T ≥ 80.
2. **Claim B là "widen-only calibration", không phải một baseline calibrate độc lập ở T80.** Grid width của runner bắt đầu từ 1.0 (bug E2), nên calibration chỉ nới được. Ở T80, `tlp2_lp_cal` nhận factor 1.0 cho stated none/extra/reversed (5/7 cell T80) và 1.1 cho missing (`results/ext_tlp3_checks/lp_cal_factors.json`; synthesis ghi "5/6", số chính xác là 5/7 cell, gồm cell none). Ở 5 cell đó nó thực chất là `targeted_lp` (IS lệch ≤ 0.02, do seed theo nội dung). Claim B ở T80 vì vậy gần như lặp lại Claim A cho `targeted_lp`. Mọi chỗ gọi `tlp2_lp_cal` phải ghi "TLP với widen-only width calibration".
3. **Hai lần gián đoạn là hai sự kiện khác nhau.** Lần 1 khoảng 02:50 giờ địa phương (+07:00), tức 19:50Z ngày 2026-11-01: chưa chạy gì trên D-07 và chưa ghi rule (mục 0). Lần 2 lúc 10:24 giờ địa phương (03:24Z), giữa run `ext_tlp2_t80c`; run đó được chạy lại không đổi (mục 6). Câu ở mục 0 ("khoảng 02:50 ngày 2026-11-02") là giờ địa phương, không phải UTC. Thêm vào đó, `ext_tlp2_t150b` bị máy sleep khoảng 79 phút (mục 7), nhưng không phải gián đoạn của run.
4. **A' trong mục 8 và `score.py` không nhất quán về Holm.** Mục 8 viết "đếm cả số qua Holm", còn `score.py` (hàm `claim`) chỉ đòi ≥ 10 thắng thô theo gate view. Quyết định cuối (docs/ext/tlp3.md mục 2, ghi trước P4-H2): **A' bắt buộc Holm** cho số thắng, còn số thua đếm thô. Trên D-07 quyết định này không đổi verdict nào ở mục 7: dev rescore bằng analyzer mới cho A với bản chính và A' (`targeted_lp` 11/12, cả 11 qua Holm) với v4 draw vòng 1 (`results/ext_tlp3_checks/k3_k4_crosscheck.json`).
5. **Spec P4-H2 ở mục 8 bị thay thế.** `experiments/configs/ext_tlp2_p4h2.json` và `experiments/ext/tlp2/score.py --runs p4h2` **không được dùng** cho P4-H2. Lý do: claim B in ra "incomplete", pairing 0/0, khối db90 đọc config D-07, run fail bị bỏ qua âm thầm, và chưa có hash manifest. Spec thay thế: `experiments/configs/ext_tlp3_p4h2.json` + `experiments/ext/tlp3/analyze_p4h2.py` + `experiments/ext/tlp3/preflight.py`, manifest `experiments/ext/tlp3/p4h2_spec_files.json` (docs/ext/tlp3.md). Ước lượng "khoảng 80 phút" ở mục 8 được thay bằng số đo ở tlp3.md mục 7.
6. **Docstring của `experiments/ext/tlp2/run_cells.py` ("same seeds") sai.** Như mục 7.1 đã ghi, driver dịch `c_idx` (bug E1 của runner), nên draw của built-in method và `targeted_lp` đổi ở các cell không đứng đầu. File không sửa vì các run đã dùng nó.
