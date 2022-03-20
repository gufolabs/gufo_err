# ---------------------------------------------------------------------
# Gufo Err: NeverFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Type
from types import TracebackType

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class NeverFailFast(BaseFailFast):
    """
    Never fail-fast. Always returns False,
    so never inflicts fail-fast.
    """

    def must_die(
        self,
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        return False
