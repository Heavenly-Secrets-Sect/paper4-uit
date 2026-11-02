# Tổng hợp vòng 2: bảy work item, kiểm chứng độc lập, và quyết định cho run niêm phong P4-H2

**Trạng thái.** Đây là bản tổng hợp của team lead sau vòng 2. Mọi kết quả ở đây đều **exploratory, chỉ trên D-07 development** (seed_base 20261102). Calibration và design probe dùng D-07H development. Không hướng nào chạy P4-H2, P4-H1 hay confirmatory split: verifier của từng hướng đều kiểm tra điều này qua manifest và transcript. Mỗi work item có một verifier độc lập. Verifier tính lại số từ `runs.jsonl` bằng code riêng, đối chiếu thời điểm ghi rule với thời điểm chạy qua transcript, và chạy implementation trên ví dụ nhỏ biết truth. Mọi con số dưới đây lấy từ file kết quả của từng hướng (`results/ext_<ID>_*`) hoặc của verifier (`results/ext_verify2_<ID>/`). Team lead không chạy thêm thí nghiệm nào.

**Ngoại lệ cần biết: v4c.** Lúc verifier kiểm tra, `results/ext_v4c_eval` chỉ có `calibration.json`. Sau đó phiên chính (không phải agent v4c) đã chạy lại đúng config `experiments/configs/ext_v4c_eval.json` với **`--workers 6`**, tức là vi phạm hard rule 5. Phiên chính đã công bố việc này trong docs/ext/v4c.md. Run mất 464.6 s, có 7560 dòng, và verdict được tính bằng `analyze.py` viết từ trước. Team lead đã kiểm tra bằng `cmp`: `calibration.json` mới giống từng byte bản của lần chạy bị cắt (`experiments/ext/v4c/calibration_interrupted_attempt.json`). **Kết quả v4c chưa được verifier độc lập kiểm tra** (xem R3-7).

**Quyết định tóm tắt.**
1. Claim chính "module thắng baseline mạnh ở cell thiếu cạnh khi T ≥ 80" **không đứng vững ở dạng tổng quát** (mục 2.1).
2. Module of record vẫn là `tolerant_v4` (frozen) cho tới khi có kết quả P4-H2. Việc chuyển sang `tolerant_v5_1` được cam kết trước, kèm điều kiện (mục 3.1).
3. **Chưa nên chạy P4-H2 ngay.** P4-H2 chỉ dùng được một lần, mà claim chính về baseline hiện chưa có frozen spec nào chấp nhận được. Nên chờ R3-1, cùng các sửa spec ở mục 3.3 và việc người dùng duyệt R2-0.

---

## 0. Tình trạng các việc vòng 2

| Việc | Hướng | Tình trạng | Verdict theo rule ghi trước | Verifier |
|---|---|---|---|---|
| R2-0 (bank xác nhận) | lead + người dùng | P4-H2 đã có, đang niêm phong (`src/paper4/topology.py:20`); **chưa có duyệt chạy** | — | — |
| R2-1 baseline fidelity | baselines2 | xong | R-B2 **FAIL** (4/8, Holm 4/8); R-B2s **HOLDS** (8/8, Holm 8/8) | partly |
| R2-2 v5.1 | v51 | xong | `tolerant_v5_1` **GIỮ** (thô và Holm); latent1 9/9 | partly |
| R2-3 auto3/auto5 | auto5 | xong | auto3 latent1 **đạt** 4/4; fair-comparison claim **FAIL** (pselect 6/8); `tolerant_auto5` **LOẠI** | partly |
| R2-4 two-sided calibration | v4c | xong (phiên chính chạy lại, workers 6) | `tolerant_v4c` **GIỮ** (C1 14/14, TOST Holm 5/14; C2 2/2, Holm 2/2) | partly (khi đó chưa có kết quả); **chưa ai kiểm chứng kết quả** |
| R2-5 eiv v2 | eiv2 | xong | `tolerant_eiv2` **LOẠI** (11/12; Holm: 7/12 có ý nghĩa ≥ 0.90, 0/12 có ý nghĩa < 0.90) | holds |
| R2-6 reversal | revlag | xong | (a) "M" 4/4 so với oracle_cal (Holm 4/4); (b) `tolerant_v4L` **GIỮ** (L1 4/4, Holm 4/4) | partly |
| R2-7 RQ4.4 | revlag | phần lớn | flag frozen **ĐẠT** F1–F4 5/5 (Holm 5/5); AUROC cho auto3/v5 **chưa làm** | partly |
| R2-8 TLP | tlp2 | xong | Claim A theo cách chấm ghi trước; A' theo sensitivity | partly |
| R2-9 bảng bản thảo | — | **chưa làm** | — | — |
| R2-10 sửa doc vòng 1 | các owner | đã append một lần vào narrow, eiv, gate, metrics, redteam, tlp | — | xác nhận ở eiv, gate, metrics |

---

## 1. Từng work item: phần đứng vững sau kiểm chứng

### 1.1 `baselines2` (R2-1): `pselect_union_v2`, `bvar_minnesota_v2` và bản `_cal`

**Verdict theo rule.** R-B2 **FAIL**: 4/8 so sánh đạt theo CI, và vẫn 4/8 khi dùng Holm qua 8. R-B2s (BVAR v2) **HOLDS**: 8/8, Holm 8/8. Verifier tái lập mọi số bằng code riêng. Rule được ghi trước khi chạy D-07 và không đổi qua lần chạy lại sau gián đoạn: mục 3 giống từng byte bản của attempt 1. Dòng v4 khớp 1260/1260 với `a2b_pselect`. Không có leakage.

**Đứng vững:**
- T80 missing-0.2, v4 − pselect_union_v2: −1.14 [−1.65, −0.63]. Với `_cal`: −1.22 [−1.62, −0.82].
- T80 missing-0.5: −1.19 [−1.64, −0.78] và −1.19 [−1.50, −0.88].
- T150 missing-0.2: −0.10 [−0.30, +0.08]. T150 missing-0.5: −0.07 [−0.25, +0.08]. Đây là **hòa, không phải thua**.
- Coverage của v4 ở 4 cell rule là 0.957–0.968.
- BVAR v2 (cả `_cal`) thua v4 ở 4/4 cell rule, với hiệu từ −1.21 đến −5.49.
- Trên 84 so sánh, v4 so với pselect_v2 và `_cal`: W19/T2/L0 cho mỗi bản, Holm cho cùng số đếm.
- Pselect_v2 lấp được lỗ hổng lag-0 của bản round 1: coverage deleted lag-0 đạt 0.96 ở T150. Điều này xác nhận X2: lợi thế lag-0 của v4 so với pselect round 1 chủ yếu là thuộc tính của bản chuyển thể.
- Trên null pair, v4 rộng hơn pselect_v2: IS 2.03–2.08 so với 1.26–1.31 ở T80, và 1.31–1.36 so với 0.91–1.00 ở T150.
- Kiểm tra known-truth của verifier: pselect_union_v2 có non-null coverage 0.90/0.98 (T80/T150). bvar_v2 cover deleted pair chỉ 0.24/0.30, đúng như prior của nó dự đoán.

**Không đứng vững hoặc phải sửa lời:**
- **Comparator bị thiếu budget.** R2-1 yêu cầu ≥ 199 draw mỗi graph. Module chỉ dùng cap = 4 graph (round 1 dùng 16) và min_draws = 40 cho mỗi orientation member, tức khoảng 80 draw mỗi graph. Doc không ghi đây là một lệch khỏi R2-1.
  - Ngay trong một cell rule (T80 missing-0.2), pselect_v2 tệ hơn pselect_union round 1: v1 − v2 = −0.67 [−1.14, −0.20].
  - Verifier chạy probe trên D-07H (20 topology × 1 replicate, T80) với bản đúng budget (cap 16, khoảng 200 draw mỗi graph). Bản này có coverage 0.971/0.957 và IS 3.39/3.62, so với 4.69/4.98 của pselect_union_v2. v4 trừ bản đúng budget cho −0.10 [−0.36, +0.17] (**hòa**) ở missing-0.2 và −0.32 [−0.68, −0.01] ở missing-0.5.
  - Kết luận: phần lớn biên ở T80 của v4 so với pselect_union_v2 đến từ budget bị cắt. Probe này không được pre-register và chạy trên D-07H, nên chỉ là cảnh báo, không phải kết quả.
- **Câu "v4 thắng baseline mạnh nhất ở T80" không được ủng hộ.** Envelope post hoc của chính tác giả cho thấy:
  - Ở T80 missing-0.2, baseline mạnh nhất là `targeted_lp`, với v4 − X = −0.20 [−0.39, −0.02] (p = 0.032; −0.21 với `_cal`). Không bản nào qua Holm trên 94 so sánh.
  - Ở T80 missing-0.5, baseline mạnh nhất là `fullvar_cal`: −0.45 [−0.59, −0.31], qua Holm.
