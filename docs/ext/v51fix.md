# Hướng "v51fix" (vòng 3, tiếp nối "v51"): sửa spec P4-H2 của `tolerant_v5_1` và các so sánh còn thiếu

**Trạng thái.** Exploratory. Đánh giá chỉ trên D-07 development (seed_base 20261102); calibration chỉ trên D-07H development. Không chạm P4-H2, P4-H1 hay confirmatory split nào; không chạy config P4-H2 nào. Đây là mục R3-2 của `docs/ext/synthesis_round2.md`.

Thư mục: code `src/paper4/ext_v51fix.py` (chỉ đăng ký biến thể sensitivity `tolerant_v5_1_t294`), script `experiments/ext/v51fix/`, config `experiments/configs/ext_v51fix_*.json`, kết quả `results/ext_v51fix_*`. Không sửa file có sẵn nào, trừ phần append "Sửa sau kiểm chứng vòng 2" vào `docs/ext/v51.md` và `docs/ext/narrow.md` (R3-6).

Quy ước thống kê giống `docs/ext/v51.md`: hiệu IS ghép cặp (method − reference) theo run; CI 95% bootstrap theo topology (1000 lần, seed 0, đúng kiểu `paired_table` của runner); p một phía từ bootstrap theo topology B = 10 000 (seed 1); Holm step-down ở mức 0.025 cho mỗi chiều, trên đúng các cell của từng quy tắc đếm. Cổng coverage ≥ 0.90 là ngưỡng điểm, không phải kiểm định.

---

## 0. Quyết định về "tau / hybrid" (ghi lúc 2026-11-02T06:05Z, trước mọi run của vòng này)

**Quyết định: bỏ "tau / hybrid" khỏi mô tả method; giữ nguyên code.** Method đi vào P4-H2 vẫn là đúng hàm `tolerant_v5_1` trong `src/paper4/ext_v51.py` (`TAU = 6.6083`), file không đổi một byte (sha256 `48bb21ad…a286`, như spec vòng 2). Không có method mới nào thay thế nó.

Lý do bỏ khỏi mô tả, và vì sao điều đó không làm method khác đi:
- Tỷ lệ r = (T − lag_max) / (1 + n·lag_max + |cạnh có hướng|/n). Với n = 14 và lag_max = 2, mẫu số ≥ 29 với mọi skeleton khai báo (kể cả skeleton rỗng). Vì vậy r ≤ (T − 2)/29: r ≤ 1.31 ở T = 40, ≤ 2.69 ở T = 80, ≤ **5.10 ở T = 150**, luôn < τ = 6.6083. Nhánh all-lag **không thể** được chọn ở T ≤ 150 với n = 14, bất kể dữ liệu hay damage. Nó chỉ có thể được chọn khi T ≥ 194 (skeleton rỗng) hoặc T ≥ 204 (21 cạnh). P4-H2 có 14 nút và 21 cạnh mỗi topology (`data/topology_bank/PROVENANCE.md`), grid T ∈ {40, 80, 150}.
- Do đó trên grid đánh giá (D-07) và grid xác nhận (P4-H2), `tolerant_v5_1` **trùng từng phép tính** với "v5 có targeted opening đã de-duplicate, chọn lại trong mỗi bootstrap draw, prescale 0.5, calibration hai chiều". Mô tả đó là mô tả chính xác của code đã đánh giá trên vùng T của paper.
- Mô tả dùng trong paper: **"`tolerant_v5_1`: v5 với targeted lag opening đã de-duplicate, chọn lại trong từng bootstrap draw."** Chú thích bắt buộc: "Code chứa một nhánh dự phòng mở mọi lag khi r ≥ 6.61 (chỉ xảy ra khi T ≳ 194 với 14 nút); nhánh này không được dùng và không được đánh giá ở bất kỳ T nào trong paper. Ngưỡng 6.61 được chốt bằng một probe trên bank calibration, nằm trên ranh giới mong manh (11% seed bootstrap của probe cho 2.94) và không được claim như một tham số đã được kiểm chứng."
- Không gọi method là "hybrid" hay "lai". Không báo τ như một đóng góp.
- Spec P4-H2 mới kiểm điều này hai lần: preflight tính cận trên r giải tích cho T ∈ {40, 80, 150}, n = 14; analyzer đếm tỷ lệ run missing đi vào nhánh targeted (`info_v51_targeted`) và phải là 100%. Nếu không phải 100% (chỉ có thể xảy ra nếu topology không có 14 nút), verdict không đổi nhưng mô tả paper phải nhắc lại nhánh chuyển.

---

## 1. Quy tắc ghi trước cho các phân tích của vòng 3 (ghi lúc 2026-11-02T06:05Z, trước mọi script và mọi run)

### 1.A Ghép cặp miễn phí `tolerant_v5_1` với `tolerant_v4c` (và các baseline `*_c2` của cùng run)

