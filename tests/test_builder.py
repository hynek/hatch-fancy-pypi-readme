# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from hatch_fancy_pypi_readme._builder import build_text
from hatch_fancy_pypi_readme._fragments import TextFragment


class TestBuildText:
    def test_single_text_fragment(self):
        """
        A single text fragment becomes the readme.
        """
        assert "This is the README!" == build_text(
            [TextFragment("This is the README!")]
        )

    def test_multiple_text_fragment(self):
        """
        A multiple text fragment are concatenated without adding any
        characters.
        """
        assert "# Level 1\n\nThis is the README!" == build_text(
            [
                TextFragment("# Level 1\n\n"),
                TextFragment("This is the README!"),
            ]
        )
