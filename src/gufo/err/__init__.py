# ---------------------------------------------------------------------
# Gufo Err
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------
"""
Human-readable error reporting.

Attributes:
    __version__: Current version.
    err: Err singletone
    Err: Err class
    HAS_CODE_POSITION: True, if Python interpreter supports
        exact code positions  (Python 3.11+)
"""

# Gufo Labs modules
from .types import (
    ErrorInfo,  # noqa
    FrameInfo,  # noqa
    SourceInfo,  # noqa
    CodePosition,  # noqa
    Anchor,  # noqa
)
from .frame import iter_frames, exc_traceback, HAS_CODE_POSITION  # noqa
from .logger import logger  # noqa
from .err import Err, err  # noqa
from .abc.failfast import BaseFailFast  # noqa
from .abc.middleware import BaseMiddleware  # noqa

__version__: str = "0.2.0"
