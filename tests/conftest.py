# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import shutil

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import NamedTuple

import pytest


@pytest.fixture(name="plugin_dir", scope="session")
def _plugin_dir():
    """
    Install the plugin into a temporary directory with a random path to
    prevent pip from caching it.

    Copy only the src directory, pyproject.toml, and whatever is needed
    to build ourselves.
    """
    with TemporaryDirectory() as d:
        directory = Path(d, "plugin")
        shutil.copytree(Path.cwd() / "src", directory / "src")
        for fn in [
            "pyproject.toml",
            "AUTHORS.md",
            "CHANGELOG.md",
            "LICENSE.txt",
            "README.md",
        ]:
            shutil.copy(Path.cwd() / fn, directory / fn)

        yield directory.resolve()


class BuildSystem(NamedTuple):
    dist: str
    backend: str


@pytest.fixture(
    name="build_system",
    params=[
        BuildSystem("hatchling", "hatchling.build"),
        BuildSystem("pdm-backend", "pdm.backend"),
    ],
    ids=lambda build_system: build_system.dist,
)
def _build_system(request):
    return request.param


@pytest.fixture(name="new_project")
def _new_project(plugin_dir, build_system, tmp_path, monkeypatch):
    """
    Create, and cd into, a blank new project that is configured to use our
    temporary plugin installation.
    """
    project_dir = tmp_path / "my-app"
    project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        f"""\
[build-system]
requires = [
    "{build_system.dist}",
    "hatch-fancy-pypi-readme @ {plugin_dir.as_uri()}",
]
build-backend = "{build_system.backend}"

[project]
name = "my-app"
version = "1.0"
dynamic = ["readme"]
""",
        encoding="utf-8",
    )

    package_dir = project_dir / "src" / "my_app"
    package_dir.mkdir(parents=True)

    package_root = package_dir / "__init__.py"
    package_root.write_text("")

    monkeypatch.chdir(project_dir)

    return project_dir
