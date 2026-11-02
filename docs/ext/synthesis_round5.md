# Tổng hợp vòng 5: `tolerant_v5_2` = `tolerant_v5_1` + NG-A v3 + `hubscreen` v2

**Trạng thái.** Đây là bản tổng hợp của lead vòng 5. Mọi kết quả ở đây là **exploratory, chỉ trên D-07 development** với seed_base mới 70261102, trên cùng 20 topology đã dùng ở các vòng trước. Calibration f_red và smoke chỉ dùng D-07H development. Unit test V0 là dữ liệu mô phỏng hai biến, không thuộc bank nào. Mỗi item có một verifier độc lập. Verifier tính lại số bằng code riêng, kiểm thứ tự hash và chạy, kiểm truth leakage, và chạy thêm test riêng (V0 với seed khác, đếm term lag 0, probe đuôi IS, test ghép với gate bị ép đóng). **Không có gì chạy trên P4-H1 hay P4-H2 (cả development lẫn confirmatory).** Lead không chạy thí nghiệm nào và không sửa file nào ngoài file này.

**Yêu cầu của người dùng cho vòng này:** "chạy vòng 5", tức thực hiện đề xuất ở mục 4 của `docs/ext/synthesis_round4.md`: xây `tolerant_v5_2` từ hai thành phần đã sửa theo verifier vòng 4, rồi đánh giá theo rule ghi trước trên seed mới.

**Quyết định tóm tắt của lead.**
1. **`tolerant_v5_2` không được giữ.** Rule ghi trước cho kết quả **KEEP COMPONENT A ONLY**: P1 đạt nhưng P2 trượt (P2c chỉ 2/6 cell, cần ≥ 4).
2. **Thành phần A (NG-A v3, method `tolerant_ngA3`) được giữ ở mức exploratory.** Nó đạt V0, V1, P1 và no-harm (a), (b). Nhưng lợi ích chỉ khoảng 0.9% interval score (IS) dưới non-Gaussian shock tổng hợp `ng_mix`, chỉ 1/8 cell qua Holm, và **không tách được khỏi NG-A v2** (v3 − v2 = −0.21% [−0.48%, +0.05%]). Bản sửa luật dấu cải thiện rõ evidence về chiều (unit test, AUROC) nhưng chưa chuyển thành khác biệt IS đo được.
3. **Thành phần B (`hubscreen` v2) bị REJECTED.** Nó sửa được lỗi bỏ cha cùng kỳ của v1 (verifier đếm 0 vi phạm trên 161.020 lần rút gọn), hoàn tất 60/60 và giữ ITT coverage 0.943–0.968. Nhưng trên run được cứu nó chỉ chứng minh được non-inferiority so với `plugin_hs_cal` ở 1/6 cell T ≤ 25, và đuôi IS ở T19 còn rất nặng.
4. **`tolerant_v5_1` vẫn là module of record.** Lead không đề nghị nâng `tolerant_ngA3` thành module chính: lợi ích nhỏ, chỉ có dưới shock tổng hợp, runtime tăng khoảng 48%, nó đổi 64% số run của v5_1 mà không có lợi gì dưới Gaussian, và có một cell tệ hơn với CI không chứa 0 (ng_mix T40 reversed-0.5).
5. **Held-out trên P4-H2 development: lead khuyến nghị chưa xin** (mục 4). Về hình thức thì điều kiện mà vòng 4 đặt ra đã đạt, vì thành phần A đạt rule. Nhưng câu hỏi mà lượt chạy đó trả lời (A có giảm IS khoảng 1% dưới shock tổng hợp trên topology mới hay không) không đáng để tiêu split chưa mở cuối cùng. Mục 4 có spec, runtime và ý nghĩa từng kết quả, phòng khi người dùng vẫn muốn chạy.
6. **Verdict của cả 3 item đứng vững sau verifier. Phần bị bác lại là diễn giải**, cũng như vòng 4: 3/3 item có ít nhất một câu phụ bị bác. Câu đưa vào paper phải lấy từ mục 3 dưới đây.

---

## 0. Tình trạng 3 item

| Item | Nội dung | Verdict theo rule | Verifier | Phần giữ lại |
|---|---|---|---|---|
| `ngorient3` (thành phần A, `tolerant_ngA3`) | NG-A v3: R là log-likelihood ratio xấp xỉ (Hyvärinen–Smith 2013 mục 2), họ log-density chọn theo dấu kurtosis của **từng biến**; factor frozen của v5_1 | **RETAINED (exploratory)**: V0, V1, P1, (a), (b) đạt | **holds** (3 câu phụ bị bác) | Evidence về chiều tốt hơn rõ; IS −0.90% dưới ng_mix, không tách được khỏi v2 |
| `hubscreen2` (thành phần B, `tolerant_v5_1_hs2`) | CSIS như v1; khi \|C_j\| > cap − 1 chỉ bỏ own lag 2..lag_max, **không bao giờ bỏ term lag 0** | **REJECTED**: chỉ trượt P2c (1/6, cần ≥ 4) | partly (2 diễn giải bị bác, 1 lỗi câu chữ) | Chế độ dự phòng chạy được và không bỏ cha cùng kỳ; không tốt hơn `plugin_hs_cal` |
| `v52` (bản ghép `tolerant_v5_2`) | A + B ghép bằng cách gán lại tên trong namespace của A trong lúc gọi; f_red tune lại cho chính v5_2 | **KEEP COMPONENT A ONLY**: P1 đạt, P2 trượt (P2c 2/6) | **holds** (3 câu phụ bị bác) | Phép ghép đúng; không thêm bằng chứng mới cho A |

Thứ tự thời gian (UTC, ngày 2026-11-02), verifier đã kiểm:
- B hash lúc 14:44:52Z, run đầu lúc 14:44:59Z. A hash lúc 14:49:31Z, V0 bắt đầu lúc 14:49:34Z.
- A chạy ng_mix từ 14:53:50Z đến 15:07:39Z và Gaussian từ 15:07:39Z đến 15:20:07Z.
- v52 hash lúc 15:37:41Z, chạy từ 15:37:51Z đến 16:01:57Z.

