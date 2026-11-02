# Tổng hợp vòng 3: kết quả sau kiểm chứng, câu chữ cuối cho Paper 4, và kế hoạch run niêm phong P4-H2

**Trạng thái.** Đây là bản tổng hợp của team lead sau vòng 3, vòng cuối trước run xác nhận duy nhất trên P4-H2. Mọi kết quả ở đây đều **exploratory, chỉ trên D-07 development** (seed_base 20261102). Calibration và design probe dùng D-07H development. Mỗi work item có một verifier độc lập. Verifier tính lại số bằng code riêng, kiểm thứ tự ghi rule và chạy, chạy known-truth test, và smoke-test spec P4-H2 trên D-07H. **Chưa có gì chạy trên P4-H2.** Không có `results/*/manifest.json` nào mang bank P4-H2 (lead guard G7 kiểm lúc 07:48Z). Team lead không chạy thí nghiệm nào. Lead chỉ viết hai script kiểm tra (`experiments/ext/synthesis_round3/`), tự test chúng trên D-07 và D-07H, và freeze một manifest hash cho kế hoạch.

**Quyết định của người dùng đã có (không bàn lại ở đây):** làm vòng 3 trước, rồi chạy P4-H2 một lần sau khi người dùng duyệt kế hoạch này. Không sửa bug E1 trước P4-H2; hệ quả được nêu ở mục 3.8. v4c không là ứng viên P4-H2 riêng, vì v5_1 bao trùm nó.

**Quyết định tóm tắt của lead.**
1. **Spec vào run P4-H2:**
   - P1: `tolerant_v5_1` so với `tolerant_v4`, primary.
   - P2: `tolerant_auto3`, primary.
   - P7: envelope bảy baseline đủ budget. Phần `tolerant_v5_1` là primary, phần `tolerant_v4` là secondary (falsification test).

   Tổng thời gian khoảng 60–75 phút với `--workers 3`, tới khoảng 100 phút nếu máy bị chia (mục 3.5).
2. **Spec bị loại vì verifier thấy chưa đủ và chưa được sửa:** P3/P4 (flag RQ4.4 và lag v4L) và P5 (TLP). Các claim tương ứng sẽ mãi chỉ là exploratory, trừ khi có bank mới. P6 đã bị P7 thay thế.
3. **Multiplicity:** verdict chính thức của mỗi spec là rule đã freeze của nó, ở mức 0.05. Overlay Bonferroni với k = 2 primary claim có p-value (P1-C1 và P7-v5_1, tức α = 0.025) là **bắt buộc báo**, và quyết định cách viết chữ "xác nhận" trong paper (mục 3.6).
4. **Module of record:** P1 quyết định, như đã cam kết ở synthesis_round2 mục 3.1. P1 CONFIRMED thì chế độ có khai báo đổi sang `tolerant_v5_1`; NOT CONFIRMED thì giữ `tolerant_v4`. P2 quyết định module của chế độ không khai báo (mục 3.10).
5. **Lỗ hổng spec mà verifier để lại cho lead** được che bằng một lead guard chung (`experiments/ext/synthesis_round3/lead_guard.py`, G1–G8) chạy trước và sau run (mục 3.3):
   - hash toàn bộ `src/paper4/*.py`, và báo lỗi nếu có `ext_*.py` mới;
   - hai biến môi trường phải unset;
   - hash manifest của bank P4-H2;
   - output dir chưa tồn tại;
   - interpreter đúng bản đã ghim.

---

## 0. Tình trạng các việc vòng 3

| Việc | Hướng | Tình trạng | Kết quả chính (D-07 development) | Verifier |
|---|---|---|---|---|
| R3-0 (duyệt) | người dùng | **chờ duyệt kế hoạch này** | — | — |
| R3-1 envelope đủ budget | baselines3 | xong | v4: nhánh (d), W19/T8/L1 (Holm 0.05 trên 56); v5_1: nhánh (b), W27/T1/L0; spec P7 frozen | **holds** |
| R3-2 sửa spec v5_1 + ghép cặp | v51fix | xong | "v5_1 bao trùm v4c" ĐẠT (6/6, Holm 6; v4c 0/21 Holm); spec P1 v2 frozen | **partly** (spec chạy được, phạm vi hash chưa đủ → lead guard che) |
| R3-3 sửa spec auto3 | auto3fix | xong | dry run D-07 CONFIRMED (Holm 13/14); P(CONFIRMED) bootstrap 0.62–0.65 (lạc quan) | **holds** (kèm 4 việc cho lead) |
| R3-4 comparator reversal | revlag3 | **chưa xong** | run D-07 không đạt điều kiện hợp lệ (oracle); chưa có verdict theo rule | **partly** |
| R3-5 sửa spec TLP | tlp3 | xong (spec), **còn lỗi** | dev re-score: A (draw chính), A' (draw round 1) | **partly** (2 lỗi cần analyzer v2) |
| R3-6 sửa câu chữ | các owner | mọi doc yêu cầu đều có heading "Sửa sau kiểm chứng vòng 2" đúng một lần | — | xác nhận ở baselines2, redteam, auto5, v4c, eiv2, tlp2, v51, narrow; revlag.md do `tables` append thay owner |
| R3-7 kiểm chứng v4c | v4cverify | xong | RETAINED tái lập; 3 đếm phần B phụ thuộc seed bootstrap | **holds** (sửa lời V2) |
| R3-8 bảng bản thảo | tables | xong | 6 bảng, mọi đếm có Holm; RQ4.2 "hẹp hơn" sai, phải restate | chưa có verifier riêng; nhiều số trùng số đã kiểm chứng ở R3-1, R3-4 |
| R3-9 AUROC cho auto3/v5_1 | revlag3 | **không có số** | run bị dừng | — |
| R3-10 eiv3 | — | không làm (ưu tiên thấp) | — | — |
| R3-11 sửa runner | — | không làm trước P4-H2 (quyết định của người dùng về E1) | — | — |

---

## 1. Từng work item: phần đứng vững sau kiểm chứng

### 1.1 `baselines3` (R3-1): so sánh chính với envelope đủ budget

**Verdict theo rule** (docs/ext/baselines3.md mục 3, ghi lúc 06:19Z, trước run D-07 lúc 06:22Z). Family có 56 so sánh: 2 method × 7 baseline × 4 cell (T80/150 × missing-0.2/0.5). Dùng Holm hai phía ở mức 0.05, cluster bootstrap theo topology với B = 4000.
- `tolerant_v4`: **nhánh (d)**. Holm W19/T8/L1; theo CI thô W24/L2. Nó thua `pselect_union_v3_cal` ở T150 missing-0.5 (+0.22 [+0.14, +0.30]) và không thắng cả envelope ở cell nào.
- `tolerant_v5_1`: **nhánh (b)**. Holm W27/T1/L0; theo CI thô W27/L0. Nó thắng cả bảy baseline ở T80 missing-0.2, T80 missing-0.5 và T150 missing-0.2. Ở T150 missing-0.5 nó hòa `pselect_union_v3_cal` (−0.01 [−0.08, +0.05]).

**Verifier xác nhận (holds):**
- Tính lại cả 56 so sánh bằng code riêng: khớp chính xác (max diff 0). Branch (b) và (d) suy ra máy móc từ rule.
- Win set của P7 khớp đúng tập W theo Holm ở B = 4000: 19 so sánh cho v4, 27 cho v5_1.
- Pre-registration giữ: hash mục 1–3 khớp `prereg_sha256.txt`, và `analyze.py` không đổi.
- Không có leakage. Bỏ stated damage thì output giống hệt (12/12). Bản `_cal` có cùng midpoint với bản thô và đúng nửa width.
- Known truth: `pselect_union_v3` cover C(H) 0.972 với skeleton đúng và 0.986 khi bỏ một cạnh thật; cặp bị bỏ được cover 12/12.
- Budget khớp `timing.json`. Baseline mạnh nhất dùng 6368 draw mỗi lần gọi, khoảng 32 lần v5_1 (199). Thời gian mỗi lần gọi: v4 0.56/0.66 s, v5_1 1.27/1.44 s, `pselect_union_v3` 8.3/11.4 s (T80/T150).
- Spec P7 chạy được. Verifier smoke-test đúng config P7, chỉ đổi bank sang D-07H, với 2 topology dưới interpreter miniconda đã ghim: 80/80 row ok, gồm cả `tlp2_db_p3`. Output giống hệt khi chạy bằng CLT python (0/80 mismatch). Manifest P7 có 28 file cộng 9 ext module, và tất cả hash lại đúng.

**Số đứng vững:**
- Ở cả 4 cell, baseline mạnh nhất là `pselect_union_v3_cal`: IS 3.36 / 3.40 / 1.91 / 2.00, coverage 0.936 / 0.943 / 0.962 / 0.967 (thứ tự T80 m0.2, T80 m0.5, T150 m0.2, T150 m0.5).
- v5_1 − `pselect_union_v3_cal`: −0.52 [−0.67, −0.37], −0.30, −0.15 [−0.23, −0.07], −0.01 [−0.08, +0.05].
- v4 − `pselect_union_v3_cal`: −0.09 [−0.27, +0.10] và −0.03 [−0.20, +0.14] (hòa ở T80); +0.15 [+0.04, +0.25] ở T150 m0.2 (p 0.0085, tệ hơn ở mức thô, hòa sau Holm); +0.22 [+0.14, +0.30] ở T150 m0.5 (thua, qua Holm).
- Coverage: v4 0.957–0.968, v5_1 0.949–0.968. Ở mọi cell, 0/60 run thất bại.
- Phần lớn biên lớn của vòng 2 ở T80 so với `pselect_union_v2` đến từ việc baseline đó bị cắt budget. `pselect_union_v3` − `pselect_union_v2` = −0.91 và −0.98 ở T80, khoảng 0 ở T150.

**Phải sửa lời:**
- "≥ 199 draw mỗi graph" là budget **yêu cầu**. Một member vẫn được giữ khi có tối thiểu 49 draw hợp lệ. Trên D-07, 32/32 member đủ draw, nên không số nào đổi.
- Câu paper ở mục 5 của baselines3.md bỏ sót rằng v4 tệ hơn baseline mạnh nhất ở T150 missing-0.2 ở mức không hiệu chỉnh. Câu ở M1 (mục 2) đã thêm vào.
- **Overlay Bonferroni ở D-07 bị lỗi thiết kế.** Với B = 4000, p nhỏ nhất là 5.0e-4, lớn hơn 0.025/56 = 4.46e-4, nên Holm 0.025 không bác được gì (0/28). Rule D-07 giữ như đã ghi. Bản chạy lại với B = 20000 chỉ mang tính mô tả: v4 W19/T8/L1 và v5_1 W27/T1/L0 ở mức 0.025. Analyzer P4-H2 đã được đổi sang B = 20000 **sau** khi có kết quả D-07 nhưng **trước** P4-H2. Thay đổi này đã công bố.
- Row đã lưu của `pselect_cal`, `fullvar_cal` (ext_redteam_calbase) và `targeted_lp(_cal)` (ext_tlp_eval) không tái lập được với runner hiện tại: 240/240 row khác, do stream tag B1 cũ. Point estimate của `pselect_cal` và `fullvar_cal` thì trùng. Bảng của vòng 3 dùng row mới của ext_baselines3_eval ở 4 cell này.

