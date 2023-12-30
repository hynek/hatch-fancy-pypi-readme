# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from contextlib import suppress
from typing import Any, NoReturn, TextIO

from hatch_fancy_pypi_readme.exceptions import ConfigurationError

from ._builder import build_text
from ._config import load_and_validate_config


def cli_run(
    pyproject: dict[str, Any], hatch_toml: dict[str, Any], out: TextIO
) -> None:
    """
    Best-effort verify config and print resulting PyPI readme.
    """
    is_dynamic = False
    with suppress(KeyError):
        is_dynamic = "readme" in pyproject["project"]["dynamic"]

    if not is_dynamic:
        _fail("You must add 'readme' to 'project.dynamic'.")

    try:
        if (
            pyproject["tool"]["hatch"]["metadata"]["hooks"][
                "fancy-pypi-readme"
            ]
            and hatch_toml["metadata"]["hooks"]["fancy-pypi-readme"]
        ):
            _fail(
                "Both pyproject.toml and hatch.toml contain "
                "hatch-fancy-pypi-readme configuration."
            )
    except KeyError:
        pass

    try:
        cfg = hatch_toml["metadata"]["hooks"]["fancy-pypi-readme"]
    except KeyError:
        try:
            cfg = pyproject["tool"]["hatch"]["metadata"]["hooks"][
                "fancy-pypi-readme"
            ]
        except KeyError:
            _fail(
                "Missing configuration "
                "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]` in"
                " pyproject.toml or `[metadata.hooks.fancy-pypi-readme]`"
                " in hatch.toml)",
            )

    try:
        config = load_and_validate_config(cfg)
    except ConfigurationError as e:
        _fail(
            "Configuration has errors:\n\n"
            + "\n".join(f"- {msg}" for msg in e.errors),
        )

    print(build_text(config.fragments, config.substitutions, "42.0"), file=out)


def _fail(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)