Mọi analyzer đều được hash cùng rule. `shasum -c` sau run khớp ở cả ba item. Riêng doc thì khác hash vì đã append kết quả, nhưng phần rule giữ nguyên từng byte: A có 185 dòng đầu trùng bản hash; B được khôi phục từ transcript, hash đúng 51dada39…; v52 có 16612 byte đầu hash đúng c4fc346b….

---

## 1. Từng item: đã xây gì, rule, verdict, phần đứng vững, phần bị bác

### 1.1 `ngorient3`: NG-A v3 (thành phần A)

**Đã xây.** Module `src/paper4/ext_r5ngorient3.py`, method `tolerant_ngA3`. Chỉ hàm evidence thay đổi so với NG-A v2, mọi phần khác giữ nguyên từng dòng:
- Khi kurtosis trội, R là log-likelihood ratio xấp xỉ của hai chiều. Họ log-density chọn theo dấu excess kurtosis của chính từng biến: super-Gaussian dùng log cosh, sub-Gaussian dùng generalized Gaussian shape 4.
- Mỗi phần dư dùng họ của biến mà nó thay thế, nên hằng số chuẩn hóa triệt tiêu.
- Dạng skew, gate JB, jackknife se, cắt p vào [0.05, 0.95], Plackett–Luce và common random numbers giữ như v2.
- Factor thừa kế factor frozen của v5_1. Không chạy calibration nào.

**Rule** (doc mục 4, hash 14:49:31Z):
- **V0:** 36 cặp law có thứ tự, b ∈ {0.3, 0.6}, m ∈ {78, 148, 400}, 500 rep. Cần đạt 5 tiêu chí:
  - C1: tỉ lệ sai chiều khi gate mở, trên hỗn hợp ng_mix ở m 148, b 0.6, ≤ 0.10;
  - C2: mọi cặp non-Gaussian ở m 400 ≤ 0.30;
  - C3: tỉ lệ ở m 400 ≤ ở m 148;
  - C4: dưới Gaussian, gate mở ≤ 0.12 và mean p trong 0.5 ± 0.02;
  - C5: bất biến thang đo đến 1e-9.
- **V1:** trùng v5_1 từng bit ở mọi cell none/extra và ở mọi run không có gate nào mở; factor bằng nhau.
- **P1:** endpoint gộp là trung bình dIS/IS_v51 qua 8 cell ng_mix (T80/150 × missing/reversed × 0.2/0.5). Đạt khi cận trên 95% một phía < 0, với cluster bootstrap B 20000. Hai guard: coverage ≥ 0.90 ở 8/8 cell, và failure ≤ v5_1 + 1.
- **No-harm:**
  - (a) 21 cell Gaussian: tỉ số ≤ 1.03 và không tệ hơn sau Holm 21;
  - (b) 13 cell ng_mix không primary: tỉ số ≤ 1.05;
  - ở cả (a) và (b), coverage ≥ 0.90 nơi v5_1 đạt.
- Một cell chỉ được tính là win hoặc thua có ý nghĩa khi có ≥ 8 cluster.

Các điều chỉnh so với bản nháp 4.2 đều ghi trước khi chạy: tỉ lệ sai đọc theo nghĩa có điều kiện (khi gate mở); C3 đo ở b 0.6; P1 giữ hai guard của v1/v2; no-harm (c) không chạy riêng cho A.

**Verdict: RETAINED (exploratory).**
- V0 PASS.
- V1: 1080/1080 run none/extra và 6/6 run không gate trùng v5_1; factor bằng nhau 2520/2520.
- P1: endpoint gộp −0.90% [−1.42%, −0.35%], cận trên −0.44%, p 0.0003; coverage 0.938–0.970.
- (a): tỉ số 0.993–1.020. (b): tỉ số ≤ 1.030.

**Phần đứng vững sau verifier.**
- **V0 tái lập độc lập.** Verifier tự viết code evidence và sampler (seed 99112233, 400 rep). |p_verifier − p_module| ≤ 2.2e-15, và gate luôn trùng.
  - C1: 0.055 theo verifier, 0.058 theo item.
  - C3: 0.017 ở m 400 so với 0.055 ở m 148 (item: 0.018 so với 0.058).
  - C2: cặp tệ nhất 0.09 theo verifier, 0.098 theo item.
- **Evidence về chiều tốt hơn v2 rõ rệt** (V0, b 0.6, hỗn hợp ng_mix): tỉ lệ sai khi gate mở của v3 là 0.114 / 0.058 / 0.018 ở m 78 / 148 / 400, của v2 là 0.184 / 0.164 / 0.150. Cặp t5 → uniform: v3 0.036, v2 0.462. AUROC xếp cạnh bị đảo ở ng_mix, v3 / v2: T40 0.629 / 0.607, T80 0.747 / 0.715, T150 0.858 / 0.773.
- **P1 tái lập** bằng bootstrap riêng (seed 424242): −0.00896 [−0.0143, −0.0036], cận trên −0.0044, p 0.00035. Chỉ T150 reversed-0.2 qua Holm 8: −0.052 [−0.085, −0.020]. T150 missing-0.5 có p Holm 0.06–0.07; T150 reversed-0.5 có p Holm 0.092. Cả 8 cell có 20 cluster. **Ở 4 cell T80, dIS gần 0** (−0.009 đến +0.003), nên lợi ích dồn vào T150.
- **Coverage cặp affected** (dC ≥ 0.05): T150 reversed-0.2 tăng +0.040 [+0.022, +0.066], Holm p 0.0002. Ba cell reversed còn lại không có ý nghĩa.
- **No-harm tái lập.**
  - (a): tỉ số 0.9935–1.0196; p Holm nhỏ nhất 0.83 theo item, 0.88 theo verifier.
  - (b): tỉ số lớn nhất 1.0296. **Ở ng_mix T40 reversed-0.5, v3 tệ hơn v5_1 với CI không chứa 0**: +0.130 [+0.048, +0.223], tỉ số 1.030. Cell này vẫn qua (b) chỉ vì (b) dùng biên 1.05 và không kiểm định. T40 reversed-0.2 cũng nghiêng về phía tệ hơn (+0.050 [−0.011, +0.118]).
