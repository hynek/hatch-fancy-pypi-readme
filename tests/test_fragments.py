# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import secrets

from pathlib import Path

import pytest

from hatch_fancy_pypi_readme._fragments import (
    FileFragment,
    TextFragment,
    load_fragments,
)
from hatch_fancy_pypi_readme.exceptions import ConfigurationError


class TestTextFragment:
    def test_cfg_empty_text(self):
        """
        Empty text keys raise a ConfigurationError.
        """
        with pytest.raises(ConfigurationError, match="can't be empty"):
            TextFragment.from_config({"text": ""})

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

    def test_unknown_options(self, txt_path):
        """
        Unknown options are caught and raised at ConfiguratinErrors
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {"path": str(txt_path), "foo": "bar", "baz": "qux"}
            )

        assert [
            "file fragment: unknown option: 'foo'",
            "file fragment: unknown option: 'baz'",
        ] == ei.value.errors

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
            "file fragment: 'end_before' 'also nope' not found.",
        ] == ei.value.errors

    def test_invalid_pattern(self, txt_path):
        """
        re-compilation errors are caught and reported.
        """
        with pytest.raises(ConfigurationError) as ei:
            FileFragment.from_config(
                {
                    "path": str(txt_path),
                    "pattern": r"**",
                }
            )
        assert [
            "file fragment: invalid pattern '**': nothing to repeat at "
            "position 0"
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


class TestLoadFragments:
    def test_invalid_fragment_type(self):
        """
        Invalid fragment types are reported.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_fragments(
                [
                    {"text": "this is ok"},
                    {"foo": "this is not"},
                    {"bar": "neither is this"},
                ]
            )

        assert [
            "Unknown fragment type {'foo': 'this is not'}.",
            "Unknown fragment type {'bar': 'neither is this'}.",
        ] == ei.value.errors

    def test_invalid_config(self):
        """
        If the config of a fragment raiss a Configuration error, collect it and
        raise it at the end.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_fragments(
                [
                    {"text": "this is ok"},
                    {"text": "this is not", "because": "of this"},
                ]
            )

        assert ["text fragment: unknown option: because"] == ei.value.errors
