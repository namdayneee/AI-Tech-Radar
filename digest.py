import time

from src.database import (
    get_unsent_articles,
    mark_article_sent,
)

from src.telegram_sender import (
    send_telegram,
)


# ============================================================
# CONFIG
# ============================================================

MIN_SCORE = 5.5

MAX_ARTICLES = 3

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


def get_category_icon(
    category: str,
) -> str:

    return CATEGORY_ICONS.get(
        category,
        "📰",
    )


# ============================================================
# IMPORTANCE
# ============================================================

def get_importance_label(
    score: float,
) -> str:

    if score >= 9:

        return "🔥 MUST KNOW"

    if score >= 8:

        return "🚨 VERY IMPORTANT"

    if score >= 7:

        return "⭐ IMPORTANT"

    return "📰 WORTH READING"


# ============================================================
# MESSAGE
# ============================================================

def build_article_message(
    article: dict,
    index: int,
) -> str:

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
        article.get(
            "importance_score"
        )
        or 0
    )

    summary = (
        article.get("summary")
        or "Chưa có tóm tắt."
    )

    why = (
        article.get(
            "why_it_matters"
        )
        or "Chưa có phân tích."
    )

    url = (
        article.get("url")
        or ""
    )

    level = (
        get_importance_label(
            score
        )
    )

    icon = (
        get_category_icon(
            category
        )
    )

    return f"""
{level}

{icon} {index}. {title}

🏷 Chủ đề: {category}
🏢 Nguồn: {source}
⭐ Điểm quan trọng: {score:.1f}/10

📝 TÓM TẮT

{summary}

💡 VÌ SAO ĐÁNG CHÚ Ý?

{why}

🔗 ĐỌC BÀI GỐC

{url}
""".strip()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "[INFO] Starting Daily Digest..."
    )

    # ========================================================
    # 1. Chỉ lấy bài CHƯA gửi
    # ========================================================

    selected = (
        get_unsent_articles(
            min_score=MIN_SCORE,
            limit=MAX_ARTICLES,
        )
    )

    print(
        f"[INFO] Found "
        f"{len(selected)} "
        f"unsent articles."
    )


    # ========================================================
    # 2. Không có bài mới
    # ========================================================

    if not selected:

        send_telegram(
            "🤖 AI TECH RADAR\n\n"
            "Hôm nay chưa có tin mới "
            "đáng chú ý chưa được gửi."
        )

        print(
            "[DONE] No new articles."
        )

        return


    # ========================================================
    # 3. Header
    # ========================================================

    send_telegram(
        "🤖 AI TECH RADAR\n\n"
        f"📊 {len(selected)} "
        "tin mới đáng chú ý"
    )

    time.sleep(1)


    # ========================================================
    # 4. Gửi từng article
    # ========================================================

    sent_count = 0

    for index, article in enumerate(
        selected,
        start=1,
    ):

        try:

            message = (
                build_article_message(
                    article,
                    index,
                )
            )

            # -----------------------------------------------
            # Gửi Telegram trước
            # -----------------------------------------------

            send_telegram(
                message
            )


            # -----------------------------------------------
            # Chỉ khi gửi thành công mới đánh dấu sent_at
            # -----------------------------------------------

            mark_article_sent(
                article["id"]
            )


            sent_count += 1

            print(
                f"[SEND] "
                f"{index}/{len(selected)} "
                f"| {article.get('title')}"
            )


        except Exception as exc:

            # Nếu lỗi:
            # sent_at vẫn NULL
            # → lần sau retry.

            print(
                "[ERROR] "
                f"{article.get('title')} "
                f"| {exc}"
            )


        time.sleep(
            SEND_DELAY_SECONDS
        )


    print(
        "[DONE] Successfully sent "
        f"{sent_count}/"
        f"{len(selected)} articles."
    )


if __name__ == "__main__":
    main()