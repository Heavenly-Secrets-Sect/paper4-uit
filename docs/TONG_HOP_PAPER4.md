# Tổng hợp Paper 4: trạng thái đến 2026-11-02

Tài liệu đọc trước. Nó gom mọi thứ đã làm và đã tìm ra, kể cả những gì thất bại. Mỗi con số đều có đường dẫn tới file gốc. Thuật ngữ kỹ thuật giữ nguyên tiếng Anh.

**Mức độ chắc chắn của các con số:**
- **"Xác nhận"**: đạt quy tắc ghi trước trên bank niêm phong P4-H2, chạy đúng một lần. Đây là mức chắc chắn nhất.
- **"Exploratory"**: chỉ trên D-07 development. Bank này đã được dùng nhiều lần để thiết kế method, nên kết quả trên nó có thể lạc quan.

---

## 0. Đọc trong 2 phút

1. Paper 4 đề xuất **một** phương pháp: `tolerant_v5_1`. Nó ước lượng hiệu ứng động C(H) kèm interval 95% khi skeleton đầu vào có thể sai (thiếu, thừa, đảo cạnh), dựa trên mức hỏng do người dùng khai báo.
2. Trên bank niêm phong P4-H2, cả ba claim chính đều **CONFIRMED**, kể cả sau hiệu chỉnh Bonferroni:
   - **v5.1 tốt hơn bản trước (v4) ở T nhỏ.** Ở T = 40 khi thiếu cạnh, interval score 4.62 / 4.99 so với 7.81 / 7.54, và không tệ hơn ở bất kỳ cell nào khác.
   - **v5.1 tốt hơn một envelope gồm 7 baseline** ở T = 80/150 khi thiếu cạnh: thắng 27/27 so sánh đã đăng ký, không thua so sánh nào.
   - **Một biến thể không cần khai báo mức hỏng (`tolerant_auto3`)** giữ coverage ≥ 0.93 ở mọi cell được kiểm, kể cả khi có biến ẩn.
3. **Vẫn chỉ là exploratory:** nhiễu đo, cờ tin cậy RQ4.4, lag output khi cạnh bị đảo, và so sánh với Targeted Local Projections (TLP) ngoài cell thiếu cạnh.
4. **Dữ liệu thật 14 × 19:** với lag_max = 1, v5.1 dùng được kể cả khi skeleton được khai báo thiếu cạnh (v4 thì không). Riêng ô đảo nhiều cạnh (reversed-0.5) không dùng được. Kết quả là exploratory, xem docs/ext/region51.md.
5. **Cần thầy quyết 4 việc** (mục 10).

---

## 1. Câu hỏi nghiên cứu nằm ở đâu

Các câu hỏi nghiên cứu nằm trong plan của thầy: `references/source_material/00_context_and_planning/Plan_Paper3_Paper4_Paper5.docx`, **mục 5.1** (Bài 4). Nguyên văn:

| RQ | Nguyên văn trong plan |
|---|---|
| RQ4.1 | Sai số cường độ và độ trễ thay đổi thế nào theo loại và mức hỏng của skeleton (nền tảng để thiết kế module)? |
| RQ4.2 | Ước lượng gộp bất định cấu trúc (khoảng hiệu ứng trên các skeleton khả dĩ quanh skeleton đã chọn) có độ phủ đúng mức danh nghĩa và hẹp hơn các cách báo một điểm không? |
| RQ4.3 | Cạnh nào của skeleton, khi sai, làm hiệu ứng lệch nhiều nhất (bản đồ chi phí theo cạnh), và bản đồ này có ổn định qua các topology không? |
| RQ4.4 | Có đại lượng quan sát được, không cần truth, dự báo được độ tin cậy của hiệu ứng không? |

