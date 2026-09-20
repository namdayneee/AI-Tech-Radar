from datetime import (
    datetime,
    timezone,
)

from src.database import (
    get_client,
)


def get_radar_item(
    source_platform: str,
    external_id: str,
):

    result = (
        get_client()
        .table(
            "radar_items"
        )
        .select("*")
        .eq(
            "source_platform",
            source_platform,
        )
        .eq(
            "external_id",
            external_id,
        )
        .limit(1)
        .execute()
    )


    if result.data:

        return result.data[0]


    return None


def insert_radar_item(
    item: dict,
):

    result = (
        get_client()
        .table(
            "radar_items"
        )
        .insert(
            item
        )
        .execute()
    )


    if not result.data:

        raise RuntimeError(
            "Không insert được radar item."
        )


    return result.data[0]


def update_observation(
    item_id: str,
    metadata: dict,
):

    return (
        get_client()
        .table(
            "radar_items"
        )
        .update(
            {

                "metadata":
                    metadata,

                "last_seen_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }
        )
        .eq(
            "id",
            item_id,
        )
        .execute()
    )


def save_metrics(
    item_id: str,
    metadata: dict,
):

    metric_names = [

        "stars",

        "forks",

        "open_issues",

        "downloads",

        "likes",

        "trending_score",
    ]


    rows = []


    for name in metric_names:

        value = metadata.get(
            name
        )


        if value is None:

            continue


        try:

            value = float(
                value
            )

        except Exception:

            continue


        rows.append(
            {

                "radar_item_id":
                    item_id,

                "metric_name":
                    name,

                "metric_value":
                    value,
            }
        )


    if rows:

        (
            get_client()
            .table(
                "radar_metrics"
            )
            .insert(
                rows
            )
            .execute()
        )


def get_unsent_radar_items(
    min_score: float = 6.5,
    limit: int = 50,
) -> list[dict]:

    result = (
        get_client()
        .table(
            "radar_items"
        )
        .select("*")
        .is_(
            "sent_at",
            "null",
        )
        .gte(
            "final_score",
            min_score,
        )
        .order(
            "final_score",
            desc=True,
        )
        .order(
            "discovered_at",
            desc=True,
        )
        .limit(
            limit
        )
        .execute()
    )


    return (
        result.data
        or []
    )


def mark_radar_sent(
    item_id: str,
):

    return (
        get_client()
        .table(
            "radar_items"
        )
        .update(
            {

                "sent_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat()
            }
        )
        .eq(
            "id",
            item_id,
        )
        .execute()
    )