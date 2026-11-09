# Thiết kế chi tiết server Discord cho nhóm 2 người

Tài liệu này là bản chi tiết của mục 3 đến 7 trong `ke_hoach_tong_mon.md`, điều chỉnh cho **nhóm 2 người, workload lớn**. Hệ thống công cụ: Discord (trao đổi, thông báo), GitHub (code, LaTeX), Obsidian (tri thức), Jira Kanban (task).

## 0. Nguyên tắc thiết kế cho nhóm 2 người

1. **Giảm việc thủ công, không thêm việc.** Mọi thứ lặp lại (nhắc deadline, bản tin, báo build lỗi) do máy làm. Hai người chỉ trả lời và quyết định.
2. **Ít kênh nhưng rõ vai trò.** Chia hai giai đoạn: **Giai đoạn A (bật ngay)** khoảng 12 kênh, **Giai đoạn B (mở khi cần)** phần còn lại. Dư kênh với 2 người chỉ tạo thêm chỗ phải nhớ.
3. **Hai người có quyền gần như ngang nhau** nhưng không dùng quyền Administrator hằng ngày; dùng role Chấp Sự với quyền vừa đủ.
4. **Mọi thứ cần lưu lâu dài rời khỏi Discord**: tri thức vào Obsidian, việc vào Jira, code vào Git. Discord chỉ là nơi trao đổi và nhận thông báo.
5. **Bí mật không đi qua Discord** (khóa API, `.env`, URL webhook). AutoMod chặn mẫu khóa (mục 7).
6. **Thiết kế để mở rộng:** khi có người thứ ba, chỉ cần thêm role Đệ Tử, không phải dựng lại.

---

## 1. Cài đặt toàn server

### 1.1 Thông tin chung
| Mục | Giá trị gợi ý |
|---|---|
| Tên server | Tên ngắn, ví dụ `Tông Môn <tên nhóm>` |
| Chế độ | Bật **Community** (cần cho Forum và Announcement) |
| Kênh quy tắc | `#truyen-cong-duong` |
| Kênh cập nhật của Community | `#truyen-cong-duong` |
| Ngôn ngữ | Tiếng Việt |
| Verification level | Cao (chỉ người có email/số điện thoại xác minh); server riêng tư nên dù sao cũng nhỏ |
| Explicit media content filter | Bật quét mọi thành viên |
| Yêu cầu 2FA cho quản trị | **Bật** (Server Settings, Safety Setup, Require 2FA for moderator actions) |
| System messages channel | Tắt thông báo chào mừng và boost để đỡ nhiễu |
| Invite | Chỉ tạo link mời có hạn dùng (1 lần, hết hạn 24 giờ); không để link vĩnh viễn |
| Timezone dùng cho nhắc việc | UTC+7 (Việt Nam). Chú ý: GitHub Actions chạy theo UTC, 08:00 VN là `0 1 * * *` |

### 1.2 Thông báo mặc định
- Server Settings, Default Notification Settings: **Only @mentions**.
- Mỗi người **mute** các kênh bot (mục 3). Riêng `#thien-co-cac` giữ bật.
- Tạo quy ước **giờ yên tĩnh** (ví dụ 23h đến 7h): không ping, trừ việc khẩn.

---

## 2. Roles

Màu chỉ để dễ nhìn; chọn tùy ý.

| Role | Ai | Quyền chính | Ghi chú |
|---|---|---|---|
| Tông Chủ | Owner (một người) | Owner của server | Ít dùng hằng ngày |
| Chấp Sự | Cả hai người | Manage Channels, Manage Roles (dưới mình), Manage Webhooks, Manage Threads, Manage Events, Manage Messages, View Audit Log | **Không** cấp Administrator. Hai người đều có role này |
| Trưởng Lão | Thầy hoặc anh hướng dẫn (nếu mời) | Xem và gửi tin ở các kênh trao đổi, tạo thread | Không có quyền quản trị |
| Đệ Tử | Thành viên tương lai | Xem, gửi tin, tạo thread, đính kèm file | Mặc định cho người mới được duyệt |
| Ký Danh | Người mới chưa duyệt | Chỉ xem `#truyen-cong-duong` | Dùng khi mở rộng |
| `@p4` | Người tham gia Paper 4 | Xem category Bí Cảnh Paper 4 | Dùng để mention theo dự án |
| `@mh-<ma-mon>` | Người học môn đó | Xem forum môn đó | Một role mỗi môn |
| Bot (tự tạo) | Webhook và bot | Gửi tin ở kênh được cấp | Không cấp quyền quản lý |

