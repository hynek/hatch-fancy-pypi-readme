# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from ._fragments import VALID_FRAGMENTS, Fragment
from ._substitutions import Substituter
from .exceptions import ConfigurationError


@dataclass
class Config:
    content_type: str
    fragments: list[Fragment]
    substitutions: list[Substituter]


_BASE = "tool.hatch.metadata.hooks.fancy-pypi-readme."


def load_and_validate_config(config: dict[str, Any]) -> Config:
    errs = []

    ct = config.get("content-type")
    if ct is None:
        errs.append(f"{_BASE}content-type is missing.")
    elif ct not in ("text/markdown", "text/x-rst"):
        errs.append(
            f"{_BASE}content-type: '{ct}' is not one of "
            "['text/markdown', 'text/x-rst']"
        )

    try:
        fragments = _load_fragments(config.get("fragments"))
    except ConfigurationError as e:
        errs.extend(e.errors)

    try:
        subs_cfg = config.get("substitutions", [])
        if not isinstance(subs_cfg, list):
            raise ConfigurationError(
                [f"{_BASE}substitutions must be an array."]
            )

        substitutions = [
            Substituter.from_config(sub_cfg) for sub_cfg in subs_cfg
        ]
    except ConfigurationError as e:
        errs.extend(e.errors)

    if errs:
        raise ConfigurationError(errs)

    return Config(
        content_type=cast(str, ct),
        fragments=fragments,
        substitutions=substitutions,
    )


def _load_fragments(config: list[dict[str, str]] | None) -> list[Fragment]:
    """
    Load fragments from *config*.
    """
    if config is None:
        raise ConfigurationError([f"{_BASE}fragments is missing."])
    if not config:
        raise ConfigurationError([f"{_BASE}fragments must not be empty."])

    frags = []
    errs = []

    for frag_cfg in config:
        for frag in VALID_FRAGMENTS:
            if frag.key not in frag_cfg:
                continue

            try:
                frags.append(frag.from_config(frag_cfg))
            except ConfigurationError as e:
                errs.extend(e.errors)

            # We have either detected and added or detected and errored, but in
            # any case we're done with this fragment.
            break
        else:
            errs.append(f"Unknown fragment type {frag_cfg!r}.")

    if errs:
        raise ConfigurationError(errs)

    return frags
