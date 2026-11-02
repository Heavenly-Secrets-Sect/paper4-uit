# Baseline fidelity cao hơn và so sánh chính (ID `baselines2`, vòng 2, mục R2-1)

**Phạm vi.** Tiếp nối hướng `redteam` của vòng 1. Làm đúng mục R2-1 trong docs/ext/synthesis_round1.md: dựng `src/paper4/ext_baselines2.py` với `pselect_union_v2` và `bvar_minnesota_v2`, rồi chạy `tolerant_v4` (frozen calibration) so với hai baseline này, cả bản uncalibrated lẫn bản width-calibrated (`calibrate_methods`), trên grid a2. Mọi kết quả là **exploratory, D-07 development**. Không đụng P4-H2, P4-H1 hay split confirmatory nào.

Không sửa file có sẵn nào. File mới: `src/paper4/ext_baselines2.py`, `experiments/configs/ext_baselines2_{probe,probe_wrap,eval}.json`, `experiments/ext/baselines2/{sanity,timing,run_eval,analyze}.py`, `results/ext_baselines2_*`, file này.

## 1. Thiết kế hai baseline (cố định trước khi chạy D-07)

Cả hai method chỉ nhận data và public skeleton (pairs + orientation). Chúng **không đọc** stated damage (trừ việc runner chọn width factor theo stated kind cho bản `_cal`, giống hệt cách làm với `tolerant_v4` và với E3 vòng 1).

### 1.1 `pselect_union_v2` (Chang–Guo–Malinsky, arXiv 2405.06763, chuyển thể SVAR)

Ba chỗ sửa so với `pselect_union` của methods.py (bug B8, xung đột X2):

1. **Selection bằng test trong structural equations của skeleton** (`diagnose.structural_pvalues`, đúng như B1 v2): kept pair dùng joint Wald của mọi term của u trong phương trình v và ngược lại; left-out pair dùng Wald của hai lag block cộng correlation của hai structural residual; Šidák combination. p-value đổi sang z hai phía; pair được chọn khi z > 1.96. Mỗi perturbed selection cộng N(0, 1) vào mọi z (như vòng 1, 100 lần). Không còn reduced-form Granger.
2. **Pair được chọn mà skeleton không có hướng thì có contemporaneous term theo cả hai hướng**: giống `ida_union` với reversible line của CPDAG, mỗi graph được fit trong nhiều orientation member và interval là union qua các member. Member đi theo cặp antithetic: một orientation ngẫu nhiên của các pair không hướng và bản lật toàn bộ của nó, nên mỗi pair như vậy được fit theo cả hai hướng (nếu một hướng tạo cycle thì giữ hướng kia). Mặc định 1 cặp, tức 2 member mỗi graph.
3. **Bootstrap budget**: tổng ít nhất `n_boot` = 199 draw, chia đều cho các member đã fit, mỗi member tối thiểu 40 draw (ví dụ 4 graph × 2 member × 40 = 320 draw). Interval của mỗi member là normal bootstrap interval C_m ± 1.96·sd*(C_m), vì với 40–50 draw thì percentile 2.5/97.5 gần như chỉ là min/max, và interval theo từng graph của bài gốc là dạng Wald. Interval báo cáo là union qua mọi member của mọi graph giữ lại. Point estimate là cumulative(mean IRF) qua các member của graph không perturbed.

Số graph giữ lại: graph không perturbed cộng các perturbed graph thường gặp nhất, tối đa `cap` = 4 (vòng 1: 16 graph × 12 draw).

### 1.2 `bvar_minnesota_v2` (Minnesota prior conjugate Normal-inverse-gamma)

