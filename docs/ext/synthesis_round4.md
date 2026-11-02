# Tổng hợp vòng 4: mượn kỹ thuật từ nghiên cứu khác cho `tolerant_v5_1`

**Trạng thái.** Đây là bản tổng hợp của lead vòng 4. Mọi kết quả ở đây là **exploratory, chỉ trên D-07 development** (seed_base 20261102; riêng `ngorient` v2 dùng seed_base mới 50261102 trên cùng 20 topology). Calibration, design probe và smoke chỉ dùng D-07H development. Mỗi candidate có một verifier độc lập: verifier tính lại số bằng code riêng, kiểm thứ tự ghi rule và chạy, và chạy thêm known-truth test. **Không có gì chạy trên P4-H1, P4-H2 (cả split development lẫn confirmatory) hay bank mới P4-H3.** Lead không chạy thí nghiệm nào và không sửa file nào ngoài file này.

**Yêu cầu của người dùng cho vòng này:** mở vòng thử, tìm hiểu càng nhiều nghiên cứu trước đó càng tốt, kiểm thử càng nhiều càng tốt. Sweep tìm được 58 mục kỹ thuật (khoảng 51 kỹ thuật khác nhau, vì 7 kỹ thuật xuất hiện ở hai góc). Có 8 candidate được xây và kiểm thử, tổng cộng 18 arm/phiên bản, kèm các kịch bản phụ (latent1, latent3, noise0.1, noise0.3, lag_max 1 và 4, non-Gaussian shock, panel thật).

**Quyết định tóm tắt của lead.**
1. **`tolerant_v5_1` vẫn là module of record.** Không candidate nào cải thiện interval score (IS) của nó theo rule đã ghi trước ở vùng nó đang chạy được.
2. **Chỉ một candidate đạt rule: `hubscreen` (RETAINED, exploratory).** Đây là chế độ dự phòng cho phương trình hub bị underdetermined (lag_max 2, T ≤ 30), không phải cải tiến IS. Verifier hạ mức claim: nó không trùng hệt v5_1 ở mọi chỗ v5_1 chạy được (98 run khác), và trên các run "được cứu" thì `plugin_hs_cal` có mean IS thấp hơn ở 6/6 cell T ≤ 25.
3. **Candidate hứa hẹn nhất dù không đạt rule: `ngorient` NG-A v2.** Không có harm trên cả 34 cell, cả 8 dIS primary đều âm, và khoảng cách coverage của cặp chịu ảnh hưởng của reversal thu hẹp có ý nghĩa ở 4/4 cell, nhưng chỉ dưới non-Gaussian shock tổng hợp. Verifier tìm ra một lỗi cấu tạo (luật dấu kurtosis cho cặp khác law) có thể là một phần lý do NG-A yếu. Đây là đầu vào chính cho vòng 5.
4. **`mondrian` M0 cho paper một cách mô tả bước (6)** như một conformal quantile trên calibration bank, tương đương factor hiện tại (IS lệch ≤ 0.5%). Nhưng **không được claim finite-sample guarantee ở mức pair**.
5. **Năm candidate thất bại và đều để lại bài học** (mục 3.3): `kilianbab`, `levboot`, `lfdropen`, `leadlag`, `prepivot`.
6. **Bài học quy trình quan trọng nhất:** re-tune width factor cho một method gần giống v5_1 tự nó dịch IS khoảng ±0.03–0.07, đủ để tạo "win" hay "harm" có ý nghĩa sau Holm. Từ vòng 5, mọi arm xây trên v5_1 phải thừa kế factor frozen của v5_1, hoặc báo cáo phân rã gate/factor.
7. **Vòng 5 (mục 4):** một phiên bản ghép `tolerant_v5_2` = v5_1 + `hubscreen` v2 (dự phòng, không bỏ cha cùng kỳ) + NG-A v3 (sửa luật dấu, unit test trên cặp khác law), factor thừa kế. Rule ghi trước, chạy trên seed mới của D-07 development. **Chỉ nên xin người dùng duyệt dùng P4-H2 development khi phiên bản ghép đạt rule vòng 5.** Bây giờ thì chưa nên.

---

## 0. Tình trạng 8 candidate

| Candidate | Bước của v5_1 | Weakness nhắm tới | Verdict theo rule | Verifier | Phần giữ lại |
|---|---|---|---|---|---|
| `kilianbab` (K1, KBC, K0) | (5) | bias mẫu nhỏ; factor bị chê ad hoc | K1 NOT RETAINED (0/8 win, 3/8 tệ hơn sau Holm); KBC REJECTED (tripwire, 8/8 tệ hơn); K0 NOT RETAINED | partly | Mô tả: interval của v5_1 ở T ≤ 80 lệch về phía 0 (97–100% số lần trượt) |
| `ngorient` (NG-A, NG-B; v1, v2) | (3), (4) | hướng ngẫu nhiên; reversal undercoverage; chỉ có Gaussian | REJECTED cả hai arm, cả hai phiên bản. v2 NG-A: 2/8 win (ngưỡng 3), no-harm 34/34 | partly | NG-A v2 là ứng viên cho v3; v5_1 giữ coverage 0.91–0.97 dưới non-Gaussian shock |
| `mondrian` (M0, M2) | (6) | factor bị chê ad hoc; reversal undercoverage | M2 NOT RETAINED (0/18 win); validity PASS | partly | M0 làm cách mô tả bước (6), không kèm guarantee |
| `lfdropen` | (2) | mở lag quá nhiều ở T nhỏ | NOT RETAINED (0/6 win, 5/6 tệ hơn sau Holm, no-harm 1/3) | **holds** | Mở ít hơn v5_1 theo cách này thì tệ hơn |
| `levboot` (L2, L3, W3) | (5) | small-T, hub gần underdetermined | NOT RETAINED cả ba (0/8 win; 15/24 tệ hơn sau Holm) | partly | Interval C(H) gần như bất biến với scale của residual pool |
| `leadlag` (A, D) | (3) | latent confounder bị đọc thành cạnh thiếu | NOT RETAINED cả hai; ở factor bằng nhau, gate 0/10 khác biệt | partly | Số đo co-child coverage; cảnh báo về factor re-tune |
| `prepivot` (pp, pp_orig) | (6) | factor bị chê ad hoc; panel thật không có bank | NOT RETAINED (tệ hơn 9/9 sau Holm, coverage ≥ 0.90 chỉ 1/9) | partly | Double bootstrap rút gọn undercalibrated ngay cả khi skeleton đúng |
| `hubscreen` | (1), (2) dự phòng | hub underdetermined ở lag_max 2, T < 40 | **RETAINED (exploratory)**: C1–C4 đạt | partly | Chế độ dự phòng có cờ; không tốt hơn `plugin_hs_cal` trên run được cứu |

Verifier tái lập được **mọi verdict** theo rule ghi trước. Phần bị bác chủ yếu là **diễn giải** cho paper (7/8 candidate có ít nhất một diễn giải bị bác; chỉ `lfdropen` đứng vững nguyên phần verdict, còn hai diễn giải của nó cũng bị bác).

---

## 1. Bản đồ tài liệu từ sweep

Sweep trả về 58 mục, chia theo 5 góc: bootstrap (11), orientation (12), selection (12), high-dimensional (12), robust (11). Các kỹ thuật xuất hiện hai lần được gộp vào một dòng và ghi "(2 mục)". Mọi mục được agent sweep đánh dấu `verified: true`. Cột "Ghi chú nguồn" ghi chỗ mà việc kiểm nguồn chỉ là một phần, theo chính sweep hoặc theo verifier vòng 4.

Ký hiệu cột Quyết định: **X** = được xây thành candidate; **→X** = gộp vào một candidate; **H** = hoãn sang vòng sau; **L** = loại.

### 1.1 Góc bootstrap (11 mục)

| Kỹ thuật | Nguồn chính | Plug-in vào v5_1 | QĐ | Lý do |
|---|---|---|---|---|
| Prepivoting / calibrate nominal level bằng double bootstrap | Beran 1987 Biometrika 74(3); Loh 1987 JASA 82(397); Martin 1990 JASA 85(412) | thay bước (6) bằng calibration theo từng dataset | **X** (`prepivot`) | width rule duy nhất không cần bank, dùng được cả cho panel thật |
| Fast double bootstrap; single double-bootstrap; warp-speed Monte Carlo | Davidson–MacKinnon 2007 CSDA 51(7); Chang–Hall 2015 Biometrika 102(1); Giacomini–Politis–White 2013 ET 29(3) | giảm chi phí double bootstrap; screen nhiều biến thể interval | →X (FDB làm pre-screen của `prepivot`); L (Chang–Hall, warp-speed) | Chang–Hall: lợi không chuyển sang interval. Warp-speed: IS cần interval đầy đủ mỗi dataset, chỉ dùng screen. FDB với B_i = 1 hóa ra không làm được vì root theo sd cần ít nhất 2 inner draw |
| Kilian bootstrap-after-bootstrap / Pope bias formula | Kilian 1998 REStat 80(2); Pope 1990 JTSA 11(3); Engsted–Pedersen 2014 Econometrics 2(1); Li–Plagborg-Møller–Wolf 2024 JoE 244(2) | bước (5): trừ bias của hệ số lag | **X** (`kilianbab`) | đã nằm trong danh sách "listed but not tried"; probe vòng 3 bị bỏ vì đọc bias từ draw có đổi cấu trúc, bản này sửa đúng chỗ đó |
| Split-conformal / CQR / TRUST trên calibration bank (2 mục, gộp với Lei et al.) | Romano–Patterson–Candès 2019 arXiv:1905.03222; Cabezas et al. 2024/25 arXiv:2411.19368; Lei et al. 2018 JASA 113(523) | bước (6): quantile conformal thay grid factor | **X** (`mondrian`) | chi phí bằng 0, trả lời trực tiếp chỉ trích "ad hoc" |
| Leverage-adjusted residual (HC2/HC3) trong residual bootstrap | Wu 1986 AoS 14(4); Davidson–Flachaire 2008 JoE 146(1); MacKinnon–White 1985 JoE 29(3) | `simulate_from_fit` | **X** (`levboot`) | rẻ, nhắm đúng hub ở T nhỏ. Ghi chú nguồn: candidate chỉ đọc abstract; verifier đọc full text bản working paper QED 1000 của Davidson–Flachaire |
| BCa với block-jackknife acceleration | Efron 1987 JASA 82(397); Efron–Narasimhan 2020 JCGS 29(3); Kilian 1999 REStat 81(4) | thay `percentile_interval` | →X (BC, chỉ z0, là arm KBC của `kilianbab`) | acceleration tốn thêm khoảng 10 pipeline run; z0 không ổn định khi draw có point mass |
| Bagging + infinitesimal-jackknife SE sau selection (2 mục) | Efron 2014 JASA 109(507); Wager–Hastie–Efron 2014 JMLR 15 | interval thứ hai từ draw sẵn có | L | v5_1 đã báo mean của draw. Recursive bootstrap sinh lại chuỗi, nên số lần resample residual row không phải đơn vị dữ liệu. Cần B 500–1000 |
| Skewness-adjusted bootstrap cho IRF | Grabowski–Staszewska-Bystrova–Winker 2020 AStA 104(1) | giữa refit và `cumulative(irf)` | H | trùng với phần re-centering của Kilian và thêm một tầng |
| Residual MBB / recursive-design wild bootstrap | Brüggemann–Jentsch–Trenkler 2016 JoE 191(1); Gonçalves–Kilian 2004 JoE 123(1); Bruns–Lütkepohl 2023 Comp. Econ. 62(4) | `simulate_from_fit`, bật bằng diagnostic | L (wild Rademacher có mặt như arm W3 của `levboot`) | chỉ sửa variance; vấn đề của noise là attenuation bias; chưa có kịch bản heteroskedastic |
| Lag-augmented VAR bootstrap (uniform validity) | Inoue–Kilian 2020 JoE 215(2); Hansen 1999 REStat 81(4) | thêm lag p+1 cho khối cha | L | generator chặn rho_max 0.9; lag thêm làm hub càng underdetermined |
| Bayesian bootstrap (Dirichlet weights) | Rubin 1981 AoS 9(1) | thay resample nguyên row ở T < 40 | L | draw hỏng đến từ số term, không phải rank deficiency, nên lập luận survivor bias không áp dụng |

