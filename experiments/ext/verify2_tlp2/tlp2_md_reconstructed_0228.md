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