Các mục khác của plan liên quan:
- **Mục 5.2:** thiết kế thí nghiệm.
- **Mục 5.4:** metric. Gồm sai số tuyệt đối/tương đối của cường độ, sai số lag, coverage, độ rộng; không dùng F1/SHD.
- **Mục 7:** interface. Module nhận skeleton, mức hỏng và dữ liệu.
- **Mục 8:** năm sản phẩm.
- **Mục 9:** hướng mở rộng. Biến ẩn và nhiễu đo được giao cho Bài 4.

### Trả lời từng RQ và trạng thái

| RQ | Trả lời ngắn | Trạng thái | Nguồn |
|---|---|---|---|
| RQ4.1 | Cạnh thiếu là loại hỏng nặng nhất. Cặp có cạnh trực tiếp bị xoá: `plugin` có sai số tương đối khoảng 1.0 và sai số mean-lag khoảng 0.9 quý; v4 giảm còn 0.63 và 0.37 (T40, thiếu 20%). Cạnh thừa gần như vô hại. Cạnh đảo làm sai cả lag | Exploratory | docs/ext/bang_ban_thao.md bảng 4a; docs/ext/metrics.md |
| RQ4.2 | **Đúng nửa đầu, sai nửa sau.** Module đạt coverage danh nghĩa (0.92–0.97, trong khi `plugin` chỉ 0.33–0.66 khi thiếu cạnh). Nhưng interval của module **rộng hơn**, không hẹp hơn: width gấp 1.2–3.6 lần `plugin`, vì `plugin` hẹp mà sai. Paper phải phát biểu lại RQ4.2 theo interval score, thước đo gộp cả độ rộng lẫn việc trượt | **Xác nhận** (phần interval score, P4-H2) | docs/ext/bang_ban_thao.md bảng 5a, 5b; mục 4 dưới đây |
| RQ4.3 | Gần như toàn bộ chi phí đến từ cạnh **nằm trên đường truyền dẫn** giữa hai biến. Mất một cạnh như vậy làm hiệu ứng lệch 81–93%. Bản đồ chi phí ổn định qua các topology (Spearman 0.97–0.99) | Exploratory | docs/ket_qua_rq43.md |
| RQ4.4 | **Có, ở mức vừa.** Một cờ logistic đã khóa trước (width, relative width, mức hỏng khai báo) đạt AUROC 0.73 ở T80/150 và 0.82 ở T40 trên dữ liệu mới. Cặp bị gắn cờ trượt nhiều gấp 4.3 lần. Các diagnostic plan gợi ý (độ ổn định hệ số, phần dư) **không** dự báo được theo chiều đã nêu | Exploratory (bị loại khỏi lượt chạy P4-H2) | docs/ext/bang_ban_thao.md bảng 6; docs/ext/revlag.md |

### Năm sản phẩm theo mục 8 của plan

| Sản phẩm | Trạng thái |
|---|---|
| 1. Module ước lượng chịu lỗi (đóng góp chính) | Có: `tolerant_v5_1`, đã xác nhận |
| 2. Bản đồ chi phí theo cạnh | Có (RQ4.3), exploratory |
| 3. Chẩn đoán độ tin cậy | Có (RQ4.4), exploratory |
| 4. Vùng dùng được theo (mức hỏng, T, lag) | Có cho cả v4 và v5.1 (docs/ket_qua_vung_dung_duoc.md, docs/ext/region51.md). v5.1 dùng được ở nhánh thiếu cạnh từ T = 19 / 40 / 80 với lag_max 1 / 2 / 4; v4 cần 25 / 40 / 150. Exploratory |
| 5. Generator động kèm hàm mở rộng T | Generator có. **Hàm lạm phát chưa làm**, vì plan chưa định nghĩa |

---

## 2. Thiết lập thực nghiệm

