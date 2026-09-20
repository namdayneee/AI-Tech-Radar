import requests

from src.radar.profile import (
    load_profile,
)


def collect_github_releases() -> list[dict]:

    profile = load_profile()

    repositories = profile.get(
        "github_release_watchlist",
        [],
    )


    session = requests.Session()

    session.headers.update(
        {
            "Accept":
                "application/vnd.github+json",

            "X-GitHub-Api-Version":
                "2022-11-28",

            "User-Agent":
                "ai-tech-radar",
        }
    )


    results = []


    for repository in repositories:

        url = (
            "https://api.github.com/repos/"
            f"{repository}/releases/latest"
        )


        try:

            response = session.get(
                url,
                timeout=30,
            )


            # Một số repo không dùng GitHub Releases.

            if response.status_code == 404:
                continue


            response.raise_for_status()


            data = response.json()


            release_id = data.get(
                "id"
            )


            results.append(
                {

                    "source_platform":
                        "github",


                    "external_id":
                        (
                            f"release:"
                            f"{repository}:"
                            f"{release_id}"
                        ),


                    "item_type_hint":
                        "RELEASE",


                    "name":
                        repository,


                    "title":
                        (
                            f"{repository} "
                            f"{data.get('tag_name', '')}"
                        ).strip(),


                    "description":
                        (
                            data.get(
                                "body"
                            )
                            or ""
                        )[:6000],


                    "url":
                        (
                            data.get(
                                "html_url"
                            )
                            or ""
                        ),


                    "published_at":
                        data.get(
                            "published_at"
                        ),


                    "metadata": {

                        "repository":
                            repository,

                        "tag":
                            data.get(
                                "tag_name"
                            ),

                        "prerelease":
                            data.get(
                                "prerelease",
                                False,
                            ),

                        "draft":
                            data.get(
                                "draft",
                                False,
                            ),
                    },
                }
            )


        except Exception as exc:

            print(
                "[WARN] GitHub release "
                f"{repository}: {exc}"
            )


    return results