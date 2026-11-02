# Hướng `r4ngorient` (vòng 4): orientation theo non-Gaussianity cho bước repair và reversal của `tolerant_v5_1`

**Trạng thái.** Exploratory. Evaluation chỉ trên D-07 development (seed_base 20261102). Calibration và mọi probe chỉ trên D-07H development. Không đụng P4-H1, P4-H2 (cả hai split) hay confirmatory split nào. Không LLM call, không git commit. Module of record vẫn là `tolerant_v5_1` (đã xác nhận trên P4-H2). Hướng này chỉ thêm file mới.

## 1. Câu hỏi và nguồn

`tolerant_v5_1` rút **ngẫu nhiên** chiều của cạnh cùng kỳ ở hai chỗ:
- bước [3] contemporaneous repair: cặp do BH tìm ra được thêm với chiều u → v hay v → u, mỗi chiều xác suất 1/2;
- bước [4] targeted reversal: lật k_rev cặp trong pool cạnh cùng kỳ đáng kể, chọn bằng permutation đều (`methods._flip_from`).

Với shock Gaussian, chiều của một cạnh cùng kỳ đứng riêng không xác định được, nên đồng xu công bằng là đúng. Với shock non-Gaussian thì chiều xác định được: LiNGAM (Shimizu et al. 2006), VARLiNGAM (Hyvärinen, Zhang, Shimizu, Hoyer 2010, JMLR 11:1709–1731), identification by non-Gaussianity trong SVAR (Lanne, Meitz, Saikkonen 2017, J. Econometrics 196(2):288–304; Keweloh 2021; Cordoni, Doremus, Moneta 2024). Hướng này thay **đúng hai đồng xu đó** bằng evidence từ likelihood-ratio cặp đôi của Hyvärinen & Smith (2013, JMLR 14:111–152), đặt sau một gate Jarque–Bera. Gate theo khuyến nghị của Montiel Olea, Plagborg-Møller & Qian (2022, AEA P&P 112:481–485): kiểm tra non-Gaussianity trước khi dựa vào nó để identify, vì identification yếu khi shock gần Gaussian. Varsortability (Reisach, Seiler, Weichwald 2021, NeurIPS, arXiv:2102.13647) được audit để chắc rằng evidence không ăn theo thang đo của dữ liệu mô phỏng.

Ghi chú về các nguồn đã đọc lại khi cài đặt:
- H-S 2013: với x, y đã chuẩn hoá và ρ = tương quan, xấp xỉ LR là R = ρ·Ê{x g(y) − g(x) y}. Mình suy lại dấu: với g = tanh ≈ u − u³/3, R ≈ (ρ/3)·Ê{x³y − xy³}, và với x → y thì Ê{x³y − xy³} = ρ(1 − ρ²)·exkurt(x). Vậy R > 0 nghĩa là x → y khi nguồn super-Gaussian, và cần nhân −1 khi sub-Gaussian. Dạng cumulant bậc ba R = ρ·Ê{x²y − xy²} có kỳ vọng ρ²·skew(x)·(1 − ρ) > 0 khi x → y và skew(x) > 0, nên phải lật dấu để skewness dương trước.
- **Giới hạn đã biết của dạng skew:** nếu nguyên nhân x đối xứng mà chỉ nhiễu của y bị lệch, kỳ vọng của R bằng 0, nên dạng skew không có thông tin. Rule chọn dạng (S ≥ K) có thể rơi vào trường hợp này. Mình giữ nguyên thiết kế được giao, không sửa sau khi thấy số.
- Hướng `llm` đã dùng `lingam_measure` (dạng tanh, không gate) trên phần dư AR(1) của panel thật để làm proxy (docs/ext/llm.md). Hướng này không dùng lại kết quả đó.

## 2. File của hướng này (chỉ file mới)

| File | Vai trò |
|---|---|
| `src/paper4/ext_r4ngorient.py` | `tolerant_ngA` (NG-A, chính), `tolerant_ngB` (NG-B, phụ); hàm evidence `ng_evidence` |
| `experiments/ext/r4ngorient/laws.py` | Luật shock đơn vị phương sai, generator non-Gaussian (`simulate`), gán luật theo nút |
| `experiments/ext/r4ngorient/run_ng.py` | Driver riêng: dùng lại helper của `run_experiment.py`, sinh dữ liệu theo `shock`, xuất `runs.jsonl`, `pairs.npz`, `diag.jsonl` (evidence + nhãn truth gắn ngoài method), `audit.jsonl` (varsortability) |
| `experiments/ext/r4ngorient/unit_test.py` | Unit test gate 2 biến (trước mọi bank run) |
| `experiments/ext/r4ngorient/check_pairing.py` | Kiểm tra hàng `tolerant_v5_1` Gaussian trùng `results/ext_v51_eval/runs.jsonl` |
| `experiments/ext/r4ngorient/make_frozen.py` | Ghép factor frozen: v5_1 từ `frozen_v4_v51.json` nguyên văn + NG-A/NG-B từ calibration Gaussian D-07H |
| `experiments/ext/r4ngorient/analyze.py` | Rule ghi trước + mọi diagnostic (`--prefix` chọn họ run v1/v2) |
| `experiments/ext/r4ngorient/posthoc.py` | Post-hoc factor bằng nhau (viết sau kết quả v1, chỉ mô tả) |
| `experiments/ext/r4ngorient/make_configs.py` | Sinh config evaluation v1 kèm sha256 frozen |
| `experiments/ext/r4ngorient/real_panel.py` | Bảng mô tả non-Gaussianity của panel thật (không rule) |
| `experiments/configs/ext_r4ngorient_*.json` | Config |
| `results/ext_r4ngorient_*` | Kết quả |

## 3. Thiết kế method (cài đặt và các điều chỉnh trước khi đăng ký)

**Evidence cho cặp (u, v)** (`ng_evidence`):
- x, y là phần dư cấu trúc của u và v, lấy từ các phương trình **không chứa** term cùng kỳ u–v:
  - với BH candidate: phần dư của base fit f0 (u, v không kề nhau);
  - với cạnh pool u → v: phần dư của u từ base fit, và phương trình của v fit lại **bỏ u_t** (một OLS).
