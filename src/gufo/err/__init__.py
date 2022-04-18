# ---------------------------------------------------------------------
# Gufo Err
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------
"""
Human-readable error reporting.

Attributes:
    __version__: Current version.
"""

# Gufo Labs modules
from .types import ErrorInfo, FrameInfo, SourceInfo  # noqa
from .frame import iter_frames, exc_traceback  # noqa
from .logger import logger  # noqa
from .err import Err, err  # noqa
from .abc.failfast import BaseFailFast  # noqa
from .abc.middleware import BaseMiddleware  # noqa

__version__: str = "0.2.0"
