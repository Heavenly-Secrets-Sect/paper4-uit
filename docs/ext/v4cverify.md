# Hướng "v4cverify" (R3-7): kiểm chứng độc lập kết quả v4c

**Trạng thái.** Vòng 3, verification. Không có method mới, không có rule giữ/loại mới. Chỉ đọc `results/ext_v4c_eval/runs.jsonl` (D-07 development, seed_base 20261102) và các run ghép cặp đã có (`a2_baselines`, `a2b_pselect`, `ext_redteam_calbase`). Lượt chạy lại duy nhất là 2 unit của chính config `ext_v4c_eval` (D-07 development) cộng khối calibration D-07H development của nó. Không chạm P4-H1, P4-H2 hay confirmatory split nào. Không chạy config P4-H2 nào.

- Code của tôi: `experiments/ext/v4cverify/recompute.py` (viết mới, không import và không đọc `experiments/ext/v4c/analyze.py`; chỉ dùng chung định nghĩa trong rule ở docs/ext/v4c.md mục 4).
- So sánh row-by-row: `experiments/ext/v4cverify/compare_rows.py`.
- Config chạy lại: `experiments/configs/ext_v4cverify_rerun_w3.json` (miniconda, numpy 2.5.4) và `experiments/configs/ext_v4cverify_rerun_w3_clt.json` (python3 CLT, numpy 2.0.2). Hai config giống hệt `ext_v4c_eval.json`, chỉ khác `name`, `max_topologies` = 2 và `replicates` = 1 (unit seed = seed_base + 1000·t_idx + rep không phụ thuộc hai khóa này, nên 2 unit (syn_dag_00, rep 0) và (syn_dag_01, rep 0) phải tái tạo đúng các dòng tương ứng của run gốc). Khối calibration giữ nguyên (cả 20 topology D-07H development).
- Output: `results/ext_v4cverify_*`.

## 1. Tiêu chí kiểm chứng (ghi trước khi tính hay chạy bất cứ gì)

Các số được so với `results/ext_v4c_eval/ruling.md` và `describe.md` (sinh bởi analyze.py).