**Nguồn.** `tolerant_v5_1` từ `results/ext_v51_eval/runs.jsonl`; `tolerant_v4c`, `pselect_union_c2`, `ida_union_c2`, `bvar_minnesota_c2` từ `results/ext_v4c_eval/runs.jsonl` (run do phiên chính chạy với `--workers 6` và miniconda numpy 2.5.4; kết quả v4c chưa được verifier độc lập kiểm, R3-7).

**Kiểm tra identity (làm trước, quyết định cách báo).** Với mỗi khoá (topology, replicate, T, kind, rate), dòng `tolerant_v4` của hai run phải trùng: cùng status, |ΔIS| < 1e-12, cùng `n_covered_nonnull` và `n_nonnull`, đủ 1260/1260 khoá. Nếu trùng: ghép cặp thật. Nếu chỉ lệch ở mức số thực (mọi số đếm trùng, |ΔIS| < 1e-9): vẫn ghép cặp (cùng dữ liệu, cùng skeleton hỏng), công bố mức lệch. Nếu số đếm lệch: chỉ báo so sánh trung bình không ghép cặp.

**Quy tắc đếm (mô tả).** Trên 21 cell (18 cell hỏng + 3 cell none): "v5_1 thắng X" nếu coverage v5_1 ≥ 0.90 và cận trên CI (v5_1 − X) < 0; "X thắng v5_1" nếu coverage X ≥ 0.90 và cận dưới CI > 0. Báo số đếm thô và sau Holm (21 cell, mỗi chiều), và báo riêng 2 cell T = 40 missing, 4 cell T = 80/150 missing.

**Tiêu chí mô tả "v5_1 bao trùm v4c" (synthesis vòng 2, mục 3.1).** Câu này được giữ nếu (i) v5_1 thắng v4c ở **cả hai** cell T = 40 missing sau Holm, và (ii) v4c thắng v5_1 ở **0/21** cell sau Holm. Nếu (ii) sai, câu phải viết lại, nêu rõ các cell v4c tốt hơn. Coverage của hai method ở T = 40 missing (v4c cao hơn) được báo cạnh câu này.

**Đã biết trước (công bố).** Từ synthesis vòng 2: ở T = 40 missing, v5_1 có IS 4.84 / 5.09, v4c 6.98 / 6.82; coverage v5_1 0.922 / 0.939, v4c 0.958 / 0.956. Phần (i) gần như chắc chắn đạt. Phần chưa biết là các cell còn lại.

### 1.B Ghép cặp miễn phí `tolerant_v5_1` với `pselect_union_v2`, `pselect_union_v2_cal`, `bvar_minnesota_v2_cal`

**Nguồn.** `results/ext_baselines2_eval/runs.jsonl` (R2-1). Kiểm tra identity của dòng `tolerant_v4` với `ext_v51_eval` như 1.A.

**Quy tắc đếm.** Như 1.A, trên 21 cell, với X ∈ {`pselect_union_v2`, `pselect_union_v2_cal`, `bvar_minnesota_v2_cal`} (báo kèm `bvar_minnesota_v2` thô). Báo riêng 4 cell chính T = 80/150 × missing-0.2/0.5 (thô và Holm trên 4 cell) và 2 cell T = 40 missing.

**Điều kiện đi kèm bắt buộc khi trích.** `pselect_union_v2` bị thiếu budget so với R2-1 (cap 4 graph, khoảng 80 draw mỗi graph; verifier vòng 2). Mọi câu "v5_1 thắng pselect_union_v2" thừa hưởng điều kiện này và **không** được viết thành "thắng baseline mạnh nhất". So sánh với bản đúng budget là việc của R3-1.

**Đã biết trước (công bố).** Synthesis: v4 − pselect_union_v2 ở T80 missing là −1.14 / −1.19, ở T150 là −0.10 / −0.07 (hòa); v5_1 − v4 ở T80 missing khoảng −0.4 / −0.6 và ở T150 missing −0.2 / −0.23. Vì vậy tôi dự đoán v5_1 thắng pselect_union_v2 ở T80 missing, và có thể thắng ở T150 missing. Đây không phải kiểm định độc lập.

### 1.C Sensitivity mô tả: v5_1 với τ ≈ 2.94, chỉ ở T = 150

**Kịch bản.** Verifier vòng 2 (`results/ext_verify2_v51/tau_fragility.json`): với 11% seed bootstrap của probe, cận trên CI của d(100) ≥ 0, nên T\* = 80 và τ = trung điểm r̄(80), r̄(100) của `probe_tau2` = (2.6033 + 3.2708)/2 = **2.9370**. Với τ đó, T = 40 (r ≈ 1.27) và T = 80 (r ≈ 2.60) vẫn đi nhánh targeted, còn T = 150 (r ≈ 4.94) đi nhánh all-lag. Vì vậy chỉ T = 150 cần chạy.

