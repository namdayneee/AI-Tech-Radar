-- ============================================================
-- AI TECH RADAR
-- Migration 003
-- Theo dõi bài nào đã gửi Telegram
-- ============================================================


-- 1. Thêm cột sent_at
alter table public.articles
add column if not exists sent_at timestamptz null;


-- 2. Các bài hiện tại đã được gửi trong giai đoạn test.
-- Đánh dấu chúng là đã gửi để hệ thống mới không spam lại.
--
-- Nếu bạn MUỐN gửi lại toàn bộ bài hiện có,
-- thì xóa phần UPDATE này trước khi Run.
update public.articles
set sent_at = now()
where sent_at is null;


-- 3. Index giúp lấy nhanh bài chưa gửi
create index if not exists idx_articles_unsent
on public.articles (
    importance_score desc,
    fetched_at desc
)
where sent_at is null;