### 2.1 Sinh dữ liệu
1. Lấy một **topology**, tức đồ thị nhân quả 14 nút, 21 cạnh.
2. Gán cho mỗi cạnh một lag (0, 1 hoặc 2 quý) và một hệ số. Kết quả là "true model", một SVAR, viết trong `src/paper4/generator.py`.
3. Từ true model, sinh dữ liệu T × 14 và tính **C_true**, tức ground truth của hiệu ứng.
4. Lấy skeleton thật rồi **làm hỏng có kiểm soát**: xoá, thêm hoặc đảo 20% hay 50% số cạnh.
5. Đưa (dữ liệu, skeleton hỏng, mức hỏng khai báo) vào từng method. So output với C_true.

### 2.2 Các topology bank

Mỗi bank gồm 40 đồ thị, chia đôi thành development và confirmatory. Tất cả sinh bằng cùng một script với bank D-07 của Paper 2.

| Bank | Nguồn gốc | Vai trò |
|---|---|---|
| D-07 | Paper 2 | **Phần development**: nơi phát triển và thử mọi method. Mọi số exploratory đều từ đây |
| D-07H | Paper 2 (held-out) | **Phần development**: hiệu chỉnh width (calibration). Không dùng để chấm điểm |
| P4-H1 | Sinh cho Paper 4, seed 20261102 | Kiểm tra held-out cho v4 (vòng đầu) và cho nhóm A |
| **P4-H2** | Sinh sau vòng 1, seed 20261103 | **Niêm phong:** không ai nhìn vào cho tới lượt chạy xác nhận duy nhất ngày 2026-11-02 |

**Vì sao cần niêm phong.** D-07 đã được dùng nhiều lần để chỉnh method. Một kết quả tốt trên D-07 có thể chỉ do method đã bị nắn theo chính bank đó. P4-H2 chưa từng bị nhìn trước, nên kết quả trên nó là bằng chứng độc lập. Hiện mọi split đều đã dùng; claim xác nhận mới sẽ cần sinh bank mới. Phần development của P4-H2 vẫn chưa mở.

### 2.3 Thước đo
- **Coverage:** tỷ lệ interval chứa C_true, gộp trên mọi cặp có hiệu ứng thật và mọi lượt chạy. Mục tiêu khoảng 0.95.
- **Interval score (IS):** IS = độ rộng + 40 × (khoảng cách từ C_true tới interval, nếu trượt). Càng thấp càng tốt. Đây là thước đo chính khi so method.
- **So sánh ghép cặp:** hiệu IS giữa hai method trên cùng dữ liệu, CI 95% bằng bootstrap theo topology, kèm hiệu chỉnh Holm khi so nhiều cell.

### 2.4 Quy trình chống "chỉnh theo kết quả"
- Mọi quy tắc giữ hay loại được **ghi trước khi chạy**, trong `docs/decision_rules.md` hoặc doc của từng hướng.
- Kết quả, kể cả thất bại, được chép nguyên văn sau khi chạy.
- Mỗi hướng có một agent kiểm chứng độc lập: tính lại số, đối chiếu thời điểm ghi quy tắc, thử code trên ví dụ biết đáp án.

---

## 3. Phương pháp đề xuất: `tolerant_v5_1`

**File:** `src/paper4/ext_v51.py`, dựng trên `src/paper4/ext_narrow.py` và `src/paper4/methods.py`.

**Input:**
- dữ liệu T × 14;
- skeleton (cặp nào nối nhau, chiều của cạnh);
- mức hỏng khai báo: số cạnh thiếu k, số cạnh thừa, số cạnh đảo r. Chỉ là số lượng, không cho biết cạnh nào.

**Output:** C(H) cho mọi cặp biến, kèm interval 95%.

### Các bước

```
dữ liệu + skeleton + khai báo (thiếu k, đảo r)
  │
  ├─ [1] Chấm bằng chứng cho từng cặp KHÔNG nối trong skeleton
  ├─ [2] Targeted lag opening: chỉ mở lag cho các cặp có bằng chứng mạnh nhất
  ├─ [3] Contemporaneous repair: thêm lại cạnh cùng kỳ nghi bị thiếu
  ├─ [4] Targeted reversal: lật thử các cạnh cùng kỳ có hệ số đáng kể
  ├─ [5] Bootstrap: mỗi draw làm lại [1]–[4] trên dữ liệu giả → 199 giá trị C(H)
  └─ [6] Hiệu chỉnh width hai chiều → interval cuối
```

