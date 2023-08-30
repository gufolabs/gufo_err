# ---------------------------------------------------------------------
# Gufo Err: AlwaysFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""AlwaysFailFast."""
# Python modules
from types import TracebackType
from typing import Type

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class AlwaysFailFast(BaseFailFast):
    """
    Always fail-fast.

    Trigger fail-fast unconditionally.

    Examples:
        ``` py
        err.setup(fail_fast=[AlwaysFailFast()])
        ```
    """

    def must_die(
        self: "AlwaysFailFast",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Check if the process must die quickly.

        Always returns True.
        """
        return True
