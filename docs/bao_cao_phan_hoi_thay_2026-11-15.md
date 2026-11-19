# Báo cáo xử lý phản hồi của các thầy (buổi họp 13/11/2026)

Ngày 15/11/2026. Mục đích: để các thầy xem xét **trước khi viết bài**. Kết quả thực nghiệm là **thăm dò (exploratory)** trừ phần ghi rõ "xác nhận" ở mục 2, đã chạy một lần trên tập topology kiểm tra chưa dùng, theo đặc tả và tiêu chí ghi trước.

Tên phương pháp trong báo cáo: **STRIDE** (Skeleton-Tolerant Re-selecting Intervals for Dynamic Effects), kèm hiệu chỉnh độ rộng ở mức topology. Tên cũ trong các tài liệu đã đóng băng là STRIDE.

## 1. Tóm tắt trạng thái

| # | Phản hồi | Trạng thái |
|---|---|---|
| 1 | Áp dụng dữ liệu thực tế (Việt Nam) | **Làm một phần:** đã chạy trên panel hiện có (minh họa) và mô phỏng theo panel có ground truth; thu số liệu ngân hàng thật không khả thi qua nguồn công khai (xem mục 8) |
| 2 | Điều kiện đủ để coverage đúng | **Đã có phát biểu, bản nháp chứng minh và kiểm chứng độc lập trên 1.200 topology, lag 1–3: đạt ở lag 1 và 3, không đạt ở lag 2** |
| 3 | Hệ số 0,5 | **Xong (thăm dò):** giải thích và kiểm độ nhạy |
| 4 | Mở rộng mô phỏng | **Xong phần chính:** tập 1.200 topology, lag 1–3, nhiễu đuôi dày (t4, Laplace) ở lag 1; chưa thêm số nút khác 14 |
| 5 | AUROC của RQ4.4 | **Đã làm: tiêu chí đạt ở lag 3, không đạt ở lag 1 và 2** (T = 40 chỉ hơn cờ cũ +0,015 và +0,028); xem mục 12 |
| 6 | Rà phần so sánh chính | **Đã chạy so sánh ở cùng mức đảm bảo:** STRIDE thắng 3/8 ô, BVAR-Minnesota 4/8, PSel-Union 1/8 (xem mục 11) |
| 7 | Vẽ architecture | **Xong** (hình đính kèm) |
| 8 | Giải thích số liệu trong bảng | **Có bản nháp** (`docs/latex/draft_giai_thich_bang.md`), chưa chèn vào bài |
| 9 | Tài liệu từ 2021 | **Xong phần tìm và kiểm chứng:** 79 mục; chưa đưa vào bài |
| 10 | Ablation theo T và mức hỏng | **Xong (thăm dò)** |

## 2. Điểm 2: điều kiện đủ cho coverage

**Vấn đề với cách làm hiện tại.** Hệ số nới độ rộng trước đây là phân vị gộp mức cặp, tính trên khoảng 20 topology. Nó bảo đảm độ phủ *trung bình* quanh 0,95, không bảo đảm gì cho từng topology. Kiểm tra trên 20 topology cũ cho thấy hệ số đó xấp xỉ **trung vị** của điểm theo đơn vị.

**Phát biểu mới.** Mỗi topology là một đơn vị. Điểm của đơn vị là hệ số nhỏ nhất làm cho không quá β = 10% cặp phi-null bị trượt (lấy max theo hai mức hỏng). Hệ số hiệu chỉnh là thống kê hạng của các điểm này trên N topology hiệu chỉnh:

- *Phiên bản biên:* k0 = ⌈(N+1)(1−δ)⌉ với δ = 0,10. Khi các topology hiệu chỉnh và kiểm tra hoán vị được, xác suất điểm của một topology mới không vượt hệ số này là ít nhất k0/(N+1).
- *Phiên bản PAC:* chọn k0 nhỏ nhất sao cho phân phối Beta(k0, N+1−k0) tại 0,90 không quá 0,05, tức độ tin cậy 0,95 (theo mẫu hiệu chỉnh) rằng ít nhất 90% topology mới thỏa điều kiện. Cần N ≥ 59.