- Chuẩn hoá trên m dòng.
- **Gate.** JB_i = m(skew_i²/6 + exkurt_i²/24), p_i = exp(−JB_i/2) (đuôi χ²₂). Gate mở khi 1 − (1 − min(p_x, p_y))² < 0.10.
- **Chọn dạng.** S = m(skew_x² + skew_y²)/6, K = m(exkurt_x² + exkurt_y²)/24.
  - S ≥ K: dạng skew. Lật dấu từng biến cho skewness dương, rồi R = ρ·mean(x²y − xy²).
  - Ngược lại: dạng tanh R = ρ·mean(x·tanh y − tanh x·y), nhân −1 nếu exkurt trung bình của cặp < 0.
- R > 0 nghĩa là u → v.
- se(R) bằng delete-one-block jackknife trên 10 block dòng liên tiếp.
- p_uv = Φ(R/se), cắt về [0.05, 0.95]. Gate đóng thì p_uv = 0.5 đúng.

**Dùng evidence (NG-A).**
- Bước [3]: `rng.random() < p_uv` thay cho `< 0.5`; cycle check giữ nguyên.
- Bước [4]: thứ tự Plackett–Luce trên pool với trọng số w_e = 1 − p(chiều đang khai báo), bằng key Efraimidis–Spirakis U^(1/w_e). Sau đó lật k_rev cạnh đầu tiên không tạo chu trình.
- Mỗi bootstrap draw đều fit base terms trước (nhánh `tolerant` thêm một `fit_equations`), tính gate và p từ phần dư của draw đó, rồi mới rút cấu trúc và refit.
- Mọi phần khác giống hệt v5_1: switch TAU, targeted opening chọn lại mỗi draw với de-dup, BH, pool, 199 draw, percentile, PRESCALE 0.5.

**NG-B (phụ).** log-odds = evidence Gaussian + logit(p của NG-A), rồi qua logistic và cắt [0.05, 0.95]:
- cạnh pool e: dl_e (`ext_revlag3.orientation_evidence`) + logit(w_e), là log-odds cạnh bị đảo;
- BH candidate: log-likelihood Gaussian của hai phương trình u, v khi thêm u → v trừ khi thêm v → u (cùng term như draw sẽ fit) + logit(p_uv).

**Điều chỉnh so với đề xuất, ghi trước khi chạy D-07, kèm lý do:**
1. **Common random numbers.** NG-A và NG-B dùng chung stream bootstrap với v5_1 (`rng(ext_seed("tolerant_v5_1"))`, khoá `stream_of` trong config).
   - Bước [3] gọi RNG đúng số lần như v5_1.
   - Ở bước [4], khi mọi w_e = 0.5 (mọi gate đóng), module gọi chính `methods._flip_from`. Phân phối vẫn như đề xuất: ES key với trọng số bằng nhau cho permutation đều.
   - Hệ quả: khi gate đóng ở mọi draw, NG-A trả **đúng từng bit** kết quả v5_1. Nhờ vậy so sánh ghép cặp có phương sai nhỏ và kiểm tra no-harm có power.
   - Smoke trên D-07H xác nhận: ở cell none/extra, 100% cặp trùng.
2. **NG-B cho BH candidate.** Đề xuất chỉ nói "dl_e của revlag3", mà dl_e chỉ định nghĩa cho cạnh pool. Mình dùng log-likelihood Gaussian tương tự cho hai chiều của candidate (định nghĩa ở trên) và cắt NG-B về [0.05, 0.95] như NG-A.
3. **Jackknife.** Dạng (skew/tanh) và dấu lật lấy từ toàn mẫu và giữ cố định trong các subsample, để R không nhảy dạng giữa các block. Chuẩn hoá thì làm lại trong từng subsample.
4. **No-harm Gaussian: Holm qua 21 cell, không phải 19.** Lưới G có 3 T × (none + 6 cell hỏng) = 21 cell. Cell none/extra được giữ trong họ, vì NG-A ≡ v5_1 ở đó trừ width factor tune lại.
5. **Failure.** Cell không là WIN nếu số run thất bại của arm > số run thất bại của v5_1 + 1.
6. **Sensitivity factor ng_mix.** Calibration chỉ là phép nhân quanh trung điểm, nên IS với factor tune trên ng_mix D-07H được tính lại chính xác từ `pairs.npz` (half_mới = half/fac_cũ × fac_mới), không cần chạy lại D-07.

## 4. Những gì đã chạy TRƯỚC khi ghi phần đăng ký này (chỉ D-07H development)

1. **Smoke/timing** `ext_r4ngorient_smoke` (D-07H development, seed_base 20261102 + 700 000 để không trùng unit calibration, ng_mix, 3 unit, T 40/80/150, đủ 7 cell; 47.6 s với `--workers 3`).
   - **Đã xem:** thời gian theo method, trạng thái (63/63 ok mỗi method), NG-A ≡ v5_1 ở none/extra (identity check), và tỷ lệ gate mở theo T: 0.11–0.20 ở T40, khoảng 0.55 ở T80, khoảng 0.76–0.82 ở T150.
   - **Không xem** IS, coverage hay sai số.
2. Kiểm tra moment của các luật trong `laws.py` (2·10⁶ mẫu): đúng mean 0, var 1, skew và exkurt như thiết kế.

Chưa có gì chạy trên D-07.

## 5. Đăng ký trước

### 5.1 Unit test gate (`unit_test.py`, trước mọi bank run)

- **Mô hình:** LiNGAM 2 biến x → y, x = e₁, y = b·x + e₂, với e₁, e₂ độc lập cùng luật (đơn vị phương sai). Luật skewexp rút dấu ngẫu nhiên riêng cho từng biến ở mỗi rep.
- **Lưới:** b ∈ {0.3, 0.6}; m ∈ {38, 78, 148}; luật ∈ {laplace, t5, skewexp, uniform, gauss}, thêm t10 để mô tả; 500 rep mỗi ô; seed 20261104.
- Gọi `ng_evidence(x, y)` với x là nguyên nhân.
- **(i)** Tỷ lệ đúng chiều = tỷ lệ rep có p > 0.5 (gate đóng tính là **không đúng**). Yêu cầu ≥ 0.80 ở m = 148, b = 0.6 cho laplace và cho skewexp.
  - Nếu (i) hỏng vì tỷ lệ < 0.5 (dấu ngược), quy ước dấu được đảo **một lần**, ghi lại, và chạy lại test.
  - Nếu hỏng theo cách khác thì **dừng**: không bank run nào cho NG-A/NG-B.
