---
hide:
    - navigation
---
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

To see unreleased changes, please see the [CHANGELOG on the master branch](https://github.com/gufolabs/gufo_err/blob/master/CHANGELOG.md) guide.

## [Unreleased]

### Security

* Install security updates during devcontainer build.
* Use python:3.13-slim-trixie as base for devcontainer.

### Infrastructure

* Codecov integration.

## 0.5.0 - 2025-08-27

### Fixed

* Restore previous exception handler on deleting err object

### Added

* Python 3.13 support

### Changed

* Minimal sentry_sdk version is 2.8.0

### Removed

* Python 3.8 support

### Infrastructure

* Move requirements to pyproject.toml
* Move to ruff formatter from black
* mkdocs-material 9.5.44
* mypy 1.13.0
* ruff 0.11.2
* pytest 8.3.3

## 0.4.1 - 2023-12-11

### Added

* Python 3.12 tests.

### Changed

* docs: Fancy home page.
* devcontainer: Use Python 3.12.

## 0.4.0 - 2023-09-01

### Added

* `err` command-line tool.
* `BaseFormatter` abstract base class.
* `TerseFormatter` and `ExtendFormatter` formatters.
* `ErrorInfo` got optional `root_module` field.
* `ErrorInfo.get_top_app_frame()` function.
* `py.typed` file for PEP-561 compatibility
* docs: "Supported standards" page

### Changed

* docs: Code Quality
* Refined docstrigs

### Infrastructure

* Use `actions/checkout@v3`
* Use `actions/cache@v3`
* Use ` pypa/gh-action-pypi-publish@release/v1`
* Project structure tests
* CI workflows tests
* Adopt Ruff
* Coverage 7.3.0
* mypy 1.5.1
* Move `.coveragerc` to `pyproject.toml`
* Move `setup.cfg` to `pyproject.toml`

## 0.3.0 - 2022-11-09

### Added

* Python 3.11 support.
* TracebackMiddleware shows exact problem position on Python 3.11+
* `CodePosition` structure for exact code location (Python 3.11+)
* `SourceInfo` got optional `pos` field.
* Add CITATIONS.cff
* Developer's Common Tasks

### Changed

* Move changelog into the project's root

### Infrastructure

* Use Python 3.11 for devcontainer
* mkdocs-material 8.5.8
* pytest 7.2.0
* Coverage 6.5.0

## 0.2.0 - 2022-04-18

###  Added

* `ErrorInfo` JSON serialization/deserialization.
* ErrorInfoMiddleware to write collected errors to JSON files.
* New Err.setup options:
  
    * `error_info_path`
    * `error_info_compress`

## 0.1.1 - 2022-04-15

### Added

* `__version__` attribute.

## 0.1.0 - 2022-03-22

### 

* Initial release.