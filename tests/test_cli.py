# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import sys

from io import StringIO
from pathlib import Path

import pytest

from hatch_fancy_pypi_readme.__main__ import tomllib
from hatch_fancy_pypi_readme._cli import cli_run

from .utils import run


@pytest.fixture(name="pyproject", scope="session")
def _pyproject():
    return tomllib.loads(
        (Path("tests") / "example_pyproject.toml").read_text()
    )


@pytest.fixture(name="empty_pyproject")
def _empty_pyproject():
    return {
        "project": {"dynamic": ["foo", "readme", "bar"]},
        "tool": {"hatch": {"metadata": {"hooks": {"fancy-pypi-readme": {}}}}},
    }


class TestCLIEndToEnd:
    @pytest.mark.usefixtures("new_project")
    def test_missing_config(self):
        """
        Missing configuration is caught and gives helpful advice.

        Run it as it would be run by the user.
        """
        out = run("hatch_fancy_pypi_readme", check=False)

        assert (
            "Missing configuration "
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]`)\n" == out
        )

    def test_ok(self):
        """
        A valid config is rendered.
        """
        out = run("hatch_fancy_pypi_readme", "tests/example_pyproject.toml")

        assert out.startswith("# Level 1 Header")

    def test_ok_redirect(self, tmp_path):
        """
        It's possible to redirect output into a file.
        """
        out = tmp_path / "out.txt"

        assert "" == run(
            "hatch_fancy_pypi_readme",
            "tests/example_pyproject.toml",
            "-o",
            str(out),
        )

        assert out.read_text().startswith("# Level 1 Header")


class TestCLI:
    def test_cli_run_missing_dynamic(self, capfd):
        """
        Missing readme in dynamic is caught and gives helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run({}, sys.stdout)

        out, err = capfd.readouterr()

        assert "You must add 'readme' to 'project.dynamic'.\n" == err
        assert "" == out

    def test_cli_run_missing_config(self, capfd):
        """
        Missing configuration is caught and gives helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run(
                {"project": {"dynamic": ["foo", "readme", "bar"]}}, sys.stdout
            )

        out, err = capfd.readouterr()

        assert (
            "Missing configuration "
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]`)\n" == err
        )
        assert "" == out

    def test_cli_run_config_error(self, capfd, empty_pyproject):
        """
        Configuration errors are detected and give helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run(empty_pyproject, sys.stdout)

        out, err = capfd.readouterr()

        assert (
            "Configuration has errors:\n\n"
            "- Missing tool.hatch.metadata.hooks.fancy-pypi-readme."
            "content-type setting.\n"
            "- Missing tool.hatch.metadata.hooks.fancy-pypi-readme.fragments "
            "setting.\n" == err
        )
        assert "" == out

    def test_cli_run_ok(self, capfd, pyproject):
        """
        Correct configuration gives correct output to the file selected.
        """
        sio = StringIO()

        cli_run(pyproject, sio)

        out, err = capfd.readouterr()

        assert "" == err
        assert "" == out
        assert sio.getvalue().startswith("# Level 1 Header")
