-- ============================================================
-- AI TECH RADAR V2
-- Technology Intelligence Database
-- ============================================================


-- ============================================================
-- 1. RADAR ITEMS
-- ============================================================

create table if not exists public.radar_items (

    id uuid
        primary key
        default gen_random_uuid(),

    -- github / huggingface / pypi / ...
    source_platform text
        not null,

    -- ID duy nhất bên nguồn.
    -- Ví dụ:
    -- repo:owner/repo
    -- model:Qwen/model
    external_id text
        not null,

    -- AI_MODEL / DEV_TOOL / GITHUB_REPO / ...
    item_type text
        not null,

    name text,

    title text
        not null,

    description text,

    url text
        not null,

    category text,

    -- ========================================================
    -- SCORING
    -- ========================================================

    relevance_score numeric(4,2)
        not null
        default 0,

    novelty_score numeric(4,2)
        not null
        default 0,

    quality_score numeric(4,2)
        not null
        default 0,

    momentum_score numeric(4,2)
        not null
        default 0,

    importance_score numeric(4,2)
        not null
        default 0,

    final_score numeric(4,2)
        not null
        default 0,

    -- ========================================================
    -- AI ANALYSIS
    -- ========================================================

    summary text,

    why_it_matters text,

    -- WATCH / ASSESS / TRIAL
    radar_status text
        not null
        default 'WATCH',

    -- ========================================================
    -- SOURCE-SPECIFIC DATA
    -- ========================================================

    metadata jsonb
        not null
        default '{}'::jsonb,

    -- ========================================================
    -- TIME
    -- ========================================================

    published_at timestamptz,

    discovered_at timestamptz
        not null
        default now(),

    last_seen_at timestamptz
        not null
        default now(),

    -- ========================================================
    -- TELEGRAM / SAVED
    -- ========================================================

    sent_at timestamptz,

    saved boolean
        not null
        default false,

    created_at timestamptz
        not null
        default now(),

    constraint radar_items_unique_source
        unique (
            source_platform,
            external_id
        )
);


-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_radar_items_unsent
on public.radar_items (
    final_score desc,
    discovered_at desc
)
where sent_at is null;


create index if not exists idx_radar_items_type
on public.radar_items (
    item_type,
    final_score desc
);


create index if not exists idx_radar_items_last_seen
on public.radar_items (
    last_seen_at desc
);


create index if not exists idx_radar_items_cleanup
on public.radar_items (
    discovered_at,
    final_score
)
where saved = false;


-- ============================================================
-- 2. METRICS SNAPSHOTS
-- ============================================================

create table if not exists public.radar_metrics (

    id bigserial
        primary key,

    radar_item_id uuid
        not null
        references public.radar_items(id)
        on delete cascade,

    metric_name text
        not null,

    metric_value numeric
        not null,

    captured_at timestamptz
        not null
        default now()
);


create index if not exists idx_radar_metrics_item
on public.radar_metrics (
    radar_item_id,
    metric_name,
    captured_at desc
);


-- ============================================================
-- SECURITY
-- ============================================================

alter table public.radar_items
enable row level security;

alter table public.radar_metrics
enable row level security;


grant all
on table public.radar_items
to service_role;


grant all
on table public.radar_metrics
to service_role;


grant usage, select
on sequence public.radar_metrics_id_seq
to service_role;