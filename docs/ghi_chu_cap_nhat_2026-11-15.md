# Ghi chú cập nhật: từng phản hồi của các thầy đã được xử lý như thế nào

Ngày 15/11/2026. File này đi kèm báo cáo `bao_cao_phan_hoi_thay_2026-11-15.pdf` và bản thảo LaTeX `latex/main.pdf`. Mục đích: bạn xác nhận (1) hiểu đúng phản hồi chưa, (2) hướng đi đúng chưa.

## A. Danh sách phản hồi, cách hiểu và hướng đi

| # | Phản hồi của các thầy | Tôi hiểu là | Hướng đi đã chọn | Trạng thái | Bạn cần xác nhận |
|---|---|---|---|---|---|
| 1 | Áp dụng dữ liệu thực tế (thị trường Việt Nam), ra kết quả thực tế | Chạy phương pháp trên dữ liệu thật để thấy tính thực tiễn; là một section riêng (case study), tách khỏi mô phỏng | Chạy trên panel 14 biến × 19 quý hiện có (chỉ minh họa, không báo coverage); thêm mô phỏng theo panel có ground truth. Thu số liệu ngân hàng thật không khả thi | Làm một phần | Có chấp nhận phần ngân hàng của panel là mô phỏng (khai báo rõ) không? Có nguồn dữ liệu trả phí không? |
| 2 | Chứng minh điều kiện đủ để coverage đúng | Có một phát biểu hữu hạn mẫu, kèm điều kiện, về việc khoảng tin cậy phủ đúng | Phát biểu theo conformal ở mức topology: hệ số nới độ rộng là thống kê hạng trên các topology hiệu chỉnh | Có phát biểu và xác nhận độc lập (lag 1, 3 đạt; lag 2 không đạt) | Mức bảo đảm "ít nhất 90% topology có không quá 10% cặp trượt" có đúng ý các thầy không? Bản chứng minh chưa được thẩm định ngoài |
| 3 | Chứng minh hệ số 0,5 | Giải thích vì sao có hằng số này | Không có lý thuyết; kiểm độ nhạy và đề xuất bỏ hằng số | Xong | Có đồng ý bỏ hằng số? |
| 4 | Mở rộng mô phỏng (cấu hình phân phối Gaussian, tăng số topology) | Nhiều topology hơn, đa dạng nhiễu và lag hơn | Tập 1.200 topology (trước đây 40), lag 1–3, nhiễu t4/Laplace, sai số đo | Xong, trừ số nút khác 14 | Có cần số nút khác 14 không? |
| 5 | Cải thiện AUROC ở RQ4.4 | Cờ độ tin cậy phân biệt cặp nào sẽ bị trượt tốt hơn | Mô hình mới với đặc trưng quan sát được | Tiêu chí không đạt (+0,014 ở T = 40); phát hiện hai lỗi đặc trưng; **đang chạy lại phiên bản 2** | Định nghĩa "cặp bị trượt" làm nhãn có hợp lý không? |
| 6 | Xem kỹ phần so sánh trong kết quả chính | Phép so sánh với baseline phải công bằng | Hiệu chỉnh mọi phương pháp bằng cùng quy tắc ở cùng mức đảm bảo | Đã chạy (lag 1, T = 40 và 150) | Tập baseline bắt buộc gồm những gì? |
| 7 | Vẽ architecture | Sơ đồ khối của phương pháp | Hình 6 bước, đầu vào và đầu ra | Xong | Hình có đúng ý? |
| 8 | Giải thích số liệu trong các bảng kết quả | Mỗi bảng có đoạn "cách đọc" | Đã chèn vào LaTeX cho 6 bảng, thêm 2 bảng cho RQ4.3 và RQ4.4 | Xong | , |
| 9 | Tìm tài liệu từ 2021 trở đi | Cập nhật và mở rộng danh mục tham khảo | 79 mục đã kiểm chứng; đã nối vào LaTeX và thêm hai đoạn Công trình liên quan | Xong | , |
| 10 | Ablation: tìm T hoặc mức hỏng mà module chạy được | Ngưỡng dùng được theo T, lag và mức hỏng | Quét T, lag, mức hỏng 0,1–0,8 | Xong (thăm dò + xác nhận theo lag) | , |

Cấu trúc bài đề xuất: Giới thiệu; Công trình liên quan; Bài toán; Phương pháp; Bảo đảm lý thuyết; Thiết lập mô phỏng; **Kết quả chính**; **Case study**; Thảo luận; Kết luận. Mô phỏng là phần chính, ứng dụng dữ liệu thật là một section riêng.

## B. Điều đã thay đổi trong bài LaTeX (`latex/`)

| File | Thay đổi |
|---|---|
| `main.tex` | Tên phương pháp đổi thành **SRCI** (macro `\ours`); `.bib` nối thêm `references_2021` |
| `references.bib` | Sửa 2 mục lỗi thời (`montiel2024double` đã đăng ở Econometrica; `ballarin2021ridge`) |
| `references_2021.bib` (mới) | 79 mục đã kiểm chứng, 69 từ 2021 trở đi |
| `sections/01_gioi_thieu.tex` | Thêm 2 đoạn Công trình liên quan: conformal và bảo đảm hữu hạn mẫu; bootstrap cho IRF |
| `sections/05_ket_qua.tex` | Thêm 6 đoạn "cách đọc bảng" và 2 bảng mới (RQ4.3, RQ4.4) |
| `figures/architecture_srci.png` | Hình sơ đồ phương pháp (chưa chèn vào bài) |

**Chưa được cập nhật trong bài (quan trọng):** các section Kết quả vẫn mô tả kết quả cũ. Chưa có section về bảo đảm coverage, về tập topology 1.200 và lag 1–3, về so sánh ở cùng mức đảm bảo, về cờ mới, về nhiễu đo, và về case study. Lý do: chờ các thầy xem xét trước khi viết lại.

## C. Hai kết quả làm yếu kết luận cũ

1. **Nhiễu đo làm hỏng bảo đảm:** tỉ lệ topology thỏa điều kiện còn 0,776 (nhiễu 10%) và 0,501 (nhiễu 30%), tệ hơn khi T lớn.
2. **So sánh ở cùng mức đảm bảo:** SRCI thắng 3/8 ô, BVAR-Minnesota 4/8, PSel-Union 1/8. Kết luận cũ "27/28 so sánh có lợi cho SRCI" dùng hệ số riêng cho từng phương pháp nên không còn là kết luận chính.

Ngoài ra lag 2 không đạt tiêu chí (9/12 ô, cần 80%); phương pháp từ chối đưa ra đảm bảo ở lag 2 với T = 30 và lag 3 với T = 40.

## D. Các file kèm theo

- `bao_cao_phan_hoi_thay_2026-11-15.pdf`: báo cáo cho các thầy (12 mục, có số liệu).
- `latex/main.pdf`: bản thảo LaTeX đã cập nhật một phần (19 trang).
- `ext/decision_rules.md`: nhật ký các quy tắc, hash và kết quả (ghi trước khi chạy).
- Đặc tả: `ext/p4h8_spec.md`, `ext/p4h8_cmp_spec.md`, `ext/p4h8_flag_spec.md`, `ext/p4h8_flag_spec_v2.md`.

## E. Đang chạy

Phiên bản 2 của cờ tin cậy (sửa hai lỗi đặc trưng, thêm lag 2 và 3, báo AUROC theo lag × T × loại hỏng × mức hỏng). Khi có kết quả, bảng AUROC trong báo cáo sẽ được thay.
