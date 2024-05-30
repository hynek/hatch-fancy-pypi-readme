# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import email.parser

import pytest

from .utils import append, replace, run


def build_project(*args, check=True):
    if not args:
        args = ["-w"]

    return run("build", *args, check=check)


def pyproject(backend, new_project, additional_text):
    append(new_project / "pyproject.toml", additional_text)

    if backend == "setuptools":
        replace(
            new_project / "pyproject.toml",
            {
                "tool.hatch.metadata.hooks.": "tool.",
                "hatchling.build": "setuptools.build_meta",
                "hatchling": "setuptools",
            },
        )


@pytest.mark.slow()
@pytest.mark.parametrize("backend", ("hatchling", "setuptools"))
def test_build(new_project, backend):
    """
    Build a fake project end-to-end and verify wheel contents.
    """
    pyproject(
        backend,
        new_project,
        """
[tool.hatch.metadata.hooks.fancy-pypi-readme]
content-type = "text/markdown"

[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
text = '''# Level 1

Fancy *Markdown*.
'''

[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
text = "---\\nFooter"
""",
    )

    build_project()

    whl = next(new_project.glob("dist/my_app-1.0-*.whl"))
    assert whl.exists()

    run("wheel", "unpack", whl)

    metadata = email.parser.Parser().parsestr(
        (
            new_project / "my_app-1.0" / "my_app-1.0.dist-info" / "METADATA"
        ).read_text()
    )

    assert "text/markdown" == metadata["Description-Content-Type"]
    assert (
        "# Level 1\n\nFancy *Markdown*.\n---\nFooter"
        == metadata.get_payload().strip()
    )


@pytest.mark.slow()
@pytest.mark.parametrize("backend", ("hatchling", "setuptools"))
def test_invalid_config(new_project, backend):
    """
    Missing config makes the build fail with a meaningful error message.
    """
    pyproject(
        backend,
        new_project,
        # If we leave out the config for good, the plugin doesn't get activated.
        "[tool.hatch.metadata.hooks.fancy-pypi-readme]",
    )

    out = build_project(check=False)

    assert "hatch_fancy_pypi_readme.exceptions.ConfigurationError:" in out
    assert ".fancy-pypi-readme.content-type is missing." in out
    assert ".fancy-pypi-readme.fragments is missing." in out