**Điều kiện hoán vị** được bảo đảm bằng cách xây bank: 1.200 topology rút độc lập từ cùng một bộ sinh, chia ngẫu nhiên thành thiết kế (100), hiệu chỉnh (550) và kiểm tra (550); một tập thí điểm 360 topology (60/150/150) đã được dùng để chọn quy tắc và script, phần kiểm tra của tập thí điểm vẫn chưa mở. Ở các bank cũ, hai tập hiệu chỉnh và kiểm tra là các tập cố định, không có cơ sở này.

**Giới hạn cần nói thẳng.** Mệnh đề chỉ nói về topology mới *cùng họ bộ sinh*, trong kịch bản sạch, hỏng một loại, khai báo đúng. Không nói gì về cặp riêng lẻ, về dữ liệu thật, về nhiễu đuôi dày hay khai báo sai. Bản nháp chứng minh do một nhóm phản biện nội bộ soạn, chưa có thẩm định ngoài.

**Kết quả xác nhận** (tập 1.200 topology: 550 để hiệu chỉnh, 550 để kiểm tra; chạy một lần, hệ số đã đóng băng, tiêu chí ghi trước). Mức bảo đảm đo bằng tỉ lệ topology có không quá 10% cặp phi-null bị trượt (mục tiêu 0,90):

| Lag | Ô có hệ số hữu hạn | Tỉ lệ topology thỏa điều kiện: luật cũ / phân vị biên / PAC | Ô đạt tiêu chí (khoảng tin cậy chạm 0,90) | Kết luận |
|---|---|---|---|---|
| 1 | 20/20 | 0,805 / 0,897 / 0,918 | 17/20 (85%) | **Đạt** (cần 80%) |
| 2 | 12/16 | 0,805 / 0,890 / 0,912 | 9/12 (75%) | **Không đạt** (cần 80%) |
| 3 | 8/12 | 0,801 / 0,888 / 0,906 | 8/8 | **Đạt** |

Cái giá so với luật cũ (cùng các ô có hệ số hữu hạn): khoảng rộng hơn ×1,18 / ×1,14 / ×1,10 và interval score cao hơn 11% / 6% / 3% (lag 1 / 2 / 3, với hệ số biên). PAC rộng hơn khoảng 5% so với hệ số biên.

Cần nói thẳng:
- **Lag 2 không đạt tiêu chí đã ghi trước** (75% so với 80%). Theo đặc tả, tuyên bố đảm bảo bị rút ở ba ô không đạt: T = 80 thừa cạnh, T = 80 đảo cạnh, T = 150 đảo cạnh. Cận trên nhỏ nhất vẫn là 0,880.
- **Vùng phương pháp từ chối đưa ra đảm bảo (abstain)**: lag 2 với T = 30 và lag 3 với T = 40, vì ở đó 9% đến 92% lượt fit thất bại. Ở chính các ô đó, luật cũ vẫn trả về khoảng tin cậy nhưng chỉ 7% đến 76% topology đạt điều kiện (ví dụ lag 3, T = 40, thiếu cạnh: 7%). Nghĩa là hệ số mới đồng thời là một cờ độ tin cậy: nó cho biết lúc nào không nên tin khoảng.
- Với các ô đạt, tỉ lệ thỏa điều kiện khoảng 0,89 đến 0,90, đúng mức mục tiêu chứ không dư; sai số lấy mẫu của 550 topology khoảng ±0,025.
- Tập topology vẫn từ một bộ sinh, 14 nút, 21 cạnh, nhiễu Gaussian sạch; không nói gì về dữ liệu thật, nhiễu đuôi dày hay khai báo sai.

## 3. Điểm 3: hệ số 0,5

Hệ số 0,5 nhân vào nửa độ rộng *trước* bước hiệu chỉnh; lưới hiệu chỉnh cũ chỉ cho phép nới (từ 1,0), mà ở T nhỏ khoảng bootstrap đã quá rộng. Không có lý thuyết nào dẫn tới đúng giá trị 0,5. Nếu cố định và áp giống nhau ở hiệu chỉnh và kiểm tra, khoảng cuối cùng chỉ phụ thuộc tích 0,5·c, nên bảo đảm ở mục 2 không bị ảnh hưởng.

