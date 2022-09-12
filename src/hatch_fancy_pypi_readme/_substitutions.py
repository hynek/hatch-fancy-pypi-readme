# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import cast

from hatch_fancy_pypi_readme.exceptions import ConfigurationError


@dataclass
class Substituter:
    pattern: re.Pattern[str]
    replacement: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Substituter:
        errs = []
        flags = 0

        ignore_case = cfg.get("ignore-case", False)
        if not isinstance(ignore_case, bool):
            errs.append(
                f"Value {ignore_case!r} for 'ignore-case' is not a bool."
            )

        if ignore_case:
            flags += re.IGNORECASE

        try:
            pattern = re.compile(cfg["pattern"], flags=flags)
        except KeyError:
            errs.append(f"Substitution {cfg} is missing a 'pattern' key.")
        except re.error as e:
            errs.append(
                f"{cfg['pattern']!r} is not a valid regular expression: {e}"
            )

        replacement = cfg.get("replacement")
        if replacement is None:
            errs.append(f"Substitution {cfg} is missing a 'replacement' key.")
        elif not isinstance(replacement, str):
            errs.append(f"Replacement value {replacement!r} is not a string.")

        if errs:
            raise ConfigurationError(errs)

        return cls(pattern, cast(str, replacement))

    def substitute(self, text: str) -> str:
        return self.pattern.sub(self.replacement, text)