**Method.** `tolerant_v5_1_t294` trong `src/paper4/ext_v51fix.py`: đúng code của `ext_v51.tolerant_v5_1` (gọi lại `allag_ratio`, `tolerant_sel_dd`, `methods.tolerant`, `_prescale` của module gốc), chỉ khác hằng τ = 2.9370 và tên. Module chỉ đăng ký tên này (không đăng ký `tolerant_v5_1`, để không ghi đè method gốc trong runner, lỗi E4).

**Run.** `experiments/configs/ext_v51fix_t150tau.json`: D-07 development, seed_base 20261102, T = [150], damage kinds/rates như grid a2 (giữ danh sách cell để c_idx và dòng v4 trùng `ext_v51_eval`, lỗi E1), 20 topology × 3 replicate, n_boot 199, H = 4, methods `tolerant_v4` (frozen `tolerant_v4_frozen.json`) và `tolerant_v5_1_t294` (calibrate trên D-07H development như `ext_v51_eval`). `--workers 3`, ước tính dưới 15 phút.

**Ghép cặp.** Identity của 420 dòng `tolerant_v4` ở T = 150 với `ext_v51_eval` như 1.A. Nếu đạt, `tolerant_v5_1` (từ `ext_v51_eval`) được ghép với `t294`.

**Báo (mô tả, không đổi verdict hay spec nào):**
1. Tỷ lệ run missing đi nhánh all-lag dưới `t294` (phải là 100%).
2. Bảy cell T = 150: coverage / IS của v4, v5_1, t294; hiệu ghép cặp t294 − v5_1 và t294 − v4, CI 95%, Holm trên 7 cell mỗi chiều.
3. Áp lại C2 (6 cell hỏng T = 150: coverage ≥ 0.90 và IS ≤ 1.05 × v4) và C3 (T = 150 none: IS ≤ 1.05 × v4) cho t294, như mô tả.
4. Câu diễn giải ghi trước: nếu t294 − v5_1 có cận dưới CI > 0 ở cả hai cell T = 150 missing (sau Holm), thì "lợi thế của v5_1 ở T = 150 missing phụ thuộc vào việc τ rơi trên 4.94; trong kịch bản 11% seed, method sẽ mở mọi lag ở T = 150 và mất phần lợi đó". Nếu không, câu là "kết quả T = 150 không nhạy với τ trong kịch bản đó".
5. Ở 5 cell không phải missing, t294 và v5_1 cùng code path, chỉ khác stream bootstrap (seed theo tên) và factor calibrate; hiệu ở đó đo nhiễu Monte Carlo, báo để làm thang so sánh.

**Đã biết trước (công bố).** Vòng 2: v5_1 − `v5_cal2` ở T = 150 missing là −0.33 / −0.24 (khác stream và khác calibration), và `v5_cal2` gần v4 ở T = 150 (tỷ lệ IS 0.99–1.01). Tôi dự đoán t294 tệ hơn v5_1 khoảng 0.2–0.35 ở T = 150 missing và gần v4.

### 1.D Số chỉ có trong shell output

Ghi vào `results/ext_v51fix_shellonly/` kèm nguồn (transcript, timestamp): sanity check de-dup (02:23Z), timing run attempt 1 (19:47:56Z, d(40) = −3.596, d(200) = +0.151), thời gian mỗi fit (từ `probe_tau2.json`). Tính lại từ `results/ext_v51_eval/runs.jsonl` khoảng **theo từng run** của số term trùng trên fit dữ liệu gốc (sửa câu "3–17").

### 1.E Kiểm thử analyzer mới trước khi freeze (kiểm thử phần mềm, không phải đánh giá)

Analyzer mới `experiments/ext/v51fix/rule_p4h2_v2.py` được chạy ở chế độ `--dev-dryrun` trên `results/ext_v51_eval` (D-07 development, đã có kết quả) và phải tái lập đúng phán quyết vòng 2: C1 2/2 (Holm 2/2), C2 12/12, C3 7/7. Thêm các test lỗi cố ý trên bản sao trong scratchpad: (a) xoá mọi dòng `tolerant_v5_1` ok của một cell → phải ra NOT CONFIRMED, không crash; (b) đổi 4 dòng của một cell thành failed → vượt trần failure → NOT CONFIRMED; (c) đổi `info_c_T` của một dòng → validity FAIL. Output kiểm thử ghi vào `results/ext_v51fix_dryrun/`. Nếu không tái lập được, analyzer có lỗi và được sửa trước khi freeze; mọi lần sửa được ghi ở đây.

**Ghi chú thời điểm (theo mtime và `experiments/ext/v51fix/t150tau_started_utc.txt`).** Mục 0 và 1 ở trên được ghi xong lúc 06:04:31Z (trong doc ghi tròn "06:05Z"). Run `ext_v51fix_t150tau` bắt đầu lúc 06:04:57Z; script ghép cặp chạy lúc 06:05:35Z. Mọi phân tích đều chạy sau khi quy tắc đã được ghi.

---

## 2. Kết quả (append nguyên văn sau khi chạy; không đổi quy tắc)

