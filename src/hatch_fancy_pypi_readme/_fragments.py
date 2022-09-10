# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable

from jsonschema import Draft202012Validator, Validator


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from .exceptions import ConfigurationError


TEXT_V = Draft202012Validator(
    {
        "type": "object",
        "properties": {"text": {"type": "string", "pattern": ".+"}},
        "required": ["text"],
        "additionalProperties": False,
    },
    format_checker=Draft202012Validator.FORMAT_CHECKER,
)

FILE_V = Draft202012Validator(
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "pattern": ".+"},
            "start-after": {"type": "string", "pattern": ".+"},
            "end-before": {"type": "string", "pattern": ".+"},
            "pattern": {"type": "string", "format": "regex"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    format_checker=Draft202012Validator.FORMAT_CHECKER,
)


class Fragment(Protocol):
    key: ClassVar[str]
    validator: ClassVar[Validator]

    @classmethod
    def from_config(self, cfg: dict[str, str]) -> Fragment:
        ...

    def render(self) -> str:
        ...


@dataclass
class TextFragment:
    """
    A static text fragment.
    """

    key: ClassVar[str] = "text"
    validator: ClassVar[Validator] = TEXT_V

    _text: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment:
        return cls(cfg[cls.key])

    def render(self) -> str:
        return self._text


@dataclass
class FileFragment:
    """
    A static text fragment.
    """

    key: ClassVar[str] = "path"
    validator: ClassVar[Validator] = FILE_V

    _contents: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment:
        path = Path(cfg.pop(cls.key))
        start_after = cfg.pop("start-after", None)
        end_before = cfg.pop("end-before", None)
        pattern = cfg.pop("pattern", None)

        errs: list[str] = []

        try:
            contents = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise ConfigurationError([f"Fragment file '{path}' not found."])

        if start_after is not None:
            try:
                _, contents = contents.split(start_after, 1)
            except ValueError:
                errs.append(
                    f"file fragment: 'start-after' {start_after!r} not found."
                )

        if end_before is not None:
            try:
                contents, _ = contents.split(end_before, 1)
            except ValueError:
                errs.append(
                    f"file fragment: 'end-before' {end_before!r} not found."
                )

        if pattern:
            m = re.search(pattern, contents, re.DOTALL)
            if not m:
                errs.append(f"file fragment: pattern {pattern!r} not found.")
            else:
                try:
                    contents = m.group(1)
                except IndexError:
                    errs.append(
                        "file fragment: pattern matches, but no group "
                        "defined."
                    )

        if errs:
            raise ConfigurationError(errs)

        return cls(contents)

    def render(self) -> str:
        return self._contents


VALID_FRAGMENTS: Iterable[type[Fragment]] = (TextFragment, FileFragment)
