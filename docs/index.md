---
template: index.html
hide:
    - navigation
    - toc
hero:
    title: Gufo Err
    subtitle: The flexible and robust python error handling framework
    install_button: Getting Started
    source_button: Source Code
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

## Features

* Clean API to extract execution frames.
* Global Python exception hook.
* Endless recursion detection  (to be done).
* Local error reporting.
* Configurable fail-fast behavior.
* Configurable error-reporting formats.
* Error fingerprinting.
* Traceback serialization/deserialization.
* [CLI tool](man/err.md) for tracebacks analysis.
* Seamless [Sentry][Sentry] integration.

## On Gufo Stack

This product is a part of [Gufo Stack][Gufo Stack] - the collaborative effort 
led by [Gufo Labs][Gufo Labs]. Our goal is to create a robust and flexible 
set of tools to create network management software and automate 
routine administration tasks.

To do this, we extract the key technologies that have proven themselves 
in the [NOC][NOC] and bring them as separate packages. Then we work on API,
performance tuning, documentation, and testing. The [NOC][NOC] uses the final result
as the external dependencies.

[Gufo Stack][Gufo Stack] makes the [NOC][NOC] better, and this is our primary task. But other products
can benefit from [Gufo Stack][Gufo Stack] too. So we believe that our effort will make 
the other network management products better.

[Gufo Labs]: https://gufolabs.com/
[Gufo Stack]: https://docs.gufolabs.com/
[NOC]: https://getnoc.com/
[Sentry]: https://sentry.io/