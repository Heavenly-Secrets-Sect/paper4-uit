# Quy trình phát hành tri thức: Obsidian → Git → Confluence

Trạng thái: kế hoạch, chưa dựng. Các bước đánh dấu (chưa kiểm chứng) cần thử trên space nháp trước khi dùng.

## Nguyên tắc

- Git là nguồn gốc duy nhất. Confluence chỉ là bản đọc đã công bố, đẩy một chiều. Không sửa trực tiếp trên Confluence, vì lần phát hành sau sẽ ghi đè.
- Chỉ những file nằm trong thư mục `publish/` của vault mới được đẩy lên. Ghi chú nháp, ý tưởng chưa công bố thì ở ngoài thư mục này.
- Task nằm ở Jira, kiến thức nằm ở Obsidian, Confluence chỉ dành cho người ngoài nhóm cần đọc bản đã chốt.

## Các bước

1. Viết và sửa ghi chú trong vault như bình thường (Obsidian Git tự commit và push).
2. Khi một ghi chú sẵn sàng công bố, chuyển hoặc sao chép nó vào `publish/` và đặt `status: done` trong frontmatter.
3. Chuyển `[[wikilink]]` thành link thường, bỏ callout và embed Obsidian trong các file ở `publish/` (chưa kiểm chứng công cụ chuyển đổi).
4. Một người trong nhóm tạo GitHub Release với tên tag dạng `v0.1`, ghi rõ nội dung thay đổi.
5. Workflow `publish-confluence` chạy khi release được publish: chuyển Markdown sang định dạng Confluence và tạo hoặc cập nhật page trong space đã chọn (chưa kiểm chứng, dự kiến dùng `mark` hoặc script gọi REST API).
6. Workflow gửi tin vào kênh thông báo trên Discord: "Đã xuất bản vX lên Confluence" kèm link release.
7. Nếu workflow lỗi, `notify-failure` báo vào kênh hộ-sơn-đại-trận (cần thêm tên workflow mới vào danh sách theo dõi).

## Secret cần có (trong repo vault, không đưa vào chat hay commit)

- URL site Confluence
- Email tài khoản Atlassian
- API token Atlassian
- Webhook Discord cho kênh thông báo

## Việc cần làm trước khi dùng

- Tạo space Confluence và chọn page cha.
- Thử đẩy 1 file mẫu lên space nháp.
- Kiểm tra giới hạn gói Free của Confluence.
- Quyết định có cần Confluence thật không: nếu không có người ngoài nhóm đọc, xuất PDF từ LaTeX là đủ.
