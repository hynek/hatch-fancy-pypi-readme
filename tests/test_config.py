# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import pytest

from hatch_fancy_pypi_readme._config import load_and_validate_config
from hatch_fancy_pypi_readme.exceptions import ConfigurationError


class TestValidateConfig:
    @pytest.mark.parametrize(
        "cfg",
        [{"content-type": "text/markdown", "fragments": [{"text": "foo"}]}],
    )
    def test_valid(self, cfg):
        """
        Valid configurations return empty error lists.
        """
        load_and_validate_config(cfg)

    def test_missing_content_type(self):
        """
        Missing content-type is caught.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config({"fragments": [{"text": "foo"}]})

        assert (
            [
                "tool.hatch.metadata.hooks.fancy-pypi-readme."
                "content-type is missing."
            ]
            == ei.value.errors
            == ei.value.args[0]
        )

    def test_wrong_content_type(self):
        """
        Missing content-type is caught.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {"content-type": "text/html", "fragments": [{"text": "foo"}]}
            )

        assert [
            "tool.hatch.metadata.hooks.fancy-pypi-readme.content-type: "
            "'text/html' is not one of ['text/markdown', 'text/x-rst']"
        ] == ei.value.errors


VALID_FOR_FRAG = {"content-type": "text/markdown"}


def cow_add_frag(**kw):
    d = VALID_FOR_FRAG.copy()
    d["fragments"] = [kw]

    return d


class TestValidateConfigFragments:
    def test_empty_fragments(self):
        """
        Empty fragments are caught.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {"content-type": "text/markdown", "fragments": []}
            )

        assert (
            [
                "tool.hatch.metadata.hooks.fancy-pypi-readme.fragments must "
                "not be empty."
            ]
            == ei.value.errors
            == ei.value.args[0]
        )

    def test_missing_fragments(self):
        """
        Missing fragments are caught.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config({"content-type": "text/markdown"})

        assert (
            [
                "tool.hatch.metadata.hooks.fancy-pypi-readme.fragments"
                " is missing."
            ]
            == ei.value.errors
            == ei.value.args[0]
        )

    def test_empty_fragment_dict(self):
        """
        Empty fragment dicts are handled gracefully.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {"content-type": "text/markdown", "fragments": [{}]}
            )

        assert ["Unknown fragment type {}."] == ei.value.errors

    def test_empty_text_fragment(self):
        """
        Text fragments can't be empty.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(cow_add_frag(text=""))

        assert [
            "tool.hatch.metadata.hooks.fancy-pypi-readme.fragments.0.text "
            "must not be empty."
        ] == ei.value.errors

    def test_invalid_fragments(self):
        """
        Invalid fragments are caught.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {
                    "content-type": "text/markdown",
                    "fragments": [
                        {"text": "this is ok"},
                        {"foo": "this is not"},
                        {"bar": "neither is this"},
                    ],
                }
            )

        assert {
            "Unknown fragment type {'foo': 'this is not'}.",
            "Unknown fragment type {'bar': 'neither is this'}.",
        } == set(ei.value.errors)

    def test_fragment_loading_errors(self):
        """
        Errors that happen while loading a fragment are propagated.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {
                    "content-type": "text/markdown",
                    "fragments": [{"path": "yolo"}],
                }
            )

        assert ["Fragment file 'yolo' not found."] == ei.value.errors


VALID_FOR_SUB = {
    "content-type": "text/markdown",
    "fragments": [{"text": "foobar"}],
}


def cow_add_sub(**kw):
    d = VALID_FOR_SUB.copy()
    d["substitutions"] = [kw]

    return d


class TestValidateConfigSubstitutions:
    def test_invalid_substitution(self):
        """
        Invalid substitutions are caught and reported.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                {
                    "content-type": "text/markdown",
                    "fragments": [{"text": "foo"}],
                    "substitutions": [{"foo": "bar"}],
                }
            )

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions"
            ".0.pattern is missing.",
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions"
            ".0.replacement is missing.",
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions.0"
            ".foo: extra field not permitted.",
        } == set(ei.value.errors)

    def test_empty(self):
        """
        Empty dict is not valid.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(cow_add_sub())

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions"
            ".0.pattern is missing.",
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions"
            ".0.replacement is missing.",
        } == set(ei.value.errors)

    def test_ignore_case_not_bool(self):
        """
        Ignore case is either bool or nothing.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                cow_add_sub(
                    pattern="foo", replacement="bar", **{"ignore-case": 42}
                )
            )

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions.0."
            "ignore-case is of wrong type: 42 is not of type 'boolean'"
        } == set(ei.value.errors)

    def test_pattern_no_valid_regexp(self):
        """
        Pattern must be a valid re-regexp.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                cow_add_sub(pattern="foo???", replacement="bar")
            )

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions.0."
            "pattern: 'foo???' is not a valid Python regular expression",
        } == set(ei.value.errors)

    def test_replacement_not_a_string(self):
        """
        Replacements must be strings.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(
                cow_add_sub(pattern="foo", replacement=42)
            )

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions.0."
            "replacement is of wrong type: 42 is not of type 'string'",
        } == set(ei.value.errors)

    def test_substitutions_not_array(self):
        """
        Substitutions key must be a list.
        """
        cfg = VALID_FOR_SUB.copy()
        cfg["substitutions"] = {}

        with pytest.raises(ConfigurationError) as ei:
            load_and_validate_config(cfg)

        assert {
            "tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions is of "
            "wrong type: {} is not of type 'array'"
        } == set(ei.value.errors)