Quy tắc phân quyền cơ bản:
- Ở các category riêng, **tắt View Channel cho `@everyone`**, bật cho role tương ứng.
- Kênh bot: Đệ Tử **không có Send Messages** (webhook vẫn gửi được); bật `Create Public Threads` để thảo luận trong thread dưới tin của bot.
- Bất kỳ ai quản lý webhook phải thuộc Chấp Sự.

---

## 3. Danh sách kênh chi tiết

Quy ước tên: chữ thường không dấu, gạch ngang, kèm emoji đầu (đổi hoặc bỏ tùy ý). Cột **Giai đoạn**: A là bật ngay, B là mở sau.

### 3.1 Category 🏯 TÔNG MÔN (chung)

| Kênh | Loại | Giai đoạn | Ai ghi | Topic (mô tả hiển thị) | Ghi chú |
|---|---|---|---|---|---|
| 📜 `truyen-cong-duong` | Announcement | A | Chấp Sự | "Quy tắc, thông báo quan trọng, hướng dẫn. Đọc ghim trước." | Ghim README (mục 6.1) |
| 📥 `hom-thu` | Text | A | Mọi người | "Ghi nhanh việc cần làm và ý tưởng. Cuối tuần phân loại vào Jira hoặc Obsidian." | Thay cho ghi chú rời rạc; slowmode không cần |
| ⏰ `thien-co-cac` | Text (bot) | A | Chỉ bot và Chấp Sự | "Deadline, lịch họp, nhắc việc. Chỉ đọc." | Không mute; chỉ kênh này được ping role |
| 📰 `ban-tin` | Text (bot) | A | Chỉ bot | "Bản tin 08:00 mỗi ngày: commit, PR, việc đến hạn." | Mute |
| 🗣️ `nghi-su-dien` | Text | A | Mọi người | "Họp và quyết định. Mỗi buổi họp một thread: `YYYY-MM-DD họp`." | Biên bản ghi vào Obsidian, link vào thread |
| 🔊 `Nghị Sự Điện` | Voice | A | Mọi người | Họp thoại, chia sẻ màn hình | |
| 🔊 `Bế Quan Thất` | Voice | A | Mọi người | Làm việc tập trung cùng nhau (co-working), bật mic hay tắt tùy ý | Hợp nhóm 2 người làm từ xa |
| 💬 `tap-dich-vien` | Text | B | Mọi người | "Trò chuyện ngoài lề." | Mở khi cần tách khỏi `hom-thu` |

### 3.2 Category 📚 TÀNG KINH CÁC (tri thức)

| Kênh | Loại | Giai đoạn | Mô tả | Forum tag |
|---|---|---|---|---|
| 🧾 `tang-kinh-cac` | **Forum** | A | "Mỗi paper hoặc tài liệu một post. Link tới ghi chú Obsidian." | `da-doc-toan-van`, `moi-doc-abstract`, `can-doc-ky`, `baseline`, `phuong-phap`, `survey`, `ly-thuyet` |
| 🧰 `van-bao-cac` | Forum | B | "Tool, thủ thuật, tài nguyên." | `latex`, `python`, `obsidian`, `git`, `tool` |
| 🗃️ `cap-nhat-vault` | Text (bot) | B | "Ghi chú vault thay đổi." | Chỉ bật nếu muốn thông báo vault; mặc định dùng `ban-tin` |

