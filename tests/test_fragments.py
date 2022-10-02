# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import secrets

from pathlib import Path

import pytest

from hatch_fancy_pypi_readme._fragments import FileFragment, TextFragment
from hatch_fancy_pypi_readme.exceptions import ConfigurationError


class TestTextFragment:
    def test_ok(self):
        """
        The text that is passed in is rendered without changes.
        """
        text = secrets.token_urlsafe()

        assert text == TextFragment.from_config({"text": text}).render()


@pytest.fixture(name="txt_path")
def _txt_path():
    return Path("tests") / "example_text.md"


@pytest.fixture(name="txt")
def _txt(txt_path):
    return txt_path.read_text()


class TestFileFragment:
    def test_simple_ok(self, txt, txt_path):
        """
        Loading a file works.
        """
        assert (
            txt == FileFragment.from_config({"path": str(txt_path)}).render()
        )

    def test_start_after_ok(self, txt_path):
        """
        Specifying a `start-after` that exists in the file removes it along
        with what comes before.
        """
        assert (
            """This is the *interesting* body!

<!-- but before this -->

Uninteresting Footer
"""
            == FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-after": "<!-- cut after this -->\n\n",
                }
            ).render()
        )

    def test_start_at_ok(self, txt_path):
        """
        Specifying a `start-at` that exists in the file removes everything
        before the string, but not the string itself.
        """
        assert (
            """This is the *interesting* body!

<!-- but before this -->

Uninteresting Footer
"""
            == FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-at": "This is the *interesting* body!",
                }
            ).render()
        )

    def test_end_before_ok(self, txt_path):
        """
        Specifying an `end-before` that exists in the file cuts it off along
        with everything that follows.
        """
        assert (
            """# Boring Header

<!-- cut after this -->

This is the *interesting* body!"""
            == FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "end-before": "\n\n<!-- but before this -->",
                }
            ).render()
        )

    def test_start_end_ok(self, txt_path):
        """
        Specifying existing `start-after` and `end-before` returns exactly
        what's between them.
        """
        assert (
            "This is the *interesting* body!"
            == FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-after": "<!-- cut after this -->\n\n",
                    "end-before": "\n\n<!-- but before this -->",
                }
            ).render()
        )

    def test_start_after_end_before_not_found(self, txt_path):
        """
        If `start-after` and/or `end-before` don't exist, a helpful error is
        raised.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-after": "nope",
                    "end-before": "also nope",
                }
            )

        assert [
            "file fragment: 'start-after' 'nope' not found.",
            "file fragment: 'end-before' 'also nope' not found.",
        ] == ei.value.errors

    def test_start_at_end_before_not_found(self, txt_path):
        """
        If `start-at` and/or `end-before` don't exist, a helpful error is
        raised.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-at": "nope",
                    "end-before": "also nope",
                }
            )

        assert [
            "file fragment: 'start-at' 'nope' not found.",
            "file fragment: 'end-before' 'also nope' not found.",
        ] == ei.value.errors

    def test_start_after_at(self, txt_path):
        """
        If both `start-after` and `start-at` are passed, abort with an error.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "start-after": "cut",
                    "start-at": "cut",
                }
            )

        assert [
            "file fragment: 'start-after' and 'start-at' are mutually "
            "exclusive."
        ] == ei.value.errors

    def test_pattern_no_match(self, txt_path):
        """
        If the pattern doesn't match, a helpful error is raises.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "pattern": r"wtf",
                }
            )

        assert ["file fragment: pattern 'wtf' not found."] == ei.value.errors

    def test_pattern_no_group(self, txt_path):
        """
        If the pattern matches but lacks a group, tell the user.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "pattern": r"Uninteresting",
                }
            )

        assert [
            "file fragment: pattern matches, but no group defined."
        ] == ei.value.errors

    def test_pattern_ok(self, txt_path):
        """
        If the pattern matches and has a group, return it.
        """
        assert (
            "*interesting*"
            == FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "pattern": r"the (.*) body",
                }
            ).render()
        )
