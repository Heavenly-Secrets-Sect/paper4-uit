# Tổng hợp vòng 1: sáu hướng song song và phần kiểm chứng độc lập

**Trạng thái.** Bản tổng hợp của team lead sau vòng 1. Mọi kết quả ở đây là **exploratory, chỉ trên D-07 development** (seed_base 20261102). Calibration dùng D-07H development. Không hướng nào dùng confirmatory split hay P4-H1. Mỗi hướng có một agent "skeptic" kiểm chứng độc lập: tính lại số từ `runs.jsonl`, đối chiếu thời điểm ghi rule với thời điểm chạy qua transcript, chạy thử implementation trên ví dụ nhỏ biết truth. Mọi con số dưới đây lấy từ file kết quả của từng hướng hoặc từ script của verifier (đường dẫn ở cuối mỗi mục).

**Module of record: vẫn là `tolerant_v4` (frozen).** Vòng 1 không có version nào thay được nó theo rule ghi trước. `tolerant_auto3` (hướng `gate`) **đạt** rule B1, nhưng nó là một chế độ khác: không cần khai báo mức hỏng. Nó không thay v4 ở chế độ có khai báo (xem mục 3).

Ngoài phạm vi bản này: hai hướng `textinfo` và `llm` (docs/ext/textinfo.md, docs/ext/llm.md) có verifier riêng và không thuộc sáu kết quả được giao cho vòng tổng hợp này.

---

## 1. Từng hướng: phần đứng vững và phần không

### 1.1 `narrow`: `tolerant_v5` làm hẹp interval ở T nhỏ

**Verdict theo rule: LOẠI.** Điều kiện 1 đạt 2/2, điều kiện 3 đạt 7/7. Điều kiện 2 chỉ đạt 11/12: ở T150 missing-0.5, IS ratio v5/v4 là 1.054, vượt ngưỡng 1.05. Verifier xác nhận verdict đi ra máy móc từ rule. Rule được ghi lúc 18:33:34Z, eval khởi chạy lúc 18:33:40Z, và rule không bị sửa sau đó.

**Đứng vững (verifier tính lại với seed khác, B = 2000):**
- T40 missing-0.2: v4 0.983/7.77 → v5 0.933/4.79, paired v5−v4 −2.98 [−3.44, −2.47].
- T40 missing-0.5: v4 0.978/7.53 → v5 0.944/5.12, paired −2.41 [−2.76, −2.06].
- Cell bị loại (T150 missing-0.5): 2.215 → 2.335, paired +0.12 [−0.02, +0.25]. CI chứa 0, nên **việc bị loại là sự kiện ở mức nhiễu**, không phải bằng chứng v5 gây hại thật ở T150.
- So với `pselect_union` theo rule kiểu A2b: v5 thắng 18/18 damaged cell, v4 thắng 16/18.
- Pairing đúng: 1260/1260 dòng `tolerant_v4` trùng hệ với `a2b_pselect`.
- Không rò truth. Implementation đúng: block F bằng nested-OLS F, và trên SVAR 4 nút các cạnh bị xoá được xếp hạng 1.
- Ablation ở T40 missing-0.2: v4 7.77 → `v5_cal2` 7.01 → `v5_sel` 5.34 → v5 4.79. Ở T150 missing-0.5, `v5_sel` là +0.25 [+0.03, +0.49] so với v4. Tức là targeted opening chính là phần gây thiệt ở T lớn khi thiếu nhiều cạnh.

**Không đứng vững hoặc phải sửa lời:**
- "Structured damage: v5 thắng v4 11/18" thực ra là **10–11/18 (sát biên)**. Ô T80 shortcut-0.5 đổi dấu khi đổi seed bootstrap.
- GES T40, v5 so với pselect: cận trên +0.02 hay −0.00 tuỳ seed. Đây là **hòa sát biên**.
- "Two-sided calibration một mình cho khoảng −0.6 đến −0.8" phải sửa thành **−0.55 đến −0.76**.
- **Thiếu công bố:** lúc 18:27:12Z có một timing smoke run trên D-07 development (1 topology, 1 replicate, có v5) trước khi ghi rule, và output T40 missing đã hiện ra. Hyperparameter đã được đặt trước khi output xuất hiện, nên verifier không thấy dấu hiệu nó lái thiết kế. Dù vậy, phải bổ sung việc này vào docs/ext/narrow.md.
- Design choice (mult = 3, alpha_open = 0.10) và width calibration dùng cùng bank D-07H development. Điều này đã được công bố.

Nguồn: results/ext_narrow_eval/ruling.md, results/ext_narrow_ablation/summary.md, results/ext_narrow_ges/describe.md, results/ext_narrow_structured/describe.md. Verifier: experiments/ext/verify_narrow/.

### 1.2 `eiv`: `tolerant_eiv` chịu measurement noise

**Verdict theo rule: LOẠI.** Coverage ≥ 0.90 chỉ đạt ở 8/12 noise cell. Bốn cell noise0.3 hụt: T80 none 0.874, T80 reversed 0.885, T150 none 0.895, T150 reversed 0.893. Điều kiện chi phí trên dữ liệu sạch đạt 6/6 (ratio 1.026–1.106, ngưỡng 1.15). Verifier xác nhận rule được ghi 7 giây trước khi chạy, không có leakage, calibration đúng, và cả 36 cặp coverage/IS đều tái lập được.

**Đứng vững:**
- noise0.3 T150: IS tốt hơn v4 có ý nghĩa ở cả 3 cell. none −0.90 [−1.12, −0.68], missing −0.56, reversed −0.79. Coverage tăng từ 0.77–0.83 lên 0.89–0.92.
- noise0.3 T80 missing: eiv **tệ hơn** v4, +0.42 [+0.27, +0.57].
- Trên SVAR 3 nút với T = 40000, corrected LS với D đúng khôi phục truth: 0.700 so với OLS 0.522.