Hướng dẫn tạo post trong `tang-kinh-cac` (ghim làm hướng dẫn của forum):
> Tiêu đề: `<Tác giả năm: tên ngắn>`. Nội dung: (1) vì sao đọc, (2) ý chính một dòng, (3) liên quan tới project nào, (4) link ghi chú Obsidian, (5) mức đã đọc (abstract hay toàn văn).

### 3.3 Category 🎓 MÔN HỌC (học kỳ hiện tại)

| Kênh | Loại | Giai đoạn | Ghi chú |
|---|---|---|---|
| `mh-<ma-mon>` | **Forum** | A (mỗi môn đang học một forum) | Tag: `bai-tap`, `de-thi`, `ghi-chu`, `huong-dan`, `deadline` |

- Đặt tên post: `<loại>: <chủ đề>` (ví dụ `bai-tap: Chương 3 hồi quy`).
- Hết học kỳ: đổi tên category thành `[Archive] HK<năm>`, bỏ quyền gửi tin, chuyển xuống cuối.

### 3.4 Category 🔬 BÍ CẢNH: PAPER 4

| Kênh | Loại | Giai đoạn | Mô tả | Ghi chú |
|---|---|---|---|---|
| 🧪 `p4-tro-chuyen` | Text | A | "Trao đổi hằng ngày về Paper 4." | Role `@p4` |
| ⚗️ `p4-luyen-dan-phong` | **Forum** | A | "Mỗi lượt chạy hoặc thí nghiệm một post: mục tiêu, cấu hình, kết quả, kết luận." | Tag: `exploratory`, `confirmed`, `not-confirmed`, `dry-run`, `loi`, `T40`, `T80`, `T150` |
| ⚖️ `p4-chap-phap` | Forum | B | "Review bản thảo và PR." | Mở khi có người review ngoài hai người |
| 🤖 `p4-feed` | Text (bot) | A | "GitHub và Jira của Paper 4." | Mute. Gộp GitHub và Jira vào một kênh vì hai người không cần tách |

Mẫu post trong `p4-luyen-dan-phong` (ghim):
> **Mục tiêu:** câu hỏi cần trả lời. **Cấu hình:** file config, seed, phiên bản code (commit). **Kết quả:** số chính (kèm CI). **Kết luận:** đạt hoặc không đạt theo quy tắc đã ghi trước. **Việc tiếp theo:** link task Jira.

### 3.5 Category 🐞 ĐÌ BẤC LÂU

| Kênh | Loại | Giai đoạn | Mô tả | Tag |
|---|---|---|---|---|
| `di-bac-lau` | Forum | A | "Mỗi lỗi một post: lỗi, cách tái hiện, đã thử gì." | `can-giup`, `dang-xu-ly`, `da-xu-ly`, `latex`, `python`, `git`, `moi-truong` |

Mẫu post lỗi (ghim): lỗi gì, lệnh chạy, thông báo lỗi (ngắn, **không dán khóa hoặc đường dẫn nhạy cảm**), môi trường, đã thử gì.

### 3.6 Category 🛡️ QUẢN TRỊ (ẩn với Đệ Tử và Trưởng Lão)

| Kênh | Loại | Giai đoạn | Mô tả |
|---|---|---|---|
| `bot-log` | Text (bot) | A | "Lỗi webhook, Actions, automation." Chấp Sự mute nhưng đọc khi có sự cố |
| `cau-hinh` | Text | B | "Ghi quy ước cấu hình server (không chứa bí mật)." |

### 3.7 Category 🗄️ ARCHIVE
Chứa category môn học cũ và Bí Cảnh đã xong. Khóa quyền gửi, mọi người vẫn đọc được.

**Tổng kết Giai đoạn A:** `truyen-cong-duong`, `hom-thu`, `thien-co-cac`, `ban-tin`, `nghi-su-dien`, hai voice, `tang-kinh-cac`, forum môn học (mỗi môn một), `p4-tro-chuyen`, `p4-luyen-dan-phong`, `p4-feed`, `di-bac-lau`, `bot-log`. Khoảng 13 đến 15 kênh tùy số môn.

