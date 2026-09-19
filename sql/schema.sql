-- ============================================================
-- AI TECH RADAR DATABASE SCHEMA
-- ============================================================

create extension if not exists pgcrypto;


-- ============================================================
-- ARTICLES
-- ============================================================

create table if not exists public.articles (

    id uuid
        primary key
        default gen_random_uuid(),

    url text
        not null
        unique,

    source text
        not null,

    title text
        not null,

    raw_excerpt text,

    summary text,

    category text,

    importance_score numeric(4,2)
        default 0,

    why_it_matters text,

    published_at timestamptz
        not null,

    fetched_at timestamptz
        not null
        default now(),

    created_at timestamptz
        not null
        default now(),

    -- Bài được người dùng đánh dấu giữ lại.
    -- Cleanup sẽ KHÔNG xóa.
    saved boolean
        not null
        default false
);


-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_articles_published_at
on public.articles (
    published_at desc
);


create index if not exists idx_articles_fetched_at
on public.articles (
    fetched_at desc
);


create index if not exists idx_articles_importance
on public.articles (
    importance_score desc
);


-- Hỗ trợ cleanup.
create index if not exists idx_articles_cleanup
on public.articles (
    fetched_at,
    importance_score
)
where saved = false;


-- Hỗ trợ Saved Articles.
create index if not exists idx_articles_saved_true
on public.articles (
    saved
)
where saved = true;


-- ============================================================
-- SECURITY
-- ============================================================

alter table public.articles
enable row level security;


-- Backend sử dụng Supabase Secret Key.
grant all
on table public.articles
to service_role;