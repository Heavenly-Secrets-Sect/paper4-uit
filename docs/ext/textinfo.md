# Hướng `textinfo`: module chịu lỗi dùng side information từ văn bản của Paper 1 (không gọi LLM mới)

**Trạng thái.** Exploratory. Chạy trên D-07 development (seed_base 20261102). Calibration trên D-07H development. Không dùng confirmatory split nào, không dùng P4-H1. Quy tắc quyết định được ghi ở mục 5 **trước khi chạy evaluation**; kết quả được nối vào mục 6 nguyên văn, kể cả khi không đạt.

**File của hướng này** (không sửa file nào có sẵn):

- Module: [`src/paper4/ext_textinfo.py`](../../src/paper4/ext_textinfo.py)
- Driver và probe: `experiments/ext/textinfo/` (`run_textinfo.py`, `probe_textinfo.py`, `check_textinfo.py`, `real_side_info.py`)
- Config: `experiments/configs/ext_textinfo_*.json`
- Kết quả: `results/ext_textinfo_*`

## 1. Ý tưởng

`tolerant_v4` chỉ đọc **số lượng** cạnh hỏng (bao nhiêu cạnh thiếu, thừa, đảo), không biết cạnh nào. Nó nới skeleton "mù" trong ngân sách đó:

- khai báo thiếu cạnh → mở mọi lag của mọi nút, repair cạnh cùng kỳ theo tương quan phần dư;
- khai báo đảo cạnh → rút đảo chiều ngẫu nhiên trong các cặp cùng kỳ có hệ số significant.

Paper 1 đã trích sẵn bằng chứng văn bản cho prior graph: confidence, số nguồn, cờ `conflicted`, kết quả verifier, các quan hệ bị reject, và các chunk nhắc tới các biến. Hướng này biến bằng chứng đó thành **side information theo từng cặp**, thay cho một con số duy nhất:

- **doubt** cho mỗi cạnh trong skeleton: confidence thấp, ít nguồn, conflicted, bị verifier reject, có quan hệ ngược chiều → nhiều khả năng là cạnh thừa hoặc đảo;
- **suspicion** cho mỗi cặp ngoài skeleton: hai biến được nhắc cùng nhau trong chunk, hoặc có quan hệ đã trích nhưng bị reject → nhiều khả năng là cạnh thiếu;
- **sign hint** (và lag hint, xem mục 7).

Module vẫn tiêu đúng ngân sách đã khai báo, nhưng tiêu vào các cặp đáng ngờ nhất trước. **Không có lời gọi LLM hay API nào**; side information được tính trước bằng luật trên các trường đã lưu và đếm co-mention theo lexicon.

## 2. Ranh giới plan: câu hỏi mở cho thầy

Plan mục 8 ghi: *"Bài 4 nhận mức hỏng qua giao diện (mục 7), không dùng điểm chọn cạnh hay metric skeleton của bài 3; nếu một đóng góp cần điểm theo cạnh của bài 3 thì chuyển sang bài 5."* Bảng giao diện ở mục 7 gán trường `edge_score` (điểm theo cạnh) cho **Bài 3**.

Side information ở đây đến từ văn bản của **Paper 1**, không phải điểm chọn cạnh của Paper 3. Nhưng về hình thức, nó chính là một điểm theo cạnh đi kèm skeleton, tức đúng vai trò của `edge_score`. Vì vậy:

- **Câu hỏi mở (cần thầy quyết định):** điểm theo cạnh lấy từ văn bản Paper 1 có được coi là một phần của `damage_estimate` (thuộc Bài 4) không, hay vẫn thuộc loại `edge_score` và do đó hướng này phải chuyển sang Bài 5?
- Trong lúc chờ, hướng này được làm như một **thí nghiệm khả thi**: đo xem side information theo cặp, ở chất lượng nào, thì đáng dùng. Kết quả không làm thay đổi module chính thức `tolerant_v4`.
- Trong code, side information được gắn vào `skel.damage["text"]` (một khóa phụ của `damage_estimate`), không dùng trường `edge_score` (vẫn để `None` như cũ).