### 1.2 Góc orientation (12 mục)

| Kỹ thuật | Nguồn chính | Plug-in vào v5_1 | QĐ | Lý do |
|---|---|---|---|---|
| Pairwise likelihood ratio (tanh/skew) | Hyvärinen–Smith 2013 JMLR 14 | thay đồng xu 0.5 ở bước (3), (4) | **X** (`ngorient`) | O(T), không cần ICA lặp, quy về đúng v5_1 khi Gaussian. Verifier đã đọc PDF JMLR và đối chiếu công thức |
| Weak-identification pre-test gate | Montiel Olea–Plagborg-Møller–Qian 2022 AEA P&P 112 | gate Jarque–Bera trước orientation | →X (gate của `ngorient`) | giữ module không đổi khi không có bằng chứng non-Gaussian. Ghi chú nguồn: verifier không đọc bài này; theo verifier, bài chủ yếu khuyên dùng inference robust với weak identification hơn là một pretest, nên cụm "test trước khi identify" là diễn giải của nhóm |
| Equal-variance identifiability; varsortability audit | Peters–Bühlmann 2014 Biometrika 101(1); Reisach–Seiler–Weichwald 2021 NeurIPS | (a) luật orientation; (b) audit bank | →X (audit trong `ngorient`); L (luật orientation) | noise_var ~ U(0.5, 1.5) vi phạm giả định equal variance; audit thì rẻ và bắt buộc |
| Independence-refined orientation set (+ sign/narrative) | Drautzburg–Wright 2023 JoE 235(2); Antolín-Díaz–Rubio-Ramírez 2018 AER 108(10) | bước (4): giữ các orientation không bị bác | H | tốn công vừa, trùng `ngorient`; xét lại nếu gate của `ngorient` có thông tin |
| dCov / HSIC, TiMINo | Matteson–Tsay 2017 JASA 112(518); Peters–Janzing–Schölkopf 2013 NeurIPS | thống kê độc lập cho bước (3) | H | O(T²) mỗi draw, power thấp ở T ≤ 80; có thể là arm robustness sau này |
| SVAR-GMM / non-Gaussian ML cho khối 2×2 | Lanne–Meitz–Saikkonen 2017 JoE 196(2); Keweloh 2021 JBES 39(3); Keweloh–Wang arXiv:2310.08173 | bước (3): ước lượng góc quay cục bộ | L | weak identification ở T ≤ 150; LR theo cặp rẻ hơn. Ghi chú nguồn: arXiv v2 (10/2026) đổi tên bài |
| Identification through heteroskedasticity | Rigobon 2003 REStat 85(4); Lanne–Lütkepohl 2008 JMCB 40(6); Lewis 2021 REStud 88(6) | bước (3)/(4) cho bank GARCH | L | chưa có generator heteroskedastic; 19 quý quá ngắn để tách regime |
| DirectLiNGAM / VARLiNGAM với prior từ skeleton | Hyvärinen et al. 2010 JMLR 11; Shimizu et al. 2011 JMLR 12 | bước (4) toàn cục | H | LR theo cặp + check acyclic đã phủ; có thể làm baseline sau |
| Meek rules + residual PC (Swanson–Granger; Demiralp–Hoover) | Meek 1995 UAI; Swanson–Granger 1997 JASA 92(437); Demiralp–Hoover 2003 OBES 65(s1) | orientation dưới Gaussian | L | thông tin v-structure đã nằm trong dl_e Gaussian của revlag3 (`tolerant_v4R`, 0/4); dl_e được dùng lại trong arm NG-B |
| Multiscale bootstrap AU p-value | Komatsu–Shimizu–Shimodaira 2010 ICANN, arXiv:0909.2904 | calibrate xác suất hướng | L | nhân runtime; tác động bậc hai |
| RCD / mixed-LiNGAM (confounder vs cạnh) | Maeda–Shimizu 2020 AISTATS; Shimizu–Bollen 2014 JMLR 15 | test 3 chiều i→j, j→i, i↔j | H | cần generator non-Gaussian có confounder; làm sau `ngorient` |
| CD-NOD (thay đổi theo domain) | Huang et al. 2020 JMLR 21(89) | dummy domain trong CI test | L | dữ liệu một regime |

### 1.3 Góc selection (12 mục)

| Kỹ thuật | Nguồn chính | Plug-in vào v5_1 | QĐ | Lý do |
|---|---|---|---|---|
| Two-groups local fdr, pi0 cố định theo damage khai báo | Efron–Tibshirani–Storey–Tusher 2001 JASA 96(456); Scott–Berger 2010 AoS 38(5) | bước (2): mở lag theo xác suất | **X** (`lfdropen`) | dùng trực tiếp damage count, khác Storey pi0 đã thử. Ghi chú nguồn: candidate chỉ đọc abstract Efron 2001; verifier đọc full text Scott–Berger trên arXiv:1011.2333 |
| Conditional SIS cho hub | Barut–Fan–Verhasselt 2016 JASA 111(515); Fan–Lv 2008 JRSS-B 70(5) | bước (1)–(2) khi phương trình underdetermined | **X** (`hubscreen`) | sửa đúng chỗ v5_1 trả `_failed('underdetermined')`. Verifier đọc arXiv:1206.1024 tr. 1–10 |
| FIC / focused model averaging (2 mục) | Claeskens–Hjort 2003 JASA 98(464); Hjort–Claeskens 2003 JASA 98(464); Lohmeyer–Palm–Reuvers–Urbain 2019 Econ. Rev. 38(7) | bước (2) theo từng pair | H | cần Jacobian; selection không consistent dưới local misspecification. Ghi chú nguồn: Lohmeyer et al. chỉ đọc abstract |
| Bias-aware honest CI; Bonferroni size correction (2 mục) | Armstrong–Kolesár 2020 QE 11(1), 2021 QE 12(1), 2018 Econometrica 86(2); McCloskey 2017 JoE 200(1) | bước (6): critical value theo pair với bias bound | H | cần chọn bound M và Jacobian; `mondrian` rẻ hơn nên làm trước. Sau khi `mondrian` và `prepivot` thất bại, đây là ứng viên chính cho chỉ trích "ad hoc" |
| Robust EBCI (2 mục) | Armstrong–Kolesár–Plagborg-Møller 2022 Econometrica 90(6) | shrink 196 pair về plugin | L | metric chỉ chấm pair non-null; shrink về 0 hay về plugin làm lệch đúng tập được chấm, nên average-coverage guarantee không khớp metric |
| Bayesian graphical SVAR / SSVS | George–Sun–Ni 2008 JoE 142(1); Ahelegbey–Billio–Casarin 2016 JAE 31(2); Scott–Berger 2010; van der Pas–Szabó–van der Vaart 2017 BA 12(4) | bước (2)–(4) cùng lúc | L | MCMC cho mỗi dataset, quá tốn cho grid |
| Score-weighted orientation trong search space giới hạn | Kuipers–Suter–Moffa 2022 JCGS 31(3) | thay đồng xu bằng trọng số BIC | L | đã thử về thực chất ở revlag3 (`tolerant_v4R`, `_mix`) |
| CPSS stability selection | Shah–Samworth 2013 JRSS-B 75(1); Meinshausen–Bühlmann 2010 | bước (2) với cận false openings | L | khoảng 50× runtime nếu lồng trong draw; nửa mẫu T/2 quá yếu ở T = 40 |
| Derandomized group knockoffs (time series) | Dai–Barber 2016 ICML; Ren–Wei–Candès 2023 JASA 118(542); Chi–Fan–Ing–Lv 2025 JASA 120(551) | bước (2) với PFER | L | power quá thấp ở T = 40 |
| PoSI / inference on winners | Berk et al. 2013 AoS 41(2); Bachoc–Leeb–Pötscher 2019 AoS 47(3); Andrews–Kitagawa–McCloskey 2024 QJE 139(1) | bước (6): critical value đồng thời | L | conservative, khoảng 10× runtime |
| SIN / GGM FDR cho repair cùng kỳ | Drton–Perlman 2004 Biometrika 91(3); Liu 2013 AoS 41(6) | bước (3): partial thay marginal correlation | L | không tách được latent clique; leak từ một cạnh thiếu có giới hạn ở đây |

Mục thứ 12 của góc selection (Efron 2014 bagging + IJ) đã gộp vào dòng tương ứng ở 1.1.

### 1.4 Góc high-dimensional (12 mục)

| Kỹ thuật | Nguồn chính | Plug-in vào v5_1 | QĐ | Lý do |
|---|---|---|---|---|
| Robust EBCI | AKP 2022 (trùng 1.3) | bước (6) | L | như trên |
| Bias-aware CI dưới ràng buộc xấp xỉ đúng, bound theo damage | Armstrong–Kolesár 2021 QE 12(1), 2018 Econometrica 86(2) (trùng 1.3) | bước (6) | H | như trên |
| Bias-aware ridge cho phương trình hub | Armstrong–Kolesár–Kwon arXiv:2012.14823 | bước (1) ở hub | L | tốn công vừa–cao; `hubscreen` rẻ hơn cho cùng lỗi |
| Post-double-selection / DML cho evidence test | Belloni–Chernozhukov–Hansen 2014 REStud 81(2); Chernozhukov et al. 2018 EJ 21(1) | bước (1) | L | lasso trong 199 draw; `hubscreen` rẻ hơn. Ghi chú nguồn: chi tiết tạp chí của BCH 2014 lấy từ trích dẫn đã biết |
| Desparsified lasso VAR/LP | Adamek–Smeekes–Wilms 2024 EJ 27(3); Krampe–Paparoditis–Trenkler 2023 JoE 234(1); Krampe–Kreiss–Paparoditis 2021 Bernoulli 27(3) | thay OLS ở phương trình hub | L | đã trong danh sách "listed but not tried"; nodewise lasso trong 199 draw; `hubscreen` rẻ hơn |
| Stein shrinkage giữa fit skeleton và fit mở toàn bộ | Hansen 2016 JoE 190(1); Li–Plagborg-Møller–Wolf 2024 | bước (2) + nhánh TAU | H | hợp lý nhưng giữ mỗi vòng một thay đổi ở bước (2). Sau `lfdropen` (mở ít hơn thì tệ hơn), đây là hướng mở mềm đáng thử |
| Jackknife model averaging | Hansen–Racine 2012 JoE 167(1); Zhang–Wan–Zou 2013 JoE 174(2) | bước (2) | H | như Stein |
| FIC theo từng pair | Hjort–Claeskens 2003; Lohmeyer et al. 2019 (trùng 1.3) | bước (2) | H | như trên |
| Spectral deconfounding (trim) / doubly debiased lasso (2 mục, gộp với 1.5) | Ćevid–Bühlmann–Meinshausen 2020 JMLR 21(232); Guo–Ćevid–Bühlmann arXiv:2004.03758 | bước (1), (3) | L | latent 3 con trong n = 14 không phải dense confounding. Ghi chú nguồn: việc đăng AoS của Guo et al. lấy từ trích dẫn đã biết |
| FAVAR factor augmentation | Bernanke–Boivin–Eliasz 2005 QJE 120(1) | thêm PC của residual | L | tốn bậc tự do ở T = 40, có thể nuốt hub thật; ưu tiên `leadlag` trước |
| Split-conformal (Lei et al.) với cell Mondrian | Lei et al. 2018 JASA 113(523); Chernozhukov–Wüthrich–Zhu 2018 COLT | bước (6) | →X (`mondrian`) | như 1.1. Ghi chú nguồn: chi tiết tạp chí của Lei et al. lấy từ trích dẫn đã biết |
| Iterated double bootstrap, single inner draw | Chang–Hall 2015 (trùng 1.1) | bias của tâm | L | như 1.1 |

