# ---------------------------------------------------------------------
# Gufo Err: get_formatter function
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""get_formatter implementation."""
# Gufo Err modules
from ..abc.formatter import (
    DEFAULT_PRIMARY_CHAR,
    DEFAULT_SECONDARY_CHAR,
    BaseFormatter,
)


def get_formatter(
    format: str = "terse",
    *,
    primary_char: str = DEFAULT_PRIMARY_CHAR,
    secondary_char: str = DEFAULT_SECONDARY_CHAR,
) -> BaseFormatter:
    """
    Configure and return formatter instance.

    Args:
        format: Formatter name, one of:
            * `terse`
            * `extend`
        primary_char: Caret primary char.
        secondary_char: Caret secondary char.

    Returns:
        Formatter instance.
    """
    if format == "terse":
        from .terse import TerseFormatter

        return TerseFormatter(
            primary_char=primary_char, secondary_char=secondary_char
        )
    if format == "extend":
        from .extend import ExtendFormatter

        return ExtendFormatter(
            primary_char=primary_char, secondary_char=secondary_char
        )
    msg = f"Invalid formatter: {format}"
    raise ValueError(msg)
