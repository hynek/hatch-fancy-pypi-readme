# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from typing import Any, TextIO

from hatch_fancy_pypi_readme.exceptions import ConfigurationError

from ._builder import build_text
from ._config import load_and_validate_config


def cli_run(pyproject: dict[str, Any], out: TextIO) -> None:
    try:
        cfg = pyproject["tool"]["hatch"]["metadata"]["hooks"][
            "fancy-pypi-readme"
        ]
    except KeyError:
        print(
            "Missing configuration "
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]`)",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        config = load_and_validate_config(cfg)
    except ConfigurationError as e:
        print(
            "Configuration has errors:\n\n"
            + "\n".join(f"- {msg}" for msg in e.errors),
            file=sys.stderr,
        )
        sys.exit(1)

    print(build_text(config.fragments), file=out)