---

## 4. Danh sách webhook và nguồn thông báo

Mỗi webhook tạo trong Channel Settings, Integrations, Webhooks. Đặt tên và avatar riêng cho dễ phân biệt. **URL là bí mật.**

| Kênh nhận | Nguồn | Sự kiện | Cách gửi | Tên secret |
|---|---|---|---|---|
| `p4-feed` | GitHub repo paper | Pushes, PR, Issues, Releases | Webhook GitHub (URL + `/github`) | (không cần secret trong repo) |
| `p4-feed` | Jira | Chuyển sang Blocked, sắp đến hạn | Jira Automation, hành động "Send web request" | Lưu trong cấu hình Jira |
| `thien-co-cac` | Cron nhắc deadline | 3 ngày, 1 ngày trước hạn | GitHub Actions (hoặc Jira Automation) | `DISCORD_WEBHOOK_REMINDER` |
| `ban-tin` | Cron mỗi ngày | Tóm tắt 24 giờ | GitHub Actions | `DISCORD_WEBHOOK_DIGEST` |
| `bot-log` | Actions | Build lỗi, workflow fail | GitHub Actions | `DISCORD_WEBHOOK_LOG` |

Quy tắc an toàn webhook:
- **Mọi payload đặt `allowed_mentions` rỗng** để tin tự động không ping nhầm ai (ví dụ commit message có `@everyone`):
  ```json
  {"content":"...","allowed_mentions":{"parse":[]}}
  ```
- Chỉ role cần ping mới mở ra rõ ràng cho từng workflow.
- Lộ URL thì xóa webhook và tạo lại, cập nhật secret.

### 4.1 Workflow: bản tin hằng ngày (08:00 VN)
Đặt trong `.github/workflows/daily-digest.yml` của repo paper. Sao chép sang repo vault nếu muốn bản tin cho vault.

```yaml
name: daily-digest
on:
  schedule:
    - cron: "0 1 * * *"   # 01:00 UTC = 08:00 giờ Việt Nam
  workflow_dispatch:
jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Post digest
        env:
          WEBHOOK: ${{ secrets.DISCORD_WEBHOOK_DIGEST }}
        run: |
          SINCE=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)
          LOG=$(git log --since="$SINCE" --pretty='- %s (%an)' | head -20)
          if [ -z "$LOG" ]; then exit 0; fi
          BODY=$(printf '**%s: 24 giờ qua**\n%s' "$GITHUB_REPOSITORY" "$LOG" | head -c 1800)
          jq -n --arg c "$BODY" '{content:$c, allowed_mentions:{parse:[]}}' \
            | curl -sS -H "Content-Type: application/json" -d @- "$WEBHOOK"
```

Ghi chú: Discord giới hạn nội dung tin khoảng 2000 ký tự nên đã cắt ở 1800. Ngày không có commit thì không gửi. Cần thử chạy tay (`workflow_dispatch`) trước khi tin cậy.

### 4.2 Workflow: báo khi `main` được cập nhật (tùy chọn)
```yaml
name: notify-main
on:
  push:
    branches: [main]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Post to Discord
        env:
          WEBHOOK: ${{ secrets.DISCORD_WEBHOOK_LOG }}
          MSG: ${{ github.event.head_commit.message }}
          AUTHOR: ${{ github.event.head_commit.author.name }}
          URL: ${{ github.event.head_commit.url }}
        run: |
          jq -n --arg c "**$AUTHOR** cập nhật main: $MSG $URL" \
            '{content:$c, allowed_mentions:{parse:[]}}' \
            | curl -sS -H "Content-Type: application/json" -d @- "$WEBHOOK"
```

### 4.3 Jira Automation gửi sang Discord
Rule: khi issue chuyển sang `Blocked`, hoặc trước hạn 3 ngày; hành động "Send web request": phương thức POST, header `Content-Type: application/json`, body:
```json
{"content":"{{issue.key}} đang bị chặn: {{issue.summary}} {{issue.url}}","allowed_mentions":{"parse":[]}}
```
Các biến `{{issue.key}}`, `{{issue.summary}}`, `{{issue.url}}` cần kiểm tra lại đúng trong Jira của bạn.