Kiểm độ nhạy (hiệu chỉnh trên split hiệu chỉnh, đánh giá trên split thiết kế):

| Tiền co κ | Hệ số hiệu dụng | Sàn lưới chạm | Coverage | Interval score |
|---|---|---|---|---|
| 0,25 | 1,424 | 0/20 | 0,951 | 5,24 |
| 0,5 | 1,435 | 0/20 | 0,952 | 5,26 |
| 1,0 | 1,460 | 0/20 | 0,955 | 5,33 |
| 2,0 | 2,000 | 20/20 | 0,988 | 6,55 |

Kết luận: với κ từ 0,25 đến 1,0 kết quả gần như trùng nhau (khác biệt là do làm tròn lưới); κ = 2 làm lưới chạm sàn nên khoảng quá rộng. Vậy 0,5 không quan trọng miễn là không chạm sàn lưới. **Đề xuất:** bỏ hằng số này, dùng hệ số là thống kê hạng chính xác (không qua lưới) ở mục 2.

## 4. Điểm 10: T nhỏ nhất và mức hỏng mà phương pháp còn chạy được

**Kết quả xác nhận về T tối thiểu theo số lag** (tập 1.200 topology, xem mục 2): phương pháp có hệ số bảo đảm hữu hạn từ **T = 19 ở lag 1, T = 40 ở lag 2, T = 80 ở lag 3**. Dưới các ngưỡng đó (lag 2 với T = 30, lag 3 với T = 40) tỉ lệ fit thất bại từ 9% đến 92% và phương pháp từ chối đưa ra đảm bảo. T tối thiểu tăng theo số lag, khớp với bản đồ thăm dò đã có (19, 40, 80 cho lag 1, 2, 4).

Phần quét theo mức hỏng dưới đây chỉ chạy ở lag 1 trên tập thí điểm 360 topology (split thiết kế):

Quét trên split thiết kế (60 topology; T ∈ {19, 30, 40, 80, 150}; mức hỏng 0,1 đến 0,8; ba loại hỏng; n = 14, 21 cạnh, lag 1). Quy tắc ghi trước: một ô *dùng được* nếu fit thành công ≥ 95% và coverage cặp phi-null tại hệ số hiệu chỉnh ≥ 0,90.

- **Thiếu cạnh:** dùng được ở mọi T tested, kể cả T = 19 và mức hỏng 0,8.
- **Thừa cạnh:** dùng được ở T ≥ 30 với mọi mức đến 0,8. Ở T = 19, thất bại từ mức 0,7 (tỉ lệ fit thành công 0,92 rồi 0,87).
- **Đảo chiều:** dùng được ở T ≥ 30 với mọi mức đến 0,8. Ở T = 19, thất bại từ mức 0,5 (tỉ lệ thành công 0,92 đến 0,88).

Hạn chế: "thành công" chỉ là bước fit hoàn tất; coverage chỉ tính trên các lần fit thành công; chưa đánh giá interval score so với oracle; coverage cao (0,96 đến 0,99) là hệ quả của hệ số bảo thủ mức topology. Một đơn vị có số cạnh đảo bằng 0 ở mức hỏng thấp bị xếp vào ô "không hỏng" và đã được loại khỏi tính tỉ lệ thành công. Dữ liệu từ nhánh phát triển khác của nhóm (khai báo sai mức hỏng) cho thấy khai báo gấp đôi số cạnh thiếu ở mức 50% làm chỉ 5 đến 11 trong 60 lượt chạy được; kết quả này đã được tái lập một phần và chưa nằm trong bài này.

## 5. Điểm 7: sơ đồ phương pháp

![Sơ đồ phương pháp STRIDE](latex/figures/architecture_srci.png){width=100%}

Hình: `docs/latex/figures/architecture_srci.png` (và .pdf). Gồm đầu vào, 6 bước (chấm bằng chứng, mở lag có chọn lọc, bổ sung cạnh cùng kỳ bằng Benjamini–Hochberg, đảo chiều có chọn lọc, bootstrap có chọn lại cấu trúc, hiệu chỉnh độ rộng) và đầu ra, kèm luật chuyển nhánh theo tỉ số hàng trên số biến hồi quy.