Nguồn: results/ext_baselines3_{eval,cal,budget,dryrun_p4h2}/. Verifier: results/ext_verify3_baselines3/.

### 1.2 `v51fix` (R3-2): spec P1 v2 và các ghép cặp còn thiếu

**Verdict theo rule** (docs/ext/v51fix.md mục 1, ghi lúc 06:04:31Z, trước mọi run):
- **1.A "v5_1 bao trùm v4c": ĐẠT.** v5_1 thắng ở 6/6 cell missing, cả thô lẫn Holm. v4c thắng 1/21 cell thô (T80 none, +0.06 [+0.01, +0.12]) và 0/21 sau Holm.
- **1.B.** Với `pselect_union_v2`, bản `_cal` và `pselect_union_c2`, v5_1 thắng 21/21 (Holm 21/21). Với `bvar_minnesota_v2_cal`, v5_1 thắng 9 cell thô (7 sau Holm), còn baseline thắng 4 cell thô (2 sau Holm: T40 extra-0.2 +0.81 [+0.22, +1.58], extra-0.5 +0.93 [+0.43, +1.59]). Ở T40 missing hai bên hòa sau Holm. Riêng missing-0.5, v5_1 thắng ở mức thô: −0.42 [−0.86, −0.04].
- **1.C τ ≈ 2.94 (2.9370), chỉ ở T150.** Lợi thế của v5_1 ở T150 missing biến mất: t294 − v5_1 = +0.33 [+0.27, +0.39] và +0.28 [+0.20, +0.35], cả hai qua Holm. t294 − v4 = +0.03 và +0.05, không qua Holm. C2 vẫn 6/6 và C3 vẫn đạt.

**Verifier xác nhận (partly):**
- Mọi số ghép cặp tái lập được bằng một stream bootstrap độc lập. Row v4 khớp 1260/1260.
- Chứng minh nhánh đúng: (T−2)/29 ≤ 5.10 < 6.6083 ở T ≤ 150 với n = 14. Vì vậy nhánh all-lag không bao giờ được chọn trên grid của paper.
- Spec P1 v2 chạy được: preflight PASS 14/14, 18 hash khớp. Dry run D-07 tái lập đúng vòng 2: C1 2/2, C2 12/12, C3 7/7. Bonferroni upper bound là −2.25/−1.99 (97.5%).
- Analyzer qua 8/8 known-truth test, gồm các biên: ratio 1.049 / 1.051, coverage 0.901 / 0.899, 12 / 13 failure, và ITT coverage tính tay ra 0.8554.

**Không đứng vững hoặc phải sửa lời:**
- **Phạm vi hash chưa đủ để khoá.** Runner import mọi `src/paper4/ext_*.py`, nhưng 12 module và `diagnose.py` chạy mà không được ghim. Preflight không so hash ext với lúc freeze và không báo lỗi khi có `ext_*.py` mới. Verifier đã chứng minh: wrap `calibrate_width` và `tolerant_v3` trong bộ nhớ, preflight vẫn PASS. **Lead guard G3/G4 che lỗ hổng này** (mục 3.3).
- **ITT rủi ro hơn doc nói.** Chỉ **một** run v5_1 thất bại cũng đủ đẩy coverage xuống dưới 0.90, ở 19/60 vị trí có thể thất bại tại T80 reversed-0.5, 5/60 tại T40 missing-0.2 (C1), và 2/60 tại mỗi cell T80 extra-0.2/0.5. Ở 4 cell này, trần 3/60 mỗi cell gần như không bao giờ là ràng buộc. Câu đúng: "một run thất bại có thể lật C1 hoặc C2 ở 4 cell".
- **Đếm của sensitivity τ:** con số bền là "t294 tệ hơn v5_1 sau Holm ở 2/7 cell". Cell thứ ba (reversed-0.2) chỉ qua Holm ở 25% seed bootstrap.
- Lệnh trong spec không có `cd`. Preflight không kiểm `PAPER4_TOPOLOGY_ROOT` và không hash manifest P4-H2. Cả hai đều do lead guard và mục 3.4 xử lý.
- Một câu trong khối R3-6 vừa append vào v51.md bị sửa tại chỗ. Việc này đã công bố; về nguyên tắc đó là lần sửa thứ hai.
- Mô tả paper của v5_1 phải nói rõ method vẫn **phân nhánh theo stated missing > 0**: targeted opening đã de-dup khi skeleton khai báo có cạnh thiếu, còn ngược lại là v5 thường (tolerant với target_reversal).
- "21/21 so với pselect_union_v2" gồm những cell mà comparator chỉ cover 0.66–0.88, và comparator còn thiếu budget. Con số này không được trích như kết quả "baseline mạnh nhất".

Nguồn: results/ext_v51fix_{pairs,t150tau,shellonly,dryrun}/. Verifier: results/ext_verify3_v51fix/.

### 1.3 `auto3fix` (R3-3): spec P2 đã sửa

**Kết quả:**
- Analyzer mới (`check_p4h2_v2.py`) xử lý run thất bại/thiếu theo nguyên tắc "failed = uncovered". Một cell trượt nếu có hơn 3/60 run hỏng, và tỉ số IS được ghép cặp (≥ 57 cặp).
- Dry run trên row D-07 cho CONFIRMED, Holm 13/14. Cell duy nhất Holm không bác là T80 reversed-0.5 (coverage 0.903, p 0.385). auto3 có 60/60 run ok ở mọi cell.
- Bootstrap topology trên row D-07 cho P(CONFIRMED) = 0.616. Qua các seed Monte Carlo con số nằm trong 0.62–0.65, và nó lạc quan. Rủi ro gần như dồn hết vào T80 reversed-0.5 (band 95% 0.880–0.925).
- Ghép cặp mô tả với v5_1: auto3 tệ hơn ở 17/21 cell (13/21 sau Holm) và không tốt hơn ở cell nào. Ở T40 missing chênh +3.73 [+2.91, +4.56] và +3.88 [+2.96, +5.00]. Đây là cái giá của việc không đọc damage được khai báo. Hai mode khác nhau nên so sánh chỉ mang tính mô tả.

**Verifier xác nhận (holds):**
- Hash của ext_gate.py, width_table.json và tolerant_v4_frozen.json giống từng byte vòng 2.
- Config mới bằng config vòng 2 ở mọi key trừ name và purpose.
- Dry run tái lập chính xác. Verifier tính lại mọi số từ row thô.
- Analyzer qua 19/19 case known-truth, gồm coverage đúng 0.90, 3 và 4 failure, 57 và 56 cặp, ratio 1.35 và 1.36, kiểm tra I1–I5.
- Fix I4 (k = 0 thì dùng 'none') khớp đúng runner.
- Manifest đủ ở thời điểm viết: có mọi module runner import, 15 ext, chuỗi import GES của ACIIDS, và manifest D-07H.

**Phải sửa lời và việc cho lead:**
- **(a) I4 có hiệu lực theo analyzer, không theo text mục 1.1.** Mục 1.1 của docs/ext/auto3fix.md vẫn giữ định nghĩa I4 cũ, đã được thừa nhận là sai. Nếu áp text đó nguyên văn, mọi topology có stated k = 0 trong một cell reversed sẽ cho NOT CONFIRMED (integrity). **Lead ghi tại đây, trước P4-H2: định nghĩa I4 có hiệu lực là định nghĩa trong `experiments/ext/auto3fix/check_p4h2_v2.py` (width_key; k = 0 thì dùng 'none'), file này đã được hash.** Ngưỡng và cell của C1–C3 và L1 không đổi.
- (b) Phải liệt kê lại `ext_*.py` lúc hash. Lead guard G3 làm việc này.
- (c) File hash đưa cho preflight P6 phải là `results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt`, để P6 chứng minh "không đổi kể từ lúc spec được kiểm chứng" (mục 3.4, lệnh 3).
- (d) Phải chạy bằng `/Users/kietnt/miniconda3/bin/python`, và `PAPER4_TOPOLOGY_ROOT`, `PAPER4_ACIIDS_ROOT` phải unset. Lead guard G1/G2 kiểm.
- Fault injection của chính owner không tách được cái cap 3/60 khỏi cổng coverage. Known-truth test của verifier thì tách được (4 failure ở coverage 0.933 vẫn trượt). Kết luận vẫn giữ.
- Ở T80 reversed-0.2, "tệ hơn v5_1" chỉ vừa đủ ngưỡng (CI [+0.00, +0.17], p 0.050). Số nên trích là Holm 7/8.

Nguồn: results/ext_auto3fix_{dryrun,fragility,v51pair,e1}/. Verifier: results/ext_verify3_auto3fix/.

### 1.4 `revlag3` (R3-4, R3-9): comparator reversal khả thi; **chưa xong**

**Đứng vững (verifier: partly):**
- **Pre-registration có thật.** Hash rule lúc 06:15:39Z, trước mọi run D-07; 11 hash file khớp.
- **Probe D-07H (thiết kế, đã xem số).** Likelihood evidence Δℓ phân biệt được cặp bị đảo ở T80/150 (AUROC 0.827–0.878), nhưng ở T40 thì không (0.503–0.546). Ở T80, 10–20% cặp bị đảo nằm ngoài pool. Ở cùng mức calibration, không variant nào tăng coverage trên affected pair: R1 0/4 cho cả năm variant, kể cả sau Holm.
- **Trên row D-07 của run `ext_revlag3_rev`.** Verifier chạy analyzer đã băm của owner trên một bản sao các row này. R1/R2 chỉ dùng v4 và M; các row này hợp lệ, và rev2 sẽ cho đúng các row đó. Kết quả: R1 0/4 cho `tolerant_v4R`, `_mix` và `Rmap` (Holm 0/4); `Rmap` trượt R2a. **Tuy vậy, run này không đạt điều kiện hợp lệ đã ghi trước.** Cột oracle bị fit ở cell đánh giá đầu tiên (c_idx 5), một hệ quả kiểu E1. Rule nói run hỏng thì "coi là hỏng" và không cho chạy lại. Vì vậy **không có verdict R3-4 theo rule**. Con số 0/4 là thông tin, không phải verdict.
- **"Nhiều draw hơn" không đóng được gap.** sd Monte Carlo của centre chỉ bằng 0.035–0.049 lần centring error. Interval trung bình hai stream đổi coverage −0.009 đến +0.013. v4L là tolerant_v3 cài lại trên một stream độc lập, nên đây là ước lượng hợp lệ.
- **1/width trong RQ4.4.** Sau Holm(9), flag tốt hơn 1/width ở 5/9 tập và kém hơn ở 1/9 (GES T40). Mã hoá stated lệch ở 219/39123 row, và F1–F4 không đổi (ratio 4.32 → 4.33).

