# ---------------------------------------------------------------------
# Gufo Err: Types
# ---------------------------------------------------------------------
# Copyright (C) 2022-26, Gufo Labs
# ---------------------------------------------------------------------
"""Public API data types."""

# Python modules
import datetime
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class Anchor:
    """Exact problem position (Python 3.11+).

    Denotes operator of subscript which causes the problem.

    Args:
        left: Starting column.
        right: Stopping column.
    """

    left: int
    right: int


@dataclass
class CodePosition:
    """Exact code position for Python 3.11+.

    Args:
        start_line: First line of code
        end_line: Last line of code
        start_col: Starting column (on start_line)
        end_col: Ending column (on end_line)
        anchor: Problem anchor
    """

    start_line: int
    end_line: int
    start_col: int
    end_col: int
    anchor: Anchor | None


@dataclass
class SourceInfo:
    """Source context for frame.

    Args:
        file_name: Normalized file name.
        first_line: first line of source context.
        current_line: current execution line.
        lines: List of lines, starting from `first_line`
        pos: Optional exact code position for Python 3.11+
    """

    file_name: str
    first_line: int
    current_line: int
    lines: list[str]
    pos: CodePosition | None = None


@dataclass
class FrameInfo:
    """Execution frame.

    Args:
        name: Current callable name.
        source: Optional `SourceInfo` procedure. May be missing
            on loader problems.
        locals: Dicts of local variables.
        module: Python module name.
    """

    name: str
    source: SourceInfo | None
    locals: dict[str, Any]
    module: str | None = None


@dataclass
class ErrorInfo:
    """Current execution frame information.

    Args:
        name: Application or service name, as set by
            [setup()][gufo.err.Err.setup]
        version: Application or service version, as set by
            [setup()][gufo.err.Err.setup]
        fingerprint: Error fingerprint.
        stack: List of `FrameInfo`. Current execution frame is first.
        exception: Exception instance, if caught.
        timestamp: Error timestamp.
        root_module: Optional root module, as set by
            [setup()][gufo.err.Err.setup]
    """

    name: str
    version: str
    fingerprint: UUID
    stack: list[FrameInfo]
    exception: BaseException
    timestamp: datetime.datetime | None = None
    root_module: str | None = None

    def get_app_top_frame(self) -> FrameInfo | None:
        """Get application's top stack frame.

        Find top stack frame belonging to the application,
        if `root_module` is set, or return stack top otherwise.

        Returns:
            * [FrameInfo][gufo.err.FrameInfo] if the stack is not empty.
            * None otherwise.
        """
        if not self.stack:
            return None
        if self.root_module:
            prefix = f"{self.root_module}."
            for frame in self.stack:
                if frame.module and (
                    frame.module == self.root_module
                    or frame.module.startswith(prefix)
                ):
                    return frame
        return self.stack[0]


class ExceptionStub(Exception):
    """Stub to deserialized exceptions.

    Args:
        kls: Exception class name
        args: Exception arguments
    """

    def __init__(self, kls: str, args: tuple[Any, ...]) -> None:
        self.kls = kls
        self.args = args

    def __str__(self) -> str:
        """Format exception to string.

        Returns:
            Formatted string.
        """
        if not self.args:
            return self.kls
        return f"{self.kls}: {self.args[0]}"