**[1] Chấm bằng chứng.** Với mỗi cặp (u, v) không nối trong skeleton, chạy ba test trong **phương trình cấu trúc của chính skeleton**:
- F-test: thêm khối lag của u vào phương trình của v;
- F-test theo chiều ngược lại;
- Fisher z trên tương quan giữa phần dư cấu trúc của u và v.

Ba p-value được gộp bằng Šidák.

Lý do không test trong reduced-form VAR: ở đó, hiệu ứng truyền qua cạnh cùng kỳ làm các cặp không nối nhau trông như có quan hệ Granger. Đây là phát hiện từ thử nghiệm B1 (mục 8).

**[2] Targeted lag opening.** Đây là điểm mới chính so với v4.
- v4 đưa lag của **cả 14 biến** vào mọi phương trình. Ở T = 40, đó là 28 biến hồi quy trên 38 dòng, nên phương sai rất lớn và interval rất rộng.
- v5.1 chỉ mở khối lag cho **K cặp có p-value nhỏ nhất**, với K = max(3k, số cặp có p < 0.10).
- Danh sách term được khử trùng lặp.

**[3] Contemporaneous repair** (giữ từ v4). Cạnh cùng kỳ bị thiếu để lại dấu vết là tương quan giữa phần dư. Module kiểm định bằng Benjamini–Hochberg rồi thêm lại tối đa k cạnh. Chiều của các cạnh này dữ liệu không xác định được, nên mỗi draw rút chiều ngẫu nhiên.

**[4] Targeted reversal** (giữ từ v4). Mỗi draw lật r cạnh, chỉ trong số các cạnh cùng kỳ có |t| > 1.645.

**[5] Bootstrap có chọn lại cấu trúc.** Mỗi draw sinh dữ liệu giả từ phần dư, rồi **làm lại bước [1]–[4]** trên dữ liệu giả đó. Interval, tức phân vị 2.5–97.5% của 199 giá trị C(H), vì vậy phản ánh cả nhiễu dữ liệu lẫn sự không chắc chắn về cấu trúc. Đây chính là ý "khoảng hiệu ứng trên các skeleton khả dĩ quanh skeleton đã chọn" trong RQ4.2.

**[6] Hiệu chỉnh width hai chiều.** Interval được nhân với một hệ số tune trước cho từng cặp (T, loại hỏng khai báo), trên bank riêng D-07H. Hệ số có thể **dưới 1**. v4 thì chỉ nới được, nên ở T = 40 nó over-cover (0.98).

**Khi khai báo không có cạnh thiếu,** v5.1 chạy giống v4, chỉ khác bước [6].

**Về tham số τ trong code:** code có một ngưỡng chuyển sang "mở toàn bộ lag" khi T lớn. Với 14 biến và T ≤ 150, ngưỡng này không bao giờ được kích hoạt (360/360 run trên P4-H2 đều đi nhánh targeted). Paper không mô tả τ là một phần của method, chỉ nhắc ở phần threats.

### Ablation: thành phần nào đóng góp gì

Nguồn: docs/ext/bang_ban_thao.md, bảng 2a và 2b (exploratory).

| Thành phần | Tác dụng |
|---|---|
| Repair + orientation draws (từ v4) | Nguồn lợi thế so với cách chỉ mở mọi lag. `fullvar_cal` tệ hơn v4 ở 19/21 cell sau Holm |
| Hiệu chỉnh width hai chiều (`tolerant_v4c`) | Giảm IS 0.71–0.79 ở T40 khi thiếu cạnh; ở cell khác gần như không đổi |
| Targeted lag opening, chọn lại trong từng draw | Giảm IS ở cả 6 cell thiếu cạnh (−0.23 đến −2.93), không làm tệ cell nào |

---

