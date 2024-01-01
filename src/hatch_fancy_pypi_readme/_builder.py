# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ._fragments import Fragment
    from ._substitutions import Substituter


def build_text(
    fragments: list[Fragment],
    substitutions: list[Substituter],
    version: str = "",
) -> str:
    """
    Try avoiding breaking the API unnecessarily; it's used directly by
    scikit-build-core.
    """
    text = "".join(f.render() for f in fragments)

    for sub in substitutions:
        text = sub.substitute(text)

    return text.replace("$HFPR_VERSION", version)