- **v3 không tách được khỏi v2 về IS.** v2 tự nó cũng đạt endpoint gộp (−0.69%, cận trên −0.26%). v3 − v2 = −0.21% [−0.48%, +0.05%] theo item (verifier: −0.20% [−0.48%, +0.04%]), CI chứa 0.
- **Factor:** `frozen_r5ngorient3.json` trùng `frozen_v4_v51.json` từng khóa; `info_c_T` của v5_1 và ngA3 bằng nhau 1260/1260 trên ng_mix và 1260/1260 trên Gaussian.
- Không có truth leakage: evidence chỉ dùng residual.
- **Runtime so với v5_1:** +48% trên ng_mix, +26% trên Gaussian.

**Phần bị verifier bác** (đều là câu phụ, không đổi verdict).
- "Seed 70261102 chưa từng dùng (đã kiểm guard)" là sai theo nghĩa đen. Lúc guard được viết (khoảng 14:48Z), B đã ghi manifest dùng seed này (cal từ 14:45Z, P2 từ 14:47Z). Seed vẫn mới so với vòng 1–4, và việc dùng chung là seed bắt buộc của vòng 5, nên dữ liệu vẫn đúng như dự định. Chỉ câu chữ của guard là cũ.
- "v2 không giảm theo m" là sai: 0.184 / 0.164 / 0.150 vẫn giảm đơn điệu. Câu đúng: **v2 giảm chậm và vẫn ở mức 0.15–0.18, còn v3 xuống khoảng 0.02 ở m 400.**
- "Mọi hash khớp" quá rộng: doc khác hash vì đã append kết quả. Phần rule trùng từng byte.

**Ghi chú của lead.**
- Gate mở dưới Gaussian ở mức pair là 0.078 / 0.119 / 0.160 ở T40 / 80 / 150, nên T150 vượt mức danh nghĩa 0.10 (giống v2).
- Ở mức run thì gate gần như luôn mở ở đâu đó: trong lưới G, 717/1260 run có ít nhất một gate mở trong dữ liệu hoặc trong một draw. Vì vậy V1 (ii) chỉ có 6 run để kiểm. Đây là kiểm tra yếu, và item đã thừa nhận.

### 1.2 `hubscreen2`: `hubscreen` v2 (thành phần B)

**Đã xây.** Module `src/paper4/ext_r5hubscreen2.py`, method `tolerant_v5_1_hs2`.
- Nhánh CSIS giữ nguyên như v1.
- Khi |C_j| > cap − 1, v2 chỉ bỏ own lag 2..lag_max và không bao giờ bỏ term lag 0.
- Nếu phương trình vẫn không qua check của `fit_equations` thì run fail và được tính vào ITT.
- Output có cờ `hs_reduced` và số phương trình bị rút gọn, chia theo data/total, truncation, fit-fail và screen-fail.
- f_red được tune trên D-07H development với 3 replicate.
- f_v51 lấy từ file frozen cho T40/80/150. Với T19–35 nó lấy từ calibration v5_1 của vòng 4, vì file frozen không có T < 40.

**Rule** (doc mục 3, hash 14:44:52Z):
- **V0:** unit test T1–T4.
- **V1:** trùng v5_1 từng bit trên mọi run có `hs_reduced` = 0, và 0 term lag 0 bị bỏ.
- **P2a:** hoàn tất ≥ 59/60 ở 12/12 cell (lag_max 2 × T{19, 25, 30, 35} × {missing, reversed, extra}-0.2).
- **P2b:** ITT ≥ 0.90 ở ≥ 10/12 cell, không cell nào < 0.85.
- **P2c:** trên run được cứu ở 6 cell T ≤ 25, so với `plugin_hs_cal`. H0 là tỉ số mean IS ≥ 1.10, kiểm bằng cluster bootstrap B 20000, Holm 6, cần ≥ 8 cluster. Đạt khi ≥ 4/6 cell.
- **No-harm (a):** trên G như A, thêm điều kiện đủ 60 dòng mỗi cell.

**Verdict: REJECTED**, chỉ trượt P2c.
- V0 PASS. V1 1618/1618.
- P2a 12/12 cell 60/60. P2b ITT 0.943–0.968 ở 12/12.
- P2c 1/6; đếm không hiệu chỉnh cũng 1/6.
- (a) 21/21 tầm thường, vì G không có run rút gọn nào nên tỉ số đúng 1.0000 ở cả 21 cell.

**Phần đứng vững sau verifier.**
- **Không bao giờ bỏ cha cùng kỳ khai báo.** Verifier gắn instrumentation riêng (không dùng bộ đếm của item) trên 240 run hs2 (T19/25, 92 run có truncation). Kết quả: 161.020 lần rút gọn, trong đó 21.416 ở nhánh truncation, mang 255.872 term lag 0, với **0 vi phạm** và 0 lần mất own lag 1. 5.040/5.040 cha (u, 0) khai báo có mặt trong fit mức data. IS tính lại trùng runs.jsonl 240/240.
- **P2c tái lập** với 3 bộ seed bootstrap, lần nào cũng 1/6. Chỉ T25 missing đạt: tỉ số 0.629, cận trên 0.806–0.807. T25 reversed có p 0.054–0.055, không đạt cả khi không hiệu chỉnh.
- **Đuôi IS rất nặng ở T19 missing:** mean 288.00 so với 56.81 của `plugin_hs_cal`, nhưng median 30.40 so với 40.38. IS lớn nhất 14361.7. Bỏ 3 run lớn nhất thì mean còn 37.31. hs2 có IS thấp hơn `plugin_hs_cal` ở 41/60 run.
- **Identity trung thực:** 89/1707 run v5_1-ok bị đổi, cả 89 do rút gọn chỉ trong draw.
- **Mô tả:** ở T25 missing, hs2 tệ hơn v5_1 có ý nghĩa: tỉ số 1.302, +3.663, 26 run, 13 cluster, cùng factor 1.6.

