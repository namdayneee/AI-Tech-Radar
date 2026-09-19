from datetime import datetime, timezone

from src.ai import analyze_article
from src.config import RSS_FEEDS, MAX_AI_ANALYSES_PER_RUN
from src.database import article_exists, save_article
from src.hn_collector import collect_hacker_news
from src.rss_collector import collect_feed


def main():
    candidates = []

    for feed in RSS_FEEDS:
        try:
            found = collect_feed(feed)
            print(f"[RSS] {feed['name']}: {len(found)} items")
            candidates.extend(found)
        except Exception as exc:
            print(f"[ERROR] RSS {feed['name']}: {exc}")

    try:
        hn = collect_hacker_news()
        print(f"[HN] {len(hn)} relevant stories")
        candidates.extend(hn)
    except Exception as exc:
        print(f"[ERROR] Hacker News: {exc}")

    # Dedup ngay trong cùng một lần chạy theo URL.
    unique = {}
    for item in candidates:
        unique[item["url"]] = item

    analyzed_count = 0
    saved_count = 0

    for item in unique.values():
        if analyzed_count >= MAX_AI_ANALYSES_PER_RUN:
            print("[INFO] Đã đạt MAX_AI_ANALYSES_PER_RUN.")
            break

        try:
            if article_exists(item["url"]):
                continue

            analysis = analyze_article(item)
            analyzed_count += 1

            if not analysis.get("relevant"):
                print(f"[SKIP] {item['title']}")
                continue

            article = {
                **item,
                "category": analysis.get("category", "Other"),
                "importance_score": analysis.get("importance_score", 0),
                "summary": analysis.get("summary", ""),
                "why_it_matters": analysis.get("why_it_matters", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            save_article(article)
            saved_count += 1
            print(
                f"[SAVE {article['importance_score']}/10] "
                f"{article['source']} - {article['title']}"
            )

        except Exception as exc:
            print(f"[ERROR] {item.get('title')}: {exc}")

    print(f"[DONE] analyzed={analyzed_count}, saved={saved_count}")


if __name__ == "__main__":
    main()