- Theo từng structural equation (các phương trình độc lập khi biết contemporaneous term đệ quy của skeleton): σ_j² ~ IG(a0 = 1.5, b0 = s_j²/2), đúng marginal của IW(diag(s²), n + 2) trong Giannone–Lenza–Primiceri (2015); β_j | σ_j² ~ N(0, σ_j² V0_j).
- V0 = (λ/l)²/s_i² cho x_i ở lag l, nhân θ khi pair nằm ngoài skeleton và i ≠ j; contemporaneous parent của skeleton có prior phẳng (1e4/s_i²). s_i là residual sd của AR(lag_max) đơn biến.
- λ, θ chọn trên grid bằng closed-form marginal likelihood (multivariate t) của mọi phương trình cộng Gamma hyperprior của GLP trên λ (mode 0.2, sd 0.4).
- **Posterior draws lấy cả σ_j²** từ inverse-gamma posterior rồi mới lấy β_j | σ_j² (vòng 1 cố định σ_j² = s_j², bug B9). Interval = percentile 2.5–97.5 của C(H) qua 199 posterior draw.

### 1.3 Bản `_cal` và random stream

`pselect_union_v2_cal`, `bvar_minnesota_v2_cal` cho đúng raw interval của bản uncalibrated, rồi runner nới bằng factor tune theo (T, stated kind) trên D-07H development, sàn 1.0 (`C_GRID`), giống E3 vòng 1. Để hai bản dùng **chung một bộ draw**, random stream của module lấy từ hash của (họ method, data, public skeleton, lag_max, H, n_boot) chứ không từ stream của runner, kèm cache theo process. Cache miss thì tính lại ra đúng kết quả đó, nên kết quả không phụ thuộc thứ tự gọi (khác với `targeted_lp_cal` vòng 1, vốn phụ thuộc thứ tự).

### 1.4 Kiểm tra trên ví dụ nhỏ biết truth (`experiments/ext/baselines2/sanity.py` → `results/ext_baselines2_sanity/sanity.txt`)

- Closed-form NIG log marginal likelihood trùng với `scipy.stats.multivariate_t` (−47.054227 cả hai).
- `bvar_minnesota_v2` ở T = 3000 trên SVAR 4 nút: C(0→3) 0.817 [0.733, 0.924], truth 0.822.
- `pselect_union_v2` ở T = 150, xoá cạnh cùng kỳ 0→1: coverage 0.95 qua 20 seed; trung bình 3.10 pair được chọn (truth 3); 1.10 pair không hướng (tức cạnh bị xoá được chọn lại và fit theo hai hướng).
- Bản uncalibrated và `_cal` cho raw interval giống hệt nhau (kể cả khi xoá cache giữa hai lần gọi).

## 2. Các lần chạy trước khi ghi rule (công bố đầy đủ)

Không có lần chạy nào trên D-07 trước khi ghi mục 3. Các lần chạy trước đó đều trên D-07H development:

- `results/ext_baselines2_probe/` (config `ext_baselines2_probe.json`): 4 topology D-07H development × 1 replicate, T ∈ {40, 80, 150}, cell none/missing/reversed, method `tolerant_v3`, `pselect_union`, `pselect_union_v2`, `bvar_minnesota`, `bvar_minnesota_v2`. Mục đích: timing và kiểm tra sơ bộ. Thiết kế (cap 4, 2 member, 40 draw, normal interval) đã cố định **trước** probe này và không đổi sau đó. Điều thấy được (chỉ để công bố, D-07H, 4 topology):
  - T = 40: `pselect_union_v2` mất rất nhiều pair (lost 0.76–0.85), vì all-lag structural test ở T = 40 gần như không có power, nên graph được chọn gần như rỗng. Vòng 1 lost 0.52–0.54.
  - T = 150 missing: `pselect_union_v2` uncalibrated đã có coverage 0.978/0.985 với IS 1.87/2.15, sát `tolerant_v3` uncalibrated (2.23/1.99). Tức là baseline mới **mạnh hơn hẳn** bản vòng 1 (2.56/4.03) và claim chính có thể thất bại ở T = 150.
  - `bvar_minnesota_v2` cải thiện IS so với vòng 1 ở mọi cell probe, nhưng vẫn under-cover ở cell missing (0.59–0.82).