**Phần bị verifier bác.**
- **"Đuôi nặng đến từ fit gần explosive ở m = 17" là chưa được đo, và câu chữ sai.** Probe của verifier (`results/ext_verify5_hubscreen2/tail_probe.json`) đo spectral radius của companion matrix dạng rút gọn:
  - run có IS lớn nhất có radius 8.18 (IS 14361.7), các run tiếp theo 3.71, 2.19, 1.77, 1.42;
  - run có IS quanh median (khoảng 30) cũng explosive, radius 1.16–1.49, và 100% fit mức draw của chúng có radius ≥ 1;
  - dof nhỏ nhất của phương trình là 1–2 ở cả hai nhóm.

  Vậy các fit này không "gần" explosive mà là explosive, ở cả run điển hình. Chỉ **độ lớn** của radius đi cùng đuôi.
- **"v2 gần như không khác v1 về IS, nên giữ cha cùng kỳ không phải nguồn của đuôi" bị confound bởi factor.** v1 dùng f_red vòng 4, v2 dùng f_red tune lại ở vòng 5: T19 extra 4.2 so với 3.7, T30 reversed 3.0 so với 4.0, T25 extra 3.4 so với 2.9. Các cell có IS khác nhau (19 extra 1.095, 30 reversed 0.915, 25 extra 1.051) đi theo chiều của thay đổi factor. Bằng chứng trực tiếp duy nhất là run có IS lớn nhất ở T19 missing (14361.7) trùng nhau giữa v1 và v2.
- **Lỗi câu chữ nhỏ:** khóa 35|missing có khóa riêng (3 run, đúng MIN_RED), không gộp theo T. Giá trị vẫn là 1.8, nhưng factor này chỉ được tune trên 3 run.

**Ghi chú của verifier, lead giữ lại.** Trên run v5_1-ok chỉ bị đổi do rút gọn trong draw, hs2 nhân f_red thay vì f_v51 (T30 missing 2.0 so với 2.2, T30 reversed 3.0 so với 3.7). Vì vậy IS giảm ở T30 trong doc mục 5.3.4 một phần là hiệu ứng factor.

### 1.3 `v52`: bản ghép `tolerant_v5_2`

**Đã xây.** Module `src/paper4/ext_r5v52.py`. Mỗi lần gọi, module gán lại `fit_equations`, `select_open` và `bootstrap_C` trong namespace của `ext_r5ngorient3` sang bản rút gọn của B, rồi trả lại tên cũ trong `finally`.
- f_red được tune lại cho chính v5_2 trên D-07H development (3 replicate, luật và fallback của B), vì smoke cho thấy gate mở ở gần như mọi run P2 có rút gọn.
- f_v51 frozen.
- Kết quả với f_red của B được báo song song.

**Rule** (doc mục 4, hash 15:37:41Z). Chuyển từ mục 4.2 của vòng 4, thêm hai phần:
- **V-comp:** v5_2 trùng `tolerant_ngA3` trên mọi run không rút gọn, và trùng hs2 trên mọi run không có gate mở.
- **Luật "giữ riêng một thành phần":** đòi thêm run riêng của thành phần đó đã RETAINED.

P1, P2 và no-harm (a), (b) giữ như ở A và B. Có thêm (c) chỉ để mô tả: latent1 và noise0.1 × T{80, 150} × {missing, reversed}-0.2.

**Verdict: KEEP COMPONENT A ONLY.**
- V0, V1, V-comp, P1, (a), (b) đạt.
- P2: P2a 12/12, P2b 12/12, **P2c 2/6** (T25 missing 0.630; T25 reversed 0.889 với 9 cluster). Với f_red của B cũng 2/6.
- (c) chỉ mô tả: tỉ số 0.988–1.007, p Holm 8 nhỏ nhất 0.70.

**Phần đứng vững sau verifier.**
- **Phép ghép đúng.** Verifier chạy lại 51 run độc lập:
  - không rút gọn thì trùng ngA3 38/38;
  - không gate thì trùng hs2 19/19;
  - không có cả hai thì trùng v5_1 15/15;
  - tên được trả lại 51/51.

  Test mạnh nhất là test ép gate của A đóng trên P2 missing/reversed (T19/25/30). Khi đó v5_2 trùng hs2 từng bit ở 60/60 run, gồm 43 run rút gọn và 14 run chỉ rút gọn ở fit evidence.
- **Không cha cùng kỳ nào bị bỏ:** `hs_contemp_dropped` = 0 trên cả 3720 dòng.
- **Số tái lập:**
  - P1 −0.008955, trùng A tuyệt đối;
  - P2c T19 missing 290.38 / 56.81 = 5.111; T25 missing 0.630 (17 cluster); T25 reversed 0.889 (9 cluster);
  - run v5_1-ok 3447, bị đổi 2206 (89 do rút gọn, 2117 do gate).
- **Holm và luật ≥ 8 cluster** được cài đúng như đã đăng ký.
- **Runtime so với v5_1:** +50% ng_mix, +26% G, +59% P2, +33% latent1/noise0.1. Tổng thời gian khoảng 24 phút.

**Phần bị verifier bác.**
- **Danh sách khác biệt f_red giữa v5_2 và B thiếu khóa 25|none** (2.2 so với 2.3). Không ảnh hưởng, vì không cell đánh giá nào dùng khóa này.
- **"V-comp trùng hs2 244/244 trên P2" nói quá mức kiểm tra:** 240/244 run đó là cell extra, nơi code của A không chạy. Chỉ có 4 run reversed và không có run missing nào. Phép ghép thực sự đúng, nhưng bằng chứng đến từ check_compose (48/48) và test ép gate đóng của verifier (60/60), không đến từ con số 244.
- **"Ba cell T19 vẫn tệ hơn `plugin_hs_cal`" sai câu chữ.** Ở T19 missing chỉ mean tệ hơn; median nghiêng về v5_2 (30.17 so với 40.38), và bỏ 3 run lớn nhất thì mean còn 39.81 < 56.81. Không có kiểm định "tệ hơn" nào được chạy. Câu đúng: **"không chứng minh được non-inferiority (biên 1.10)"**. T19 extra (1.0999) nằm sát biên.