### 1.5 Góc robust: confounder và measurement noise (11 mục)

| Kỹ thuật | Nguồn chính | Plug-in vào v5_1 | QĐ | Lý do |
|---|---|---|---|---|
| Lead-lag residual cross-correlation (Haugh/Hong), negative-control logic | Haugh 1976 JASA 71; Hong 1996 Biometrika 83(3); Lipsitch–Tchetgen Tchetgen–Cohen 2010 Epidemiology 21(3) | gate trước repair ở bước (3) | **X** (`leadlag`) | rẻ, nhắm đúng latent persistent. Ghi chú nguồn: candidate tóm tắt Haugh/Hong theo nội dung đã biết, không đọc; kernel của Hong không được dùng |
| Sparse + low-rank precision (latent GGM, LRpS) | Chandrasekaran–Parrilo–Willsky 2012 AoS 40(4); Frot–Nandy–Maathuis 2019 JRSS-B 81(3); Jalali–Sanghavi 2012 ICML; Zorzi–Sepulchre arXiv:1405.0027 | bước (3) | H | hợp với confounder ≥ 3 node; cần chọn rank/penalty trước. Ứng viên tiếp theo cho weakness confounder, sau khi `leadlag` không có tác dụng |
| Rank / vanishing tetrad | Silva et al. 2006 JMLR 7; Huang et al. 2022 NeurIPS | gom các repair thành một latent | L | power thấp ở T = 40 |
| Forni–Gambetti sufficient information | Forni–Gambetti 2014 JME 66 | diagnostic + factor | L | ưu tiên `leadlag` trước |
| Spectral deconfounding | (trùng 1.4) | | L | |
| Lag-collider orientation (SVAR-FCI, LPCMCI) | Malinsky–Spirtes 2018 PMLR 92; Gerhardus–Runge 2020 NeurIPS | hướng + nhãn ↔ | L | thông tin thứ tự thời gian đã nằm trong dl_e của revlag3 |
| State-space VAR + EM-Kalman | Nalatore–Ding–Rangarajan 2007 PRE 75; Shumway–Stoffer 1982 JTSA 3(4); Komunjer–Ng 2014 ET 30(1); Newbold 1978 IER 19(3) | thay OLS dưới noise | H | vài phút mỗi dataset với 199 draw. Ghi chú nguồn: Newbold chỉ có record RePEc |
| Modified Yule–Walker / Frisch scheme / Blom bound | Staudenmayer–Buonaccorsi 2005 JASA 100; Söderström 2007 Automatica 43(6); Blom et al. 2018 UAI | ước lượng variance của noise | H | identification của noise variance trùng một phần với eiv/eiv2 đã thử. Ghi chú nguồn: phần Frisch scheme của Söderström chỉ xác nhận qua slide của tác giả |
| SIMEX trên C(H) | Cook–Stefanski 1994 JASA 89(428); Stefanski–Cook 1995 | bias-shift percentile | H | cần variance của noise từ dòng trên. Ghi chú nguồn: Stefanski–Cook 1995 chỉ thấy qua listing thứ cấp |
| OVB sensitivity bound (partial R²) | Cinelli–Hazlett 2020 JRSS-B 82(1); Chernozhukov et al. arXiv:2112.13398 | bước (6) với k cố định | L | chọn k = 1 là tùy ý và conservative |
| Proximal 2SLS với lead/lag proxy | Miao–Geng–Tchetgen Tchetgen 2018 Biometrika 105(4); Tchetgen Tchetgen et al. arXiv:2009.10982 | bước (3)–(4) | L | proxy yếu và khó hợp lệ trong VAR. Ghi chú nguồn: dạng 2SLS tuyến tính lấy từ trí nhớ, chưa xác nhận |

### 1.6 Nguồn mới do verifier đưa ra trong vòng 4 (chưa mở trong vòng này, trích từ trí nhớ)

- Dunn, Wasserman, Ramdas, "Distribution-free prediction sets for two-layer hierarchical models", JASA 2023, arXiv:1809.07441. Liên quan trực tiếp đến `mondrian`: dữ liệu của bài toán là hai tầng (pair trong dataset trong topology), và bài này cho conformal hợp lệ cho một đơn vị mới trong một group mới.
- Hosking 1980 và Li–McLeod 1981: hiệu chỉnh bậc tự do cho portmanteau test trên residual đã fit của mô hình đa biến. Liên quan đến lỗi null của `leadlag` A.

### 1.7 Vì sao chọn 8 candidate này

Tiêu chí của lead lúc chọn: (a) mỗi candidate nhắm một weakness đã biết của v5_1; (b) chi phí runtime không quá khoảng 5× v5_1; (c) có điểm cắm rõ vào đúng một hoặc hai bước, để so sánh ghép cặp với v5_1 bằng common random numbers; (d) không trùng thứ đã thử. Hai kỹ thuật trong danh sách "listed but not tried" được làm (Kilian 1998; non-Gaussian orientation). Các kỹ thuật còn lại trong danh sách đó vẫn chưa làm: stability selection (loại vì runtime), desparsified lasso (loại vì `hubscreen` rẻ hơn), Herbst–Johannsen LP bias correction và Hochsprung–Runge–Gerhardus 2025 (sweep không đưa vào pool), robust Bayes over identification schemes (sweep không đưa vào pool).

---

## 2. Từng candidate: đã xây gì, rule, verdict, phần đứng vững, fidelity

Quy ước chung cho mọi candidate: so sánh ghép cặp với `tolerant_v5_1` dùng factor frozen (`experiments/ext/v51/frozen_v4_v51.json`); dIS = IS(arm) − IS(v5_1) trên pair non-null; CI từ topology-cluster bootstrap (20 cluster, B = 20000, seed 20261104); Holm ở 0.05. Mọi candidate đều xác nhận được row v5_1 của driver trùng với run đã lưu (ví dụ `results/ext_v51_eval` 1260/1260).

### 2.1 `kilianbab`: Kilian bootstrap-after-bootstrap, kèm arm BC

**Đã xây.** `src/paper4/ext_r4kilianbab.py`. Stage 1: 99 refit với cấu trúc **cố định** (không re-select, không repair, không flip) để ước lượng bias của hệ số lag; B0 không bao giờ được sửa; số 0 do selection không bị đụng; shrink tuyến tính khi companion radius ≥ 1. Stage 2: bootstrap từ fit đã sửa, mỗi draw chạy lại (1)–(4) như v5_1 rồi trừ bias. Ba arm: K1 (BaB + factor re-tune trên D-07H), KBC (đầu mút BC), K0 (không factor). Khi ép bias = 0, K1 trùng v5_1 từng bit (14/14 cell; verifier thêm 28/28 case mới).

**Rule** (ghi 12:15Z, hash khớp sau run). 8 cell primary T{40, 80} × {missing, reversed} × {0.2, 0.5}. RETAINED nếu ≥ 3/8 win, coverage ≥ 0.90 ở cả 8, không cell primary nào tệ hơn sau Holm, no-harm ở 13 cell còn lại. Tripwire: T80 reversed-0.5 tệ hơn sau Holm thì REJECTED. K0 "factor-free" cần coverage ≥ 0.90 ở cả 21 cell và non-inferior ≥ 6/8.

**Verdict.** K1 NOT RETAINED (0/8 win; 3/8 tệ hơn sau Holm; no-harm thất bại). KBC REJECTED (tripwire, p = 0.0001; 8/8 tệ hơn). K0 NOT RETAINED (coverage < 0.90 ở 4/21; non-inferior 0/8). Family overlay 0/16.

**Phần đứng vững sau verifier.**
- Mọi số và mọi đếm Holm tái lập; tập cell tệ hơn không đổi khi đổi seed bootstrap.
- dIS của K1 ở primary đều dương: T40 missing-0.2 +0.20 [+0.05, +0.35], T40 reversed-0.5 +0.36 [+0.26, +0.46], T80 reversed-0.5 +0.02 [−0.08, +0.11].
- Interval của v5_1 ở T ≤ 80 lệch về phía 0: 98.6–100% số lần trượt ở primary nằm ở phía 0 (oracle: 89–95%). BaB giảm offset của midpoint khoảng một nửa (ví dụ −0.36 → −0.17 ở T40 missing-0.2).
- Nhưng BaB đẩy companion radius của data fit từ 0.879 lên 0.933 ở T40, và shrink chạy ở 31–50% draw T40.
- Known-truth trong bối cảnh gốc của Kilian (VAR(1) hai biến, T = 40, cấu trúc cố định): coverage C(H) 0.728 → 0.915, IS 7.91 → 4.05. Lõi BaB được cài đúng; nó chỉ không giúp khi chồng lên selection/repair/reversal của v5_1.
- Kịch bản phụ: K1 gây hại dưới latent1 (+0.23 đến +0.55 ở 6/6 cell), trung tính hoặc tốt hơn chút dưới noise0.1 (−0.14 đến +0.06).

**Phần bị verifier bác.**
- Câu đề xuất cho paper "0.05–0.20 của width factor của v5_1 là bias mẫu nhỏ" **không đứng vững**. Factor của K1 giảm chủ yếu vì draw của BaB rộng hơn trước khi nhân factor (raw width 1.18–1.28× ở T40, 1.16–1.19× ở T80, 1.08–1.12× ở T150). Tổng width so với v5_1 ≥ 1.0 ở 18/21 cell. Re-centering gần như không bớt được width cần thiết.
- Rule đã hash nhưng `analyze.py` không nằm trong hash và được sửa 83 s sau khi run bắt đầu (trước khi có output). Verifier tính lại độc lập và ra cùng verdict.
- KBC tính z0 so với tâm của thế giới bootstrap đã sửa bias, nên z0 ≈ 0 theo cấu tạo (|mean z0| ≤ 0.014). Việc KBC bị bác **không** phải là bằng chứng chống lại BC áp lên chính draw của v5_1.

