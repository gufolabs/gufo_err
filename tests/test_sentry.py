# ---------------------------------------------------------------------
# Gufo Err: SentryMiddleware tests
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Labs modules
from gufo.err import Err
from gufo.err.middleware.sentry import SentryMiddleware


def test_sentry_middleware():
    # Configure sentry without URL
    err = Err().setup(
        middleware=[
            SentryMiddleware("http://public@127.0.0.1:9999/1", debug=True)
        ]
    )
    # Without __before_send
    try:
        raise RuntimeError()
    except RuntimeError:
        err.process()


def test_sentry_middleware_skip_before_send():
    # Configure sentry without URL
    err = Err().setup(
        middleware=[
            SentryMiddleware(
                "http://public@127.0.0.1:9999/1",
                debug=True,
                before_send=lambda _event, _hint: None,
            )
        ]
    )
    # Without __before_send
    try:
        raise RuntimeError()
    except RuntimeError:
        err.process()
