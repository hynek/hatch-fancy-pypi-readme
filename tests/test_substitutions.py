# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

from hatch_fancy_pypi_readme._substitutions import (
    Substituter,
    load_substitutions,
)
from hatch_fancy_pypi_readme.exceptions import ConfigurationError


class TestLoadSubstitutions:
    def test_empty(self):
        """
        Having no substitutions is fine.
        """
        assert [] == load_substitutions([])

    def test_error(self):
        """
        Invalid substitutions are caught and reported.
        """
        with pytest.raises(ConfigurationError) as ei:
            load_substitutions([{"in": "valid"}])

        assert [
            "substitution: missing `pattern` key.",
            "substitution: missing `replacement` key.",
        ] == ei.value.errors


VALID = {"pattern": "f(o)o", "replacement": r"bar\g<1>bar"}


def cow_valid(**kw):
    d = VALID.copy()
    d.update(**kw)

    return d


class TestSubstituter:
    def test_ok(self):
        """
        Valid pattern leads to correct behavior.
        """
        sub = Substituter.from_config(VALID)

        assert "xxx barobar yyy" == sub.substitute("xxx foo yyy")

    @pytest.mark.parametrize(
        "cfg, errs",
        [
            ({}, ["missing `pattern` key.", "missing `replacement` key."]),
            (cow_valid(ignore_case=42), ["`ignore_case` must be a bool."]),
            (
                cow_valid(pattern="???"),
                ["can't compile pattern: nothing to repeat at position 0"],
            ),
        ],
    )
    def test_catches_all_errors(self, cfg, errs):
        """
        All errors are caught and reported.
        """
        with pytest.raises(ConfigurationError) as ei:
            Substituter.from_config(cfg)

        assert errs == ei.value.errors

    def test_twisted(self):
        """
        Twisted example works.

        https://github.com/twisted/twisted/blob/eda9d29dc7fe34e7b207781e5674dc92f798bffe/setup.py#L19-L24
        """
        assert (
            "For information on changes in this release, see the `NEWS <https://github.com/twisted/twisted/blob/trunk/NEWS.rst>`_ file."  # noqa
        ) == Substituter.from_config(
            {
                "pattern": r"`([^`]+)\s+<(?!https?://)([^>]+)>`_",
                "replacement": r"`\1 <https://github.com/twisted/twisted/blob/trunk/\2>`_",  # noqa
                "ignore_case": True,
            }
        ).substitute(
            "For information on changes in this release, see the `NEWS <NEWS.rst>`_ file."  # noqa
        )