**Fidelity với nguồn.** Trung thành với Kilian 1998 ở các điểm chính (bias từ stage 1, không sửa khi data fit non-stationary, shrink tới khi stationary, percentile của draw đã sửa). Lệch: sửa hệ số lag cấu trúc theo từng phương trình với B0 cố định thay vì hệ số reduced-form (không được nêu là adaptation); shrink tuyến tính thay vì đệ quy (lệch tới khoảng 0.05 ở d ≈ 0.4; không đổi verdict); bias ước lượng dưới cấu trúc chưa flip được áp cho draw đã flip (đã nêu).

**Câu dùng được cho paper.** "Ở T ≤ 80, interval của v5_1 trượt gần như luôn ở phía 0 (97–100% số lần trượt, so với 89–95% của oracle). Kilian re-centering giảm nửa độ lệch đó nhưng làm draw rộng hơn phần nó tiết kiệm, nên width cần thiết không giảm." Không dùng câu "x% của factor là bias".

### 2.2 `ngorient`: gated non-Gaussian pairwise LR orientation

**Đã xây.** `src/paper4/ext_r4ngorient.py`. LR theo cặp của Hyvärinen–Smith 2013 (dạng tanh hoặc skew), gate Jarque–Bera, se bằng block jackknife, p cắt về [0.05, 0.95]. Thay đồng xu ở bước (3) và hoán vị đều ở bước (4) (Plackett–Luce, key Efraimidis–Spirakis). Evidence tính lại trong mỗi draw. NG-A: chỉ evidence non-Gaussian; NG-B: cộng dl_e Gaussian của revlag3 trên thang log-odds. Common random numbers với v5_1: arm trùng v5_1 từng bit khi mọi gate đóng. Generator mới trong driver (`experiments/ext/r4ngorient/laws.py`): `ng_mix` (Laplace, t5, exponential lệch, uniform theo node), `ng_t10`.

**Rule** (ghi 12:19Z, trước run D-07). Unit test phải đạt trước mọi bank run. 8 cell primary: ng_mix × T{80, 150} × {missing, reversed} × {0.2, 0.5}. RETAINED nếu ≥ 3/8 win, coverage ≥ 0.90 ở cả 8, no-harm (a) trên 21 cell Gaussian (IS ratio ≤ 1.03, không tệ hơn sau Holm 21), (b) trên 13 cell ng_mix còn lại (ratio ≤ 1.05). v2 (ghi trước run v2, sau khi đã thấy v1 và post hoc của v1): cùng rule, chỉ đổi là arm thừa kế factor frozen của v5_1, dữ liệu mới (seed_base 50261102).

**Verdict.** REJECTED cả hai arm, cả hai phiên bản.
- v1 (factor re-tune trên D-07H Gaussian): NG-A 0/8 win, no-harm (a) thất bại ở Gaussian T150; NG-B 1/8.
- v2 (factor thừa kế, dữ liệu mới): NG-A **2/8 win** (T80 missing-0.5 −0.084 [−0.165, −0.019]; T150 rev-0.2 −0.078 [−0.126, −0.032]), cả 8 dIS âm, IS ratio 0.958–0.995, coverage 0.934–0.971, **no-harm đạt 34/34**. NG-B 3/8 win nhưng no-harm (a) thất bại ở Gaussian T150 reversed-0.5 (ratio 1.032 > 1.03). NG-B thắng NG-A ở 0/8.

**Phần đứng vững sau verifier.**
- Verdict tái lập với 3 seed bootstrap; đếm WIN ổn định.
- Unit test: hướng đúng 0.946 (Laplace) và 0.910 (skewexp) ở m 148, b 0.6; gate-open dưới Gaussian 0.056–0.078; bất biến scale.
- Dấu của R khớp log-likelihood ratio chính xác của Laplace ở 98.3% trường hợp gate mở. Công thức đúng với HS 2013 (eq. 5, mục 2.6, eq. 13).
- Secondary v2: coverage cặp chịu ảnh hưởng tăng +0.021 / +0.034 / +0.018 / +0.013 ở 4 cell reversed ng_mix, Holm(4) p 0.042 / 0.023 / 0.009 / 0.029, mà width trung bình của các cặp đó gần như không đổi (0.996–1.009). Trên dữ liệu Gaussian cùng cell: −0.021 đến +0.002.
- AUROC cho cạnh pool bị đảo thật (ng_mix, T 40/80/150): NG-A 0.55–0.58 / 0.67–0.72 / 0.78; NG-B 0.61–0.66 / 0.82–0.85 / 0.88–0.91; dl Gaussian một mình 0.58–0.63 / 0.78–0.81 / 0.84–0.85.
- Phát hiện phụ: v5_1 với factor Gaussian giữ coverage 0.912–0.970 dưới ng_mix và 0.952–0.969 dưới t10.
- Varsortability của các bank 0.88–0.94; R²-sortability 0.53–0.59.
- Panel thật (m = 17): không node thật nào bác normality sau Holm (Holm p nhỏ nhất 0.395); power của JB ở m 17 rất thấp (Laplace 0.28, t5 0.20, skewexp 0.56, uniform 0.004); gate mở ở 4/21 cạnh khai báo.
- Runtime: NG-A +45%, NG-B +86% so với v5_1.

**Phần bị verifier bác.**
- **Lỗi cấu tạo không được nêu:** unit test lấy cause và noise từ **cùng một law**, nhưng trong ng_mix khoảng 3/4 cặp là khác law. Trên cặp khác law, luật dấu kurtosis (dấu của **trung bình** excess kurtosis của cặp) làm evidence không consistent: tỉ lệ sai hướng trung bình theo hỗn hợp law của ng_mix là 0.132 / 0.162 / 0.148 ở m 78 / 148 / 400, **không giảm theo m**; cặp có uniform gần như tung đồng xu (t5→uniform sai 52% ở m 400). HS 2013 mục 2.6 dùng dấu kurtosis của một biến và lưu ý thường hai dấu giống nhau; uniform (exkurt −1.2) trộn với law super-Gaussian phá giả định đó. Vì vậy một phần lý do NG-A yếu là lỗi cấu tạo, **không phải giới hạn của non-Gaussian identification**.
- "No-harm thất bại ở v1 là do noise của factor re-tune" chỉ là một attribution: trên calibration bank ng_mix, factor của NG-A ≥ factor của v5_1 ở 12/12 key, gợi ý có hướng hệ thống.
- "Method đầu tiên trong project thu hẹp có ý nghĩa khoảng cách coverage của cặp reversal" phải kèm điều kiện "không nới interval, chỉ dưới non-Gaussian shock tổng hợp": M2 của `mondrian` cũng có 2/6 cell có ý nghĩa ở T150 (nhưng nới theo lớp). Hiệu ứng nhỏ (đóng 14–38% khoảng cách), là endpoint phụ của một phiên bản thiết kế sau post hoc v1. Với t-test mức topology, NG-A v2 chỉ còn 1/8 win.
- Gate-open Gaussian ở T150 là 0.17–0.18, cao hơn mức danh nghĩa 0.10 (đã nêu).

**Fidelity với nguồn.** Công thức đo theo đúng HS 2013. Lệch do nhóm tự đặt: bộ chọn dạng S ≥ K; dấu kurtosis lấy từ trung bình của cặp (sai khi hai dấu ngược nhau, đúng chỗ HS gọi là "complication"); gate JB và p từ block jackknife không có trong HS.

### 2.3 `mondrian`: split-conformal (Mondrian) cho bước (6)

**Đã xây.** `src/paper4/ext_r4mondrian.py`. Chỉ đổi bước (6); bước (1)–(5) gọi đúng `ext_v51.tolerant_v5_1` trên cùng RNG stream; cấu trúc từng draw được ghi bằng cách bọc `bootstrap_C`. Score s = |C_true − mid| / h trên pair non-null của calibration bank, quantile ⌈(N+1)·0.95⌉. M0: không chia lớp; M2: hai lớp R (structure-sensitive) và S, định nghĩa bằng arrival time chặn ở H + 1 (thay reachability, vì reachability tính cả lag chỉ còn là "cùng thành phần liên thông").

**Rule** (hash 12:21Z, trước run D-07). Validity V1–V4 (M0 phải trùng v5_1 trong |IS ratio − 1| ≤ 0.02, |Δcov| ≤ 0.02). WIN cần Holm 18 bác cả M2 − v5_1 lẫn M2 − M0 (loại win chỉ do làm tròn grid). RETAINED nếu ≥ 4/18 win, coverage ≥ 0.90 ở mọi cell, không tệ hơn sau Holm 21, IS ratio ≤ 1.05.

**Verdict.** M2 NOT RETAINED (WIN 0/18); validity PASS.

**Phần đứng vững sau verifier.**
- V1 1260/1260 và 720/720; V2 tái lập 12/12 factor frozen; q_table tái lập chính xác bằng code độc lập; mọi số trong ruling tái lập tới 3 chữ số.
- M0 tương đương v5_1: max |IS ratio − 1| = 0.0047, max |Δcov| = 0.007. Mô tả bước (6) như một conformal quantile thực nghiệm trên calibration bank là có cơ sở.
- M2: không cell nào M2 tốt hơn M0 sau Holm; chia lớp chủ yếu dịch coverage từ S sang R; thứ tự lớp ước lượng trên D-07H không chuyển sang D-07 ở T40 reversed (lớp R 0.895 → 0.836).
- Secondary: coverage cặp chịu ảnh hưởng tăng ở 2/6 cell (T150 rev-0.2 +0.030, rev-0.5 +0.014); khoảng cách tới oracle_cal còn −0.065 đến −0.138.
- Factor T40 tune trên 1 replicate D-07H không ổn định (q T40 none 1.30 → 1.64 với 3 replicate).
- noise0.1 T80 missing-0.2: M2 xấu đi +0.118 [+0.034, +0.202], coverage 0.883.

**Phần bị verifier bác.**
- Kết luận "finite-sample guarantee ở mức pair không đứng vững, vì coverage của M0 loại 0.95 ở 11/21 cell" là **non-sequitur**. Split-conformal guarantee là marginal, lấy trung bình qua việc rút calibration set; một calibration bank cố định chỉ cho training-conditional coverage. Resample topology của D-07H cho dải coverage T40 [0.891, 0.967] (none), chứa 0.95. Calibrate trên D-07H rep 0 rồi test trên D-07H rep 1–2 đã cho 0.889–0.926 ở T40: rep 0 "dễ" bất thường. Toy 20 cluster × 60 pair phụ thuộc: marginal 0.946, nhưng sd của coverage có điều kiện là 0.086. Câu đúng: pair không exchangeable nên cận 1/(N+1) với N ≈ 1170 không áp dụng; với khoảng 20 cluster, factor của một bank có thể lệch 0.03–0.05.
- No-harm "đạt" phụ thuộc seed: T40 reversed-0.5 p 0.0025 so với ngưỡng 0.00238; với 1 trong 10 seed khác, Holm 21 bác.
- Câu "doc giữ nguyên sha256" sai về chữ: chỉ prefix mục 1–4 giữ hash.

