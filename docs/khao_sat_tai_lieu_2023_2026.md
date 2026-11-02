# Khảo sát tài liệu 2023–2026 cho Paper 4

**Phạm vi.** Ba hướng được khảo sát song song (2/11/2026):

1. Ước lượng hiệu ứng khi đồ thị nhân quả không chắc chắn (structure uncertainty).
2. Kinh tế lượng chuỗi thời gian: SVAR, local projection (LP), suy luận vững khi mô hình sai, external instruments.
3. Chẩn đoán đồ thị được cung cấp, biến ẩn và nhiễu đo, prior từ LLM có lỗi.

**Độ tin cậy.** Mỗi tài liệu đã được agent tra trên trang arXiv, venue hoặc DOI (đúng tiêu đề và tác giả). Một số chỉ xác nhận qua trang listing, đã ghi chú bên cạnh. Chưa đọc full text, chỉ đọc abstract. **Cần đối chiếu lại trước khi trích dẫn trong bài.**

## 1. Kết luận chính

- **Chưa thấy công trình nào làm đúng bài toán của Paper 4:** cho interval của **hiệu ứng động** (cumulative IRF) với coverage được hiệu chỉnh, từ một skeleton được cung cấp có lỗi, và dùng **mức hỏng khai báo** (chỉ số lượng, không biết vị trí) để nhắm chỗ nới lỏng.
  - Các công trình về structure uncertainty đều làm trên dữ liệu i.i.d. và hiệu ứng tĩnh.
  - Các công trình chuỗi thời gian dừng ở độ tin cậy của cạnh hoặc identifiability.
  - Các công trình SVAR thì lấy trung bình qua các cách nhận diện (identification), không hiệu chỉnh coverage theo kiểu frequentist, và không có "ngân sách lỗi" khai báo.
- **B1 (tự ước lượng mức hỏng) là khoảng trống thật.** Không có phương pháp nào ước lượng số cạnh sai của một đồ thị cho trước kèm đảm bảo. Coherency score của Faltenbacher và cộng sự tự nhận chỉ là "heuristic proxy" cho SHD.
- **A1 (biến ẩn) là khoảng trống thật.** Tài liệu có nói rằng tương quan phần dư do biến ẩn là một bidirected edge (SVAR-FCI, LPCMCI). Nhưng chưa ai đánh giá bước "sửa cạnh thiếu bằng tương quan phần dư" khi có confounder. Thực nghiệm A1 của mình là mới.
- **Rủi ro định vị lớn nhất:** Chang, Guo & Malinsky (Biometrika 2026). Bài này lấy union của interval qua nhiều đồ thị khả dĩ, rất gần ý tưởng của module, nhưng làm trên dữ liệu i.i.d. và không có lag. Bài viết của mình phải trích dẫn và phân biệt rõ.

## 2. Công trình gần nhất (cần định vị so với chúng)

