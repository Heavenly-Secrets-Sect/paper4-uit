# Rà soát phần so sánh chính (phản hồi điểm 6)

Ngày 2026-11-15. Dựa trên `docs/latex/sections/05_ket_qua.tex`, mục "So sánh với các phương pháp tham chiếu khi thiếu cạnh". Đây là rà soát, chưa có thực nghiệm mới.

## Những điểm yếu của phép so sánh hiện tại (đã xác nhận trong bản thảo)

| # | Vấn đề | Bằng chứng trong bài | Hệ quả |
|---|---|---|---|
| 1 | Chỉ có 4 ô (thiếu 20% và 50%, T = 80 và 150) | Bảng `tab:main` | Chưa so sánh ở thừa cạnh, đảo cạnh, T nhỏ (T = 40 chỉ là kết quả thăm dò) |
| 2 | Hệ số hiệu chỉnh của từng phương pháp "(cal)" là phân vị gộp mức cặp, chọn trên bank cũ | mục `Thiết lập` | Mỗi phương pháp đạt một mức coverage khác nhau (0,937 đến 0,988); so sánh IS giữa các mức coverage khác nhau không công bằng hoàn toàn |
| 3 | STRIDE nhận số cạnh thiếu khai báo, các tham chiếu hầu hết không | đoạn "Có ba điều cần lưu ý" | Lợi thế gộp phương pháp và thông tin |
| 4 | PSel-Union (cal) dùng 32 lần số lần bootstrap | đoạn sau `tab:diff` | Ngân sách tính toán không ngang nhau |
| 5 | Một số tham chiếu là bản do nhóm chuyển thể | `Thiết lập` | Chưa phải bản công bố gốc |
| 6 | RB không đạt 0,95 ngay cả khi skeleton đúng | `tab:full` | Một phần cải thiện của STRIDE là do hiệu chỉnh độ rộng |
| 7 | Tiêu chí RQ4.1 sửa sau khi thấy kết quả | cuối mục RQ4.1 | Đã khai báo; vẫn là điểm các thầy sẽ hỏi |
| 8 | Câu "RQ4.2: STRIDE có khoảng hẹp hơn RB" sai hướng | mục `Thảo luận` | Khoảng của STRIDE rộng hơn RB; phải phát biểu theo interval score (bài đã sửa) |

## Đề xuất sửa (xếp theo mức đóng góp)

**A. So sánh ở cùng mức đảm bảo (khắc phục 2).** Hiệu chỉnh *mọi* phương pháp bằng cùng một quy tắc thống kê hạng theo topology trên cùng tập 550 topology hiệu chỉnh của P4-H8 (cùng β = 0,10, δ = 0,10), rồi so độ rộng và interval score ở cùng mức đảm bảo. Khi đó câu hỏi là "phương pháp nào cho khoảng hẹp nhất ở cùng bảo đảm", công bằng hơn nhiều so với so sánh các mức coverage khác nhau. Cần chạy từng phương pháp tham chiếu trên 550 topology hiệu chỉnh và 550 topology kiểm tra: ước lượng 2 đến 3 giờ mỗi lượt lag 1 (chưa đo), vì các tham chiếu chậm hơn STRIDE.

**B. Mở rộng ô (khắc phục 1).** Thêm ô thừa cạnh, đảo cạnh và T = 40; chạy cùng lưới như phần đảm bảo.

**C. Ghi rõ ngân sách và thông tin (khắc phục 3, 4, 5).** Bảng phụ: mỗi phương pháp dùng thông tin khai báo nào, bao nhiêu lần bootstrap, bản gốc hay chuyển thể. Thêm một biến thể STRIDE không dùng số cạnh thiếu khai báo (mở số cặp cố định) để đo riêng phần lợi thế do thông tin.

**D. Nêu rõ hạn chế (khắc phục 6, 7, 8).** Giữ các câu khai báo hiện có; thêm câu nói rõ rằng so sánh là với các tham chiếu đã chọn, không phải mọi phương pháp có thể.

## Quyết định cần thầy cho ý kiến
1. Có chấp nhận hiệu chỉnh mọi tham chiếu theo cùng quy tắc (A) làm phép so sánh chính không?
2. Tập tham chiếu nào bắt buộc: PSel-Union, Full VAR, TLP, BVAR-Minnesota (đã có); DYNOTEARS hoặc PCMCI+ (chưa có bản chạy được; gói tham chiếu của repo gốc tự ghi chưa kiểm chứng)?

## Trạng thái
**Đã chạy (2026-11-15):** so sánh ở cùng mức đảm bảo (đề xuất A) trên 200 topology kiểm tra, lag 1, T = 40 và 150, bốn loại hỏng, sáu phương pháp, hệ số của mọi phương pháp tính bằng cùng quy tắc trên 150 topology hiệu chỉnh (đặc tả `p4h8_cmp_spec.md`, kết quả `results/ext_p4h8_cmp/test_eval.md`).

**Kết quả:** ở cùng mức đảm bảo, STRIDE **không** tốt nhất ở mọi ô. Theo quy tắc ghi trước, số ô thắng (IS thấp nhất trong các phương pháp đạt mức đảm bảo): BVAR-Minnesota 4, STRIDE 3, PSel-Union (ngân sách bootstrap gấp 32) 1, trên 8 ô. STRIDE thắng ở các ô thiếu và đảo cạnh (T = 40 cả hai loại, T = 150 đảo); BVAR-Minnesota thắng ở các ô không hỏng và thừa cạnh; PSel-Union thắng ở T = 150, thiếu cạnh. So cặp với STRIDE: STRIDE tốt hơn PSel, Full VAR, TLP ở 8/8 ô và PSel-Union ở 7/8 ô, nhưng với BVAR-Minnesota thì 4 ô mỗi bên. Điều này điều chỉnh kết luận cũ (27/28 so sánh có lợi cho STRIDE khi mỗi phương pháp dùng hệ số riêng): lợi thế thật nhưng hẹp hơn, và tập trung ở các loại hỏng cần mở cấu trúc.

**Chưa làm:** đề xuất B (thêm lag 2, T khác), biến thể STRIDE không dùng số cạnh thiếu khai báo (đề xuất C).