## 6. Điểm 4: mô phỏng

Đã có bộ sinh tập topology tham số hóa và hai tập mới (360 và 1.200 topology; trước đây là 40). Đã chạy lag 1, 2, 3 (mục 2).

**Nhiễu đuôi dày** (thăm dò, tập kiểm tra, lag 1, cùng hệ số đóng băng, nhiễu đổi sang Student-t 4 bậc tự do hoặc Laplace, phương sai bằng 1; đây là vi phạm giả thiết "Gaussian sạch", không thuộc bảo đảm):

| Nhiễu | Tỉ lệ topology thỏa điều kiện: luật cũ / phân vị biên / PAC | Ô đạt tiêu chí | Độ rộng trung bình (biên) |
|---|---|---|---|
| Gaussian (xác nhận) | 0,805 / 0,897 / 0,918 | 17/20 | 4,86 |
| Student-t(4) | 0,824 / 0,909 / 0,927 | 18/20 | 5,25 |
| Laplace | 0,812 / 0,901 / 0,921 | 17/20 | 6,29 |

Hệ số hiệu chỉnh trên Gaussian vẫn giữ tỉ lệ thỏa điều kiện ở mức 0,90 khi nhiễu động học đổi (khoảng rộng hơn một chút, Laplace rộng hơn 29%).

**Sai số đo (nhiễu cộng thêm lên dữ liệu quan sát, phương sai bằng 10% và 30% phương sai của mỗi cột)** thì khác hẳn, và đây là một hạn chế thật:

| Sai số đo | Tỉ lệ thỏa điều kiện: luật cũ / biên / PAC | Ô thấp nhất đến cao nhất (biên) | Coverage cặp (biên) |
|---|---|---|---|
| Không | 0,805 / 0,897 / 0,918 | 0,86 đến 0,93 | 0,971 |
| 10% | 0,642 / 0,776 / 0,810 | 0,53 đến 0,93 | 0,948 |
| 30% | 0,363 / 0,501 / 0,544 | 0,03 đến 0,88 | 0,878 |

Bảo đảm **không chịu được sai số đo**, và tệ hơn khi T lớn (ở 10% nhiễu, T = 150 chỉ còn 0,53 đến 0,59), vì sai lệch do sai số đo không giảm khi có thêm dữ liệu. Điều này nhất quán với các thử nghiệm sơ bộ của nhóm khác (coverage tụt xuống 0,66 đến 0,75). Bài cần nói rõ giới hạn này; hướng khắc phục (ví dụ ước lượng tỉ lệ nhiễu đo rồi nới khoảng, như nhánh adapt của repo gốc) chưa được đánh giá đầy đủ và không được đưa vào. Cần thầy cho ý kiến: có thêm tập topology với số nút khác 14 không.

## 7. Điểm 9: tài liệu từ 2021

79 mục đã kiểm chứng (69 từ 2021 trở đi): conformal (17), IRF và SVAR (18), suy luận sau chọn mô hình hoặc khi đồ thị sai (10), học cấu trúc chuỗi thời gian (10), FDR (9), interval score (5), VAR dữ liệu Việt Nam (7), sai số đo (3). Hai chủ đề còn mỏng: sai số đo trong mô hình nhân quả chuỗi thời gian, và nghiên cứu về Việt Nam. Kiểm chứng chủ yếu qua Crossref; chưa đọc từng bài. File: `docs/latex/references_2021.bib`.

## 8. Điểm 1: dữ liệu thực tế

**Thu số liệu thật qua nguồn công khai: không khả thi với công sức hợp lý.** Một thăm dò nhỏ (3 ngân hàng × 2 quý) chỉ mở được 1 trong 6 tài liệu: báo cáo ACB 2024Q3 là ảnh scan phải OCR (số đọc khá tốt, nhãn bị méo); MBB chặn truy cập bằng cơ chế chống bot; trang nhà đầu tư của VCB tải danh sách bằng JavaScript nên không có đường dẫn. Ước lượng thu đủ 14 ngân hàng × 19 quý là 80 đến 150 giờ (từ một tài liệu, chưa đo), tự động hóa tối đa khoảng 30%; điều khoản sử dụng chưa kiểm chứng. Vì vậy phần ngân hàng của panel vẫn là dữ liệu mô phỏng hiệu chỉnh (7 biến), và bài phải nói rõ điều đó. Nếu trường có cơ sở dữ liệu tài chính trả phí, xuất một lần có thể thay thế.

