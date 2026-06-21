# ---------------------------------------------------------------------
# Gufo Err: ErrorInfoMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022-26, Gufo Labs
# ---------------------------------------------------------------------
"""ErrorInfo middleware."""

# Python modules
import os
from pathlib import Path
from typing import Optional, Union

# Gufo Labs modules
from ..abc.middleware import BaseMiddleware
from ..codec import to_json
from ..compressor import Compressor
from ..logger import logger
from ..types import ErrorInfo


class ErrorInfoMiddleware(BaseMiddleware):
    """
    Dump error to JSON file.

    Use `err` tool to manipulate collected files.

    Args:
        path: Path to directory to write error info.
        compress: Compression algorithm. One of:

            * `None` - do not compress
            * `gz` - GZip
            * `bz2` - BZip2
            * `xz` - LZMA/xz

    Raises:
        ValueError: If path is not writable.


    Examples:
        ``` py
        from gufo.err import err

        err.setup(error_info_path="/var/err/", error_info_compress="gz")
        ```
    """

    def __init__(
        self: "ErrorInfoMiddleware",
        path: Union[Path, str],
        compress: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.path = Path(path)
        # Check permissions
        if not os.access(self.path, os.W_OK):
            msg = f"{path} is not writable"
            raise ValueError(msg)
        self.compressor = Compressor(format=compress)

    def process(self: "ErrorInfoMiddleware", info: ErrorInfo) -> None:
        """Middleware entrypoing.

        Args:
            info: ErrorInfo instance.
        """
        # ErrorInfo path
        fn = self.path / f"{info.fingerprint}.json{self.compressor.suffix}"
        try:
            with open(fn, "xb") as fp:
                fp.write(self.compressor.encode(to_json(info).encode()))
        except FileExistsError:
            logger.info("Error %s is already registered", info.fingerprint)