- **Khoảng cách coverage deleted lag-0 so với lag-1/2 của v4.** Gap nằm trong 0.03–0.05, nhưng CI chỉ loại 0 ở 2/4 cell. Ở T150 missing-0.2 gap gần bằng 0 (−0.007). Số coverage lag-0 của bvar_v2 đã calibrate phải là 0.557–0.78, không phải 0.57–0.78.
- **Spec P4-H2 (C1) không đủ thông tin.** C1 chỉ so v4 với một comparator thiếu budget, nên gần như chắc chắn PASS. Một lần PASS không ủng hộ được câu "thắng baseline mạnh nhất" (mục 3.2).
- Correction 6 trong redteam.md ("F5 đã xử lý") phải sửa: F5 mới xử lý được một phần (R3-6).

Nguồn: results/ext_baselines2_eval/{rule_check.txt, analysis.md, envelope.md, numbers.json}. Verifier: results/ext_verify2_baselines2/{recompute.json, known_truth.json, fidelity2_summary.json, claim_checks.json}.

### 1.2 `v51` (R2-2): `tolerant_v5_1`, v5 có de-duplicate term

**Verdict theo rule.** `tolerant_v5_1` **GIỮ**: C1 2/2, C2 12/12, C3 7/7, C4a 2/2, C4b 2/2, và bản Holm cũng GIỮ. Latent1 đạt 9/9. Verifier tái lập verdict với ba seed bootstrap (0, 11, 12), xác nhận timeline (rule (b), (c) và cam kết về tau được append lúc 02:25:01Z, trước probe 2 và trước mọi run D-07), và kiểm tra fix de-dup trên known truth: hệ số thật 0.6 cho ra 0.298 khi còn term trùng, 0.595 khi đã de-dup.

**Đứng vững:**
- (a) Ghép cặp miễn phí qua dòng v4 trùng nhau (1260/1260). v5 round 1 thắng pselect_cal 18/18 (Holm 18/18), thắng fullvar_cal 18/18 (Holm 18/18), thắng targeted_lp_cal 13/18 (Holm 11/18). Lưu ý: đây là các dòng v5 round 1 còn bug.
- T40 missing (C1): coverage 0.922/0.939, IS 4.84/5.09 so với 7.77/7.53 của v4. Hiệu v5_1 − v4 = −2.93 [−3.44, −2.34] và −2.44 [−2.83, −2.03].
- C4a (so với pselect_cal ở T40 missing): −2.90 và −2.37. C4b: hòa targeted_lp_cal, +0.08 [−0.29, +0.49] và +0.07 [−0.26, +0.41].
- C2 (T80/150): IS ratio 0.855–1.026. Cell sát nhất là T80 reversed-0.5: coverage 0.918, ratio 1.026, hiệu +0.08 [+0.01, +0.14] (p thô 0.012, không qua Holm: 0/12 cell tệ hơn có ý nghĩa).
- Trên 18 damaged cell, v5_1 thắng pselect_cal 18 (Holm 18), fullvar_cal 18 (18), targeted_lp_cal 13 (12), và v4 7 (7).
- Bug duplicate term chạm 100% run missing. So với v5 round 1 (còn bug), v5_1 tốt hơn ở T150 missing −0.22/−0.35 và ở T80 missing-0.5 −0.25.
- Latent1: coverage 0.919–0.956 ở 9/9 cell. Latent3: 8/9 (T150 none 0.875, v4 là 0.871 ở cùng cell). IS > 1.05 × v4 ở 0/27 cell.

**Không đứng vững hoặc phải sửa lời:**
- **"Bug bác bỏ X3/X4" là nói quá.** Chỉ phần số của narrow trong X3/X4 (v5_sel +0.25 ở T150; "dữ liệu narrow cho thấy targeted thua ở T150") đến từ module có bug. Bằng chứng của gate trong X4 (T80 missing-0.2: 9.29 so với 5.18) độc lập với bug, vì `ext_gate.py` không import ext_narrow. Kết luận chính của X3 (repair + orientation là biên ở T150) không nói về targeted opening. `v5_sel` chưa được test lại sau khi de-dup.
- **Tau = 6.6083 nằm trên một ranh giới mong manh.** Procedure được áp dụng đúng, nhưng ở T = 100 cận trên CI là −0.0038. Verifier chạy lại với 200 seed bootstrap: cận trên dao động từ −0.0118 đến +0.0047 và ≥ 0 ở 11% seed. Với các seed đó, T* = 80 và tau ≈ 2.94, khi ấy T150 sẽ đi nhánh all-lag. Vì vậy câu "targeted thắng rõ ở mọi T" phải bỏ.
- **"Hybrid" thực chất là v5 đã sửa bug.** Trên grid D-07 và P4-H2 (14 nút, r ≲ 5 < 6.61), nhánh all-lag không bao giờ được dùng.
- Vài số chỉ có trong shell output: sanity check de-dup, timing run của attempt 1 (d(40) = −3.60, d(200) = +0.15), và "1.9–2.5 s mỗi fit". Verifier đã lưu chúng vào results/ext_verify2_v51/timeline.json; owner phải ghi chúng vào results/ext_v51_*.
- "3–17 duplicated term" là khoảng của **trung bình theo cell** (3.1–16.7), không phải khoảng theo từng run.
- Phần cải thiện so với v5 round 1 ở T150 trộn ba thứ: fix bug, factor calibrate khác (2.5 so với 2.3), và seed ext mới.
- Dưới noise0.1, coverage của v5_1 dưới 0.90 ở 5/9 cell, trong khi v4 chỉ ở 1/9. Không cell nào dưới 0.90 có ý nghĩa sau Holm. Biên coverage ở C2 mỏng: 0.918–0.927 ở 3/12 cell.
- Chưa so v5_1 với pselect_union_v2.

Nguồn: results/ext_v51_{pairs,probe,eval,a1}/. Verifier: results/ext_verify2_v51/{recompute.md, known_truth.json, tau_fragility.json, timeline.json}.

### 1.3 `auto5` (R2-3): auto3 dưới latent, so sánh công bằng, và `tolerant_auto5`

**Verdict theo rule.**
- (a) auto3 đạt latent1: 4/4 cell, Holm 4/4.
- (b) Claim "auto3 thắng mọi baseline calibrate theo T ở 8 cell missing/reversed khi T ≥ 80" **FAIL**: plugin, ida_union và bvar đều 8/8, nhưng pselect_union chỉ 6/8. Holm cho cùng số đếm.
- (c) `tolerant_auto5` **LOẠI**: C1 hụt ở T80 reversed-0.5 (0.898). Ablation `auto5_small` cũng hụt ở cùng cell (0.894).

Verifier tái lập cả ba verdict. Rule có trước mỗi run và không đổi. Không có leakage: auto5 cho output giống hệt khi damage = {} và khi damage = {'missing': 99}.

**Đứng vững:**
- Coverage của auto3 dưới latent1: missing-0.2 0.956/0.977, reversed-0.2 0.937/0.970 (T80/T150).
- Latent3: auto3 6/6 cell ≥ 0.90, v4 5/6. Noise0.1: 5/6, hụt ở T80 reversed-0.2 với 0.883.
- Tỉ lệ gate mở trên cell none tăng theo confounding: sạch 0.08/0.05, latent1 0.25/0.47, latent3 0.55/0.82.
- Hai cell hòa với pselect_union (calT): T80 missing-0.2 −0.24 [−0.48, +0.06] và T150 missing-0.2 −0.02 [−0.17, +0.13].
- Trên skeleton đúng, auto3 thua raw ida_union ở mọi T (+0.69/+0.12/+0.14) và thua raw plugin ở T150 (+0.29 [+0.17, +0.42]).
- auto5: C2 có ratio 1.045/1.045/1.146; C3 cell GES đạt; C4 (không tệ hơn pselect_union ở T40 missing) đạt: −0.56 [−1.28, +0.18] và −0.55 [−1.40, +0.53]. Đây là version đầu tiên của nhánh auto không thua pselect_union ở T40 missing.
- auto5 − auto3 ở T40: missing −2.16/−2.89, GES −2.73. Đổi lại, coverage ở T40 missing giảm từ 0.911 xuống 0.873 và từ 0.954 xuống 0.892.

**Không đứng vững hoặc phải sửa lời:**
- "auto5 có IS thấp hơn auto3 ở 23/24 cell, có ý nghĩa ở 13/24": **dưới Holm chỉ còn 10/24**. Một phần lợi ích là do width factor đóng thấp hơn (1.25 so với 1.3 ở T80, 1.2 so với 1.3 ở T150), không phải do targeting.
- Phát hiện phụ "targeted thắng all-lag cả ở T80/T150, trái X4" là **gợi ý, không phải bác bỏ**:
  - small − auto5 chỉ có CI > 0 ở 6/16 cell (Holm 5/16); 10 cell còn lại hòa.
  - Ở T150 so sánh bị lẫn với width factor tune trong mẫu (1.25 so với 1.2, chênh 4.2%).
  - Chỉ T80 missing-0.2 (+0.41) và T150 missing-0.2 (+0.24) rõ ràng lớn hơn phần chênh factor.