**Đã chạy trên panel hiện có** (14 biến, 19 quý, skeleton 21 cạnh, hệ số mới, 5 seed bootstrap, 3 mức khai báo): khoảng tin cậy của **cả 10 cặp quan tâm chọn trước**, ở mọi mức khai báo và mọi seed, đều chứa 0. Nhóm cặp giữa hai biến quan sát (lãi suất chính sách đến lợi suất cổ phiếu, GDP, CPI; CPI đến khối lượng giao dịch) là dữ liệu thật; nhóm có biến ngân hàng chỉ minh họa. Khoảng rộng ra khi khai báo nhiều cạnh thiếu hơn (ví dụ lãi suất chính sách → lợi suất cổ phiếu: rộng 0,92 khi không hỏng, 4,4 khi thiếu 20%, 7,3 khi thiếu 50%). Đọc đúng: 19 quý quá ngắn để kết luận dấu của hiệu ứng nào; phương pháp phản ánh đúng mức bất định đó, chứ không tạo ra kết quả có ý nghĩa kinh tế.

**Mô phỏng theo panel có ground truth** (mô hình động fit lên panel làm ground truth, 400 lần sinh chuỗi T = 19, n = 14, thiếu 0, 20%, 50% cạnh):

| Khai báo | Phương pháp | Coverage cặp phi-null | Tỉ lệ lần sinh có ≤10% cặp trượt | Độ rộng trung vị | Fit thành công |
|---|---|---|---|---|---|
| Không hỏng | RB cắm skeleton | 0,904 | 0,620 | 1,87 | 400/400 |
| Không hỏng | STRIDE | 0,990 | 0,990 | 3,64 | 400/400 |
| Thiếu 20% | RB cắm skeleton | 0,663 | 0,000 | 1,70 | 400/400 |
| Thiếu 20% | STRIDE | 0,981 | 0,959 | 5,09 | 390/400 |
| Thiếu 50% | RB cắm skeleton | 0,291 | 0,000 | 1,45 | 400/400 |
| Thiếu 50% | STRIDE | 0,993 | 0,978 | 13,94 | 359/400 |

STRIDE giữ coverage rất cao (0,98 đến 0,99) trong khi RB tụt xuống 0,29 khi thiếu 50% cạnh. **Hạn chế quan trọng:** khi thiếu cạnh, một số lần sinh cho khoảng rộng đột biến (độ rộng trung bình lên tới vài trăm đến vài nghìn, trong khi trung vị là 5 đến 14) và 10% lần fit thất bại ở mức thiếu 50%. Ở T = 19 với 11 cạnh thiếu, bài toán gần vô định; các thầy cần biết điều này khi đọc phần ứng dụng. Đây là mô hình từ một ground truth duy nhất, không phải bảo đảm theo topology, và panel gốc có 7 biến mô phỏng.

**Phương án bán mô phỏng neo vào số thật** mà tôi đã đề xuất chưa được xây; mô phỏng theo panel ở trên là phiên bản đơn giản hơn, và phần ngân hàng vẫn phải được khai báo.

## 9. Cấu trúc bài đề xuất

Giới thiệu; Công trình liên quan; Bài toán; Phương pháp (hình architecture); Bảo đảm lý thuyết; Thiết lập mô phỏng; **Kết quả chính** (so sánh, tác động mức hỏng, ablation); **Case study** (dữ liệu thật); Thảo luận; Kết luận. Khảo sát khoảng 80 bài ở Computational Statistics (qua bản arXiv) cho thấy mẫu phổ biến nhất là mô phỏng chiếm phần chính, kèm một section ứng dụng dữ liệu thật ngắn; chưa thấy bài SVAR nào ở tạp chí này, nên mức phù hợp phạm vi cần thầy xác nhận.

## 10. Việc cần thầy cho ý kiến

