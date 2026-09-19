from datetime import datetime, timezone
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import feedparser


def _clean_html(value: str) -> str:
    if not value:
        return ""
    return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)


def _parse_date(entry) -> str:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = date_parser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def collect_feed(feed_config: dict) -> list[dict]:
    parsed = feedparser.parse(feed_config["url"])
    items = []

    if getattr(parsed, "bozo", False):
        print(f"[WARN] RSS có cảnh báo: {feed_config['name']}: {parsed.bozo_exception}")

    for entry in parsed.entries[: feed_config.get("max_items", 10)]:
        url = entry.get("link", "").strip()
        title = _clean_html(entry.get("title", "")).strip()
        excerpt = _clean_html(
            entry.get("summary", "")
            or entry.get("description", "")
        )[:5000]

        if not url or not title:
            continue

        items.append(
            {
                "url": url,
                "source": feed_config["name"],
                "title": title,
                "raw_excerpt": excerpt,
                "published_at": _parse_date(entry),
            }
        )

    return items
