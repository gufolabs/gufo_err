# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

To see unreleased changes, please see the [CHANGELOG on the master branch](https://github.com/gufolabs/gufo_err/blob/master/CHANGELOG.md) guide.

## [Unreleased]

### Added

* Add CITATIONS.cff

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