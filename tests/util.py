# ---------------------------------------------------------------------
# Gufo Err: testing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from io import StringIO
from logging import StreamHandler
from contextlib import contextmanager
from typing import Generator

# Gufolabs modules
from gufo.err import logger


@contextmanager
def log_capture() -> Generator[StringIO, None, None]:
    buffer = StringIO()
    handler = StreamHandler(buffer)
    logger.addHandler(handler)
    yield buffer
    logger.removeHandler(handler)
