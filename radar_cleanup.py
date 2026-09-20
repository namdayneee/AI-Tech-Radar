import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from src.database import (
    get_client,
)


LOW_DAYS = int(
    os.getenv(
        "RADAR_RETENTION_LOW_DAYS",
        "30",
    )
)


MEDIUM_DAYS = int(
    os.getenv(
        "RADAR_RETENTION_MEDIUM_DAYS",
        "90",
    )
)


HIGH_DAYS = int(
    os.getenv(
        "RADAR_RETENTION_HIGH_DAYS",
        "365",
    )
)


def cutoff(
    days: int,
) -> str:

    return (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=days
        )
    ).isoformat()


def delete_range(
    min_score,
    max_score,
    days,
):

    query = (
        get_client()
        .table(
            "radar_items"
        )
        .delete()
        .eq(
            "saved",
            False,
        )
        .lt(
            "discovered_at",
            cutoff(
                days
            ),
        )
    )


    if (
        min_score
        is not None
    ):

        query = query.gte(
            "final_score",
            min_score,
        )


    if (
        max_score
        is not None
    ):

        query = query.lt(
            "final_score",
            max_score,
        )


    result = (
        query.execute()
    )


    return len(
        result.data
        or []
    )


def main():

    low = delete_range(
        None,
        7,
        LOW_DAYS,
    )


    medium = delete_range(
        7,
        9,
        MEDIUM_DAYS,
    )


    high = delete_range(
        9,
        None,
        HIGH_DAYS,
    )


    print(
        "[DONE] "
        "Radar cleanup: "
        f"low={low}, "
        f"medium={medium}, "
        f"high={high}"
    )


if __name__ == "__main__":

    main()