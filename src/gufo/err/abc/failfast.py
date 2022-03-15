# ---------------------------------------------------------------------
# Gufo Err: BaseFailFast method
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type
from types import TracebackType

# GufoLabs modules
if TYPE_CHECKING:
    from ..err import Err


class BaseFailFast(ABC):
    """
    Abstract base type for fail-fast behavior. Fail-fast classes
    must implement `must_die` method. When fail-fast check
    decides the error is unrecoverable, it must return `True` value.
    """

    @abstractmethod
    def must_die(
        self,
        err: "Err",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Fail-fast check. Must be overriden in subclasses.

        Args:
            err: Err instance, calling the check.
            t: Exception type. Same as `sys.exc_info()[0]`.
            v: Exception value. Same as `sys.exc_info()[1]`.
            tb: Traceback. Same as `sys.exc_info()[2]`.

        Returns:
            * `True`, if the error is not recoverable and the process
            must be terminated ASAP.
            * `False` to pass to the next check.
        """
        ...