## 4. Kết quả đã xác nhận trên P4-H2

Lượt chạy duy nhất diễn ra ngày 2026-11-02, 08:07–08:50 UTC. Guard kiểm hash trước và sau đều PASS: code không đổi trong lúc chạy. Không run nào thất bại. Verdict nguyên văn nằm trong `docs/decision_rules.md`, mục "Outcome of the P4-H2 confirmatory run".

| Spec | Câu hỏi | Verdict | Số chính |
|---|---|---|---|
| **P1** | v5.1 có tốt hơn v4 mà không hại ở đâu không? | **CONFIRMED** (cả sau Bonferroni) | T40 thiếu 20%: IS 4.62 so với 7.81, hiệu −3.19 [−3.54, −2.87]. T40 thiếu 50%: 4.99 so với 7.54, hiệu −2.55 [−2.76, −2.34]. Coverage 0.928 / 0.947. Ở 19 cell còn lại, không cell nào tệ hơn có ý nghĩa |
| **P2** | `tolerant_auto3` có giữ coverage không cần khai báo không? | **CONFIRMED** | Coverage 0.929–0.984 ở 8 cell thiếu/đảo cạnh; 0.945–0.975 khi có biến ẩn. Holm 14/14 |
| **P7** | v5.1 có tốt hơn baseline mạnh nhất không? | **CONFIRMED** (cả sau Bonferroni) | Tái lập 27/27 so sánh thắng ở T80/150 khi thiếu cạnh, không thua so sánh nào. Cell hòa duy nhất là T150 thiếu 50% so với `pselect_union_v3_cal`: −0.05 [−0.17, +0.04]. Baseline đó dùng gấp 32 lần số bootstrap draw |
| P7-v4 (phụ) | v4 so với cùng envelope | CONFIRMED (19/19), không thua | Ở D-07 v4 từng thua tại T150 thiếu 50%; ở P4-H2 thì không. v4 vẫn không thắng toàn bộ envelope ở cell nào |

**Bảy baseline của envelope:**
- `pselect_union_v3` và bản đã hiệu chỉnh width: chuyển thể từ Chang–Guo–Malinsky, Biometrika 2026, đủ ngân sách;
- `pselect_cal`;
- `fullvar_cal`: mở mọi lag;
- Targeted Local Projections đã hiệu chỉnh (Nemtyrev & Boldea 2026);
- TLP với double bootstrap;
- BVAR Minnesota đã hiệu chỉnh.

---

## 5. Kết quả exploratory (D-07 development, cùng held-out P4-H1 nếu có ghi)

| Chủ đề | Kết quả | Nguồn |
|---|---|---|
| Biến ẩn (1 hoặc 3 confounder) | v4: coverage ≥ 0.92 ở 11/12 cell, trong khi oracle còn 0.76–0.78. Bước repair nhầm confounder thành cạnh thiếu, nhưng coverage vẫn giữ. Đạt trên held-out P4-H1 | docs/ket_qua_nhom_a.md |
| **Nhiễu đo** | **Giới hạn chính.** Nhiễu 30%: v4 chỉ 0.77–0.89. Bản errors-in-variables `tolerant_eiv2` đạt 11/12 cell (cell hụt 0.897) nhưng bị loại; nó cũng tốn 5–12% IS trên dữ liệu sạch. v5.1 còn yếu hơn v4 ở nhiễu 10% (5/9 cell dưới 0.90) | docs/ext/eiv2.md; docs/ext/v51fix.md |
| Skeleton do GES của Paper 2 học | GES sót khoảng 60% cạnh và thêm khoảng 13 cạnh thừa. v4 vẫn đạt coverage 0.94–0.98, các method khác 0.32–0.59. Đạt trên held-out P4-H1 | docs/ket_qua_nhom_a.md |
| Lag output khi cạnh bị đảo | Lấy lag từ structural draws (`tolerant_v4L`) nâng peak-lag hit từ 0.01–0.05 lên 0.11–0.35. Vẫn xa oracle (0.90) | docs/ext/revlag.md |
| Coverage trên cặp chịu ảnh hưởng của cạnh đảo | v4 kém một oracle đã hiệu chỉnh 0.06–0.08. Một cách xử lý thay thế khả thi (revlag3) chưa thu hẹp được khoảng này | docs/ext/revlag.md; docs/ext/synthesis_round3.md |
| TLP ở T40 | TLP có IS thấp hơn v4 nhưng coverage chỉ 0.79–0.87. Bản TLP hiệu chỉnh width hòa v5.1 | docs/ext/tlp2.md |

