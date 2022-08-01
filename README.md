# *hatch-fancy-pypi-readme*

*Because your ✨fancy project✨ deserves a ✨fancy PyPI landing page✨.*

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-fancy-pypi-readme.svg)](https://pypi.org/project/hatch-fancy-pypi-readme)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-fancy-pypi-readme.svg)](https://pypi.org/project/hatch-fancy-pypi-readme)
[![License: MIT](https://img.shields.io/badge/license-MIT-C06524)](https://github.com/hynek/hatch-fancy-pypi-readme/blob/main/LICENSE.txt)

*hatch-fancy-pypi-readme* is a [*Hatch*](https://hatch.pypa.io/) metadata plugin for everyone who cares about the first impression of their project’s PyPI landing page.
It allows you to define your PyPI project description[^names] in terms of concatenated fragments that are based on **static strings**, **files**, and most importantly:
**parts of files** defined using **cut-off points** or **regular expressions** (*coming soon*).

[^names]: PyPI project description, PyPI landing page, PyPI readme all refer to the same thing.
    In *setuptools* it's called `long_description` and is the text shown on a project’s PyPI page.

    We refer to it as “readme” because that’s how it’s called in [PEP 621](https://peps.python.org/pep-0621/)-based `pyproject.toml` files.

You want your PyPI readme to be the project readme, but without badges, followed by the license file, and the changelog section for *only the last* release?
You’ve come to the right place!


## Configuration

*hatch-fancy-pypi-readme* is, like *Hatch*, configured in your project’s `pyproject.toml`.

First you have to add *hatch-fancy-pypi-readme* to your `[build-system]`:

```toml
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme"]
build-backend = "hatchling.build"
```

Next you must add a `[tool.hatch.metadata.hooks.fancy-pypi-readme]` section.

Here, you **must** supply a `content-type`.
Usually it’s going to be `text/markdown` or `text/x-rst`.

```toml
[tool.hatch.metadata.hooks.fancy-pypi-readme]
content-type = "text/markdown"
```


### Fragments

Finally, you also **must** supply an *array* of `fragments`.
A fragment is a piece of text that is appended to your readme in the order that it’s specified.

We recommend *TOML*'s [syntactic sugar for arrays of wrapping the array name in double brackets](https://toml.io/en/v1.0.0#array-of-tables) and will use it throughout this documentation.


#### Text

Text fragments consist of a single `text` key and are appended to the readme exactly as you specify them:

```toml
[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
text = "Fragment #1"

[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
text = "Fragment #2"
```

results in:

```
Fragment #1Fragment #2
```

Note that there’s no additional space or empty lines between fragments unless you specify them.


#### File

A file fragment reads a file specified by the `file` key and appends it:

```toml
[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
file = "AUTHORS.md"
```

Additionally it’s possible to cut away parts of the file before appending it:

- **`start-after`** cuts away everything before the string specified.
- **`end-before`** cuts away everything after.
- **`regexp`** **TODO**
- **`fallback`** **TODO**

Both *Markdown* and *reST* have comments (`<!-- this is a Markdown comment -->` and `.. this is a reST comment`) that you can use for invisible markers:

```markdown
# Boring Header

<!-- cut after this -->

This is the *interesting* body!

<!-- but before this -->

Uninteresting Footer
```

together with:

```toml
[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
file = "path.md"
start-after = "<!-- cut after this -->\n\n"
end-before = "\n\n<!-- but before this -->"
```

would append:

```markdown
This is the *interesting* body!
```

to you readme.

Note that you you can insert the same file **multiple times** – each time a different part!

---

For a complete example, please see our [example configuration][example-config].


## CLI Interface

For faster feedback loops, *hatch-fancy-pypi-readme* comes with a CLI interface that takes a `pyproject.toml` file as an argument and renders out the readme that would go into respective package.

Your can run it either as `hatch-fancy-pypi-readme` or `python -m hatch_fancy_pypi_readme`.
If you don’t pass an argument, it looks for a `pyproject.toml` in the current directory.
You can optionally pass a `-o` option to write the output into a file instead of to standard out.

Since *hatch-fancy-pypi-readme* is part of the isolated build system, it shouldn’t be installed along with your projects.
Therefore we recommend running it using [*pipx*](https://pypa.github.io/pipx/):


```shell
pipx run hatch-fancy-pypi-readme
```

---

You can pipe the output into tools like [*rich-cli*](https://github.com/Textualize/rich-cli#markdown) or [*bat*](https://github.com/sharkdp/bat) to verify your markup.

For example, if you run

```shell
$ pipx run hatch-fancy-pypi-readme | pipx run rich-cli --markdown -
```

with our [example configuration][example-config], you will get the following output:

![rich-cli output](https://raw.githubusercontent.com/hynek/hatch-fancy-pypi-readme/main/rich-cli-out.svg)

---

While the execution model is somewhat different from the *Hatch*-Python packaging pipeline, it uses the same configuration validator and text renderer.


## Project Links

- **License**: [MIT](https://choosealicense.com/licenses/mit/)
- **PyPI**: https://pypi.org/project/hatch-fancy-pypi-readme/
- **Source Code**: https://github.com/hynek/hatch-fancy-pypi-readme
- **Documentation**:  https://github.com/hynek/hatch-fancy-pypi-readme#readme
- **Changelog**: https://github.com/hynek/hatch-fancy-pypi-readme/blob/main/CHANGELOG.md
- **Supported Python Versions**: 3.8 and later.
  Please note that this is the requirement for **building** packages and *not* for the packages themselves!

[example-config]: https://github.com/hynek/hatch-fancy-pypi-readme/blob/main/tests/example_pyproject.toml