**Fidelity với nguồn.** Không phải split conformal sách giáo khoa (Lei et al.: fit trên một split, score trên split iid khác). Đây là simulation-based calibration (gần TRUST, hoặc prepivoting kiểu Beran) với locally weighted score. Quantile ⌈(N+1)(1−α)⌉ và quantile Mondrian theo lớp được cài đúng. Không thừa nhận cấu trúc hai tầng của dữ liệu; tài liệu đúng là Dunn–Wasserman–Ramdas 2023.

**Câu dùng được cho paper.** "Width factor là conformal quantile ⌈(N+1)·0.95⌉ của |C_true − mid|/h trên calibration bank (D-07H). Đơn vị exchangeable là topology, nên chúng tôi không claim guarantee hữu hạn mẫu ở mức pair; factor ở T40 nhạy với mẫu calibration."

### 2.4 `lfdropen`: mở lag theo two-groups local fdr, pi0 cố định theo damage

**Đã xây.** `src/paper4/ext_r4lfdropen.py`. Chỉ đổi bước (2) của nhánh targeted. z = Φ⁻¹(1 − p) từ Sidak p; pi0 = 1 − k/m cố định; f1 normal fit bằng EM; luôn mở top k (thay 3k), các cặp khác mở khi P ≥ 0.5 trên data, hoặc Bernoulli(P) trong mỗi draw. Common random numbers với v5_1 trừ phần Bernoulli.

**Rule** (hash 12:18Z). V1: trùng v5_1 ở 15 cell không khai báo thiếu cạnh. 6 cell primary missing × T{40, 80, 150}. RETAINED nếu ≥ 2/6 win, coverage ≥ 0.90, no-harm ở 3 cell latent1 × missing-0.2.

**Verdict.** NOT RETAINED: WIN 0/6, LOSS 5/6 sau Holm (T40 m0.2 +0.623 [+0.279, +0.946]; T80 m0.5 +0.447; chỉ T150 m0.2 hòa), no-harm 1/3 (T40 +0.662, T80 +0.156 tệ hơn sau Holm).

**Phần đứng vững sau verifier (overall: holds).**
- Mọi số quyết định verdict tái lập bằng code độc lập; replay end-to-end hai unit D-07 khớp bit; monkeypatch bước (2) về luật v5_1 thì candidate trùng v5_1. Chỉ bước (2) khác.
- Sửa analyzer sau preview (V1 bỏ thêm key `info_lfdr_crn` như rule text đã ghi) chỉ có thể đẩy verdict từ INVALID sang NOT RETAINED, không về phía RETAINED.
- Cơ chế: trước calibration interval hẹp hơn 6–25%; nhưng số khối mở giảm 64–66% ở T40, recall cạnh thiếu thật giảm 0.642 → 0.421 (T40 m0.2), 80–83% run T40 chỉ mở đúng sàn k. Factor tune lại trên D-07H tăng 2.3 → 3.6 ở T40, nên interval sau calibration rộng hơn 17–29%.
- Kịch bản phụ: tệ hơn sau Holm 13/17, tốt hơn 0/17.
- EM với pi0 cố định đạt MLE số; theoretical null phù hợp (tỉ lệ p < 0.10 ở cặp sạch 0.09–0.11).

**Phần bị verifier bác.**
- Cơ chế "indirect evidence chiếm chỗ" sai ở T40: nguyên nhân chính là **power thấp** (p median của cạnh thiếu thật 0.12 và 0.054, hạng khoảng 12/80). Một screen tổng hợp có tín hiệu yếu và không có tín hiệu gián tiếp tái tạo đúng mẫu hình (90% run ở sàn).
- "Dữ liệu ủng hộ giữ K = max(3k, #p<0.10)" và "mở thêm thì rẻ" không được chứng minh: thí nghiệm chỉ thử mở **ít hơn**. Kết quả vòng 1 nói ngược lại ở T40 (mở mọi lag tốn 30–35% IS so với targeted; `docs/ext/narrow.md`).

**Fidelity với nguồn.** Định nghĩa lfdr đúng, nhưng f1 là normal tham số với pi0 cố định, trong khi Efron ước lượng f phi tham số và bound pi0 từ dữ liệu: đây là biến thể tham số. Scott–Berger mục 3 cho phép p chủ quan phản ánh tỉ lệ tin là có, nên pi0 = 1 − k/m hợp lệ cho k cạnh thiếu thật; nhưng lớp "non-null" của screen ở T lớn còn gồm tín hiệu gián tiếp, nên con số này đánh giá thấp khối non-null.

### 2.5 `levboot`: residual hiệu chỉnh leverage trong residual bootstrap

**Đã xây.** `src/paper4/ext_r4levboot.py`. L2 (r/√(1−h)), L3 (r/(1−h)) resample nguyên row như v5_1; W3 wild bootstrap recursive-design với Rademacher và residual HC3. `estimator.simulate_from_fit` chỉ thay tạm trong lúc gọi. Arm U (pool đều qua code của module) trùng v5_1 với max diff 0.

**Rule** (hash 12:28Z). 8 cell primary (6 cell hỏng ở T40 + missing T80), Holm gộp 24 test. RETAINED nếu ≥ 2/8 win, coverage ≥ 0.90, no-harm ở 13 cell còn lại. Claim phụ "leverage giải thích một phần factor" chỉ khi raw coverage tăng ≥ 0.02 ở ≥ 4/6 cell T40.

**Verdict.** NOT RETAINED cả ba arm. Primary: 0 win, Holm bác 15/24 theo chiều tệ hơn (L2 1/8, L3 7/8, W3 7/8). No-harm tệ hơn: L2 3/13, L3 11/13, W3 4/13. Claim phụ không đạt (0/6).

**Phần đứng vững sau verifier.**
- Pairing, hash, Holm tái lập; `leverages()` khớp đường chéo hat matrix tới 1.9e-15.
- Leverage thật thấp hơn giả thuyết: mean h ở lag_max 2, T40 là 0.276–0.430 (giả thuyết 0.5–0.8); tỉ lệ h > 0.9 chỉ 0.0002–0.0021.
- L3 bơm phương sai pool 1.48–1.92× ở T40 mà raw coverage hầu như không đổi (−0.004 đến +0.016). Raw coverage của v5_1 ở T40: 0.836–0.909.

**Phần bị verifier bác.**
- Suy luận "phần thiếu coverage ở T40 không do leverage, nhiều khả năng do bias" là **non-sequitur**. Bootstrap là mô phỏng recursive-design của SVAR tuyến tính, C(H) chỉ phụ thuộc B, nên phân phối hệ số gần như bất biến với scale chung của residual pool (regressor scale theo shock). Probe trên D-07H: nhân pool 1.3 (variance ×1.69) đổi width trung vị +1.4%; nhân 3.0 (variance ×9) chỉ đổi +2.9%. Phương sai pool không dùng làm diagnostic được. Hệ quả: chính rescale √(m/dof) của v5_1 cũng gần như không có tác dụng.
- "T150 không phải không đổi" bị đọc quá: với L2, raw coverage ở T150 missing đổi +0.000/+0.004; dIS có ý nghĩa (+0.040, +0.060) đến từ factor tune lại nhảy một bậc grid (1.15 → 1.20), không từ pool.
- W3 không phải "gần nguồn nhất": Davidson–Flachaire xét regressor cố định, exogenous, loại trừ lagged dependent variable, sai số heteroskedastic và test với residual có ràng buộc. Họ viết interval thông thường không hưởng lợi từ phiên bản họ khuyên, và heteroskedasticity quan trọng hơn leverage nhiều. Dữ liệu ở đây homoskedastic Gaussian.

**Fidelity với nguồn.** Thấp. L2/L3 áp transform của wild bootstrap fixed-design vào resample row iid, nơi transform chỉ đổi scale pool. Công thức HC2/HC3 đúng.

### 2.6 `leadlag`: gate Haugh lead-lag trước contemporaneous repair

**Đã xây.** `src/paper4/ext_r4leadlag.py`. BH như cũ nhưng không cap; với mỗi candidate, Q của Haugh (bỏ lag 0, trọng số mẫu nhỏ, χ²(2M), M = 4 hoặc 6); p < 0.05 thì gắn nhãn confounded, không repair, nhường slot cho candidate kế tiếp. A: gate trên residual f0; D: gate trên residual chỉ theo skeleton (thêm sau probe D-07H, trước rule; ba biến thể B, C, E bị bỏ ở probe).

**Rule** (hash 12:22Z). V1 identity ở cell không khai báo thiếu cạnh. 8 cell primary {latent1, latent3} × missing × T{80, 150}. RETAINED nếu ≥ 2/8 win, coverage ≥ 0.90, no-harm ở 10 cell (6 cell missing sạch + 4 cell latent T40). AUROC cận dưới ≤ 0.5 ở T150 thì báo "gate not informative".

**Verdict.** NOT RETAINED cả hai. A: 2/8 win (latent3 m0.2 ở T80 −0.045 và T150 −0.044) nhưng no-harm thất bại ở cell sạch T150 (+0.033, +0.043). D: 1/8 win, cùng thất bại no-harm (+0.069, +0.090). Theo rule gate có "informative" (AUROC T150 A 0.592 [0.532, 0.648], D 0.593). Phân rã post hoc ở factor của v5_1: phần gate 0/10 tốt hơn, 0/10 tệ hơn sau Holm, cho cả A và D.

**Phần đứng vững sau verifier.**
- Pre-registration, fidelity với v5_1 (chỉ thêm gate ở bước (3)), không leak truth, mọi đếm và AUROC tái lập với seed khác.
- Phần factor của phân rã: A Holm có ý nghĩa ở 6/10 cell (ví dụ latent3 T150 m0.2 −0.051; sạch T150 m0.2 +0.030). **Re-tune factor cho một method gần v5_1 tự nó tạo win hoặc harm có ý nghĩa.**
- Co-child coverage ở T150: v5_1 0.828–0.853, oracle 0.928–0.937. Probe D-07H: v5_1 tiêu 0.4 (latent1) đến 1.3 (latent3) slot repair mỗi run cho cặp co-child.
- Điểm mù white-noise confounder được xác nhận trên toy known-truth (tỉ lệ gắn nhãn 0.03–0.05, bằng null).

**Phần bị verifier bác.**
- Factor của D ở T40 missing là 2.4, không phải 2.3 như bảng trong doc; cell no-harm T40 của D chưa từng được phân rã.
- "Mọi harm đến từ factor" sai với D latent1 T150 m0.5 (+0.068 = gate +0.027 [−0.020, +0.080] + factor +0.041).
- "Gate không đổi IS" là không bác được, không phải tương đương: CI phần gate của D rộng (latent1 T80 m0.5 +0.107 [−0.004, +0.237]). Với A, có thể nói "không phát hiện tác động".
- Cơ chế "residual VAR chỉ giữ innovation của latent" chỉ đúng cho residual kiểu A. Residual kiểu D (chỉ own lag) tách được confounder phi = 0.8 khỏi cạnh cùng kỳ thật với AUROC đã hiệu chỉnh size 0.74–0.97 ở T150 trên toy. D thất bại trên D-07 vì **cạnh thật cũng rò cross-correlation có lag** (D gắn nhãn 29/41 cạnh lag thật).
- Null χ²(2M) sai cho residual f0: OLS đã làm residual trực giao với các lag mở của cặp, hấp thụ khoảng 2·lag_max bậc tự do. Size thực tế 0.000–0.017 ở mức danh nghĩa 0.05, tới cả T = 1000. Một phần sự "trơ" của A là do test bị miscalibrated; sau khi hiệu chỉnh size, power của A vẫn gần mức danh nghĩa, nên kết luận chính không đổi.
- Kết quả noise0.1 A T150 −0.046 nhiều khả năng do factor (2.4 so với 2.3), không phải do gate.

