create extension if not exists pgcrypto;


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

    saved boolean
        not null
        default false,

    -- NULL = chưa gửi Telegram
    -- timestamp = đã gửi thành công
    sent_at timestamptz
        null
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


create index if not exists idx_articles_cleanup
on public.articles (
    fetched_at,
    importance_score
)
where saved = false;


create index if not exists idx_articles_saved_true
on public.articles (
    saved
)
where saved = true;


create index if not exists idx_articles_unsent
on public.articles (
    importance_score desc,
    fetched_at desc
)
where sent_at is null;


-- ============================================================
-- SECURITY
-- ============================================================

alter table public.articles
enable row level security;


grant all
on table public.articles
to service_role;