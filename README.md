# Gufo Labs Err

*Gufo Labs Err is the flexible and robust python error handling framework.*.

[![PyPi version](https://img.shields.io/pypi/v/gufo_err.svg)](https://pypi.python.org/pypi/gufo_loader/)
![Python Versions](https://img.shields.io/pypi/pyversions/gufo_err)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Build](https://img.shields.io/github/workflow/status/gufolabs/gufo_err/Run%20Tests/master)
![Sponsors](https://img.shields.io/github/sponsors/gufolabs)

---

**Documentation**: [https://docs.gufolabs.com/gufo_err/](https://docs.gufolabs.com/gufo_err/)

**Source Code**: [https://github.com/gufolabs/gufo_err/](https://github.com/gufolabs/gufo_err/)

---

## Python Error Handling

Errors are in human nature - so any modern software may face errors. 
Software may contain errors itself, may be affected 
by third-party libraries' mistakes, or may weirdly use 
third-party libraries. Computers, operation systems, and networks also may fail. 
So proper error handling is the key component to building reliable and robust software.

Proper error handling consists of the stages:

* **Collecting** - we must catch the error for further processing.
* **Reporting** - we must log the error.
* **Mitigation** - we must restart software if an error is unrecoverable  (fail-fast behavior) or try to fix it on-fly.
* **Reporting** - we must report the error to the developers to allow them to fix it.
* **Fixing** - developers should fix the error.

Gufo Err is the final solution for Python exception handling and introduces the middleware-based approach. Middleware uses clean API for stack frame analysis and source code extraction.

## Virtues

* Clean API to extract execution frames.
* Global Python exception hook.
* Endless recursion detection  (to be done).
* Local error reporting.
* Configurable fail-fast behavior.
* Configurable error-reporting formats.
* Error fingerprinting.
* Traceback serialization.
* CLI tool for tracebacks analysis.
* Seamless [Sentry][Sentry] integration.

[Sentry]: https://sentry.io/
