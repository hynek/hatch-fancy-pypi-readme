# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

from hatch_fancy_pypi_readme._substitutions import Substituter


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
                "ignore-case": True,
            }
        ).substitute(
            "For information on changes in this release, see the `NEWS <NEWS.rst>`_ file."  # noqa
        )

    @pytest.mark.parametrize(
        "pat,repl,text,expect",
        [
            (
                r"#(\d+)",
                r"[#\1](https://github.com/pydantic/pydantic/issues/\1)",
                "* Foo #4224, #4470 Bar",
                "* Foo [#4224](https://github.com/pydantic/pydantic/issues/"
                "4224), [#4470](https://github.com/pydantic/pydantic/issues/"
                "4470) Bar",
            ),
            (
                r"( +)@([\w\-]+)",
                r"\1[@\2](https://github.com/\2)",
                "foo @github-user bar",
                "foo [@github-user](https://github.com/github-user) bar",
            ),
        ],
    )
    def test_pydantic(self, pat, repl, text, expect):
        """
        Pydantic examples work.
        https://github.com/hynek/hatch-fancy-pypi-readme/issues/9#issuecomment-1238584908
        """
        assert expect == Substituter.from_config(
            {
                "pattern": pat,
                "replacement": repl,
                "ignore-case": True,
            }
        ).substitute(text)