- `results/ext_baselines2_probe_wrap/`: kiểm tra plumbing của `run_eval.py` (2 topology D-07H, T = 80, missing-0.2, calibration trên 3 topology D-07H).
- `experiments/ext/baselines2/timing.py`: thời gian mỗi method trên 1 unit D-07H, không dùng cho kết luận. Lần chạy đầu chỉ in ra shell; lần thứ hai ghi vào `results/ext_baselines2_probe/timing.json` (0.41–0.83 s cho `pselect_union_v2`, 0.08–0.12 s cho `bvar_minnesota_v2`, 0.66–1.06 s cho `tolerant_v3` mỗi lần gọi, tuỳ T và load máy).

**Thời điểm.** Mục 3 dưới đây được ghi xong lúc khoảng 19:51Z ngày 2026-11-01 (02:51 ngày 02/11 giờ máy, +07); run evaluation khởi chạy ngay sau đó (thời điểm thật nằm trong `results/ext_baselines2_eval/run.log`).

## 3. Rule ghi trước (viết trước khi chạy `ext_baselines2_eval`)

**Run.** `python experiments/ext/baselines2/run_eval.py --config experiments/configs/ext_baselines2_eval.json --workers 3`. Wrapper gọi nguyên runner, chỉ thêm pair-level coverage vào mỗi row ở bước scoring. Bank D-07 development, seed_base 20261102 (cùng data và damaged skeleton với a2_baselines/a2b_pselect), 20 topology × 3 replicate, T ∈ {40, 80, 150}, kind {extra, missing, reversed} × rate {0.2, 0.5} + none, n_boot 199, H 4. Method: `tolerant_v4` (frozen calibration `experiments/calibration/tolerant_v4_frozen.json`), `pselect_union_v2`, `pselect_union_v2_cal`, `bvar_minnesota_v2`, `bvar_minnesota_v2_cal`. Calibration: block calibration của a3_ges.json (D-07H development, 1 replicate, kind extra/missing/reversed, rate 0.2/0.5). Grid đầy đủ, không giảm (ước tính khoảng 12–15 phút với 3 worker).

