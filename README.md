# AI Tech Radar

AI Tech Radar là một hệ thống cá nhân dùng để tự động thu thập, phân tích và gửi các tin tức AI và công nghệ đáng chú ý mỗi ngày.

## Mục tiêu

Hệ thống giúp người dùng:

- Theo dõi các tin AI và công nghệ mới.
- Giảm thời gian phải tự tìm kiếm thông tin từ nhiều nguồn.
- Tự động lọc những bài có mức độ liên quan và quan trọng cao.
- Nhận bản tin ngắn gọn qua Telegram.

## Cách hoạt động

```text
Nguồn tin
   ↓
RSS / API
   ↓
Python Collector
   ↓
Gemini phân tích
   ↓
Supabase lưu dữ liệu
   ↓
Telegram gửi bản tin
```

Hệ thống lấy dữ liệu từ các nguồn như:

- OpenAI
- Google AI
- Hugging Face
- Microsoft Research
- arXiv
- Hacker News

Gemini được dùng để:

- Phân loại chủ đề.
- Chấm điểm mức độ quan trọng.
- Tóm tắt nội dung.
- Giải thích vì sao bài viết đáng chú ý.

## Kiến trúc

```text
Cloudflare Cron
      ↓
GitHub Actions
      ↓
collect.py
      ↓
Gemini
      ↓
Supabase
      ↓
digest.py
      ↓
Telegram
```

Cloudflare chịu trách nhiệm kích hoạt hệ thống theo lịch.

GitHub Actions chạy các tác vụ thu thập, gửi bản tin và dọn dữ liệu.

Supabase lưu các bài viết đã được phân tích.

Telegram là nơi người dùng nhận các tin quan trọng.

## Quản lý dữ liệu

Hệ thống có cơ chế tự động xóa dữ liệu cũ để tránh database tăng vô hạn.

```text
score < 7       → giữ 30 ngày
score 7–8.9     → giữ 90 ngày
score >= 9      → giữ 365 ngày
saved = true    → giữ lại
```

Các bài đã gửi Telegram được đánh dấu bằng `sent_at` để tránh gửi trùng.

## Công nghệ sử dụng

- Python
- Gemini API
- Supabase PostgreSQL
- Telegram Bot API
- GitHub Actions
- Cloudflare Workers
- RSS
- Hacker News API

## Kết quả

AI Tech Radar có thể tự động:

```text
Thu thập tin
→ Phân tích
→ Lưu dữ liệu
→ Lọc tin quan trọng
→ Gửi Telegram
→ Dọn dữ liệu cũ
```

Hệ thống hoạt động tự động trên cloud và không cần bật máy tính cá nhân liên tục.