## 3. Module

`textinfo(data, skel, lag_max, H, n_boot, rng)`, đăng ký trong `METHODS` của `ext_textinfo.py`. Ngân sách là số cạnh khai báo, giống hệt v4. Điểm văn bản được đổi thành normal score theo hạng (van der Waerden), nên chỉ thứ hạng có ý nghĩa; trọng số của cặp là w = exp(γ·z), chuẩn hóa về trung bình 1. Không có text thì mọi trọng số bằng 1.

1. **Khai báo thiếu cạnh: mở lag có chọn lọc (targeted opening).** Thay vì mở mọi lag, chỉ mở lag block của các cặp ngoài skeleton theo thứ tự p / w:
   - p là p-value adjacency của cặp trong structural fit all-lag của skeleton (`diagnose.structural_pvalues`: Wald test của lag block hai chiều và tương quan phần dư cấu trúc, gộp Šidák);
   - w là trọng số suspicion.
   Đây là thứ tự của weighted Benjamini–Hochberg (Genovese, Roeder và Wasserman 2006): trọng số có trung bình 1 giữ được bảo đảm FDR dù trọng số tốt hay xấu, và trọng số tốt thì tăng power. Số block mở K = max(⌈5·k_missing⌉, số reject của weighted BH ở q = 0.1), không quá số cặp ngoài skeleton. Khi fit all-lag không làm được thì mở hết (như v4).
2. **Repair cạnh cùng kỳ theo text:** weighted BH (cùng trọng số) trên tương quan phần dư cấu trúc all-lag, tối đa k_missing cặp, chiều rút ngẫu nhiên mỗi draw (như v4).
3. **Khai báo đảo cạnh: rút đảo có trọng số.** Pool giống v3 (hệ số cùng kỳ significant). Mỗi draw đảo k_reversed cặp, chọn không hoàn lại với xác suất tỉ lệ trọng số doubt (Gumbel top-k), bỏ qua lần đảo tạo chu trình. Trọng số đều thì đúng là draw của v3.
4. **Khai báo thừa cạnh:** như v4 (giữ term của skeleton). Bỏ một cạnh thật thì gây bias, giữ một cạnh null chỉ tốn variance.
5. **Sign pruning (tùy chọn, `textinfo_sign`):** bỏ các bootstrap draw mà tổng hệ số fit của một cặp ngược dấu với sign hint *tự tin* (sign hint trên cặp có doubt ở nửa dưới). Nếu việc này bỏ quá nửa số draw thì không prune.

Các biến thể:

| Tên | Mô tả |
|---|---|
| `textinfo` | **Module chính của hướng này**: mục 1–3 |
| `textinfo_all` | Mở mọi lag như v4; text chỉ tác động qua repair và rút đảo (biến thể "an toàn", không thể mất lag term nào) |
| `textinfo_null` | `textinfo` với mọi trọng số bằng 1 (bỏ qua text): tách phần lợi do targeted opening khỏi phần lợi do text |
| `textinfo_sign` | `textinfo` + sign pruning |

Trên cell không khai báo thiếu hay đảo (none, extra), mọi biến thể dùng cùng random stream với `tolerant_v3` của runner (tag 6), nên **trùng draw-for-draw với v3**, có cùng hệ số width và cho đúng kết quả của `tolerant_v4`.

**Width calibration.** Như v4: mỗi biến thể có hệ số riêng theo (T, loại hỏng khai báo), tune trên D-07H development bằng đúng lưới (1.0–10, bước 0.1) và đích của runner. Hệ số được **gộp qua mức hỏng và qua cả ba mức chất lượng text**, nên nó không mang thông tin về chất lượng text. `textinfo_sign` dùng hệ số của `textinfo` (prune là bước sau trên chính các draw đó).