---

## 6. `tolerant_auto3` là gì

**Vấn đề nó giải quyết.** v5.1 cần người dùng khai báo mức hỏng (thiếu bao nhiêu cạnh, đảo bao nhiêu). Ngoài đời, con số này thường không có. auto3 là biến thể **không cần khai báo**: nó tự quyết định từ dữ liệu.

**File:** `src/paper4/ext_gate.py`, kèm bảng width `experiments/ext/gate/width_table.json`.

**Cách làm:**
1. **Test từng cặp không nối** trong phương trình cấu trúc của skeleton: F-test khối lag theo hai chiều, cộng Fisher z trên tương quan phần dư, gộp bằng Šidák.
2. **Gate toàn cục.** Giả thuyết H0 là "skeleton không thiếu cạnh nào". p-value toàn cục = Šidák trên p nhỏ nhất của tất cả các cặp; ngưỡng α = 0.10. Ý tưởng theo Eulig et al. (AAAI 2025): kiểm tra đồ thị trước khi dùng nó.
3. **Gate đóng** (không đủ bằng chứng thiếu cạnh): fit đúng skeleton như được cho.
4. **Gate mở:** dùng nhánh thiếu cạnh của v4, tức mở mọi lag và repair cạnh cùng kỳ. Ngân sách repair lấy từ chính bằng chứng ở bước 1.
5. **Dự phòng cạnh đảo:** chiều cạnh cùng kỳ không chẩn đoán được từ dữ liệu, nên mỗi draw lật mỗi cạnh cùng kỳ đáng kể với xác suất 0.2.
6. **Width:** hệ số tune theo (T, trạng thái gate) trên D-07H.

**Kết quả:**
- Trên P4-H2 (spec P2): **CONFIRMED.**
- Trên D-07:
  - tốn 7–20% IS so với v4 có khai báo đúng;
  - trên skeleton đúng, thua raw `ida_union` 0.12–0.69 IS;
  - so với baseline được hiệu chỉnh công bằng, thắng plugin, IDA và BVAR ở 8/8 cell, thắng pselect ở 6/8 (2 cell hòa).

**Quan hệ với v5.1.** auto3 **không phải một chế độ của v5.1**. Nó là code riêng, xây trên nền v4: khi gate mở thì mở mọi lag, không dùng targeted opening. Bản ghép gate với v5.1 (`tolerant_auto5`) đã thử và bị loại ở mức nhiễu: một cell đạt 0.898 so với ngưỡng 0.90.

**Lựa chọn cho paper, khi chỉ đề xuất một method:**
- **(a) Khuyến nghị:** v5.1 là method chính. auto3 nằm trong một mục ngắn "Extension: khi không khai báo được mức hỏng", ghi rõ đây là biến thể riêng, cũng đã xác nhận trên P4-H2.
- **(b)** Bỏ auto3 khỏi Paper 4, để dành cho Paper 5.

---

## 7. Thử nghiệm dùng văn bản và LLM

