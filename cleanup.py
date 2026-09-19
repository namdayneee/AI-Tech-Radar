import os
from datetime import datetime, timedelta, timezone

from src.database import get_client


# ============================================================
# RETENTION CONFIGURATION
# ============================================================

# score < 7
LOW_RETENTION_DAYS = int(
    os.getenv(
        "RETENTION_LOW_DAYS",
        "30",
    )
)

# 7 <= score < 9
MEDIUM_RETENTION_DAYS = int(
    os.getenv(
        "RETENTION_MEDIUM_DAYS",
        "90",
    )
)

# score >= 9
HIGH_RETENTION_DAYS = int(
    os.getenv(
        "RETENTION_HIGH_DAYS",
        "365",
    )
)


# ============================================================
# HELPERS
# ============================================================

def cutoff_date(days: int) -> str:
    """
    Trả về timestamp UTC của N ngày trước.
    """

    return (
        datetime.now(timezone.utc)
        - timedelta(days=days)
    ).isoformat()


def delete_low_importance(
    client,
) -> int:
    """
    score < 7
    và cũ hơn LOW_RETENTION_DAYS.
    """

    cutoff = cutoff_date(
        LOW_RETENTION_DAYS
    )

    result = (
        client.table("articles")
        .delete()
        .eq("saved", False)
        .lt("importance_score", 7)
        .lt("fetched_at", cutoff)
        .execute()
    )

    return len(
        result.data or []
    )


def delete_medium_importance(
    client,
) -> int:
    """
    7 <= score < 9
    và cũ hơn MEDIUM_RETENTION_DAYS.
    """

    cutoff = cutoff_date(
        MEDIUM_RETENTION_DAYS
    )

    result = (
        client.table("articles")
        .delete()
        .eq("saved", False)
        .gte("importance_score", 7)
        .lt("importance_score", 9)
        .lt("fetched_at", cutoff)
        .execute()
    )

    return len(
        result.data or []
    )


def delete_high_importance(
    client,
) -> int:
    """
    score >= 9
    và cũ hơn HIGH_RETENTION_DAYS.

    Các bài saved=true vẫn được giữ mãi.
    """

    cutoff = cutoff_date(
        HIGH_RETENTION_DAYS
    )

    result = (
        client.table("articles")
        .delete()
        .eq("saved", False)
        .gte("importance_score", 9)
        .lt("fetched_at", cutoff)
        .execute()
    )

    return len(
        result.data or []
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "======================================"
    )
    print(
        "AI TECH RADAR - DATABASE CLEANUP"
    )
    print(
        "======================================"
    )

    print()

    print(
        "Retention policy:"
    )

    print(
        f"score < 7       : "
        f"{LOW_RETENTION_DAYS} days"
    )

    print(
        f"7 <= score < 9  : "
        f"{MEDIUM_RETENTION_DAYS} days"
    )

    print(
        f"score >= 9      : "
        f"{HIGH_RETENTION_DAYS} days"
    )

    print(
        "saved = true    : keep forever"
    )

    print()

    client = get_client()

    # --------------------------------------------------------
    # Low
    # --------------------------------------------------------

    low_deleted = (
        delete_low_importance(
            client
        )
    )

    print(
        f"[CLEANUP] Low importance: "
        f"deleted {low_deleted}"
    )

    # --------------------------------------------------------
    # Medium
    # --------------------------------------------------------

    medium_deleted = (
        delete_medium_importance(
            client
        )
    )

    print(
        f"[CLEANUP] Medium importance: "
        f"deleted {medium_deleted}"
    )

    # --------------------------------------------------------
    # High
    # --------------------------------------------------------

    high_deleted = (
        delete_high_importance(
            client
        )
    )

    print(
        f"[CLEANUP] High importance: "
        f"deleted {high_deleted}"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total_deleted = (
        low_deleted
        + medium_deleted
        + high_deleted
    )

    print()

    print(
        "--------------------------------------"
    )

    print(
        f"[DONE] Total deleted: "
        f"{total_deleted}"
    )

    print(
        "--------------------------------------"
    )


if __name__ == "__main__":
    main()