### 2.A `tolerant_v5_1` so với `tolerant_v4c` và các baseline `*_c2` (chạy 06:05:35Z, 0 ước lượng mới)

Script `experiments/ext/v51fix/pair_v4c_bl2.py`; số liệu `results/ext_v51fix_pairs/pairs.md`, `pairs.json`.

**Identity: đạt.** Dòng `tolerant_v4` của `ext_v4c_eval` trùng `ext_v51_eval` 1260/1260 ở mức 1e-12 (max |ΔIS| = 0, mọi số đếm trùng), dù run v4c dùng `--workers 6` và miniconda numpy 2.5.4. Ghép cặp thật.

| X | v5_1 thắng X (thô / Holm 21) | X thắng v5_1 (thô / Holm 21) | T40 missing: v5_1 − X | T80 missing | T150 missing |
|---|---|---|---|---|---|
| `tolerant_v4c` | 6 / 6 (đúng 6 cell missing) | 1 / 0 (T80 none +0.06 [+0.01, +0.12]) | −2.14 [−2.64, −1.54]; −1.73 [−2.08, −1.34] | −0.38 [−0.49, −0.28]; −0.27 [−0.40, −0.14] | −0.28 [−0.34, −0.23]; −0.19 [−0.25, −0.12] |
| `pselect_union_c2` | 21 / 21 | 0 / 0 | −2.78; −2.28 | −1.05 [−1.19, −0.93]; −1.06 [−1.24, −0.87] | −0.88 [−0.99, −0.78]; −0.92 [−1.02, −0.81] |
| `ida_union_c2` | 12 / 12 | 0 / 0 | −17.3; −26.3 | −16.3; −27.6 | −14.4; −27.6 |
| `bvar_minnesota_c2` | 17 / 16 | 0 / 0 | −3.68; −2.25 | −4.95; −3.21 | −4.02; −2.93 |

**Tiêu chí ghi trước 1.A ("v5_1 bao trùm v4c"): ĐẠT.** (i) v5_1 thắng v4c ở 2/2 cell T40 missing sau Holm (21 cell); (ii) v4c thắng v5_1 ở 0/21 cell sau Holm (1/21 thô: T80 none). Ở 15 cell không phải missing, hai method hòa (|hiệu| ≤ 0.06). Điều kiện đi kèm: ở T40 missing, v4c cover cao hơn (0.958 / 0.956 so với 0.922 / 0.939); v5_1 đổi một phần coverage lấy interval hẹp hơn nhiều. Kết quả v4c vẫn chưa được verifier độc lập kiểm (R3-7); identity của dòng v4 chỉ xác nhận cùng dữ liệu và skeleton, không xác nhận cột v4c.

### 2.B `tolerant_v5_1` so với `pselect_union_v2(_cal)` và `bvar_minnesota_v2(_cal)`

**Identity: đạt** (1260/1260 ở 1e-12, max |ΔIS| = 0, với `ext_baselines2_eval`).

| X | v5_1 thắng X (thô / Holm 21) | X thắng v5_1 (thô / Holm 21) | 4 cell chính T80/150 missing: v5_1 thắng (thô / Holm 4 / Holm 21) | T40 missing |
|---|---|---|---|---|
| `pselect_union_v2` | 21 / 21 | 0 / 0 | 4 / 4 / 4 | 2 / 2 |
| `pselect_union_v2_cal` | 21 / 21 | 0 / 0 | 4 / 4 / 4 | 2 / 2 |
| `bvar_minnesota_v2_cal` | 9 / 7 | **4 / 2** | 4 / 4 / 4 | thô 1/2, Holm 0/2 (hòa) |
| `bvar_minnesota_v2` (thô) | 13 / 12 | 0 / 0 | 4 / 4 / 4 | 2 / 2 |

Số chính (v5_1 − X, CI 95%):
- `pselect_union_v2`: T80 missing −1.57 [−2.10, −1.05], −1.46 [−1.86, −1.08] (coverage của pselect_v2 chỉ 0.877 / 0.878); T150 missing −0.39 [−0.59, −0.23], −0.30 [−0.49, −0.14] (coverage pselect_v2 0.965 / 0.967). `_cal` ở T150 trùng bản thô (factor 1.0); ở T80 −1.65 [−2.05, −1.26], −1.46 [−1.74, −1.20].
- `bvar_minnesota_v2_cal`: T40 missing −0.41 [−0.92, +0.16] và −0.42 [−0.86, −0.04] (p một phía 0.016, không qua Holm 21): **hòa**. bvar_v2_cal **tốt hơn** v5_1 ở T40 extra-0.2 (+0.81 [+0.22, +1.58]) và extra-0.5 (+0.93 [+0.43, +1.59]) sau Holm, và ở T40 none (+0.64 [+0.13, +1.21]) và reversed-0.2 (+0.72 [+0.17, +1.44]) không hiệu chỉnh. Ở T80/150 missing v5_1 thắng nó rõ (−1.48 đến −2.02).

