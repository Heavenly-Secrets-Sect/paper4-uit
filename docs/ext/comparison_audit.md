# Rà soát phần so sánh chính (phản hồi điểm 6)

Ngày 2026-11-15. Dựa trên `docs/latex/sections/05_ket_qua.tex`, mục "So sánh với các phương pháp tham chiếu khi thiếu cạnh". Đây là rà soát, chưa có thực nghiệm mới.

## Những điểm yếu của phép so sánh hiện tại (đã xác nhận trong bản thảo)

| # | Vấn đề | Bằng chứng trong bài | Hệ quả |
|---|---|---|---|
| 1 | Chỉ có 4 ô (thiếu 20% và 50%, T = 80 và 150) | Bảng `tab:main` | Chưa so sánh ở thừa cạnh, đảo cạnh, T nhỏ (T = 40 chỉ là kết quả thăm dò) |
| 2 | Hệ số hiệu chỉnh của từng phương pháp "(cal)" là phân vị gộp mức cặp, chọn trên bank cũ | mục `Thiết lập` | Mỗi phương pháp đạt một mức coverage khác nhau (0,937 đến 0,988); so sánh IS giữa các mức coverage khác nhau không công bằng hoàn toàn |
| 3 | SRCI nhận số cạnh thiếu khai báo, các tham chiếu hầu hết không | đoạn "Có ba điều cần lưu ý" | Lợi thế gộp phương pháp và thông tin |
| 4 | PSel-Union (cal) dùng 32 lần số lần bootstrap | đoạn sau `tab:diff` | Ngân sách tính toán không ngang nhau |
| 5 | Một số tham chiếu là bản do nhóm chuyển thể | `Thiết lập` | Chưa phải bản công bố gốc |
| 6 | RB không đạt 0,95 ngay cả khi skeleton đúng | `tab:full` | Một phần cải thiện của SRCI là do hiệu chỉnh độ rộng |
| 7 | Tiêu chí RQ4.1 sửa sau khi thấy kết quả | cuối mục RQ4.1 | Đã khai báo; vẫn là điểm các thầy sẽ hỏi |
| 8 | Câu "RQ4.2: SRCI có khoảng hẹp hơn RB" sai hướng | mục `Thảo luận` | Khoảng của SRCI rộng hơn RB; phải phát biểu theo interval score (bài đã sửa) |

## Đề xuất sửa (xếp theo mức đóng góp)

**A. So sánh ở cùng mức đảm bảo (khắc phục 2).** Hiệu chỉnh *mọi* phương pháp bằng cùng một quy tắc thống kê hạng theo topology trên cùng tập 550 topology hiệu chỉnh của P4-H8 (cùng β = 0,10, δ = 0,10), rồi so độ rộng và interval score ở cùng mức đảm bảo. Khi đó câu hỏi là "phương pháp nào cho khoảng hẹp nhất ở cùng bảo đảm", công bằng hơn nhiều so với so sánh các mức coverage khác nhau. Cần chạy từng phương pháp tham chiếu trên 550 topology hiệu chỉnh và 550 topology kiểm tra: ước lượng 2 đến 3 giờ mỗi lượt lag 1 (chưa đo), vì các tham chiếu chậm hơn SRCI.

**B. Mở rộng ô (khắc phục 1).** Thêm ô thừa cạnh, đảo cạnh và T = 40; chạy cùng lưới như phần đảm bảo.

**C. Ghi rõ ngân sách và thông tin (khắc phục 3, 4, 5).** Bảng phụ: mỗi phương pháp dùng thông tin khai báo nào, bao nhiêu lần bootstrap, bản gốc hay chuyển thể. Thêm một biến thể SRCI không dùng số cạnh thiếu khai báo (mở số cặp cố định) để đo riêng phần lợi thế do thông tin.

**D. Nêu rõ hạn chế (khắc phục 6, 7, 8).** Giữ các câu khai báo hiện có; thêm câu nói rõ rằng so sánh là với các tham chiếu đã chọn, không phải mọi phương pháp có thể.

## Quyết định cần thầy cho ý kiến
1. Có chấp nhận hiệu chỉnh mọi tham chiếu theo cùng quy tắc (A) làm phép so sánh chính không?
2. Tập tham chiếu nào bắt buộc: PSel-Union, Full VAR, TLP, BVAR-Minnesota (đã có); DYNOTEARS hoặc PCMCI+ (chưa có bản chạy được; gói tham chiếu của repo gốc tự ghi chưa kiểm chứng)?

## Trạng thái
Chưa chạy. Chạy A và B cần một đặc tả ghi trước với hash, và dùng cùng hai split hiệu chỉnh và kiểm tra của P4-H8 (phương pháp tham chiếu không được chỉnh trên split kiểm tra).
