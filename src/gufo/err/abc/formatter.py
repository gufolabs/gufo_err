# ---------------------------------------------------------------------
# Gufo Err: BaseFormatter class
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""BaseFormatter class."""
# Python modules
from abc import ABC, abstractmethod
from typing import Iterable

# GufoLabs modules
from ..types import CodePosition, ErrorInfo, ExceptionStub, FrameInfo

DEFAULT_PRIMARY_CHAR = "~"
DEFAULT_SECONDARY_CHAR = "^"


class BaseFormatter(ABC):
    """
    Abstract base class for formatters.

    Formatters process [ErrorInfo][gufo.err.ErrorInfo]
    instances and produces human-readable output.

    All formatters must implement `iter_format` method.

    Args:
        primary_char: Caret primary char.
        secondary_char: Caret secondary char.
    """

    def __init__(
        self: "BaseFormatter",
        primary_char: str = DEFAULT_PRIMARY_CHAR,
        secondary_char: str = DEFAULT_SECONDARY_CHAR,
    ) -> None:
        self.primary_char = primary_char
        self.secondary_char = secondary_char

    def format(self: "BaseFormatter", err: ErrorInfo) -> str:
        """
        Format ErrorInfo to human-readable string.

        Args:
            err: ErrorInfo instance

        Returns:
            Human-readable output.
        """
        return "\n".join(self.iter_format(err))

    @abstractmethod
    def iter_format(self: "BaseFormatter", err: ErrorInfo) -> Iterable[str]:
        """
        Iterator yielding human-redable lines.

        Process ErrorInfo instance and yield humar-readable
        lines one-by-one.

        Args:
            err: ErrorInfo instance

        Returns:
            Iterator yieldig formatted lines.
        """

    def traceback_message(self: "BaseFormatter") -> str:
        """
        Get proper traceback message.

        Returns:
            String like "Traceback (most resent call last):"
        """
        return "Traceback (most resent call last):"

    def iter_stack(
        self: "BaseFormatter", err: ErrorInfo
    ) -> Iterable[FrameInfo]:
        """
        Iterate stack according to direction.

        Args:
            err: ErrorInfo instance.

        Returns:
            Iterable of FrameInfo
        """
        yield from err.stack

    def get_caret(
        self: "BaseFormatter",
        line: str,
        pos: CodePosition,
        indent: int,
        dedent: int = 0,
    ) -> str:
        """
        Generate caret for code position.

        Carret has a format:
        ```
        <spaces><primary chars...><secondary chars...><primary chars...>
        ```.

        Args:
            line: Current unstripped line of code
            pos: CodePositio
            indent: Add `indent` leading spaces
            dedent: Remove `indent` leading spaces
        """
        if pos.start_line != pos.end_line:
            msg = "Position must be on single line"
            raise ValueError(msg)
        # Leading spaces
        leading = " " * (pos.start_col + indent - dedent)
        # Parse AST and find anchors
        anchor = pos.anchor
        #
        if not anchor:
            # Fill everything with secondary char
            carret_len = pos.end_col - pos.start_col
            return f"{leading}{self.secondary_char * carret_len}"
        # <primary...><secondary...><primary...>
        prolog = self.primary_char * (anchor.left - pos.start_col)
        middle = self.secondary_char * (anchor.right - anchor.left)
        epilog = self.primary_char * (pos.end_col - anchor.right)
        return f"{leading}{prolog}{middle}{epilog}"

    @staticmethod
    def get_exception_summary(x: BaseException) -> str:
        """
        Format exception to summary string.

        Args:
            x: Exception instance

        Returns:
            Formatted string
        """
        # Class name
        if isinstance(x, ExceptionStub):
            cls_name = x.kls
            info = str(x.args[0]) if x.args else ""
        else:
            cls_name = x.__class__.__name__
            info = str(x)
        # Format result
        if info:
            return f"{cls_name}: {info}"
        return cls_name