**Ghi chú của lead.**
- (i) P1, (a) và (b) của v5_2 chỉ chép lại số của A: cùng dữ liệu, cùng code, và ng_mix lẫn G không có run rút gọn nào. Run ghép **không thêm bằng chứng độc lập nào cho A**.
- (ii) Ô T25 reversed được tính "đạt" P2c có p bootstrap là 0.0000 với 9 cluster và 25 run. Đây đúng là loại p suy biến khi số cluster nhỏ mà vòng 4 đã cảnh báo. Ngưỡng ≥ 8 cluster chỉ vừa đủ chặn trường hợp này. Dù sao verdict cũng không phụ thuộc vào ô này: 2/6 hay 1/6 đều trượt.
- (iii) Hai thành phần giao nhau nhiều hơn vòng 4 dự đoán. Mục 3.2 vòng 4 cho rằng vùng hoạt động của chúng "gần như không giao nhau" vì "ở T ≤ 30 gate gần như luôn đóng". Ở mức run thì điều đó sai: trên P2 (Gaussian, T ≤ 35), 476/720 run có gate mở ở đâu đó, 269 run có cả hai thành phần cùng hoạt động, và T19 missing là 60/60.
- (iv) Mô tả post hoc, không có CI: trên P2, tỉ số mean IS v5_2/hs2 là 0.957–0.967 ở ba cell reversed và 0.995–1.008 ở cell missing. Tức là dưới **Gaussian** shock, ở T nhỏ, gate của A vẫn làm IS đổi khoảng 3–4% ở cell reversed. Lead không có giải thích được kiểm chứng cho điều này và không đưa nó vào paper.

---

## 2. Verdict cuối

| Đối tượng | Verdict | Cơ sở |
|---|---|---|
| `tolerant_v5_2` (A + B) | **Không giữ** | P2c 2/6 < 4 (rule ghi trước, hash 15:37:41Z) |
| Thành phần A, `tolerant_ngA3` | **Giữ, exploratory** | Run riêng RETAINED; trong run ghép, V1, V-comp, P1, (a), (b) đạt |
| Thành phần B, `tolerant_v5_1_hs2` | **Không giữ (REJECTED)** | P2c 1/6 trong run riêng; nhánh "giữ riêng B" không thể xảy ra |
| `tolerant_v5_1` | **Vẫn là module of record** | Đã xác nhận trên P4-H2 confirmatory; vòng 5 không có gì thay thế nó |

**"Giữ A" nghĩa là gì.** A được ghi nhận là một biến thể exploratory đạt rule vòng 5, chứ không phải module mới. Lead xếp A là **extension tùy chọn cho trường hợp có bằng chứng non-Gaussian rõ**, không dùng mặc định, vì bốn lý do:
1. Lợi ích nhỏ (khoảng 1% IS), chỉ đo được dưới shock tổng hợp do nhóm tự chọn, và dồn ở T150.
2. Có một cell tệ hơn với CI không chứa 0 (T40 reversed-0.5 +0.130), đúng nơi AUROC của evidence thấp nhất (0.63).
3. Dưới Gaussian nó đổi 2117/3447 run v5_1-ok mà không lợi gì (tỉ số 0.993–1.020).
4. Trên panel thật 14 × 19 (m = 17), vòng 4 không thấy bằng chứng non-Gaussian, và JB gần như không có power ở cỡ mẫu đó.

**Có thể quy công cho bản sửa luật dấu tới đâu.** Chỉ ở phần evidence: V0 và AUROC. Về IS, kết quả tương thích với "v2 đã đủ": v3 − v2 có CI chứa 0.

---

## 3. Paper có thể nói gì

**Quy ước.** Mọi câu dưới đây là **exploratory, D-07 development, seed_base 70261102, cùng 20 topology đã dùng ở các vòng trước**. Không câu nào là held-out hay xác nhận. Số được lấy từ phần "đứng vững" ở mục 1 và từ `results/ext_r5*`.

**Câu R5-1 (độ bền của v5_1 dưới non-Gaussian shock, tái lập trên seed mới).**
> Với width factor tune trên dữ liệu Gaussian và giữ nguyên, `tolerant_v5_1` đạt coverage 0.937–0.970 ở cả 21 cell dưới non-Gaussian shock tổng hợp `ng_mix` (exploratory, D-07 development, seed mới trên cùng 20 topology). Kết quả này tái lập khoảng 0.91–0.97 đã thấy ở vòng 4.

Nguồn: cột coverage của v5_1 trong `results/ext_r5v52_analysis/ruling.md`, P1 (0.937–0.970) và no-harm (b) (0.938–0.964).

**Câu R5-2 (NG-A v3, nếu paper có mục extension; nếu không thì bỏ).**
> Một biến thể định hướng cạnh theo non-Gaussianity (`tolerant_ngA3`) so sánh log-likelihood xấp xỉ của hai chiều theo Hyvärinen và Smith (2013). Họ log-density được chọn theo dấu excess kurtosis của từng biến, có gate Jarque–Bera, và biến thể thừa kế nguyên width factor của `tolerant_v5_1`. Dưới `ng_mix`, nó giảm interval score trung bình 0.9% (95% CI 0.35%–1.42%) trên 8 cell chính. Lợi ích dồn ở T150: chỉ 1/8 cell có ý nghĩa sau Holm (T150 reversed-0.2: −0.052 [−0.085, −0.020]), còn ở T80 khác biệt gần 0. Ở T40 reversed-0.5, biến thể tệ hơn (+0.130 [+0.048, +0.223], tỉ số 1.03). Dưới Gaussian shock, tỉ số IS là 0.993–1.020 trên 21 cell. Endpoint gộp được chọn sau khi thấy phiên bản trước, và lợi ích IS không tách được khỏi phiên bản đó (chênh −0.21% [−0.48%, +0.05%]). Vì vậy kết quả này chỉ là exploratory.

