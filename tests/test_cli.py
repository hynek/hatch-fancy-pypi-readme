# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import sys

from io import StringIO
from pathlib import Path

import pytest

from hatch_fancy_pypi_readme.__main__ import _maybe_load_hatch_toml, tomllib
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
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]` in"
            " pyproject.toml or `[metadata.hooks.fancy-pypi-readme]` in"
            " hatch.toml)\n" == out
        )

    def test_ok(self):
        """
        A valid config is rendered.
        """
        out = run("hatch_fancy_pypi_readme", "tests/example_pyproject.toml")

        assert out.startswith("# Level 1 Header")
        assert "1.0.0" not in out

        # Check substitutions
        assert (
            "[GitHub-relative link](https://github.com/hynek/"
            "hatch-fancy-pypi-readme/tree/main/README.md)" in out
        )
        assert (
            "Neat features. [#4](https://github.com/hynek/"
            "hatch-fancy-pypi-readme/issues/4)" in out
        )

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

    def test_empty_explicit_hatch_toml(self, tmp_path):
        """
        Explicit empty hatch.toml is ignored.
        """
        hatch_toml = tmp_path / "hatch.toml"
        hatch_toml.write_text("")

        assert run(
            "hatch_fancy_pypi_readme",
            "tests/example_pyproject.toml",
            f"--hatch-toml={hatch_toml.resolve()}",
        ).startswith("# Level 1 Header")

    def test_config_in_hatch_toml(self, tmp_path, monkeypatch):
        """
        Implicit empty hatch.toml is used.
        """
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """\
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme"]
build-backend = "hatchling.build"

[project]
name = "my-pkg"
version = "1.0"
dynamic = ["readme"]
"""
        )
        hatch_toml = tmp_path / "hatch.toml"
        hatch_toml.write_text(
            """\
[metadata.hooks.fancy-pypi-readme]
content-type = "text/markdown"

[[metadata.hooks.fancy-pypi-readme.fragments]]
text = '# Level 1 Header'
"""
        )

        monkeypatch.chdir(tmp_path)

        assert run("hatch_fancy_pypi_readme").startswith("# Level 1 Header")


class TestCLI:
    def test_cli_run_missing_dynamic(self, capfd):
        """
        Missing readme in dynamic is caught and gives helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run({}, {}, sys.stdout)

        out, err = capfd.readouterr()

        assert "You must add 'readme' to 'project.dynamic'.\n" == err
        assert "" == out

    def test_cli_run_missing_config(self, capfd):
        """
        Missing configuration is caught and gives helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run(
                {"project": {"dynamic": ["foo", "readme", "bar"]}},
                {},
                sys.stdout,
            )

        out, err = capfd.readouterr()

        assert (
            "Missing configuration "
            "(`[tool.hatch.metadata.hooks.fancy-pypi-readme]` in"
            " pyproject.toml or `[metadata.hooks.fancy-pypi-readme]` in"
            " hatch.toml)\n" == err
        )
        assert "" == out

    def test_cli_run_two_configs(self, capfd):
        """
        Ambiguous two configs.
        """
        meta = {
            "metadata": {
                "hooks": {
                    "fancy-pypi-readme": {"content-type": "text/markdown"}
                }
            }
        }
        with pytest.raises(SystemExit):
            cli_run(
                {
                    "project": {
                        "dynamic": ["foo", "readme", "bar"],
                    },
                    "tool": {"hatch": meta},
                },
                meta,
                sys.stdout,
            )

        out, err = capfd.readouterr()

        assert (
            "Both pyproject.toml and hatch.toml contain "
            "hatch-fancy-pypi-readme configuration.\n" == err
        )
        assert "" == out

    def test_cli_run_config_error(self, capfd, empty_pyproject):
        """
        Configuration errors are detected and give helpful advice.
        """
        with pytest.raises(SystemExit):
            cli_run(empty_pyproject, {}, sys.stdout)

        out, err = capfd.readouterr()

        assert (
            "Configuration has errors:\n\n"
            "- tool.hatch.metadata.hooks.fancy-pypi-readme."
            "content-type is missing.\n"
            "- tool.hatch.metadata.hooks.fancy-pypi-readme.fragments "
            "is missing.\n" == err
        )
        assert "" == out

    def test_cli_run_ok(self, capfd, pyproject):
        """
        Correct configuration gives correct output to the file selected.
        """
        sio = StringIO()

        cli_run(pyproject, {}, sio)

        out, err = capfd.readouterr()

        assert "" == err
        assert "" == out
        assert sio.getvalue().startswith("# Level 1 Header")


class TestMaybeLoadHatchToml:
    def test_none(self, tmp_path, monkeypatch):
        """
        If nothing is passed and not hatch.toml is found, return empty dict.
        """
        monkeypatch.chdir(tmp_path)

        assert {} == _maybe_load_hatch_toml(None)

    def test_explicit(self, tmp_path, monkeypatch):
        """
        If one is passed, return its parsed content and ignore files called
        hatch.toml.
        """
        monkeypatch.chdir(tmp_path)

        hatch_toml = tmp_path / "hatch.toml"
        hatch_toml.write_text("gibberish")

        not_hatch_toml = tmp_path / "not-hatch.toml"
        not_hatch_toml.write_text("[foo]\nbar='qux'")

        assert {"foo": {"bar": "qux"}} == _maybe_load_hatch_toml(
            str(not_hatch_toml)
        )

    def test_implicit(self, tmp_path, monkeypatch):
        """
        If none is passed, but a hatch.toml is present in current dir, parse
        it.
        """
        monkeypatch.chdir(tmp_path)

        hatch_toml = tmp_path / "hatch.toml"
        hatch_toml.write_text("[foo]\nbar='qux'")

        assert {"foo": {"bar": "qux"}} == _maybe_load_hatch_toml(None)
