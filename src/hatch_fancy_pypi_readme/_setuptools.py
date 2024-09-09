from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ._builder import build_text
from ._config import Config, load_and_validate_config

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

if TYPE_CHECKING:
    from setuptools import Distribution


_NAME = "fancy-pypi-readme"


def get_config() -> Config | None:
    with open("pyproject.toml", "rb") as f:
        tools = tomllib.load(f).get("tool") or {}

    return (
        load_and_validate_config(tools[_NAME], f"tool.{_NAME}.")
        if _NAME in tools
        else None
    )


def update_metadata(dist: Distribution) -> None:
    """Update the distribution's core metadata description"""
    config = get_config()
    if config:
        dist.metadata.long_description = build_text(
            config.fragments,
            config.substitutions,
            version=dist.metadata.get_version(),
        )
        dist.metadata.long_description_content_type = config.content_type


# Delay hook so that plugins like setuptools-scm can run first:
update_metadata.order = 100  # type: ignore[attr-defined]