- "IS của baseline calT tăng 2.2–3.3 lần" phải sửa thành **1.9–3.3 lần**.
- `_calT` không calibrate theo cùng target với auto3, vì grid bị chặn ở 5.0, nên mô tả "giống runner" là sai. Verdict không đổi dưới `_calT1`.
- Khi gộp một factor theo T, plugin/ida đã calibrate chỉ cover 0.44–0.52 ở missing-0.5. Vì vậy "thắng baseline đã calibrate" ở đó gần như tự động, không phải bằng chứng mạnh.
- Doc chưa nhắc rằng auto3 cũng thua raw plugin và raw ida ở T150 extra-0.2/0.5 (+0.12 đến +0.28).
- Main run mất 23.4 phút, vượt khoảng 20 phút (đã công bố). Probe script được chép vào `experiments/ext/gate_probes/`, nằm ngoài thư mục được phép (đã công bố).

Nguồn: results/ext_auto5_{a1,fair,main,probe,gate_corrections,p4h2_dryrun}/. Verifier: results/ext_verify2_auto5/{recompute.json, known_truth.json, extra_checks.json}.

### 1.4 `v4c` (R2-4): two-sided calibration cho module và baseline

**Verdict theo rule (do phiên chính chạy, chưa được kiểm chứng).** `tolerant_v4c` **GIỮ**.
- C1: 14/14 cell có IS ratio trong [0.97, 1.03], cụ thể 0.981–1.014. TOST sau Holm chỉ đạt 5/14, tức phần lớn cell "không khác" theo point ratio nhưng chưa chứng minh được tương đương.
- C2: T40 missing-0.2 có coverage 0.983 → 0.958, IS 7.77 → 6.98, hiệu −0.79 [−0.99, −0.58]. T40 missing-0.5 có coverage 0.978 → 0.956, IS 7.53 → 6.82, hiệu −0.71 [−0.87, −0.54]. Đạt 2/2, Holm 2/2.
- Factor hiệu dụng của v4c ở T40 missing là 0.85, dưới sàn 1.0 cũ.
- Pairing: plugin và v4 khớp 1260/1260 với a2_baselines.

**Đã được verifier xác nhận trước khi có kết quả:**
- Rule có trước mọi run D-07.
- analyze.py được viết trước khi có output và trung thành với rule.
- Implementation đúng: `calibrate_width(v4c, 2.6)` bằng `calibrate_width(v3, 1.3)` trong sai số 1.8e-15.
- Không có leakage.
- v4c cùng code path với `v5_cal2` của narrow. Vì vậy run D-07 chủ yếu là **replication**: ablation round 1 cho −0.76/−0.55, run này cho −0.79/−0.71.

**Phần B (mô tả, chưa kiểm chứng; results/ext_v4c_eval/describe.md):**
- Đổi sang grid hai phía (so sánh (c), (d)) không đổi kết luận ở cell missing khi T ≥ 80: v4 và v4c đều thắng cả ba baseline `*_c2` ở 4/4 cell.
- Ở T40 missing, v4c thắng pselect_union_c2 ở 2/2 cell, còn v4 chỉ hòa.
- D1 (vòng 1: v4 thắng ida/bvar ở reversed 4/6, extra 3/6) không còn đúng nguyên dạng dưới (b), (c), (d).
- Baseline `*_c2` tốt hơn `*_cal` ngoài cell missing ở 8/45 cell (Holm 4/45) và tệ hơn ở 6/45. Thiên lệch do sàn 1.0 có thật nhưng nhỏ.

**Phải sửa lời (verifier, áp dụng cho doc):**
- Có 4 factor dưới 1.0 ngoài cell missing (pselect và ida ở T150 none/extra), không phải 2.
- "Factor c2 khớp E3" sai ở 6/27 cell không chạm sàn.
- Tỉ số của v5 ở cell không thiếu cạnh là 0.985–1.019, không phải 0.987.
- Doc phải công bố việc đổi interpreter (python3 CLT với numpy 2.0.2 sang miniconda với numpy 2.5.4; verifier kiểm thấy khác biệt chỉ ở mức 1e-10), cả ba lần chạy, và `--workers 6`.
- Stream bootstrap của v4c và v4 khác nhau, nên C1 trộn hiệu ứng factor với nhiễu Monte Carlo.

Nguồn: results/ext_v4c_eval/{ruling.md, describe.md, analysis.json}. Verifier (trước khi có kết quả): results/ext_verify2_v4c/.

### 1.5 `eiv2` (R2-5): cap theo từng phương trình

**Verdict theo rule.** **LOẠI**. Điều kiện 1 đạt 11/12; cell hụt là noise0.3 T80 reversed với 0.897. Điều kiện 2 đạt 6/6 (ratio 1.051–1.118). Verifier: **holds**. Các số tái lập được với 4 seed. Pre-registration được xác nhận qua transcript. Implementation đúng trên known truth: r̂ = 0.240 so với truth 0.231 ở T = 40000.

**Đứng vững:**
- Cap theo từng phương trình chữa đúng bệnh mà verifier vòng 1 chỉ ra. r̂ ở noise0.3 tăng từ 0.115/0.159 (round 1, cùng run) lên 0.193/0.206 (truth 0.231). Không có lần sửa positive-definiteness nào.
- Số cell noise0.3 hụt 0.90 giảm từ 4/6 (eiv round 1, seed mới) xuống 1/6.
- IS so với v4: ở noise0.3 tốt hơn ở 3/6 cell (cả ba cell T150), tệ hơn ở 1/6 (T80 missing +0.45). Ở noise0.1 tốt hơn 0/6, tệ hơn 2/6. Trên dữ liệu sạch tệ hơn 6/6. Mọi số đếm đều giữ nguyên dưới Holm.
- Trên null pair, |C| tăng ở 18/18 cell.
- Ablation `plugin_eiv2` tốt hơn plugin ở 12/12 noise cell (Holm).
- Với nhiễu không đồng nhất het0.3, eiv2 đạt 0.90 ở 2/6 cell, eiv ở 1/6, v4 ở 0/6.

**Phải sửa lời:**
- "Hụt ở mức nhiễu", "không có thất bại thật": **không bác được thì không có nghĩa là đạt**. Với 20 cluster, CI của cell hụt là [0.871, 0.924]. Chỉ 7/12 cell (và 2/6 cell noise0.3) có ý nghĩa ≥ 0.90. Câu "11/12" là câu theo point estimate và phải kèm con số 7/12 theo Holm.
- "Hiệu ứng của việc sửa cap" (eiv2 so với eiv): stream bootstrap khác nhau và factor khác nhau ở 2/6 cell. Lợi ích coverage chủ yếu được mua bằng width (rộng hơn 15.6–18.4%), còn IS khác biệt ở 0/6 cell.
- Spread do rng của probe 2 lên tới 0.023, không phải ≤ 0.01. RMSE ở T150 là 0.073.
- Doc chưa công bố một timing run trên D-07H (cho phép, nhưng phải ghi vào doc).

Nguồn: results/ext_eiv2_{eval,hetero,probes,r1fix}/. Verifier: results/ext_verify2_eiv2/{recompute.txt, cov_ci.txt, confound.txt, small_case.txt, probe_rng_diff.txt}.

### 1.6 `revlag` (R2-6, R2-7): coverage dưới reversal, lag output, và flag RQ4.4

**Verdict theo rule.**
- (a) So với oracle_cal: **M** ở 4/4 cell (Holm 4/4), bền qua theta. So với raw oracle: không kết luận được (4 cell U).
- (b) `tolerant_v4L` **GIỮ**: L1 4/4 (Holm 4/4), L2 có 0 cell tệ hơn.
- (c) Flag frozen **ĐẠT** F1–F4 5/5 (Holm 5/5) trên run D-07 mới (seed_base 30261102), và transfer được sang GES, latent1, latent3, noise0.1, noise0.3 (5/5, Holm 5/5).

Verifier xác nhận: hash của rule khớp, validity identity giữ (38,934 dòng, 0 khác biệt), mọi số tái lập được, và v4L đúng trên known truth (C/lo/hi giống hệt v4 ở 48/48 run).

**Đứng vững:**
- Coverage trên affected pair (|ΔC| ≥ 0.05), v4 so với oracle_cal: rev-0.2 T80 0.862 so với 0.944 (gap −0.082 [−0.108, −0.056]); rev-0.2 T150 0.909 so với 0.978; rev-0.5 T80 0.863 so với 0.945; rev-0.5 T150 0.906 so với 0.970.
- Verifier bổ sung một bằng chứng mạnh hơn: oracle_cal là reference cùng mức width (trên unaffected pair, chênh coverage là −0.002 đến +0.005). Trên affected pair, interval của v4 **rộng hơn** (median 2.23 so với 1.45) nhưng sai số điểm lớn gấp 2.4 lần (0.51 so với 0.21). Vậy gap đến từ **centering**, không phải từ width.
- L1, peak-lag hit v4 → v4L: 0.027 → 0.110, 0.014 → 0.123, 0.047 → 0.347, 0.052 → 0.321 (mọi p Holm = 0.002). Mean-lag error trên damaged reversed pair giảm từ 0.86–0.91 xuống 0.37–0.60. L2: 0/21 cell tệ hơn.
- Flag trên clean T80/150: AUROC 0.730 [0.694, 0.763] so với rel_width 0.657 (delta +0.073 [+0.040, +0.110]); 8.2% pair bị flag; miss-rate ratio 4.32 [3.42, 5.50]. Ở T40: AUROC 0.824, 19.3% bị flag, ratio 7.95.
- Phần sửa doc vòng 1 đã được append một lần vào metrics.md.

