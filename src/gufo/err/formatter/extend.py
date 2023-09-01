# ---------------------------------------------------------------------
# Gufo Err: ExtendFormatter class
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""ExtendFormatter."""
# Python modules
from pprint import pformat
from typing import Iterable, Tuple

# Gufo Err modules
from ..abc.formatter import BaseFormatter
from ..types import ErrorInfo, FrameInfo


class ExtendFormatter(BaseFormatter):
    """
    Extended output.

    Produces extended output with code surroundings
    and variable values.
    """

    SEP = "-" * 79
    MAX_VAR_LEN = 72

    def iter_format(self: "ExtendFormatter", err: ErrorInfo) -> Iterable[str]:
        """
        Iterator yielding human-redable lines.

        Process ErrorInfo instance and yield humar-readable
        lines one-by-one.

        Args:
            err: ErrorInfo instance

        Returns:
            Iterator yieldig formatted lines.
        """
        yield f"Error: {err.fingerprint}"
        yield self.get_exception_summary(err.exception)
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
                    if (
                        n == fi.source.current_line
                        and fi.source.pos
                        and fi.source.pos.start_line == fi.source.pos.end_line
                    ):
                        # Show caret
                        yield self.get_caret(line, fi.source.pos, 10)
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

    def iter_vars(
        self: "ExtendFormatter", fi: FrameInfo
    ) -> Iterable[Tuple[str, str]]:
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
            except Exception as e:  # noqa: BLE001
                rv = f"repr() failed: {e}"
            yield k, rv
