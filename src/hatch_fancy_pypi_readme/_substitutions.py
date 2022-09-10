# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

from dataclasses import dataclass


@dataclass
class Substituter:
    pattern: re.Pattern[str]
    replacement: str

    @classmethod
    def from_config(cls, cfg: dict[str, str]) -> Substituter:
        flags = 0

        ignore_case = cfg.get("ignore-case", False)
        if ignore_case:
            flags += re.IGNORECASE

        pattern = re.compile(cfg["pattern"], flags=flags)
        replacement = cfg["replacement"]

        return cls(pattern, replacement)

    def substitute(self, text: str) -> str:
        return self.pattern.sub(self.replacement, text)
