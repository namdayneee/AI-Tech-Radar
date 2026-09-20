from src.radar.profile import (
    load_profile,
)


# ============================================================
# PREFILTER BASE SCORE
# ============================================================

TYPE_BASE_SCORE = {

    "AI_MODEL":
        5.0,

    "DEV_TOOL":
        4.5,

    "GITHUB_REPO":
        4.0,

    "LANGUAGE_CANDIDATE":
        4.0,

    "RELEASE":
        6.0,

    "FRAMEWORK":
        4.5,

    "PACKAGE":
        3.0,

    "PAPER":
        4.5,

    "SECURITY":
        5.0,

    "OTHER":
        2.0,
}


# ============================================================
# HELPERS
# ============================================================

def safe_float(
    value,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 10.0,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ============================================================
# CHEAP PREFILTER
# ============================================================

def prefilter_score(
    candidate: dict,
) -> float:
    """
    Cheap scoring trước Gemini.

    Mục tiêu:

    100+ candidates
        ↓
    cheap rules
        ↓
    ~25 candidates
        ↓
    Gemini

    giúp tiết kiệm quota.
    """

    profile = load_profile()


    high_keywords = [

        str(keyword).lower()

        for keyword
        in profile.get(
            "high_priority_keywords",
            [],
        )
    ]


    medium_keywords = [

        str(keyword).lower()

        for keyword
        in profile.get(
            "medium_priority_keywords",
            [],
        )
    ]


    item_type = str(
        candidate.get(
            "item_type_hint",
            "OTHER",
        )
    ).upper()


    score = TYPE_BASE_SCORE.get(
        item_type,
        2.0,
    )


    text = " ".join(
        [

            str(
                candidate.get(
                    "title",
                    "",
                )
            ),

            str(
                candidate.get(
                    "description",
                    "",
                )
            ),

            str(
                candidate.get(
                    "metadata",
                    {},
                )
            ),
        ]
    ).lower()


    # ========================================================
    # KEYWORDS
    # ========================================================

    high_hits = sum(

        1

        for keyword
        in high_keywords

        if keyword in text
    )


    medium_hits = sum(

        1

        for keyword
        in medium_keywords

        if keyword in text
    )


    score += min(
        high_hits * 1.2,
        4.0,
    )


    score += min(
        medium_hits * 0.5,
        2.0,
    )


    # ========================================================
    # METADATA SIGNALS
    # ========================================================

    metadata = (
        candidate.get(
            "metadata"
        )
        or {}
    )


    stars = safe_float(
        metadata.get(
            "stars"
        )
    )


    downloads = safe_float(
        metadata.get(
            "downloads"
        )
    )


    likes = safe_float(
        metadata.get(
            "likes"
        )
    )


    trending = safe_float(
        metadata.get(
            "trending_score"
        )
    )


    # ========================================================
    # GITHUB POPULARITY
    # ========================================================

    if stars >= 5000:

        score += 2.5

    elif stars >= 1000:

        score += 2.0

    elif stars >= 100:

        score += 1.0

    elif stars >= 20:

        score += 0.5


    # ========================================================
    # HUGGING FACE DOWNLOADS
    # ========================================================

    if downloads >= 1_000_000:

        score += 2.0

    elif downloads >= 100_000:

        score += 1.5

    elif downloads >= 10_000:

        score += 0.8


    # ========================================================
    # LIKES
    # ========================================================

    if likes >= 1000:

        score += 1.2

    elif likes >= 100:

        score += 0.8

    elif likes >= 20:

        score += 0.4


    # ========================================================
    # TRENDING
    # ========================================================

    if trending > 0:

        score += min(
            trending / 20,
            1.5,
        )


    return round(
        score,
        2,
    )


# ============================================================
# FINAL AI SCORE
# ============================================================

def calculate_final_score(
    analysis: dict,
) -> float:
    """
    Final Technology Radar score.

    Trọng số:

    relevance  35%
    quality    20%
    momentum   20%
    novelty    15%
    importance 10%
    """

    relevance = clamp(
        safe_float(
            analysis.get(
                "relevance_score"
            )
        )
    )


    quality = clamp(
        safe_float(
            analysis.get(
                "quality_score"
            )
        )
    )


    momentum = clamp(
        safe_float(
            analysis.get(
                "momentum_score"
            )
        )
    )


    novelty = clamp(
        safe_float(
            analysis.get(
                "novelty_score"
            )
        )
    )


    importance = clamp(
        safe_float(
            analysis.get(
                "importance_score"
            )
        )
    )


    score = (

        relevance
        * 0.35

        +

        quality
        * 0.20

        +

        momentum
        * 0.20

        +

        novelty
        * 0.15

        +

        importance
        * 0.10
    )


    return round(
        clamp(score),
        2,
    )