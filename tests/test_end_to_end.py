# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import email.parser

import pytest

from .utils import append, run


def build_project(*args, check=True):
    if not args:
        args = ["-w"]

    return run("build", *args, check=check)


@pytest.mark.slow
def test_build(new_project):
    """
    Build a fake project end-to-end and verify wheel contents.
    """
    append(
        new_project / "pyproject.toml",
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

    whl = new_project / "dist" / "my_app-1.0-py2.py3-none-any.whl"

    assert whl.exists()

    run("wheel", "unpack", whl)

    metadata = email.parser.Parser().parsestr(
        (
            new_project / "my_app-1.0" / "my_app-1.0.dist-info" / "METADATA"
        ).read_text()
    )

    assert "text/markdown" == metadata["Description-Content-Type"]
    assert (
        "# Level 1\n\nFancy *Markdown*.\n---\nFooter" == metadata.get_payload()
    )


@pytest.mark.slow
def test_invalid_config(new_project):
    """
    Missing config makes the build fail with a meaningful error message.
    """
    pyp = new_project / "pyproject.toml"

    # If we leave out the config for good, the plugin doesn't get activated.
    pyp.write_text(
        pyp.read_text() + "[tool.hatch.metadata.hooks.fancy-pypi-readme]"
    )

    out = build_project(check=False)

    assert "hatch_fancy_pypi_readme.exceptions.ConfigurationError:" in out
    assert (
        "Missing tool.hatch.metadata.hooks.fancy-pypi-readme.content-type "
        "setting." in out
    )
    assert (
        "Missing tool.hatch.metadata.hooks.fancy-pypi-readme.fragments "
        "setting." in out
    )