**Đọc kết quả.**
- Ở T150 missing, v4 chỉ hòa `pselect_union_v2` (synthesis 2.1), còn v5_1 thắng nó (−0.39, −0.30, qua Holm). Đây là ứng viên cho câu "không hòa mà thắng ở T150" — nhưng thừa hưởng nguyên điều kiện budget: `pselect_union_v2` có cap 4 graph và khoảng 80 draw mỗi graph. Bản đúng budget (R3-1) có thể thu hẹp biên này như nó đã làm với v4 ở T80. **Không được viết "v5_1 thắng baseline mạnh nhất".**
- Ở T40, baseline mạnh nhất với v5_1 không phải pselect mà là `bvar_minnesota_v2_cal`: hòa ở cell missing, và tốt hơn v5_1 ở cell extra/none/reversed-0.2 (C3 chỉ so v5_1 với v4, nên điểm này chưa từng hiện ra). Câu C-T40 của synthesis ("thắng `pselect_cal`, hòa `targeted_lp_cal`") phải thêm: "hòa `bvar_minnesota_v2_cal`; ở T40 trên cell không thiếu cạnh, `bvar_minnesota_v2_cal` có IS thấp hơn cả v4 lẫn v5_1 (2/5 cell qua Holm, 4/5 không hiệu chỉnh)". Phần so v4 với bvar_v2_cal ở các cell đó là của baselines2/R3-1, tôi không tính ở đây.

### 2.C Sensitivity τ ≈ 2.94 ở T = 150 (run 06:04:57Z–06:08:10Z, 193.6 s, 840 dòng, mọi run ok)

Script `experiments/ext/v51fix/tau_sens.py`; số liệu `results/ext_v51fix_t150tau/sens.md`, `sens.json`, run `results/ext_v51fix_t150tau/`.

- **Identity: đạt.** 420/420 dòng `tolerant_v4` ở T150 trùng `ext_v51_eval` ở 1e-12 (xác nhận rằng giữ danh sách cell thì c_idx không đổi, E1).
- **Nhánh:** 100% run missing của t294 đi nhánh all-lag (r̄ 4.90 / 4.98). Factor calibrate (runner) ở T150: missing 2.5 (v5_1 2.3), reversed 2.5 (2.4), none/extra 2.4 (2.4).

| cell T150 | v4 cov / IS | v5_1 cov / IS | t294 cov / IS | t294 − v5_1 | t294 − v4 |
|---|---|---|---|---|---|
| missing-0.2 | 0.968 / 2.057 | 0.966 / 1.759 | 0.974 / 2.085 | **+0.33 [+0.27, +0.39]** (Holm) | +0.03 [+0.00, +0.06] (p 0.030, không Holm) |
| missing-0.5 | 0.962 / 2.215 | 0.968 / 1.986 | 0.975 / 2.262 | **+0.28 [+0.20, +0.35]** (Holm) | +0.05 [+0.01, +0.09] (p 0.005, không Holm) |
| reversed-0.2 | 0.970 / 1.894 | 0.959 / 1.828 | 0.962 / 1.861 | +0.03 [+0.01, +0.06] (Holm) | −0.03 [−0.06, −0.01] (p 0.005, không Holm) |
| none / extra-0.2 / extra-0.5 / reversed-0.5 | | | | +0.004 / −0.014 / −0.020 / −0.003 (CI chứa 0) | CI chứa 0 |

- C2 áp lại cho t294 ở 6 cell hỏng T150: **6/6**; C3 (T150 none): **ĐẠT**. t294 tệ hơn v4 có ý nghĩa sau Holm: 0/7; tốt hơn: 0/7. t294 tệ hơn v5_1 sau Holm: 3/7 (2 cell missing và reversed-0.2); tốt hơn: 0/7.
- **Câu diễn giải theo quy tắc 1.C:** "**lợi thế của v5_1 ở T150 missing phụ thuộc vào việc τ rơi trên 4.94**". Trong kịch bản 11% seed (τ ≈ 2.94), method ở T150 missing sẽ là all-lag, IS ngang v4 (+0.03 / +0.05) và mất toàn bộ phần lợi −0.30 / −0.23 so với v4. Spec C2 vẫn đạt trong kịch bản đó (C2 chỉ đòi không tệ hơn 5%).
- **Thang nhiễu (mục 5 của quy tắc):** ở reversed-0.2, t294 và v5_1 chạy cùng code; khác biệt +0.03 (qua Holm) chỉ đến từ stream bootstrap và factor 2.5 so với 2.4. Tức là hiệu cỡ 0.03 trong khung này có thể đến từ chênh calibration ±0.1 factor. Các hiệu nhỏ (ví dụ +0.08 ở T80 reversed-0.5 trong C2 vòng 2) phải đọc theo thang này.
- Hệ quả cho paper: lợi thế ở T150 missing của v5_1 là kết quả của **targeted opening đã de-dup**, không phải của "τ". Vì thế quyết định ở mục 0 (bỏ τ khỏi mô tả) là đúng: method được mô tả và xác nhận là targeted-dedup ở mọi T ≤ 150; kịch bản τ ≈ 2.94 chỉ cho thấy rằng một thủ tục chọn τ khác hẳn có thể đã chọn nhánh kém hơn ở T150.

