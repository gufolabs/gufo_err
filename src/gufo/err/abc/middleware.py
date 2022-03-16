# ---------------------------------------------------------------------
# Gufo Err: BaseResponse class
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# GufoLabs modules
if TYPE_CHECKING:
    from ..types import ErrorInfo
    from ..err import Err


class BaseMiddleware(ABC):
    """
    Abstract base type for error processing middleware.
    Middleware must implement `process` method.
    """

    @abstractmethod
    def process(self, err: "Err", info: "ErrorInfo") -> None:
        """
        Process the error.

        Args:
            err: Err instance, calling the error processing.
            info: ErrorInfo instance with detailed error information.
        """
        ...
