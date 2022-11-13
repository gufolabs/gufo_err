# Gufo Err Documentation

*Gufo Err* is the flexible and robust python error handling framework.

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