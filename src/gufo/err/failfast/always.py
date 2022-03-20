# ---------------------------------------------------------------------
# Gufo Err: AlwaysFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Type
from types import TracebackType

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class AlwaysFailFast(BaseFailFast):
    """
    Always fail-fast. Trigger fail-fast unconditionally.
    """

    def must_die(
        self,
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        return True
