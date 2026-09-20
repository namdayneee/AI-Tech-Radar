from datetime import datetime, timezone
from functools import lru_cache

from supabase import create_client

from src.config import (
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


# ============================================================
# SUPABASE CLIENT
# ============================================================

@lru_cache(maxsize=1)
def get_client():
    """
    Tạo một Supabase client duy nhất
    cho toàn bộ process.
    """

    if (
        not SUPABASE_URL
        or not SUPABASE_SECRET_KEY
    ):
        raise RuntimeError(
            "Thiếu SUPABASE_URL "
            "hoặc SUPABASE_SECRET_KEY."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY,
    )


# ============================================================
# ARTICLE EXISTS
# ============================================================

def article_exists(
    url: str,
) -> bool:

    result = (
        get_client()
        .table("articles")
        .select("id")
        .eq("url", url)
        .limit(1)
        .execute()
    )

    return bool(
        result.data
    )


# ============================================================
# SAVE ARTICLE
# ============================================================

def save_article(
    article: dict,
):

    return (
        get_client()
        .table("articles")
        .upsert(
            article,
            on_conflict="url",
        )
        .execute()
    )


# ============================================================
# RECENT ARTICLES
# ============================================================

def get_recent_articles(
    since_iso: str,
    limit: int = 50,
) -> list[dict]:
    """
    Giữ lại cho report/dashboard sau này.
    """

    result = (
        get_client()
        .table("articles")
        .select("*")
        .gte(
            "fetched_at",
            since_iso,
        )
        .order(
            "importance_score",
            desc=True,
        )
        .limit(limit)
        .execute()
    )

    return (
        result.data
        or []
    )


# ============================================================
# UNSENT ARTICLES
# ============================================================

def get_unsent_articles(
    min_score: float = 5.5,
    limit: int = 10,
) -> list[dict]:
    """
    Lấy các bài:

    - chưa gửi Telegram
    - score >= min_score

    Không giới hạn 24 giờ.

    Lý do:
    nếu một ngày scheduler hoặc Telegram lỗi,
    bài chưa gửi vẫn còn để hôm sau retry.
    """

    result = (
        get_client()
        .table("articles")
        .select("*")
        .is_(
            "sent_at",
            "null",
        )
        .gte(
            "importance_score",
            min_score,
        )
        .order(
            "importance_score",
            desc=True,
        )
        .order(
            "fetched_at",
            desc=True,
        )
        .limit(limit)
        .execute()
    )

    return (
        result.data
        or []
    )


# ============================================================
# MARK SENT
# ============================================================

def mark_article_sent(
    article_id: str,
):
    """
    Chỉ gọi hàm này SAU KHI
    Telegram gửi thành công.
    """

    sent_at = (
        datetime.now(timezone.utc)
        .isoformat()
    )

    return (
        get_client()
        .table("articles")
        .update(
            {
                "sent_at": sent_at
            }
        )
        .eq(
            "id",
            article_id,
        )
        .execute()
    )