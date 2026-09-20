from datetime import (
    datetime,
    timezone,
)

from src.collectors.github_discovery import (
    collect_github_repositories,
)

from src.collectors.github_releases import (
    collect_github_releases,
)

from src.collectors.huggingface_radar import (
    collect_huggingface,
)

from src.collectors.pypi_radar import (
    collect_pypi_packages,
)


from src.radar.ai import (
    analyze_radar_item,
)

from src.radar.database import (
    get_radar_item,
    insert_radar_item,
    save_metrics,
    update_observation,
)

from src.radar.profile import (
    load_profile,
)

from src.radar.scoring import (
    prefilter_score,
    calculate_final_score,
)


# ============================================================
# COLLECT ALL SOURCES
# ============================================================

def collect_all() -> list[dict]:

    candidates = []


    collectors = [

        (
            "GitHub discovery",
            collect_github_repositories,
        ),

        (
            "GitHub releases",
            collect_github_releases,
        ),

        (
            "Hugging Face",
            collect_huggingface,
        ),

        (
            "PyPI",
            collect_pypi_packages,
        ),
    ]


    for name, collector in collectors:

        try:

            found = collector()


            print(
                f"[COLLECT] "
                f"{name}: "
                f"{len(found)}"
            )


            candidates.extend(
                found
            )


        except Exception as exc:

            print(
                f"[ERROR] "
                f"{name}: "
                f"{exc}"
            )


    return candidates


# ============================================================
# MAIN
# ============================================================