| Công trình | Làm gì | Khác Paper 4 ở đâu |
|---|---|---|
| Chang, Guo, Malinsky. *Post-selection inference for causal effects after causal discovery*. Biometrika 2026; arXiv 2405.06763 | Chạy PC nhiều lần với test statistic bị nhiễu ngẫu nhiên, lọc đồ thị, lấy **union interval**. Coverage đúng theo tiệm cận | Dữ liệu i.i.d., Gaussian. Đồ thị **học từ dữ liệu**, không phải skeleton cho sẵn. Không có lag hay IRF. Không có mức hỏng khai báo |
| Padh, Li, Casolo, Kilbertus. *Your Assumed DAG is Wrong and Here's How To Deal With It*. CLeaR 2025; arXiv 2502.17030 | Tối ưu để chặn trên/dưới hiệu ứng trên tập đồ thị phù hợp với tri thức không hoàn hảo | Chặn **population** (không có sampling uncertainty). I.i.d. |
| Strieder & Drton. JCI 2023; CLeaR 2024 (dual likelihood); nền tảng: Strieder và cộng sự, UAI 2021 | Vùng tin cậy gộp cả bất định cấu trúc lẫn độ lớn hiệu ứng | Giả định phương sai nhiễu bằng nhau. **Phát hiện quan trọng:** bootstrap under-cover khi có structure uncertainty, kể cả n lớn. Đây là luận cứ cho bước hiệu chỉnh width của module |
| Singh và cộng sự. *CausalGuard*. arXiv 2605.21928 (2026, preprint) | Prior cạnh từ LLM → sinh DAG → lọc bằng CI test → trọng số BIC → conformal | I.i.d. Conformal không áp dụng được cho chuỗi T = 19 |
| Giacomini, Kitagawa, Volpicella. *Uncertain identification*. Quantitative Economics 2022 | Robust Bayes, lấy trung bình qua các SVAR có ràng buộc nhận diện khác nhau | Có SVAR và IRF, nhưng không hiệu chỉnh coverage và không có mức hỏng |
| Ahelegbey, Billio, Casarin. JAE 2016 | MCMC đồng thời trên DAG cùng kỳ, đồ thị lag và tham số VAR | Bayesian. Prior không gắn với skeleton cho sẵn |
| Keweloh (và Wang). *Uncertain Short-Run Restrictions…*. arXiv 2303.13281; JAE 2026 theo RePEc | Co về các ràng buộc zero, tự ngừng co khi dữ liệu bác bỏ. **Gần nhất với "skeleton có zero sai"** | Cần nhiễu non-Gaussian và GMM bậc cao, nên chỉ khả thi với T lớn |

**Câu định vị đề xuất:** Paper 4 là phương pháp frequentist cho SVAR ở T nhỏ:
- dùng **ngân sách lỗi khai báo** (số cạnh thiếu, thừa, đảo) để nhắm phần cấu trúc cần nới lỏng;
- **hiệu chỉnh coverage bằng thực nghiệm**, đáp lại phát hiện của Strieder và cộng sự rằng bootstrap under-cover;
- đánh giá trade-off coverage/width theo từng loại hỏng, cho cumulative IRF.

## 3. Ứng viên baseline đã công bố

| Baseline | Nguồn | Trạng thái |
|---|---|---|
| IDA-style union trên Markov equivalence class | Maathuis, Kalisch, Bühlmann, Annals of Statistics 2009 | **Đã implement** (`ida_union`) |
| BVAR với Minnesota prior, hyperparameter chọn bằng marginal likelihood | Minnesota prior; Giannone, Lenza, Primiceri 2015 | **Đã implement** (`bvar_minnesota`) |
| Lag-augmented LP | Montiel Olea & Plagborg-Møller, Econometrica 2021 | Đã có từ trước (`lp_allpast`) |
| SVAR port của Chang–Guo–Malinsky: nhiễu test statistic trên phần dư VAR, union interval qua các đồ thị giữ lại | Biometrika 2026 | **Nên làm tiếp.** Baseline có nguyên lý nhất, gần nhất |
| Targeted Local Projections: co LP về SVAR (có thể chính là SVAR trên skeleton hỏng), dùng double bootstrap | Nemtyrev & Boldea, arXiv 2603.00248 (2026) | Nên làm. So sánh "like-for-like" |
| IRFC: chọn giữa VAR, LP và mức shrinkage theo risk khi mô hình sai cục bộ | González-Casasús & Schorfheide, arXiv 2502.03693 / NBER w33474 | Tùy chọn. Chỉ cho point estimate |
| Lấy trung bình LP và VAR theo từng horizon | Chen, Pesavento, Vonnák, arXiv 2605.05456 (2026) | Tùy chọn, nhẹ |
| Bagged-PCMCI+: bagging dựa trên dữ liệu, thay cho bagging ngẫu nhiên | Debeire, Gerhardus, Runge, Eyring, CLeaR 2024 | Tùy chọn |

## 4. Theo từng hướng mở rộng