1. Mức bảo đảm mong muốn: phiên bản biên (khoảng rộng hơn 24%) hay PAC (rộng hơn 40%)?
2. Dữ liệu ngân hàng: có nên đầu tư thu số liệu thật (60 đến 90 giờ), hay chấp nhận bán mô phỏng có khai báo rõ?
3. Có mở rộng bank sang kích thước khác (số nút, số cạnh) không?
4. Tên phương pháp và thứ tự các section.
5. Phù hợp phạm vi Computational Statistics vì chưa thấy bài SVAR cùng tạp chí.

## 11. Điểm 6: so sánh với các phương pháp tham chiếu ở cùng mức đảm bảo

Mỗi phương pháp được hiệu chỉnh bằng **cùng một quy tắc** (thống kê hạng theo topology, β = 10%, δ = 10%) trên cùng 150 topology hiệu chỉnh, rồi chạy một lần trên 200 topology kiểm tra (lag 1, T = 40 và 150, bốn loại hỏng). Khi đó các phương pháp đạt cùng mức đảm bảo (tỉ lệ topology thỏa điều kiện quanh 0,90) và so sánh được bằng độ rộng và interval score.

| Phương pháp | Số ô (trên 8) có IS thấp nhất | So cặp với STRIDE (8 ô): STRIDE tốt hơn / phương pháp đó tốt hơn |
|---|---|---|
| BVAR-Minnesota | 4 | 4 / 4 |
| STRIDE | 3 | , |
| PSel-Union (ngân sách bootstrap gấp 32) | 1 | 7 / 1 |
| PSel, Full VAR, TLP | 0 | 8 / 0 mỗi phương pháp |

Đọc đúng: STRIDE thắng ở các ô thiếu cạnh và đảo cạnh (T = 40 cả hai loại, T = 150 đảo cạnh); BVAR-Minnesota thắng ở các ô không hỏng và thừa cạnh ở cả hai T; PSel-Union thắng ở T = 150 thiếu cạnh với ngân sách tính toán gấp 32 lần. Hai phương pháp không đạt mức đảm bảo ở một ô (BVAR-Minnesota ở T = 150 thiếu cạnh: 0,84; PSel-Union ở T = 150 đảo cạnh: 0,81). **Điều này làm yếu kết luận cũ** (STRIDE tốt hơn ở 27/28 so sánh khi mỗi phương pháp dùng hệ số riêng): ở cùng mức đảm bảo, lợi thế của STRIDE có thật nhưng hẹp hơn và tập trung ở các loại hỏng cần mở cấu trúc. Hạn chế: chỉ lag 1, hai giá trị T, 200 topology kiểm tra (khoảng tin cậy của tỉ lệ khoảng ±0,04); một số phương pháp là bản do nhóm chuyển thể; STRIDE dùng số cạnh thiếu khai báo.

## 12. Điểm 5: cờ độ tin cậy

Cờ (phiên bản 1) là mô hình gradient boosting với các đặc trưng quan sát được (độ rộng, tỉ lệ |trung điểm| trên nửa độ rộng, khoảng có chứa 0 hay không, khai báo hỏng, đường đi trong skeleton khai báo, độ rộng trung vị theo hàng và cột, thứ hạng độ rộng trong lượt chạy, tỉ lệ số dòng trên số biến hồi quy...). Huấn luyện chỉ trên split hiệu chỉnh (kiểm định chéo theo topology), đóng băng trước khi chạy split kiểm tra (592.412 cặp).

| Nhóm T | AUROC cờ mới | AUROC cờ cũ | Hiệu [khoảng tin cậy 95%] | Cặp trượt nhiều gấp (top 10%) |
|---|---|---|---|---|
| Tất cả | 0,869 | 0,792 | +0,077 [+0,065; +0,088] | 5,74 |
| 19–30 | 0,928 | 0,821 | +0,107 [+0,082; +0,134] | 7,33 |
| 40 | 0,882 | 0,868 | +0,014 [+0,010; +0,018] | 6,13 |
| 80–150 | 0,776 | 0,744 | +0,032 [+0,026; +0,038] | 3,96 |

