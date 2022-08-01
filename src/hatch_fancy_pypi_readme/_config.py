# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._fragments import Fragment, load_fragments
from .exceptions import ConfigurationError


@dataclass
class Config:
    content_type: str
    fragments: list[Fragment]


def load_and_validate_config(config: dict[str, Any]) -> Config:
    errs = []
    frags = []

    if "content-type" not in config:
        errs.append(
            "Missing tool.hatch.metadata.hooks.fancy-pypi-readme.content-type "
            "setting."
        )

    try:
        try:
            frag_cfg_list = config["fragments"]
        except KeyError:
            errs.append(
                "Missing tool.hatch.metadata.hooks.fancy-pypi-readme.fragments"
                " setting."
            )
        else:
            frags = load_fragments(frag_cfg_list)

    except ConfigurationError as e:
        errs.extend(e.errors)

    if errs:
        raise ConfigurationError(errs)

    return Config(config["content-type"], frags)
