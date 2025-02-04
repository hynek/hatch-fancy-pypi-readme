# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable, Protocol

from .exceptions import ConfigurationError


class Fragment(Protocol):
    key: ClassVar[str]

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment: ...

    def render(self) -> str: ...


@dataclass
class TextFragment:
    """
    A static text fragment.
    """

    key: ClassVar[str] = "text"

    _text: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment:
        text = cfg[cls.key]
        if not text:
            raise ConfigurationError(["Text fragments must not be empty."])

        return cls(text)

    def render(self) -> str:
        return self._text


@dataclass
class FileFragment:
    """
    A static text fragment.
    """

    key: ClassVar[str] = "path"

    _contents: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment:
        path = Path(cfg.pop(cls.key))
        start_after = cfg.pop("start-after", None)
        start_at = cfg.pop("start-at", None)
        end_before = cfg.pop("end-before", None)
        pattern = cfg.pop("pattern", None)

        errs: list[str] = []

        try:
            contents = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise ConfigurationError(
                [f"Fragment file '{path}' not found."]
            ) from None

        if start_after and start_at:
            raise ConfigurationError(
                [
                    "file fragment: 'start-after' and 'start-at' are "
                    "mutually exclusive."
                ]
            )

        if start_after is not None:
            try:
                _, contents = contents.split(start_after, 1)
            except ValueError:
                errs.append(
                    f"file fragment: 'start-after' {start_after!r} not found."
                )
        elif start_at is not None:
            p = contents.find(start_at)
            if p == -1:
                errs.append(
                    f"file fragment: 'start-at' {start_at!r} not found."
                )
            contents = contents[p:]

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
                        "file fragment: pattern matches, but no group defined."
                    )

        if errs:
            raise ConfigurationError(errs)

        return cls(contents)

    def render(self) -> str:
        return self._contents


VALID_FRAGMENTS: Iterable[type[Fragment]] = (TextFragment, FileFragment)
