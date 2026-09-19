# AI Tech Radar

AI Tech Radar là hệ thống cá nhân dùng để tự động thu thập, lọc và gửi các tin AI/công nghệ đáng chú ý mỗi ngày.

Hệ thống ưu tiên các chủ đề như:

- AI, LLM, AI Agent, Coding Agent
- OpenAI, Google, Hugging Face, Microsoft
- Developer Tools
- Web, Backend, Database
- DevOps, Cloud
- Hệ điều hành, Mạng máy tính, Distributed Systems
- Cybersecurity
- Nghiên cứu AI mới

## Kiến trúc hệ thống

```text
RSS / Hacker News / arXiv
          │
          ▼
      collect.py
          │
          ▼
        Gemini
          │
   ┌──────┼───────────┐
   ▼      ▼           ▼
Category  Score     Summary
   │      │           │
   └──────┴─────┬─────┘
                ▼
             Supabase
                │
       ┌────────┴────────┐
       ▼                 ▼
   digest.py         cleanup.py
       │                 │
       ▼                 ▼
   Telegram        Xóa dữ liệu cũ
```

## Luồng hoạt động

Mỗi ngày hệ thống tự động chạy theo lịch bằng GitHub Actions.

```text
06:45
Collect News
   ↓
RSS / API
   ↓
Gemini phân tích
   ↓
Lưu Supabase

07:30
Supabase
   ↓
Lọc tin quan trọng
   ↓
Telegram
```

Mỗi bài được gửi thành một tin nhắn Telegram riêng, gồm:

```text
Mức độ quan trọng
Tiêu đề
Chủ đề
Nguồn
Điểm
Tóm tắt
Vì sao đáng chú ý
Link bài gốc
```

## Data Lifecycle

Database không lưu dữ liệu vô hạn.

```text
score < 7       → giữ 30 ngày
score 7–8.9     → giữ 90 ngày
score >= 9      → giữ 365 ngày
saved = true    → giữ lại
```

Cleanup chạy tự động mỗi tuần.

## Công nghệ sử dụng

```text
Python
Gemini API
Supabase PostgreSQL
Telegram Bot API
GitHub Actions
RSS
Hacker News API
```

## Mục tiêu

AI Tech Radar giúp biến một lượng lớn tin công nghệ thành một feed ngắn gọn, có chọn lọc và dễ theo dõi mỗi ngày.
