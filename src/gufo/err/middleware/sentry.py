# ---------------------------------------------------------------------
# Gufo Err: SentryMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, Callable, Generator
from contextvars import ContextVar
from contextlib import contextmanager

# Third-party modules
import sentry_sdk

# Gufo Labs Modules
from ..abc.middleware import BaseMiddleware
from ..types import ErrorInfo


_current_err = ContextVar[Optional[ErrorInfo]]("current_err", default=None)


@contextmanager
def _err_context(info: ErrorInfo) -> Generator[None, None, None]:
    """
    Set __current_err context variable with error info
    and remove it on exit.
    """
    token = _current_err.set(info)
    yield
    _current_err.reset(token)


class SentryMiddleware(BaseMiddleware):
    """
    [Sentry](https://sentry.io/) integration. `SentryMiddleware`
    is the wrapper around sentry_sdk to seamless integration
    into Gufo Err.

    Args:
        dsn: URL of the sentry installation. If not provided,
            use `SENTRY_DSN` envoronment variable.
            Do not send any events if value is not set.
        debug: Turns debug mode on and off.
        release: Set current version explicitly. Sentry
            will try to determine the version automatically
            if not set.
        before_send: The function accepting sentry event
            object and returning modified event object or
            nothing to stop processing.

    Examples:
        To configure the SentryMiddleware:

        ``` py
        from gufo.err import err
        from gufo.err.middleware.sentry import SentryMiddleware

        err.setup()
        err.add_middleware(
            SentryMiddleware("http://127.0.0.1:1000/", debug=True)
        )
        ```
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        debug: bool = False,
        release: Optional[str] = None,
        before_send: Optional[
            Callable[
                [Dict[str, Any], Dict[str, Any]], Optional[Dict[str, Any]]
            ]
        ] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.__user_before_send = before_send
        sentry_sdk.init(
            dsn,
            debug=debug,
            release=release,
            before_send=self.__before_send,
            **kwargs
            # shutdown_timeout=config.sentry.shutdown_timeout,
            # release=version.version,
            # max_breadcrumbs=config.sentry.max_breadcrumbs,
            # default_integrations=config.sentry.default_integrations,
            # before_send=before_send,
        )

    def __before_send(
        self, event: Dict[str, Any], hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Call user-defined `before_send` and add additional
        fingerprint information.

        Args:
            event: Sentry event object.
            hint: Error hints.

        Returns:
            Event object
        """
        # Call user-defined handler
        if (
            self.__user_before_send
            and self.__user_before_send(event, hint) is None
        ):
            return None  # User handler interrupts processing

        if "exc_info" not in hint:
            return event

        exception = hint["exc_info"][1]
        info = _current_err.get()
        event["fingerprint"] = [
            "{{ type }}",
            str(exception),
            str(info.fingerprint) if info else "",
        ]
        return event

    def process(self, info: ErrorInfo) -> None:
        with _err_context(info):
            sentry_sdk.capture_exception()
