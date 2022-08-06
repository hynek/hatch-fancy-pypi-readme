# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture(scope='session')
def plugin_dir():
    with TemporaryDirectory() as d:
        directory = Path(d, 'plugin')
        shutil.copytree(Path.cwd() / "src", directory / "src")
        for fn in ["pyproject.toml", "README.md", "CHANGELOG.md"]:
            shutil.copy(Path.cwd() / fn, directory / fn)

        yield directory.resolve()


@pytest.fixture(name="new_project")
def new_project(plugin_dir, tmp_path, monkeypatch):
    project_dir = tmp_path / "my-app"
    project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        f"""\
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme @ {plugin_dir.as_uri()}"]
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
