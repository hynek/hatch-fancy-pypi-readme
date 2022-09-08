# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ._fragments import Fragment
from ._substitutions import Substituter


def build_text(
    fragments: list[Fragment], substitutions: list[Substituter]
) -> str:
    rv = []
    for f in fragments:
        rv.append(f.render())

    text = "".join(rv)

    for sub in substitutions:
        text = sub.substitute(text)

    return text
