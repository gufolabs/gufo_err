# ---------------------------------------------------------------------
# Gufo Err: TerseFormatter class
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""TerseFormatter class."""
# Python modules
from typing import Iterable

from ..abc.formatter import BaseFormatter

#  Gufo Err modules
from ..types import ErrorInfo


class TerseFormatter(BaseFormatter):
    """Condensed terse output."""

    def iter_format(self: "TerseFormatter", err: ErrorInfo) -> Iterable[str]:
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
        yield self.traceback_message()
        for fi in self.iter_stack(err):
            if fi.source:
                yield (
                    f'  File "{fi.source.file_name}", '
                    f"line {fi.source.current_line}, in {fi.name}"
                )
                if (
                    fi.source.pos
                    and fi.source.pos.start_line == fi.source.pos.end_line
                ):
                    # Exact position, single line
                    pos = fi.source.pos
                    current_line = fi.source.lines[
                        pos.start_line - fi.source.first_line
                    ]
                    line = current_line.lstrip()
                    yield f"    {line}"
                    # Show caret
                    yield self.get_caret(
                        current_line, pos, 4, len(current_line) - len(line)
                    )
                else:
                    # No position, show current line
                    line = fi.source.lines[
                        fi.source.current_line - fi.source.first_line
                    ].lstrip()
                    yield f"    {line}"
            else:
                yield '  File "<stdin>", line ??? in <module>'
        yield self.get_exception_summary(err.exception)
