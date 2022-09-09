# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

from dataclasses import dataclass

from hatch_fancy_pypi_readme.exceptions import ConfigurationError


def load_substitutions(config: list[dict[str, str]]) -> list[Substituter]:
    errs = []
    subs = []

    for cfg in config:
        try:
            subs.append(Substituter.from_config(cfg))
        except ConfigurationError as e:
            errs.extend(e.errors)

    if errs:
        raise ConfigurationError([f"substitution: {e}" for e in errs])

    return subs


@dataclass
class Substituter:
    pattern: re.Pattern[str]
    replacement: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Substituter:
        errs = []
        flags = 0

        ignore_case = cfg.get("ignore_case", False)
        if not isinstance(ignore_case, bool):
            errs.append("`ignore_case` must be a bool.")
        if ignore_case:
            flags += re.IGNORECASE

        try:
            pattern = re.compile(cfg["pattern"], flags=flags)
        except KeyError:
            errs.append("missing `pattern` key.")
        except re.error as e:
            errs.append(f"can't compile pattern: {e}")

        try:
            replacement = cfg["replacement"]
        except KeyError:
            errs.append("missing `replacement` key.")

        if errs:
            raise ConfigurationError(errs)

        return cls(pattern, replacement)

    def substitute(self, text: str) -> str:
        return self.pattern.sub(self.replacement, text)