Tiêu chí ghi trước (tăng ít nhất 0,03 AUROC ở **cả ba** nhóm T với khoảng tin cậy trên 0) **không đạt** vì nhóm T = 40 chỉ tăng 0,014, do cờ cũ ở đó vốn đã mạnh (0,868). Cải thiện rõ ở T nhỏ và vừa phải ở T lớn, nơi AUROC vẫn chỉ 0,78.

**Phiên bản 2** (sửa hai lỗi đặc trưng ở phiên bản 1: số cạnh khai báo bị ghi bằng 0, và skeleton chỉ tính cạnh cùng kỳ; một mô hình cho cả lag 1, 2, 3; đặc tả viết trước khi đọc dữ liệu; chấm trên tập chưa dùng cho cờ, một lần cho mỗi lag). AUROC cờ mới / cờ cũ theo nhóm T:

| Lag | T 19–30 | T 40 | T 80–150 | Tiêu chí (mỗi nhóm T hơn ít nhất 0,03) |
|---|---|---|---|---|
| 1 | 0,924 / 0,808 (+0,115) | 0,885 / 0,870 (+0,015) | 0,786 / 0,737 (+0,049) | **Không đạt** (T = 40) |
| 2 | không có (từ chối) | 0,894 / 0,865 (+0,028) | 0,790 / 0,737 (+0,053) | **Không đạt** (T = 40, thiếu 0,002) |
| 3 | không có (từ chối) | không có (từ chối) | 0,790 / 0,731 (+0,059) | **Đạt** |

Tiêu chí không đạt ở lag 1 và lag 2, đạt ở lag 3. Cờ mới hơn cờ cũ ở mọi nhóm T với khoảng tin cậy trên 0, nhưng mức hơn ở T = 40 nhỏ (cờ cũ ở đó đã 0,87). Sửa hai lỗi đặc trưng **không đổi kết luận** của phiên bản 1.

AUROC theo kịch bản (lag 1; cờ mới / cờ cũ; "thấp" và "cao" là mức hỏng 0,2 và 0,5):

| T | Không hỏng | Thừa cạnh thấp / cao | Thiếu cạnh thấp / cao | Đảo cạnh thấp / cao |
|---|---|---|---|---|
| 19 | 0,932 / 0,918 | 0,943 / 0,938; 0,940 / 0,921 | 0,915 / 0,840; **0,954 / 0,530** | **0,981 / 0,477**; 0,966 / 0,667 |
| 30 | 0,894 / 0,878 | 0,888 / 0,872; 0,889 / 0,875 | 0,875 / 0,861; 0,856 / 0,848 | 0,907 / 0,897; 0,912 / 0,901 |
| 40 | 0,892 / 0,875 | 0,869 / 0,854; 0,907 / 0,881 | 0,868 / 0,852; 0,859 / 0,858 | 0,889 / 0,872; 0,910 / 0,892 |
| 80 | 0,808 / 0,771 | 0,828 / 0,798; 0,840 / 0,803 | 0,796 / 0,775; 0,781 / 0,772 | 0,877 / 0,841; 0,865 / 0,839 |
| 150 | 0,660 / 0,609 | 0,696 / 0,631; 0,696 / 0,635 | 0,686 / 0,661; 0,702 / 0,671 | 0,796 / 0,759; 0,815 / 0,773 |

Điều đọc được: (1) AUROC giảm mạnh khi T lớn, từ khoảng 0,93 ở T = 19 xuống 0,66 đến 0,70 ở T = 150 khi không hỏng, vì khi T lớn ít cặp bị trượt hơn và các cặp trượt giống các cặp chứa hơn; (2) cờ cũ gần như vô dụng ở T = 19 khi thiếu hoặc đảo cạnh (0,48 đến 0,67) còn cờ mới đạt 0,92 đến 0,98; (3) AUROC gần như không phụ thuộc mức hỏng (thấp so với cao); (4) lag 2 và 3 có xu hướng tương tự (xem `results/ext_p4h8_flag_v2/test_eval_v2.md`). Bảng này loại các ô mà phương pháp từ chối đưa ra đảm bảo (lag 2 với T = 30, lag 3 với T = 40), vì ở đó không có khoảng cuối để chấm.