**Thống kê** (code `experiments/ext/baselines2/analyze.py`, viết trước khi chạy): coverage pooled trên non-null pair của run ok; hiệu IS(v4) − IS(X) theo từng run (topology, replicate), ước lượng = trung bình; CI 95% percentile từ 4000 cluster bootstrap theo 20 topology (seed 20261102); p một phía cho "v4 tốt hơn" = (1 + #{bootstrap mean ≥ 0})/(B + 1).

**R-B2 (primary, đúng như R2-1).** Claim chính "v4 thắng baseline mạnh nhất ở cạnh thiếu khi T ≥ 80" được **GIỮ** nếu ở cả 4 cell missing-0.2, missing-0.5 × T ∈ {80, 150}: coverage của v4 ≥ 0.90 **và** cận trên CI 95% của IS(v4) − IS(X) < 0, với **mỗi** X ∈ {`pselect_union_v2`, `pselect_union_v2_cal`}. Tức là 8/8 so sánh phải đạt. Nếu không: **THẤT BẠI**, claim chính phải thu hẹp (xem mục 3.1).

- **Multiplicity:** báo thêm số cell đạt khi thay điều kiện CI bằng Holm step-down trên 8 so sánh của rule (một phía, mức 0.025, tương ứng CI hai phía 95%). Verdict theo rule là verdict theo CI như R2-1 ghi; kết quả Holm được báo cạnh đó, và nếu CI đạt mà Holm không đạt thì claim phải viết là "đạt không hiệu chỉnh, không qua Holm".

**R-B2s (secondary).** Cùng điều kiện với X ∈ {`bvar_minnesota_v2`, `bvar_minnesota_v2_cal`}, Holm trên 8 so sánh của nó.

**Mô tả, không chấm:** mọi cell còn lại (T = 40, none, extra, reversed) so với 4 baseline, đếm W/T/L kèm Holm hai phía trên toàn bộ 84 so sánh; v2 so với bản vòng 1 trên cùng data (đọc từ a2b_pselect/a2_baselines); coverage của pair bị xoá theo lag thật của cạnh (lag 0 so với lag 1–2) cho cả 5 method; kiểm tra regression: row `tolerant_v4` phải trùng từng số với `results/a2b_pselect` (frozen factor = factor của a2).

### 3.1 Nếu R-B2 thất bại: cách thu hẹp đã định trước

Claim chính sẽ được viết lại đúng theo tập cell đạt, không hơn:
- nếu chỉ T = 150 hỏng: "v4 thắng baseline mạnh nhất ở cạnh thiếu khi T = 80; ở T = 150 hai bên hòa (hoặc baseline tốt hơn), và lợi thế của module ở T lớn chỉ còn so với các baseline yếu hơn";
- nếu chỉ bản `_cal` hoặc chỉ bản uncalibrated hỏng: nêu rõ claim chỉ đứng dưới điều kiện calibration tương ứng;
- nếu hỏng ở cả T = 80: claim "thắng baseline đã công bố ở cạnh thiếu" bị rút, chỉ còn claim so với plugin, `ida_union`, `bvar` và các baseline vòng 1.
Không thêm điều kiện mới, không đổi ngưỡng sau khi thấy kết quả. Mọi version baseline/method mới sau khi thấy kết quả là version mới với rule mới.

## 4. Kết quả

(Thêm sau khi chạy, nguyên văn từ `results/ext_baselines2_eval/rule_check.txt` và `analysis.md`.)

### 4.0 Gián đoạn và chạy lại (công bố)

Lần thử đầu của vòng 2 khởi chạy `ext_baselines2_eval` ngay sau khi ghi mục 3 (khoảng 02:51 giờ máy ngày 02/11). Usage limit cắt ngang lần đó trước khi runner ghi `runs.jsonl`/`summary.md` (thư mục `results/ext_baselines2_eval/` rỗng, không có `run.log`), nên lần đó không cho kết quả nào. Run được chạy lại **một lần**, với config, module, `run_eval.py` và `analyze.py` y nguyên (mtime của cả bốn file đều trước lúc ghi rule), 3 worker. Start 2026-11-02T02:22:15Z, end 02:36:01Z, 825 s, 6300 row, toàn bộ status ok (`results/ext_baselines2_eval/run.log`). Grid đầy đủ, không giảm. Trong lúc chạy, load average của máy lên khoảng 32 vì các agent khác chạy song song. Kiểm tra regression: 1260 row `tolerant_v4` trùng từng số với `results/a2b_pselect`, 0 mismatch (analysis.md, mục 5).

### 4.1 Rule R-B2 (primary): **THẤT BẠI**

Nguyên văn từ `results/ext_baselines2_eval/rule_check.txt`:

| X | T | cell | v4 cov | IS v4 | IS X | cov X | v4 - X [95% CI] | p (one-sided) | CI rule | Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| pselect_union_v2 | 80 | missing-0.2 | 0.959 | 3.28 | 4.41 | 0.877 | -1.14 [-1.65, -0.63] | 0.0002 | pass | pass |
| pselect_union_v2 | 80 | missing-0.5 | 0.957 | 3.37 | 4.56 | 0.878 | -1.19 [-1.64, -0.78] | 0.0002 | pass | pass |
| pselect_union_v2 | 150 | missing-0.2 | 0.968 | 2.06 | 2.15 | 0.965 | -0.10 [-0.30, +0.08] | 0.1640 | FAIL | FAIL |
| pselect_union_v2 | 150 | missing-0.5 | 0.962 | 2.22 | 2.29 | 0.967 | -0.07 [-0.25, +0.08] | 0.2044 | FAIL | FAIL |
| pselect_union_v2_cal | 80 | missing-0.2 | 0.959 | 3.28 | 4.49 | 0.940 | -1.22 [-1.62, -0.82] | 0.0002 | pass | pass |
| pselect_union_v2_cal | 80 | missing-0.5 | 0.957 | 3.37 | 4.56 | 0.937 | -1.19 [-1.50, -0.88] | 0.0002 | pass | pass |
| pselect_union_v2_cal | 150 | missing-0.2 | 0.968 | 2.06 | 2.15 | 0.965 | -0.10 [-0.29, +0.08] | 0.1612 | FAIL | FAIL |
| pselect_union_v2_cal | 150 | missing-0.5 | 0.962 | 2.22 | 2.29 | 0.967 | -0.07 [-0.24, +0.08] | 0.2032 | FAIL | FAIL |

Counts (cells out of 4): pselect_union_v2: 2/4 (Holm over 8: 2/4); pselect_union_v2_cal: 2/4 (Holm over 8: 2/4)

**Verdict R-B2 (primary, X in pselect_union_v2 / _cal): FAILS** (CI rule); under Holm: FAILS.

Tổng: 4/8 so sánh đạt theo CI, cũng 4/8 theo Holm trên 8. Cả 4 so sánh hỏng đều ở T = 150, và hỏng theo kiểu **hòa** chứ không thua: điểm ước lượng vẫn nghiêng về v4 (−0.07 đến −0.10), nhưng CI chứa 0. Coverage của v4 đạt ≥ 0.90 ở cả 4 cell (0.957–0.968). Ở T = 150, factor D-07H của `pselect_union_v2_cal` là 1.0, nên bản `_cal` gần như trùng bản uncalibrated (p lệch nhau chút ít chỉ do bootstrap stream).

### 4.2 Rule R-B2s (secondary): ĐẠT

`bvar_minnesota_v2`: 4/4 (Holm trên 8: 4/4); `bvar_minnesota_v2_cal`: 4/4 (Holm trên 8: 4/4). v4 − X nằm trong khoảng −1.21 đến −5.49, mọi cận trên CI < −1.0 (bảng đầy đủ trong `rule_check.txt`).

### 4.3 Thu hẹp claim chính (áp đúng mục 3.1, nhánh "chỉ T = 150 hỏng")

Claim chính chỉ được viết như sau:

> Ở cạnh thiếu, `tolerant_v4` (frozen calibration) thắng baseline mạnh nhất khi **T = 80**: interval score thấp hơn `pselect_union_v2` và `pselect_union_v2_cal` ở cả missing-0.2 lẫn missing-0.5 (−1.14 đến −1.22, Holm 4/4 trong họ 8 so sánh), với coverage 0.957–0.959. Ở **T = 150**, v4 **hòa** `pselect_union_v2` (−0.10 [−0.30, +0.08]; −0.07 [−0.25, +0.08]). Lợi thế ở T lớn chỉ còn so với các baseline yếu hơn (`pselect_union` vòng 1, `pselect_cal`, `fullvar_cal`, `targeted_lp(_cal)`, các bản BVAR, `ida_union`, `plugin`).

Câu trong synthesis (mục "claim đứng vững", dòng "4/4 cell … *(Còn chờ R2-1)*") phải bỏ "4/4 cell ở T ≥ 80" so với baseline mạnh nhất. Ta không được thêm điều kiện mới hay đổi ngưỡng.

### 4.4 Mô tả (không chấm, không đổi verdict)

- **Cơ chế (X2 được xác nhận).** Khi cặp được chọn lại có hạng cùng kỳ theo cả hai hướng, pair bị xoá có lag thật 0 không còn là điểm yếu của pselect: ở T = 150, coverage của pair lag 0 là 0.962/0.964 (`pselect_union_v2`), so với 0.949/0.938 của v4 (analysis.md, mục 6). Ở T ≥ 80, v4 cover pair lag 0 bị xoá kém hơn pair lag 1–2 khoảng 0.03–0.05 (missing-0.5: −0.049 [−0.095, −0.007] ở T80, −0.032 [−0.060, −0.007] ở T150). `pselect_union_v2` không có chênh lệch này (−0.020 đến +0.007, CI chứa 0). `bvar_minnesota_v2` hầu như không bao giờ cover pair lag 0 bị xoá (0.06–0.13 khi uncalibrated, 0.57–0.78 khi calibrated), vì prior chỉ có hạng cùng kỳ cho các cạnh có trong skeleton.
- **Mọi cell, 84 so sánh** (analysis.md, mục 3). So với `pselect_union_v2`/`_cal`, v4 có W 19 / T 2 / L 0 mỗi bản, Holm cũng 19/2/0. Hai ô hòa chính là T150 missing. So với `bvar_minnesota_v2`: W 13 / T 7 / L 1 (Holm W 10 / T 11 / L 0). So với `bvar_minnesota_v2_cal`: W 8 / T 7 / L 6 (Holm W 7 / T 11 / L 3). Cả 6 ô thua đều ở T = 40.
- **"Fidelity cao hơn" không có nghĩa là mạnh hơn ở mọi nơi.** So với `pselect_union` vòng 1 trên cùng data (analysis.md, mục 4), `pselect_union_v2` tệ hơn ở mọi cell T = 40 (IS 11–14 so với 6–7: all-lag structural test thiếu power, graph gần rỗng, còn union qua 8 member thì nới width) và ở mọi cell không thiếu cạnh khi T = 80. Nó chỉ tốt hơn ở T150 missing (+0.16 [−0.04, +0.35]; +0.82 [+0.56, +1.10]). Vì vậy các ô W của v4 so với `pselect_union_v2` ở T = 40 và ngoài cell missing **không được** trích như "thắng baseline mạnh hơn". `bvar_minnesota_v2` có IS thấp hơn bản vòng 1 ở cả 21/21 cell theo điểm ước lượng; ở 18/21 cell CI loại trừ 0 (ba cell có CI chứa 0 là T40 extra-0.5 và hai cell T150 reversed).
- **Baseline mạnh nhất theo từng cell, mọi version đã lưu (POST HOC, `experiments/ext/baselines2/envelope.py` → `results/ext_baselines2_eval/envelope.md`).** Viết sau khi thấy kết quả, không phải rule. Mọi nguồn đều ghép cặp được qua row v4 (0 mismatch). Cụ thể:
  - T80 missing-0.2: baseline mạnh nhất là `targeted_lp` (3.48); v4 − X = −0.20 [−0.39, −0.02] (p = 0.032) và với `targeted_lp_cal` là −0.21 [−0.36, −0.05] (p = 0.0085). Cả hai **không qua Holm** trên 94 so sánh của bảng đó. Với mọi baseline khác ở T80, v4 qua Holm.
  - T80 missing-0.5: mạnh nhất là `fullvar_cal` (3.82); v4 − X = −0.45 [−0.59, −0.31], qua Holm.
  - T150 cả hai cell: mạnh nhất là `pselect_union_v2` (hòa, như trên).
  - T40: v4 thua `targeted_lp_cal`, `tolerant_v5` và `bvar_minnesota_v2_cal` (+2.0 đến +3.0, qua Holm).

  Vì vậy câu ở T = 80 chỉ đứng vững hoàn toàn so với họ pselect/BVAR/IDA/fullvar. So với `targeted_lp` ở missing-0.2, đó là "đạt không hiệu chỉnh, không qua Holm".
- **`tolerant_v5` so với `pselect_union_v2`** (envelope.md): thắng ở T40/T80 missing; ở T150 cũng hòa (−0.18 [−0.41, +0.06]; +0.05 [−0.10, +0.20]).
- **Null pair.** v4 rộng hơn trên null pair: IS null 2.03/2.08 (T80) và 1.31/1.36 (T150), so với 1.26/1.31 và 0.91/1.00 của `pselect_union_v2`. Lợi thế của v4 nằm ở non-null pair (lost pair), không phải ở width tổng thể (số trong `numbers.json`, `summary`).
- Width factor của bản `_cal` (analysis.md, mục 8): `pselect_union_v2_cal` cần 4.4–8.7 ở T40 nhưng chỉ 1.0–1.7 ở T ≥ 80. `bvar_minnesota_v2_cal` cần 2.2–2.8 ở cell missing.

Mọi số ở mục 4 nằm trong `results/ext_baselines2_eval/{rule_check.txt, analysis.md, numbers.json, envelope.md, envelope.json}`.

## 5. Bug/nhận xét về file có sẵn (chỉ báo, không sửa)

- Không thấy bug mới trong runner. `frozen_calibration` ghi đè **mọi** key không bắt đầu bằng `_`, nên một file frozen có thể chứa cả factor của baseline. Spec P4-H2 dưới đây dùng đúng điều đó.
- Seed của module này lấy từ hash có chứa `skel.damage`. Method không dùng stated damage để ước lượng, nhưng draw của nó phụ thuộc stated damage. Điều này không ảnh hưởng tính công bằng; chỉ ghi lại.

## 6. Frozen spec for P4-H2 (CHƯA chạy)

Ứng viên: so sánh chính đã thu hẹp (mục 4.3). Method được đánh giá là `tolerant_v4` (frozen, không đổi). Các baseline là đối chứng.

- **Module:** `src/paper4/ext_baselines2.py` (giữ nguyên như lúc đánh giá trên D-07; method `pselect_union_v2`, `pselect_union_v2_cal`, `bvar_minnesota_v2_cal`), cộng `tolerant_v4` built-in.
- **Width factor đã đóng băng:** `experiments/ext/baselines2/frozen_calibration_p4h2.json`. Các key `mod|*` copy nguyên từ `experiments/calibration/tolerant_v4_frozen.json` (đã kiểm từng giá trị). Các key `pselect_union_v2_cal|*` và `bvar_minnesota_v2_cal|*` lấy từ `results/ext_baselines2_eval/calibration.json` (tune trên D-07H development). Runner vẫn calibrate lại trên D-07H vì có `calibrate_methods`, nhưng file frozen ghi đè.
- **Config:** `experiments/configs/ext_baselines2_p4h2.json`, với `"bank": "P4-H2"`, `"split": "confirmatory"`, T ∈ {80, 150}, kind missing × rate {0.2, 0.5}, 3 replicate, n_boot 199, H 4, seed_base 20261102, `"frozen_calibration": "experiments/ext/baselines2/frozen_calibration_p4h2.json"`.
- **Lệnh (chạy đúng một lần):** `python experiments/ext/baselines2/run_eval.py --config experiments/configs/ext_baselines2_p4h2.json --workers 3`, sau đó `python experiments/ext/baselines2/analyze_p4h2.py`. Code phân tích đã được dry-run chỉ trên row D-07 (`results/ext_baselines2_dryrun_p4h2/`, không phải kết quả xác nhận).
- **Rule xác nhận (C1, quyết định claim):** ở T = 80, cell missing-0.2 và missing-0.5, với X ∈ {`pselect_union_v2`, `pselect_union_v2_cal`} (4 so sánh): coverage của v4 (pooled trên non-null pair) ≥ 0.90 **và** so sánh bị bác bỏ bởi Holm step-down ở mức họ 0.025 một phía trên 4 so sánh. p một phía = (1 + #{bootstrap mean của IS(v4) − IS(X) ≥ 0})/(B + 1), B = 4000 cluster bootstrap theo topology, rng 20261102. ĐẠT khi và chỉ khi đạt cả 4/4. Số đếm chỉ theo CI được báo kèm.
- **C2 (secondary, không quyết định):** cùng phép test với X = `bvar_minnesota_v2_cal` ở T ∈ {80, 150} × 2 cell missing, Holm trên 4 so sánh của nó.
- **D (mô tả, không verdict):** T = 150 so với `pselect_union_v2(_cal)`. Claim chỉ là "không thấy khác biệt", và không có margin tương đương nào được khai báo.
- Nếu C1 thất bại trên P4-H2, claim "thắng baseline mạnh nhất ở cạnh thiếu" bị rút hoàn toàn, chỉ còn so sánh với BVAR/IDA/plugin.

## Sửa sau kiểm chứng vòng 2

Phần này được append ở vòng 3 (hướng `baselines3`, docs/ext/baselines3.md), theo mục R3-6 và 1.1, 2.1 của docs/ext/synthesis_round2.md. Không sửa nội dung phía trên; các câu dưới đây thay thế câu tương ứng.

1. **Comparator thiếu budget, lệch khỏi R2-1 mà doc không ghi.** R2-1 yêu cầu ≥ 199 draw mỗi graph. `pselect_union_v2` dùng cap = 4 graph (vòng 1: 16) và `min_draws` = 40 cho mỗi orientation member, tức khoảng 80 draw mỗi graph, kèm normal interval. Mục 1.1 và 3 lẽ ra phải ghi đây là lệch khỏi R2-1. Bản đúng budget (`pselect_union_v3`, cap 16, 199 draw mỗi member, 6368 draw mỗi lần gọi; docs/ext/baselines3.md) tốt hơn v2 ở T80 missing: −0.91 [−1.42, −0.45] và −0.98 [−1.41, −0.61]; bản two-sided calibrated tốt hơn v2 ở cả bốn cell (−1.05, −1.16, −0.24, −0.29). Vì vậy biên −1.14 / −1.19 / −1.22 của v4 ở T80 trong mục 4.1 chủ yếu là do comparator bị cắt budget, **không** được trích như lợi thế của module.
2. **Claim chính phải hẹp lại theo synthesis_round2 mục 2.1, và hẹp hơn nữa sau R3-1.** Câu ở mục 4.3 ("v4 thắng baseline mạnh nhất khi T = 80") bị rút. So với envelope đủ budget (R3-1, D-07 development, Holm trên 56): v4 hòa `pselect_union_v3_cal` ở T80 (−0.09 [−0.27, +0.10]; −0.03 [−0.20, +0.14]) và **thua** nó ở T150 missing-0.5 (+0.22 [+0.14, +0.30]); không cell nào v4 thắng trọn envelope. Câu "không baseline nào đã thử có interval score thấp hơn v4 ở cell nào" của synthesis_round2 mục 2.1 cũng sai với baseline đủ budget. Câu thay thế nằm ở docs/ext/baselines3.md mục 5. Spec P6 (`ext_baselines2_p4h2.json`, `analyze_p4h2.py` của hướng này) **không được chạy**; spec P7 trong docs/ext/baselines3.md mục 6 thay thế nó.
3. **Khoảng cách coverage lag 0 so với lag 1–2 của v4 (mục 4.4, gạch đầu dòng "Cơ chế").** Câu "v4 cover pair lag 0 bị xoá kém hơn pair lag 1–2 khoảng 0.03–0.05" phải sửa: điểm ước lượng là −0.045 [−0.139, +0.025] (T80 missing-0.2), −0.049 [−0.095, −0.007] (T80 missing-0.5), −0.007 [−0.055, +0.035] (T150 missing-0.2), −0.032 [−0.060, −0.007] (T150 missing-0.5). CI chỉ loại 0 ở **2/4 cell**, và ở T150 missing-0.2 khoảng cách gần bằng 0. Số: results/ext_verify2_baselines2/claim_checks.json.
4. **Coverage lag 0 của `bvar_minnesota_v2_cal`:** "0.57–0.78" phải là **0.557–0.777** (gồm T40; ở T ≥ 80 là 0.570–0.777). Số: results/ext_verify2_baselines2/claim_checks.json.
5. **Row cũ của baseline vòng 1 dùng trong envelope (mục 4.4, POST HOC).** Row của `pselect_cal`, `fullvar_cal` (ext_redteam_calbase) và `targeted_lp(_cal)` (ext_tlp_eval) được tạo trước khi runner đổi stream tag ext (B1), nên không tái lập được với runner hiện tại (240/240 row khác ở 4 cell missing T ≥ 80; point estimate của `pselect_cal`/`fullvar_cal` trùng 60/60, chỉ draw bootstrap khác; chênh IS trung bình ≤ 0.08). Với row mới (results/ext_baselines3_eval), v4 − `targeted_lp_cal` ở T80 missing-0.2 là −0.23 [−0.42, −0.05] và v4 − `targeted_lp` là −0.18 [−0.39, +0.01].
6. Seed hash của `ext_baselines2.py` chứa stated damage (đã ghi ở mục 5). `pselect_union_v3` bỏ điều này: stream của nó không phụ thuộc stated damage, và output không đổi khi xoá stated damage (12/12 lần gọi, results/ext_baselines3_budget/timing.json).
