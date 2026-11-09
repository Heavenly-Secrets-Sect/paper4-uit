#!/usr/bin/env python3
"""Nhắc hạn chót vào Discord (kênh thiên-kiếp-bảng).

Đọc docs/team/deadlines.yml, chọn các mục còn 3 ngày, còn 1 ngày, đến hạn hôm nay,
hoặc quá hạn tối đa 7 ngày, rồi gửi MỘT tin vào webhook Discord.
Không có mục nào cần nhắc thì không gửi gì.

Biến môi trường:
  WEBHOOK         URL webhook Discord (bắt buộc, trừ khi DRY_RUN=1)
  DEADLINES_FILE  đường dẫn file (mặc định docs/team/deadlines.yml)
  TODAY           ghi đè ngày hiện tại, dạng YYYY-MM-DD (để thử)
  DRY_RUN         đặt 1 để chỉ in nội dung, không gửi
"""
import datetime
import json
import os
import sys
import urllib.request
from zoneinfo import ZoneInfo

import yaml

FILE = os.environ.get("DEADLINES_FILE", "docs/team/deadlines.yml")
REMIND_DAYS = {3, 1, 0}
MAX_OVERDUE = 7
TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def to_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value).strip())


def label(days_left):
    if days_left < 0:
        return f"🕓 Quá hạn {-days_left} ngày"
    if days_left == 0:
        return "🔴 Hôm nay"
    if days_left == 1:
        return "🟠 Còn 1 ngày"
    return f"🟡 Còn {days_left} ngày"


def build_message(items, today):
    rows = []
    for it in items:
        if not isinstance(it, dict) or "title" not in it or "due" not in it:
            print(f"Bỏ qua mục không hợp lệ: {it!r}", file=sys.stderr)
            continue
        due = to_date(it["due"])
        days_left = (due - today).days
        if days_left in REMIND_DAYS or -MAX_OVERDUE <= days_left < 0:
            rows.append((days_left, it, due))
    if not rows:
        return None
    rows.sort(key=lambda r: r[0])
    lines = ["⚡ **Thiên kiếp sắp tới**"]
    for days_left, it, due in rows:
        line = f"- {label(days_left)}: **{it['title']}** (hạn {due.strftime('%d/%m/%Y')})"
        if it.get("owner"):
            line += f", phụ trách {it['owner']}"
        if it.get("link"):
            line += f" {it['link']}"
        lines.append(line)
    return "\n".join(lines)[:1800]


def post(webhook, content):
    payload = json.dumps({"content": content, "allowed_mentions": {"parse": []}}).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "thien-co-mon-reminder/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"Discord trả về {resp.status}")


def main():
    today = to_date(os.environ["TODAY"]) if os.environ.get("TODAY") else datetime.datetime.now(TZ).date()
    with open(FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    message = build_message(data.get("items") or [], today)
    if message is None:
        print("Không có hạn nào cần nhắc hôm nay.")
        return 0
    if os.environ.get("DRY_RUN") == "1":
        print(message)
        return 0
    webhook = os.environ.get("WEBHOOK", "")
    if not webhook:
        print("Thiếu secret DISCORD_WEBHOOK_REMINDER", file=sys.stderr)
        return 1
    post(webhook, message)
    print("Đã gửi nhắc việc.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
