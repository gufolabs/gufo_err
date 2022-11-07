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
from .types import ErrorInfo, FrameInfo, SourceInfo, CodePosition  # noqa
from .frame import iter_frames, exc_traceback, HAS_CODE_POSITION  # noqa
from .logger import logger  # noqa
from .err import Err, err  # noqa
from .abc.failfast import BaseFailFast  # noqa
from .abc.middleware import BaseMiddleware  # noqa

__version__: str = "0.2.0"