**Không đứng vững hoặc phải sửa lời:**
- **"Lỗi module do nhánh xử lý đảo chiều" không được ủng hộ.** Reference là một oracle biết hướng thật, còn module chỉ biết số cạnh bị đảo. Chưa có comparator khả thi nào được chạy, nên chưa biết gap có giảm được hay chỉ là cái giá thông tin.
- **"Khó nội tại ở T80" bị nói quá.** Raw oracle under-cover ở mọi nơi khi T80: 0.899 ở cell none, 0.902/0.909 trên unaffected pair. Phần khó riêng của affected pair nhiều nhất khoảng 0.03 ở T80 và bằng 0 ở T150.
- "Bền theo theta" gần như hiển nhiên: các tập affected gần như trùng nhau (233/232/227 và 569/564/558 pair).
- **L1 ở rev-0.2 mong manh.** Cell T80 chỉ dựa trên 6 pair bất đồng trong 73 pair, và **không tái lập** trên run mới: +0.026 [0.000, 0.066], Holm p 0.128, nên L1 chỉ còn 3/4.
- Peak hit của v4L vẫn rất xa oracle (0.11–0.35 so với 0.90–0.93), và lag percentile interval chỉ cover 0.66–0.76. **Không được** báo lag interval như interval trung thực.
- Flag ở T40: so với score đơn giản 1/width, phần lợi chỉ là +0.015 [+0.005, +0.025] (AUROC 0.808 so với 0.824). Ở T80/150 là +0.072. Comparator đã đăng ký (rel_width) là comparator yếu.
- Flag được train và test trên cùng 20 topology D-07, chỉ khác seed. Đây là generalisation sang dữ liệu mới, không sang topology mới.
- Câu "cả hai script được viết trước khi thấy số nào" sai với analyze_flag.py: script này được viết sau khi đã xem (a)/(b), nhưng trước khi có số (c).
- AUROC cho auto3/v5 (một phần của R2-7) chưa làm.

**Câu X1 mới (thay câu X1 vòng 1):**
> Trên các pair bị ảnh hưởng bởi cạnh đảo (|ΔC| ≥ 0.05), `tolerant_v4` cover 0.86 (T80) và 0.91 (T150), so với 0.94–0.98 của một oracle biết hướng đúng được widen về cùng mức width. Interval của v4 rộng hơn nhưng lệch tâm. Chưa test xem gap này có giảm được bằng cách xử lý reversal tốt hơn hay không.

Nguồn: results/ext_revlag_{lag,fresh,identity,flagdesign}/. Verifier: results/ext_verify2_revlag/{recheck_a.md, recheck_bc.md, known_truth.md, width_baseline.md}.

### 1.7 `tlp2` (R2-8): TLP với double bootstrap đúng bài

**Verdict theo rule mô tả.** Theo cách chấm ghi trước: Claim A. Với các bootstrap draw của v4 từ round 1 (sensitivity): Claim A'. Verifier chạy lại score.py và được output giống từng byte. Rule ghi lúc 02:28:14Z, trước run đầu tiên lúc 02:28:33Z. Các dòng được tái lập bit-for-bit, và known truth cho coverage 0.938/0.965 ở T150/T400.

**Đứng vững:**
- Ở T ≥ 80, v4 thắng `tlp2_db` (MSDB B1 = 200, B2 = 100, p = 2q = 4) và `tlp2_db_p3` ở 12/12 damaged cell. Mọi lần thắng đều qua Holm, dưới cả hai cách chấm.
- So với `targeted_lp` (một tầng), v4 thắng 12/12 theo cách chấm chính và 11/11 theo sensitivity. Cell sát biên là T80 missing-0.2: −0.22 [−0.42, −0.02] ở bản chính, −0.18 [−0.38, +0.02] (p = 0.076) với draw round 1.
- TLP không thắng cell nào ở T ≥ 80, có hoặc không có cổng coverage.
- Ở T40 missing, TLP có IS thấp hơn nhưng under-cover (0.79–0.87). `tlp2_lp_cal` thắng v4 ở hai cell này (coverage 0.965/0.950, IS 4.86/4.84 so với 7.77/7.53).
- Pairing check ghi trước **thất bại** (660/1260) do bug c_idx trong driver của chính owner (`run_cells.py`). Bug này đã được công bố, và giải thích của owner được verifier xác nhận.

**Không đứng vững hoặc phải sửa lời:**
- **"Double bootstrap đúng bài không làm TLP mạnh lên" lẫn hai thay đổi.** `tlp2_db` đổi cùng lúc double bootstrap, p từ 3 lên 4, và mẫu theo horizon. `tlp2_db_p3`, bản tách riêng double bootstrap, **tốt hơn** `targeted_lp` ở 5/14 cell (T80 none −0.23 [−0.41, −0.02], extra −0.19/−0.19). Thiệt hại chủ yếu đến từ p = 4. Câu an toàn: "cấu hình đúng bài (MSDB, p = 2q) tệ hơn bản một tầng ở 15/21 cell; MSDB với p = q + 1 tốt hơn ở cell sạch/extra nhưng v4 vẫn thắng mọi cell."
- **Claim B (v4 thắng TLP đã calibrate) không độc lập ở T80.** Grid calibration chỉ widen được, và `tlp2_lp_cal` nhận factor 1.0 ở 5/6 cell T80, nên nó thực chất là `targeted_lp`. Phải gọi đúng là "widen-only calibration".
- Caveat 4 của owner lẫn hai lần gián đoạn khác nhau (02:50 và 10:24 giờ địa phương); doc thì xử lý đúng.