def main():

    profile = load_profile()


    limits = profile.get(
        "limits",
        {},
    )


    max_ai = int(
        limits.get(
            "ai_analyses_per_run",
            25,
        )
    )


    min_prefilter = float(
        limits.get(
            "min_prefilter_score",
            4.0,
        )
    )


    min_store = float(
        limits.get(
            "min_store_score",
            4.5,
        )
    )


    # ========================================================
    # 1. COLLECT
    # ========================================================

    candidates = collect_all()


    print(
        f"[INFO] Raw candidates: "
        f"{len(candidates)}"
    )


    # ========================================================
    # 2. DEDUP
    # ========================================================

    unique = {}


    for candidate in candidates:

        key = (

            candidate[
                "source_platform"
            ],

            candidate[
                "external_id"
            ],
        )


        candidate[
            "_prefilter_score"
        ] = prefilter_score(
            candidate
        )


        old = unique.get(
            key
        )


        if old is None:

            unique[
                key
            ] = candidate

            continue


        if (
            candidate[
                "_prefilter_score"
            ]
            >
            old[
                "_prefilter_score"
            ]
        ):

            unique[
                key
            ] = candidate


    print(
        f"[INFO] Unique candidates: "
        f"{len(unique)}"
    )


    # ========================================================
    # 3. RANK BY CHEAP SCORE
    # ========================================================

    ranked = sorted(

        unique.values(),

        key=lambda item:
            item.get(
                "_prefilter_score",
                0,
            ),

        reverse=True,
    )


    # ========================================================
    # COUNTERS
    # ========================================================

    analyzed = 0

    created = 0

    observed = 0

    skipped_prefilter = 0

    skipped_ai = 0

    skipped_score = 0


    # ========================================================
    # 4. PROCESS
    # ========================================================

    for candidate in ranked:


        # ====================================================
        # EXISTING ITEM?
        # ====================================================

        existing = (
            get_radar_item(

                candidate[
                    "source_platform"
                ],

                candidate[
                    "external_id"
                ],
            )
        )


        if existing:

            update_observation(
                existing["id"],

                candidate.get(
                    "metadata",
                    {},
                ),
            )


            save_metrics(
                existing["id"],

                candidate.get(
                    "metadata",
                    {},
                ),
            )


            observed += 1

            continue


        # ====================================================
        # PREFILTER
        # ====================================================

        cheap_score = float(
            candidate.get(
                "_prefilter_score",
                0,
            )
        )


        if cheap_score < min_prefilter:

            skipped_prefilter += 1

            continue


        # ====================================================
        # GEMINI DAILY LIMIT
        # ====================================================

        if analyzed >= max_ai:

            print(
                "[INFO] Gemini analysis "
                f"limit reached: {max_ai}"
            )

            break


        # ====================================================
        # AI ANALYSIS
        # ====================================================

        try:

            analysis = (
                analyze_radar_item(
                    candidate
                )
            )


            analyzed += 1


            # =================================================
            # DEBUG SCORES
            # =================================================

            print(
                "[AI] "
                f"{candidate['title']} "
                "| "
                f"rel={analysis['relevance_score']} "
                f"nov={analysis['novelty_score']} "
                f"quality={analysis['quality_score']} "
                f"momentum={analysis['momentum_score']} "
                f"importance={analysis['importance_score']}"
            )


            # =================================================
            # AI SAYS NOT RELEVANT
            # =================================================

            if not analysis.get(
                "relevant"
            ):

                skipped_ai += 1

                print(
                    "[SKIP AI] "
                    + candidate[
                        "title"
                    ]
                )

                continue


            # =================================================
            # FINAL SCORE
            # =================================================

            final_score = (
                calculate_final_score(
                    analysis
                )
            )


            # =================================================
            # TOO LOW TO STORE
            # =================================================

            if final_score < min_store:

                skipped_score += 1

                print(
                    "[SKIP SCORE] "
                    f"{final_score}/10 "
                    f"| "
                    f"{candidate['title']}"
                )

                continue


            # =================================================
            # BUILD DB ROW
            # =================================================

            row = {

                "source_platform":
                    candidate[
                        "source_platform"
                    ],


                "external_id":
                    candidate[
                        "external_id"
                    ],


                "item_type":
                    analysis[
                        "item_type"
                    ],


                "name":
                    candidate.get(
                        "name"
                    ),


                "title":
                    candidate[
                        "title"
                    ],


                "description":
                    candidate.get(
                        "description",
                        "",
                    )[:8000],


                "url":
                    candidate[
                        "url"
                    ],


                "category":
                    analysis.get(
                        "category",
                        "Other",
                    ),


                "relevance_score":
                    analysis[
                        "relevance_score"
                    ],


                "novelty_score":
                    analysis[
                        "novelty_score"
                    ],


                "quality_score":
                    analysis[
                        "quality_score"
                    ],


                "momentum_score":
                    analysis[
                        "momentum_score"
                    ],


                "importance_score":
                    analysis[
                        "importance_score"
                    ],


                "final_score":
                    final_score,


                "summary":
                    analysis.get(
                        "summary",
                        "",
                    ),


                "why_it_matters":
                    analysis.get(
                        "why_it_matters",
                        "",
                    ),


                "radar_status":
                    analysis.get(
                        "radar_status",
                        "WATCH",
                    ),


                "metadata":
                    candidate.get(
                        "metadata",
                        {},
                    ),


                "published_at":
                    candidate.get(
                        "published_at"
                    ),


                "last_seen_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }


            # =================================================
            # SAVE
            # =================================================

            saved = (
                insert_radar_item(
                    row
                )
            )


            # =================================================
            # SAVE METRIC SNAPSHOT
            # =================================================

            save_metrics(
                saved["id"],
                row["metadata"],
            )


            created += 1


            print(
                "[SAVE] "
                f"{row['item_type']} "
                f"{final_score}/10 "
                f"| "
                f"{row['title']}"
            )


        except Exception as exc:

            print(
                "[ERROR] "
                f"{candidate['title']}: "
                f"{exc}"
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print(
        "======================================"
    )

    print(
        "TECHNOLOGY RADAR COLLECTION SUMMARY"
    )

    print(
        "======================================"
    )

    print(
        f"raw={len(candidates)}"
    )

    print(
        f"unique={len(unique)}"
    )

    print(
        f"analyzed={analyzed}"
    )

    print(
        f"created={created}"
    )

    print(
        f"observed={observed}"
    )

    print(
        f"skip_prefilter="
        f"{skipped_prefilter}"
    )

    print(
        f"skip_ai="
        f"{skipped_ai}"
    )

    print(
        f"skip_score="
        f"{skipped_score}"
    )

    print(
        "======================================"
    )


if __name__ == "__main__":

    main()