### 2.D Số chỉ có trong shell output (`results/ext_v51fix_shellonly/shell_only.md`, `shell_only.json`)

- Timing run attempt 1 (D-07H, 19:47:56Z, module còn bug, 1 topology): d(40) = −3.596 (0.2: −2.257; 0.5: −4.934), d(200) = +0.151 (0.2: −0.095; 0.5: +0.398); τ của smoke run đó 3.9383 (không dùng). Chép nguyên văn từ transcript `agent-a7558e999131276cc.jsonl`.
- Sanity check de-dup (D-07H, 02:23:49Z, 3 topology, T40 missing-0.5, n_boot 49): term trùng trên fit dữ liệu 8 / 12 / 4; cộng dồn qua draw 976 / 800 / 692; |lệch cận dưới| tối đa 1.98 / 2.51 / 1.69. Script của lần đó nằm trong scratchpad và không được giữ; chỉ output còn lại (transcript `agent-aecea0233cf01bed2.jsonl`).
- "1.9–2.5 s mỗi fit": từ trường `sec` của `probe_tau2.json`: targeted 1.87–2.53 s, all-lag 0.86–1.23 s mỗi fit ở T40–150 (T200: 2.89 / 1.39), dưới tải CPU chung.
- **Term trùng theo từng run (tính lại từ `results/ext_v51_eval/runs.jsonl`):** trên fit dữ liệu gốc **0–44 term mỗi run**; trung bình theo cell 3.1–16.7. Chỉ **290/360** run missing có term trùng trên fit dữ liệu gốc (cell T40 missing-0.2: 28/60); **360/360** có term trùng khi tính cả các bootstrap draw (700–8 752 term mỗi run). Câu "100% run missing có term trùng (3–17 term trên fit dữ liệu gốc)" của vòng 2 phải sửa như mục 4 dưới đây.

### 2.E Kiểm thử analyzer v2 (06:09–06:10Z; `results/ext_v51fix_dryrun/`)

- Dry run trên `ext_v51_eval` (D-07 development): tái lập đúng vòng 2: C1 2/2 (Holm 2/2), C2 12/12 (tệ hơn sau Holm 0/12), C3 7/7 (0/7); validity 6/6 PASS; 360/360 run missing đi nhánh targeted, r max 4.981. Overlay Bonferroni (97.5%, 98.33%) cũng đạt (cận trên −2.25 / −1.99 và −2.19 / −1.97). Output `results/ext_v51fix_dryrun/ruling_v2.md`.
- Test lỗi cố ý (bản sao trong scratchpad, output chép vào `results/ext_v51fix_dryrun/fault_tests/`): lần chạy đầu **crash** ở test "0 run ok" và "xoá dòng" (dòng in margin coverage định dạng None). Đã sửa dòng đó (chỉ phần in mô tả, không đổi điều kiện nào) trước khi freeze; chạy lại: cả 7 test cho NOT CONFIRMED đúng lý do, không crash: 0 run ok của v5_1 (vượt trần tổng 60 > 12, cell "0 ok runs"); dòng bị xoá (V3 FAIL); 4/60 run failed trong một cell (vượt trần cell); sai `info_c_T` (V5 FAIL); thiếu fingerprint (V6 FAIL); v4 0 run ok ở một cell; 3 run failed ở T80 reversed-0.5 (trong trần, nhưng coverage ITT 0.855 < 0.90).
- Preflight: self-test PASS 14/14 (`results/ext_v51fix_dryrun/preflight_selftest.json`); test âm (giả lập trong bộ nhớ việc `ext_v51fix` đăng ký `tolerant_v5_1` và `tolerant_v4`): FAIL đúng ở B1, B2, B3 (`preflight_negative_test.json`).
- Hash các file vòng 2 không đổi: `ext_v51.py` 48bb21ad…, `ext_narrow.py` 9fc15ae7…, `methods.py` 85bc718f…, `estimator.py` 70314e98…, `frozen_v4_v51.json` 43ac16aa….

---

## 3. Frozen spec for P4-H2, v2 (P1 sửa) — ghi lúc 2026-11-02T06:11Z, **CHƯA CHẠY**

Thay thế spec vòng 2 (`experiments/configs/ext_v51_p4h2.json` + `experiments/ext/v51/rule_p4h2.py`): spec cũ **không được chạy**; preflight mới sẽ FAIL nếu `results/ext_v51_p4h2` tồn tại. Chỉ chạy một lần, sau khi người dùng duyệt (R3-0); không chạy thử, không chạy một phần.

**Manifest spec:** `experiments/ext/v51fix/p4h2_spec_files.json` (19 file kèm sha256 lúc freeze, vai trò từng file, lệnh, thời gian, rule, danh sách ext module khác để tham khảo). Lead hash lại toàn bộ ngay trước run.