---

## 5. Nhịp làm việc hằng ngày cho 2 người

| Thời điểm | Việc | Nơi |
|---|---|---|
| Sáng | Đọc `ban-tin` và `thien-co-cac` (1 phút) | Discord |
| Đầu buổi làm | Kéo task từ `Ready` sang `In Progress` (WIP tối đa 2 mỗi người) | Jira |
| Trong ngày | Ý tưởng, việc phát sinh: ghi nhanh vào `hom-thu`. Hỏi và trả lời trong thread | Discord |
| Khi xong việc | Mở PR, kéo task sang `In Review`, nhắn người kia | GitHub, Jira |
| Cuối ngày (2 phút) | Cập nhật trạng thái task, ghi một dòng "hôm nay xong gì, mai làm gì" vào thread `Standup` trong `nghi-su-dien` (hoặc bỏ nếu hôm đó đã nói chuyện) | Discord |
| Hằng tuần (20 phút, voice) | Rà `hom-thu`, đưa vào Jira hoặc Obsidian; nhìn board, việc bị chặn; chọn việc cho tuần | Voice `Nghị Sự Điện` |
| Hằng tháng (30 phút) | Rà backlog, kênh nào thừa thì gộp, đặt lại WIP | Voice |

Phân công quyền sở hữu (ghi trong `cau-hinh` hoặc Obsidian): ai chịu trách nhiệm kênh/bot nào, ai duyệt PR của ai. Với 2 người, **hai người review chéo** nhau.

---

## 6. Nội dung ghim và quy tắc

### 6.1 Tin ghim trong `truyen-cong-duong` (README)
> **Chào mừng đến Tông Môn.**
> **Công cụ:** Discord để trao đổi; GitHub cho code và LaTeX; Obsidian cho tri thức; Jira cho việc.
> **Quy tắc:**
> 1. Việc cần làm thì vào Jira, không để trôi trong chat.
> 2. Tri thức và quyết định ghi vào Obsidian, rồi link vào Discord.
> 3. Trao đổi trong thread hoặc forum post, không rải trong kênh chính.
> 4. Không dán khóa API, `.env`, URL webhook, hoặc dữ liệu chưa công bố.
> 5. Không commit thẳng lên `main`; dùng Pull Request.
> 6. Ping role khi cần, không dùng `@everyone` trừ việc khẩn. Giờ yên tĩnh 23h đến 7h.
> 7. Hết học kỳ hoặc hết dự án thì archive, không xóa.
> **Bảng nghĩa tên:** Tàng Kinh Các = thư viện; Thiên Cơ Các = lịch và nhắc việc; Nghị Sự Điện = họp; Luyện Đan Phòng = thí nghiệm; Chấp Pháp Đường = review; Đì Bấc Lâu = debug; Bí Cảnh = một dự án.

### 6.2 Quy ước đặt tên
- Post forum: `<tác giả năm: tên>` (tài liệu), `<loại>: <chủ đề>` (môn học), `YYYY-MM-DD <mô tả ngắn>` (thí nghiệm hoặc họp).
- Nhánh Git: `exp/P4-12-ten-ngan`, `feat/...`, `fix/...`, `docs/...`.
- Commit: `P4-12: nội dung ngắn` (có mã Jira).
- File Obsidian: `YYYY-MM-DD-chu-de` cho họp; `tacgia-nam-tukhoa` cho paper.

---

## 7. AutoMod và an toàn

Bật AutoMod (Server Settings, Safety Setup, AutoMod) với các quy tắc:

| Quy tắc | Loại | Mục đích |
|---|---|---|
| Chặn mẫu khóa GitHub: `ghp_[A-Za-z0-9]{20,}` | Regex tùy chỉnh | Tránh dán token cá nhân |
| Chặn mẫu khóa API kiểu `sk-[A-Za-z0-9]{20,}` | Regex tùy chỉnh | Tránh dán khóa dịch vụ |
| Chặn `discord.com/api/webhooks/` | Từ khóa tùy chỉnh | Tránh dán URL webhook |
| Chặn `@everyone` với người không phải Chấp Sự | Mention | Tránh ping nhầm |

