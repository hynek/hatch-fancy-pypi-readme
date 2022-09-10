# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jsonschema

from ._fragments import VALID_FRAGMENTS, Fragment
from ._humanize_validation_errors import errors_to_human_strings
from ._substitutions import Substituter
from ._validators import CustomValidator
from .exceptions import ConfigurationError


@dataclass
class Config:
    content_type: str
    fragments: list[Fragment]
    substitutions: list[Substituter]


SCHEMA = {
    "$schema": CustomValidator.META_SCHEMA["$id"],
    "type": "object",
    "properties": {
        "content-type": {
            "type": "string",
            "enum": ["text/markdown", "text/x-rst"],
        },
        "fragments": {
            "type": "array",
            "minItems": 1,
            # Items are validated separately for better error messages.
            "items": {"type": "object"},
        },
        "substitutions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "regex": True},
                    "replacement": {"type": "string"},
                    "ignore-case": {"type": "boolean"},
                },
                "required": ["pattern", "replacement"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["content-type", "fragments"],
    "additionalProperties": False,
}


def load_and_validate_config(config: dict[str, Any]) -> Config:
    errs = sorted(
        CustomValidator(SCHEMA).iter_errors(config),
        key=jsonschema.exceptions.relevance,
    )
    if errs:
        raise ConfigurationError(errors_to_human_strings(errs))

    return Config(
        config["content-type"],
        _load_fragments(config["fragments"]),
        [
            Substituter.from_config(sub_cfg)
            for sub_cfg in config.get("substitutions", [])
        ],
    )


def _load_fragments(config: list[dict[str, str]]) -> list[Fragment]:
    """
    Load fragments from *config*.

    This is a bit more complicated because validating the fragments field using
    `oneOf` leads to unhelpful error messages that are difficult to convert
    into something humanly meaningful.

    So we detect first, validate using jsonschema and try to load them. They
    still may fail loading if they refer to files and lack markers / the
    pattern doesn't match.
    """
    frags = []
    errs = []

    for i, frag_cfg in enumerate(config):
        for frag in VALID_FRAGMENTS:
            if frag.key not in frag_cfg:
                continue

            try:
                ves = sorted(
                    frag.validator.iter_errors(frag_cfg),
                    key=jsonschema.exceptions.relevance,
                )
                if ves:
                    raise ConfigurationError(
                        errors_to_human_strings(ves, ("fragments", i))
                    )
                frags.append(frag.from_config(frag_cfg))
            except ConfigurationError as e:
                errs.extend(e.errors)

            # We have either detecte and added or detected and errored, but in
            # any case we're done with this fragment.
            break
        else:
            errs.append(f"Unknown fragment type {frag_cfg!r}.")

    if errs:
        raise ConfigurationError(errs)

    return frags