## 4. Đánh giá trong mô phỏng: side information tổng hợp có chất lượng kiểm soát

Topology mô phỏng không có văn bản. Side information được sinh **bên ngoài method**, từ damage log riêng (thứ chỉ phần đánh giá được đọc), rồi gắn vào skeleton hỏng. Method không bao giờ thấy log hay truth.

- Mỗi cặp nút có một nhiễu N(0, 1), rút một lần cho mỗi (unit, loại hỏng), dùng chung cho mọi mức chất lượng và mọi rate (common random numbers, nên so sánh giữa các mức chất lượng là paired).
- Cặp bị hỏng thật được cộng thêm δ(a) = √2·Φ⁻¹(a): cặp bị xóa vào `suspicion`, cặp bị thêm hoặc bị đảo vào `doubt`. Theo mô hình binormal cùng phương sai, AUROC của điểm so với hỏng thật đúng bằng a (kỳ vọng). AUROC thực tế được ghi trong summary.
- a ∈ {0.5, 0.7, 0.9}. a = 0.5 là text vô dụng.
- Sign hint: dấu thật của cạnh thật, lật với xác suất 0.1; cạnh thừa (null) nhận dấu ngẫu nhiên.

Driver `experiments/ext/textinfo/run_textinfo.py` import hàm từ `run_experiment.py` (không sửa): cùng unit seed, cùng dynamic SEM, cùng skeleton hỏng (rate lồng nhau), cùng data stream, cùng `evaluate`. `tolerant_v4` được dựng lại đúng như runner.

**Grid.** D-07 development, 20 topology × 3 replicate; T ∈ {80, 150} (hai lần chạy, mỗi T một lần); cell: none, {extra, missing, reversed} × {0.2, 0.5}; n_boot = 199, H = 4, lag_max = 2; method: `plugin`, `tolerant_v4`, `textinfo@a`, `textinfo_all@a`, `textinfo_null`. Chạy phụ `ext_textinfo_sign`: 2 replicate, a ∈ {0.5, 0.9}, `textinfo` và `textinfo_sign`.

### Probe thiết kế trên D-07H development (đã làm trước khi ghi quy tắc)

`experiments/ext/textinfo/probe_textinfo.py`, 10 topology × 1, T ∈ {80, 150}, interval chưa calibrate, kết quả ở `results/ext_textinfo_probe/summary.md`. Probe chỉ dùng bank calibration. Nó dùng để chọn hai tham số, rồi đóng băng chúng:

- **γ = 0.5 thay vì 1.** Với γ = 1, ở a = 0.5 interval score trên cell đảo tệ hơn v3 tới +4.5% (T = 150, đảo 50%). Với γ = 0.5 thì độ lệch ở a = 0.5 nằm trong khoảng −4.6% đến +1.3%, mà ở a = 0.9 vẫn giảm IS 5–13%.
- **Hệ số mở K = 5·k thay vì 3·k.** Targeted opening làm giảm IS thô (T = 80, thiếu 20%: 2.84–2.96 so với 3.21 của v3) nhưng coverage thô chỉ 0.87–0.90 (v3: 0.92). 5·k giữ coverage tốt hơn 3·k ở T = 150.
- Cảnh báo đã thấy trước: phần lợi do text trong cell thiếu cạnh nhỏ hơn nhiều so với phần lợi do targeted opening, và sau calibration (hệ số width lớn hơn cho biến thể under-cover) phần lợi thô có thể mất.

## 5. Quy tắc quyết định (ghi trước khi chạy evaluation)

Tham chiếu: `tolerant_v4`. "Cell bị hỏng" = {extra, missing, reversed} × {0.2, 0.5} ở T = 80 và T = 150, tức **12 cell**. Chênh lệch interval score là paired (method trừ `tolerant_v4`), 95% CI bootstrap theo topology (hàm `paired_table` của runner).