- **(ii)** Với shock Gaussian, ở **mỗi** ô (b, m): tỷ lệ gate mở ≤ 0.12 và mean p ∈ [0.48, 0.52].
- **(iii)** Bất biến thang đo: với a, c = exp(U(−3, 3)) > 0, |p(a·x, c·y) − p(x, y)| ≤ 1e−9 và gate trùng, trên mọi rep của mọi ô. Thêm hai mục chỉ để báo: thang âm, và tính phản đối xứng p(y, x) = 1 − p(x, y).
- Unit test đạt khi (i), (ii), (iii) cùng đạt.

### 5.2 Calibration (Gaussian, D-07H development)

- `ext_r4ngorient_cal_gauss`: D-07H development, 20 topology × 1 replicate, unit seed_base 20261102 + 500 000 như runner, T 40/80/150, kind extra/missing/reversed × 0.2/0.5 + none. Method: `tolerant_ngA`, `tolerant_ngB` trên stream của v5_1.
- Factor chọn đúng như `run_experiment.calibrate`, theo (method, T, width_key).
- Gộp vào `experiments/ext/r4ngorient/frozen_ngorient.json` bằng `make_frozen.py`: `tolerant_v5_1|*` và `mod|*` chép nguyên văn từ `experiments/ext/v51/frozen_v4_v51.json` (đủ key T 40/80/150 × 4 kind), cộng `tolerant_ngA|*` và `tolerant_ngB|*` mới. Sha256 được ghi ở mục 6 trước evaluation.
- **Kiểm tra driver:** factor NG-A ở none/extra phải bằng factor v5_1 frozen, vì method trùng từng bit và stream trùng. Lệch thì báo là lệch driver; rule không đổi.
- **Sensitivity (mô tả):** `ext_r4ngorient_cal_ngmix` giống hệt nhưng shock ng_mix, method v5_1 + NG-A + NG-B.

### 5.3 Evaluation runs (D-07 development, seed_base 20261102, 20 topology × 3 replicate, H 4, lag_max 2, n_boot 199, τ 0.1, `--workers 3`)

| Run | Shock | T | Cell | Method |
|---|---|---|---|---|
| `ext_r4ngorient_gauss` | gauss | 40, 80, 150 | none + {extra, missing, reversed} × {0.2, 0.5} | oracle, tolerant_v5_1, tolerant_ngA, tolerant_ngB |
| `ext_r4ngorient_ngmix` | ng_mix | 40, 80, 150 | như trên | như trên |
| `ext_r4ngorient_t10` | ng_t10 | 80, 150 | missing-0.2, reversed-0.2 (c_idx giữ như lưới đầy đủ) | như trên |

- Factor: v5_1 dùng factor frozen của nó, NG-A/NG-B dùng `frozen_ngorient.json`. Oracle là raw.
- `oracle_cal` = oracle nới quanh trung điểm bằng 1.4/1.3/1.2 (`analyze_lag.OCAL`, như revlag3).

**Điều kiện hợp lệ (validity):**
- V1: unit test 5.1 đạt.
- V2: mọi hàng `tolerant_v5_1` của `ext_r4ngorient_gauss` trùng hàng tương ứng của `results/ext_v51_eval/runs.jsonl` (cùng topology, replicate, T, kind, rate) trên status, n_nonnull, n_covered_nonnull, iscore_nonnull_mean (|Δ| ≤ 1e−9), width_kept. Nếu không trùng, run Gaussian không ghép cặp được với run đã lưu; kết luận vẫn tính trên v5_1 chạy lại trong cùng run, nhưng phải báo.
- V3: tỷ lệ gate mở của NG-A trên bank Gaussian, gộp mọi T, cell, draw và cặp được đánh giá, ≤ 0.15.

**Thống kê.**
- Đơn vị là run (topology × replicate × T × cell). IS của run = mean IS trên cặp non-null; IS của cell = mean trên các run mà cả hai method đều ok.
- dIS = mean ghép cặp (arm − v5_1). CI 95% bằng cluster bootstrap theo topology (20 cụm), B = 20000, seed 20261104, percentile.
- p một phía:
  - cho "arm tốt hơn": tỷ lệ resample có dIS ≥ 0, sàn 1/B;
  - cho "arm tệ hơn": tỷ lệ resample có dIS ≤ 0.
- Coverage = n_covered_nonnull / n_nonnull, gộp trên các run ok. IS ratio = IS arm / IS v5_1 trên run ghép cặp.

**Rule cho mỗi arm (NG-A chính, NG-B cùng rule):**
- **Cell chính:** ng_mix × T {80, 150} × {missing, reversed} × {0.2, 0.5}, tổng 8 cell.
- **WIN.** Một cell là WIN khi đủ ba điều kiện:
  - Holm (0.05, họ 8 cell của arm đó) bác H0 "dIS ≥ 0";
  - coverage của arm ≥ 0.90;
  - số run thất bại của arm ≤ số của v5_1 + 1.
- **RETAINED (exploratory)** khi đủ cả năm điều kiện:
  - (1) WIN ≥ 3/8;
  - (2) coverage ≥ 0.90 ở cả 8 cell chính;
  - (3) no-harm (a): ở **mọi** cell của lưới Gaussian (21 cell), IS ratio ≤ 1.03 **và** không có cell nào tệ hơn có ý nghĩa (Holm 0.05 qua 21 cell, H0 "dIS ≤ 0");
  - (4) no-harm (b): ở 13 cell ng_mix ngoài cell chính (cả 7 cell của T40, cộng none/extra-0.2/extra-0.5 ở T80 và T150), IS ratio ≤ 1.05, và coverage của arm ≥ 0.90 ở mọi cell mà v5_1 đạt ≥ 0.90;
  - (5) V1, V3 đạt.
  Ngược lại là **REJECTED**.
- **NG-B so với NG-A:** NG-B chỉ được giữ **thay** NG-A khi NG-B RETAINED **và** thắng NG-A ở ≥ 2/8 cell chính (Holm 0.05 qua 8, H0 "dIS(B − A) ≥ 0").
- **Phụ (báo, không quyết định):** coverage trên cặp affected (định nghĩa red team: dC ≥ 0.05, `run_pairs.delta_C`), Δ = cov(arm) − cov(v5_1) ở 4 cell reversed chính của ng_mix. CI cluster bootstrap B = 20000, seed 20261104; p một phía H0 Δ ≤ 0, Holm qua 4. Kèm closed share = Δ / (cov(oracle_cal) − cov(v5_1)) và gap cov(arm) − cov(oracle_cal). Bảng tương tự cho cell missing và cho lưới Gaussian (mô tả).

