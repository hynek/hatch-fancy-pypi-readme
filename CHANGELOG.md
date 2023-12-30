# Changelog

All notable changes to this project will be documented in this file.

The format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/) and this project adheres to [*Calendar Versioning*](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is for emergencies when we need to start branches for older releases.

<!-- changelog follows -->


## [Unreleased](https://github.com/hynek/hatch-fancy-pypi-readme/compare/23.1.0...HEAD)

### Added

- `$HFPR_VERSION` is now replaced by the package version in the PyPI readme.
  The version is not available in CLI mode, therefore it's replaced by the dummy value of `42.0`.
  [#39](https://github.com/hynek/hatch-fancy-pypi-readme/pull/39)


## [23.1.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.8.0...23.1.0) - 2023-05-22

### Added

- CLI support for `hatch.toml`.
  [#27](https://github.com/hynek/hatch-fancy-pypi-readme/issues/27)


## [22.8.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.7.0...22.8.0) - 2022-10-02

### Added

- Added `start-at` in addition to `start-after` that preserves the string that is looked for. This often removes the need for adding markers because you can define the starting point using a heading that becomes part of the fragment.

   For example: `start-at = "## License"` gives you `## License` and everything that follows.
   [#16](https://github.com/hynek/hatch-fancy-pypi-readme/issues/16)


## [22.7.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.6.0...22.7.0) - 2022-09-12

### Changed

- Removed another circular dependency: this time the wonderful [*jsonschema*](https://python-jsonschema.readthedocs.io/).
  The price of building packaging tools is to not use packages.


## [22.6.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.5.0...22.6.0) - 2022-09-11

### Changed

- Unfortunately, life is unfair and depending on oneself is problematic for others packaging your code.
  So absolutely nothing changed again, except that we’re back to a boring PyPI readme so you don’t have to.


## [22.5.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.4.0...22.5.0) - 2022-09-10

### Changed

- Absolutely nothing – just working around the hen-egg problem to use substitutions in the PyPI readme!


## [22.4.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.3.0...22.4.0) - 2022-09-10

### Added

- It is now possible to run *regular expression*-based substitutions over the final readme.
  [#9](https://github.com/hynek/hatch-fancy-pypi-readme/issues/9)
  [#11](https://github.com/hynek/hatch-fancy-pypi-readme/issues/11)


## [22.3.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.2.0...22.3.0) - 2022-08-06

### Added

- Support for Python 3.7.
  While our Python version only applies when building a package, a package is built whenever it is installed.
  This includes *tox* environments.
  *hatch-fancy-pypi-readme* will always *at least* support the same Python version as the latest version of *Hatchling* – *Hatch*’s build backend – does.

  To get this version out, we had to stop dog-fooding *hatch-fancy-pypi-readme*. 😢


## [22.2.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.1.0...22.2.0) - 2022-08-05

### Changed

- We can finally use *hatch-fancy-pypi-readme* for our own ✨fancy✨ PyPI readme!


### Fixed

- Hopefully fixed readmes with emojis on Windows.


## [22.1.0](https://github.com/hynek/hatch-fancy-pypi-readme/tree/22.1.0) - 2022-08-05

### Added

- Initial release.
