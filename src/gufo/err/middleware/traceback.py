# ---------------------------------------------------------------------
# Gufo Err: Traceback class
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Callable, Iterable, Tuple
from pprint import pformat

# Gufo Labs modules
from ..abc.middleware import BaseMiddleware
from ..types import ErrorInfo, FrameInfo
from ..logger import logger


class TracebackMiddleware(BaseMiddleware):
    SEP = "-" * 79
    MAX_VAR_LEN = 72

    def __init__(self, format: str = "terse") -> None:
        """
        Dump traceback to the `gufo.err` logger.

        Args:
            format: dumping format, one of `terse`, `extend`.

        Examples:
            Implicit initialization of the middleware using
            default `terse` format:

            ```
            from gufo.err import err

            err.setup()
            ```

            Implicit initialization of the middleware using
            explicit `terse` format:

            ```
            from gufo.err import err

            err.setup(format="terse")
            ```

            Implicit initialization of the middleware using
            explicit `extend` format:

            ```
            from gufo.err import err

            err.setup(format="extend")
            ```

            Explicit initialization of the middleware:

            ```
            from gufo.err import err
            from gufo.err.middleware.traceback import TracebackMiddleware

            err.setup(middleware=[TracebackMiddleware(format="extend")])
            ```


        """
        super().__init__()
        try:
            self.format: Callable[[ErrorInfo], Iterable[str]] = getattr(
                self, f"iter_fmt_{format}"
            )
        except AttributeError:
            raise ValueError(f"Invalid format {format}")

    def process(self, info: ErrorInfo) -> None:
        msg = "\n".join(self.format(info))
        logger.error(msg)

    def iter_stack(self, err: ErrorInfo) -> Iterable[FrameInfo]:
        """
        Iterate stack according to direction.

        Args:
            err: ErrorInfo instance.

        Returns:
            Iterable of FrameInfo
        """
        yield from err.stack

    def traceback_message(self) -> str:
        """
        Get proper traceback message.

        Returns:
            String like "Traceback (most resent call last):"
        """
        return "Traceback (most resent call last):"

    def iter_vars(self, fi: FrameInfo) -> Iterable[Tuple[str, str]]:
        """
        Iterate frame variables and convert them to the readable form.

        Args:
            fi: FrameInfo instance

        Returns:
            Iterable of (`var name`, `var value`).
        """
        for k, v in fi.locals.items():
            try:
                rv = repr(v)
                if len(rv) > self.MAX_VAR_LEN:
                    rv = pformat(v)
            except Exception as e:
                rv = f"repr() failed: {e}"
            yield k, rv

    def iter_fmt_terse(self, err: ErrorInfo) -> Iterable[str]:
        yield f"Error: {err.fingerprint}"
        yield self.traceback_message()
        for fi in self.iter_stack(err):
            if fi.source:
                yield (
                    f'  File "{fi.source.file_name}", '
                    f"line {fi.source.current_line}, in {fi.name}"
                )
                line = fi.source.lines[
                    fi.source.current_line - fi.source.first_line
                ].lstrip()
                yield f"    {line}"
            else:
                yield '  File "<stdin>", line ??? in <module>'
        yield f"{err.exception.__class__.__name__}: {str(err.exception)}"

    def iter_fmt_extend(self, err: ErrorInfo) -> Iterable[str]:
        yield f"Error: {err.fingerprint}"
        yield f"{err.exception.__class__.__name__}: {str(err.exception)}"
        yield self.traceback_message()
        for fi in self.iter_stack(err):
            yield self.SEP
            if fi.source:
                yield (
                    f"File: {fi.source.file_name} "
                    f"(line {fi.source.current_line})"
                )
                for n, line in enumerate(
                    fi.source.lines, start=fi.source.first_line
                ):
                    sign = "==>" if n == fi.source.current_line else "   "
                    yield f"{n:5d} {sign} {line}"
            else:
                yield "File: <stdin> (line ???)"
            if fi.locals:
                yield "Locals:"
                for var_name, var_value in self.iter_vars(fi):
                    if len(var_value) > self.MAX_VAR_LEN:
                        yield f"{var_name:>20s} |\n{var_value}"
                    else:
                        yield f"{var_name:>20s} = {var_value}"
        yield self.SEP
