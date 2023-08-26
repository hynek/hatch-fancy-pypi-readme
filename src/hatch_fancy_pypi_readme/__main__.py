# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import sys

from contextlib import closing
from pathlib import Path
from typing import TextIO

from ._cli import cli_run


if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a README from a pyproject.toml & hatch.toml."
        " If a hatch.toml is passed / detected, it's preferred."
    )
    parser.add_argument(
        "pyproject_path",
        nargs="?",
        metavar="PATH-TO-PYPROJECT.TOML",
        default="pyproject.toml",
        help="Path to the pyproject.toml to use for rendering. "
        "Default: pyproject.toml in current directory.",
    )
    parser.add_argument(
        "--hatch-toml",
        nargs="?",
        metavar="PATH-TO-HATCH.TOML",
        default=None,
        help="Path to an additional hatch.toml to use for rendering. "
        "Default: Auto-detect in the current directory.",
    )
    parser.add_argument(
        "-o",
        help="Target file for output. Default: standard out.",
        metavar="TARGET-FILE-PATH",
    )
    args = parser.parse_args()

    pyproject = tomllib.loads(Path(args.pyproject_path).read_text())
    hatch_toml = _maybe_load_hatch_toml(args.hatch_toml)

    out: TextIO
    out = Path(args.o).open("w") if args.o else sys.stdout  # noqa: SIM115

    with closing(out):
        cli_run(pyproject, hatch_toml, out)


def _maybe_load_hatch_toml(hatch_toml_arg: str | None) -> dict[str, object]:
    """
    If hatch.toml is passed or detected, load it.
    """
    if hatch_toml_arg:
        return tomllib.loads(Path(hatch_toml_arg).read_text())

    if Path("hatch.toml").exists():
        return tomllib.loads(Path("hatch.toml").read_text())

    return {}


if __name__ == "__main__":
    main()
