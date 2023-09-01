# ---------------------------------------------------------------------
# Gufo Err: TracebackMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""TracebackMiddleware."""

# Gufo Labs modules
from ..abc.middleware import BaseMiddleware
from ..formatter.loader import get_formatter
from ..logger import logger
from ..types import ErrorInfo


class TracebackMiddleware(BaseMiddleware):
    """
    Dump traceback to the `gufo.err` logger.

    Args:
        format: dumping format, one of `terse`, `extend`.

    Raises:
        ValueError: On invalid `format`.

    Examples:
        Implicit initialization of the middleware using
        default `terse` format:

        ``` py
        from gufo.err import err

        err.setup()
        ```

        Implicit initialization of the middleware using
        explicit `terse` format:

        ``` py
        from gufo.err import err

        err.setup(format="terse")
        ```

        Implicit initialization of the middleware using
        explicit `extend` format:

        ``` py
        from gufo.err import err

        err.setup(format="extend")
        ```

        Explicit initialization of the middleware:

        ``` py
        from gufo.err import err
        from gufo.err.middleware.traceback import TracebackMiddleware

        err.setup(middleware=[TracebackMiddleware(format="extend")])
        ```
    """

    def __init__(
        self: "TracebackMiddleware",
        format: str = "terse",
        primary_char: str = "~",
        secondary_char: str = "^",
    ) -> None:
        super().__init__()
        self.formatter = get_formatter(
            format=format,
            primary_char=primary_char,
            secondary_char=secondary_char,
        )

    def process(self: "TracebackMiddleware", info: ErrorInfo) -> None:
        """
        Middleware entrypoint.

        Dumps stack info error log with given stack format.

        Args:
            info: ErrorInfo instance.
        """
        logger.error(self.formatter.format(info))
