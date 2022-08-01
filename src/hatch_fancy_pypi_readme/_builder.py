# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ._fragments import Fragment


def build_text(fragments: list[Fragment]) -> str:
    rv = []
    for f in fragments:
        rv.append(f.render())

    return "".join(rv)