**Diagnostic (mô tả, không quyết định):**
- tỷ lệ gate mở theo shock × T × kind (theo draw và ở mức dữ liệu);
- với BH candidate là cạnh cùng kỳ thật bị xoá (missing, true_lag 0) và được repair: tỷ lệ draw có chiều đúng (v5_1 kỳ vọng khoảng 0.5), và tỷ lệ p_uv > 0.5 ở mức dữ liệu;
- AUROC của w_e (xác suất cạnh pool bị đảo) với nhãn "cạnh pool thật sự bị đảo", theo shock × T: cho NG-A, cho NG-B, và cho dl_e Gaussian riêng (đối chiếu 0.83–0.88 của revlag3). Kèm tần suất lật theo draw của cạnh bị đảo so với không bị đảo;
- varsortability và R²-sortability của chuỗi quan sát (summary graph và đồ thị cùng kỳ) theo shock × T;
- ng_t10: dIS, coverage, gate rate;
- sensitivity: dIS ở 8 cell chính khi mọi factor (v5_1, NG-A, NG-B) tune lại trên ng_mix D-07H;
- thời gian chạy theo method.

**Dự đoán ghi trước:**
- Gate ng_mix mở khoảng 10–20% ở T40, khoảng 50–60% ở T80, khoảng 80% ở T150 (từ smoke).
- NG-A đúng chiều tốt hơn ngẫu nhiên ở T ≥ 80. IS giảm ở cell reversed rõ hơn ở cell missing (missing có ít cạnh cùng kỳ thật bị xoá: q0 = 0.3).
- Theo bài học của revlag3, coverage trên cặp affected có thể không tăng.
- Gaussian: NG-A ≈ v5_1 trong sai số MC.
- Mình không dám đoán WIN ≥ 3/8; khả năng cao nhất là 1–4/8.

### 5.4 Panel thật (mô tả, không rule)

- **Dữ liệu:** `ACIIDS/02_observational_data/processed/core14_provenance.csv` (chỉ đọc), quý 2020Q2–2024Q4. Transform như `experiments/ext/llm/signal_quality.transformed_panel`: sai phân bậc 1 cho 8 cột trong `DIFF`, mức cho 6 cột còn lại, ra 18 dòng.
- **Kiểm tra chéo:** giá trị phải bằng `candidate_quarterly_matrix_raw.csv`.
- **Skeleton khai báo:** 21 cạnh prior Paper 1 (induced subgraph của `prior_graph_final_278.json`, acyclic).
- **Phương trình, lag_max 1:** own lag + lag của các nút kề + cha cùng kỳ. Nếu phương trình underdetermined (số regressor + 2 > m), dùng own lag + cha cùng kỳ. Với lag_max 1 còn m = 17 dòng (đề xuất ghi 18 dòng, đó là số dòng trước khi lấy lag).
- **Bảng theo nút:** skewness, excess kurtosis, JB, p của JB tiệm cận, p của JB theo Monte Carlo chính xác (10⁴ mô phỏng Gaussian qua cùng ma trận thiết kế), p Shapiro–Wilk, Holm qua 14 (cho p JB MC và cho p SW).
- Báo riêng hai nhóm: 7 nút real/derived_from_real (macro, stock) và 7 nút banking simulated_calibrated/derived_from_simulated (phản ánh simulator calibration, không phải thực tế).
- **Power Monte Carlo của JB (MC critical value, mức 0.05) ở m = 17 và 18** cho từng luật của ng_mix và t10 (mẫu iid, 10⁴ lần), để đọc đúng một kết quả "không bác bỏ".
- Không làm Mardia đa biến.

## 6. Nhật ký chạy (ghi theo thứ tự)

Mọi mục được ghi ngay sau khi chạy. Phần 1–5 ở trên được ghi xong trước mục 6.1.

**6.1 Unit test** (`unit_test.py`, 22 s; `results/ext_r4ngorient_unittest/unit_test.md`), chép nguyên văn:
- "(i) đúng chiều ở m 148, b 0.6: {'laplace': 0.946, 'skewexp': 0.91} -> ĐẠT"
- "(ii) Gaussian: gate mở ≤ 0.12 và mean p ∈ [0.48, 0.52] ở cả 6 ô -> ĐẠT" (gate mở 0.056–0.078; mean p 0.498–0.510)
- "(iii) max |Δp| thang dương = 4.00e-15, gate lệch 0 -> ĐẠT"
- "Báo thêm: max |Δp| thang âm = 4.00e-15; max |p(y,x) − (1 − p(x,y))| = 7.77e-16"
- "**Unit test: PASS**". Không cần đảo dấu.

Ghi chú mô tả từ cùng bảng:
- Luật uniform ở m = 38 không bao giờ mở gate (JB tiệm cận rất bảo thủ với phân phối platykurtic); ở m = 78, gate mở 0.13–0.14.
- t10 ở m = 148 chỉ mở gate 0.48–0.59, tỷ lệ đúng chiều 0.36–0.42.
- Tỷ lệ đúng chiều khi gate mở là 0.67–1.00 tuỳ luật.

**6.2 Panel thật** (`real_panel.py`, 1.3 s; `results/ext_r4ngorient_realpanel/real_panel.md`). Bảng mô tả, xem mục 8.

**6.3 Calibration Gaussian D-07H development** (`ext_r4ngorient_cal_gauss`, 410.2 s, `--workers 3`, 20 unit).
- Factor (đã gồm PRESCALE 0.5), theo thứ tự T 40/80/150 × none/extra/missing/reversed:
  - NG-A: 2.6/2.6/2.3/2.6, 2.6/2.4/2.5/2.6, 2.4/2.4/2.4/2.6;
  - NG-B: 2.6/2.6/2.3/2.7, 2.6/2.4/2.5/2.7, 2.4/2.4/2.3/2.6;
  - v5_1 frozen để so: 2.6/2.6/2.3/2.8, 2.6/2.4/2.6/2.7, 2.4/2.4/2.3/2.4.
- **Kiểm tra driver đạt:** factor NG-A ở none/extra trùng v5_1 frozen ở cả 6 key.
- `experiments/ext/r4ngorient/frozen_ngorient.json` sha256 `68b42d47bae60bcb0304d2b3d880a66ef2de170a4fbfd61708e302c2784cf63d`. File này được ghi trước mọi run D-07; config evaluation kiểm hash này.