### B1: tự ước lượng mức hỏng từ dữ liệu
- **Eulig và cộng sự**, *Toward Falsifying Causal Graphs Using a Permutation-Based Test*, AAAI 2025 (arXiv 2305.09565). Đếm số CI statement mà đồ thị hàm ý nhưng dữ liệu vi phạm, rồi so với các đồ thị hoán vị nhãn nút. Dễ implement bằng Fisher-z có sẵn.
- **Faltenbacher, Wahl, Herman, Runge**, *How PC-based Methods Err*, UAI 2026 (arXiv 2502.14719). Coherency score; tự nhận chỉ là proxy heuristic cho SHD.
- **Ramsey, Andrews, Spirtes**, *Markov Checker / CAFS*, arXiv 2409.20187 (2024). Kiểm định Markov condition của một DAG cho trước; tiêu chí số cạnh tối thiểu nhắm vào cạnh thừa.
- **Faller và cộng sự**, *Self-Compatibility*, AISTATS 2024 (arXiv 2307.09552). Đồ thị học trên các tập con biến phải khớp nhau.
- **Debeire và cộng sự**, CLeaR 2024. Tần suất cạnh qua bootstrap có giữ cấu trúc thời gian.
- **Công thức đề xuất cho B1:**
  - **Cạnh thiếu:** đếm số reject (BH) trong các CI statement mà skeleton hàm ý, kiểm định trên phần dư VAR. Hiệu chỉnh số đếm theo baseline hoán vị của Eulig, rồi hiệu chỉnh power (kiểu π0).
  - **Cạnh thừa:** Markov checker và tiêu chí tối thiểu cạnh.
  - **Cạnh đảo:** chỉ nhận diện được một phần (qua v-structure và lag). Dùng tần suất chiều qua bootstrap.

### B2: mở rộng xuống T nhỏ
- **Targeted LP** (Nemtyrev & Boldea 2026): co về mô hình có cấu trúc, và double bootstrap tính đến phần lệch do shrinkage. Đây đúng là thứ bản v1 (ridge) thiếu.
- **Ballarin**, *Ridge Regularized Estimation of VAR Models for Inference*, JTSA (arXiv 2105.00860). Lý thuyết giải thích vì sao ridge làm interval under-cover, và cách suy luận có tính đến bias.
- **Herbst & Johannsen**, *Bias in Local Projections*, J. Econometrics 2024. Hiệu chỉnh bias dạng đóng cho LP ở mẫu ngắn.
- **Krampe, Paparoditis, Trenkler**, J. Econometrics 2023; **Adamek, Smeekes, Wilms**, arXiv 2209.03218. Desparsified SVAR/LP, bỏ được giới hạn số biến hồi quy. Nhưng lý thuyết tiệm cận khó đứng ở T = 19.
- **Montiel Olea, Plagborg-Møller, Qian, Wolf**, *Double Robustness of Local Projections*, arXiv 2405.09509. Lý thuyết: LP giữ coverage khi mô hình sai cục bộ; VAR chỉ giữ được nếu đủ lag. Dùng để lập luận rằng hẹp hơn LP mà vẫn đủ coverage thì cần cấu trúc được nhắm đúng.

### B3: thông tin bên ngoài (gắn với ý tưởng tin tức, nghị định của anh Hậu)
- Một proxy (external instrument) hợp lệ chỉ nhận diện được **cột impact của đúng cú sốc nó đại diện**, không nhận diện cả DAG. Proxy yếu hoặc nội sinh làm sai coverage. Keweloh, Klein, Prüser (arXiv 2302.13066) kiểm định tính ngoại sinh của proxy thay vì tin nó.
- **Chuỗi cú sốc từ văn bản / LLM đã có:**
  - Aruoba & Drechsel, *Identifying Monetary Policy Shocks: A Natural Language Approach*, NBER w32417 (2024; AEJ: Macro, forthcoming).
  - Fernández-Fuertes, *Monetary Policy Shocks: A New Hope – LLMs and Central Bank Communication* (job market paper 2025–2026).
  - **Chưa thấy bài nào dùng chuỗi từ LLM làm proxy trong proxy-SVAR có suy luận chính thức.** Đây là một khoảng trống.