**Không đứng vững:**
- **Chẩn đoán nguyên nhân bị bác.** Tác giả đổ cho weak instruments. Verifier tìm ra nguyên nhân lớn hơn nằm ngay trong code: `estimate_noise_share` đặt `crit[grid > lam] = inf` bên trong vòng lặp qua các phương trình. Như vậy r̂ bị chặn trên bởi min theo **cả 14 phương trình** của lambda_min. Trên đúng dữ liệu probe 2 (D-07H, seed 777):
  - Estimator được đánh giá cho 0.121 (T80) và 0.175 (T150).
  - Estimator probe 2 không có cap cho 0.193 và 0.220.
  - Truth là 0.231.
  - Cap bị chạm ở 5/12 run (T80) và 3/12 run (T150).
  Vậy cap gây phần lớn bias. Weak instruments chỉ giải thích phần còn lại (0.231 → 0.193).
- "Probe 2 lạc quan vì topology được rút" **bị bác**. Probe 2 chạy một hàm khác (`noise_est.gmm_common`). Docstring của ext_eiv.py và câu "probe cho thấy gần unbiased" trong eiv.md gán sai kết quả đó cho estimator được đánh giá.
- "Noise 10%: đã giải quyết (coverage ≥ 0.93)" là **nói quá**. Min coverage là 0.927. v4 vốn đã đạt ≥ 0.90 ở 5/6 cell noise0.1. eiv không tốt hơn v4 có ý nghĩa ở cell noise0.1 nào, và tệ hơn ở T80 missing (+0.73 [+0.44, +1.09]) và T80 reversed (+0.16).
- Chi phí chưa báo cáo: eiv làm tăng |C| trên null pair ở mọi cell, ví dụ noise0.3 T80 none 0.052 → 0.087.
- Mô hình noise D = r·var(y) trùng đúng generator A1, nên đây là trường hợp thuận lợi nhất cho method.

Nguồn: results/ext_eiv_a1noise/rule_check.txt, summary.md. Verifier: experiments/ext/verify_eiv/ (cap_vs_probe.py).

### 1.3 `tlp`: Targeted Local Projections (Nemtyrev & Boldea, arXiv 2603.00248) làm baseline

**Verdict (rule mô tả): v4 thắng `targeted_lp` 13/18 damaged cell (12/12 ở T ≥ 80), TLP thắng 0.** So với bản đã calibrate width `targeted_lp_cal` (bản chuyển thể của nhóm, không phải method đã công bố), v4 vẫn thắng 13/18 và `targeted_lp_cal` thắng 2/18: T40 missing-0.2 và missing-0.5, với coverage 0.953/0.935 và IS 4.75/5.02 so với v4 7.77/7.53. Verifier xác nhận số liệu, pre-registration (rule ghi 30 giây trước khi chạy), pairing 3780/3780 dòng với a2b, và implementation (LP khớp IRF thật trong sai số 0.009 ở T = 2e5).

**Phải sửa lời:**
- "TLP không thắng cell nào" chỉ đúng nhờ cổng coverage ≥ 0.90. Xét riêng proper scoring rule, `targeted_lp` có IS **thấp hơn** v4 có ý nghĩa ở T40 missing: +2.61 [+1.91, +3.27] và +1.65, với coverage 0.864/0.826. Câu viết trong paper phải nói rõ điều này.
- "Double bootstrap faithful, nên simplification không bất lợi cho baseline" chưa được chứng minh. Probe không faithful (B2 = 49, p = 3, mức 95%). Ở T80 none, double bootstrap tốt hơn có ý nghĩa (−0.59 [−1.14, −0.18]), cỡ bằng biên của v4 ở T80 none/extra. Probe bổ sung của verifier ở T = 40 và T80 extra-0.5 (results/ext_verify_tlp_db/) không thấy bất lợi, nên kết luận 12/12 ở T ≥ 80 vẫn đứng.
- "MSE shrinkage của all-lags fit về plugin là cách chữa" mới là **giả thuyết**, chưa có thí nghiệm nào.

Nguồn: results/ext_tlp_eval/tlp_rules.md, summary.md. Verifier: experiments/ext/verify_tlp/.

### 1.4 `gate`: `tolerant_auto3`, B1 bản 3, không cần khai báo mức hỏng

**Verdict theo rule B1 (không đổi so với decision_rules.md): GIỮ.** C1, C2 (ở cả T = 40/80/150) và C3 đều đạt. Verifier xác nhận mọi số, rule ghi 16 giây trước khi chạy, không rò truth (skeleton được dựng lại không có damage/log/lag_hint), và false-alarm của gate đúng alpha (0.100/0.100/0.110 trên seed mới).

**Đứng vững:**
- C2, IS trên skeleton đúng so với v4: 1.124/1.071/1.195. B1 v2 là 1.48/1.28/1.59.
- C1 coverage ở T80: 0.903–0.951; ở T150: 0.966–0.980.
- C3, cell GES: T80 cov 0.941 và paired so với v4 −0.17 [−0.31, −0.03]; T150 cov 0.955.
- Tỉ lệ gate mở: skeleton đúng 0.10/0.08/0.05; missing-0.2 0.62/0.98/1.00.
- So với baseline ở missing/reversed T ≥ 80: thắng hoặc hòa cả ba. Ví dụ T80 missing-0.5 so với pselect −1.06 [−1.36, −0.78].
- Phát hiện phương pháp luận: test ngay trong fit cấu trúc của skeleton nâng tỉ lệ phát hiện missing-0.2 ở T40 từ 0.10 lên 0.70. Test all-lag và bootstrap resample theo dòng gần như không có power.

**Không đứng vững:**
- "B1 v1/v2 mở all-lag gần như mọi run" phải sửa thành **48–73%**. Gate giảm false alarm khoảng 5–10 lần, không phải từ ~100%.
- "Thắng baseline đã công bố với thông tin ngang nhau" **bị bác dạng tổng quát**:
  - Trên skeleton đúng, auto3 thua `ida_union` ở mọi T: +0.69, +0.12, +0.14.
  - Ở T150, auto3 thua cả `plugin` ở none và extra (+0.23 đến +0.29), vì flip allowance làm over-cover (0.985) mà grid không hạ được dưới 1.0.
  - Thông tin cũng không ngang nhau: auto3 được calibrate trên D-07H, cùng generator và cùng cell mix với bank đánh giá, còn baseline thì không được calibrate.
  - Dạng đứng vững là dạng thu hẹp: ở T ≥ 80, trên cell missing và reversed.