**Method.** `tolerant_v5_1` (`src/paper4/ext_v51.py`, không đổi so với code đã đánh giá) so với `tolerant_v4` (frozen). Mô tả paper: "v5 với targeted lag opening đã de-duplicate, chọn lại trong mỗi bootstrap draw" (mục 0).

**Lệnh (đúng thứ tự):**
1. `/Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/preflight_p4h2.py` → phải in `PREFLIGHT PASS` và exit 0; ghi `results/ext_v51fix_p4h2_preflight/preflight.json`. Nếu FAIL thì không chạy.
2. `/Users/kietnt/miniconda3/bin/python experiments/run_experiment.py --config experiments/configs/ext_v51fix_p4h2.json --workers 3`
3. `/Users/kietnt/miniconda3/bin/python experiments/ext/v51fix/rule_p4h2_v2.py` → `results/ext_v51fix_p4h2/ruling_v2.md`, `ruling_v2.json`.

**Thời gian dự kiến với `--workers 3`:** khoảng 11 phút cho run (cùng config trên D-07 mất 647 s, 2520 dòng; P4-H2 confirmatory có 20 topology như D-07), tới khoảng 20 phút nếu CPU bị chia nhiều; preflight < 30 s; analyzer khoảng 1 phút. Số dòng mong đợi: 2520.

**Sửa (1)–(4) của verifier:**
1. **Phạm vi hash.** Analyzer mới tự chứa (chỉ numpy và thư viện chuẩn), không import `common.py`. Manifest ghim: `ext_v51.py`, `ext_narrow.py`, `methods.py`, `estimator.py`, `effects.py`, `skeleton.py`, `metrics.py`, `generator.py`, `topology.py`, `__init__.py`, `experiments/run_experiment.py`, config, `frozen_v4_v51.json`, `tolerant_v4_frozen.json`, analyzer, preflight, `ext_v51fix.py` (được runner import; chỉ đăng ký `tolerant_v5_1_t294`), manifest D-07H. Manifest P4-H2 được liệt kê với sha256 mong đợi từ PROVENANCE.md (0b7e6579…c7d8) và **không** được v51fix mở; lead hash nó.
2. **Guard identity của method (E4).** Preflight dùng chính `ext_methods()` của runner để kiểm `tolerant_v5_1` → `paper4.ext_v51.tolerant_v5_1` (`__module__ == 'paper4.ext_v51'`, cùng object), chỉ `ext_v51` đăng ký tên này, không ext module nào đăng ký tên built-in (kể cả `tolerant_v4`), các helper ext_v51 dùng là object gốc (không bị monkeypatch), TAU = 6.6083, PRESCALE = 0.5, file frozen không ghi đè key nào khác (E5). Sau run, analyzer kiểm fingerprint (`info_v51_targeted`, `info_v51_ratio` trên mọi dòng v5_1 ok, không có trên dòng v4), width factor từng dòng bằng frozen, prescale 0.5, `calibration.json` bằng frozen, manifest config bằng file config.
3. **Run thất bại.** Cell có 0 run ok của một trong hai method → điều kiện của cell đó FAIL → NOT CONFIRMED (không crash; đã test). Trần: run failed của v5_1 ≤ 1% tổng (12/1260) và ≤ 5% mỗi cell rule (3/60). Cổng coverage dùng **coverage ITT**: run failed của v5_1 được tính là không cover pair non-null nào của nó (số pair lấy từ cùng topology × replicate). Trên D-07, v5_1 có 0 run failed trên 1260 (và 0 trên 3780 run a1), nên điều này không đổi verdict dry run.
4. **τ và nhánh all-lag.** Ghi trước: nhánh all-lag không thể được chọn ở T ≤ 150 với 14 nút (r ≤ 5.10 < 6.6083); preflight kiểm giải tích, analyzer kiểm từng run. τ mong manh (11% seed bootstrap của probe cho 2.94); run này chỉ xác nhận method đã freeze; hành vi ở T150 dưới τ ≈ 2.94 là sensitivity D-07 ở mục 2.C (lợi thế T150 missing biến mất, C2 vẫn đạt), không được kiểm trên P4-H2.

**Quy tắc confirmatory (ngưỡng giữ nguyên spec vòng 2; chỉ thêm validity, trần failure và coverage ITT).** `tolerant_v5_1` được **XÁC NHẬN** trên P4-H2 nếu mọi điều sau đúng:
- **V (validity):** sáu kiểm tra V1–V6 của analyzer đều PASS.
- **F (failure):** trần tổng và trần từng cell như trên.
- **C1:** ở T = 40 missing-0.2 và missing-0.5: coverage ITT của v5_1 ≥ 0.90 và cận trên CI 95% (bootstrap theo topology, 1000, seed 0) của hiệu IS ghép cặp (v5_1 − v4) < 0.
- **C2:** ở T = 80 và 150, 12 cell hỏng: coverage ITT của v5_1 ≥ 0.90 và IS trung bình v5_1 ≤ 1.05 × IS trung bình v4.
- **C3:** none ở T = 40/80/150 và extra/reversed × 0.2/0.5 ở T = 40 (7 cell): IS v5_1 ≤ 1.05 × IS v4.

