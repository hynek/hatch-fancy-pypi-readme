# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from collections.abc import Mapping
from unittest import mock

import pdm.backend.base
import pdm.backend.config
import pdm.backend.hooks
import pytest

from hatch_fancy_pypi_readme.pdm import FancyReadmeHook


README_CONFIG = {
    "content-type": "text/markdown",
    "fragments": [{"text": "# Level 1 Header\n"}],
}


@pytest.fixture(name="dynamic_metadata")
def _dynamic_metadata():
    return ["readme"]


@pytest.fixture(name="readme_config")
def _readme_config():
    return README_CONFIG


@pytest.fixture(name="pyproject_data")
def _pyproject_data(dynamic_metadata, readme_config):
    data = {
        "project": {
            "name": "my-project",
            "dynamic": dynamic_metadata,
        },
        "tool": {
            "hatch": {
                "metadata": {"hooks": {"fancy-pypi-readme": readme_config}}
            }
        },
    }
    return _remove_null_values(data)


def _remove_null_values(data):
    """Recursively remove any null values from nested mapping."""
    return {
        k: _remove_null_values(v) if isinstance(v, Mapping) else v
        for k, v in data.items()
        if v is not None
    }


@pytest.fixture(name="context")
def _context(pyproject_data, tmp_path):
    config = pdm.backend.config.Config(tmp_path, pyproject_data)
    return mock.Mock(name="Context", config=config)


def test_pdm_build_hook_enabled_true(context):
    hook = FancyReadmeHook()
    assert hook.pdm_build_hook_enabled(context)


@pytest.mark.parametrize(
    ("dynamic_metadata", "readme_config"),
    [
        pytest.param(["readme"], None, id="no fancy-pypi-readme config"),
        pytest.param(None, README_CONFIG, id="static readme"),
        pytest.param(["readme"], "scalar", id="fancy-pypi-readme not a table"),
    ],
)
def test_pdm_build_hook_enabled_false(context):
    hook = FancyReadmeHook()
    assert not hook.pdm_build_hook_enabled(context)


def test_pdm_build_initialize(context):
    FancyReadmeHook().pdm_build_initialize(context)

    metadata = context.config.metadata
    assert "readme" not in metadata.get("dynamic", [])
    assert metadata["readme"]["content-type"] == "text/markdown"
    assert metadata["readme"]["text"] == "# Level 1 Header\n"
