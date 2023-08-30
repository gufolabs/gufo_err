# ---------------------------------------------------------------------
# Gufo Err: NeverFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""NeverFailFast."""
# Python modules
from types import TracebackType
from typing import Type

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class NeverFailFast(BaseFailFast):
    """
    Never fail-fast.

    Always returns False, so never inflicts fail-fast.

    Examples:
        ``` py
        err.setup(fail_fast=[NeverFailFast()])
        ```
    """

    def must_die(
        self: "NeverFailFast",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Check if the process must die quickly.

        Always returns False.
        """
        return False