**6.4 Calibration ng_mix D-07H development** (`ext_r4ngorient_cal_ngmix`, 860.6 s, chạy song song với 6.5).
- Dùng cho sensitivity (mô tả). Factor, theo thứ tự T 40/80/150 × none/extra/missing/reversed:
  - v5_1: 3.0/2.8/2.5/3.2, 2.8/2.8/2.5/3.0, 2.4/2.4/2.2/2.4;
  - NG-A: 3.0/2.8/2.5/3.2, 2.8/2.8/2.5/3.1, 2.4/2.4/2.3/2.5;
  - NG-B: 3.0/2.8/2.5/3.2, 2.8/2.8/2.5/3.0, 2.4/2.4/2.3/2.5.
- Ở T40/80, factor của mọi method trên ng_mix **lớn hơn** factor Gaussian (ví dụ v5_1 none ở T40: 3.0 so với 2.6). Residual bootstrap phủ thấp hơn khi shock có đuôi dày; đây là quan sát về v5_1, không riêng arm mới.

**6.5 Evaluation Gaussian** (`ext_r4ngorient_gauss`, 2148.0 s, 5040 hàng).
- Vượt mục tiêu 30 phút vì chạy song song với 6.4 trên cùng máy; lưới không bị cắt.
- **V2 đạt:** 1260/1260 hàng `tolerant_v5_1` trùng `results/ext_v51_eval/runs.jsonl`, 0 field lệch (`results/ext_r4ngorient_gauss/pairing.json`).

**6.6** `ext_r4ngorient_ngmix` khởi chạy sau 6.4; `ext_r4ngorient_t10` khởi chạy sau 6.5, song song với 6.6.

**6.7 Evaluation ng_mix và ng_t10.**
- `ext_r4ngorient_ngmix`: 1998.9 s, 5040 hàng. `ext_r4ngorient_t10`: 709.5 s, 960 hàng.
- Hai run chạy song song nên vượt 30 phút; lưới không bị cắt. Mọi method ok 60/60 ở mọi cell của cả ba run.

**6.8 Kết quả v1 theo rule đã đăng ký** (`analyze.py`, `results/ext_r4ngorient_analysis/ruling.md`), chép nguyên văn:
- Validity:
  - "V1 unit test: PASS"
  - "V2 ghép cặp v5_1 với results/ext_v51_eval: True (shared 1260, field mismatch 0)"
  - "V3 tỷ lệ gate mở của NG-A trên bank Gaussian (mọi T, cell, draw, cặp): 0.1271 (108878/856486) -> đạt (≤ 0.15)"
- "**Verdict NG-A:** WIN 0/8 (Holm qua 8); coverage ≥ 0.90 ở cả 8 cell chính: có; no-harm (a): KHÔNG đạt; no-harm (b): KHÔNG đạt; validity (V1, V3): đạt -> **REJECTED**."
- "**Verdict NG-B:** WIN 1/8 (Holm qua 8); coverage ≥ 0.90 ở cả 8 cell chính: có; no-harm (a): KHÔNG đạt; no-harm (b): đạt; validity (V1, V3): đạt -> **REJECTED**."
- "NG-B thắng NG-A ở 1/8 cell; NG-B thay NG-A: **không**."

**v1: cả NG-A và NG-B đều REJECTED.** Số chi tiết ở mục 8.

**6.9 Post-hoc (viết SAU khi thấy kết quả v1, chỉ mô tả, không đổi verdict)** (`posthoc.py`, `results/ext_r4ngorient_analysis/posthoc_equal_factor.md`).
- Đưa interval của arm về đúng factor frozen của v5_1 (phép đổi chính xác).
- Kết quả: "NG-A: WIN 3/8; no-harm (a) đạt []; no-harm (b) đạt []." và "NG-B: WIN 3/8; no-harm (a) đạt []; no-harm (b) đạt []."
- Diễn giải: lỗi no-harm của v1 nằm ở Gaussian T150. Đó là các cell mà factor tune lại của arm lớn hơn của v5_1 (reversed 2.6 so với 2.4; missing 2.4 so với 2.3). Factor là noise của calibration trên 20 unit với bước 0.05. Orientation không phải nguyên nhân.
- Vì quy tắc "post-hoc tìm ra" này chọn sau khi thấy số, dữ liệu v1 **không** được dùng để đánh giá nó. Xem mục 7.

## 7. Version 2 (`ngorient v2`): đăng ký trước, SAU khi có kết quả v1 và post-hoc 6.9

**Thay đổi duy nhất so với v1:** NG-A và NG-B **không tune lại width factor**. Chúng dùng factor frozen của v5_1 cho cùng (T, width_key). Code method không đổi (`src/paper4/ext_r4ngorient.py`, cùng file).

**Lý do (không phụ thuộc kết quả, nhưng được gợi ý bởi post-hoc nên phải công bố):**
- Arm bằng v5_1 từng bit ở none/extra và khi mọi gate đóng.
- Factor là sửa lỗi small-sample của bootstrap theo (T, kind); không có lý do nó đổi khi chỉ đổi đồng xu orientation.
- Tune lại trên 20 unit D-07H thêm noise factor cỡ ±0.1 (raw), lớn hơn hiệu ứng cần đo.

**Frozen:** `experiments/ext/r4ngorient/frozen_ngorient_v2.json` = `frozen_v4_v51.json` nguyên văn + `tolerant_ngA|*` = `tolerant_ngB|*` = `tolerant_v5_1|*`. Sha256 ghi ở 7.1 trước khi chạy.

**Dữ liệu mới:** D-07 development (cùng 20 topology), **seed_base 50261102**, chưa run nào dùng (đã grep mọi config và manifest: các seed đã dùng là 20261101, 20261102, 20961102, 30261102). Vì vậy truth, skeleton hỏng và dữ liệu đều mới. Topology vẫn là của D-07 nên kết quả vẫn **exploratory**, không phải xác nhận.

**Run** (20 × 3, T 40/80/150, đủ 7 cell, n_boot 199, method oracle, v5_1, NG-A, NG-B, `stream_of` như v1, `--workers 3`):
- `ext_r4ngorient_v2_ngmix`;
- `ext_r4ngorient_v2_gauss`.
ng_t10 không chạy lại.

**Rule:** giống hệt 5.3. Cùng 8 cell chính, WIN (Holm qua 8 + coverage ≥ 0.90 + failure), RETAINED (WIN ≥ 3/8, coverage ≥ 0.90 ở 8 cell, no-harm (a) qua 21 cell Gaussian với ratio ≤ 1.03 và Holm, no-harm (b) qua 13 cell ng_mix), NG-B thay NG-A khi thắng ≥ 2/8. Cùng B = 20000, seed 20261104. Phần phụ và diagnostic giống v1.