**V1. Rule A.** Tôi tính lại bằng code của mình: IS theo run ok chung, coverage pooled (lost pair tính là không phủ, tức `n_covered_nonnull / n_nonnull` gộp), bootstrap theo topology (cluster), B = 2000, seed 20261102, percentile; p một phía = (1 + #{boot ≥ 0})/(B + 1); TOST và Holm như mục 4 của v4c.md.
- Point estimate (IS, coverage, ratio, width) là tất định: phải khớp tới 3 chữ số thập phân như ruling.md in ra. Lệch → "discrepancy".
- Đếm C1 (14/14) và C2 (2/2, Holm 2/2) phải khớp. Nếu đếm khác, phán quyết RETAINED được coi là **không đứng vững** trừ khi khác biệt chỉ đến từ cell "borderline" (định nghĩa dưới), khi đó báo là "phụ thuộc bootstrap".
- CI và p phụ thuộc cách rút bootstrap (thứ tự gọi rng của tôi khác analyze.py). Dung sai: cận CI lệch ≤ 0.03 (trên thang IS) hoặc ≤ 0.005 (trên thang ratio) được coi là khớp. Đếm TOST Holm (5/14) được báo; khác biệt ở cell có p_TOST nằm trong [0.5·ngưỡng Holm, 2·ngưỡng Holm] coi là borderline.
- **Borderline:** một cell mà phân loại phụ thuộc vào việc một cận CI ở trong khoảng ±0.02 quanh 0 (thang IS) hoặc coverage trong ±0.002 quanh 0.90, hoặc p một phía trong [0.5·ngưỡng, 2·ngưỡng] của Holm.

**V2. Phần B.** Tính lại đếm W/T/L và W sau Holm cho 12 cặp (so sánh (a)–(d) × 3 baseline) trên 21 cell và trên 15 cell ngoài missing; D1 (đếm reversed/extra, kể cả IUT-Holm), D3, D4, D5, D7, bảng cell missing, và D6 (4 factor < 1.0; X_c2 tốt hơn X_cal 8/45, Holm 4/45; tệ hơn 6/45). Phần B "đứng vững" nếu mọi đếm khớp; mọi chênh lệch được liệt kê theo cell và gắn nhãn borderline hay discrepancy. Kiểm thêm: dòng `tolerant_v4` dùng ở (a), (b) lấy từ run khác (`a2b_pselect`, `ext_redteam_calbase`) phải trùng khít với dòng `tolerant_v4` của `ext_v4c_eval`, nếu không phép ghép cặp (a)/(b) với v4 của run này là không hợp lệ.

**V3. `--workers 6` so với 3.** Chạy `ext_v4cverify_rerun_w3` với `--workers 3` (cùng interpreter mặc định `python` = miniconda). So sánh: (i) `calibration.json` với `results/ext_v4c_eval/calibration.json` (mọi key, so bằng nhau tuyệt đối); (ii) mọi dòng của 2 unit (6 method × 3 T × 7 cell = 126 dòng/unit, 252 dòng) với dòng cùng khóa (method, topology, replicate, T, kind, rate) của run gốc, trên **mọi** trường. Kết luận "workers không đổi kết quả" nếu bằng nhau tuyệt đối (bit-identical sau JSON round-trip). Nếu chỉ lệch ≤ 1e-9 tương đối thì báo "khớp tới sai số floating point", và nêu khả năng nguồn (BLAS threading). Lệch lớn hơn → discrepancy, và kết quả v4c không được coi là tái lập.

Lý do kỳ vọng bằng nhau tuyệt đối: seed của mọi stream chỉ phụ thuộc (unit, T, c_idx, tag); `pool.map` giữ thứ tự; số worker chỉ đổi việc unit nào chạy ở process nào.

**V4. Interpreter.** Chạy `ext_v4cverify_rerun_w3_clt` bằng `/Library/Developer/CommandLineTools/usr/bin/python3` (numpy 2.0.2, scipy 1.13.1), `--workers 3`, cùng 2 unit. So sánh như V3, với run gốc và với run miniconda. Báo: interpreter nào tái tạo run gốc bit-identical; max |Δ| tuyệt đối và tương đối của các trường số; calibration.json có khác không (một factor đổi là thay đổi rời rạc, sẽ được báo riêng). Không có ngưỡng giữ/loại: V4 chỉ để công bố.

**Thời gian dự kiến.** Mỗi lượt chạy lại: calibration 20 unit + 2 unit đánh giá, khoảng 30 s CPU mỗi unit → khoảng 4 phút với 3 worker; hai lượt chạy tuần tự, khoảng 8–10 phút. Recompute: vài phút.

## 2. Kết quả

Nguồn: `results/ext_v4cverify_recompute/{recompute.txt, recompute.json, compare_published.txt, seed_sensitivity.txt, compare_rows.txt, compare_rows.json, r36_checks.txt, timing.json}`; hai run `results/ext_v4cverify_rerun_w3/` và `results/ext_v4cverify_rerun_w3_clt/`. Thứ tự thực hiện: doc này (mục 1) được ghi trước; sau đó mới chạy recompute và hai lượt chạy lại.

### V1. Rule A: **đứng vững (holds)**. `tolerant_v4c` RETAINED được tái lập.

- Ghép cặp: `plugin` và `tolerant_v4` của `ext_v4c_eval` trùng `a2_baselines` 1260/1260 dòng (status, n_covered_nonnull, IS). `tolerant_v4` cũng trùng 1260/1260 với `a2b_pselect` và `ext_redteam_calbase`, nên phép ghép (a)/(b) của phần B là hợp lệ. (Trùng "mọi trường" là 0/1260 chỉ vì các run cũ có thêm/khác trường info; ba trường dùng để chấm trùng hết.) Status ok 1260/1260 cho cả 6 method.
- **C1: 14/14** (ratio 0.9811–1.0140, khớp 0.981–1.014). Mọi point estimate (IS, coverage, ratio) khớp analyze.py tới sai số 4e-15. **TOST Holm 5/14**, đúng cùng 5 cell (T80 missing-0.5, T80 reversed-0.2, T150 none, T150 extra-0.2, T150 missing-0.2). Cận CI của ratio lệch tối đa 0.0016 so với analyze.py (dung sai 0.005). Qua 50 seed bootstrap, TOST Holm là 5/14 ở 48 seed và 4/14 ở 2 seed.
- **C2: 2/2, Holm 2/2.** T40 missing-0.2: coverage 0.983 → 0.958, IS 7.765 → 6.977, hiệu −0.79 [−0.99, −0.58]. T40 missing-0.5: 0.978 → 0.956, 7.528 → 6.817, −0.71 [−0.88, −0.54]. Qua 50 seed, cận trên lớn nhất là −0.533, nên C2 không phụ thuộc bootstrap.
- Một điểm về nhãn: cột "width" trong ruling.md/describe.md là **median qua run** của `width_kept` (6.601/5.613 và 6.454/5.378), không phải mean (mean là 6.923/5.824 và 6.708/5.647). Không ảnh hưởng phán quyết.
- Factor hiệu dụng: khớp toàn bộ. Không raw c nào chạm sàn 1.0 hay trần 10 của grid. Có **5 factor < 1.0**: `tolerant_v4c|40|missing` = 0.85 cộng **4 factor baseline ngoài missing** (`pselect_union_c2` và `ida_union_c2` ở T150 none/extra, 0.95/0.90 và 0.95/0.95). So với E3, trên 27 (X, T, kind) mà E3 không chạm sàn: chỉ 8/27 bằng nhau đúng, **6/27 lệch ≥ 0.1** (pselect 40 none +0.3, pselect 40 reversed +0.1, ida 40 missing −0.5, ida 150 missing +0.3, ida 150 reversed −0.1, bvar 40 reversed −0.1), số còn lại lệch đúng một bước grid mịn (0.05).

### V2. Phần B: **đứng vững, có 3 chênh lệch nhỏ, cả 3 đều borderline theo định nghĩa ghi trước.**

- 252 cell (4 so sánh × 3 baseline × 21 cell): point estimate khớp tới 3.6e-15; **phân loại W/T/L khớp 252/252**. Cận CI lệch trung vị 0.012, lệch > 0.03 ở 56 cell, nhưng lớn nhất chỉ 6.6% độ rộng CI. Ở mọi cell lệch > 0.03, cận gần 0 nhất cách 0 ít nhất 0.061, nên không phân loại nào đổi. Cận CI lệch quá dung sai 0.03 ghi trước là do các cell missing có IS lớn (thang 10–30) và cell T40 có CI rộng. Tôi báo thẳng đây là vượt dung sai về con số, nhưng không đổi kết luận nào.
- Đếm W/T/L (21 cell và 15 cell ngoài missing) khớp ở cả 12 cặp. Đếm **W sau Holm** khớp ở 11/12 cặp. Cặp lệch: **(b) ida_union: 13 của tôi so với 12** (ngoài missing 7 so với 6). Nguyên nhân là cell T150 extra-0.5 (p một phía 0.0015 của tôi so với 0.0040; ngưỡng Holm ở hạng 13 là 0.025/9 = 0.0028), tức borderline. Qua 50 seed bootstrap, cell này được Holm bác ở 18/50 seed, nên số 12 hay 13 tuỳ seed.
- Cũng nguyên nhân đó: **D1 (b), danh sách IUT-Holm**, của tôi có 5 cell (thêm T150 extra-0.5), analyze.py có 4. Đếm thô D1 khớp hoàn toàn: (a) reversed 4/6, extra 3/6 (giống vòng 1); (b) 5/6, 2/6; (c) 4/6, 3/6 (cùng số nhưng khác cell: T80 extra-0.5 thay T80 extra-0.2); (d) 5/6, 1/6.
- **D6: X_c2 tốt hơn X_cal ở 9/45 (của tôi) so với 8/45.** Cell thêm là ida_union T80 extra-0.2: cận trên −0.0009 (của tôi) so với +0.0003. Borderline; qua 50 seed, cận trên < 0 ở 21/50. Sau Holm vẫn 4/45, cùng 4 cell. Tệ hơn 6/45, cùng 6 cell.
- D2 (12/12 W ở cả (a)–(d)), D3, D4, D5, D7 và bảng cell missing khớp từng ký tự. Cụ thể: ở T ≥ 80 missing, (b)/(c)/(d) thắng cả ba baseline 4/4. Ở T40 missing, (d) v4c thắng `pselect_union_c2` 2/2, trong khi (b)/(c) v4 chỉ hòa.
- Kết luận phần B của describe.md đứng vững. Cách viết đúng: "thiên lệch do sàn 1.0 có thật nhưng nhỏ: X_c2 tốt hơn X_cal ở 8–9/45 cell ngoài missing tùy seed bootstrap (Holm 4/45), tệ hơn ở 6/45". Số Holm của (b) ida_union phải báo là 12–13.

### V3. `--workers 6` so với 3: **không đổi gì, bit-identical.**

`ext_v4cverify_rerun_w3` (miniconda, numpy 2.5.4, scipy 1.17.1, `--workers 3`, 218.8 s): `calibration.json` **trùng từng byte** với `results/ext_v4c_eval/calibration.json` (85 key). 252/252 dòng của (syn_dag_00, rep 0) và (syn_dag_01, rep 0) trùng tuyệt đối với dòng cùng khóa của run `--workers 6`, trên mọi trường (max |Δ| = 0). `skeletons.jsonl` của 2 unit cũng trùng. Đúng như kỳ vọng: mọi seed chỉ phụ thuộc (unit, T, c_idx, tag).

### V4. Interpreter: **không có khác biệt nào ở mức dòng kết quả.**

`ext_v4cverify_rerun_w3_clt` (`/Library/Developer/CommandLineTools/usr/bin/python3`, numpy 2.0.2, scipy 1.13.1, `--workers 3`, 284.8 s): calibration.json trùng từng byte, 252/252 dòng trùng tuyệt đối với run gốc và với run miniconda. Probe của verifier vòng 2 (khác biệt interval ≤ 1e-10 trên 1 unit D-07H) không để lại dấu vết nào trong 252 dòng này, kể cả ở chữ số cuối của float. Hệ quả: **không xác định được run `--workers 6` đã dùng interpreter nào**, vì cả hai đều tái tạo nó. Đồng thời câu hỏi đó cũng không còn quan trọng với 2 unit đã kiểm. Giới hạn: chỉ kiểm 2/60 unit đánh giá (cả hai thuộc profile erdos_renyi) và toàn bộ khối calibration.

### Thời gian

Mỗi lượt 2 unit gồm 22 unit (20 calibration + 2 đánh giá). Ngoại suy cho đủ `ext_v4c_eval` (80 unit) với 3 worker: khoảng 13 phút (miniconda) đến 17 phút (CLT) ở load average 4–8. Ước tính 10–12 phút trong v4c.md là thấp. Lần chạy đầu (CLT, 3 worker) bị cắt sau 12.25 phút khi vẫn đang ở pha đánh giá, khớp với ngoại suy này.

### Phán quyết kiểm chứng

- **"RETAINED" đứng vững**: C1 14/14 (tất định), C2 2/2 và Holm 2/2, bền với seed bootstrap.
- **Đếm phần B đứng vững**, với hai con số phải ghi kèm phụ thuộc seed: (b) ida_union Holm 12–13/21 (ngoài missing 6–7/15) và D6 "tốt hơn" 8–9/45. D1 (b) IUT-Holm có 4–5 cell.
- **`--workers 6` và đổi interpreter không làm đổi dòng nào** trên 2 unit và trên calibration.
- Lưu ý còn nguyên từ synthesis: C1 trộn hiệu ứng factor với nhiễu Monte Carlo, vì bootstrap stream của v4c (`ext_seed`) khác v4 (`rng(6)`). v4c không phải ứng viên P4-H2 riêng. **Không có spec P4-H2 từ hướng này** (p4h2_spec: none).

Sửa câu chữ R3-6 đã được append vào docs/ext/v4c.md và docs/ext/eiv2.md (heading "Sửa sau kiểm chứng vòng 2").