**`textinfo` được giữ lại (RETAINED)** nếu cả hai điều kiện đều đúng:

1. **Lợi khi text tốt.** Ở a = 0.9, có **ít nhất 6 trong 12** cell bị hỏng thỏa đồng thời: (i) upper bound của CI chênh lệch IS < 0; (ii) coverage của `textinfo@a0.9` ≥ 0.90.
2. **Không hại khi text vô dụng.** Ở a = 0.5, trong **mọi** cell ở T = 80 và 150 (none và 6 cell bị hỏng), mean IS của `textinfo@a0.5` ≤ 1.05 × mean IS của `tolerant_v4`.

Ngược lại là **REJECTED**.

Ghi chú viết trước:

- Trên cell extra, `textinfo` trùng hệt `tolerant_v4` theo thiết kế, nên chênh lệch bằng đúng 0 và cell extra **không bao giờ** tính là thắng. Điều kiện 1 vì thế thực chất đòi ≥ 6 trong 8 cell missing/reversed. Quy tắc giữ nguyên dạng đề xuất (12 cell), không nới.
- `textinfo_all` được chấm bằng **cùng quy tắc**, báo cáo như ứng viên thứ hai, riêng biệt. Không chọn biến thể sau khi xem kết quả: nếu chỉ `textinfo_all` đạt thì kết luận ghi đúng như vậy.
- Báo cáo mô tả, không ảnh hưởng verdict:
  - S1, phần lợi riêng của text: `textinfo@a0.9` so với `textinfo_null`, đếm cell missing/reversed có upper CI < 0;
  - S2, tính đơn điệu: chênh lệch IS so với v4 có giảm dần theo a = 0.5 → 0.7 → 0.9 trong từng cell missing/reversed không;
  - sign pruning: `textinfo_sign` − `textinfo` ở a = 0.9 và 0.5.
- Dữ liệu thật (mục 7) chỉ được mô tả. Không có ground truth, nên không có claim nào về hiệu quả.
- Áp quy tắc bằng `experiments/ext/textinfo/check_textinfo.py`.

## 6. Kết quả

Các lần chạy: `results/ext_textinfo_cal/calibration.json` (D-07H development, 40 topology × 1, 320 s), `results/ext_textinfo_t80/` (460 s), `results/ext_textinfo_t150/` (463 s), `results/ext_textinfo_sign/`. Quy tắc được áp bằng `check_textinfo.py`; bảng đầy đủ ở `results/ext_textinfo_verdict/verdict.md`. AUROC thực tế của side information tổng hợp khớp với mức đặt: 0.49–0.51, 0.69–0.72 và 0.88–0.91.

**Hệ số width (D-07H development).** Trên cell none/extra, mọi biến thể có đúng hệ số của v4 (1.3 ở T = 80, 1.2 ở T = 150). `textinfo` cần hệ số lớn hơn trên cell missing: 1.5 so với 1.3 của v4 ở T = 80, và 1.3 so với 1.2 ở T = 150. Đó là cái giá của targeted opening (under-cover trước calibration). Trên cell reversed, hệ số là 1.3, so với 1.4 của v4 ở T = 80.

### Verdict theo quy tắc ghi trước (nguyên văn từ `check_textinfo.py`)

**`textinfo`: REJECTED.** Điều kiện 1 không đạt: thắng **4 / 12** cell, cần ≥ 6. Điều kiện 2 đạt.

**`textinfo_all`: REJECTED.** Điều kiện 1 không đạt: thắng **2 / 12** cell. Điều kiện 2 đạt.

Điều kiện 1, ở a = 0.9: chênh lệch IS so với `tolerant_v4` [95% CI], kèm coverage:

| T | Cell | `textinfo` | `textinfo_all` |
|---|---|---|---|
| 80 | missing-0.2 | **−0.275 [−0.406, −0.132]** (0.944) | −0.001 [−0.019, +0.026] |
| 80 | missing-0.5 | +0.029 [−0.109, +0.194] (0.958) | −0.005 [−0.041, +0.027] |
| 80 | reversed-0.2 | **−0.054 [−0.093, −0.008]** (0.933) | **−0.054 [−0.093, −0.008]** |
| 80 | reversed-0.5 | −0.025 [−0.096, +0.046] (0.917) | −0.025 [−0.096, +0.046] |
| 150 | missing-0.2 | **−0.234 [−0.308, −0.157]** (0.965) | **−0.003 [−0.008, −0.000]** |
| 150 | missing-0.5 | **−0.092 [−0.147, −0.034]** (0.971) | −0.003 [−0.025, +0.017] |
| 150 | reversed-0.2 | −0.033 [−0.065, +0.002] (0.975) | −0.033 [−0.065, +0.002] |
| 150 | reversed-0.5 | −0.032 [−0.084, +0.013] (0.966) | −0.032 [−0.084, +0.013] |
| 80, 150 | extra (4 cell) | 0 (trùng v4 theo thiết kế) | 0 |

Để so độ lớn: IS của v4 là 3.28 / 3.37 / 2.79 / 2.97 ở T = 80 và 2.06 / 2.22 / 1.89 / 2.02 ở T = 150 (theo thứ tự các dòng trên). Lợi lớn nhất là −8% (missing-0.2, T = 80) và −11% (missing-0.2, T = 150). Trên cell reversed, lợi chỉ 1–2%.

Điều kiện 2, ở a = 0.5: tỉ số IS so với v4 nằm trong 0.92–1.016 cho `textinfo` và 0.999–1.016 cho `textinfo_all`. Mức xấu nhất là reversed-0.5 ở T = 80 (1.016), dưới ngưỡng 1.05. Trên none/extra tỉ số đúng bằng 1.000.

### Đọc kết quả (mô tả, không thay đổi verdict)

- **Phần lợi của `textinfo` trên cell missing chủ yếu đến từ targeted opening, không phải từ text.** `textinfo_null` (không text) so với v4 đạt −0.192 [−0.349, −0.049] (T = 80, missing-0.2), −0.218 (T = 150, missing-0.2) và −0.076 (T = 150, missing-0.5); coverage 0.935–0.967. Phần text thêm vào (S1, `textinfo@a0.9` − `textinfo_null`) trên cell missing chỉ từ −0.08 đến +0.04, và CI đều cắt 0. Phần lợi do targeted opening chồng lên hướng `narrow`.
- **Trên cell reversed, text có đóng góp riêng rõ ràng nhưng nhỏ.** S1 âm và CI không cắt 0 trong **4 / 4 cell reversed**: −0.039, −0.080, −0.032, −0.073. Mức này là 1–4% của IS. So với v4 thì phần lợi này bị bù trừ một phần, nên chỉ 1 / 4 cell có CI < 0. Lý do: chính bộ máy không text (`textinfo_null`, rút đảo đều, hệ số width 1.3 so với 1.4 của v4 ở T = 80) đã kém v4 một chút trên reversed-0.5 (+0.055 ở T = 80, +0.041 ở T = 150, CI chạm 0).
- **S2, đơn điệu theo chất lượng:** lợi so với v4 tăng dần khi a đi từ 0.5 → 0.7 → 0.9 ở 7 / 8 cell missing/reversed của `textinfo`. Ngoại lệ là missing-0.5 ở T = 150, phẳng ở khoảng −0.09 vì đã mở 55 / 81 block. Chiều hướng đúng như kỳ vọng; độ lớn thì nhỏ.
- **Text vô dụng (a = 0.5) không gây hại đáng kể**, nhờ γ = 0.5 và weighted BH. Có một dấu hiệu: ở T = 80, missing-0.2, trọng số ngẫu nhiên làm thứ tự mở kém hơn hẳn không dùng text (`textinfo@a0.5` 3.259 so với `textinfo_null` 3.085; +0.19 [+0.04, +0.36]). Text nhiễu không gây hại *so với v4*, nhưng có hại *so với chỉ dùng dữ liệu*.
- **Vì sao lợi nhỏ.** (i) Reversal pool của v3 đã nhỏ: chỉ các cặp cùng kỳ significant, nên một trọng số tốt chỉ dồn xác suất trong vài cặp. (ii) Interval score phạt nặng khi trượt truth, nên các bước nới mù của v4 vốn đã gần tối ưu về coverage; thu hẹp được thì ít. (iii) Cell extra không có chỗ cho text, vì module không tiêu ngân sách ở đó.