- "Gate là thành phần then chốt" chỉ đúng trên skeleton không thiếu cạnh. Ở cell missing, bản bỏ gate **tốt hơn** ở cả T40 lẫn T150. Ở T150 (chưa công bố): 2.22 so với 2.34, và 2.30 so với 2.40, do hệ số width open|150 là 1.3 so với 1.2.
- Lệch hard rule 4: width không đi qua `calibrate_methods`. Lý do hợp lý, vì runner key theo stated kind, và đã được ghi lại.
- Script probe của mục 3.1–3.3 trong gate.md chỉ nằm trong scratchpad, nên không tái lập được từ repo.

Nguồn: results/ext_gate_auto3/summary.md, experiments/ext/gate/. Verifier: experiments/ext/verify_gate/ (none_cell.py).

### 1.5 `metrics`: bảng RQ4.1 và RQ4.4

**Verdict: một phần.** Pair-level rerun khớp a2_baselines/a2b_pselect tuyệt đối (8400 run, 0 mismatch). Verifier xác nhận mọi số chính và kiểm role labelling trên toy graph.

**Đứng vững (RQ4.1):**
- Damage phá cả strength lẫn coverage, trên damaged pair lẫn downstream pair. Ví dụ plugin ở missing-0.5, T150: coverage 0.012 (damaged) và 0.22 (downstream).
- Lag sai nặng: mean-lag error của plugin trên damaged pair là 0.87–1.04, so với 0.16–0.21 trên untouched pair. Tăng T không chữa được.
- Module khôi phục hiệu ứng cùng kỳ của cạnh lag-0 bị xoá (coverage 0.91–0.95). `pselect_union` mất phần này: 0.50–0.62 trên lag-0, so với 0.87–0.97 trên lag 1–2. Ở T150 missing-0.5, chênh lệch là −0.474 [−0.543, −0.404].
- Dưới reversal, lag output của module **trùng plugin** (đã kiểm trong code: không có repair candidate thì theta = irf(fit0.B)). Peak hit 0.05, oracle 0.92.
- Null-pair false-signal của module thấp hơn plugin ở cả 21 cell, có cell chỉ sát nút (0.020 so với 0.022).

**Đứng vững (RQ4.4):**
- `rel_width` dự báo miss với AUROC 0.660 [0.619, 0.702], đạt R1. Nhưng "useful" chỉ đạt trên point estimate, CI chạm xa dưới 0.65: **sát biên**.
- Flag rel_width > 2 ở T ≥ 80: ratio 2.60 [2.05, 3.38]. Ở T40 flag này thất bại (85.5% pair bị flag).

**Không đứng vững:**
- "Module under-cover pair đi qua cạnh đảo" như một điểm yếu của module **bị bác về quy kết**. Oracle (skeleton đúng) miss các pair đó gần như ngang: T80 0.162 so với module 0.158; T150 0.060 so với 0.083. Chỉ khoảng +0.02–0.03 là có thể quy cho reversal handling. Mức nền 0.03 trên untouched pair thấp chỉ vì width calibration bơm rộng.
- "Các diagnostic của plan không mang thông tin" là sai lời. `resid_lb` có quan hệ **ngược** (0.453 [0.421, 0.485]). Với large_err, `lag_stab` có dự báo (0.588). Câu đúng là: không diagnostic nào của plan dự báo miss **theo chiều đã nêu**.
- "Cơ chế yếu của baseline mạnh nhất" thực chất là **thuộc tính của bản chuyển thể trong repo** (methods.py `pselect_union.to_skel` đưa cặp được chọn lại mà không có hướng vào `s.undetermined`, chỉ fit lag terms). Đây không phải điểm yếu của Chang–Guo–Malinsky gốc.
- Chiều ngược của width (interval hẹp miss nhiều hơn) và combined model là post hoc theo chiều, và chỉ có CV support. Không được trình bày như một flag đã validate.
- Câu "smoke-test trước full run" mâu thuẫn với timestamp: analyze_pairs.py được sửa lúc 01:27:16, sau khi run bắt đầu khoảng 01:25. Không có thay đổi rule nào sau khi có kết quả (01:38:26), nhưng câu chữ phải sửa.

Nguồn: results/ext_metrics_pairs/, results/ext_metrics_rq41/, results/ext_metrics_flags/. Verifier: experiments/ext/verify_metrics/ (rev_matched.py).

### 1.6 `redteam`: audit và các kiểm tra E3/P1/P2

**Verdict: không có lỗi critical; claim chính đứng vững dưới equal calibration; có nhiều vấn đề major về quy trình và fidelity.** Verifier xác nhận F1–F7 đều có thật và mọi rule outcome đều báo đúng.

**Đứng vững:**
- **R-E3a HELD:** ở T ≥ 80, v4 thắng `pselect_cal`, `bvar_cal`, `ida_cal` ở cả 4 missing cell. Với pselect_cal: −0.68, −0.76, −0.56, −0.68, mọi cận trên < 0.
- **T40 missing: v4 hòa `pselect_cal`.** pselect_cal đạt coverage 0.965/0.968, IS 7.74/7.46, chênh lệch +0.02 [−0.33, +0.39] và +0.07 [−0.31, +0.47]. Câu "module là method duy nhất đạt coverage ở T40" chỉ đúng khi so với baseline chưa calibrate.
- **R-P1a FLAG:** coverage của v4 trên pair bị ảnh hưởng bởi cạnh đảo ở T80 là 0.862/0.863. Cận trên clustered là 0.897/0.899, nên flag có thật nhưng sát biên.
- **P2:** sàn 1.0 của C_GRID chỉ chạm ở T40 missing (c* = 0.9).
- **Tái lập:** 111/111 dòng chạy lại giống hệt; verifier chạy thêm 21/21 dòng. Bank không chồng nhau (0 overlap SHA-256 qua 6 split).
- F1 (damage log riêng tư đi vào mọi method): verifier xác nhận bằng một spy method. Hiện chưa method nào đọc nó, nên đây là rò **tiềm ẩn**.
- F2 (seed ext phụ thuộc số ext module): nặng hơn báo cáo. Tag của v5 nay là 111.
- F3 (hệ số width của "frozen v4" bị tune lại theo config), F5 (fidelity của baseline), F7 (biên so với pselect ở missing-0.2 không qua Bonferroni: 4/6 → 2/6), F8, F10–F15: đều xác nhận.

