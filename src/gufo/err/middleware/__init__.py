# ---------------------------------------------------------------------
# Gufo Err: middleware module
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""
Middleware handlers.

Configured middleware handlers are launched on every unhandled exception
and allows to customize an error processing. See
[BaseMiddleware][gufo.err.abc.middleware.BaseMiddleware] for details.

Available out-of-box:

* [ErrorInfoMiddleware][gufo.err.middleware.errorinfo.ErrorInfoMiddleware]:
  Dump errors to JSON files.
* [SentryMiddleware][gufo.err.middleware.sentry.SentryMiddleware]:
  Sentry integration.
* [TracebackMiddleware][gufo.err.middleware.traceback.TracebackMiddleware]:
  Dump traceback to the gufo.err logger.
"""
