# ---------------------------------------------------------------------
# Gufo Err
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------
"""
Human-readable error reporting.

Attributes:
    __version__: Current version.
    HAS_CODE_POSITION: True, if Python interpreter supports
        exact code positions  (Python 3.11+)
"""

# Gufo Labs modules
from .types import (
    ErrorInfo,
    FrameInfo,
    SourceInfo,
    CodePosition,
    Anchor,
)
from .frame import iter_frames, exc_traceback, HAS_CODE_POSITION
from .logger import logger
from .err import Err, err
from .abc.failfast import BaseFailFast
from .abc.middleware import BaseMiddleware

__version__: str = "0.2.0"