**Câu R5-3 (evidence về chiều, unit test).**
> Trong unit test LiNGAM hai biến, trên hỗn hợp law của `ng_mix` với b = 0.6, tỉ lệ sai chiều khi gate mở của evidence mới là 0.114, 0.058 và 0.018 ở m = 78, 148 và 400. Phiên bản dùng dấu kurtosis trung bình của cặp giảm chậm và vẫn ở 0.150 khi m = 400. Trong bank, AUROC xếp cạnh bị đảo ở T150 tăng từ 0.773 lên 0.858.

**Câu R5-4 (panel ngắn, lag_max 2; thay câu tương ứng của vòng 4 về `hubscreen`).**
> Ở lag_max 2 với T ≤ 30, `tolerant_v5_1` thường không fit được phương trình của node hub (T19 missing: hoàn tất 0/60). Một chế độ dự phòng rút gọn phương trình bằng screening, không bao giờ bỏ cha cùng kỳ khai báo, hoàn tất 60/60 ở cả 12 cell với ITT coverage 0.943–0.968. Nhưng trên các run được cứu, chế độ này chỉ chứng minh được non-inferiority (biên tỉ số 1.10) so với `plugin_hs_cal` ở 1/6 cell T ≤ 25. Đuôi IS rất nặng: ở T19 missing, mean là 288.0 nhưng median chỉ 30.4, và IS lớn nhất là 14361.7. Ở m = 17, các fit dạng rút gọn đều explosive, kể cả ở run có IS điển hình. Chúng tôi không đưa chế độ dự phòng vào method, và khuyến nghị lag_max 1 cho panel ngắn.

Câu cuối là gợi ý cho người viết paper. Nó dựa trên quan sát của vòng 4 (ở lag_max 1, v5_1 chạy được trên panel thật) cộng với kết quả này; người dùng và thầy quyết định có giữ hay không.

**Câu R5-5 (lựa chọn thiết kế).**
> Ghép hai thành phần trên thành một phiên bản `tolerant_v5_2` không đạt quy tắc ghi trước: nó chỉ đạt non-inferiority so với `plugin_hs_cal` ở 2/6 cell, trong khi quy tắc cần 4. Vì vậy `tolerant_v5_1` vẫn là method chính.

**Không được nói** (đã bị bác hoặc không có bằng chứng):
- "Sửa luật dấu kurtosis làm IS tốt hơn": v3 − v2 có CI chứa 0.
- "NG-A chỉ thay đổi kết quả khi shock non-Gaussian" hay "trùng v5_1 dưới Gaussian": dưới Gaussian, gate mở ở ít nhất một chỗ trong 57% run G và đổi 2117 run v5_1-ok.
- "Đuôi IS do fit gần explosive": fit explosive cả ở run điển hình.
- "Giữ cha cùng kỳ không ảnh hưởng IS": so sánh v2 với v1 bị confound bởi f_red.
- "Ở T19 chế độ dự phòng tệ hơn `plugin_hs_cal`": câu đúng là không chứng minh được non-inferiority.
- "P2c gần đạt (2/6)": ô thêm vào chỉ có 9 cluster và 25 run, với p bootstrap suy biến.
- Mọi câu kiểu "held-out", "xác nhận" hay finite-sample guarantee cho kết quả vòng 5.

---

## 4. Có nên xin người dùng duyệt một held-out run trên P4-H2 development?

**Khuyến nghị của lead: không xin bây giờ.**

Về hình thức, điều kiện mà vòng 4 đặt ra (mục 4.3) đã đạt, vì một thành phần đạt rule vòng 5. Lead vẫn không khuyến nghị, vì những lý do sau.
1. **Câu hỏi quá nhỏ so với giá của split.** Lượt chạy chỉ trả lời được một câu: A có giảm IS khoảng 1% dưới shock tổng hợp `ng_mix`, trên 20 topology mới, hay không. P4-H2 development (20 topology theo manifest của P4-H2) là split chưa mở cuối cùng của generator hiện tại. Sau nó, mọi kiểm tra độc lập đều cần sinh bank mới P4-H3, việc cũng phải được người dùng duyệt.
2. **Power thấp và có winner's curse.** Endpoint gộp được chọn sau khi thấy v2, nên −0.90% nhiều khả năng là ước lượng lệch lên. Nửa độ rộng CI trên 20 cluster khoảng 0.5%. Nếu hiệu ứng thật chỉ khoảng 0.4–0.5%, xác suất đạt trên topology mới chỉ khoảng một nửa (ước lượng thô của lead, chưa mô phỏng). Kết quả "không đạt" khi đó gần như không mang thông tin.
3. **Không đổi được claim chính của paper.** Ba claim chính đã CONFIRMED trên P4-H2 confirmatory. A không phải module of record. Dù held-out đạt thì A vẫn chỉ là "held-out exploratory" và dưới shock tổng hợp, chứ không phải xác nhận.
4. **Giá trị thực tế thấp trên panel thật.** Ở m = 17, JB gần như không có power, nên gate của A hiếm khi mở vì lý do đúng.

**Khi nào nên xin.** Chỉ nên xin khi có ít nhất một trong hai điều sau:
- (i) Thầy hoặc người dùng quyết định paper cần mục extension non-Gaussian với một số held-out.
- (ii) Có thêm một candidate với hiệu ứng lớn hơn, để **một** lượt chạy duy nhất trên P4-H2 development kiểm nhiều arm, với rule và Holm chung được ghi trước.

**Nếu người dùng vẫn muốn chạy ngay: spec đề xuất.** Spec này chưa được đóng băng. Lead của bước đó phải viết `spec_files.json` kèm hash rồi mới được chạy.
- **Method:** `tolerant_v5_1` (mốc) và `tolerant_ngA3`. Không chạy B và v5_2, vì cả hai bị loại.
- **File cần đóng băng (sha256):**
  - code: `src/paper4/ext_r5ngorient3.py`, `src/paper4/ext_r4ngorient.py`, `src/paper4/ext_v51.py`, `src/paper4/ext_narrow.py`, `src/paper4/methods.py`, `src/paper4/estimator.py`, `experiments/run_experiment.py`;
  - driver và generator: driver `experiments/ext/r4ngorient/` cùng `laws.py` (generator `ng_mix` nằm ở đây);
  - factor và analyzer: `experiments/ext/r5ngorient3/frozen_r5ngorient3.json`, `experiments/ext/r5ngorient3/analyze.py`;
  - config: hai config mới, sao từ `ext_r5ngorient3_ngmix.json` và `ext_r5ngorient3_gauss.json`, chỉ đổi bank sang P4-H2 development và đổi seed_base.