**Không đứng vững:**
- **F6 bị bác về cách đóng khung.** "fullvar_cal lấy ~97% lợi ích, repair + orientation chỉ thêm 0.22–0.70" là đo so với plugin, mà IS của plugin bị lost pair chi phối. So với `pselect_cal`, fullvar_cal chỉ đạt 0.67/0.41/0.05/−0.03 phần biên của v4. **Ở T150, fullvar_cal hòa pselect_cal** (2.59 so với 2.62; 2.91 so với 2.89). Vậy gần như **toàn bộ lợi thế của v4 so với baseline mạnh nhất ở T150 đến từ repair + orientation draws**. Kết quả này củng cố đóng góp của module.
- Một số con số (n_graphs = 16, số pair được chọn, biên Bonferroni, tag list) chỉ có trong output shell, không có trong file. Verifier đã tái lập được, nhưng phải ghi vào file.
- Bias do sàn calibration: pselect_cal, ida_cal và fullvar_cal ngồi ở factor 1.0 trong khi over-cover ở nhiều cell không thiếu cạnh. Vì vậy các so sánh **mô tả** ngoài cell missing nghiêng về v4. Claim pre-registered ở cell missing không bị ảnh hưởng.
- E3 chạy 1561.8 giây và có lúc 6 worker, tức là vi phạm hard rule 6. Đã được công bố.