Cần kiểm tra giới hạn số quy tắc và độ dài regex của Discord trước khi nhập. Quy tắc chỉ bắt các mẫu phổ biến, không thay cho việc cẩn thận.

Thêm:
- Tài khoản quản trị bật 2FA.
- Lưu URL webhook trong password manager.
- Dữ liệu chưa công bố (kết quả chưa chốt, thông tin nhạy cảm của nhóm) chỉ đăng ở kênh có quyền hạn chế hoặc chỉ link sang Obsidian.
- Xem Audit Log hằng tháng.

---

## 8. Các bước dựng cụ thể (click path)

**Bước 1. Tạo server.** "Create My Own", "For me and my friends". Đặt tên và avatar.
**Bước 2. Bật Community.** Server Settings, Enable Community, chọn kênh quy tắc và cập nhật (tạm thời dùng kênh mặc định, đổi sang `truyen-cong-duong` sau).
**Bước 3. Cài đặt chung.** Mục 1.1 và 1.2.
**Bước 4. Tạo roles.** Mục 2, thứ tự từ trên xuống: Tông Chủ, Chấp Sự, Trưởng Lão, Đệ Tử, Ký Danh, các role dự án/môn. Gán Chấp Sự cho cả hai người.
**Bước 5. Tạo category và kênh.** Mục 3, theo giai đoạn A. Với từng kênh: đặt topic, đặt quyền (kênh bot tắt Send Messages với Đệ Tử), tạo tag cho forum.
**Bước 6. Ghim nội dung.** README (6.1), hướng dẫn forum, mẫu post.
**Bước 7. AutoMod.** Mục 7.
**Bước 8. Webhook GitHub.** Tạo webhook cho `p4-feed`, thêm `/github`, cấu hình ở GitHub chỉ chọn sự kiện cần (mục 4 của kế hoạch tổng). Thử bằng một PR giả.
**Bước 9. Actions.** Thêm secret `DISCORD_WEBHOOK_DIGEST`, `DISCORD_WEBHOOK_LOG`, `DISCORD_WEBHOOK_REMINDER`. Chạy tay từng workflow bằng `workflow_dispatch`.
**Bước 10. Jira Automation.** Tạo rule Blocked và sắp đến hạn, thử bằng một task giả.
**Bước 11. Scheduled Event.** Tạo sự kiện họp tuần lặp lại (Events, Create Event, chọn voice `Nghị Sự Điện`, lặp hằng tuần).
**Bước 12. Kiểm tra 3 ngày.** Dùng thật 3 ngày; ghi lại kênh nào không dùng, tin nào quá ồn; chỉnh.

---

## 9. Mở rộng khi có người thứ ba

- Thêm role Đệ Tử và role dự án; mở khóa các kênh Giai đoạn B cần thiết (`p4-chap-phap`, `tap-dich-vien`).
- Nếu bản tin quá dài, tách bản tin theo repo hoặc giảm số dòng.
- Bật bảo vệ nhánh `main` bắt buộc 1 review (với 2 người thì mỗi người review người còn lại).
- Rà lại quyền: người mới chỉ thấy category cần thiết.

---

## 10. Việc chưa kiểm chứng

- Giới hạn Discord: số tag forum, độ dài regex AutoMod, số quy tắc AutoMod, giới hạn ký tự tin nhắn. Kiểm tra trong giao diện khi cấu hình.
- Biến thông minh (`{{issue.*}}`) và hành động "Send web request" của Jira Automation trên gói của bạn.
- Cron của GitHub Actions có thể trễ vài phút đến vài chục phút khi hệ thống bận; không phù hợp cho việc cần đúng giờ tuyệt đối.
- Giới hạn gói miễn phí của Jira.