**Validity:**
- V1 đã đạt.
- V3 tính trên `ext_r4ngorient_v2_gauss`.
- V2 (ghép cặp với run đã lưu) không áp dụng vì seed mới. Thay vào đó, arm phải bằng v5_1 ở mọi run none/extra ("share identical" = 1.00 ở 9 cell × 2 shock).

**Dự đoán ghi trước:**
- Post-hoc 6.9 cho WIN 3/8, nhưng con số đó đã tận dụng dữ liệu v1. Trên dữ liệu mới, mình dự đoán WIN 1–3/8, tập trung ở T150 reversed.
- Có nguy cơ hồi quy về trung bình, nên RETAINED khoảng 50/50.

**7.1** `frozen_ngorient_v2.json` sha256 `6d4dc22e50ef392467387627d9cdc512bbce7ae83c39bc95a21fd266c779866d`. Config `experiments/configs/ext_r4ngorient_v2_{ngmix,gauss}.json`. Hai run khởi chạy song song ngay sau khi ghi mục 7 và dòng này.

## 8. Số chi tiết v1 (D-07 development, seed_base 20261102; mọi số ở `results/ext_r4ngorient_analysis/ruling.md` và `posthoc_equal_factor.md`)

### 8.1 Cell chính ng_mix (8 cell), NG-A − v5_1

| T | cell | cov NG-A / v5_1 | IS NG-A / v5_1 | dIS [CI] | p Holm (8) | dIS khi factor bằng nhau (post-hoc) |
|---|---|---|---|---|---|---|
| 80 | missing-0.2 | 0.954 / 0.957 | 2.807 / 2.840 | −0.033 [−0.061, −0.002] | 0.141 | −0.010 [−0.027, +0.006] |
| 80 | missing-0.5 | 0.963 / 0.970 | 2.987 / 3.003 | −0.016 [−0.087, +0.064] | 0.987 | +0.023 [−0.041, +0.089] |
| 80 | reversed-0.2 | 0.941 / 0.946 | 2.778 / 2.840 | −0.062 [−0.130, +0.012] | 0.349 | −0.056 [−0.120, +0.011] |
| 80 | reversed-0.5 | 0.935 / 0.942 | 2.860 / 2.889 | −0.029 [−0.077, +0.027] | 0.691 | −0.018 [−0.054, +0.023] |
| 150 | missing-0.2 | 0.968 / 0.963 | 1.836 / 1.823 | +0.013 [−0.001, +0.026] | 1.000 | −0.015 [−0.031, −0.001] |
| 150 | missing-0.5 | 0.970 / 0.963 | 1.971 / 1.965 | +0.006 [−0.021, +0.030] | 1.000 | −0.029 [−0.052, −0.007] |
| 150 | reversed-0.2 | 0.968 / 0.949 | 1.868 / 1.902 | −0.035 [−0.083, +0.009] | 0.379 | −0.088 [−0.131, −0.047] |
| 150 | reversed-0.5 | 0.957 / 0.931 | 1.992 / 2.034 | −0.042 [−0.125, +0.027] | 0.691 | −0.082 [−0.141, −0.031] |

- NG-B có WIN duy nhất ở T80 reversed-0.2: −0.079 [−0.130, −0.033], p Holm 0.0016.
- **No-harm (a) hỏng.**
  - NG-A tệ hơn có ý nghĩa ở Gaussian T150 missing-0.2 (+0.030 [+0.017, +0.044]), missing-0.5 (+0.039) và reversed-0.2 (+0.069, ratio 1.038), p Holm 0.0011 mỗi cell.
  - NG-B tệ hơn ở Gaussian T150 reversed-0.2 (+0.045 [+0.018, +0.071], p Holm 0.0053).
  - Khi factor bằng nhau, cả bốn hiệu này về 0: −0.000, +0.003, +0.016 [−0.013, +0.045] cho NG-A, và +0.010 cho NG-B.
- **No-harm (b) của NG-A hỏng** ở ng_mix T40 reversed-0.5: coverage 0.899 so với 0.912 của v5_1. Khi factor bằng nhau, cell này có coverage 0.917.

### 8.2 Evidence có thật không? (diagnostic, mức dữ liệu và mức draw)

**Gate mở theo draw:**
- Gaussian: 0.066–0.082 ở T40, 0.10–0.12 ở T80, 0.17–0.18 ở T150. Gộp 0.127, đạt V3, nhưng ở T150 vượt mức danh nghĩa 0.10 (JB trên phần dư hồi quy, nhiều cặp đánh giá lặp).
- ng_mix: 0.11–0.17 / 0.41–0.47 / 0.77–0.78.
- ng_t10: 0.23–0.25 / 0.44.

**Cạnh cùng kỳ thật bị xoá, được repair (ng_mix), tỷ lệ draw chọn đúng chiều:**
- NG-A: 0.557 / 0.582 / 0.669 ở T40/80/150.
- NG-B: 0.538 / 0.638 / 0.730.
- Đối chiếu Gaussian NG-A (gần như v5_1): 0.54. Cycle check đã ép một phần chiều.

**Cạnh pool thật sự bị đảo (AUROC của xác suất bị đảo):**

| shock | T | NG-A | NG-B | dl Gaussian (revlag3) |
|---|---|---|---|---|
| gauss | 40 / 80 / 150 | 0.48 / 0.50 / 0.48 | 0.65 / 0.82 / 0.84 | 0.66 / 0.82 / 0.85 |
| ng_mix | 40 / 80 / 150 | 0.55 / 0.67 / 0.78 | 0.66 / 0.82 / 0.91 | 0.63 / 0.78 / 0.85 |
| ng_t10 | 80 / 150 | 0.56 / 0.62 | 0.84 / 0.88 | 0.84 / 0.86 |

**Đọc bảng:**
- Evidence non-Gaussian có thật và tăng theo T.
- Ngay cả trên ng_mix, nó **yếu hơn** evidence Gaussian của revlag3. Lý do: trong lưới này hai phương trình có lag set khác nhau, nên hai chiều không tương đương Gaussian.
- Ghép hai nguồn (NG-B) cho AUROC cao nhất: 0.91 ở ng_mix T150.
- Revlag3 đã cho thấy evidence Gaussian dùng một mình không đóng được gap coverage.

