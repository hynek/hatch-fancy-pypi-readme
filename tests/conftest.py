# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys

from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def _clean_pip_cache():
    """
    pip cache needs to be cleaned of ourselves before each test run.

    Otherwise a cached version is used which is highly confusing.

    NB: Needs at least pip 21.3 which is the first one to not fail if there's
    no hatch_fancy_pypi_readme in the cache.
    """
    subprocess.run(
        (
            sys.executable,
            "-m",
            "pip",
            "cache",
            "remove",
            "hatch_fancy_pypi_readme",
        ),
        check=True,
    )


@pytest.fixture(name="project_directory_uri", scope="session")
def _project_directory_uri():
    leading_slashes = "//" if os.sep == "/" else "///"
    return f"file:{leading_slashes}{Path.cwd().as_posix()}"


@pytest.fixture(name="new_project")
def new_project(project_directory_uri, tmp_path, monkeypatch):
    project_dir = tmp_path / "my-app"
    project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        f"""\
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme @ {project_directory_uri}"]
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