### Sign pruning (`results/ext_textinfo_sign/`, 20 topology × 2, mô tả)

`textinfo_sign` − `textinfo` (cùng bootstrap draw, cùng hệ số width): chênh lệch IS nằm trong **−0.036 đến +0.000** trên mọi cell, ở cả a = 0.5 và 0.9; coverage không đổi. Lợi lớn nhất là missing-0.5 ở T = 80. Prune chỉ thực sự được áp ở 0–42% số lần fit; các lần còn lại, nó sẽ bỏ quá nửa số draw nên bị tắt. Với hệ số cạnh 0.3–0.8 và T ≥ 80, dấu của một hệ số hiếm khi đổi giữa các draw, nên sign hint gần như không mang thêm thông tin. **Sign pruning không đáng giữ.**

**Kết luận của hướng.** Với side information theo cặp ở chất lượng AUROC tới 0.9, module dùng text **không vượt được quy tắc ghi trước** so với `tolerant_v4`. Text cho một lợi nhỏ nhưng nhất quán trên cell đảo cạnh (1–4%) và không gây hại khi vô dụng. Phần lợi lớn hơn trên cell thiếu cạnh đến từ targeted opening theo dữ liệu, tức hướng `narrow`, không phải từ text. `tolerant_v4` vẫn là module chính thức.


## 7. Dữ liệu thật: side information mà case study sẽ có (chỉ mô tả)

Script `experiments/ext/textinfo/real_side_info.py` (chỉ đọc ba file của Paper 1, không gọi LLM, không đọc `.env`). Kết quả: `results/ext_textinfo_real/inventory.md` và `side_info.json` (đúng định dạng `skel.damage["text"]` mà module đọc, khóa theo chỉ số của 14 nút core).

**Ánh xạ.** 14 nút core là danh sách nút của các topology D-07. Khóa của prior graph có dạng `source|target` bằng đúng tên canonical, nên ánh xạ là khớp tên trực tiếp. **21 / 42** cạnh prior có cả hai đầu trong core; **70** cặp core nằm ngoài prior. 77 / 124 quan hệ đã trích nối hai nút core khác nhau.

**Doubt trên 21 cạnh prior:**

| Tín hiệu | Số cạnh |
|---|---|
| confidence < 0.6 | 12 |
| chỉ một nguồn | 12 |
| `conflicted` | 6 |
| có ≥ 1 quan hệ bị verifier reject trên cặp | 11 |
| có quan hệ trích theo chiều ngược lại | 4 |
| các instance accepted ngược dấu nhau | 3 |
| **có ít nhất một tín hiệu doubt** | **20 / 21** |

Chỉ 1 cạnh (`bank_npl_ratio → bank_roe_ratio`) không có tín hiệu nào. Điểm doubt tổng hợp chỉ có 12 giá trị khác nhau trên 21 cạnh, vì confidence chỉ nhận vài mức (0.42 / 0.51 / 0.7 / 0.85). Có nhiều cặp hòa hạng, nên độ phân giải xếp hạng thấp. Cạnh đáng ngờ nhất là `bank_nim_ratio → bank_car_ratio`: confidence 0.42, một nguồn, 4 quan hệ bị reject, 3 quan hệ theo chiều ngược.

**Suspicion trên 70 cặp ngoài prior:**

