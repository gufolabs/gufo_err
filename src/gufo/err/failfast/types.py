# ---------------------------------------------------------------------
# Gufo Err: TypesFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""TypesFailFast."""
# Python modules
from types import TracebackType
from typing import Iterable, Type

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class TypesFailFast(BaseFailFast):
    """
    Fail-fast on the given list of exception types.

    Args:
        types: Iterable of exception types.

    Examples:
        ``` py
        from gufo.err import err
        from gufo.err.types import TypesFailFast

        err.setup(fail_fast=[TypesFailFast([RuntimeError, ValueError])])
        ```
    """

    def __init__(
        self: "TypesFailFast", types: Iterable[Type[Exception]]
    ) -> None:
        super().__init__()
        self.types = set(types)

    def must_die(
        self: "TypesFailFast",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Check if the process must die quickly.

        Returns true if the exception type is one of the given types.
        """
        return t in self.types
