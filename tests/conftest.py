# ---------------------------------------------------------------------
# Gufo Labs: Test configuration
# ---------------------------------------------------------------------
# Copyright (C) 2022-26, Gufo Labs
# See LICENSE.md for details
# ---------------------------------------------------------------------

"""Pytest configuration."""

# Python modules
import sys
from contextlib import suppress


def pytest_sessionfinish(session, exitstatus):
    """Teardown Sentry before Pytest closes log handlers.

    Sentry SDK's atexit handler may try to debug-log while
    shutting down its background worker. If the global logging
    handlers have already been closed by pytest, that triggers::

        ValueError: I/O operation on closed file

    Closing the client explicitly here prevents that atexit path.
    """
    sentry = sys.modules.get("sentry_sdk")
    if not sentry:
        return

    with suppress(Exception):
        client = sentry.get_current_client()
        if hasattr(client, "transport") and client.transport is not None:
            sentry.close()