- **Dữ liệu:** P4-H2 development, 20 topology × 3 replicate. seed_base phải chốt trong spec và qua guard "chưa manifest nào dùng". Chạy qua lead guard như lượt P4-H2 confirmatory, với hash trước và sau.
- **Rule:** giữ nguyên rule của r5ngorient3 (doc mục 4), trừ V0 vì V0 đã đạt:
  - V1;
  - P1: cận trên 95% một phía của endpoint gộp < 0, cộng hai guard;
  - no-harm (a) trên 21 cell Gaussian, (b) trên 13 cell ng_mix;
  - ≥ 8 cluster.

  Thêm một dòng báo kèm, không quyết định: cell T40 reversed-0.5 ng_mix.
- **Runtime:** trên D-07, item A chạy ng_mix 828.5 s và Gaussian 747.9 s với `--workers 3` (có kèm arm v2). P4-H2 development có cùng 20 topology × 3 replicate, nên ước lượng khoảng 25–30 phút, cộng vài phút guard và analyzer.
- **Ý nghĩa từng kết quả:**
  - **P1 đạt, (a) và (b) đạt:** paper được nói "trên 20 topology held-out chưa từng dùng, `tolerant_ngA3` giảm IS dưới `ng_mix`" (held-out exploratory). A có thể vào mục extension. v5_1 vẫn là module chính.
  - **P1 trượt, (a) và (b) đạt:** lợi ích của A không tái lập ngoài D-07. Paper chỉ giữ câu R5-3 (evidence về chiều) và câu "không gây hại dưới Gaussian", bỏ R5-2.
  - **(a) hoặc (b) trượt:** bỏ A khỏi paper, chỉ báo như kết quả âm.
  - **Trong mọi trường hợp:** P4-H2 development coi như đã dùng, và mọi kiểm tra độc lập sau đó cần P4-H3.

---

## 5. Bài học quy trình của vòng 5

1. **Luật factor frozen có tác dụng.** Ở A, V1 trùng v5_1 từng bit và factor bằng nhau 2520/2520, nên khác biệt IS của A quy được cho method chứ không cho factor. Nhưng **f_red vẫn là nguồn confound**: so sánh hs2 với v1 bị factor làm nhiễu (mục 1.2). Từ nay, so sánh hai phiên bản của một chế độ dự phòng phải dùng chung f_red, hoặc báo phân rã method/factor.
2. **Kiểm tra identity "khi gate đóng" dựa vào run tự nhiên thì yếu.** Gate ở mức pair hiếm khi mở, nhưng ở mức run thì gần như luôn mở ở đâu đó trong một draw, nên chỉ còn 6–12 run để kiểm. Nên dùng test ép gate đóng bằng stub, như verifier v52 đã làm (60/60), và ghi test đó vào rule.
3. **V-comp phải được đo ở nơi phép ghép thực sự chạy.** Con số 244/244 hầu hết là cell extra. Rule sau nên đòi V-comp trên các cell missing/reversed có rút gọn.
4. **Run ghép tái sử dụng dữ liệu của thành phần thì không thêm bằng chứng.** P1 của v5_2 trùng A tuyệt đối. Đây không phải lỗi, nhưng không được đếm hai lần.
5. **Seed guard phải được ghi một lần bởi lead, trước khi các item chạy song song.** Guard mà mỗi item tự viết sẽ cũ ngay khi item khác bắt đầu ghi manifest (mục 1.1).
6. **≥ 8 cluster là mức tối thiểu, chưa đủ an toàn.** Ô T25 reversed (9 cluster, p 0.0000) cho thấy p bootstrap vẫn có thể suy biến ngay trên ngưỡng. Nên cân nhắc ≥ 10 cluster, hoặc báo kèm kiểm định hoán vị theo cluster.
7. **Verdict đứng vững, diễn giải thì không.** Cả 3 item có câu phụ bị bác. Các câu giải thích cơ chế (explosive, cha cùng kỳ, "không giảm") đều chưa được đo trong vòng này. Nguyên tắc của vòng 4 vẫn giữ: câu đưa vào paper chỉ lấy từ phần đứng vững.

---

## 6. Limitations cập nhật

Danh sách ở mục 5 của `docs/ext/synthesis_round4.md` vẫn đúng. Vòng 5 đổi các mục 3, 6, 8 và thêm mục 12, 13.

3. **Hướng của cạnh repair và cạnh reversal** *(đổi)*. Dưới Gaussian, hướng vẫn ngẫu nhiên. Dưới non-Gaussian shock tổng hợp, NG-A v3 cho evidence về chiều tốt hơn rõ (AUROC 0.86 ở T150) và thu hẹp khoảng cách coverage của cặp reversal ở 1/4 cell (T150 reversed-0.2, +0.040). Nhưng lợi ích IS chỉ khoảng 0.9%, không tách được khỏi v2, và ở T40, nơi evidence yếu (AUROC 0.63), biến thể này tệ hơn. Tất cả chỉ là exploratory.
6. **T nhỏ và hub** *(đổi)*. v5_1 fail ở lag_max 2, T ≤ 30. Chế độ dự phòng v2 không còn bỏ cha cùng kỳ, chạy được (60/60) và giữ ITT coverage 0.943–0.968. Nhưng đuôi IS rất nặng (T19 missing: mean 288.0, median 30.4, max 14361.7), các fit ở m = 17 explosive kể cả ở run điển hình, và trên run được cứu nó không chứng minh được non-inferiority so với `plugin_hs_cal` ở 5/6 cell. Lag_max 2 với T ≤ 25 nên được xem là ngoài phạm vi của method.
8. **Phân phối shock** *(đổi)*. v5_1 với factor Gaussian giữ coverage 0.937–0.970 dưới `ng_mix` trên seed mới (vòng 4: 0.91–0.97 dưới `ng_mix` và t10). Tất cả trên cùng 20 topology D-07. Vẫn chưa có kịch bản heteroskedastic hay phi tuyến.
12. **Gate của NG-A không phải công tắc sạch** *(mới)*. Gate mở dưới Gaussian ở mức pair là 0.08 / 0.12 / 0.16 ở T40 / 80 / 150 (T150 vượt mức danh nghĩa 0.10). Ở mức run, gate mở ở ít nhất một draw trong 57% run Gaussian. Vì vậy mọi biến thể dùng NG-A đều khác v5_1 ở phần lớn run, kể cả khi dữ liệu Gaussian.
13. **D-07 tiếp tục bị dùng lại** *(mới, nối mục 10)*. Vòng 5 thêm một seed mới nhưng vẫn trên cùng 20 topology. Trong lúc chạy thử analyzer, item A đã thấy endpoint gộp của v2 trên dữ liệu vòng 4 trước khi ghi rule. Lead của v52 đã đọc kết quả của A và B trước khi ghi rule. Cả hai đều được công bố.

