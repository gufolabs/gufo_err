# ---------------------------------------------------------------------
# Gufo Err: ErrorInfoMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Optional
import os

# Gufo Labs modules
from ..abc.middleware import BaseMiddleware
from ..types import ErrorInfo
from ..logger import logger
from ..codec import to_json
from ..compressor import Compressor


class ErrorInfoMiddleware(BaseMiddleware):
    """
    Dump error to JSON file.

    Args:
        path: Path to directory to write error info.
        compress: Compression algorithm. One of:
            * `None` - do not compress
            * `gz` - GZip
            * `bz2` - BZip2
            * `xz` - LZMA/xz
    """

    def __init__(self, path: str, compress: Optional[str] = None) -> None:
        super().__init__()
        self.path = path
        # Check permissions
        if not os.access(self.path, os.W_OK):
            raise ValueError(f"{path} is not writable")
        self.compressor = Compressor(format=compress)

    def process(self, info: ErrorInfo) -> None:
        # ErrorInfo path
        fn = os.path.join(
            self.path, f"{info.fingerprint}.json{self.compressor.suffix}"
        )
        # Check if path is already exists
        if os.path.exists(fn):
            logger.error(
                "Error %s is already registered. Skipping.", info.fingerprint
            )
            return
        # Write erorr info
        logger.error("Writing error info into %s", fn)
        with open(fn, "wb") as f:
            f.write(self.compressor.encode(to_json(info).encode("utf-8")))
