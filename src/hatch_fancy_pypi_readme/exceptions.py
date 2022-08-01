# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConfigurationError(Exception):
    """
    Configuration is invalid.
    """

    errors: list[str]
