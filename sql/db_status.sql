-- ============================================================
-- AI TECH RADAR
-- Database Status / Health Check
-- ============================================================


-- ------------------------------------------------------------
-- Tổng kích thước database
-- ------------------------------------------------------------

select
    pg_size_pretty(
        pg_database_size(
            current_database()
        )
    ) as database_size;


-- ------------------------------------------------------------
-- Kích thước riêng bảng articles
-- ------------------------------------------------------------

select
    pg_size_pretty(
        pg_total_relation_size(
            'public.articles'
        )
    ) as articles_total_size;


-- ------------------------------------------------------------
-- Tổng số articles
-- ------------------------------------------------------------

select
    count(*) as total_articles
from public.articles;


-- ------------------------------------------------------------
-- Saved articles
-- ------------------------------------------------------------

select
    count(*) as saved_articles
from public.articles
where saved = true;


-- ------------------------------------------------------------
-- Phân bố score
-- ------------------------------------------------------------

select

    count(*) filter (
        where importance_score < 7
    ) as low_importance,

    count(*) filter (
        where importance_score >= 7
        and importance_score < 9
    ) as medium_importance,

    count(*) filter (
        where importance_score >= 9
    ) as high_importance

from public.articles;


-- ------------------------------------------------------------
-- Article cũ nhất và mới nhất
-- ------------------------------------------------------------

select

    min(fetched_at)
        as oldest_article,

    max(fetched_at)
        as newest_article

from public.articles;


-- ------------------------------------------------------------
-- Số bài theo nguồn
-- ------------------------------------------------------------

select

    source,

    count(*) as article_count

from public.articles

group by source

order by article_count desc;


-- ------------------------------------------------------------
-- Số bài theo category
-- ------------------------------------------------------------

select

    category,

    count(*) as article_count

from public.articles

group by category

order by article_count desc;