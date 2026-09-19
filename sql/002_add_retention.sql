-- ============================================================
-- AI TECH RADAR
-- Migration 002: Article retention / lifecycle
-- ============================================================


-- ------------------------------------------------------------
-- 1. Cho phép người dùng giữ lại bài quan trọng
-- ------------------------------------------------------------

alter table public.articles
add column if not exists saved boolean
not null
default false;


-- ------------------------------------------------------------
-- 2. Index cho Daily Digest
-- ------------------------------------------------------------

create index if not exists idx_articles_fetched_at
on public.articles (fetched_at desc);


-- ------------------------------------------------------------
-- 3. Index hỗ trợ cleanup
--
-- Cleanup chủ yếu xử lý:
-- saved = false
-- fetched_at
-- importance_score
-- ------------------------------------------------------------

create index if not exists idx_articles_cleanup
on public.articles (
    fetched_at,
    importance_score
)
where saved = false;


-- ------------------------------------------------------------
-- 4. Index cho các bài đã bookmark
-- ------------------------------------------------------------

create index if not exists idx_articles_saved_true
on public.articles (saved)
where saved = true;