# ---------------------------------------------------------------------
# Gufo Err: BaseResponse class
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""BaseMiddleware."""
# Python modules
from abc import ABC, abstractmethod

# GufoLabs modules
from ..types import ErrorInfo


class BaseMiddleware(ABC):
    """
    Abstract base type for error processing middleware.

    Middleware must implement `process` method.
    """

    @abstractmethod
    def process(self: "BaseMiddleware", info: ErrorInfo) -> None:
        """
        Process the error.

        Args:
            info: ErrorInfo instance with detailed error information.
        """
        ...