**Phải sửa lời:**
- Câu dự kiến "gap là cái giá của việc không biết hướng" bị verifier bác. R1 so coverage affected khi coverage tổng thể của hai bên khác nhau: v4 dùng factor frozen, chỉ widen được, và over-cover cell reversed. Khi rescale về **cùng coverage tổng thể** (post hoc, có dùng truth, không có CI), v4R tăng coverage affected +0.034/+0.039 ở rev-0.2 (T80/T150), tức đóng khoảng 35–50% gap tới oracle_cal ở rev-0.2. Ở rev-0.5 chỉ +0.004–0.007. Câu paper ở M5 phản ánh điều này nhưng không dùng nó làm kết quả.
- Câu "CI loại 0 ở 5 tập" phải đổi thành "7/9 tập (5 nghiêng về flag, 2 về 1/width); sau Holm 5/9 và 1/9".
- **R3-9: không có số nào.** Run flag bị dừng.
- **Spec P3/P4 sửa lại: KHÔNG đạt hard rule 7.** Chưa có `experiments/ext/revlag3/p4h2_spec_files.json`. Mục spec trong docs/ext/revlag3.md không tồn tại. Bản nháp còn placeholder `{DRYRUN_TIME}`. Lệnh ghi interpreter không thống nhất (`python` và `/usr/bin/python3`). Check nhất quán hard-code `ext_v51_p4h2`, run đã bị thay thế. Pipeline thì chạy được (dry run D-07H của verifier: 41 s cho 6 unit). **P3/P4 bị loại khỏi P4-H2** (mục 3.2).
- `run_pairs3.py` chỉ so các giá trị `mod|*` của `_FROZEN`, không so path hay hash, nên docstring nói quá.

Nguồn: results/ext_revlag3_{probe,probe2,mcdraws,flagextra,rules,rev}/. Verifier: results/ext_verify3_revlag3/.

### 1.5 `tlp3` (R3-5): spec P5 đã sửa; **còn lỗi**

**Đứng vững (verifier: partly):**
- A' giờ bắt buộc Holm cho trận thắng của v4. Doc và analyzer dùng cùng định nghĩa.
- Preflight PASS. Method resolve đúng module. Config bằng `ext_tlp2_p4h2` trừ name và purpose.
- Dev re-score tái lập chính xác. K3 (draw v4 chính) cho A: 12/12 Holm cho cả ba X, X thắng 0. K4 (draw v4 round 1) cho A': `targeted_lp` 11/12, cell hòa là T80 missing-0.2 −0.18 [−0.38, +0.02], p 0.079.
- Known truth đúng cho Holm, cho raw vs Holm, và cho cell thiếu run.
- Thời gian ước lượng khoảng 75 phút (70–90) với `--workers 3`.
- Factor của `tlp2_lp_cal` ở T80 là 1.0 ở 5/7 cell. Con số "5/6" của synthesis vòng 2 sai.

**Lỗi còn lại (verifier):**
- (a) Doc và analyzer bất đồng về coverage khi **mọi** method thất bại ở một (unit, cell). Analyzer bỏ unit đó khỏi mẫu số, còn doc tính nó là không cover. Trong edge case này verdict có thể đổi từ A sang A'.
- (b) Check realisation mô tả trỏ vào `ext_v51_p4h2` đã bị thay thế, nên không bao giờ chạy được.
- (c) Manifest thiếu `ext_v51fix.py`.
- (d) Câu paper không nói TLP **không calibrate**.

(a) và (b) cần analyzer v2 bằng file mới, và việc đó chưa làm. **P5 bị loại** (mục 3.2). Điều kiện rút W2 không đúng, vì P7 chỉ phủ 4 cell missing. W1 (budget 70–90 phút) cũng chưa được duyệt.

Nguồn: results/ext_tlp3_{checks,smoke,preflight}/. Verifier: results/ext_verify3_tlp3/.

### 1.6 R3-6 (sửa câu chữ, append một lần)

Mọi doc được giao ở R3-6 đều có heading "Sửa sau kiểm chứng vòng 2" đúng một lần (lead đã grep): baselines2, redteam, v51, narrow, auto5, v4c, eiv2, revlag, tlp2. Có ba lệch quy trình, đều đã công bố:
- v51fix sửa tại chỗ một câu trong khối vừa append vào v51.md.
- v4cverify sửa nhỏ một lần trong khối vừa append vào eiv2.md và v4c.md. Phần eiv2.md vốn được giao cho owner eiv2; v4cverify làm thay vì eiv2 không hoạt động ở vòng 3.
- revlag.md được hướng `tables` append thay owner revlag3, dựa trên bản nháp của revlag3.

Lead chấp nhận ba lệch này: nội dung đúng với R3-6, và không đoạn văn có sẵn nào bị đổi. Trong docs/ext/v51fix.md chuỗi heading xuất hiện hai lần, nhưng chỉ vì doc nhắc tới nó; không có khối append nào trong file này.

### 1.7 `v4cverify` (R3-7): kiểm chứng v4c

**Đứng vững (verifier: holds):**
- **RETAINED tái lập được** bằng code viết độc lập với analyze.py.
  - C1: 14/14 cell, ratio 0.981–1.014. TOST sau Holm 5/14 ở seed đã định, 4–5/14 qua các seed.
  - C2: −0.79 [−0.99, −0.58] và −0.71 [−0.88, −0.54], Holm 2/2. Cận trên lớn nhất qua các seed là −0.533.
- `--workers 6` và việc đổi interpreter không làm đổi row nào. Chạy lại 2 unit cùng toàn bộ calibration bằng cả miniconda (numpy 2.5.4) lẫn CLT (numpy 2.0.2) cho 252/252 row trùng tuyệt đối, và calibration.json trùng từng byte.
- Phân loại W/T/L của phần B khớp 252/252 cell.

**Phải sửa lời:**
- "Phần B đứng vững" phải đổi thành **"đếm khớp, trừ 3 cell borderline phụ thuộc seed bootstrap"**: (b) ida Holm 12–13/21, D1 (b) IUT-Holm 4–5 cell, và D6 "c2 tốt hơn cal" 8–9/45 (Holm 4/45, tệ hơn 6/45). Lý do: V2 do chính owner ghi trước không có ngoại lệ borderline.
- Dung sai CI 0.03 bị vượt ở 56/252 cell, nhưng không phân loại nào đổi. Phải báo là "vượt dung sai", không reframe theo độ rộng CI.
- Thời gian full run với 3 worker khoảng 12–16 phút, không phải 13–17.
- Chỉ 2/60 unit được chạy lại, cả hai thuộc profile erdos_renyi. Bit-identity cho các unit còn lại chỉ là suy ra từ công thức seed.
- Hai mục chỉ có nguồn từ transcript là **chưa kiểm chứng**: interpreter và nguyên nhân bị cắt của run 1 của v4c, và một timing run của eiv2.

### 1.8 `tables` (R3-8): bảng bản thảo