**Cặp affected (phụ, ng_mix):**
- NG-A − v5_1 ở T150: +0.078 [+0.040, +0.117] (rev-0.2) và +0.055 [+0.027, +0.082] (rev-0.5), p Holm 0.0002. Closed share 0.50.
- Phần lớn đến từ interval rộng hơn (factor 2.6 so với 2.4); Gaussian T150 cũng tăng +0.047 / +0.027.
- Khi factor bằng nhau còn lại +0.052 [+0.013, +0.095] (rev-0.2) và +0.023 [−0.002, +0.046] (rev-0.5) trên ng_mix, so với +0.004 / +0.000 trên Gaussian. Đây là phần do orientation, đúng theo hướng giả thuyết.
- Ở T40/80 không có cải thiện.

**Varsortability:**
- Varsortability của chuỗi quan sát là 0.89–0.94 ở mọi bank (cả Gaussian). Dữ liệu mô phỏng có varsortability cao, như Reisach et al. cảnh báo. R²-sortability là 0.53–0.59.
- Method không dùng phương sai: evidence bất biến thang đo đến 4e−15 (unit test iii). Nên varsortability cao không thể là nguồn lợi của NG-A, nhưng là một cảnh báo cho các baseline dựa trên sắp xếp phương sai.

**Sensitivity (factor tune lại trên ng_mix D-07H):**
- NG-A − v5_1 ở T150 reversed: −0.064 [−0.109, −0.023] và −0.067 [−0.138, −0.007].
- NG-B ở T80 reversed-0.2: −0.082 [−0.127, −0.040].
- Mọi factor ng_mix ở T40/80 lớn hơn factor Gaussian. Residual bootstrap phủ kém hơn khi shock có đuôi dày, và điều này đúng cho cả v5_1.

**Thời gian** (tổng CPU trong method, ng_mix): v5_1 1371 s, NG-A 1990 s (+45%), NG-B 2556 s (+86%).

### 8.3 Panel thật (mô tả, `results/ext_r4ngorient_realpanel/real_panel.md`)

- m = 17 dòng phần dư. Không phương trình nào cần fallback. Kiểm tra chéo với ma trận raw: khớp tuyệt đối.
- **Nút real:**
  - chỉ `macro_gdp_yoy_pct` có p < 0.05 chưa hiệu chỉnh (skew −0.83, exkurt +2.82, p MC 0.028, p SW 0.012);
  - sau Holm qua 14 không nút nào bác bỏ (p MC Holm nhỏ nhất 0.395).
- **Nút banking** (dữ liệu simulator): không nút nào bác bỏ; p MC nhỏ nhất 0.052.
- **Power của JB ở m = 17:** laplace 0.28, t5 0.20, skewexp 0.56, uniform 0.004, t10 0.11. Vì vậy "không bác bỏ" **không** có nghĩa là Gaussian: JB gần như không có power ở cỡ mẫu này.
- Gate của module mở ở 4/21 cạnh khai báo.
- **Kết luận mô tả:** trên panel thật, NG-A gần như sẽ là v5_1 (gate hầu hết đóng). Không đọc chiều nào từ panel thật.

## 9. Kết quả v2 (dữ liệu mới, seed_base 50261102), chép nguyên văn từ `results/ext_r4ngorient_v2_analysis/ruling.md`

**Run.** `ext_r4ngorient_v2_gauss` 876.7 s, `ext_r4ngorient_v2_ngmix` 962.2 s, mỗi run 5040 hàng; mọi method ok 60/60 ở mọi cell.

**Validity:**
- "V1 unit test: PASS"
- "V3 tỷ lệ gate mở của NG-A trên bank Gaussian (mọi T, cell, draw, cặp): 0.1256 (107070/852302) -> đạt (≤ 0.15)"
- Kiểm tra thay V2: arm bằng v5_1 từng bit ở 18/18 cell none/extra (2 shock × 3 T × 3 cell) cho cả NG-A và NG-B.

**Verdict:**
- "**Verdict NG-A:** WIN 2/8 (Holm qua 8); coverage ≥ 0.90 ở cả 8 cell chính: có; no-harm (a): đạt; no-harm (b): đạt; validity (V1, V3): đạt -> **REJECTED**."
- "**Verdict NG-B:** WIN 3/8 (Holm qua 8); coverage ≥ 0.90 ở cả 8 cell chính: có; no-harm (a): KHÔNG đạt; no-harm (b): đạt; validity (V1, V3): đạt -> **REJECTED**."
- "NG-B thắng NG-A ở 0/8 cell; NG-B thay NG-A: **không**."

**v2: cả hai arm đều REJECTED.** Không có Frozen spec. Không spec manifest nào được tạo.

**Chi tiết v2, NG-A − v5_1, 8 cell chính ng_mix** (dIS [CI], p Holm 8):
- T80:
  - missing-0.2: −0.017 [−0.039, +0.006], 0.153
  - **missing-0.5: −0.084 [−0.165, −0.019], 0.016 (WIN)**
  - reversed-0.2: −0.051 [−0.104, −0.004], 0.063
  - reversed-0.5: −0.064 [−0.123, −0.007], 0.063
- T150:
  - missing-0.2: −0.009 [−0.024, +0.006], 0.153
  - missing-0.5: −0.038 [−0.069, −0.006], 0.061
  - **reversed-0.2: −0.078 [−0.126, −0.032], 0.0028 (WIN)**
  - reversed-0.5: −0.033 [−0.070, +0.004], 0.116
- Coverage NG-A 0.934–0.971 so với v5_1 0.925–0.967. IS ratio 0.958–0.995.
- Cả 8 điểm ước lượng đều âm, nhưng chỉ 2 cell qua Holm; ngưỡng đã ghi là 3.

**NG-B:**
- WIN ở T80 reversed-0.2 (−0.082), T150 missing-0.5 (−0.046) và T150 reversed-0.2 (−0.062).
- Hỏng no-harm (a) ở Gaussian T150 reversed-0.5: ratio 1.032 > 1.03, dIS +0.064 [+0.011, +0.130]. p Holm 0.137, không ý nghĩa, nhưng ratio vượt ngưỡng ghi trước.