Nguồn: docs/ext/redteam.md, results/ext_redteam_calbase/summary.md, experiments/ext/redteam/*.out. Verifier: experiments/ext/verify_redteam/ (check3.py).

### Bảng tóm tắt

| Hướng | Verdict theo rule | Verifier | Đóng góp còn lại sau kiểm chứng |
|---|---|---|---|
| narrow | v5 LOẠI (11/12 ở C2, ratio 1.054, CI chứa 0) | holds | IS ở T40 missing giảm 2.4–3.0; 18/18 so với pselect_union; ablation rõ ràng |
| eiv | LOẠI (8/12 coverage) | partly | Thu hẹp gap ở noise 30% T150; chẩn đoán sai, có cap cần sửa |
| tlp | v4 thắng 13/18, thua 0 (có cổng coverage) | holds | Baseline 2026 mới, sát nhất về loại; TLP_cal đạt T40 missing ngang v5 |
| gate | auto3 GIỮ (B1) | partly | Không cần khai báo damage, chi phí 7–20% IS ở T ≥ 80; claim "thắng baseline" phải thu hẹp |
| metrics | một phần | partly | Bảng RQ4.1 theo role/lag; cơ chế lag-0; RQ4.4: rel_width sát biên |
| redteam | không critical; 2 flag | partly | Claim A2 qua equal calibration; repair là nguồn lợi thế ở T150; danh sách bug |

---

## 2. Giải quyết xung đột giữa các hướng

**X1. "Module under-cover pair bị đảo" (redteam F4/R-P1a và metrics) và oracle (verifier của metrics).**
Hai hướng cùng thấy coverage khoảng 0.86 ở pair bị ảnh hưởng bởi reversal ở T80. Verifier của metrics cho thấy oracle với skeleton đúng cũng miss chừng đó (0.162 so với 0.158).
**Kết luận:** đây chủ yếu là **độ khó nội tại** của các pair này ở T80, không phải lỗi của module. Phần vượt quy được cho reversal handling chỉ khoảng +0.02–0.03, chủ yếu ở T150.
R-P1a vẫn là FLAG theo rule đã ghi, và không được viết lại. Paper báo coverage theo affected/unaffected/null **kèm cột oracle**. Hai định nghĩa khác nhau (redteam: |ΔC| ≥ 0.05; metrics: role damaged/downstream), nên vòng 2 phải đo oracle theo định nghĩa của redteam (R2-6).

**X2. Cơ chế lag-0 của pselect (metrics) và fidelity của baseline (redteam F5, verifier của metrics).**
Cả hai cùng chỉ vào methods.py `pselect_union.to_skel`: cặp được chọn lại mà không có hướng chỉ được fit lag terms. Ngoài ra chỉ có 12 draw mỗi graph, và selection dùng Granger trên reduced-form. Phát hiện của B1 v1 (Granger reduced-form sai khi có cạnh cùng kỳ) cũng áp vào đây.
**Kết luận:** lợi thế lớn nhất của v4 so với "baseline mạnh nhất" ở cell missing có thể **một phần là do bản chuyển thể yếu**. Biên ở missing-0.2 lại không qua Bonferroni (F7). Đây là rủi ro lớn nhất cho claim chính, nên được ưu tiên số 1 ở vòng 2 (R2-1).

**X3. F6 "lợi ích chủ yếu do mở all-lag" (redteam) và verifier của redteam.**
Bản đóng khung của verifier thắng: so với baseline mạnh nhất đã calibrate, repair + orientation là gần như toàn bộ biên ở T150.
Kết quả này **nhất quán với narrow**: ở T150 missing-0.5, thay all-lag bằng targeted opening (`v5_sel`) làm tệ đi +0.25, tức là phần all-lag + repair của v4 có giá trị ở T lớn.
Paper báo ablation theo bộ ba v4 / fullvar_cal / pselect_cal, không báo theo plugin.

**X4. Targeted lag opening: tốt (narrow) hay tệ (gate)?**
Gate báo targeted opening tệ hơn all-lag khi gate đã mở (T80 missing-0.2: 9.29 so với 5.18). Narrow báo targeted opening thắng lớn ở T40.
**Giải quyết:** hai thiết kế khác nhau.
- Gate chỉ mở cặp bị flag, không có ngân sách K = max(3k, ...), và không re-select trong từng bootstrap draw.
- Probe của gate nằm trong scratchpad và không tái lập được.
- Chính dữ liệu của narrow cũng cho thấy targeted opening thua ở T150 khi thiếu nhiều cạnh, khớp hướng với gate ở T ≥ 80.
Hai kết quả gộp lại ủng hộ đúng một giả thuyết: **targeted opening (có re-selection) ở T nhỏ, all-lag ở T lớn.** Đó chính là v5.1 (R2-2). Ngưỡng chuyển phải cố định trước, dựa trên rows/regressors.

**X5. Width ở T40: do sàn calibration hay do mở all-lag?**
Redteam P2, ablation của narrow và verifier của tlp thống nhất: sàn 1.0 chỉ chạm ở T40 missing và chỉ đáng khoảng 10% width. `v5_cal2` một mình giảm 0.55–0.76 IS, còn targeted opening + re-selection giảm thêm khoảng 2.2.
Hệ quả: so sánh công bằng cho "method" là v5 so với `v5_cal2` (7.01 → 4.79), không phải v5 so với v4.

**X6. T40 missing: v4 "thua pselect_union" (A2b), "hòa pselect_cal" (redteam), và v5/TLP_cal đạt khoảng 4.8–5.1.**
Ba kết quả không mâu thuẫn. pselect_cal chỉ hòa v4 vì nó cũng phải rộng ra (width 6.47 so với 6.60) mới đạt coverage.
v5 (4.79/5.12) và `targeted_lp_cal` (4.75/5.02) là hai đường độc lập đến cùng mức IS ở T40 missing. Đây là bằng chứng hai chiều rằng mức width của v4 ở đó là thừa.
v5 so với pselect_cal **chưa được ghép cặp**. Có thể ghép miễn phí vì cùng data seed: dòng v4 của E3 và của narrow đều trùng a2b. Việc này là R2-2a.

**X7. Gate "thắng baseline" và calibration bất đối xứng (verifier của gate, redteam E3).**
Redteam E3 cho thấy cách đúng là calibrate cả baseline. Nhưng với auto3, baseline phải được calibrate **không theo stated kind** (chỉ theo T, gộp mọi cell), nếu không baseline sẽ có thông tin mà auto3 không có. Đây là R2-3b.

**X8. eiv: "weak instruments" (builder) và "admissibility cap" (verifier).**
Theo verifier. Bằng chứng là thí nghiệm trực tiếp trên cùng dữ liệu (0.193 → 0.121 do cap), và ở T lớn cap không chạm (hai estimator trùng nhau ở T = 1000/4000). eiv v2 phải sửa cap trước khi nghĩ đến LIML/Fuller-k.

**X9. Seed của ext method (narrow, eiv, tlp, gate, redteam đều nêu).**
Năm hướng độc lập cùng báo một lỗi, và verifier xác nhận nó đang tệ dần (tag v5: 100 → 108 → 111). Vì vậy **mọi số của ext method chỉ tái lập được với đúng bộ file ext_*.py lúc chạy**. Ví dụ factor của v5 ở T80 missing là 2.5 hay 2.6 tuỳ run. Việc v5 bị loại ở ratio 1.054 nằm đúng trong vùng nhạy với nhiễu này. Đây là lỗi số 1 cần sửa ở mục 5.

---

## 3. Xếp hạng đóng góp cho Paper 4

Thước đo: plan (module Dynamic SEM nhận skeleton, stated damage và data rồi trả C(H) với interval trung thực; RQ4.1–4.4; sản phẩm P1–P5: bản thảo, module có API ổn định, bản đồ chi phí theo cạnh, generator động, mã chạy lại được) và mục tiêu "đề xuất một method chịu lỗi tốt, so với baseline mạnh".

1. **Claim chính đứng vững dưới equal calibration, và nguồn lợi thế được định vị (redteam E3 + verifier).**
   - v4 thắng pselect_cal/bvar_cal/ida_cal ở 4/4 missing cell T ≥ 80.
   - Ở T150, all-lag một mình chỉ hòa baseline mạnh nhất, nên phần **repair + orientation draws** là đóng góp riêng của module.
   - Đây là đóng góp lớn nhất cho mục tiêu "so với baseline mạnh", nhưng còn **điều kiện**: phải qua được baseline đã nâng fidelity (R2-1) và phải báo số đếm cell theo Holm.
2. **Chế độ không cần khai báo: `tolerant_auto3` (gate).** Đây là version đầu tiên đạt rule B1.
   - Nó gỡ giả định yếu nhất của thiết kế (người dùng phải khai báo mức hỏng), với chi phí 7–20% IS so với v4 được khai báo đúng ở T ≥ 80.
   - Bản thân gate là một falsification test của skeleton trước bước ước lượng, có false alarm đúng alpha. Đây là một thành phần tự đứng được.
   - Kèm theo là phát hiện phương pháp luận dùng được cho paper: test adjacency phải làm trong fit cấu trúc của skeleton, vì test all-lag, test reduced-form và bootstrap resample theo dòng không có power.
   - Giới hạn: thua ida_union và plugin trên skeleton đúng, T40 yếu, chưa thử latent/noise.
3. **Sửa điểm yếu đã biết ở T nhỏ (`tolerant_v5`, narrow).**
   - IS ở T40 missing giảm từ 7.77/7.53 xuống 4.79/5.12, coverage 0.93–0.94. Thắng pselect_union 18/18 so với 16/18 của v4.
   - Bị loại ở mức nhiễu. Hướng chữa (v5.1 lai) đã rõ và được TLP_cal xác nhận độc lập rằng mức IS khoảng 5 là đạt được.
   - Nếu v5.1 qua được, nó **đổi module of record** và xoá câu "thua ở T40" khỏi paper.
4. **RQ4.1 có bảng pair-level theo role và lag (metrics).**
   - Lấp đầy RQ4.1 đúng metric của plan (abs/rel strength, lag error, coverage, width).
   - Giải thích *vì sao* plugin sụp: damaged + downstream, lag sai không đỡ theo T.
   - Cho thấy module khôi phục hiệu ứng lag-0, với lưu ý phần so pselect là so với bản chuyển thể.
   - Lộ ra một gap thật: lag output dưới reversal trùng plugin.
5. **Baseline mới 2026 (`targeted_lp`).** Làm dày bảng baseline với một method econometrics cùng loại và rất mới. v4 thắng 12/12 ở T ≥ 80. Phải báo trung thực rằng TLP có IS thấp hơn ở T40 missing nhưng under-cover.
6. **RQ4.4 (metrics).** Một kết quả dương sát biên (rel_width, AUROC 0.66, flag dùng được ở T ≥ 80) và một kết quả âm có giá trị (diagnostic ổn định/phần dư của plan không dự báo miss theo chiều đã nêu). Combined model chưa được dùng làm claim.
7. **Measurement noise (eiv).** Hiện chỉ đủ cho câu giới hạn đã thu hẹp: ở 10% noise v4 đã ổn ở 5/6 cell; ở 30% eiv thu hẹp gap ở T150 nhưng không đóng được. Nếu eiv v2 (sửa cap) qua rule, mục này nhảy lên hạng 3–4, vì nó xoá một failure đã biết của module.

**Về module of record:** giữ v4. Ứng viên thay thế theo thứ tự là **v5.1** (chế độ có khai báo) và **auto3/auto5** (chế độ không khai báo). Paper có thể trình bày module hai chế độ: *declared* (v4, hoặc v5.1 nếu qua) và *auto* (auto3). Cả hai đều cần một bank mới để xác nhận (xem R2-0).

---

## 4. Việc vòng 2

Thứ tự ưu tiên: những việc có thể **đổi claim chính hoặc module of record** đứng trước. Mọi version mới phải ghi rule vào doc của hướng **trước** khi chạy evaluation. Mọi run tuân theo `--workers 3` và khoảng 15 phút.

**R2-0. Quyết định cần người duyệt (không agent nào tự làm): bank xác nhận mới.**
- *Mục tiêu:* có một bank chưa dùng (ví dụ P4-H2, sinh bằng cùng generator với topology mới, kiểm tra không chồng SHA-256 với 6 split hiện có) để chạy **một lần** cho v5.1, auto3 và eiv v2.
- *Vì sao:* mọi split đã dùng hết, và D-07 development đã gợi ý ngưỡng của v5.1 cũng như thiết kế của auto3. Không có bank mới thì mọi kết quả vòng 2 vẫn chỉ là exploratory.
- *Bằng chứng mong đợi:* bản ghi split-usage cập nhật và rule của mỗi version được khoá trước khi sinh bank.
- *Owner:* team lead đề xuất, người dùng/giảng viên duyệt. Hard rules hiện tại không cho dùng bank nào ngoài D-07/D-07H development.

**R2-1. Nâng fidelity baseline và chạy lại so sánh chính.** Ưu tiên cao nhất.
- *Mục tiêu:* tạo `src/paper4/ext_baselines2.py` (không sửa methods.py) với:
  - `pselect_union_v2`: ≥ 199 bootstrap draw mỗi graph; adjacency test trong phương trình cấu trúc; cặp được chọn lại mà không có hướng thì được union qua **cả hai hướng kèm hạng cùng kỳ**, như ida_union làm với CPDAG.
  - `bvar_minnesota_v2`: conjugate prior cho error variance.
  - Tuỳ chọn EHW SE cho LP.
  - Chạy v4 (và v5 nếu có) so với các bản này, cả uncalibrated lẫn calibrated theo đúng cách của E3. Báo số đếm cell theo **Holm** và cột coverage lag-0/lag-1-2.
- *Vì sao:* biên so với pselect ở missing-0.2 không qua Bonferroni (F7). Cơ chế lag-0 là do bản chuyển thể (X2). Một reviewer sẽ bắt đúng chỗ này.
- *Bằng chứng mong đợi:* rule ghi trước dạng "v4 coverage ≥ 0.90 và cận trên CI của IS(v4) − IS(X) < 0 ở 4/4 missing cell T ≥ 80, X ∈ {pselect_v2, pselect_v2_cal}". Nếu thất bại, claim chính phải thu hẹp lại.
- *Owner:* redteam (xây baseline), metrics (bảng lag-0 trên pair-level).

**R2-2. `tolerant_v5.1`: lai targeted/all-lag, cộng các phép đo ghép cặp miễn phí cho v5.**
- *Mục tiêu:*
  - (a) Không chạy lại gì: ghép cặp v5 (ext_narrow_eval) với pselect_cal và fullvar_cal (ext_redteam_calbase) và với targeted_lp_cal (ext_tlp_eval), qua dòng v4 trùng nhau. Phải kiểm tra lại pairing trước.
  - (b) Pre-register v5.1: targeted opening có re-selection khi tỉ lệ rows/regressors của all-lag fit < ngưỡng τ cố định (chọn trên D-07H probe, **không** trên D-07), và `v5_cal2` khi ngược lại. Exploratory trên D-07 dev, ghi rõ rằng vùng của τ đã được D-07 gợi ý. Chạy xác nhận trên bank mới nếu R2-0 được duyệt.
  - (c) Chạy v5 qua kịch bản a1 (latent1/latent3/noise).
- *Vì sao:* đây là ứng viên duy nhất có thể đổi module of record và xoá điểm yếu T40. (a) cho biết v5 có thắng cả baseline đã calibrate ở T40 hay không.
- *Bằng chứng mong đợi:* đạt cả ba điều kiện của rule v5 (không nới ngưỡng 1.05). Coverage ≥ 0.90 dưới latent1.
- *Owner:* narrow. tlp hỗ trợ (a).

**R2-3. auto3: độ bền, so sánh công bằng, và bản ghép với v5.**
- *Mục tiêu:*
  - (a) Chạy auto3 qua kịch bản a1 latent/noise. Confounder có thể làm gate mở.
  - (b) So sánh với baseline được calibrate **theo T, gộp cell, không đọc stated kind**, kể cả cell none. Báo IS so với ida_union/plugin trên skeleton đúng.
  - (c) `tolerant_auto5`: gate → khi mở ở T nhỏ thì dùng targeted opening có re-selection của v5, kèm two-sided calibration để chữa over-cover 0.985 ở T150. Đây là version mới với rule mới.
  - (d) Chép probe script từ scratchpad vào experiments/ext/gate/.
- *Vì sao:* auto3 là đóng góp "không cần khai báo" duy nhất đã đạt rule. Claim "thắng baseline" hiện phải thu hẹp, và (b) quyết định câu chữ.
- *Bằng chứng mong đợi:* với auto3 ở latent1, coverage ≥ 0.90 ở cell missing/reversed T ≥ 80. Với auto5, rule B1 cộng thêm "IS ở T40 missing không tệ hơn pselect_union".
- *Owner:* gate. narrow tư vấn (c).

**R2-4. Two-sided calibration (grid dưới 1.0) cho mọi method.**
- *Mục tiêu:* đo lại v4, các baseline đã calibrate và auto3 với grid bắt đầu từ 0.5 (bản wrapper ext, hoặc pre-scale 0.5 như v5). Pre-register là `tolerant_v4c` có hệ số mới.
- *Vì sao:* sàn 1.0 làm v4 thừa width ở T40 missing, làm auto3 over-cover ở T150, và làm so sánh mô tả ngoài cell missing nghiêng về v4 (vì baseline ngồi ở sàn). Sửa một lần thì công bằng cho tất cả.
- *Bằng chứng mong đợi:* ở T ≥ 80, v4c không đổi so với v4 (dự đoán từ ablation `v5_cal2`); ở T40 missing giảm khoảng 0.55–0.76. Cần kiểm tra lại mọi claim mô tả ngoài cell missing.
- *Owner:* redteam (wrapper calibration chung), narrow.

**R2-5. `tolerant_eiv` v2.**
- *Mục tiêu:* bỏ cap toàn cục trong `estimate_noise_share`, thay bằng cap theo từng phương trình hoặc soft penalty kèm kiểm tra corrected Gram matrix không âm. Sau đó mới xét LIML/Fuller-k. Chạy ablation `plugin_eiv`, và thử noise khác nhau giữa các chuỗi.
- *Vì sao:* noise 30% là failure đã biết của module of record. Verifier chỉ ra cap gây phần lớn bias của r̂.
- *Bằng chứng mong đợi:* giữ nguyên rule cũ (12/12 cell ≥ 0.90, clean cost ≤ 1.15) để so được. Ghi thêm IS ở noise0.1 so với v4 và |C| trên null pair.
- *Owner:* eiv.

**R2-6. Reversal: coverage theo pair và lag output.**
- *Mục tiêu:*
  - (a) Đo coverage của oracle theo định nghĩa "affected" của redteam (|ΔC| ≥ 0.05), với sensitivity ở ngưỡng 0.02/0.05/0.10.
  - (b) Pre-register một thay đổi báo cáo: mean/peak lag lấy từ structural draws (như C(H)) hoặc báo lag interval, thay cho lag của fit0.
- *Vì sao:* lag error là metric chính của plan, và dưới reversal module hiện không hơn plugin (peak hit 0.05 so với oracle 0.92).
- *Bằng chứng mong đợi:* (a) chốt câu "khó nội tại" hay "lỗi module"; (b) peak hit trên damaged pair bị đảo tăng có ý nghĩa mà không làm tệ cell khác.
- *Owner:* metrics, redteam (a).

**R2-7. RQ4.4: freeze và mở rộng.**
- *Mục tiêu:* freeze combined logistic, hoặc flag hai phía (rất hẹp HOẶC tương đối rộng), để chỉ test một lần trên bank mới. Xuất pair-level rows cho GES/latent/noise. Báo AUROC cho auto3/v5.
- *Vì sao:* RQ4.4 hiện chỉ có một kết quả dương sát biên.
- *Bằng chứng mong đợi:* AUROC với CI, và flag đạt R3 ở cả T40.
- *Owner:* metrics.

**R2-8. TLP: hoàn thiện baseline.**
- *Mục tiêu:* chạy double bootstrap với B2 = 100 và p sát bài gốc ở các cell T80 none/extra (nơi bản single-level có thể bất lợi, −0.59). Đưa `targeted_lp` vào bảng baseline chính với câu chữ đã sửa. Tuỳ chọn: version "v4 + TLP shrink" (ưu tiên thấp, vì v5 đã đạt cùng mức).
- *Vì sao:* đóng câu hỏi "baseline bị làm yếu" trước khi reviewer hỏi.
- *Bằng chứng mong đợi:* v4 vẫn thắng ở T80 none/extra so với TLP double bootstrap, hoặc ta báo trung thực là không.
- *Owner:* tlp.

**R2-9. Bảng và câu chữ cho bản thảo (P1).**
- *Mục tiêu:*
  - Bảng ablation v4 / fullvar_cal / pselect_cal.
  - Số đếm cell theo Holm với CI clustered.
  - Coverage theo affected/unaffected/null kèm oracle.
  - Restate RQ4.2 theo interval score, vì v4 rộng hơn plugin trong khi plan hỏi "hẹp hơn".
  - Restate T40 thành "hòa pselect đã calibrate".
  - Ghi mọi con số ad hoc (n_graphs, Bonferroni, tag list) vào file.
- *Owner:* redteam, metrics.

**R2-10. Công bố và vệ sinh quy trình** (chỉ append vào doc của chính hướng đó).
- narrow.md: timing smoke run trên D-07 lúc 18:27:12Z; "11/18" → "10–11/18"; "−0.6 đến −0.8" → "−0.55 đến −0.76".
- eiv.md và docstring của ext_eiv.py: sửa câu gán kết quả probe 2; "≥ 0.93" → "≥ 0.927", kèm việc IS tệ hơn ở T80 missing/reversed.
- gate.md: "gần như mọi run" → "48–73%"; công bố bản bỏ gate tốt hơn ở cell missing T150; thu hẹp claim so với baseline.
- metrics.md: thời điểm smoke-test; resid_lb là "inverse"; "useful" là sát biên; cơ chế lag-0 thuộc bản chuyển thể.
- tlp.md: "loses none" kèm điều kiện; double-bootstrap probe "không faithful".

---

## 5. Bug cần sửa trong file có sẵn (CHƯA sửa, chỉ báo)

| # | File:dòng | Vấn đề | Đề xuất sửa | Mức |
|---|---|---|---|---|
| B1 | experiments/run_experiment.py:196–198 | Seed bootstrap của ext method là `rng(100 + e_idx)`, với e_idx là vị trí trong danh sách mọi ext method của repo. Số đổi khi có agent thêm/bớt file (tag v5: 100 → 108 → 111) | Seed theo `crc32(method_name)` | Major (tái lập) |
| B2 | experiments/run_experiment.py:60–73 | Import **mọi** ext_* không có try/except, nên một module hỏng làm sập mọi run | Chỉ import module mà config yêu cầu, có guard | Major |
| B3 | experiments/run_experiment.py:162–198, 137; src/paper4/skeleton.py:42; tests/test_core.py:96 | `skel.log` (cặp hỏng thật, lag thật, số lỗi GES thật) và `lag_hint` đi vào mọi method. Test chỉ kiểm `to_interface()`, mà hàm này không ai gọi | Gọi `to_interface()` hoặc strip log/lag_hint trước khi gọi method; thêm test bằng spy method | Major (rò tiềm ẩn, chưa bị khai thác) |
| B4 | experiments/run_experiment.py:401 (và :265) | Hệ số width của "frozen v4" bị tune lại theo config (rq42_v4 có mod\|40\|none 1.7 so với 1.4 ở a2). Trigger calibration và key không nhất quán; dòng misstated dùng factor của v3 (F11) | Freeze `calibration_v4.json`, nạp theo key; trigger mỗi khi có `calibrate_methods` | Major |
| B5 | docs/decision_rules.md:155, :207 | Bảng hệ số ghi 80: 1.3/1.5/1.4 và câu "không đổi code hay width factor" sai so với hệ số thực dùng | Cập nhật bảng, ghi rõ drift | Minor (doc) |
| B6 | experiments/run_experiment.py:45 | `C_GRID` bắt đầu từ 1.0, nên calibration chỉ nới rộng được, không làm hẹp được | Là thay đổi thiết kế, cần version mới (R2-4), không sửa âm thầm | Design |
| B7 | src/paper4/metrics.py:76–78 | Chỉ chấm non-null pair; IS trên null pair không được lưu | Lưu thêm IS và coverage của null pair | Minor |
| B8 | src/paper4/methods.py:666, `pselect_union.to_skel`, `pair_evidence` | `per = max(10, 199//16)` = 12 draw mỗi graph; cặp chọn lại không có hướng chỉ fit lag terms; selection bằng Granger reduced-form | Không sửa tại chỗ (sẽ đổi kết quả cũ). Làm baseline v2 ở ext (R2-1) | Fidelity |
| B9 | src/paper4/methods.py:554, 563 | `bvar_minnesota` giữ error variance cố định s_j² | Như B8, làm v2 ở ext | Fidelity |
| B10 | src/paper4/methods.py:298, 302, 319 | `repair_candidates`/`contemporaneous_pool` chạy một lần, không chạy lại trong từng bootstrap draw | Thiết kế; narrow cho thấy re-select trong draw có lợi. Đưa vào version mới | Design |
| B11 | src/paper4/methods.py, `tolerant()` | Không có repair candidate thì theta = irf(fit0.B), nên lag output dưới reversal trùng plugin | Version mới (R2-6b) | Design gap |
| B12 | experiments/run_flags.py:146–147; experiments/run_edge_cost.py:172–173 | Lặp trên D-07 confirmatory; split-usage log không ghi lần tái dùng cho RQ4.3/RQ4.4 | Cập nhật log split usage | Minor (quy trình) |
| B13 | docs/ket_qua_rq42.md (các dòng cũ); docs/ket_qua_nhom_a.md:67, :125 | Doc cũ; claim A3 về interval score quá rộng | Sửa câu chữ theo redteam | Minor (doc) |

Bug trong file ext của vòng 1 (owner tự sửa bằng version mới, không sửa file cũ đã được đánh giá):
- `src/paper4/ext_eiv.py`, `estimate_noise_share`: cap toàn cục `crit[grid > lam] = inf` trong vòng lặp phương trình, kèm docstring gán sai kết quả probe 2. Xử lý ở R2-5.
- `src/paper4/ext_tlp.py`: `targeted_lp_cal` dựa vào cache module-level và thứ tự gọi của runner. Sẽ vỡ nếu B1/B2 đổi thứ tự. Owner nên làm cho nó tự tính khi cache miss.

---

## 6. Câu dùng được ngay cho paper (đã qua kiểm chứng, đều là exploratory, D-07 development)

- Dưới equal calibration, ở T ≥ 80 trên cell thiếu cạnh, `tolerant_v4` có interval score thấp hơn `pselect_cal`, `bvar_cal` và `ida_cal` ở 4/4 cell, với coverage 0.957–0.968. Ở T150, fit all-lag một mình chỉ hòa `pselect_cal`. Lợi thế còn lại đến từ contemporaneous repair và orientation draws. *(Còn chờ R2-1.)*
- Ở T40 trên cell thiếu cạnh, `tolerant_v4` hòa `pselect_union` đã calibrate. Hai cách làm hẹp độc lập (`tolerant_v5`, `targeted_lp_cal`) đạt IS khoảng 4.8–5.1 so với 7.5–7.8, với coverage 0.93–0.95.
- `tolerant_auto3` không đọc mức hỏng khai báo. Nó giữ coverage ≥ 0.90 ở cell thiếu và đảo cạnh ở T ≥ 80, thắng hoặc hòa ba baseline ở các cell đó, và tốn 7–20% interval score so với v4 được khai báo đúng. Trên skeleton đúng, nó chịu phạt 0.12–0.69 IS so với `ida_union`, và ở T150 cả so với `plugin`.
- Test adjacency phải làm trong phương trình cấu trúc của skeleton. Granger test trên VAR reduced-form, test all-lag và bootstrap resample theo dòng đều không có power hoặc báo động giả khi có cạnh cùng kỳ.
- Measurement noise: ở 10%, `tolerant_v4` đạt coverage ≥ 0.90 ở 5/6 cell. Ở 30%, hiệu chỉnh errors-in-variables nâng coverage ở T150 lên 0.89–0.92 nhưng chưa đạt 0.90 ở mọi cell. Đây vẫn là giới hạn.
- Không diagnostic ổn định hay phần dư nào trong plan dự báo được miss theo chiều đã nêu. Relative width dự báo miss ở mức vừa (AUROC 0.66, sát biên "useful").
