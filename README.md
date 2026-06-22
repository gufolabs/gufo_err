# Gufo Err

*Gufo Err is a flexible and robust Python error handling framework.*

[![PyPi version](https://img.shields.io/pypi/v/gufo_err.svg)](https://pypi.python.org/pypi/gufo_err/)
![Downloads](https://img.shields.io/pypi/dw/gufo_err)
![Python Versions](https://img.shields.io/pypi/pyversions/gufo_err)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Build](https://img.shields.io/github/actions/workflow/status/gufolabs/gufo_err/py-tests.yml?branch=master)
[![codecov](https://codecov.io/gh/gufolabs/gufo_err/graph/badge.svg?token=NME8DXFKJN)](https://codecov.io/gh/gufolabs/gufo_err)
![Sponsors](https://img.shields.io/github/sponsors/gufolabs)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
---

**Documentation**: [https://docs.gufolabs.com/gufo_err/](https://docs.gufolabs.com/gufo_err/)

**Source Code**: [https://github.com/gufolabs/gufo_err/](https://github.com/gufolabs/gufo_err/)

---

## Python Error Handling

Errors are in human nature - so any modern software may face errors.  Software may contain errors itself, may be affected by third-party libraries' mistakes, or may weirdly use third-party libraries. Computers, operation systems, and networks also may fail. So proper error handling is the key component to building reliable and robust software.

Proper error handling consists of the stages:

* **Collecting** - we must catch the error for further processing.
* **Reporting** -  we must report the error to the developers to allow them to fix it.
* **Mitigation** - we must restart software if an error is unrecoverable  (fail-fast behavior) or try to fix it on-the-fly.
* **Fixing** - developers should fix the error.

Gufo Err is the final solution for Python exception handling and introduces the middleware-based approach. Middleware uses clean API for stack frame analysis and source code extraction.

## Installation

Install with pip

```shell
pip install gufo-err
```

## Quickstart

### Zero-boilerplate Global Hook
    
Wrap your application entry point in err.setup(catch_all=True). This replaces Python's default sys excepthook, collecting execution frame data, generating deterministic fingerprints, and dispatching formatted tracebacks to your middleware pipeline.
    
``` python
from gufo.err import err

err.setup(
    name="my_service", version="1.0.0",
    catch_all=True, format="extend"  # enables locals + source context
)
    
run_my_application()
```

### Local Scoped Handling
    
Apply the same analysis to specific code blocks without touching the rest of your application flow:
    
``` python
try:
    do_something_critical()
except Exception:
    err.process()  # analyze current stack, fingerprint, and dispatch middleware
    raise          # or recover gracefully
```

### Persisting Crash Reports (Offline Environments)
    
In network infrastructure, standard logs may be ephemeral due to restricted storage or unexpected device shutdowns. Gufo Err persistently stores structured error details to the local filesystem via ErrorInfoMiddleware:
    
```python
from gufo.err import err

err.setup(
    name="router_firmware", version="10.2.1",
    catch_all=True,
    format="extend",                # locals + source code context
    error_info_path="/var/crash"    # persist crash reports to disk
)
```    
    
Every unrecoverable exception creates a file in `/var/crash` containing the fingerprint, traceback, local variables, and exact source lines. Inspect them later via the CLI tool even after the process has died:

List all recorded crashes (fingerprint, exception type, service, timestamp):

``` bash
err list -p /var/crash
Fingerprint                          Exception            Service                   Time

0dc69dd9-85f9-5491-bc06...          NameError: foobar    router_firmware           2
```    

View full traceback and stack frame locals of a specific report  

```bash
err view -p /var/crash <fingerprint>
Error: ...
```

### Sending errors to Sentry (Cloud/SaaS Integration)

For teams requiring centralized error tracking with remote dashboards, Gufo Err seamlessly integrates with sentry_sdk via the SentryMiddleware. It enriches your Sentry events with deep local variables and source code context that standard SDK instrumentation usually misses:

# Install the optional sentry extra
```bash
pip install "gufo-err[sentry]"
```

Set your Sentry DSN (or pass it explicitly):

```bash
export SENTRY_DSN="https://key@sentry.io/project-id"
```

```python
from os import environ

from gufo.err import err
from gufo.err.middleware.sentry import SentryMiddleware

err.setup(
    name="my_service", version="1.0.0",
    catch_all=True, format="extend"
)
err.add_middleware(
    *[SentryMiddleware(environ.get("SENTRY_DSN"))], debug=True
)
```

## Why Gufo Err?
    
Python's standard sys.excepthook is basic by design. Libraries like rich.traceback beautify errors but don't solve production realities: identifying unique bugs in high-traffic systems, debugging stateful failures from afar, and ensuring safe shutdowns. 
    
Gufo Err fills this gap for robust Python services (network infra, long-running daemons, CLI tools) by introducing a structured middleware pipeline for exception analysis.
    
* **Deterministic Bug Fingerprinting** - Every failure gets a stable UUID generated from its stack context and exception type. No more guessing if two identical traces are the same bug or two different edge cases.
* **Stateful Debugging at Zero Cost** — automatic source extraction and local variable capture turn "mystery crashes" into debugable extend format dumps, available even when attaching a debugger is impossible. 
* **Modular Middleware Pipeline** - Route errors to JSON files (ErrorInfoMiddleware), Sentry, or custom logic without touching your business code. Add or swap transport layers in one place.
* **Fail-Fast safety for critical systems** - Built-in fail-fast policies detect unrecoverable states (e.g., corrupted configs/database connections) and force an immediate os._exit() after securely dumping the application state and executing cleanup callbacks, preventing silent data loss or network corruption.
* **Local-first & Zero External Dependencies** - Runs perfectly offline without Sentry accounts or telemetry. Unlike SaaS error trackers, your production systems remain fully deterministic, auditable, and safe even behind restricted firewalls.

 ## Other Features

* **Traceback Serialization/Deserialization:** Serialize ErrorInfo objects for cross-process transfer, inter-process communication, or storage without using JSON directly. Deserialization reconstructs the full exception data structure for offline inspection. 
* **Structured Frame Extraction API:** A clean, standalone API to extract execution frames and local variables from any Python traceback on-demand (useful if you need Gufo Err's state-detection without the middleware pipeline).
* **CLI Analysis Tool (err command):** The `err` CLI provides subcommands to list, view, and clear recorded crash reports directly from the terminal. Allows diagnostics of production crashes even after the process has terminated.

## Comparison with Alternatives

Gufo Err focuses on structured crash data collection for production environments where standard tools leave gaps in debugging, deduplication, and post-mortem analysis. Below is a feature comparison across common Python error handling approaches:

| Feature | **Gufo Err** | **sys.excepthook** | **rich.traceback** | **sentry_sdk** | **loguru** | **better_exceptions** |
| ------------------------------- | --- | --- | --- | --- | --- | --- |
| **Trace formats**               |     |     |     |     |     |     | 
| → Basic                         | ✅  | ✅   | ✅  | ❌  | ✅   | ✅  |
| → Terse                         | ✅  | ❌   | ✅  | ❌  | ✅   | ✅  |
| → Expanded with locals          | ✅  | ❌   | ✅  | ❌  | ❌   | ✅  |
| → Custom                        | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| Colored tracebacks              | ❌  | ❌   | ✅  | ❌  | ❌   | ❌  |
| Error Deduplication             | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| **Error persistence**           |     |     |     |     |     |     | 
| → local                         | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| → self-hosted                   | ❌  | ❌   | ❌  | ✅  | ❌   | ❌  |
| → cloud                         | ❌  | ❌   | ❌  | ✅  | ❌   | ❌  |
| Error processing middleware     | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| Error manipulation API          | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| Fail-fast behavior              | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| **Tools**                       |     |     |     |     |     |     | 
| → CLI analysis tool             | ✅  | ❌   | ❌  | ❌  | ❌   | ❌  |
| → Web UI                        | ❌  | ❌   | ❌  | ✅  | ❌   | ❌  |

* **Trace format** - defines the level of detail

    * `basic` - the standard Python traceback format (just line numbers, file paths and exception messages).
    * `terse` - compact display optimized for readability in terminal output or log files.
    * `expanded with locals` — detailed output showing surrounding source lines plus captured local variables.
    * `custom` - you can plug your own formatting logic into the pipeline.

* **Error persistence** - the ability to persist error traces and query them later without replaying the original process or reading log files. Three deployment modes are possible:
    
    * `local` - traces stored as files on disk. No additional services. No external connections required.
    * `self-hosted` - traces delivered to an on-premises service (e.g. self-hosted Sentry). All data stays on infrastructure you control.
    * `cloud`- traces delivered to a vendor SaaS platform (e.g. hosted Sentry). Data leaves your infrastructure and is managed by the provider.

## On Gufo Stack

This product is a part of [Gufo Stack][Gufo Stack] - the collaborative effort  led by [Gufo Labs][Gufo Labs]. Our goal is to create a robust and flexible set of tools to create network management software and automate routine administration tasks.

To do this, we extract the key technologies that have proven themselves in the [NOC][NOC] and bring them as separate packages. Then we work on API, performance tuning, documentation, and testing. The [NOC][NOC] uses the final result as the external dependencies.

[Gufo Stack][Gufo Stack] makes the [NOC][NOC] better, and this is our primary task. But other products can benefit from [Gufo Stack][Gufo Stack] too. So we believe that our effort will make  the other network management products better.

[Gufo Labs]: https://gufolabs.com/
[Gufo Stack]: https://docs.gufolabs.com/
[NOC]: https://getnoc.com/
[Sentry]: https://sentry.io/