**Phụ: cặp affected, ng_mix, NG-A − v5_1** (Holm qua 4):
- T80 rev-0.2: +0.021 [+0.000, +0.045], p Holm 0.042
- T150 rev-0.2: +0.034 [+0.007, +0.063], p Holm 0.023
- T80 rev-0.5: +0.018 [+0.007, +0.028], p Holm 0.009
- T150 rev-0.5: +0.013 [+0.002, +0.023], p Holm 0.029
- **4/4 có ý nghĩa.** Closed share 0.14–0.38 so với oracle_cal. Gap còn lại −0.030 đến −0.081.
- Cùng các cell đó trên Gaussian: −0.021 đến +0.002 (không cải thiện, đúng như kỳ vọng khi gate đóng).
- NG-B không cải thiện cặp affected (−0.015 đến +0.012).

**Diagnostic v2 lặp lại v1:**
- AUROC cạnh pool bị đảo trên ng_mix: NG-A 0.58 / 0.72 / 0.78, NG-B 0.61 / 0.85 / 0.88, dl Gaussian 0.58 / 0.81 / 0.84. Gaussian: NG-A 0.49–0.52.
- Draw đúng chiều cho cạnh cùng kỳ bị xoá (ng_mix): NG-A 0.548 / 0.606 / 0.679.
- v5_1 phủ 0.922–0.967 trên ng_mix (v2) và 0.912–0.970 (v1) với factor Gaussian.

## 10. Kết luận

1. **Verdict theo rule ghi trước:**
   - v1: NG-A REJECTED, NG-B REJECTED.
   - v2 (dữ liệu mới, không tune lại factor): NG-A REJECTED (WIN 2/8, cần 3), NG-B REJECTED (no-harm (a), ratio 1.032).
   - Không có module mới; `tolerant_v5_1` vẫn là module of record. Không có Frozen spec.
2. **Điều được ủng hộ (exploratory, D-07 development):**
   - Evidence non-Gaussian có thật. Unit test đạt, chiều đúng tăng theo T, AUROC 0.67–0.78 ở T ≥ 80 trên ng_mix.
   - Đặt sau gate thì nó gần như không làm hại dưới Gaussian, khi factor không bị tune lại (no-harm v2 đạt cả 34 cell).
   - Trên ng_mix ở T ≥ 80, NG-A giảm IS 1–4% ở cả 8 cell chính trong v2 (2 cell qua Holm). Ở v1, khi factor bằng nhau, các cell T150 cũng cho kết quả tương tự.
   - Đây là method đầu tiên trong dự án **thu hẹp có ý nghĩa** gap coverage trên cặp chịu ảnh hưởng của cạnh đảo mà không đổi width: v2 4/4 cell, closed share 0.14–0.38. Revlag3 với evidence Gaussian không làm được.
   - Hiệu ứng nhỏ, chỉ có khi shock thật sự non-Gaussian và T ≥ 80.
3. **Điều không được ủng hộ:**
   - Thắng ở ≥ 3/8 cell.
   - Bất kỳ lợi ích nào ở T40 (gate gần như luôn đóng).
   - Lợi ích ở ng_t10 (khi factor bằng nhau: T150 reversed −0.033 [−0.085, +0.018], còn lại xấp xỉ 0).
   - NG-B (ghép evidence Gaussian) tốt hơn NG-A: 0/8 ở v2.
4. **Bài học về calibration (quan trọng cho paper):**
   - Tune lại width factor trên 20 unit D-07H với bước 0.05 tạo noise đủ lớn để làm hỏng no-harm. v1 hỏng ở Gaussian T150 hoàn toàn vì factor 2.6 so với 2.4.
   - Đây là bằng chứng cụ thể cho điểm yếu "width factor tune trên bank" mà reviewer có thể nêu. Biến thể nào khác v5_1 chỉ ở phần cấu trúc nên kế thừa factor của v5_1, thay vì tune lại.
5. **Sản phẩm phụ dùng được cho paper (exploratory):** `tolerant_v5_1` với factor Gaussian frozen vẫn phủ 0.912–0.970 dưới shock non-Gaussian hỗn hợp, và 0.952–0.969 dưới t10, ở mọi cell được thử. Đây là robustness check trước đây chưa có ("chỉ Gaussian tuyến tính").
6. **Panel thật:** JB không có power ở m = 17 (power 0.004–0.56). Không có nút real nào bác bỏ normality sau Holm. Gate mở 4/21. Trên dữ liệu thật hiện có, hướng này không giúp được gì.
7. **Nếu muốn đi tiếp** (cần quyết định của người dùng, không làm ở đây):
   - một v3 với rule mới, ví dụ ngưỡng WIN dựa trên tổng hợp qua 8 cell thay vì đếm cell;
   - kiểm tra trên bank niêm phong mới (P4-H3).
   Mọi số hiện tại đều đã thấy, nên không được dùng để chọn rule cho chính chúng.

## 11. Bug và quan sát về file có sẵn (không sửa)

- Không thấy bug mới trong `ext_v51.py`, `ext_narrow.py`, `methods.py`, `estimator.py`, `run_experiment.py`.
  - Driver riêng tái lập 1260/1260 hàng v5_1.
  - Factor calibration của driver trùng factor frozen của v5_1 ở 6/6 key none/extra.
- **Quan sát (không phải bug):**
  - Docstring `methods.tolerant` và TONG_HOP mục 3 nói chiều cạnh repair "không xác định được từ dữ liệu". Điều này chỉ đúng với một cạnh cùng kỳ đứng riêng dưới shock Gaussian. Trong lưới hiện tại, evidence Gaussian theo lag set đã cho AUROC khoảng 0.8 (revlag3 và mục 8.2). Dưới shock non-Gaussian, chiều identify được.
  - Factor calibration của mọi method trên ng_mix lớn hơn trên Gaussian ở T40/80. Residual bootstrap phủ thấp hơn khi shock có đuôi dày.
- Bug E1 (seed theo vị trí cell) vẫn còn. Driver giữ c_idx của lưới đầy đủ để không bị ảnh hưởng. Riêng oracle trong run ng_t10 được fit ở cell đầu tiên có chạy (missing-0.2), nên stream oracle khác run đầy đủ; oracle chỉ dùng để tham chiếu.

## 12. Split đã dùng

- D-07H development: smoke (seed_base 20261102 + 700 000, 3 unit), calibration Gaussian và ng_mix (seed_base 20261102 + 500 000, 20 unit mỗi run).
- D-07 development: v1 seed_base 20261102 (gauss, ng_mix, ng_t10), v2 seed_base 50261102 (gauss, ng_mix).
- Không đụng P4-H1, P4-H2 hay confirmatory split nào. Không có manifest nào mang bank khác D-07/D-07H.