**Báo kèm (không phải verdict chính thức):** C1 bản Holm (2 cell); overlay Bonferroni cho C1 theo số primary spec có thành phần p-value (2 spec: CI 97.5%; 3 spec: CI 98.33%), theo mục 3.3 của synthesis — verdict chính thức vẫn là spec gốc; số cell C2/C3 mà v5_1 tệ hơn có ý nghĩa sau Holm; số cell có coverage dưới 0.90 có ý nghĩa sau Holm (14 cell có cổng) và danh sách cell coverage < 0.93; tỷ lệ run missing đi nhánh targeted.

**Rủi ro ghi trước.** Coverage của v5_1 trên D-07 sát ngưỡng ở 4 cell (T40 missing-0.2 0.922, T80 extra-0.2 0.927, T80 extra-0.5 0.925, T80 reversed-0.5 0.918). Với 20 topology, CI coverage một cell rộng khoảng ±0.03, nên C2 có thể hụt chỉ vì nhiễu. Coverage ITT làm rủi ro này tăng nếu có run failed. Nếu NOT CONFIRMED, v4 được giữ và kết quả T40 của v5_1 chỉ là exploratory (synthesis 3.1).

**Bug E1 (không sửa trước P4-H2, theo quyết định của người dùng).** Built-in method được seed theo vị trí cell. Config này có đúng danh sách cell của grid a2 (như `ext_v51_p4h2` cũ), nên dòng v4 của nó là bảng v4 P4-H2 của paper (thay cho `ext_v51_p4h2` trong synthesis 3.3). Các config P4-H2 khác có danh sách cell khác sẽ có realisation v4 khác; mỗi test chỉ ghép cặp trong config của nó. Hệ quả: không ghép được dòng v5_1 của run này với baseline của config P4-H2 khác qua dòng v4, trừ khi hai config có cùng danh sách T × cell và cùng seed_base (khi đó dòng v4 trùng, như mục 2.C đã kiểm trên D-07: giữ danh sách cell nhưng bỏ T vẫn cho dòng v4 trùng, vì seed dùng giá trị T chứ không dùng vị trí T).

**Multiplicity giữa các spec (điểm (5) của verifier)** là việc của lead; analyzer chỉ in overlay.

---

## 4. Tổng kết vòng 3 của hướng v51fix

- **"tau / hybrid":** bỏ khỏi mô tả, giữ code. Trên grid T ≤ 150, n = 14, nhánh all-lag không thể kích hoạt (chứng minh giải tích; 360/360 run missing trên D-07 đi nhánh targeted). Method P4-H2 vẫn đúng là code đã đánh giá.
- **v5_1 bao trùm v4c (tiêu chí ghi trước): ĐẠT.** v5_1 thắng v4c ở 6/6 cell missing (Holm 6), v4c thắng 0/21 sau Holm.
- **v5_1 so với pselect_union_v2(_cal):** thắng 21/21 (Holm 21), gồm 4/4 cell chính T80/150 missing (T150: −0.39, −0.30), với điều kiện comparator thiếu budget. **Mới:** ở T40, `bvar_minnesota_v2_cal` hòa v5_1 ở cell missing và tốt hơn v5_1 ở T40 extra-0.2/0.5 (Holm).
- **τ ≈ 2.94 ở T150:** lợi thế T150 missing của v5_1 (−0.30 / −0.23 so với v4) biến mất (t294 − v5_1 = +0.33 / +0.28, Holm); C2 vẫn đạt 6/6.
- **Spec P4-H2 v2:** file mới, preflight + analyzer tự chứa, đã kiểm thử; manifest `experiments/ext/v51fix/p4h2_spec_files.json`.

### Ghi chú sau khi viết (06:14Z)

- Phần công bố "đã biết trước" ở 1.B ghi v5_1 − v4 ở T80 missing "khoảng −0.4 / −0.6" và T150 "−0.2 / −0.23" theo trí nhớ; số đúng (vòng 2) là −0.44 / −0.27 và −0.30 / −0.23. Không ảnh hưởng quy tắc nào.
- R3-6 đã append một lần vào `docs/ext/v51.md` và `docs/ext/narrow.md` (heading "Sửa sau kiểm chứng vòng 2"). Ngay sau khi append, tôi sửa tại chỗ một câu trong chính khối vừa append của v51.md (mục 8: câu về C4 ban đầu viết "chỉ đúng với `pselect_cal`", sai vì v5_1 cũng thắng `fullvar_cal`, `pselect_union_v2(_cal)` và các baseline `*_c2` ở T40 missing); không có lần append thứ hai và không chạm nội dung cũ.
