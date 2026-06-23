# ---------------------------------------------------------------------
# Gufo Err: NeverFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022-26, Gufo Labs
# ---------------------------------------------------------------------
"""NeverFailFast."""

# Python modules
from types import TracebackType

# Gufo Labs modules
from ..abc.failfast import BaseFailFast


class NeverFailFast(BaseFailFast):
    """Never fail-fast.

    Always returns False, so never inflicts fail-fast.

    Examples:
        ``` py
        err.setup(fail_fast=[NeverFailFast()])
        ```
    """

    def must_die(
        self,
        t: type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """Check if the process must die quickly.

        Always returns False.
        """
        return False
