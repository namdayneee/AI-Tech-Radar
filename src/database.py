from supabase import create_client

from src.config import (
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


def get_client():
    """
    Tạo Supabase client.
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


def article_exists(
    url: str,
) -> bool:
    """
    Kiểm tra URL đã tồn tại chưa.

    Mục đích:
    - tránh Gemini phân tích lại cùng một bài
    - tránh lưu duplicate
    """

    client = get_client()

    result = (
        client.table("articles")
        .select("id")
        .eq(
            "url",
            url,
        )
        .limit(1)
        .execute()
    )

    return bool(
        result.data
    )


def save_article(
    article: dict,
):
    """
    Lưu article vào Supabase.
    """

    client = get_client()

    return (
        client.table("articles")
        .upsert(
            article,
            on_conflict="url",
        )
        .execute()
    )


def get_recent_articles(
    since_iso: str,
    limit: int = 50,
) -> list[dict]:
    """
    Lấy các article mà hệ thống
    PHÁT HIỆN trong khoảng thời gian gần đây.

    Dùng fetched_at thay vì published_at.

    Ví dụ:

    published_at:
        bài gốc đăng 2 ngày trước

    fetched_at:
        bot mới phát hiện hôm nay

    → vẫn xuất hiện trong Daily Digest hôm nay.
    """

    client = get_client()

    result = (
        client.table("articles")
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