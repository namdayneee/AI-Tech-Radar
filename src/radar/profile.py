from functools import lru_cache
from pathlib import Path

import yaml


PROFILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "radar_profile.yaml"
)


@lru_cache(maxsize=1)
def load_profile() -> dict:

    with PROFILE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        return (
            yaml.safe_load(file)
            or {}
        )