### 7.1 Không gọi LLM: dùng metadata Paper 1 có sẵn (hướng `textinfo`)
- **Ý tưởng:** biến độ tin của cạnh, số nguồn, cờ `conflicted` và việc hai biến được nhắc cùng nhau trong 278 chunk thành **bản đồ nghi ngờ theo từng cạnh**. Module sẽ ưu tiên nới lỏng những cạnh đáng ngờ.
- **Đánh giá:** trong mô phỏng, tín hiệu văn bản được thay bằng tín hiệu tổng hợp có chất lượng kiểm soát (AUROC 0.5 / 0.7 / 0.9).
- **Kết quả: bị loại** (thắng 4/12 cell, ngưỡng là 6/12).
  - Text chỉ giúp 1–4% ở cell đảo cạnh.
  - Text vô dụng thì không làm hại.
  - Phần lợi chính đến từ việc mở lag theo bằng chứng dữ liệu. Ý này về sau trở thành targeted opening của v5.
- Nguồn: docs/ext/textinfo.md.

### 7.2 Có gọi LLM (hướng `llm`)

**Ràng buộc:** 1152 lệnh gọi `gpt-5-mini-2025-08-07`. Mọi lệnh đều đi qua `src/paper4/llm.py`, client này cố định `store=False` và chỉ gửi khi IP đi ra ở Singapore. Mình đã kiểm tra lại cả 1152 bản ghi cache.

| Thử nghiệm | Kết quả |
|---|---|
| L1: hỏi thứ tự nhân quả cùng kỳ của 14 biến | Đảo chiều 4/21 cạnh prior |
| L4: hỏi về từng cạnh dựa trên chunk văn bản | Chiều nhất quán 96% giữa các prompt; câu trả lời có/không chỉ 70% |
| L3: trích chuỗi cú sốc chính sách | Chỉ 8 sự kiện đồng thuận trong 19 quý, quá thưa để làm external instrument |

**Phát hiện:**
- **LDR → POLICY_RATE có khả năng sai, và NIM → NPL có khả năng ngược chiều.** Hai phương pháp gần độc lập (L1 và L4) cùng chỉ ra.
- **Gợi ý cạnh thiếu:** NIM–PROV_COVERAGE, LDR → NPL.
- **Cột `macro_policy_rate_pct` trong panel lệch với văn bản.** Văn bản đặt các đợt tăng lãi suất ở 2022Q3 và 2022Q4, nhưng panel chỉ đổi ở 2022Q1 và 2023Q1. **Cần người kiểm tra.**
- **Chất lượng tín hiệu** khoảng AUROC 0.7, nhưng không loại trừ được 0.5 vì không có ground truth.

**Chưa làm:** chưa ghép tín hiệu LLM vào v5.1, và tín hiệu này không có trong lượt chạy P4-H2. Đề xuất còn lại ở docs/ext/de_xuat_llm_pending.md. Nguồn: docs/ext/llm.md.

---

## 8. Hành trình các phiên bản

| Phiên bản | Ý tưởng | Kết quả |
|---|---|---|
| v1 `soft` | Ridge prior cho cạnh ngoài skeleton | Loại: bias do shrinkage làm under-cover |
| v2 | Mọi lag + repair + lật chiều ngẫu nhiên | Loại: coverage ở cell đảo 20% chỉ 0.86–0.89 |
| v3 / v3_cal | Lật chiều có nhắm mục tiêu | Giữ |
| v4 | Hiệu chỉnh width riêng cho module | Giữ; module chính thức cho tới 2026-11-02 |
| B1 bản 1, bản 2 | Tự ước lượng mức hỏng bằng đếm Storey | Loại: báo động giả tốn 1.3–1.6 lần IS. **Phát hiện:** Granger test trên reduced-form không dùng được để kiểm tra adjacency |
| **auto3** (B1 bản 3) | Gate kiểm định trước khi mở lag | Giữ; xác nhận trên P4-H2 |
| v5 (vòng 1) | Targeted opening | Loại ở mức nhiễu. Có **bug** lặp lag term làm hệ số bị chia đôi |
| eiv, eiv2 | Errors-in-variables cho nhiễu đo | Loại (eiv2 đạt 11/12) |
| auto5 | Gate + targeted opening | Loại (0.898) |
| v4c | Width hai chiều | Giữ; dùng trong ablation |
| **v5.1** | v5 đã sửa bug + width hai chiều | **Giữ; xác nhận trên P4-H2; module chính thức hiện tại** |

