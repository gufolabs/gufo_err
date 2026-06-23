# ---------------------------------------------------------------------
# Gufo Err: testing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2022-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
from logging import StreamHandler

# Gufolabs modules
from gufo.err import logger


@contextmanager
def log_capture() -> Generator[StringIO, None, None]:
    buffer = StringIO()
    handler = StreamHandler(buffer)
    logger.addHandler(handler)
    yield buffer
    logger.removeHandler(handler)