**Fidelity với nguồn.** Thống kê Haugh được tính đúng (đuôi χ² chính xác; size đúng trên chuỗi trắng độc lập). Lệch: null χ² của Haugh giả định chuỗi đã prewhiten đơn biến, còn đây là residual của hồi quy đa biến có chứa khối lag của cặp (cần hiệu chỉnh kiểu Hosking hoặc Li–McLeod). Hong 1996 chỉ được trích, không dùng kernel. Logic negative control chỉ khớp lỏng: gate gộp lead và lag cả hai chiều, mà lag không phải negative control khi có thể thiếu cạnh lag thật.

### 2.7 `prepivot`: double bootstrap rút gọn, không bank factor

**Đã xây.** `src/paper4/ext_r4prepivot.py`. 199 outer draw trùng v5_1 từng bit; 39 outer series đầu, mỗi series chạy lại toàn bộ v5_1 với 19 inner draw. Root r = |C0 − mean C**| / sd C**; f_d = quantile 0.95 / z_ref. Tinh chỉnh trước run: (R1) thế giới tầng trong do chính thủ tục chạy trên x_b sinh ra; (R2) root chỉ trên pair ngoài đường chéo có |C0| > 0.1; (R3) z_ref = t_{0.975,18}·√(20/19) = 2.1555.

**Rule** (hash 12:18:43Z, run bắt đầu 12:18:48Z). 9 cell (T{40, 80} × missing/reversed × 0.2/0.5 + none T80). Non-inferior nếu cận trên 95% của IS_pp/IS_v51 < 1.10 (Holm 9). RETAINED nếu non-inferior ≥ 7/9 và coverage ≥ 0.90 ở cả 9.

**Verdict.** NOT RETAINED: non-inferior 0/9 sau Holm, **tệ hơn v5_1 ở 9/9** sau Holm, coverage ≥ 0.90 chỉ 1/9 (T40 missing-0.2: cov 0.922 → 0.828, R 1.196). Bản `_orig` cũng thất bại (non-inferior 1/9, coverage 0/9).

**Phần đứng vững sau verifier.**
- Pre-registration và pairing (540/540, 720/720, 600/600, 720/720) tái lập; không leak truth; không calibrate trên D-07.
- f_pp chỉ bằng 0.65–0.84 lần bank factor hiệu dụng ở 9 cell primary.
- Run phụ: T150 non-inferior (R 0.98–1.05, coverage 0.90–0.94); lag_max 1 T19/25 coverage ≥ 0.90 chỉ 1/10 cell; latent1/noise0.1 tệ hơn 12/12.
- Panel thật: f_pp nhỏ hơn bank factor lag1 T19 ở cả 4 khai báo.
- Runtime 4.8–5.6× v5_1.

**Phần bị verifier bác.**
- Diễn giải "bank factor chủ yếu bù bias cấu trúc, không phải sai số mẫu nhỏ" **không đứng vững**. (a) Bank factor hiệu dụng không tăng theo damage: none ≥ missing ở mọi T (T40 1.30 so với 1.15; lag1 T25 1.90 so với 1.50). (b) Với skeleton đúng (none), f_pp vẫn thiếu xa (T80 1.098 so với 1.30) và pp undercover (0.898–0.904). Probe oracle trên D-07H: factor cần cho 0.95 coverage là 1.65 ở none T80 và T40, trong khi f_pp khoảng 1.09–1.17. **Double bootstrap rút gọn bị undercalibrated ngay cả khi không có damage cấu trúc.** (c) Spearman −0.62 chủ yếu là tương phản giữa nhánh v3 (none) và nhánh targeted (missing); trong riêng missing chỉ −0.18 đến −0.45.
- `pp_orig` không phải "đúng như đề xuất": nó vẫn giữ R1, nên thiết kế đúng của spec chưa từng chạy.
- "Non-inferior và đủ coverage ở cell vô hại (extra)" sai: coverage chỉ đạt ở 1/4 cell extra với T ≤ 80.
- Hướng tiếp "đưa damage giả vào thế giới tầng trong" dựa trên attribution sai, nên không đóng được khoảng thiếu ở cell none.

**Fidelity với nguồn.** Xấp xỉ: đây là calibration kiểu Loh 1987 dùng xấp xỉ normal (quantile của root studentized), không phải prepivoting đúng nghĩa của Beran (biến đổi root bằng CDF bootstrap của nó; 19 inner draw không đủ). Nên gọi là "calibration kiểu Loh với xấp xỉ normal". Khuyến nghị số inner draw của Martin 1990 chưa được kiểm. FDB của Davidson–MacKinnon không dùng được (B_i = 1 không cho sd).

### 2.8 `hubscreen`: CSIS cho phương trình hub underdetermined

**Đã xây.** `src/paper4/ext_r4hubscreen.py`, method `tolerant_v5_1_hs`. Khi một phương trình fail check underdetermined (ở screening hoặc fitting), giữ tập điều kiện C_j (own lag + cha cùng kỳ), xếp hạng các lag term còn lại (gộp chung term skeleton và term của khối mở) theo |t| khi thêm riêng từng term vào OLS trên [1, C_j], giữ top d = floor(m/2.5) − 1 − |C_j|. Hai width factor: f_v51 cho run không rút gọn, f_red tune trên run rút gọn của D-07H. Thêm mốc `plugin_hs_cal`. Tinh chỉnh trước rule: probe D-07H cho thấy lưới đề xuất (lag 2 T{30, 35, 40}, lag 1 T{19, 25, 30}) gần như không có rút gọn, nên lưới chính đổi thành lag 2 × T{19, 25, 30, 35} × {missing, reversed, extra}-0.2.

**Rule** (ghi trước run lag 2; theo mtime). V2: candidate trùng v5_1 trên mọi run không rút gọn mà v5_1 ok. C1: hoàn tất ≥ 59/60 ở cả 12 cell. C2: ITT coverage ≥ 0.90 ở ≥ 10/12, không cell nào < 0.85. C3: trên run v5_1 hoàn tất, IS ratio ≤ 1.05 và không tệ hơn sau Holm. C4: IS ≤ `plugin_cal` ở ≥ 6/12 cell.

**Verdict.** **RETAINED (exploratory).** V2 1458/1458; C1 12/12 (60/60 mọi cell); C2 ITT 0.924–0.976, Holm bác "ITT ≤ 0.90" 12/12; C3 ratio đạt 12/12, tệ hơn 0/11; C4 8/12 (thắng Holm 4, thua Holm 1).

**Phần đứng vững sau verifier.**
- Re-run 4 unit D-07: 216/216 row khớp chính xác. Pairing T40 với `ext_v51_eval` và `a2_baselines` 240/240.
- Số trong ruling tái lập: v5_1 chỉ hoàn tất 0/8/3 run (trên 60) ở T19, 26/36/33 ở T25; coverage trên run "được cứu" 0.931–1.000.
- Đuôi IS rất nặng: T19 missing mean 152.63, median 25.17, max 4206.65.
- `_cond_t` khớp OLS |t| trực tiếp; known-truth (hub, T19) recall term thật 0.42–0.75 so với 0.25 ngẫu nhiên.
- Panel thật: ở lag 1, v5_1 chạy được ở cả 4 khai báo không cần rút gọn (giả thuyết "chặn phân tích lag 1" sai, đã báo đúng); ở lag 2 chỉ candidate chạy được, width trung vị 2.12–7.30, gần như không interval nào loại được 0.

**Phần bị verifier bác.**
- "Strict superset, trùng hệt v5_1 ở mọi chỗ v5_1 chạy được" **sai**: v5_1 hoàn tất 1556 run, candidate trùng ở 1458; 98 run khác vì candidate rút gọn ở mức draw hoặc screening, nơi v5_1 bỏ draw hỏng hoặc rơi về tập mở ở mức data. V2 vòng tròn vì chỉ kiểm run có `hs_reduced = 0`.
- C4 chủ yếu đo v5_1 so với `plugin_cal`: ở 7/8 cell thắng, đa số run ghép cặp trùng v5_1. Ở hai cell mà đa số run là được cứu hoặc rút gọn (T19 missing, T25 missing), candidate tệ hơn (+299.46 có ý nghĩa; +1.67).
- Win ở T19 reversed (p "0.0000") chỉ dựa trên 8 run từ 3 cluster: p bootstrap suy biến.
- Trên run được cứu ở T ≤ 25, `plugin_hs_cal` (cùng phép rút gọn, không có máy móc tolerant) có mean IS thấp hơn ở **6/6 cell** (T19 missing 45.92 so với 152.63) với coverage tương đương. Nếu C4 dùng mốc này thì chỉ đạt 5/12, dưới ngưỡng. Median thì nghiêng về candidate ở 5/6.
- Ở T19 reversed và extra, 76–77% lần rút gọn rơi vào nhánh |C_j| > cap − 1: nhánh này bỏ own lag 2 ở mọi trường hợp và **bỏ ít nhất một cha cùng kỳ khai báo** ở 55% (reversed) và 38% (extra). Ở đó phép rút gọn là truncation xóa cạnh skeleton, không phải CSIS.
- C2 gần như tự động: f_red tune trên run rút gọn từ cùng generator.

**Fidelity với nguồn.** Một phần. Xếp hạng theo |t| là họ hàng đơn điệu của partial correlation, không phải |β| chuẩn hóa của Barut et al.; d cố định thay vì ngưỡng theo dữ liệu (đã nêu). Lệch không nêu: nhánh |C_j| > cap − 1 bỏ một phần X_C, điều nguồn không có; với d 3–5 ở m 17, lý do sure screening (d tăng theo n) không áp dụng.

---

## 3. Cái gì cải thiện `tolerant_v5_1`, cái gì ghép được, cái gì thất bại

### 3.1 Theo từng weakness đã biết