| Tín hiệu | Số cặp |
|---|---|
| co-mention theo trường `candidate_nodes` đã lưu | 19 |
| co-mention theo lexicon từ khóa | 35 |
| **co-mention theo một trong hai** | **41 / 70** |
| có quan hệ đã trích nhưng bị reject | 2 |
| có quan hệ accepted nhưng không vào prior cuối | 1 |

Phần lớn tín hiệu suspicion đến từ co-mention. Co-mention là tín hiệu yếu: hai biến hay được nhắc cùng nhau (ví dụ NIM, nợ xấu, CAR trong cùng một báo cáo ngân hàng) không có nghĩa là có cạnh. Chỉ 3 cặp có bằng chứng dạng quan hệ.

**Sign và lag hint.** 16 / 21 cạnh có sign (positive/negative); 5 cạnh còn lại mang nhãn `policy_shock`, không phải dấu. Lag hint gần như không có thông tin: 19 cạnh có `immediate`, 2 cạnh có `1_quarter`, còn lại `unknown`. Vì vậy module **không dùng lag hint**: một hint `immediate` gần như đồng loạt không phân biệt được cạnh nào.

**Không có ground truth**, nên không thể biết AUROC thật của các điểm này là 0.5, 0.7 hay 0.9. Mục 6 chỉ cho biết lợi ích *nếu* điểm đạt một mức chất lượng nào đó.

## 8. Caveat

- **Side information tổng hợp lý tưởng hơn thật.** Nhiễu độc lập giữa các cặp, mô hình binormal, không phụ thuộc vào độ mạnh của cạnh. Văn bản thật có thể nghi ngờ đúng những cạnh yếu (ít được nhắc), là những cạnh ít ảnh hưởng tới hiệu ứng nhất. Lỗi của văn bản cũng có thể tương quan với lỗi của dữ liệu.
- **AUROC của doubt gộp chung thừa và đảo.** Module chỉ dùng doubt cho rút đảo. Trong dữ liệu thật, một cạnh bị nghi có thể là thừa chứ không phải đảo.
- **Mọi kết quả đều ở mức exploratory** trên D-07 development. γ và hệ số mở được chọn trên D-07H development (bank calibration), không phải trên bank đánh giá. Chưa có held-out check: mọi split của các bank hiện có đã được dùng (xem `docs/decision_rules.md`).
- **Ranh giới plan chưa được quyết** (mục 2).
- **Lag hint không dùng được** trên dữ liệu thật hiện có (mục 7).

## 9. Đề xuất cần LLM (PENDING, chờ người dùng duyệt; chưa làm)

Không có đề xuất nào dưới đây đã được thực hiện. Xem thêm `docs/ext/de_xuat_llm_pending.md` (L1–L5), tài liệu chung cho các hướng.

- **T1. Đo chất lượng thật của side information** (gần L2). Cho LLM đọc lại các chunk liên quan tới từng cặp core và gán nhãn "có quan hệ trực tiếp / gián tiếp / không / chiều nào", dùng nhiều prompt và nhiều model. Độ đồng thuận giữa chúng (không phải logit confidence) là một điểm doubt/suspicion tốt hơn co-mention. Nó cũng cho một ước lượng thô về mức AUROC mà văn bản có thể đạt, để đọc kết quả mục 6.
- **T2. Lag hint có nội dung.** `lag_hint` hiện tại gần như toàn `immediate`/`unknown`. Một LLM trích "sau bao lâu" từ câu văn (ví dụ "sau hai quý") sẽ cho lag hint thật. Khi đó có thể mở lag block theo đúng lag thay vì cả block.
- **T3. Chiều cho cạnh được repair** (gần L4). Hiện chiều của cạnh cùng kỳ được thêm lại bị rút ngẫu nhiên. Có thể hỏi LLM chiều của các cặp do dữ liệu đề xuất, rồi thay xác suất 0.5 bằng xác suất có trọng số.
