# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import os
import shutil

from pathlib import Path

import pytest


@pytest.fixture(name="new_project")
def new_project(tmp_path, monkeypatch):
    plugin_directory = tmp_path / "plugin"
    shutil.copytree(Path.cwd() / "src", plugin_directory / "src")
    for fn in ["pyproject.toml", "README.md", "CHANGELOG.md"]:
        shutil.copy(Path.cwd() / fn, plugin_directory / fn)

    project_dir = tmp_path / "my-app"
    project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        f"""\
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme @ {plugin_directory.as_uri()}"]
build-backend = "hatchling.build"

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
