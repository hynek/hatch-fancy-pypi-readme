# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from typing import Any, NoReturn, TextIO

from hatch_fancy_pypi_readme.exceptions import ConfigurationError

from ._builder import build_text
from ._config import load_and_validate_config


def cli_run(pyproject: dict[str, Any], out: TextIO) -> None:
    """
    Best-effort verify config and print resulting PyPI readme.
    """
    is_dynamic = False
    try:
        is_dynamic = "readme" in pyproject["project"]["dynamic"]
    except KeyError:
        pass

    if not is_dynamic:
        _fail("You must add 'readme' to 'project.dynamic'.")

    try:
        cfg = pyproject["tool"]["hatch"]["metadata"]["hooks"][
            "fancy-pypi-readme"
        ]
    except KeyError:
        _fail(
            "Missing configuration "
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]`)",
        )

    try:
        config = load_and_validate_config(cfg)
    except ConfigurationError as e:
        _fail(
            "Configuration has errors:\n\n"
            + "\n".join(f"- {msg}" for msg in e.errors),
        )

    # This no cover pragma is utter nonsense, because this line gets executed
    # _many_ times.
    print(build_text(config.fragments), file=out)  # pragma: no cover


def _fail(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)
