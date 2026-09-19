import time
from datetime import datetime, timedelta, timezone

from src.database import get_recent_articles
from src.telegram_sender import send_telegram


# ============================================================
# CONFIG
# ============================================================

MIN_SCORE = 5.5

# Tối đa số bài gửi mỗi ngày.
MAX_ARTICLES = 10

# Nghỉ giữa các message Telegram để tránh gửi quá dồn.
SEND_DELAY_SECONDS = 1


# ============================================================
# CATEGORY
# ============================================================

CATEGORY_ICONS = {
    "AI": "🤖",
    "Research": "🔬",
    "Developer Tools": "🛠",
    "Programming": "💻",
    "Infrastructure": "☁️",
    "Systems": "⚙️",
    "Security": "🔐",
    "Other": "📰",
}


def get_category_icon(category: str) -> str:
    """
    Trả icon tương ứng với category.
    """

    return CATEGORY_ICONS.get(
        category,
        "📰",
    )


# ============================================================
# IMPORTANCE LEVEL
# ============================================================

def get_importance_label(score: float) -> str:
    """
    Chuyển importance_score thành mức độ dễ nhìn trên Telegram.
    """

    if score >= 9.0:
        return "🔥 MUST KNOW"

    if score >= 8.0:
        return "🚨 VERY IMPORTANT"

    if score >= 7.0:
        return "⭐ IMPORTANT"

    return "📰 WORTH READING"


# ============================================================
# BUILD MESSAGE
# ============================================================

def build_article_message(
    article: dict,
    index: int,
) -> str:
    """
    Mỗi article được biến thành đúng 1 Telegram message.
    """

    title = (
        article.get("title")
        or "Không có tiêu đề"
    )

    source = (
        article.get("source")
        or "Unknown"
    )

    category = (
        article.get("category")
        or "Other"
    )

    score = float(
        article.get("importance_score")
        or 0
    )

    summary = (
        article.get("summary")
        or "Chưa có tóm tắt."
    )

    why_it_matters = (
        article.get("why_it_matters")
        or "Chưa có phân tích."
    )

    url = (
        article.get("url")
        or ""
    )

    category_icon = get_category_icon(
        category
    )

    importance_label = get_importance_label(
        score
    )

    message = f"""
{importance_label}

{category_icon} {index}. {title}

🏷 Chủ đề: {category}
🏢 Nguồn: {source}
⭐ Điểm quan trọng: {score:.1f}/10

📝 TÓM TẮT

{summary}

💡 VÌ SAO ĐÁNG CHÚ Ý?

{why_it_matters}

🔗 ĐỌC BÀI GỐC

{url}
""".strip()

    return message


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "[INFO] Starting Daily Digest..."
    )

    # ========================================================
    # 1. Lấy các article hệ thống phát hiện trong 24h gần nhất
    # ========================================================

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=24)
    ).isoformat()

    articles = get_recent_articles(
        since_iso=since,
        limit=50,
    )

    print(
        f"[INFO] Found "
        f"{len(articles)} articles "
        f"in the last 24 hours."
    )

    # ========================================================
    # 2. Lọc theo importance_score
    # ========================================================

    selected = []

    for article in articles:

        score = float(
            article.get(
                "importance_score"
            )
            or 0
        )

        if score >= MIN_SCORE:
            selected.append(article)

    # ========================================================
    # 3. Sắp xếp quan trọng nhất lên đầu
    # ========================================================

    selected.sort(
        key=lambda article: float(
            article.get(
                "importance_score"
            )
            or 0
        ),
        reverse=True,
    )

    # ========================================================
    # 4. Giới hạn số bài
    # ========================================================

    selected = selected[
        :MAX_ARTICLES
    ]

    print(
        f"[INFO] Selected "
        f"{len(selected)} articles "
        f"with score >= {MIN_SCORE}."
    )

    # ========================================================
    # 5. Không có tin
    # ========================================================

    if not selected:

        message = (
            "🤖 AI TECH RADAR\n\n"
            "24 giờ qua chưa có tin mới "
            f"vượt ngưỡng {MIN_SCORE}/10."
        )

        send_telegram(message)

        print(
            "[DONE] No important articles."
        )

        return

    # ========================================================
    # 6. Gửi header
    # ========================================================

    header = f"""
🤖 AI TECH RADAR

📅 Bản tin 24 giờ gần nhất

📊 {len(selected)} tin đáng chú ý

🔥 >= 9.0  MUST KNOW
🚨 >= 8.0  VERY IMPORTANT
⭐ >= 7.0  IMPORTANT
📰 >= 5.5  WORTH READING
""".strip()

    send_telegram(header)

    time.sleep(1)

    # ========================================================
    # 7. Mỗi article = 1 Telegram message
    # ========================================================

    for index, article in enumerate(
        selected,
        start=1,
    ):

        message = build_article_message(
            article,
            index,
        )

        try:

            send_telegram(message)

            print(
                f"[SEND] "
                f"{index}/{len(selected)} "
                f"| "
                f"{article.get('importance_score')} "
                f"| "
                f"{article.get('title')}"
            )

        except Exception as exc:

            print(
                f"[ERROR] Failed to send "
                f"article {index}: {exc}"
            )

        time.sleep(
            SEND_DELAY_SECONDS
        )

    # ========================================================
    # 8. Done
    # ========================================================

    print(
        f"[DONE] Sent "
        f"{len(selected)} "
        f"articles to Telegram."
    )


if __name__ == "__main__":
    main()