---

## 9. Giới hạn và những gì reviewer sẽ hỏi

1. **Baseline mạnh nhất là bản chuyển thể của nhóm.** Biên thắng phụ thuộc ngân sách tính toán của baseline, nên bảng chính phải có cột ngân sách. Ở T150 thiếu 50%, v5.1 chỉ hòa.
2. **D-07 bị dùng lại nhiều lần.** Chỉ những claim chạy trên P4-H2 mới là xác nhận.
3. **RQ4.2 phải phát biểu lại:** module **rộng hơn** plugin chứ không hẹp hơn.
4. **Coverage sát 0.90 ở vài cell:** v5.1 có 0.918–0.928, và chỉ có 20 topology mỗi cell.
5. **Nhiễu đo và cạnh đảo** còn là giới hạn.
6. **Phạm vi hẹp:** chỉ SVAR tuyến tính Gaussian, 14 nút, một generator.
7. **Dữ liệu thật 14 × 19:** với lag_max = 1, v5.1 dùng được ở các ô none, missing và reversed-0.2, nhưng không ở reversed-0.5 (docs/ext/region51.md, exploratory). v4 không chạy được ở nhánh thiếu cạnh.
8. **Reproducibility:**
   - bug lặp term đã từng đảo một kết luận;
   - seed của method built-in phụ thuộc vị trí cell (bug E1, chưa sửa; kiểm tra trên P4-H2 cho 0 sai lệch);
   - nhiều lượt chạy phải chạy lại sau gián đoạn, và đều đã được công bố.

---

## 10. Cần thầy quyết

1. **auto3:** đưa vào Paper 4 dưới dạng extension, hay để sang Paper 5?
2. **Text/LLM:** thuộc Bài 4 hay Bài 5? Plan mục 8 nói Bài 4 không dùng `edge_score`, mà `edge_score` thuộc Bài 3; điểm theo cạnh lấy từ text đóng vai trò tương tự.
3. **Cột lãi suất `macro_policy_rate_pct`** trong panel thật có đúng không? Văn bản cho các mốc khác.
4. **Hàm lạm phát để mở rộng T** (sản phẩm 5): plan chưa định nghĩa.

Ngoài ra, chọn tên cho method trong bản thảo, ví dụ "Skeleton-Tolerant Dynamic SEM (ST-DSEM)".

---

## 11. Bản đồ file

| Nội dung | File |
|---|---|
| Plan của thầy | references/source_material/00_context_and_planning/Plan_Paper3_Paper4_Paper5.docx |
| Lịch sử quy tắc ghi trước và kết quả | docs/decision_rules.md |
| Tổng hợp vòng 1, 2, 3 | docs/ext/synthesis_round1.md, synthesis_round2.md, synthesis_round3.md |
| Bảng sẵn cho bản thảo | docs/ext/bang_ban_thao.md |
| Kết quả nhóm A (biến ẩn, nhiễu, GES, baseline) | docs/ket_qua_nhom_a.md |
| Khảo sát tài liệu 2023–2026 | docs/ext/khao_sat_tai_lieu_2023_2026.md |
| Phương pháp đề xuất | src/paper4/ext_v51.py, src/paper4/ext_narrow.py, src/paper4/methods.py |
| auto3 | src/paper4/ext_gate.py |
| Text/LLM | docs/ext/textinfo.md, docs/ext/llm.md, src/paper4/llm.py |
| Lượt chạy P4-H2 | results/ext_synthesis_round3_p4h2_logs/, results/ext_v51fix_p4h2/, results/ext_auto3fix_p4h2_*/, results/ext_baselines3_p4h2/ |

**Trạng thái git:** toàn bộ công việc từ tối 2026-11-01 **chưa commit**. Commit cuối là `c03d63e`.
