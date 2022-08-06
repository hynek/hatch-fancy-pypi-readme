# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol
from .exceptions import ConfigurationError


def load_fragments(config: list[dict[str, str]]) -> list[Fragment]:
    """
    Load all fragments from the fragments config list.

    Raise ConfigurationError on unknown or misconfigured ones.
    """
    if not config:
        raise ConfigurationError(
            [
                "tool.hatch.metadata.hooks.fancy-pypi-readme.fragments must "
                "not be empty."
            ]
        )

    frags = []
    errs = []
    for frag_cfg in config:
        for frag in _VALID_FRAGMENTS:
            if frag.key not in frag_cfg:
                continue

            try:
                frags.append(frag.from_config(frag_cfg))
            except ConfigurationError as e:
                errs.extend(e.errors)

            break
        else:
            errs.append(f"Unknown fragment type {frag_cfg!r}.")

    if errs:
        raise ConfigurationError(errs)

    return frags


class Fragment(Protocol):
    key: ClassVar[str]

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

    _text: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Fragment:
        contents = cfg.pop("text")

        if not contents:
            raise ConfigurationError(["text fragment: text can't be empty."])

        if cfg:
            raise ConfigurationError(
                [f"text fragment: unknown option: {o}" for o in cfg.keys()]
            )

        return cls(contents)

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
        path = Path(cfg.pop("path"))
        start_after = cfg.pop("start-after", None)
        end_before = cfg.pop("end-before", None)
        pattern = cfg.pop("pattern", None)

        errs: list[str] = []
        if cfg:
            errs.extend(
                f"file fragment: unknown option: {o!r}" for o in cfg.keys()
            )

        contents = path.read_text(encoding="utf-8")

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
                    f"file fragment: 'end_before' {end_before!r} not found."
                )

        if pattern:
            try:
                m = re.search(pattern, contents, re.DOTALL)
                if not m:
                    errs.append(
                        f"file fragment: pattern {pattern!r} not found."
                    )
                else:
                    try:
                        contents = m.group(1)
                    except IndexError:
                        errs.append(
                            "file fragment: pattern matches, but no group "
                            "defined."
                        )
            except re.error as e:
                errs.append(f"file fragment: invalid pattern {pattern!r}: {e}")

        if errs:
            raise ConfigurationError(errs)

        return cls(contents)

    def render(self) -> str:
        return self._contents


_VALID_FRAGMENTS: Iterable[type[Fragment]] = (TextFragment, FileFragment)
