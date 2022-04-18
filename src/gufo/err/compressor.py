# ---------------------------------------------------------------------
# Gufo Err: ErrorInfoMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Tuple, Dict, Callable
import os


class Compressor(object):
    """
    Compressor/decompressor class.
    Use .encode() to compress data and .decode() to decompress.

    Args:
        format: Compression algorithm. One of:

            * `None` - do not compress
            * `gz` - GZip
            * `bz2` - BZip2
            * `xz` - LZMA/xz

    Raises:
        ValueError: If format is not supported.
    """

    FORMATS: Dict[
        Optional[str],
        Tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]],
    ]

    def __init__(self, format: Optional[str] = None) -> None:
        try:
            self.encode, self.decode = self.FORMATS[format]
        except KeyError:
            raise ValueError(f"Unsupported format: {format}")
        if format is None:
            self.suffix = ""
        else:
            self.suffix = f".{format}"

    @classmethod
    def autodetect(cls, path: str) -> "Compressor":
        """
        Returns Compressor instance for given format.

        Args:
            path: File path

        Returns:
            Compressor instance
        """
        return Compressor(format=cls.get_format(path))

    @classmethod
    def get_format(cls, path: str) -> Optional[str]:
        """
        Auto-detect format from path.

        Args:
            path: File path.

        Returns:
            `format` parameter.
        """
        _, ext = os.path.splitext(path)
        if ext.startswith("."):
            fmt = ext[1:]
            if fmt in cls.FORMATS:
                return fmt
        return None

    @staticmethod
    def encode_none(data: bytes) -> bytes:
        return data

    @staticmethod
    def decode_none(data: bytes) -> bytes:
        return data

    @staticmethod
    def encode_gz(data: bytes) -> bytes:
        import gzip

        return gzip.compress(data)

    @staticmethod
    def decode_gz(data: bytes) -> bytes:
        import gzip

        return gzip.decompress(data)

    @staticmethod
    def encode_bz2(data: bytes) -> bytes:
        import bz2

        return bz2.compress(data)

    @staticmethod
    def decode_bz2(data: bytes) -> bytes:
        import bz2

        return bz2.decompress(data)

    @staticmethod
    def encode_xz(data: bytes) -> bytes:
        import lzma

        return lzma.compress(data)

    @staticmethod
    def decode_xz(data: bytes) -> bytes:
        import lzma

        return lzma.decompress(data)


Compressor.FORMATS = {
    None: (Compressor.encode_none, Compressor.decode_none),
    "gz": (Compressor.encode_gz, Compressor.decode_gz),
    "bz2": (Compressor.encode_bz2, Compressor.decode_bz2),
    "xz": (Compressor.encode_xz, Compressor.decode_xz),
}
