# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import jsonschema
import pytest

from hatch_fancy_pypi_readme._humanize_validation_errors import (
    errors_to_human_strings,
)


def test_pattern_mismatch():
    """
    We currently don't use the format with other values than .+ -- i.e. not
    empty. It's easiest to write a unit test that ensures it does the correct
    thing for both cases.
    """
    v = jsonschema.Draft202012Validator(
        {"type": "string", "pattern": "foo"},
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )

    with pytest.raises(jsonschema.ValidationError) as ei:
        v.validate("bar")

    assert [
        "tool.hatch.metadata.hooks.fancy-pypi-readme.some-field: 'bar' does "
        "not match 'foo'"
    ] == errors_to_human_strings([ei.value], ("some-field",))