- **Định chiều cạnh cùng kỳ bằng tính non-Gaussian:** Cordoni, Dorémus, Moneta, JEDC 2024. Cần T vừa phải trở lên, nên hợp với mô phỏng T = 40–300, không hợp với panel thật.
- **Hochsprung, Runge, Gerhardus**, *Using Time Structure to Estimate Causal Effects*, arXiv 2504.11076 (2025). Dùng cấu trúc lag để nhận diện hiệu ứng trong SVAR **kể cả khi có biến ẩn**. Có thể thành một hướng sửa cho A1.

### A1: biến ẩn và nhiễu đo
- **LPCMCI** (Gerhardus & Runge, NeurIPS 2020) và **SVAR-FCI** (Malinsky & Spirtes 2018): biểu diễn biến ẩn bằng bidirected edge.
- **TCD-Arena** (Stein và cộng sự, ICLR 2026; arXiv 2605.03045): 33 kiểu vi phạm giả định, gồm biến ẩn cùng kỳ hoặc có lag và 7 loại nhiễu quan sát. Có thể mượn cách sinh vi phạm.
- **Forni & Gambetti**, J. Monetary Economics 2014: kiểm định "informational sufficiency" của VAR.
- **Brignone, Franconi, Mazzali**, arXiv 2307.06145: thiếu thông tin và nhiễu đo làm lệch IRF trong proxy-SVAR.

### Prior từ LLM có lỗi
- **Không bài nào nhận tỷ lệ lỗi dạng số làm input.** Các cách được dùng:
  - soft prior cân với độ khớp dữ liệu (Ban và cộng sự, IEEE TAI 2025);
  - kiểm tra nhất quán trên Markov equivalence class (Long và cộng sự 2023, *LMs as Imperfect Experts*);
  - phát hiện lỗi sau khi học, như "quasi-circle" cho prior đảo chiều (Chen, Ban và cộng sự, TPAMI 2025);
  - trust calibration không cần nhãn (CauTion, arXiv 2606.03602).
- **Kumar và cộng sự**, arXiv 2608.23660 (2026): LLM **dự đoán thừa cạnh**, gán nhầm cạnh gián tiếp hoặc ngược chiều thành cạnh trực tiếp, và confidence lấy từ logit không đáng tin. Hàm ý:
  - skeleton từ LLM chủ yếu hỏng kiểu **thừa** và **đảo**;
  - ủng hộ cách tiếp cận khai báo mức hỏng, hoặc ước lượng mức hỏng từ dữ liệu.
- **Vashishtha và cộng sự**, ICLR 2025 (arXiv 2310.15117): nên hỏi LLM về **thứ tự nhân quả** thay vì cạnh. Với SVAR đệ quy, thứ tự cùng kỳ chính là thứ quyết định nhận diện.

## 5. Hệ quả cho kế hoạch

1. **Định vị:** trích dẫn và phân biệt với Chang–Guo–Malinsky, Padh và cộng sự, Strieder–Drton, Giacomini–Kitagawa–Volpicella, Keweloh.
2. **A2:**
   - Đã thêm IDA-style và BVAR Minnesota.
   - Bước tiếp: SVAR port của Chang–Guo–Malinsky và Targeted LP.
3. **B1:** bắt đầu từ kiểm định hoán vị của Eulig cộng với đếm reject BH trên phần dư VAR.
4. **B2:** thử Targeted LP hoặc shrinkage có hiệu chỉnh bias (Ballarin), cộng hiệu chỉnh bias của Herbst–Johannsen.
5. **B3:** proxy cho cú sốc (mô phỏng: proxy = cú sốc + nhiễu) để định chiều cạnh cùng kỳ. Nối với việc LLM trích ngày sự kiện. Cần thầy quyết định thuộc Bài 4 hay Bài 5.
