create extension if not exists pgcrypto;

create table if not exists public.articles (
    id uuid primary key default gen_random_uuid(),
    url text not null unique,
    source text not null,
    title text not null,
    raw_excerpt text,
    summary text,
    category text,
    importance_score numeric(4,2) default 0,
    why_it_matters text,
    published_at timestamptz not null,
    fetched_at timestamptz not null default now(),
    created_at timestamptz not null default now()
);

create index if not exists idx_articles_published_at
    on public.articles (published_at desc);

create index if not exists idx_articles_importance
    on public.articles (importance_score desc);

alter table public.articles enable row level security;

-- Không tạo policy public.
-- Backend/GitHub Actions dùng service_role key nên có thể thao tác server-side.
grant all on table public.articles to service_role;
