# AI Tech Radar

AI Tech Radar là hệ thống cá nhân dùng để tự động theo dõi các tin tức và công nghệ mới trong lĩnh vực AI, lập trình và phần mềm.

Mục tiêu của dự án là giúp người dùng không phải tự mở nhiều website mỗi ngày mà vẫn có thể biết được những nội dung đáng chú ý như:

- Model AI mới
- Công cụ hỗ trợ lập trình mới
- Repository GitHub mới
- Release mới của framework, thư viện và công nghệ
- Package mới
- Tin tức AI và công nghệ quan trọng

Hệ thống tự động thu thập dữ liệu, dùng Gemini để phân tích và chấm điểm, lưu vào Supabase và gửi các nội dung đáng chú ý qua Telegram.

---

## V1 — News Radar

Phiên bản đầu tiên tập trung vào việc theo dõi các bài báo và tin tức công nghệ.

Luồng hoạt động:

```text
RSS / Hacker News
        ↓
     collect.py
        ↓
      Gemini
        ↓
     Supabase
        ↓
     Telegram
```

Các bài viết được AI:

- Phân loại chủ đề
- Chấm điểm mức độ quan trọng
- Tóm tắt nội dung
- Giải thích vì sao đáng chú ý

Dữ liệu được lưu trong bảng:

```text
articles
```

V1 giúp tự động hóa việc đọc tin, nhưng vẫn chủ yếu phụ thuộc vào các bài báo.

---

## V2 — Technology Radar

V2 mở rộng hệ thống từ một News Radar thành một Technology Radar.

Ngoài bài báo, hệ thống có thể theo dõi trực tiếp:

```text
AI_MODEL
DEV_TOOL
GITHUB_REPO
RELEASE
LANGUAGE
FRAMEWORK
PACKAGE
```

Các nguồn chính gồm:

```text
GitHub
Hugging Face
PyPI
RSS
Hacker News
arXiv
```

Luồng V2:

```text
GitHub / Hugging Face / PyPI / RSS / HN
                    ↓
                 Collector
                    ↓
                Pre-filter
                    ↓
                  Gemini
                    ↓
              radar_items
                    ↓
                 Telegram
```

Mỗi công nghệ được đánh giá theo nhiều tiêu chí như:

```text
Relevance
Novelty
Quality
Momentum
Importance
```

Sau đó hệ thống tính `final_score` để quyết định nội dung nào đáng lưu và đáng gửi.

---

## Kiến trúc hiện tại

```text
Cloudflare Cron
       ↓
Cloudflare Worker
       ↓
GitHub Actions
       ↓
Python Collectors
       ↓
Gemini
       ↓
Supabase
       ↓
Telegram
```

Cloudflare chịu trách nhiệm chạy hệ thống theo lịch.

GitHub Actions chạy các script thu thập, gửi bản tin và dọn dữ liệu.

Supabase lưu dữ liệu.

Telegram là nơi nhận các tin quan trọng.

---

## Database

Hệ thống hiện dùng hai bảng chính:

```text
articles
```

Lưu các bài báo và tin tức của V1.

```text
radar_items
```

Lưu các công nghệ của V2 như model, tool, repo, release và package.

Ngoài ra có:

```text
radar_metrics
```

để lưu các chỉ số như stars, downloads hoặc likes phục vụ việc theo dõi xu hướng sau này.

---

## Công nghệ sử dụng

```text
Python
Gemini API
Supabase
Telegram Bot
GitHub Actions
Cloudflare Workers
GitHub API
Hugging Face
PyPI
RSS
Hacker News
```

---

## Quá trình phát triển

```text
V1

News
↓
Gemini
↓
Supabase
↓
Telegram
```

được nâng cấp thành:

```text
V2

News
+
AI Models
+
Developer Tools
+
GitHub Repositories
+
Releases
+
Packages
        ↓
      Gemini
        ↓
 Technology Radar
        ↓
     Supabase
        ↓
     Telegram
```

Mục tiêu cuối cùng của AI Tech Radar là trở thành một hệ thống theo dõi công nghệ cá nhân, giúp phát hiện sớm những công nghệ mới có thể hữu ích cho việc học tập, lập trình và xây dựng dự án.
