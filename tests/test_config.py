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
                "Missing tool.hatch.metadata.hooks.fancy-pypi-readme."
                "content-type setting."
            ]
            == ei.value.errors
            == ei.value.args[0]
        )

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
                "Missing tool.hatch.metadata.hooks.fancy-pypi-readme.fragments"
                " setting."
            ]
            == ei.value.errors
            == ei.value.args[0]
        )
