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


class BaseResponse(ABC):
    """
    Abstract base type for error response. Error responses must
    implement `respond` method. Error responses may include
    debug output, notifications, self-healing actions, and much more.
    """

    @abstractmethod
    def respond(self, err: "Err", info: "ErrorInfo") -> None:
        """
        Respond to the error.

        Args:
            err: Err instance, calling the response.
            info: ErrorInfo instance with detailed error information.
        """
        ...