---

## 7. Bước tiếp

**Việc cần người dùng quyết định** (theo thứ tự lead khuyến nghị):
1. **Commit toàn bộ vào git.** Vòng 5 thêm nhiều file mới (`*r5*`, `*verify5*`) vào hơn 20 giờ công việc chưa commit từ trước. Lead không commit, theo đúng ràng buộc.
2. **Gặp thầy** với `docs/TONG_HOP_PAPER4.md` cùng tóm tắt vòng 4 và vòng 5. Câu cho paper lấy ở mục 3 trên. Việc bổ sung vào `TONG_HOP_PAPER4.md` cần người dùng cho phép, vì lead vòng này chỉ được sửa file này.
3. **Không xin held-out P4-H2 development bây giờ** (mục 4).

**Nếu tiếp tục nghiên cứu** (mọi thứ phải chạy trên dữ liệu mới, không tune trên D-07 thêm):
- **Gate của NG-A theo T.** Kết quả gợi ý tắt NG-A ở T40, nơi evidence yếu và có harm. Nhưng giả thuyết này sinh ra từ chính dữ liệu D-07 vòng 5, nên chỉ được kiểm trên bank mới, với rule ghi trước.
- **Panel ngắn, lag_max 2.** Nếu muốn cứu vùng này, hướng có cơ sở là xử lý tính explosive: shrinkage về vùng stationary, hoặc ridge trên phương trình hub, đo spectral radius trong rule. Phương án đơn giản hơn và có lẽ đủ cho paper là tuyên bố vùng này nằm ngoài phạm vi.
- **Bias-aware honest CI (Armstrong–Kolesár)** và **conformal hai tầng theo topology** vẫn là hai hướng còn để ngỏ cho chỉ trích "width factor ad hoc" (vòng 4 mục 4.4).
- **Bank mới P4-H3**, nếu cần thêm claim xác nhận. Việc sinh bank cũng phải được người dùng duyệt.

**Bẫy trong code đã báo** (không sửa, theo ràng buộc):
- Analyzer của v52 không kiểm no-harm (b) ở nhánh KEEP-B, dù rule 4.8 đòi. Nhánh này không thể xảy ra trong vòng 5.
- A fit lại base terms trong mỗi draw chỉ để tính evidence. Nếu fit đó underdetermined thì draw fail, trong khi v5_1 không có fit này. Hiện chưa có fit-fail nào, nhưng đây là khác biệt cấu trúc.
- Phép ghép của v52 gán lại tên ở mức module: an toàn với process pool, nhưng không an toàn khi nhiều thread cùng gọi `ext_r5ngorient3`. Đây là cùng loại rủi ro đã báo ở vòng 4 cho `mondrian`, `levboot` và `prepivot`.
- File frozen `frozen_v4_v51.json` không có T < 40. Mọi chế độ dự phòng ở T19–35 phải lấy factor v5_1 từ calibration vòng 4 (seed 20261102, 3 replicate). Đây là factor chưa được "frozen" chính thức.
- Các bẫy cũ ở vòng 4 mục 5.11 vẫn còn, kể cả bug E1.

---

## Phụ lục: file của vòng 5

**Doc từng item:** `docs/ext/r5ngorient3.md`, `docs/ext/r5hubscreen2.md`, `docs/ext/r5v52.md`.

**Module:** `src/paper4/ext_r5ngorient3.py`, `src/paper4/ext_r5hubscreen2.py`, `src/paper4/ext_r5v52.py`.

**Driver, analyzer và test:** `experiments/ext/r5ngorient3/`, `experiments/ext/r5hubscreen2/`, `experiments/ext/r5v52/`. Config là `experiments/configs/ext_r5*_*.json`.

**Prereg (hash):** `results/ext_r5ngorient3_prereg/hashes.txt`, `results/ext_r5hubscreen2_prereg/hashes.txt`, `results/ext_r5v52_prereg/hashes.txt`. Riêng v52 có thêm `seed_guard.txt` và `check_after_run.txt`.

**Ruling:**
- `results/ext_r5ngorient3_analysis/ruling.md`;
- `results/ext_r5hubscreen2_ruling/ruling.md` (post hoc ở `posthoc.md`);
- `results/ext_r5v52_analysis/ruling.md` (post hoc ở `posthoc.json`).

**V0 và calibration:** V0 ở `results/ext_r5ngorient3_v0/v0.md`. Calibration ở `results/ext_r5hubscreen2_cal/calibration.json` và `results/ext_r5v52_cal/calibration.json`.

**Verifier:**
- Script: `experiments/ext/verify5_ngorient3/`, `experiments/ext/verify5_hubscreen2/`, `experiments/ext/verify5_v52/`.
- Kết quả: `results/ext_verify5_ngorient3/` (v0_indep.json, recompute.json), `results/ext_verify5_hubscreen2/` (check_lag0.json, recompute.json, tail_probe.json, doc_hash_check.txt), `results/ext_verify5_v52/` (identity_tally.json, closed_gate_compose.json, recompute.json).

**Frozen spec:** không có, vì verdict không phải RETAINED-combined. Không có run held-out nào.