| Weakness | Candidate | Kết quả sau verifier |
|---|---|---|
| Width factor tune trên bank (bị chê ad hoc) | `mondrian`, `prepivot`, `kilianbab`, `levboot` | **Chưa giải quyết.** Thứ duy nhất dùng được là cách mô tả M0 (conformal quantile trên bank, không guarantee mức pair). Factor không giảm được nhờ bias correction (re-centering làm draw rộng hơn) hay leverage (pool scale gần như trơ). Width rule không cần bank (`prepivot`) undercalibrated ngay cả khi skeleton đúng |
| Hướng ngẫu nhiên; reversal undercoverage 0.06–0.08 so với oracle | `ngorient`, `mondrian` M2 | **Cải thiện nhỏ, chỉ dưới non-Gaussian shock tổng hợp:** NG-A v2 thu hẹp 14–38% khoảng cách ở 4/4 cell reversed ng_mix (Holm), không nới interval. Dưới Gaussian không có gì mới (dl_e đã thử ở revlag3). M2 tăng coverage cặp reversal ở 2/6 cell T150 nhưng bằng cách nới lớp R |
| Measurement noise 30% | (không candidate nào) | Không đổi. EM-Kalman, SIMEX, modified Yule–Walker hoãn |
| Latent confounder bị đọc thành cạnh thiếu | `leadlag` | **Không cải thiện.** Gate A trơ (null sai, power thấp); gate D rò vì cạnh thật cũng tạo cross-correlation có lag. Có thêm số đo cho limitation: co-child coverage 0.83–0.85 so với oracle 0.93 ở T150 |
| Interval rộng ở T nhỏ | `lfdropen`, `kilianbab`, `levboot` | **Không cải thiện.** Mở ít hơn làm factor tăng mạnh; BaB và leverage làm draw rộng hơn hoặc không đổi |
| Hub underdetermined ở lag_max 2, T < 40 | `hubscreen` | **Chạy được** (completion 60/60, ITT coverage ≥ 0.92) nhưng đuôi IS nặng, ở nhánh truncation bỏ cha cùng kỳ, và không tốt hơn `plugin_hs_cal` về mean IS trên run được cứu |
| Chỉ có Gaussian | `ngorient` | Có generator non-Gaussian đầu tiên (`ng_mix`, `ng_t10`, trong driver). v5_1 với factor Gaussian giữ coverage 0.91–0.97 dưới cả hai |

### 3.2 Cái gì ghép được

Các thành phần còn giá trị chạm vào các bước rời nhau:
- `hubscreen` (bước (1)–(2)) chỉ hoạt động trên phương trình mà v5_1 sẽ fail, tức ở lag_max 2, T ≤ 30, cộng 98 run ở T25/T30 có rút gọn ở mức draw.
- NG-A (bước (3)–(4)) chỉ khác v5_1 khi gate mở; dưới Gaussian gate mở 7–8% ở T40, 10–12% ở T80, 17–18% ở T150; ở T ≤ 30 gate gần như luôn đóng.
- M0 (bước (6)) chỉ là cách mô tả, không đổi số.

Vì vậy ba thứ ghép với nhau gần như không tương tác: vùng hoạt động của `hubscreen` (T ≤ 30) và của NG-A (T ≥ 80, non-Gaussian) gần như không giao nhau. Điều kiện ghép: NG-A phải thừa kế factor frozen của v5_1 (bài học của v1), và `hubscreen` dùng f_red cho run rút gọn.

Không nên ghép: `kilianbab` (tệ hơn ở mọi cell primary; gây hại dưới latent), `levboot` (trơ hoặc tệ hơn), `lfdropen` (tệ hơn), `leadlag` (trơ ở factor bằng nhau), `prepivot` (tệ hơn 9/9), M2 (không tốt hơn M0, gây hại dưới noise0.1).

### 3.3 Cái gì thất bại và bài học

1. **Re-centering không mua được width (`kilianbab`).** Bias về phía 0 là thật và đo được, nhưng ở n = 14 với selection/repair/reversal, sửa bias đẩy fit về gần biên non-stationary và làm draw rộng hơn phần tiết kiệm. Kilian 1998 vẫn đúng trong bối cảnh gốc (verifier tái lập trên VAR(1) hai biến); thất bại nằm ở việc chồng lên pipeline có selection.
2. **Scale của residual pool gần như không ảnh hưởng interval (`levboot`).** Trong recursive-design bootstrap của SVAR tuyến tính, regressor scale theo shock, nên phân phối của B (và của C(H)) gần như bất biến với scale chung của pool. Hệ quả: mọi hiệu chỉnh chỉ đổi variance của pool (HC2, HC3, √(m/dof)) đều gần như vô dụng ở đây. Muốn tách leverage khỏi bias cần một thiết kế khác (fixed-design bootstrap, hoặc đo bias của C(H) với truth trên D-07H).
3. **Mở ít hơn thì tệ hơn, nhưng chưa biết 3k có tối ưu không (`lfdropen`).** Ở T40 screening không đủ power để xếp cạnh thiếu thật vào top k; chi phí bỏ sót lớn hơn phần variance tiết kiệm. Vòng 1 cho thấy mở mọi lag cũng tốn 30–35%. K tối ưu nằm đâu đó giữa; một luật mở mềm trên sàn 3k (Stein shrinkage, JMA) là hướng còn để ngỏ.
4. **Gate dựa trên cross-correlation có lag không tách được confounder trong VAR (`leadlag`).** Hai lý do khác nhau cho hai biến thể: residual f0 hấp thụ cả dấu vết của latent lẫn bậc tự do của null; residual chỉ theo skeleton thì giữ dấu vết latent nhưng cạnh thật cũng rò. Điểm mù white-noise confounder dưới Gaussian không có cách nào gỡ bằng dữ liệu bậc hai.
5. **Double bootstrap rút gọn không thay được bank (`prepivot`).** Với 39 × 19 draw và xấp xỉ normal, calibration theo dataset undercalibrated cả khi skeleton đúng (cần 1.65, được khoảng 1.1). Không nên đọc thất bại này như bằng chứng rằng bank factor "chủ yếu là bias cấu trúc".
6. **Chia lớp Mondrian không chuyển từ calibration bank sang eval bank ở T40 (`mondrian` M2).** Với khoảng 20 topology, quantile theo lớp không ổn định.
7. **Unit test phải phủ đúng hỗn hợp của kịch bản (`ngorient`).** Unit test chỉ dùng cặp cùng law, trong khi 3/4 cặp của ng_mix là khác law, đúng chỗ luật dấu kurtosis hỏng.

**Bài học quy trình xuyên suốt.**
- **Factor re-tune là nguồn nhiễu lớn ngang hiệu ứng cần đo.** Re-tune factor cho một method gần v5_1 dịch IS khoảng ±0.03–0.07 (leadlag: phần factor có ý nghĩa ở 6/10 cell; ngorient v1; levboot ở T150). Từ vòng 5: arm xây trên v5_1 thừa kế factor frozen, hoặc báo phân rã gate/factor ngay trong rule.
- **Calibration trên 1 replicate D-07H không ổn định ở T40** (q 1.30 → 1.64 với 3 replicate). Điều này cũng là một threat của chính factor frozen của v5_1.
- **p bootstrap suy biến khi số cluster nhỏ** (3 cluster ở hubscreen T19 reversed). Rule vòng 5 nên đòi tối thiểu số cluster cho một cell được tính là win.
- **Kết luận ở mức verdict đứng vững; diễn giải cho paper thì không.** Verifier bác ít nhất một diễn giải ở cả 8 candidate. Mọi câu đưa vào paper từ vòng 4 phải lấy từ phần "đứng vững" ở mục 2, không từ summary của candidate.
- **Analyzer phải nằm trong hash.** `kilianbab` (analyze.py không hash) và `lfdropen` (analyzer sửa sau preview) đều không làm đổi verdict, nhưng vòng 5 nên hash analyzer cùng rule.

Lead không tính overlay Holm toàn family qua 8 candidate. Với số win ít như trên, một overlay rộng hơn chỉ có thể giảm số win.

---

## 4. Đề xuất vòng 5

### 4.1 Phiên bản ghép `tolerant_v5_2` (đề xuất, chưa xây)

`tolerant_v5_2` = `tolerant_v5_1` + hai thành phần sửa theo verifier + một thay đổi cách viết:

**(A) NG-A v3 ở bước (3)–(4).**
- Sửa luật dấu: không dùng dấu kurtosis trung bình của cặp. Tính R như hiệu log-likelihood xấp xỉ của hai hướng (HS 2013 mục 2), với hàm log-density G_i chọn **theo từng biến** từ dấu excess kurtosis của chính biến đó (họ log cosh cho super-Gaussian, một họ sub-Gaussian cho sub-Gaussian), và dạng skew (eq. 13) khi skew trội. Phần gate JB, jackknife se, cắt p, Plackett–Luce và common random numbers giữ như v2.
- Factor: thừa kế factor frozen của v5_1, không re-tune.

**(B) `hubscreen` v2 ở bước (1)–(2), chỉ cho phương trình sẽ fail.**
- Không bao giờ bỏ cha cùng kỳ khai báo. Khi |C_j| > cap − 1: bỏ own lag 2..lag_max trước; nếu vẫn vượt và phương trình không qua được check `len(terms) + 2 ≤ m` của `fit_equations` thì run được ghi là fail (tính vào ITT).
- Output mang cờ `hs_reduced` và số phương trình bị rút gọn.
- Identity được định nghĩa trung thực: trùng v5_1 trên run mà cả data lẫn mọi draw đều không rút gọn; số run v5_1-ok bị đổi phải báo.
- f_red tune trên **3 replicate** D-07H development (vì 1 replicate không ổn định ở T nhỏ).

**(C) Bước (6) không đổi.** Factor frozen của v5_1 cho run không rút gọn. Paper mô tả bước (6) theo cách M0 (mục 2.3), không claim guarantee mức pair.

### 4.2 Rule ghi trước cho vòng 5 (bản nháp; phải được hash cùng analyzer trước run đầu tiên)

**Dữ liệu.** D-07 development, 20 topology × 3 replicate, **seed_base mới chưa từng dùng** (đề xuất 70261102; guard kiểm không có manifest nào dùng seed này). Calibration f_red trên D-07H development, 3 replicate. Không đụng P4-H1, P4-H2.

**V0 (unit test NG-A v3, trước mọi bank run).** LiNGAM hai biến, b ∈ {0.3, 0.6}, m ∈ {78, 148, 400}, 500 rep, **mọi cặp law có thứ tự** từ {Laplace, t5, skewexp(±), uniform, Gaussian}. Đạt nếu:
- tỉ lệ sai hướng (khi gate mở) trung bình theo hỗn hợp law của ng_mix ở m 148, b 0.6 ≤ 0.10;
- không cặp law non-Gaussian nào sai > 0.30 ở m 400, b 0.6;
- tỉ lệ sai hướng trung bình ở m 400 ≤ ở m 148 (consistency);
- dưới Gaussian: gate-open ≤ 0.12, mean p trong 0.5 ± 0.02; bất biến scale |dp| ≤ 1e-9.

V0 thất bại thì bỏ thành phần (A) khỏi vòng 5.

**V1 (identity).** Ở mọi cell none/extra, và ở mọi run không gate nào mở và không rút gọn, `tolerant_v5_2` trùng v5_1 từng bit. Báo số run v5_1-ok bị đổi do (B).

**P1 (thành phần A, kịch bản ng_mix).** 8 cell primary ng_mix × T{80, 150} × {missing, reversed} × {0.2, 0.5}. Endpoint chính là **gộp**: trung bình qua 8 cell của dIS/IS_v51, CI từ topology-cluster bootstrap (B 20000, seed 20261104); đạt nếu cận trên 95% một phía < 0. Phụ: số win theo Holm 8 từng cell (báo, không quyết định); coverage cặp chịu ảnh hưởng ở 4 cell reversed, Holm 4. Ghi rõ trong doc: đổi từ luật "≥ 3/8 win" sang endpoint gộp là quyết định đưa ra **sau** khi thấy v2 (8/8 dIS âm nhưng nhỏ); seed mới giảm nhưng không xóa vấn đề này, nên kết quả vẫn là exploratory.

