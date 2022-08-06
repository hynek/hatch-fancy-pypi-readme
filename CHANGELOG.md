# Changelog

All notable changes to this project will be documented in this file.

The format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/) and this project adheres to [*Calendar Versioning*](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is for emergencies when we need to start branches for older releases.

<!-- changelog follows -->

## [22.3.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.2.0...22.3.0) - 2022-08-06

### Added

- Support for Python 3.7.
  While our Python version only applies when building a package, a package is built whenever it is installed.
  This includes *tox* environments.
  *hatch-fancy-pypi-readme* will always *at least* support the same Python version as the latest version of *Hatchling* – *Hatch*'s build backend – does.

  To get this version out, we had to stop dog-fooding *hatch-fancy-pypi-readme*. 😢


## [22.2.0](https://github.com/hynek/hatch-fancy-pypi-readme/compare/22.1.0...22.2.0) - 2022-08-05

### Changed

- We can finally use *hatch-fancy-pypi-readme* for our own ✨fancy✨ PyPI readme!


### Fixed

- Hopefully fixed readmes with emojis on Windows.


## [22.1.0](https://github.com/hynek/hatch-fancy-pypi-readme/tree/22.1.0) - 2022-08-05

### Added

- Initial release.