Sáu bảng nằm ở docs/ext/bang_ban_thao.md. Định nghĩa được băm lúc 07:03:33Z, trước khi tính số; nguồn ghi dưới từng bảng; mọi đếm có Holm. **Chưa có verifier riêng cho R3-8.** Tuy vậy nhiều số trùng với số đã kiểm chứng: bảng 1a trùng R3-1, bảng 6 (Holm 5/9 và 1/9) trùng holm_inv_width.json của verifier revlag3, và bảng 3a trùng phân tích revlag. Các kết quả mới:
- **Bảng 1b (envelope post hoc, 21 cell, 21–25 ứng viên mỗi cell, Holm trên 44).** Trên 18 damaged cell:
  - v4 tốt hơn baseline mạnh nhất ở 3, thua ở 5, hòa ở 10.
  - v5_1 tốt hơn ở 6, thua ở 2 (T40 extra-0.2/0.5, so với `bvar_minnesota_v2_cal`), hòa ở 10.
  - Cách chọn X theo IS thấp nhất trên chính D-07 nghiêng về phía baseline (winner's curse).
  - `pselect_union_v3` chỉ được chạy ở T80/150 missing.
- **Bảng 2 (ablation, Holm trên 84).** v4c − v4 tốt hơn ở 2/21 cell (chỉ T40 missing). v5_1 − v4 tốt hơn ở 7/21 và tệ hơn ở 0. `fullvar_cal` − v4 và `pselect_cal` − v4 đều tệ hơn ở 19/21.
- **Bảng 3.** Trên affected pair, v4 thấp hơn oracle_cal ở cả 6 cell reversed (Holm 6/12). Trên unaffected pair, v4 hòa oracle_cal ở 18/21 cell sau Holm.
- **Bảng 4b.** Gap "lag 0 so với lag 1–2" trên cạnh bị xoá có ý nghĩa ở 3/6 cell thô và **0/6 sau Holm**.
- **Bảng 5 (Holm trên 154).** v4 tốt hơn plugin ở 14/21 cell và tốt hơn inflate ở 12/21, không thua cell nào. Median width của v4 bằng 1.20–3.61 lần plugin, nên câu "hẹp hơn" trong plan **sai**.
- **Lệch định nghĩa đã công bố.** L1: null pair dùng "tỷ lệ interval chứa 0" thay cho coverage. L2: giữ row tlp2 của năm run lọc cell (E1), việc này không đổi X hay top-3 ở cell nào.

### 1.9 Bảng tóm tắt

| Hướng | Verdict theo rule | Verifier | Phần còn lại sau kiểm chứng |
|---|---|---|---|
| baselines3 | v4 (d) W19/T8/L1; v5_1 (b) W27/T1/L0 (Holm 56) | holds | v5_1 thắng baseline mạnh nhất ở 3/4 cell missing T ≥ 80; v4 không thắng cell nào và thua ở T150 m0.5; spec P7 đủ |
| v51fix | bao trùm v4c ĐẠT; spec P1 v2 | partly | spec chạy được, phạm vi hash cần lead guard; ITT nhạy với một failure; lợi thế T150 phụ thuộc τ |
| auto3fix | dry run CONFIRMED 13/14 | holds | spec đủ, kèm 4 việc cho lead; xác suất đạt khoảng 0.62–0.65 (lạc quan) |
| revlag3 | không có verdict R3-4 hợp lệ; R3-9 không có số | partly | evidence có ở T ≥ 80 nhưng không tăng coverage affected ở calibration riêng; spec P3/P4 thiếu |
| tlp3 | dev A / A' | partly | spec còn 2 lỗi cần analyzer v2; bị loại |
| v4cverify | RETAINED tái lập | holds | 3 đếm phần B phụ thuộc seed; workers/interpreter không đổi row |
| tables | 6 bảng | chưa có verifier riêng | v5_1 thua 2/18 damaged cell (T40 extra); RQ4.2 "hẹp hơn" sai |

---

## 2. Câu chữ cuối cho các claim chính của Paper 4

**Quy ước chung cho mọi câu dưới đây.**
1. Mọi số là D-07 development (exploratory), trừ khi câu ghi "trên P4-H2".
2. Mọi đếm cell đều kèm Holm.
3. "Hòa / không thua" là quan sát, không phải non-inferiority có margin. Không được viết "non-inferior".
4. Baseline mạnh nhất là bản chuyển thể của nhóm.
5. Chỗ ghi **[P4-H2: …]** được điền máy móc theo mục 3.10 sau run, chỉ dùng câu đã viết sẵn ở đó.

**Mô tả method (dùng nguyên văn trong phần Method):**
> `tolerant_v5_1` là `tolerant_v4` cộng thêm targeted lag opening: khi skeleton khai báo có cạnh thiếu, method mở lag block cho các cặp có evidence; tập cặp này được chọn lại trong mỗi bootstrap draw, và term trùng được de-duplicate. Khi skeleton không khai báo cạnh thiếu, method chạy như v5 không có targeted opening. Width được calibrate hai phía (pre-scale 0.5) trên D-07H. Mỗi lần gọi dùng 199 bootstrap refit.

Không dùng chữ "hybrid", và không nhắc τ như một tham số hoạt động. Lý do: ở T ≤ 150 với 14 nút, nhánh all-lag không thể được chọn. τ chỉ xuất hiện trong phần threats.

### M1. Claim chính: so với baseline mạnh nhất ở cell thiếu cạnh khi T ≥ 80

> Ở T ≥ 80 trên cell thiếu cạnh (missing-0.2 và missing-0.5), chúng tôi so với một envelope bảy baseline:
> - post-selection union (Chang–Guo–Malinsky) do nhóm chuyển thể, bản đủ budget (`pselect_union_v3`): 16 graph, adjacency test trong structural equation, cặp chọn lại được fit theo cả hai hướng, 199 bootstrap draw yêu cầu cho mỗi member, tổng cộng 6368 draw mỗi lần gọi;
> - bản của nó được calibrate width hai phía;
> - `pselect_cal`, `fullvar_cal`, Targeted Local Projections đã calibrate (`targeted_lp_cal`), TLP double bootstrap với p = q + 1 (`tlp2_db_p3`), và BVAR Minnesota đã calibrate.
>
> `tolerant_v5_1` có interval score thấp hơn mọi baseline ở 3/4 cell, với 27/28 so sánh thắng và 0 thua (Holm trên 56 so sánh), và coverage 0.949–0.968. Ở T150 missing-0.5 nó hòa baseline mạnh nhất `pselect_union_v3_cal` (−0.01 [−0.08, +0.05]). Baseline này dùng gấp 32 lần số draw và 6.6–7.9 lần thời gian mỗi lần gọi của `tolerant_v5_1`. Module trước đó, `tolerant_v4` (frozen), không thắng baseline mạnh nhất ở cell nào: hòa ở T80 (−0.09 [−0.27, +0.10]; −0.03 [−0.20, +0.14]), tệ hơn ở T150 missing-0.2 ở mức không hiệu chỉnh (+0.15 [+0.04, +0.25], hòa sau Holm), và thua ở T150 missing-0.5 (+0.22 [+0.14, +0.30], qua Holm). **[P4-H2: câu P7 theo mục 3.10.]**

Điều kiện đi kèm (bắt buộc):
- (i) Kết quả chỉ nói về 4 cell (T80/150 × missing-0.2/0.5).
- (ii) Bảng chính phải có cột budget (bảng 1c).
- (iii) Calibration hai phía của baseline mạnh nhất là do nhóm thêm vào cho công bằng. v5_1 cũng được calibrate hai phía, còn grid của v4 frozen chỉ widen được. Trận thua của v4 là kết quả của module frozen, không phải so sánh giữa hai method cùng cách calibrate.
- (iv) D-07 đã được dùng nhiều lần cho dòng v5.
- Câu vòng 2 "không baseline nào đã thử có interval score thấp hơn v4 ở cell nào" là **sai** và phải xoá khỏi mọi bản nháp.

**M1b (envelope post hoc, chỉ exploratory, không gắn với P4-H2):**
> Trên envelope post hoc gồm mọi baseline đã lưu (21–25 ứng viên mỗi cell), ở 18 damaged cell T = 40/80/150, `tolerant_v5_1` tốt hơn baseline mạnh nhất ở 6/18 cell, thua ở 2/18 (T40 extra-0.2/0.5, so với BVAR Minnesota đã calibrate) và hòa ở 10/18. `tolerant_v4` tốt hơn ở 3/18, thua ở 5/18 và hòa ở 10/18 (Holm trên 44 so sánh).

Điều kiện: chọn X theo IS thấp nhất trên chính D-07 nghiêng về phía baseline. Ở extra, reversed và T40 chưa có pselect đủ budget.

### M2. Chế độ có khai báo ở T nhỏ, và ablation

> Ở T = 40 trên cell thiếu cạnh, `tolerant_v4` over-cover (0.978–0.983) với interval score 7.53–7.77, thua TLP đã calibrate width (4.75–4.84; Holm). Chỉ dùng calibration hai phía (`tolerant_v4c`) đã giảm interval score 0.71–0.79, với coverage 0.956–0.958; kết quả này được kiểm chứng độc lập. Thêm targeted lag opening có de-duplicate (`tolerant_v5_1`) thì interval score là 4.84/5.09, coverage 0.922/0.939. Mức này hòa TLP đã calibrate (+0.08 [−0.31, +0.50]; +0.25 [−0.02, +0.53]) và hòa BVAR Minnesota đã calibrate sau Holm, và tốt hơn `tolerant_v4c` ở cả 6/6 cell thiếu cạnh (Holm). Ở T ≥ 80, `tolerant_v5_1` có interval score 0.855–1.026 lần v4, và không cell nào tệ hơn có ý nghĩa sau Holm (0/21). Khi skeleton chỉ có cạnh thừa ở T = 40, BVAR Minnesota đã calibrate tốt hơn cả hai module (so với v5_1: +0.81 [+0.22, +1.60] và +0.93 [+0.43, +1.59], Holm). **[P4-H2: câu P1 theo mục 3.10.]**

> Trong ablation, contemporaneous repair cùng orientation draw là phần mang lợi thế của module so với việc mở mọi lag: `fullvar_cal` tệ hơn v4 ở 19/21 cell sau Holm, hòa ở T40 missing. Calibration hai phía chỉ có tác dụng ở T40 missing (−0.79, −0.71; 2/21 cell sau Holm). Targeted lag opening đã de-dup giảm interval score ở cả 6 cell missing (−2.93 đến −0.23) mà không làm tệ cell nào sau Holm (0/21).

Điều kiện:
- Coverage của v5_1 sát 0.90 ở 4 cell (0.918–0.927).
- Dưới noise0.1, v5_1 dưới 0.90 ở 5/9 cell, so với 1/9 của v4 (sau Holm không cell nào có ý nghĩa).
- Lợi thế của v5_1 ở T150 missing (−0.30/−0.23 so với v4) chỉ có khi ngưỡng chuyển nhánh τ > 4.94. Với τ ≈ 2.94 (kịch bản ở 11% seed bootstrap của probe chọn τ), lợi thế này biến mất (+0.33/+0.28, Holm), còn C2 vẫn đạt.

### M3. Chế độ không khai báo (`tolerant_auto3`)

> `tolerant_auto3` không đọc mức hỏng được khai báo. Ở T ≥ 80 nó giữ coverage ≥ 0.90 ở mọi cell thiếu và đảo cạnh, kể cả khi có một confounder ẩn (latent1: 0.937–0.977). So với các baseline được calibrate theo T mà không đọc stated kind, nó thắng `plugin`, `ida_union` và `bvar_minnesota` ở 8/8 cell missing/reversed, và thắng `pselect_union` ở 6/8 (hòa ở missing-0.2, T80 và T150; Holm cho cùng số đếm). Không đọc damage có giá: so với `tolerant_v5_1`, auto3 có interval score cao hơn ở 17/21 cell (13/21 sau Holm) và không thấp hơn ở cell nào, với chênh +3.7 đến +3.9 ở T40 missing. Trên skeleton đúng, nó chịu phạt 0.12–0.69 interval score so với raw `ida_union`. **[P4-H2: câu P2 theo mục 3.10.]**

Điều kiện:
- Ở missing-0.5, plugin/ida được calibrate gộp chỉ cover 0.44–0.52, nên các trận thắng ở đó gần như tự động.
- Câu về độ mong manh ở docs/ext/auto3fix.md mục 1.2 phải đi kèm mọi lần báo kết quả P2.
- P2 là rule theo point estimate, không có kiểm soát sai lầm loại I.

### M4. Targeted Local Projections

> Ở T ≥ 80, `tolerant_v4` có interval score thấp hơn Targeted Local Projections **không calibrate width** (Nemtyrev & Boldea 2026) ở 12/12 damaged cell, cả với bản double bootstrap đúng bài (B1 = 200, B2 = 100, p = 2q) lẫn bản double bootstrap với p = q + 1. Với bản bootstrap một tầng con số là 11–12/12 cell. Mọi lần thắng đều qua Holm trong 12 cell, và TLP không tốt hơn ở cell nào. Ở 4 cell thiếu cạnh khi T ≥ 80, `tolerant_v5_1` thắng cả TLP đã calibrate lẫn `tlp2_db_p3` (thuộc envelope M1). Ở T = 40 không có câu "v4 thắng": TLP có IS thấp hơn ở hai cell thiếu cạnh nhưng under-cover (0.79–0.87), còn bản TLP đã calibrate width thắng v4 ở hai cell đó.

Điều kiện:
- "Calibration" của TLP trong runner chỉ widen được (factor 1.0 ở 5/7 cell T80). Một TLP được calibrate hai phía có thể thu hẹp gap.
- Câu "double bootstrap đúng bài không làm TLP mạnh lên" phải tách theo p: thiệt hại chủ yếu đến từ p = 4.
- Claim này **chỉ là exploratory**, vì P5 bị loại khỏi P4-H2.

### M5. Reversal (RQ4.1, phần cạnh đảo) và lag output

> Trên các pair bị ảnh hưởng bởi cạnh đảo (ΔC ≥ 0.05), `tolerant_v4` cover 0.82–0.87 ở T ≤ 80 và 0.91 ở T150, so với 0.93–0.98 của một oracle biết hướng đúng được widen về cùng mức width (thấp hơn có ý nghĩa ở 6/6 cell reversed, Holm). Interval của v4 rộng hơn nhưng lệch tâm. Trên pair không bị ảnh hưởng, v4 ngang oracle cùng mức width (18/21 cell hòa sau Holm). Chúng tôi thử một comparator khả thi: lấy orientation draw theo likelihood evidence. Evidence này phân biệt được cạnh bị đảo ở T80/150 (AUROC 0.83–0.88) nhưng không phân biệt được ở T40 (0.50–0.55). Ở mức calibration riêng của nó, comparator không tăng coverage trên affected pair ở cell nào (0/4). Khi so ở cùng coverage tổng thể (post hoc, không có CI), nó đóng khoảng 35–50% gap ở reversed-0.2 và gần như không đóng gì ở reversed-0.5. Tăng số orientation draw không đóng được gap: sai số Monte Carlo của centre chỉ bằng ≤ 0.05 lần centring error.

> Báo lag từ structural draws (`tolerant_v4L`) nâng peak-lag hit trên damaged reversed pair từ 0.01–0.05 lên 0.11–0.35, và giảm mean-lag error từ 0.86–0.91 xuống 0.37–0.60, mà không làm tệ cell nào (0/21, Holm). Mức này vẫn xa oracle (0.90–0.93). Ở reversed-0.2 lợi ích nhỏ và không tái lập ở T80 trên run mới. Lag interval chỉ cover 0.66–0.76.

Điều kiện:
- Phần comparator là thử nghiệm sơ bộ. Run D-07 không đạt điều kiện hợp lệ ghi trước (cột oracle), nên không có verdict theo rule. Con số 0/4 tính trên các row v4 và comparator hợp lệ của run đó và trên probe D-07H.
- Lag interval không được báo như interval trung thực.
- Cả hai câu chỉ là exploratory (P4 bị loại).

### M6. RQ4.1: đặc trưng sai số

> Khi skeleton thiếu cạnh, cách báo một điểm (plugin) báo hiệu ứng mất đường đi bằng 0: trên damaged pair, sai số tuyệt đối là 1.26–1.34, sai số tương đối là 1.00, và sai số không giảm theo T. Trên cùng các pair, module có sai số tuyệt đối giảm theo T (0.78–0.87 ở T40, 0.45–0.48 ở T80, 0.25–0.27 ở T150), mean-lag error 0.18–0.38 và peak hit 0.36–0.72. Cái giá xuất hiện ở T40: trên downstream pair của cell missing, sai số tuyệt đối của module cao hơn plugin (0.90 so với 0.69; 0.85 so với 0.70). Coverage trên cặp có cạnh bị xoá ở lag 0 thấp hơn ở lag 1–2 khoảng 0.01–0.05, nhưng chênh lệch không có ý nghĩa sau Holm (0/6 cell).

### M7. RQ4.2 phát biểu lại theo interval score (thay câu "hẹp hơn" của plan)

> Cách báo một điểm trên skeleton đã cho under-cover khi skeleton thiếu cạnh (plugin 0.33–0.66). Nới rộng interval của nó không cứu được hiệu ứng đã mất (`inflate` 0.49–0.54 ở missing-0.5). Module trả interval rộng hơn plugin (median width gấp 1.20–3.61 lần) nhưng giữ coverage 0.91–0.98. Interval score của nó thấp hơn plugin ở 14/21 cell và thấp hơn `inflate` ở 12/21 cell (Holm trên 154 so sánh), và không cell nào tệ hơn. Mọi cell thắng `inflate` là cell missing hoặc reversed. Ở skeleton đúng và skeleton chỉ thừa cạnh, nó ngang `inflate`.

Thêm: trên null pair, v4 rộng hơn `pselect_union_v2` (IS null khoảng 1.6 lần ở T80).

### M8. RQ4.4: flag độ tin cậy

> Một flag logistic cố định (width, relative width, stated damage) được train trên một run D-07 và test trên một run D-07 mới (cùng topology, seed mới). Ở T80/150 nó đạt AUROC 0.730 [0.694, 0.763], cao hơn score đơn giản 1/width (0.658; chênh +0.072 [+0.037, +0.107]). Flag đánh dấu 8.2% pair, với miss-rate gấp 4.32 lần [3.42, 5.50]. Ở T40, AUROC 0.824 gần như hoàn toàn đến từ width (1/width cho 0.808). Trên 9 tập kiểm tra, flag tốt hơn 1/width ở 5/9 và kém hơn ở 1/9 (GES T40), Holm trên 9.

Điều kiện:
- Generalisation chỉ sang seed mới, chưa sang topology mới.
- AUROC cho auto3 và v5_1 chưa có (R3-9).
- Claim chỉ là exploratory (P3 bị loại).

### M9. Measurement noise (giới hạn)

Dùng câu "Kết luận vòng 2" ở docs/ext/eiv2.md, kèm hai số bắt buộc:
- "11/12 cell theo point estimate; 7/12 cell có coverage ≥ 0.90 có ý nghĩa sau Holm (2/6 ở noise0.3)";
- lợi ích coverage chủ yếu được mua bằng width (rộng hơn 15.6–18.4%).

`tolerant_eiv2` bị loại theo rule.

### M10. Phương pháp và reproducibility (phần threats, không phải đóng góp chính)

> Test adjacency phải làm trong structural equation của skeleton, vì test Granger trên reduced form không phải test adjacency hợp lệ. Khi mở lag theo từng cặp, term phải được de-duplicate: một lỗi trùng term đã làm giảm một nửa hệ số trong mọi run missing của version round 1, và đảo kết luận "targeted thua ở T lớn". Seed của các method built-in phụ thuộc vị trí cell trong config (bug E1, không sửa trước run xác nhận). Mọi test chỉ ghép cặp trong chính một config; với spec P7, các row được giữ đúng vị trí cell bằng một wrapper.

---

## 3. Kế hoạch run P4-H2 cuối cùng (chờ người dùng duyệt)

### 3.1 Bảng spec

Mọi đường dẫn đều tương đối với `/Users/kietnt/Desktop/Workspace/Paper4_UIT`. Thời gian là ước lượng với `--workers 3`.

| # | Vai trò | Method | Config | Analyzer (+ guard riêng) | Spec manifest | Rule xác nhận (tóm tắt; nguyên văn ở doc owner) | Thời gian | Kiểm chứng |
|---|---|---|---|---|---|---|---|---|
| **P1** | **primary** (chế độ có khai báo; quyết định module of record) | `tolerant_v5_1` vs `tolerant_v4` | `experiments/configs/ext_v51fix_p4h2.json` (a2 grid T 40/80/150, 7 cell, 3 rep, n_boot 199, seed_base 20261102; frozen `experiments/ext/v51/frozen_v4_v51.json`) | `experiments/ext/v51fix/rule_p4h2_v2.py` (+ `preflight_p4h2.py`) | `experiments/ext/v51fix/p4h2_spec_files.json` | CONFIRMED khi tất cả đều đúng: V1–V6; failure v5_1 ≤ 12/1260 và ≤ 3/60 mỗi cell rule, cell có 0 run ok thì trượt; **C1**: T40 missing-0.2/0.5 có coverage ITT ≥ 0.90 và cận trên CI 95% (topology bootstrap 1000, seed 0) của (v5_1 − v4) < 0; **C2**: 12 damaged cell T80/150 có coverage ITT ≥ 0.90 và IS ≤ 1.05 × v4; **C3**: 7 cell còn lại có IS ≤ 1.05 × v4 (docs/ext/v51fix.md mục 3) | khoảng 11 phút (tới 20); 2520 row | partly → đủ khi có lead guard (G1–G4, G8) và lệnh `cd` |
| **P2** | **primary** (chế độ không khai báo) | `tolerant_auto3` vs `tolerant_v4` (+ `plugin`; config 2 có thêm `oracle`) | `experiments/configs/ext_auto3fix_p4h2_auto3.json` (C1–C3, có GES) và `experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json` (L1) | `experiments/ext/auto3fix/check_p4h2_v2.py` (+ `preflight_p4h2.py`) | `experiments/ext/auto3fix/p4h2_spec_files.json` | CONFIRMED khi tất cả đều đúng: **C1**: coverage (failed = uncovered) ≥ 0.90 ở 8 cell missing/reversed T80/150; **C2**: IS cell none ≤ 1.35 × v4 ở T40/80/150; **C3**: GES T80/150 có coverage ≥ 0.90 và IS ≤ 1.10 × v4; **L1**: latent1 có coverage ≥ 0.90 ở missing-0.2/reversed-0.2 T80/150. Thêm: I1–I5 đạt (**I4 theo analyzer**, mục 1.3a), cell trượt khi có > 3/60 run hỏng, IS ghép cặp ≥ 57 unit, preflight in PREFLIGHT OK (docs/ext/auto3fix.md mục 1.1 và 6) | khoảng 13–18 phút + 7–11 phút | holds (4 việc cho lead đã đưa vào kế hoạch) |
| **P7-v5_1** | **primary** (claim baseline chính) | `tolerant_v5_1` vs 7 baseline | `experiments/configs/ext_baselines3_p4h2.json` (T 80/150, chỉ tính missing-0.2/0.5 nhưng giữ vị trí cell của a2, 3 rep, n_boot 199, `skip_calibration`; frozen `experiments/ext/baselines3/frozen_calibration_p7.json`), chạy qua `experiments/ext/baselines3/run_cells.py` | `experiments/ext/baselines3/analyze_p4h2.py` (+ `analyze.py`, `p7_win_set.json`; B = 20000) | `experiments/ext/baselines3/p4h2_spec_files.json` | CONFIRMED khi tất cả đều đúng: (i) coverage ≥ 0.90 ở 4/4 cell (run thất bại tính là không cover); (ii) failure ≤ 2% mỗi cell và mọi validity check đạt; (iii) cả 27 so sánh trong W_D07(v5_1) là W theo Holm hai phía 0.05 trên 56 so sánh; (iv) 0/28 L (docs/ext/baselines3.md mục 3.5 và 6, docstring của analyzer) | khoảng 22–30 phút (tới 45); 2400 row (một run chung cho cả hai phần) | holds |
| **P7-v4** | **secondary** (falsification test, không đổi module of record) | `tolerant_v4` vs 7 baseline | cùng run P7 | cùng analyzer | cùng manifest | cùng rule, với W_D07(v4) gồm 19 so sánh. Dry run D-07 cho NOT CONFIRMED do (iv) | (cùng run) | holds |
| P3 | ~~secondary~~ **LOẠI** | flag RQ4.4 | `ext_revlag3_p4h2.json` | `analyze_flag_p4h2_v2.py` | **không có** | — | — | partly: spec chưa đủ |
| P4 | ~~secondary~~ **LOẠI** | `tolerant_v4L` | (cùng run P3) | `analyze_lag_p4h2_v2.py` | **không có** | — | — | partly: spec chưa đủ |
| P5 | ~~secondary~~ **LOẠI** | v4 vs 3 TLP | `ext_tlp3_p4h2.json` | `experiments/ext/tlp3/analyze_p4h2.py` | `experiments/ext/tlp3/p4h2_spec_files.json` | — | (70–90 phút) | partly: lỗi (a)(b) chưa sửa |
| P6 | **LOẠI** | — | `ext_baselines2_p4h2.json` | — | — | — | — | bị P7 thay thế |
| — | **không vào** | v4c, eiv2, auto5 | — | — | — | — | — | v4c bị v5_1 bao trùm; eiv2, auto5 bị loại theo rule |

**Manifest chung của kế hoạch:** `experiments/ext/synthesis_round3/p4h2_plan_files.json`, freeze lúc 2026-11-02T07:48:20Z, sha256 `235d0815…3639d85`. File này gồm:
- 62 file kèm sha256: toàn bộ 26 file `src/paper4/*.py`, `experiments/run_experiment.py`, mọi file của ba spec manifest, ba spec manifest, file hash lúc viết của P2, ba doc owner, bốn config và `v4_identity.py`;
- danh sách lệnh, output dir, và các spec bị loại.

Lead guard: `experiments/ext/synthesis_round3/lead_guard.py`, sha256 `cc491e37…50fc8c6`. Check mô tả sau run: `experiments/ext/synthesis_round3/v4_identity.py`, sha256 `22315561…92893062f`. Lúc freeze, mọi 107 hash do chính các owner ghi lúc freeze (P7 37, P1 30, P2 40) đều khớp file hiện tại.

### 3.2 Spec bị loại và điều kiện để vào lại

- **P3/P4 (revlag3):** thiếu spec manifest; thiếu mục spec và rule trong doc (bản nháp còn placeholder); interpreter chưa ghim; check nhất quán trỏ vào run đã bị thay thế.
- **P5 (tlp3):** doc và analyzer bất đồng về coverage khi mọi method cùng thất bại (lỗi (a)); check realisation trỏ vào `ext_v51_p4h2` (lỗi (b)); manifest thiếu `ext_v51fix.py`; câu paper chưa nói TLP không calibrate. P5 cũng cần thêm 70–90 phút, vượt xa hard rule 5.

**Lead quyết định loại cả ba**, và không để owner sửa trong lúc chờ duyệt. Lý do là P4-H2 chỉ dùng được một lần, và một spec sửa vội mà chưa được kiểm chứng sẽ là điểm yếu lớn hơn một claim exploratory được nói thẳng. Muốn đưa một spec trở lại thì cần đủ bốn điều, theo thứ tự:
1. Owner sửa bằng file mới.
2. Một verifier độc lập kiểm lại.
3. Lead freeze lại `p4h2_plan_files.json` (lệnh `--freeze`) và cập nhật mục này.
4. Người dùng duyệt lại.

Nếu không, các claim M4 (phần ngoài cell missing), M5 (comparator và lag) và M8 **mãi chỉ là exploratory**. Sau run này không còn bank sạch, nên paper phải ghi điều đó rõ ràng.

### 3.3 Lead guard (G1–G8): các lỗ hổng spec mà verifier giao cho lead

| Check | Nội dung | Che lỗ hổng nào |
|---|---|---|
| G1 | interpreter = `/Users/kietnt/miniconda3/bin/python` với numpy 2.5.4; cwd = repo root | P1 (d), P2 (d), P7 (interpreter của spec) |
| G2 | `PAPER4_TOPOLOGY_ROOT`, `PAPER4_ACIIDS_ROOT` unset | P1 (b), P2 (d) |
| G3 | tập `src/paper4/*.py` bằng đúng tập đã freeze (26 file); có file mới hoặc thiếu file thì FAIL | P1 (a), P2 (b), P7 caveat (2) (E4: module mới có thể monkeypatch code chung) |
| G4 | 62 file của kế hoạch có hash bằng lúc freeze kế hoạch | P1 (a), P7 caveat (1) (doc rule của P7 nay đã được hash) |
| G5 | mỗi file vẫn có hash bằng hash **chính owner** ghi lúc freeze (P7 37/37, P1 30/30, P2 40/40) | P2 (c) (không đổi kể từ lúc được kiểm chứng) |
| G6 | bốn config P4-H2 đều là P4-H2/confirmatory với seed_base 20261102 | — |
| G7 | trước run: không output dir nào của spec vào, spec bị thay thế hay spec bị loại tồn tại, và không `results/*/manifest.json` nào mang bank P4-H2. Sau run: đúng 4 run dir có manifest P4-H2 | P7 caveat (3) (`run_cells.py` dùng `exist_ok`), P1 (run cũ không được chạy) |
| G8 | sha256 của `data/topology_bank/P4-H2/p4h2_manifest.json` bằng `0b7e6579…aaa1c7d8` ghi trong PROVENANCE.md (chỉ đọc raw bytes) | P1 (c); bank manifest mà mọi spec giao cho lead |

**Đã tự test, không chạm P4-H2.** Ở chế độ `--test` (bỏ G8), guard PASS. Ba negative test cho FAIL đúng như mong đợi:
- set `PAPER4_TOPOLOGY_ROOT` → G2 FAIL;
- plan bị sửa → G3 và G4 FAIL;
- phase post khi chưa có run → G7 FAIL.

`v4_identity.py` chạy trên các run D-07 tương ứng cho 0 mismatch ở 1260/240/240 row. Kết quả lưu ở `results/ext_synthesis_round3_guardtest/` và `results/ext_synthesis_round3_selftest/`.

### 3.4 Chuỗi lệnh (đúng thứ tự, mỗi lệnh chạy đúng một lần)

```bash
cd /Users/kietnt/Desktop/Workspace/Paper4_UIT
unset PAPER4_TOPOLOGY_ROOT PAPER4_ACIIDS_ROOT
PY=/Users/kietnt/miniconda3/bin/python
L=results/ext_synthesis_round3_p4h2_logs; mkdir -p $L

# 0. (lead, tay) append mục "recorded before running" vào docs/decision_rules.md (mục 3.9) — TRƯỚC lệnh 1.

# 1. Lead guard, phase pre: phải in LEAD GUARD PASS, exit 0. FAIL thì dừng và báo người dùng.
$PY experiments/ext/synthesis_round3/lead_guard.py --phase pre

# 2. Preflight P1: phải in PREFLIGHT PASS, exit 0.
$PY experiments/ext/v51fix/preflight_p4h2.py

# 3. Preflight P2 với file hash lúc viết spec: phải in PREFLIGHT OK.
$PY experiments/ext/auto3fix/preflight_p4h2.py --hashes results/ext_auto3fix_dryrun/spec_sha256_at_writing.txt --out results/ext_auto3fix_p4h2_check_preflight.json

# 4. P1 run (khoảng 11 phút)
$PY experiments/run_experiment.py --config experiments/configs/ext_v51fix_p4h2.json --workers 3 > $L/04_p1.log 2>&1; echo "exit $?"
# 5. P2 config 1 (khoảng 13–18 phút)
$PY experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3.json --workers 3 > $L/05_p2c1.log 2>&1; echo "exit $?"
# 6. P2 config 2 (khoảng 7–11 phút)
$PY experiments/run_experiment.py --config experiments/configs/ext_auto3fix_p4h2_auto3_latent1.json --workers 3 > $L/06_p2c2.log 2>&1; echo "exit $?"
# 7. P7 qua wrapper giữ vị trí cell (khoảng 22–30 phút)
$PY experiments/ext/baselines3/run_cells.py --config experiments/configs/ext_baselines3_p4h2.json --workers 3 > $L/07_p7.log 2>&1; echo "exit $?"

# 8. Lead guard, phase post: code không đổi trong lúc chạy; đúng 4 run dir có manifest P4-H2.
$PY experiments/ext/synthesis_round3/lead_guard.py --phase post

# 9–11. Analyzer (chỉ chạy sau khi cả 4 run xong; không mở output nào trước bước này)
$PY experiments/ext/v51fix/rule_p4h2_v2.py      > $L/09_p1_rule.log 2>&1   # -> results/ext_v51fix_p4h2/ruling_v2.{md,json}
$PY experiments/ext/auto3fix/check_p4h2_v2.py   > $L/10_p2_check.log 2>&1  # -> results/ext_auto3fix_p4h2_check/check.{md,json}
$PY experiments/ext/baselines3/analyze_p4h2.py  > $L/11_p7_rule.log 2>&1   # -> results/ext_baselines3_p4h2/ruling.{md,json}

# 12. Check mô tả E1 (không đổi verdict nào)
$PY experiments/ext/synthesis_round3/v4_identity.py > $L/12_identity.log 2>&1   # -> results/ext_synthesis_round3_p4h2_v4identity/

# 13. (lead, tay) append mục "Outcome" vào docs/decision_rules.md, chép verdict nguyên văn (mục 3.9).
```

Quy tắc khi chạy:
- Không chạy song song. Không có job nặng nào khác trong lúc chạy, vì load chỉ ảnh hưởng thời gian, không ảnh hưởng kết quả.
- Từ bước 4 đến bước 8, chỉ được đọc exit code và dòng cuối của log, không đọc `summary.md`.
- Không có bước nào được chạy hai lần, trừ trường hợp ở mục 3.7.

### 3.5 Tổng thời gian

| Bước | Ước lượng (`--workers 3`) | Nguồn ước lượng |
|---|---|---|
| 1–3 guard + preflight | khoảng 1–2 phút | self-test của lead; preflight < 30 s |
| 4 P1 | khoảng 11 phút (tới 20) | 647 s cho cùng config trên D-07 |
| 5–6 P2 | khoảng 20–30 phút | ext_gate_auto3 mất 1027.6 s trên D-07 dưới load nặng |
| 7 P7 | khoảng 22–30 phút (tới 45) | 954 s trên D-07 cộng `tlp2_db_p3`; ngoại suy từ smoke của verifier ra 22–25 phút |
| 8–12 guard post, analyzer, identity | khoảng 3–5 phút | analyzer P7 với B = 20000 khoảng 1 phút |
| **Tổng** | **khoảng 60–75 phút; tới khoảng 100 phút nếu máy bị chia** | |

Run P7 và tổng thời gian đều vượt mức "khoảng 30 phút" của hard rule 5. Vì đây là run một lần, **cần người dùng duyệt ngoại lệ** (R3-0). Kế hoạch này nhẹ hơn kế hoạch vòng 2 (hơn 2 giờ), vì P5 bị loại và P3/P4 không vào.

### 3.6 Multiplicity giữa các primary spec (quyết định, ghi trước P4-H2)

1. **Vai trò.**
   - Primary: P1, P2 và P7-v5_1.
   - Secondary: P7-v4 (falsification test).

   Mọi kết quả đều được báo, kể cả NOT CONFIRMED và phần secondary; không báo chọn lọc.
2. **Bên trong một spec.** Giữ đúng như đã freeze. Mỗi spec là một intersection-union test. P7 dùng Holm trên 56 so sánh; mức này bảo thủ hơn mức một IUT cần, và được giữ vì R3-1 yêu cầu.
3. **Giữa các primary spec.**
   - **Verdict chính thức** của mỗi spec là rule đã freeze ở mức ghi trong spec (0.05). Lý do: cả hai owner đã ghi điều này vào rule frozen của mình (baselines3.md mục 3.5, v51fix.md mục 3), theo synthesis vòng 2 mục 3.3. Đổi mức sau khi owner đã xem dry run D-07 sẽ là sửa rule đã đăng ký. Hơn nữa, mỗi primary claim dẫn tới một quyết định riêng: P1 quyết định module of record, P7 quyết định claim baseline, P2 quyết định chế độ auto. Mỗi quyết định được kiểm soát ở mức 0.05 của chính nó.
   - **Overlay Bonferroni** bắt buộc báo cạnh mỗi verdict. Số primary claim có thành phần p-value là k = 2: P1-C1 và P7-v5_1. P2 là rule theo point estimate nên không tính; P7-v4 là secondary nên không tính. Vì vậy α = 0.025 cho mỗi claim:
     - P1-C1 dùng CI 97.5%, analyzer đã in sẵn. Dòng 98.33% (k = 3) mà analyzer cũng in **bị bỏ qua**, vì k đã được cố định là 2 ở đây.
     - P7-v5_1 dùng cùng rule với Holm ở mức 0.025 trên 56 so sánh, B = 20000; analyzer đã in sẵn.
4. **Cách viết trong paper.**
   - Đạt ở cả hai mức: viết "xác nhận trên bank niêm phong P4-H2, kể cả sau hiệu chỉnh Bonferroni qua hai primary claim".
   - Chỉ đạt ở mức 0.05: viết "đạt rule ghi trước ở mức 0.05, nhưng không còn đạt sau hiệu chỉnh Bonferroni qua hai primary claim". Abstract và phần contribution không được dùng chữ "xác nhận" mà bỏ qua vế sau.
   - Module of record đi theo verdict chính thức của P1 (cam kết vòng 2).
5. **P2.** CONFIRMED nghĩa là "tiêu chí point estimate ghi trước giữ trên bank niêm phong", không phải một test có kiểm soát sai lầm loại I. Holm trên 14 cell coverage được báo kèm. Câu về độ mong manh (auto3fix.md mục 1.2) phải đi kèm.
6. **Các thống kê "báo kèm"** của từng analyzer (Holm của C1 trong P1, số cell coverage < 0.90 có ý nghĩa, coverage theo định nghĩa cũ của P2, …) chỉ là mô tả, không đổi verdict.

### 3.7 Quy tắc dừng, gián đoạn và lỗi

- Lead guard pre hoặc một preflight FAIL thì **không chạy gì**. Ghi lý do vào decision_rules.md và báo người dùng. P4-H2 vẫn còn nguyên.
- Một run bị gián đoạn trước khi có `runs.jsonl` (runner chỉ ghi file này ở cuối) thì:
  - đổi tên thư mục dở thành `<run dir>_aborted1` (không xoá);
  - chạy lại **một lần**, đúng lệnh và config cũ;
  - công bố việc này.

  Sau lần chạy lại, guard pre không chạy lại (nó từ chối chạy khi đã có `pre.json`). Phase post vẫn kiểm đủ.
- Nếu một method raise exception thay vì trả về failed result, runner crash, và lần chạy lại với cùng seed sẽ crash y hệt. Khi đó spec đó là **NOT CONFIRMED (incomplete)** và được báo như vậy. Không sửa code và không chạy lần thứ ba.
- Nếu guard post FAIL (code đổi trong lúc chạy, hoặc có manifest P4-H2 lạ): vẫn chạy analyzer, nhưng mọi verdict bị gắn nhãn **INVALID (integrity)** và báo người dùng trước khi viết bất cứ câu nào vào paper.

### 3.8 Hệ quả của bug E1 (không sửa, theo quyết định của người dùng)

- Seed của built-in method đi theo vị trí cell (c_idx). Vì vậy **bảng v4 trên P4-H2 của paper lấy từ run P1** (`ext_v51fix_p4h2`, đủ grid a2).
- Config 1 của P2 có cùng thứ tự cell cho 7 cell đầu (GES nằm cuối), nên row v4 của nó phải trùng P1 ở các cell chung.
- P7 giữ vị trí cell bằng wrapper, nên row v4 và v5_1 của nó phải trùng P1 ở T80/150 missing.
- Config 2 của P2 (latent1) là một realisation khác ở mọi damaged cell.
- `v4_identity.py` (bước 12) kiểm các dự đoán trên. Trên D-07 chúng đúng: 1260/1260, 240/240 và 240/240.
- Mismatch là một phát hiện reproducibility phải công bố, nhưng **không đổi verdict nào**, vì mọi test chỉ ghép cặp trong chính run của nó.
- Chạy P7 bằng runner trực tiếp, thay vì qua `run_cells.py`, sẽ dịch c_idx và cho một realisation khác. Lệnh ở mục 3.4 luôn dùng wrapper.
- Sau P4-H2, việc sửa E1 (R3-11) phải là một runner có version mới, kèm regression check. Kết quả P4-H2 chỉ tái lập được bằng runner hiện tại; hash của nó là `2255693c…4c39d8`.

### 3.9 Ghi log vào docs/decision_rules.md

Lead chỉ append, đúng hai mục: một trước bước 1 và một sau bước 12. Mục thứ nhất được ghi sau khi người dùng duyệt. File này viết bằng tiếng Anh, nên phần append cũng bằng tiếng Anh. Nội dung tối thiểu như sau.

**(A) Trước run: "P4-H2 confirmatory run (round 3), recorded before running"**
- Ai duyệt và lúc nào (UTC).
- Spec vào và vai trò: P1, P2, P7-v5_1 là primary; P7-v4 là secondary. Spec bị loại và lý do: P3/P4, P5, P6.
- Đường dẫn và sha256 của: `experiments/ext/synthesis_round3/p4h2_plan_files.json`, `lead_guard.py`, `v4_identity.py`, và tài liệu này (`docs/ext/synthesis_round3.md`).
- Mười ba lệnh của mục 3.4, nguyên văn.
- Quyết định multiplicity (mục 3.6), nguyên văn điểm 3–5.
- Cách đọc kết quả (mục 3.10): module of record theo P1; chế độ auto theo P2; claim baseline theo P7-v5_1.
- Câu E1 (mục 3.8) và quy tắc dừng (mục 3.7).
- Câu về độ mong manh của P2 (auto3fix.md mục 1.2) và câu về rủi ro ITT của P1: "một run thất bại có thể lật C1 hoặc C2 ở 4 cell".
- Bổ sung split usage còn nợ (E10): các run vòng 2 và vòng 3 trên D-07/D-07H, chỉ trỏ tới synthesis_round2.md và synthesis_round3.md, kể cả run `--workers 6` của v4c.

**(B) Sau run: "Outcome of the P4-H2 confirmatory run"**
- Thời điểm UTC bắt đầu và kết thúc của từng lệnh; `seconds` và `n_rows` từ từng manifest.
- Kết quả guard pre và post (PASS/FAIL), cùng sha256 của `hashes_pre.txt` và `hashes_post.txt`.
- Số run thất bại theo method và cell.
- **Verdict nguyên văn** của ba analyzer, gồm cả dòng overlay Bonferroni (P1-C1 97.5%; P7 Holm 0.025).
- Kết quả `v4_identity.py`.
- Mọi lệch quy trình: chạy lại theo mục 3.7, crash.
- Module of record sau run (theo bảng 3.10).
- **Split usage:** "P4-H2 confirmatory used once on <date>. Every split of D-07H, D-07, P4-H1 and P4-H2 confirmatory is now used; any further confirmatory claim (including P3/P4/P5) needs a new bank."

### 3.10 Ý nghĩa của từng kết quả

| Spec | CONFIRMED | NOT CONFIRMED |
|---|---|---|
| **P1** (primary) | **Module of record ở chế độ có khai báo đổi thành `tolerant_v5_1`** (cam kết vòng 2). Câu P4-H2 cho M2: "Trên bank niêm phong P4-H2 (spec ghi trước, chạy một lần), `tolerant_v5_1` giữ coverage ≥ 0.90 ở 14 cell có cổng, có interval score thấp hơn v4 ở T40 missing (CI 95% [số]), và không vượt 1.05 × v4 ở cell nào" (+ vế Bonferroni theo mục 3.6). v4 được mô tả là phiên bản frozen trước đó và là một mốc của ablation. | `tolerant_v4` vẫn là module of record. Kết quả T40 của v5_1 chỉ được báo là exploratory, và phải nói rõ điều kiện nào trượt (V/F/C1/C2/C3). Nếu chỉ trượt vì một run thất bại dưới ITT, vẫn là NOT CONFIRMED; cơ chế đó được nêu như rủi ro đã ghi trước, không được dùng để biện hộ. |
| **P2** (primary) | `tolerant_auto3` là module of record của chế độ không khai báo. Câu M3 thêm: "trên P4-H2, tiêu chí point estimate ghi trước (C1–C3, L1) giữ", kèm câu về độ mong manh. | Claim C-auto chỉ còn exploratory (D-07). Paper trình bày chế độ có khai báo là chế độ chính. Câu về độ mong manh giải thích rằng việc trượt riêng ở T80 reversed-0.5 không phải bằng chứng auto3 tệ đi. |
| **P7-v5_1** (primary) | M1 thêm câu: "Trên P4-H2, cả 27 so sánh thắng của D-07 đều thắng lại sau Holm trên 56 và không so sánh nào thua; coverage [số]" (+ vế Bonferroni). Chỉ được nói "xác nhận" cho 27 so sánh này và 4 cell này. | Claim baseline của paper chỉ còn exploratory (câu M1, điều kiện (iv)). Phải báo điều kiện nào trượt. Nếu trượt (iii) ở một so sánh, ví dụ T150 m0.2 so với `pselect_union_v3_cal` (−0.15 [−0.23, −0.07] trên D-07, so sánh sát nhất), thì viết "không tái lập được ở so sánh …". Nếu trượt (iv), câu "không baseline nào tốt hơn" bị rút ở cell đó. |
| **P7-v4** (secondary) | Báo đúng như vậy, và nói thêm rằng trên D-07 v4 đã thua ở T150 m0.5. Kết quả này không làm câu D-07 mạnh lên. | **Kết quả mong đợi.** Nó xác nhận rằng v4 frozen không giữ được "không thua" trước envelope đủ budget. Câu D-07 về v4 trong M1 được giữ. |

**Kết hợp với module of record:**
- P1 C + P7-v5_1 C: paper có claim chính đã xác nhận cho chính module of record.
- P1 C + P7-v5_1 NC: v5_1 vẫn là module of record, vì P1 là tiêu chí thay v4; claim baseline chỉ còn exploratory.
- P1 NC + P7-v5_1 C: v4 vẫn là module of record. Kết quả baseline đã xác nhận được báo như thuộc tính của biến thể v5_1, và **không** được viết thành claim về module of record.
- Cả hai NC: mọi claim chính là exploratory. Paper đóng khung như một nghiên cứu exploratory, kèm một lần xác nhận thất bại được báo đầy đủ.

### 3.11 Người dùng cần duyệt (R3-0)

1. Chạy P4-H2 **một lần** với P1, P2 (hai config) và P7, theo đúng 13 lệnh ở mục 3.4.
2. Ngoại lệ thời gian: khoảng 60–75 phút, tới khoảng 100 phút.
3. Loại P3/P4 và P5. Hệ quả: các claim RQ4.4, lag v4L, comparator reversal và TLP ngoài cell missing mãi chỉ là exploratory. Lựa chọn khác là mở thêm một vòng ngắn để sửa và kiểm chứng (mục 3.2), và hoãn P4-H2 tới lúc đó.
4. Quyết định multiplicity ở mục 3.6.
5. Hệ quả E1 ở mục 3.8, và bảng ý nghĩa kết quả ở mục 3.10.

---

## 4. Điểm yếu còn lại (cho phần limitations)

1. **Một bank dùng lại nhiều lần, và chỉ một bank sạch.** D-07 development đã định hình v4, v5, v5_1, auto3, các ngưỡng và flag. P4-H2 được chia cho 3 primary claim. Các claim RQ4.4, lag, reversal comparator và TLP (ngoài cell missing) không có bản xác nhận. Đây vẫn là garden of forking paths, chỉ được giảm nhờ pre-registration và một lần chạy duy nhất.
2. **Fidelity, budget và calibration của baseline.**
   - Mọi baseline mạnh đều là bản chuyển thể của nhóm.
   - Baseline mạnh nhất dùng gấp 32 lần số draw của v5_1, và calibration hai phía của nó do nhóm thêm.
   - Grid của v4 frozen chỉ widen được. Sau khi so sánh thì calibration cũng bất đối xứng.
   - TLP trong P5/M4 không calibrate; `tlp2_lp_cal` chỉ widen được.
   - Envelope ngoài T80/150 missing không có pselect đủ budget, và chọn X trên chính D-07 thì có winner's curse.
   - Row đã lưu của bốn baseline trước B1 không tái lập bit-for-bit với runner hiện tại.
3. **Biên coverage mỏng, ít cluster, và ITT.**
   - Với 20 topology, CI coverage của một cell khoảng ±0.03.
   - v5_1 có 4 cell ở mức 0.918–0.927, và một run thất bại có thể lật C1/C2.
   - auto3 có 0.903 ở T80 reversed-0.5, và P(CONFIRMED) ≈ 0.62–0.65 là con số lạc quan.
   - eiv2 có 0.897.
   - "Không cell nào dưới 0.90 có ý nghĩa" không có nghĩa là đạt.
4. **Thất bại thật ở T nhỏ.**
   - T40 extra: BVAR Minnesota đã calibrate tốt hơn cả hai module (Holm).
   - T40 missing: TLP đã calibrate thắng v4, còn v5_1 chỉ hòa.
   - Ở T40 module không có lợi thế nào trước baseline tốt nhất.
5. **T lớn.**
   - Lợi thế của v5_1 ở T150 missing chỉ có khi τ > 4.94. τ đã chọn (6.6083) mong manh: ở 11% seed bootstrap của probe, nó ra khoảng 2.94.
   - v4 thua pselect đủ budget ở T150 missing-0.5.
   - Ở T150 cell extra, mọi phương pháp gần như ngang nhau.
6. **Width.** v4 rộng hơn plugin (1.20–3.61 lần median width) và rộng hơn pselect_v2 trên null pair, nên câu "hẹp hơn" của plan sai. RQ4.2 chỉ đứng ở dạng interval score.
7. **Reversal.**
   - Gap của coverage affected do centering.
   - Comparator khả thi chưa có verdict hợp lệ. Phân tích post hoc ở cùng coverage gợi ý đóng được một phần gap ở rev-0.2, nhưng không có CI.
   - Lag interval chỉ cover 0.66–0.76.
   - 10–20% cạnh đảo ở T80 nằm ngoài pool của module.
8. **Measurement noise.** Noise 30% chưa giải quyết được: eiv2 bị loại, Holm 7/12. Dưới noise0.1, v5_1 yếu hơn v4.
9. **Reproducibility và quy trình.**
   - Bug E1 không được sửa: realisation phụ thuộc danh sách cell, và P7 cần wrapper.
   - Bug E4: runner import mọi ext.
   - Một bug trùng term đã đảo một kết luận của vòng 1.
   - Một run được chạy với `--workers 6`, kèm đổi interpreter; đã kiểm là không đổi row trên 2/60 unit.
   - Row cũ không tái lập được sau B1.
   - Có các lần sửa tại chỗ trong khối vừa append, và hai mục chỉ có nguồn từ transcript.
   - B của analyzer P7 được đổi sau khi có kết quả D-07: lỗi phân giải p làm overlay Bonferroni ở D-07 vô hiệu.
   - Tất cả đều đã công bố. Code và hash được khoá cho run P4-H2.
10. **Phạm vi.** Chỉ có SVAR tuyến tính Gaussian, 14 nút, một generator và một mô hình damage. Flag RQ4.4 chỉ generalise sang seed mới.
11. **RQ4.4.** Không có AUROC cho auto3/v5_1 (R3-9). Ở T40, 1/width gần như bằng flag; trên GES T40 flag thua 1/width.
12. **Ý nghĩa thống kê của các claim.** "Hòa" không phải non-inferiority. P2 là rule theo point estimate. Holm trên 56 trong P7 bảo thủ. Với k = 2, overlay Bonferroni chỉ kiểm soát primary claim có p-value.
13. **Kiểm chứng v4c còn giới hạn.** Chỉ 2/60 unit được chạy lại. Ba đếm phần B phụ thuộc seed bootstrap, và dung sai CI bị vượt ở 56/252 cell.
14. **R3-8 chưa có verifier riêng.** Số mới của bảng 1b, 2, 3, 4b và 5 cần được kiểm lại trước khi nộp. Ít nhất phải chạy lại `build_tables.py` và so một mẫu cell bằng code độc lập.

---

## 5. Bug và ghi chú mới của vòng 3 (chỉ báo, không sửa file có sẵn)

| # | File | Vấn đề | Xử lý |
|---|---|---|---|
| N1 | `experiments/ext/baselines3/run_cells.py` | `mkdir(exist_ok=True)`, không chặn chạy lần hai vào cùng thư mục | lead guard G7 |
| N2 | `experiments/ext/v51fix/preflight_p4h2.py`, `experiments/ext/auto3fix/preflight_p4h2.py`, `experiments/ext/tlp3/preflight.py` | ghi hash ext nhưng không so với lúc freeze; không báo lỗi khi có `ext_*.py` mới | lead guard G3–G5 |
| N3 | `experiments/ext/revlag3/run_pairs3.py` | oracle được fit ở cell đánh giá đầu tiên, nên rng mang c_idx của cell đó (hệ quả kiểu E1); chỉ so `_FROZEN` theo giá trị | ghi vào doc revlag3; P3/P4 bị loại |
| N4 | `experiments/ext/revlag3/analyze_flag_p4h2_v2.py`, `experiments/ext/tlp3/analyze_p4h2.py` | hard-code `ext_v51_p4h2`, run đã bị thay thế | spec bị loại |
| N5 | `experiments/ext/tlp3/analyze_p4h2.py` | unit mà mọi method cùng thất bại bị bỏ khỏi mẫu số coverage, khác với text doc | spec bị loại |
| N6 | `docs/ext/auto3fix.md` mục 1.1 | định nghĩa I4 cũ, đã sai | mục 1.3a ở trên: analyzer có hiệu lực |
| N7 | `src/paper4/ext_baselines3.py` | member được giữ khi có ≥ 49 draw hợp lệ, nên "199 draw" chỉ là con số yêu cầu | sửa lời (M1) |
| N8 | analyzer dùng p bootstrap (1 + #)/(B + 1) | Holm trên family lớn cần B > 2m/α | P7 dùng B = 20000; các analyzer khác phải kiểm điều này nếu dùng lại |
| N9 | runner (E1–E11 của vòng 2) | còn mở | R3-11 sau P4-H2, dùng runner có version mới kèm regression check |

---

## 6. File của lead vòng 3

- `docs/ext/synthesis_round3.md`: tài liệu này.
- `experiments/ext/synthesis_round3/lead_guard.py`: G1–G8; `--freeze` để freeze lại kế hoạch, `--test` để tự test mà không chạm P4-H2.
- `experiments/ext/synthesis_round3/v4_identity.py`: check E1 mô tả sau run.
- `experiments/ext/synthesis_round3/p4h2_plan_files.json`: manifest chung của kế hoạch (62 file, lệnh, output, spec bị loại).
- `results/ext_synthesis_round3_guardtest/{pre.json, post.json, hashes_*.txt}`: self-test của guard (pre PASS; post FAIL đúng như mong đợi vì chưa có run).
- `results/ext_synthesis_round3_selftest/{v4identity_d07/v4_identity.json, doctored_plan.json}`: self-test của identity check trên D-07 (0/1260, 0/240, 0/240 mismatch) và negative test của G3/G4.

Không file có sẵn nào bị sửa. Không git commit. Không LLM call. Không chạm P4-H1, P4-H2 hay confirmatory split nào.