**Câu paper cho TLP (A' đã sửa):**
> Ở T ≥ 80, `tolerant_v4` có interval score thấp hơn Targeted Local Projections (Nemtyrev & Boldea 2026) ở 12/12 damaged cell so với bản double bootstrap đúng bài (B1 = 200, B2 = 100, p = 2q) và bản double bootstrap với p = q + 1, và ở 11–12/12 cell so với bản bootstrap một tầng. Mọi lần thắng đều qua Holm trong 12 cell. TLP không tốt hơn ở cell nào, dù có hay không có cổng coverage ≥ 0.90. Ở T = 40 không có câu "v4 thắng": TLP có IS thấp hơn ở hai cell thiếu cạnh nhưng under-cover (0.79–0.87), còn bản TLP được calibrate width thắng v4 ở hai cell đó.

Nguồn: results/ext_tlp2_rules/, results/ext_tlp2_rules_v4r1/. Verifier: results/ext_verify2_tlp2/{rescore/, reproduce_rows.json, known_truth.json, verify_summary.json}.

### Bảng tóm tắt

| Hướng | Verdict theo rule | Verifier | Phần còn lại sau kiểm chứng |
|---|---|---|---|
| baselines2 | R-B2 FAIL (4/8, Holm 4/8); R-B2s HOLDS (8/8) | partly | T150 hòa pselect_v2; biên ở T80 phụ thuộc budget của comparator; pselect_v2 lấp được lỗ lag-0 |
| v51 | GIỮ (raw và Holm); latent1 9/9 | partly | IS ở T40 missing giảm khoảng 2.4–2.9, không hại ở T ≥ 80; tau mong manh; "hybrid" thực chất là v5 de-dup |
| auto5 | auto3 latent1 4/4; fair claim FAIL 6/8; auto5 LOẠI | partly | auto3 bền dưới latent1; claim baseline phải thu hẹp; auto5 hụt 0.898 |
| v4c | GIỮ (C1 14/14, TOST Holm 5/14; C2 2/2) | chưa kiểm chứng kết quả | Replication của v5_cal2: −0.79/−0.71 ở T40 missing |
| eiv2 | LOẠI 11/12 (Holm ≥ 0.90: 7/12) | holds | Sửa cap đúng, nhưng 30% noise vẫn chưa giải quyết; nhiễu không đồng nhất 2/6 |
| revlag | M 4/4; v4L GIỮ; flag ĐẠT | partly | Gap do centering; L1 ở rev-0.2 không tái lập; flag dùng được ở T ≥ 80 |
| tlp2 | A (A' theo sensitivity) | partly | v4 > TLP ở T ≥ 80 (A'); câu về double bootstrap và Claim B phải sửa |

---

## 2. Các claim chính của Paper 4 sau vòng 2

### 2.0 Cập nhật các xung đột X1–X9 của vòng 1

- **X1 (reversal).** Thay bằng câu X1 mới ở mục 1.6: gap so với oracle cùng mức width là 0.06–0.08 và do centering. Cả hai nửa của câu vòng 1 đều phải bỏ: "chủ yếu là khó nội tại" sai, mà "lỗi của nhánh reversal" cũng chưa được chứng minh.
- **X2 (lag-0 của pselect).** Được xác nhận. Khi adapter được sửa (pselect_v2), lỗ hổng lag-0 biến mất, và ở T150 v4 chỉ còn hòa.
- **X3 (nguồn lợi thế ở T150).** Giữ phần dựa trên redteam F6 (so với pselect_cal và fullvar_cal). Bỏ câu "nhất quán với narrow: v5_sel +0.25 ở T150", vì số đó đến từ module có bug. Bổ sung: ở T150 baseline mạnh nhất là pselect_union_v2, và nó hòa v4.
- **X4 (targeted hay all-lag).** Câu "targeted ở T nhỏ, all-lag ở T lớn" **không còn đứng vững như một phát hiện**. Bằng chứng mới:
  - Probe D-07H của v51 sau khi de-dup: targeted thắng ở T40/80/150/200, nhưng sát biên ở T100.
  - auto5: 6/16 cell targeted thắng, 10 cell hòa, và T150 bị lẫn với width factor.
  - Kết quả 9.29 so với 5.18 của gate vẫn đứng, vì là một thiết kế khác: không có re-selection, không có budget.

  Câu đúng: "targeted opening có re-selection và de-dup không tệ hơn all-lag ở mọi T đã thử, và tốt hơn rõ ở T40. Ở T ≥ 80, lợi thế nếu có thì nhỏ và chưa ổn định."
- **X5, X6.** X6 được cập nhật: v5_1 thắng pselect_cal ở T40 missing (C4a −2.90/−2.37) và hòa targeted_lp_cal. Riêng phần two-sided calibration (v4c) cho −0.79/−0.71 so với v4.
- **X7.** Đã làm (R2-3b). Kết quả là claim thu hẹp ở mục 2.2.
- **X8.** Được xác nhận bằng eiv2: r̂ 0.193/0.206 so với 0.115/0.159.
- **X9.** Đã sửa ở runner (seed theo tên). Còn một lỗi seeding khác theo vị trí cell (bug E1, mục 6).

### 2.1 Claim chính "module thắng baseline mạnh ở cell thiếu cạnh khi T ≥ 80": **không đứng vững ở dạng tổng quát**

Lý do:
1. R-B2 (rule ghi trước) **FAIL**. Ở T150, v4 chỉ hòa pselect_union_v2 ở cả hai cell missing.
2. Ở T80, biên so với pselect_union_v2 phụ thuộc budget của comparator. Comparator chỉ có khoảng 80 draw mỗi graph và 4 graph. Bản đúng budget hòa v4 ở missing-0.2 trên probe D-07H.
3. Theo envelope (baseline mạnh nhất trong từng cell, post hoc), v4 thắng qua Holm chỉ ở **1/4 cell** (T80 missing-0.5, so với fullvar_cal: −0.45 [−0.59, −0.31]). Ở T80 missing-0.2, biên so với targeted_lp chỉ qua mức không hiệu chỉnh (−0.20 [−0.39, −0.02], p = 0.032, không qua Holm trên 94). Ở T150, cả hai cell hòa.

**Câu thay thế được phép viết (exploratory, D-07 development):**
> Ở T ≥ 80 trên cell thiếu cạnh (missing-0.2 và missing-0.5), `tolerant_v4` đạt coverage 0.957–0.968, và không baseline nào đã thử có interval score thấp hơn nó ở cell nào. v4 có interval score thấp hơn có ý nghĩa (qua Holm) so với các baseline đã calibrate theo cách E3 (`pselect_cal`, `bvar_cal`, `ida_cal`; 4/4 cell), so với `bvar_minnesota_v2` và bản calibrate (4/4 cell mỗi bản), và so với mọi phiên bản Targeted Local Projections (12/12 damaged cell ở T ≥ 80, 11–12/12 với bản một tầng). So với baseline mạnh nhất trong từng cell, v4 thắng ở T80 missing-0.5, thắng không hiệu chỉnh ở T80 missing-0.2 (so với `targeted_lp`, không qua Holm), và **hòa** `pselect_union_v2` ở T150 (−0.10 [−0.30, +0.08]; −0.07 [−0.25, +0.08]).

Hai điều kiện đi kèm:
- (i) Biên ở T80 so với pselect phụ thuộc budget bootstrap của baseline. Bảng chính phải ghi số draw mỗi graph của từng method.
- (ii) "Không baseline nào thắng" là một quan sát, không phải non-inferiority có margin. Không được viết "non-inferior".

Câu cũ "v4 thắng baseline mạnh nhất ở 4/4 cell missing khi T ≥ 80" phải xoá khỏi mọi bản nháp.

### 2.2 Các claim khác (câu chữ chính xác, kèm điều kiện; tất cả là exploratory trên D-07 development)

**C-T40 (chế độ có khai báo, T nhỏ).**
> Ở T = 40 trên cell thiếu cạnh, `tolerant_v4` hòa `pselect_union` đã calibrate. Chỉ dùng two-sided calibration (`tolerant_v4c`) đã giảm interval score 0.71–0.79 (coverage 0.956–0.958). Thêm targeted lag opening có re-selection trong từng bootstrap draw (`tolerant_v5_1`) thì interval score là 4.84/5.09 so với 7.77/7.53 của v4, với coverage 0.922/0.939. Mức này thắng `pselect_cal` (−2.90, −2.37) và hòa `targeted_lp_cal`. Ở T ≥ 80, `tolerant_v5_1` có interval score trong khoảng 0.855–1.026 lần v4 và không cell nào tệ hơn có ý nghĩa sau Holm.

Điều kiện: kết quả v4c chưa được kiểm chứng. Ngưỡng τ chuyển nhánh của v5_1 nằm trên ranh giới mong manh, và trên grid này v5_1 luôn đi nhánh targeted. Coverage dưới noise0.1 yếu hơn v4 (5/9 cell dưới 0.90, so với 1/9 của v4).

**C-auto (chế độ không khai báo).**
> `tolerant_auto3` không đọc mức hỏng được khai báo. Ở T ≥ 80 nó giữ coverage ≥ 0.90 ở mọi cell thiếu và đảo cạnh, cả khi có một confounder ẩn (latent1: 0.937–0.977). So với baseline được calibrate theo T mà không đọc stated kind, nó thắng `plugin`, `ida_union` và `bvar_minnesota` ở 8/8 cell missing/reversed, và thắng `pselect_union` ở 6/8 (hòa ở missing-0.2, T80 và T150). Trên skeleton đúng, nó chịu phạt 0.12–0.69 interval score so với raw `ida_union`, và ở T150 thua cả raw `plugin` ở cell none và extra.

Điều kiện: ở missing-0.5, plugin/ida calibrate gộp chỉ cover 0.44–0.52, nên các trận thắng ở đó gần như tự động. Câu "thắng" chỉ đáng kể ở pselect.

**C-TLP.** Dùng câu A' đã sửa ở mục 1.7.

**C-reversal (RQ4.1).** Dùng câu X1 mới. Thêm câu về lag:
> Báo lag từ structural draws (`tolerant_v4L`) nâng peak-lag hit trên damaged reversed pair từ 0.01–0.05 lên 0.11–0.35, và giảm mean-lag error từ 0.86–0.91 xuống 0.37–0.60, mà không làm tệ cell nào (0/21). Mức này vẫn xa oracle (0.90–0.93). Ở reversed-0.2 lợi ích nhỏ và không tái lập ở T80 trên run mới. Lag interval cover chỉ 0.66–0.76 nên không được báo như interval trung thực.

**C-RQ4.4.**
> Một flag logistic cố định, gồm width, relative width và stated damage, train trên run D-07 trước và test trên run D-07 mới (cùng topology, seed mới), đạt AUROC 0.730 [0.694, 0.763] ở T80/150 và 0.824 ở T40. Ở T80/150 flag đánh dấu 8.2% pair với miss-rate gấp 4.32 lần. Flag transfer được sang GES, latent và noise (AUROC 0.596–0.738). Ở T40 phần lớn khả năng phân biệt đến từ width đơn thuần: 1/width cho AUROC 0.808.

**C-noise (giới hạn).** Dùng câu ở docs/ext/eiv2.md "Kết luận vòng 2", và phải thêm "7/12 cell có ý nghĩa ≥ 0.90 sau Holm" cạnh "11/12".

**C-phương pháp.** Hai câu:
> Test adjacency phải làm trong phương trình cấu trúc của skeleton.

> Khi mở lag theo từng cặp, term phải được de-duplicate. Một lỗi trùng term đã làm giảm một nửa hệ số trong mọi run missing của version round 1, và đảo kết luận "targeted thua ở T lớn".

(Câu thứ hai dành cho phần reproducibility/threats, không phải đóng góp chính.)

---

## 3. Module of record và run niêm phong P4-H2

### 3.1 Module of record

- **Hiện tại: `tolerant_v4` (frozen, `experiments/calibration/tolerant_v4_frozen.json`) vẫn là module of record.** Ứng viên đạt rule ở vòng 2 có `tolerant_v5_1` và `tolerant_v4c`. Cả hai chỉ là exploratory trên D-07 development, và D-07 đã được dùng rất nhiều cho chính dòng v5. Đổi module of record chỉ dựa trên D-07 là không được.
- **Cam kết trước (ghi tại đây, trước P4-H2):** nếu spec v5_1 cho kết quả CONFIRMED trên P4-H2, theo rule C1–C3 và với các sửa ở mục 3.3, thì module of record ở **chế độ có khai báo** đổi thành `tolerant_v5_1`. Paper sẽ mô tả nó là "v5 với targeted opening đã de-duplicate". Không gọi nó là hybrid, vì nhánh all-lag không bao giờ được dùng trên grid T ≤ 150. Nếu NOT CONFIRMED, v4 được giữ, và kết quả T40 của v5_1 chỉ được báo là exploratory.
- **`tolerant_v4c` không là ứng viên riêng.** Nó chính là nhánh all-lag (`v5_cal2`) của v5_1, và v5_1 trội hơn ở T40 missing (4.84/5.09 so với 6.98/6.82; hai run có dòng v4 trùng nhau, có thể ghép cặp miễn phí ở R3-2). Kết quả v4c được dùng để định lượng riêng phần two-sided calibration trong ablation.
- **Chế độ không khai báo: `tolerant_auto3`** được đề xuất làm module of record của chế độ auto **nếu** spec auto3 CONFIRMED. auto5 đã bị loại.
- `tolerant_eiv2` và `tolerant_auto5` không là ứng viên. `tolerant_v4L` là một thay đổi cách báo lag, không phải module mới. Nếu được xác nhận, cột lag của module of record sẽ lấy từ structural draws.

### 3.2 Bảng ứng viên cho run P4-H2 duy nhất

Mọi spec dưới đây được viết bởi owner. **Chưa spec nào được chạy.** Cột "Verifier" ghi đánh giá về độ đầy đủ của spec.

| # | Ứng viên (vai trò) | Method | Module / file khoá | Config | Frozen calibration | Analyzer | Rule xác nhận (tóm tắt) | Verifier | Quyết định của lead |
|---|---|---|---|---|---|---|---|---|---|
| P1 | v5_1 (**primary**, chế độ khai báo) | `tolerant_v5_1` vs `tolerant_v4` | src/paper4/ext_v51.py (TAU = 6.6083), ext_narrow.py, methods.py, estimator.py | experiments/configs/ext_v51_p4h2.json (a2 grid, 3 rep, n_boot 199, seed_base 20261102) | experiments/ext/v51/frozen_v4_v51.json (phần mod\|* = tolerant_v4_frozen.json) | experiments/ext/v51/rule_p4h2.py | CONFIRMED nếu cả ba đúng. **C1**: T40 missing-0.2/0.5 có cov ≥ 0.90 và cận trên CI 95% (v5_1 − v4) < 0 (topology bootstrap 1000, seed 0). **C2**: 12 damaged cell T80/150 có cov ≥ 0.90 và IS ≤ 1.05 × v4. **C3**: 7 cell có IS ≤ 1.05 × v4. Holm báo kèm | **CHƯA ĐỦ**: (1) hash common.py và các file runner/metrics/generator/skeleton/effects/topology; (2) guard `__module__ == 'paper4.ext_v51'`; (3) cell có 0 run ok thì NOT CONFIRMED thay vì crash, và đặt trần failure rate; (4) ghi rằng nhánh all-lag không dùng đến, và tau mong manh; (5) multiplicity giữa các spec | **VÀO**, sau khi owner sửa (1)–(4) bằng file mới (ví dụ rule_p4h2_v2.py) và ghi hash mới |
| P2 | auto3 (**primary**, chế độ auto) | `tolerant_auto3` vs `tolerant_v4`, `plugin`, `oracle` | src/paper4/ext_gate.py + experiments/ext/gate/width_table.json (sha256 trong results/ext_auto5_p4h2_dryrun/frozen_sha256.txt) | experiments/configs/ext_auto5_p4h2_auto3.json và experiments/configs/ext_auto5_p4h2_auto3_latent1.json | experiments/calibration/tolerant_v4_frozen.json | experiments/ext/auto5/check_p4h2.py | CONFIRMED nếu cả bốn đúng (point rule trên pooled coverage). **C1**: cov ≥ 0.90 ở 8 cell missing/reversed T80/150. **C2**: IS cell none ≤ 1.35 × v4 ở T40/80/150. **C3**: cell GES T80/150 có cov ≥ 0.90 và IS ≤ 1.10 × v4. **L1**: latent1 cov ≥ 0.90 ở missing-0.2/reversed-0.2 T80/150. Holm trên 14 cell báo kèm | **CHƯA ĐỦ (nhẹ)**: (1) run auto3 thất bại phải tính là không cover hoặc phải bằng 0, và báo số run ok theo cell (script hiện bỏ qua âm thầm); (2) ghi trước rằng dry run D-07 chỉ đạt 0.903 ở T80 reversed-0.5 (Holm 13/14), nên kết quả mong manh. P4-H2 có 20 topology, như D-07, nên ước lượng thời gian giữ nguyên | **VÀO**, sau khi sửa (1)–(2) bằng file mới |
| P3 | Flag RQ4.4 (secondary) | flag trên `tolerant_v4` | experiments/ext/revlag/frozen_flag.json (sha256 7da8843f…7df3) | experiments/configs/ext_revlag_p4h2.json (T 40/80/150, 7 cell, 3 rep) | hard-coded `ext_revlag._FROZEN` → tolerant_v4_frozen.json (key `frozen_calibration` **không được đọc**) | run_pairs.py → analyze_flag_p4h2.py | Intersection F1–F4: AUROC CI lo > 0.65 (T80/150 và T40); AUROC − AUROC(rel_width) CI lo > 0; flagged ≤ 0.5, ratio ≥ 2 với CI lo > 1 | **Gần đủ**: ghi rõ cơ chế frozen hard-coded và việc tolerant_v4_frozen.json đã được ghim hash; ghi nhận lệch mã hoá feature "stated" (0.56% dòng); nói rõ đây là claim riêng | **VÀO**. Lead ghi thêm: báo AUROC của 1/width như comparator mô tả |
| P4 | v4L lag reporting (secondary) | `tolerant_v4L` vs `tolerant_v4` | src/paper4/ext_revlag.py (hash trong results/ext_revlag_identity/p4h2_spec_sha256.txt) | experiments/configs/ext_revlag_p4h2.json (cùng run với P3) | như P3 | analyze_lag.py --run ext_revlag_p4h2 | **L1**: peak-hit gain có CI lo > 0 và Holm p < 0.05 ở 4/4 cell (rev-0.2/0.5 × T80/150). **L2**: 0/21 cell tệ hơn | **Gần đủ**; rủi ro: rev-0.2 T80 đã không tái lập trên D-07 mới | **VÀO** (không tốn thêm run). 3/4 = NOT CONFIRMED, như doc đã ghi |
| P5 | TLP baseline (secondary) | `tolerant_v4` vs `targeted_lp`, `tlp2_db`, `tlp2_db_p3` | src/paper4/ext_tlp.py, src/paper4/ext_tlp2.py | experiments/configs/ext_tlp2_p4h2.json (T 80/150, mọi damage cell) | experiments/calibration/tolerant_v4_frozen.json | experiments/ext/tlp2/score.py --runs p4h2 | **A**: mọi X, 12/12 thắng theo gate view, đều qua Holm, X thắng 0. **A'**: mọi X, ≥ 10/12, X thắng 0 theo cả hai view | **CHƯA ĐỦ**: (1) A' có bắt buộc Holm hay không phải nhất quán giữa doc và score.py; (2) hash ext_tlp.py, ext_tlp2.py, score.py, run_experiment.py; (3) ghi trước rằng claim_B "incomplete" và pairing 0/0 bị bỏ qua; (4) budget khoảng 80 phút; (5) ghi rằng realisation duy nhất theo c_idx là bản confirmatory | **CÓ ĐIỀU KIỆN**: chỉ vào nếu người dùng duyệt budget và (1)–(5) được sửa. Nếu R3-1 đưa `targeted_lp_cal`/`tlp2_db_p3` vào family chính thì P5 có thể bỏ |
| P6 | Main comparison vs pselect_union_v2 | v4 vs `pselect_union_v2(_cal)`, `bvar_minnesota_v2_cal` | src/paper4/ext_baselines2.py | experiments/configs/ext_baselines2_p4h2.json | experiments/ext/baselines2/frozen_calibration_p4h2.json | experiments/ext/baselines2/analyze_p4h2.py | C1: T80 missing, 4 so sánh với pselect_v2(_cal), Holm 0.025, PASS chỉ khi 4/4; C2: bvar_v2_cal; D: T150 mô tả | **KHÔNG CHẤP NHẬN về khoa học**: comparator thiếu budget (khoảng 80 draw/graph, cap 4), nên C1 gần như chắc chắn PASS và không nói gì về baseline mạnh nhất | **KHÔNG VÀO** ở dạng hiện tại. Thay bằng spec R3-1 |
| P7 | R3-1 main comparison (**primary**, chưa có) | v4 và v5_1 vs envelope {pselect đúng budget + `_cal`, `pselect_cal`, `fullvar_cal`, `targeted_lp_cal`, `tlp2_db_p3`, `bvar_minnesota_v2_cal`} | sẽ có | sẽ có (experiments/configs/ext_<R3 id>_p4h2.json) | phải là file frozen gồm v4 (bằng tolerant_v4_frozen.json), v5_1 và factor baseline từ D-07H | sẽ có | Đề xuất: T80/150 × missing-0.2/0.5, Holm trên toàn family (method × baseline × cell) | — | **CHỜ VÒNG 3**. Đây là claim chính của paper; không nên đốt P4-H2 trước khi spec này được khoá |
| — | v4c | `tolerant_v4c` | ext_v4c.py | không có spec | — | — | — | Không có spec (đúng, vì lúc đó chưa có kết quả) | **KHÔNG VÀO**: v5_1 bao trùm nó |
| — | eiv2, auto5 | — | — | — | — | — | — | LOẠI theo rule | **KHÔNG VÀO** |

### 3.3 Điều kiện trước khi chạy, multiplicity, và cách chạy

**Điều kiện cần (tất cả phải đúng trước khi mở P4-H2):**
1. Người dùng/giảng viên duyệt R2-0: được chạy P4-H2 một lần, và chấp nhận budget. Ước lượng với `--workers 3`:
   - P1 khoảng 11 phút (647 s trên D-07);
   - P2 khoảng 20–30 phút;
   - P3 + P4 khoảng 10 phút;
   - P5 khoảng 80 phút;
   - P7 chưa biết; riêng pselect đúng budget đã khoảng 3200 draw mỗi lần gọi.

   Tổng có thể vượt 2 giờ. Vì đây là run một lần, cần ngoại lệ có duyệt đối với hard rule 5.
2. P1, P2 và P5 (nếu vào) sửa spec bằng **file mới**, không sửa file cũ, rồi ghi sha256 mới vào doc của owner. Mọi spec phải ghim hash của `experiments/run_experiment.py`, `src/paper4/{metrics,generator,skeleton,effects,topology}.py` và `experiments/calibration/tolerant_v4_frozen.json`. Cách đơn giản nhất là một manifest hash chung do lead tạo ngay trước run.
3. Spec R3-1 (P7) được khoá, gồm rule, factor D-07H và kết quả D-07 development đã ghi. Nếu người dùng quyết định chạy P4-H2 **không** có P7, phải ghi rõ trước rằng claim baseline của paper sẽ mãi chỉ là exploratory.
4. Kết quả v4c được kiểm chứng (R3-7). Việc này không chặn run, nhưng phải xong trước khi viết ablation.

**Multiplicity giữa các spec.**
- Năm claim P1–P5 trả lời năm câu hỏi khác nhau. Mỗi spec là intersection-union bên trong nó.
- Lead quy định: **primary = P1, P2 (và P7 khi có)**; secondary = P3, P4, P5. Mọi kết quả, kể cả NOT CONFIRMED, đều được báo; không báo chọn lọc.
- Phần dùng p-value hoặc CI của primary được báo thêm một verdict có hiệu chỉnh Bonferroni theo số primary spec có thành phần p-value. Hiện chỉ có P1 C1 (và P7), nên với 2 spec thì dùng CI 97.5% cho P1 C1. Verdict theo spec gốc vẫn là verdict chính thức. Phần này lead ghi **trước** P4-H2 và cần người dùng duyệt.
- Các rule point (C2/C3 của P1, cả P2) không cần hiệu chỉnh.

**Một realisation v4 duy nhất.** Runner seed các built-in method theo vị trí cell (bug E1). Vì vậy các config P4-H2 với danh sách cell khác nhau sẽ cho các realisation v4 khác nhau. Mỗi test chỉ ghép cặp trong chính config của nó. Bảng v4 trên P4-H2 trong paper lấy từ **ext_v51_p4h2** (đủ grid a2); các config khác chỉ dùng cho test ghép cặp của chúng.

**Thứ tự và ghi log.**
- Chạy mỗi config đúng một lần bằng runner gốc (P5 không đi qua run_cells.py), theo thứ tự P1 → P2 → P3/P4 → P7 → P5.
- Không xem bất kỳ output nào trước khi tất cả config chạy xong và mọi analyzer đã chạy.
- Ghi vào split-usage log trong docs/decision_rules.md: thời điểm, hash, và verdict nguyên văn.
- Nếu một run bị gián đoạn trước khi có `runs.jsonl`, được chạy lại một lần với config giữ nguyên, và phải công bố.

---

## 4. Điểm yếu còn lại và chỗ reviewer sẽ tấn công

1. **Mọi kết quả chính chỉ là exploratory trên một bank dùng lại nhiều lần.** D-07 development đã định hình v4, v5, v5_1, auto3, ngưỡng và flag. Chỉ có một bank sạch (P4-H2), và phải chia cho 5–6 claim. Reviewer sẽ gọi đây là garden of forking paths, nên mục 3.3 phải được thực hiện đúng.
2. **Fidelity và budget của baseline.** Các baseline mạnh nhất (`pselect_cal`, `targeted_lp_cal`, `fullvar_cal`, `pselect_union_v2`) đều là bản chuyển thể của nhóm. Biên ở T80 thay đổi theo số draw của baseline. Reviewer sẽ hỏi: "baseline có được cùng budget tính toán không?" Bảng chính phải có cột budget.
3. **Calibration bất đối xứng.** Width factor được tune trên D-07H: cùng generator, cùng cell mix, nên in-distribution. Baseline được calibrate theo stated kind thì có thêm thông tin; nếu không calibrate thì bị thiệt. Grid chỉ widen được (C_GRID ≥ 1.0) nên các baseline over-cover bị kẹt ở factor 1.0 (ví dụ `tlp2_lp_cal` ở T80). v4c/`*_c2` chữa được một phần.
4. **Biên coverage mỏng và số cluster ít.** v5_1 C2 có 0.918; auto5 0.898; eiv2 0.897; dry run auto3 0.903. Với 20 topology, CI coverage một cell rộng khoảng ±0.03, và "không cell nào dưới 0.90 có ý nghĩa" không có nghĩa là đạt.
5. **T150: module không hơn pselect đã sửa.** Ở cỡ mẫu lớn, lợi thế của module so với một baseline adjacency selection tốt biến mất ở cell missing. Đóng góp phải được đóng khung là "an toàn ở T nhỏ và T vừa, không thua ở T lớn".
6. **v4 rộng hơn trên null pair.** IS null của v4 khoảng 1.6 lần pselect_v2 ở T80. Plan hỏi interval "hẹp hơn", nên RQ4.2 phải được restate theo interval score (R2-9 vẫn chưa làm).
7. **Reversal.** Coverage trên affected pair là 0.86 ở T80, do lệch tâm. Lag output vẫn xa oracle, và lag interval cover chỉ 0.66–0.76. Chưa có comparator khả thi nào để nói gap này có giảm được không.
8. **Measurement noise.** 30% vẫn chưa giải quyết (eiv2 LOẠI; nhiễu không đồng nhất 2/6). v5_1 còn yếu hơn v4 dưới noise0.1.
9. **Reproducibility.** Một bug trùng term đã đảo một kết luận của vòng 1 (X3/X4). Seed của built-in phụ thuộc vị trí cell. Nhiều run phải chạy lại sau gián đoạn. Một run được chạy với `--workers 6` và đổi interpreter. Tất cả đều đã công bố, nhưng reviewer sẽ đòi code và hash được khoá.
10. **Phạm vi.** Chỉ có SVAR tuyến tính Gaussian, 14 nút, một generator và một mô hình damage. Flag RQ4.4 mới chỉ generalise sang seed mới, chưa sang topology mới.
11. **Tau của v5_1 không làm gì trên grid.** "Hybrid" là một tham số không bao giờ được kích hoạt ở T ≤ 150. Reviewer sẽ coi đó là tham số thừa, hoặc là dấu hiệu tune.
12. **RQ4.4.** Comparator đã đăng ký (rel_width) yếu. Ở T40, 1/width gần bằng flag.

---

## 5. Việc vòng 3

Thứ tự theo mức ảnh hưởng tới claim chính và tới run P4-H2.

**R3-0. Duyệt (người dùng/giảng viên, không agent nào tự làm).** Duyệt chạy P4-H2 một lần với các spec P1–P4 (+P5, +P7), ngoại lệ về budget, và overlay Bonferroni cho primary (mục 3.3).

**R3-1. Spec so sánh chính (thay P6).** Ưu tiên cao nhất.
- Mục tiêu:
  - Module mới (ví dụ `ext_baselines3.py`) với `pselect_union_v3` đúng R2-1: ≥ 199 draw mỗi graph, cap ≥ 16 graph, kèm bản `_cal` trên D-07H.
  - Ghi rule trước, rồi chạy D-07 development cho v4 và v5_1 so với envelope {pselect_v3(_cal), pselect_cal, fullvar_cal, targeted_lp_cal, tlp2_db_p3, bvar_minnesota_v2_cal} ở T80/150 missing. Holm trên toàn family.
  - Ghi budget (số draw, thời gian mỗi lần gọi) của mọi method.
  - Sau đó viết frozen spec P4-H2: một file frozen chung, analyzer, và rule.
- Bằng chứng mong đợi: hoặc một câu "thắng baseline mạnh nhất" có điều kiện rõ, hoặc kết luận trung thực "không thua, thắng phần lớn".
- Owner: baselines2.

**R3-2. Sửa spec v5_1 và các so sánh còn thiếu.**
- Sửa các điểm (1)–(4) của P1 bằng file mới.
- Ghép cặp miễn phí v5_1 với v4c (qua dòng v4 trùng nhau) và với pselect_union_v2.
- Kiểm tra lại v5_1 với tau ≈ 2.94 (kịch bản 11% seed) chỉ ở T150, như một sensitivity mô tả.
- Ghi các số shell-only vào results/ext_v51_*.
- Owner: v51.

**R3-3. Sửa spec auto3.** Xử lý run thất bại, báo số run ok, và ghi câu về độ mong manh 0.903. Nếu muốn chữa T80 reversed-0.5 của auto5 thì phải là version mới; vì D-07 đã gợi ý cách chữa, chỉ P4-H2 hoặc một bank mới mới xác nhận được. Owner: auto5.

**R3-4. Reversal: comparator khả thi.** Pre-register một version mới: nhiều orientation draw hơn, hoặc draw có trọng số theo evidence. So nó với v4 trên affected pair để trả lời "gap có giảm được không". Báo thêm 1/width trong bảng RQ4.4. Owner: revlag.

**R3-5. TLP spec.** Sửa (1)–(5) của P5. Hoặc, nếu R3-1 đã đưa TLP vào envelope, rút P5 và ghi rõ lý do. Owner: tlp2.

**R3-6. Sửa câu chữ (chỉ append vào doc của chính hướng đó, dưới heading "Sửa sau kiểm chứng vòng 2"):**
- baselines2.md: claim hẹp lại theo mục 2.1; comparator thiếu budget; gap lag-0 chỉ ở 2/4 cell; 0.557.
- redteam.md: correction 6 ("F5 đã xử lý") → chỉ một phần.
- v51.md và narrow.md (mục 8): phạm vi của X3/X4; tau mong manh; "3–17" là trung bình theo cell; phạm vi hash; noise0.1 5/9.
- auto5.md: Holm 10/24; side finding về X4 bị lẫn yếu tố; 1.9–3.3×; target của `_calT`; thua ở cell extra T150.
- v4c.md: 4 factor dưới 1.0; c2 ≠ E3 ở 6/27 cell; 0.985; đổi interpreter; ba lần chạy; `--workers 6`; thời điểm viết analyze.py; ước lượng thời gian.
- eiv2.md: câu 11/12 kèm 7/12 Holm; confound giữa sửa cap và width; spread probe 0.023; RMSE 0.073; timing run trên D-07H.
- revlag.md: câu X1 mới; "khó nội tại"; theta; thời điểm viết analyze_flag; 1/width.
- tlp2.md: câu về double bootstrap; Claim B là widen-only; hai lần gián đoạn.

**R3-7. Kiểm chứng kết quả v4c.** Một verifier độc lập tính lại rule A và phần B từ results/ext_v4c_eval/runs.jsonl. Kiểm tra xem `--workers 6` có làm đổi kết quả không (kết quả không nên phụ thuộc số worker; kiểm bằng cách chạy lại 1–2 unit). Owner: verifier.

**R3-8. Bảng bản thảo (R2-9 còn nợ).**
- Bảng envelope theo cell (baseline mạnh nhất từng cell), kèm cột budget.
- Ablation v4 / v4c / v5_1 / fullvar_cal / pselect_cal.
- Coverage theo affected/unaffected/null với hai cột oracle (raw và oracle_cal).
- Restate RQ4.2 theo interval score.
- Mọi số đếm cell đều kèm Holm.

Owner: metrics/redteam.

**R3-9. RQ4.4 phần còn nợ của R2-7.** AUROC của flag (hoặc của một flag riêng được freeze) cho auto3 và v5_1, chỉ mô tả. Owner: revlag.

**R3-10. Ưu tiên thấp.** eiv3 với noise share theo từng chuỗi, shrink về một r chung, kèm rule mới. Hoặc calibration trên dữ liệu calibration có nhiễu (cần runner hỗ trợ). Chỉ làm khi còn CPU.

**R3-11. Runner (cần người dùng duyệt, kèm regression check).** Sửa E1, E3, E4, E5, E6 ở mục 6 **sau** run P4-H2, hoặc trước run nhưng với regression check chứng minh dòng v4 trên D-07 không đổi. Sửa E1 trước P4-H2 sẽ đổi realisation của v4, nên nếu làm thì phải làm trước khi khoá hash.

---

## 6. Bug cần sửa trong file có sẵn (CHƯA áp dụng, chỉ báo)

| # | File:dòng | Vấn đề | Đề xuất sửa | Mức |
|---|---|---|---|---|
| E1 | experiments/run_experiment.py:180–181 | Built-in method (v4, plugin, …) được seed bằng `rng([unit, 3, T, c_idx, tag])`, với c_idx là **vị trí** cell trong config. Bỏ hoặc đổi thứ tự cell là đổi draw (làm hỏng pairing của tlp2), và các config P4-H2 khác nhau sẽ cho các realisation v4 khác nhau | Seed theo hash của khoá cell (T, kind, rate); làm như một thay đổi có version kèm regression check | Major (tái lập) |
| E2 | experiments/run_experiment.py:45 (B6 vòng 1, còn mở) | `C_GRID` bắt đầu từ 1.0, nên calibration chỉ widen được. Hệ quả: `tlp2_lp_cal` bằng `targeted_lp` ở T80, auto3 over-cover ở T150, baseline over-cover kẹt ở 1.0 | Hiện các module dùng pre-scale 0.5 (v4c, v5_1, `*_c2`). Nếu sửa ở runner thì phải là version mới | Design |
| E3 | experiments/run_experiment.py (bước summarize) | Crash khi config thiếu key `purpose`, sau khi đã ghi runs.jsonl (verifier baselines2 gặp phải) | Dùng `cfg.get('purpose', '')` | Minor |
| E4 | experiments/run_experiment.py (nạp ext_*) | Runner import mọi module ext_*, nên một module nạp sau có thể âm thầm ghi đè một tên method đã đăng ký | Báo lỗi khi tên method trùng; ghi `fn.__module__` vào manifest | Major (với run niêm phong) |
| E5 | experiments/run_experiment.py:429–433 | `frozen_calibration` ghi đè **mọi** key không bắt đầu bằng `_` (`calib_c.update`). Một file frozen gộp có thể ghi đè bất kỳ method nào mà không có dấu vết | Ghi vào manifest danh sách key bị ghi đè và sha256 của file frozen; tuỳ chọn whitelist theo method | Minor/Major |
| E6 | experiments/run_experiment.py (manifest) | Manifest không ghi interpreter, numpy version và số worker (v4c đổi từ numpy 2.0.2 sang 2.5.4 mà không có dấu vết) | Ghi `sys.executable`, `numpy.__version__`, `--workers` vào manifest | Minor |
| E7 | experiments/run_experiment.py (calibration) | `calibrate_methods` chỉ key theo stated kind; không có chế độ "theo T, gộp cell", nên auto5 phải viết script riêng | Thêm tuỳ chọn key theo T (version mới) | Design |
| E8 | src/paper4/ext_narrow.py, `opened_terms` | Trùng term (đã ghi ở cuối docs/decision_rules.md), làm hệ số giảm một nửa. File được giữ nguyên để tái lập kết quả vòng 1 | Giữ nguyên file; thêm cảnh báo trong README rằng dòng `tolerant_v5`/`v5_sel` vòng 1 dùng bản có bug | Major (đã biết) |
| E9 | src/paper4/ext_tlp.py, `targeted_lp_cal` (vòng 1, còn mở) | Phụ thuộc cache module-level và thứ tự gọi của runner | Tự tính khi cache miss (`tlp2_lp_cal` đã làm vậy) | Minor |
| E10 | docs/decision_rules.md (split-usage log) | Chưa ghi các run vòng 2 trên D-07/D-07H, run v4c `--workers 6` của phiên chính, và (khi có) run P4-H2 | Append các mục trên; bắt buộc với P4-H2 | Minor (quy trình) |
| E11 | README.md | Chưa phản ánh việc module of record có thể đổi sang v5_1 sau P4-H2, và chưa nêu bug E8 | Cập nhật sau P4-H2 | Minor (doc) |

**Bug trong file vòng 2 (owner xử lý bằng file mới, không sửa file đã dùng để chạy):**
- `experiments/ext/tlp2/run_cells.py`: lọc cell làm dịch c_idx, nên docstring "same seeds" sai (hệ quả của E1).
- `experiments/ext/v51/rule_p4h2.py`: crash khi một cell có 0 run ok (`cell_stats` trả về None). Ngoài ra nó import `common.py`, file này chưa được ghim hash.
- `experiments/ext/auto5/check_p4h2.py`: bỏ âm thầm các dòng có status ≠ ok khi gộp coverage.
- `experiments/ext/revlag/run_pairs.py`: không đọc key `frozen_calibration`; factor lấy từ đường dẫn hard-coded `ext_revlag._FROZEN`. Hiện an toàn vì file đích đã được ghim hash.
- `src/paper4/ext_baselines2.py`: seed hash có chứa stated damage. Vô hại với estimation, nhưng draw phụ thuộc vào nó; cần ghi trong doc.
- `src/paper4/ext_eiv2.py`: import từ `ext_eiv.py`, nên hai file phải được giữ nguyên cùng nhau.
- `experiments/ext/tlp2/score.py` so với tlp2.md mục 8: định nghĩa A' không nhất quán về việc có bắt buộc Holm hay không.
