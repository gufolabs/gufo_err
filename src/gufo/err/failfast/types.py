# ---------------------------------------------------------------------
# Gufo Err: TypesFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Type, Iterable
from types import TracebackType

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class TypesFailFast(BaseFailFast):
    """
    Fail-fast on the given list of exception types.

    Args:
        types: Iterable of exception types.

    Example:

        ```
        from gufo.err import err
        from gufo.err.types import TypesFailFast

        err.setup(fail_fast=TypesFailFast([RuntimeError, ValueError]))
        ```
    """

    def __init__(self, types: Iterable[Type[Exception]]) -> None:
        super().__init__()
        self.types = set(types)

    def must_die(
        self,
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        return t in self.types