**P2 (thành phần B, region grid Gaussian).** lag_max 2 × T{19, 25, 30, 35} × {missing, reversed, extra}-0.2 (12 cell). Đạt nếu:
- completion ≥ 59/60 ở cả 12 cell (fail do luật mới trong (B) tính vào);
- ITT coverage ≥ 0.90 ở ≥ 10/12, không cell nào < 0.85;
- trên run được cứu ở 6 cell T ≤ 25, so với `plugin_hs_cal`: cận trên 95% của tỉ số mean IS < 1.10 ở ≥ 4/6 cell (median IS báo kèm);
- một cell chỉ được tính là win hay thua có ý nghĩa nếu có ≥ 8 topology cluster.

**No-harm (cho bản ghép).**
- (a) 21 cell Gaussian G: IS ratio ≤ 1.03, không tệ hơn sau Holm 21, coverage ≥ 0.90 nơi v5_1 đạt.
- (b) 13 cell ng_mix không primary: IS ratio ≤ 1.05, coverage ≥ 0.90 nơi v5_1 đạt.
- (c) latent1 và noise0.1 × T{80, 150} × {missing, reversed}-0.2 (8 cell): chỉ mô tả.

**Verdict.**
- RETAINED-combined nếu V0, V1, P1, P2 và no-harm (a), (b) đều đạt.
- Nếu chỉ một trong P1, P2 đạt (kèm V1 và no-harm của riêng thành phần đó): giữ riêng thành phần đó.
- Nếu không: không giữ gì, v5_1 giữ nguyên.

**Quy tắc factor.** Không re-tune factor cho bất kỳ arm nào ngoài f_red. Mọi so sánh với v5_1 ở factor bằng nhau.

**Runtime ước lượng.** G Gaussian và ng_mix mỗi cái khoảng 35–40 phút (NG-A +45%), region grid khoảng 35 phút, calibration f_red 3 replicate khoảng 15 phút, unit test vài phút: tổng khoảng 2–2.5 giờ với `--workers 3` trên máy dùng chung.

### 4.3 Có nên xin người dùng duyệt một held-out check trên P4-H2 development?

**Khuyến nghị của lead: chưa xin bây giờ. Chỉ xin khi `tolerant_v5_2` (hoặc một thành phần) đạt rule vòng 5.**

Lý do nên dùng P4-H2 development (khi đến lúc):
- Toàn bộ dữ liệu "mới" của vòng 4 (kể cả seed 50261102 của `ngorient` v2) dùng **cùng 20 topology** của D-07. Đơn vị exchangeable là topology (mục 2.3), nên bằng chứng thật sự độc lập phải đến từ topology mới. P4-H2 development là split duy nhất còn chưa mở có topology mới.
- Hiệu ứng của NG-A nhỏ (1–4% IS) và gom theo topology, đúng loại hiệu ứng dễ bị nắn theo một bank đã dùng nhiều lần.

Lý do chưa dùng:
- Chưa có thành phần nào đạt rule ở vòng 4 ngoài `hubscreen`, và `hubscreen` v1 có lỗi bỏ cha cùng kỳ. Tiêu P4-H2 development cho một phiên bản chưa đạt gì là phí.
- Đây là split chưa mở cuối cùng của generator hiện tại; sau nó, mọi kiểm tra độc lập đều cần sinh bank mới (P4-H3), cũng phải được người dùng duyệt.
- Kết quả trên P4-H2 development vẫn chỉ là **held-out exploratory**; claim xác nhận vẫn cần bank niêm phong mới P4-H3.

Nếu vòng 5 đạt, lead sẽ đề xuất một lượt chạy duy nhất, spec frozen và hash (gồm cả `experiments/ext/r4ngorient/laws.py` vì generator ng_mix đang nằm trong driver), chạy qua lead guard như P4-H2 confirmatory, cùng rule vòng 5. Quyết định tiêu split này là của người dùng.

### 4.4 Các hướng khác cho vòng 5 hoặc sau đó (không nằm trong phiên bản ghép)

- **Bias-aware honest CI (Armstrong–Kolesár)** cho bước (6): sau khi `mondrian` và `prepivot` thất bại, đây là ứng viên còn lại có lý thuyết cho chỉ trích "ad hoc". Cần chọn bound M theo damage khai báo và Jacobian của C(H).
- **Conformal hai tầng (Dunn–Wasserman–Ramdas 2023)** để phát biểu factor với đơn vị là topology.
- **Mở mềm trên sàn 3k** (Stein shrinkage của Hansen 2016, hoặc JMA): hướng còn để ngỏ sau `lfdropen`.
- **Sparse + low-rank residual precision** cho latent confounder ≥ 3 node: hướng tiếp theo sau `leadlag`.
- **Drautzburg–Wright và RCD**: chỉ nên làm nếu NG-A v3 qua V0 và P1.
- **Calibration nhiều replicate cho chính v5_1 ở T40:** chỉ mô tả độ nhạy, không đổi module of record.

Không đề xuất làm tiếp: `leadlag` với df hiệu chỉnh (power vẫn gần mức danh nghĩa sau hiệu chỉnh size), `prepivot` với damage giả trong thế giới tầng trong (dựa trên attribution sai), mọi hiệu chỉnh variance của residual pool.

---

## 5. Limitations cập nhật (cho phần limitations/threats của paper)

1. **Width factor vẫn được tune trên calibration bank.** Có thể mô tả nó là conformal quantile thực nghiệm (tương đương trong 0.5% IS), nhưng không có guarantee hữu hạn mẫu ở mức pair: pair không exchangeable, đơn vị exchangeable là topology (khoảng 20). Factor T40 nhạy với mẫu calibration (q 1.30 → 1.64 khi dùng 3 replicate thay vì 1). Ba hướng thay thế đã thử đều thất bại: calibration theo dataset (`prepivot`, tệ hơn 9/9, undercalibrated ngay cả khi skeleton đúng), bias correction (`kilianbab`), leverage correction (`levboot`).
2. **Interval ở T ≤ 80 lệch về phía 0.** 97–100% số lần trượt của v5_1 nằm ở phía 0 (oracle 89–95%). Kilian re-centering giảm nửa độ lệch nhưng không giảm width cần thiết.
3. **Hướng của cạnh repair và cạnh reversal vẫn ngẫu nhiên dưới Gaussian.** Dưới non-Gaussian shock tổng hợp, orientation theo non-Gaussianity (NG-A v2) thu hẹp 14–38% khoảng cách coverage của cặp reversal, nhưng chưa đạt rule, có lỗi cấu tạo cho cặp khác law, và chỉ là exploratory.
4. **Latent confounder.** Ở T150, v5_1 tiêu 0.4–1.3 slot repair mỗi run cho cặp co-child (probe D-07H) và cover cặp co-child 0.83–0.85 (oracle 0.93). Gate lead-lag không giúp. Confounder dạng white noise không phân biệt được với cạnh cùng kỳ dưới Gaussianity.
5. **Measurement noise.** Không đổi so với vòng 3; không candidate vòng 4 nào nhắm tới.
6. **T nhỏ và hub.** v5_1 fail ở lag_max 2, T ≤ 30 (ở T19 missing hoàn tất 0/60). Chế độ dự phòng `hubscreen` chạy được với ITT coverage ≥ 0.92 nhưng đuôi IS rất nặng (T19 missing mean 152.6, median 25.2), ở T19 thường bỏ cha cùng kỳ khai báo, và trên run được cứu không tốt hơn `plugin_hs_cal` về mean IS.
7. **Panel thật 14 × 19.** Ở lag_max 1, v5_1 chạy được không cần rút gọn. Ở lag_max 2 chỉ chế độ dự phòng chạy được, và gần như không interval nào loại được 0. Residual của panel thật không cho bằng chứng non-Gaussian (Holm p nhỏ nhất 0.395), nhưng JB gần như không có power ở m = 17; vì vậy orientation theo non-Gaussianity khó giúp trên panel thật. Không có width rule nào không cần bank dùng được ở đây (`prepivot` coverage ≥ 0.90 chỉ 1/10 cell ở lag_max 1, T19/25).
8. **Phân phối shock.** Đến vòng 3 chỉ có Gaussian. Vòng 4 có bằng chứng exploratory rằng v5_1 với factor Gaussian giữ coverage 0.91–0.97 dưới ng_mix và t10. Chưa có kịch bản heteroskedastic hay phi tuyến.
9. **Varsortability của bank cao** (0.88–0.94; R²-sortability 0.53–0.59). v5_1 không dùng thứ tự variance biên, nhưng paper nên báo con số này để trả lời chỉ trích "benchmark gaming".
10. **D-07 đã dùng lại nhiều lần.** Mọi kết quả vòng 4 là exploratory. Kể cả seed mới cũng dùng lại 20 topology đó.
11. **Bẫy trong code có sẵn (báo, không sửa):**
    - `run_experiment.py` ghi đè factor frozen trước khi lưu `calibration.json`, nên factor tune lại của một method frozen bị mất (dòng 429–435).
    - `run_experiment.py` lặng lẽ bỏ width factor của method không có trong `calibrate_methods`.
    - `ext_seed` gắn stream theo tên method, nên code giống hệt dưới tên khác không được ghép cặp bằng random numbers. Các driver vòng 4 tự vá ở phía worker.
    - Check underdetermined của `screen_pairs` chặt hơn của `fit_equations`, nên ở T25–35 nhánh targeted của v5_1 fail ngay ở screening dù phương trình vẫn fit được.
    - Instrumentation của `mondrian`, `levboot`, `prepivot` thay tạm hàm module-level trong lúc gọi; an toàn với runner nhiều process, không an toàn nếu gọi đa luồng trong cùng process.
    - Bug E1 (seed theo vị trí cell) vẫn chưa sửa, theo quyết định của người dùng ở vòng 3.

---

## Phụ lục: file của vòng 4

Doc từng candidate: `docs/ext/r4kilianbab.md`, `r4ngorient.md`, `r4mondrian.md`, `r4lfdropen.md`, `r4levboot.md`, `r4leadlag.md`, `r4prepivot.md`, `r4hubscreen.md`.

Module: `src/paper4/ext_r4kilianbab.py`, `ext_r4ngorient.py`, `ext_r4mondrian.py`, `ext_r4lfdropen.py`, `ext_r4levboot.py`, `ext_r4leadlag.py`, `ext_r4prepivot.py`, `ext_r4hubscreen.py`.

Ruling: `results/ext_r4kilianbab_eval/ruling.md`, `results/ext_r4ngorient_v2_analysis/ruling.md` (và v1: `results/ext_r4ngorient_analysis/ruling.md`), `results/ext_r4mondrian_eval/ruling.md`, `results/ext_r4lfdropen_analysis/ruling.md`, `results/ext_r4levboot_g/ruling.md`, `results/ext_r4leadlag_rule/ruling.md` (phân rã: `decomp.md`), `results/ext_r4prepivot_primary/ruling.md`, `results/ext_r4hubscreen_ruling/ruling.md`.

Verifier: `experiments/ext/verify4_<id>/` và `results/ext_verify4_<id>/` cho mỗi id trong {kilianbab, ngorient, mondrian, lfdropen, levboot, leadlag, prepivot, hubscreen}.

Frozen spec: chỉ `hubscreen` có (`experiments/ext/r4hubscreen/spec_files.json`). Không có run held-out nào.
