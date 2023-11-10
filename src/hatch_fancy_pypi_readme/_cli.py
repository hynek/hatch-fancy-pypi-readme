# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from dataclasses import dataclass
from enum import Enum
from typing import Any, NoReturn, TextIO

from hatch_fancy_pypi_readme.exceptions import ConfigurationError

from ._builder import build_text
from ._config import load_and_validate_config


class Backend(Enum):
    AUTO = "auto"
    HATCHLING = "hatchling"
    PDM_BACKEND = "pdm.backend"


@dataclass
class BackendSettings:
    pyproject_key: str
    use_hatch_toml: bool


_BACKEND_SETTINGS = {
    Backend.HATCHLING: BackendSettings(
        pyproject_key="tool.hatch.metadata.hooks.fancy-pypi-readme",
        use_hatch_toml=True,
    ),
    Backend.PDM_BACKEND: BackendSettings(
        pyproject_key="tool.pdm.build.hooks.fancy-pypi-readme",
        use_hatch_toml=False,
    ),
}


_HATCH_TOML_KEY = "metadata.hooks.fancy-pypi-readme"


def cli_run(
    pyproject: dict[str, Any],
    hatch_toml: dict[str, Any],
    out: TextIO,
    backend: Backend = Backend.AUTO,
) -> None:
    """
    Best-effort verify config and print resulting PyPI readme.
    """
    if backend is Backend.AUTO:
        backend = _dwim_backend(pyproject)
    settings = _BACKEND_SETTINGS[backend]

    if "readme" not in _get_dotted(pyproject, "project.dynamic", ()):
        _fail("You must add 'readme' to 'project.dynamic'.")

    config_data = _get_dotted(pyproject, settings.pyproject_key)
    config_key = settings.pyproject_key
    config_source = f"`[{settings.pyproject_key}]` in pyproject.toml"

    if settings.use_hatch_toml:
        hatch_toml_config = _get_dotted(hatch_toml, _HATCH_TOML_KEY)
        config_source += f" or `[{_HATCH_TOML_KEY}]` in hatch.toml"
        if hatch_toml_config and config_data:
            _fail(
                "Both pyproject.toml and hatch.toml contain "
                "hatch-fancy-pypi-readme configuration."
            )
        if hatch_toml_config is not None:
            config_data = hatch_toml_config
            config_key = _HATCH_TOML_KEY

    if config_data is None:
        _fail(f"Missing configuration ({config_source})")

    try:
        config = load_and_validate_config(config_data, base=f"{config_key}.")
    except ConfigurationError as e:
        _fail(
            "Configuration has errors:\n\n"
            + "\n".join(f"- {msg}" for msg in e.errors),
        )

    print(build_text(config.fragments, config.substitutions), file=out)


def _get_dotted(
    data: dict[str, Any], dotted_key: str, default: Any = None
) -> Any:
    try:
        for key in dotted_key.split("."):
            data = data[key]
    except KeyError:
        return default
    return data


def _dwim_backend(pyproject: dict[str, Any]) -> Backend:
    """Guess backend from pyproject.toml."""
    build_backend = _get_dotted(pyproject, "build-system.build-backend")
    if build_backend == "pdm.backend":
        return Backend.PDM_BACKEND
    return Backend.HATCHLING


def _fail(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)
