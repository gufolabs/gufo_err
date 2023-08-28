# ---------------------------------------------------------------------
# Gufo Err: ErrorInfoMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""Compressor."""
# Python modules
import os
from typing import Callable, Dict, Optional, Tuple, Type


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

    def __init__(self: "Compressor", format: Optional[str] = None) -> None:
        try:
            self.encode, self.decode = self.FORMATS[format]
        except KeyError as e:
            msg = f"Unsupported format: {format}"
            raise ValueError(msg) from e
        if format is None:
            self.suffix = ""
        else:
            self.suffix = f".{format}"

    @classmethod
    def autodetect(cls: Type["Compressor"], path: str) -> "Compressor":
        """
        Returns Compressor instance for given format.

        Args:
            path: File path

        Returns:
            Compressor instance
        """
        return Compressor(format=cls.get_format(path))

    @classmethod
    def get_format(cls: Type["Compressor"], path: str) -> Optional[str]:
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
        """
        Encoder for `none` format.

        Args:
            data: Input bytes

        Returns:
            data as is.
        """
        return data

    @staticmethod
    def decode_none(data: bytes) -> bytes:
        """
        Decoder for `none` format.

        Args:
            data: Input bytes

        Returns:
            data as is.
        """
        return data

    @staticmethod
    def encode_gz(data: bytes) -> bytes:
        """
        Encoder for `gz` format.

        Args:
            data: Input bytes

        Returns:
            gzipped stream as bytes.
        """
        import gzip

        return gzip.compress(data)

    @staticmethod
    def decode_gz(data: bytes) -> bytes:
        """
        Decoder for `gz` format.

        Args:
            data: gzipped data as bytes.

        Returns:
            Ucompressed bytes.
        """
        import gzip

        return gzip.decompress(data)

    @staticmethod
    def encode_bz2(data: bytes) -> bytes:
        """
        Encoder for `bz2` format.

        Args:
            data: Input bytes

        Returns:
            bzipped stream as bytes.
        """
        import bz2

        return bz2.compress(data)

    @staticmethod
    def decode_bz2(data: bytes) -> bytes:
        """
        Encoder for `bz2` format.

        Args:
            data: bzipped data as bytes.

        Returns:
            Ucompressed bytes.
        """
        import bz2

        return bz2.decompress(data)

    @staticmethod
    def encode_xz(data: bytes) -> bytes:
        """
        Encoder for `xz` format.

        Args:
            data: Input bytes

        Returns:
            xzipped stream as bytes.
        """
        import lzma

        return lzma.compress(data)

    @staticmethod
    def decode_xz(data: bytes) -> bytes:
        """
        Decoder for `xz` format.

        Args:
            data: xzipped data as bytes.

        Returns:
            Ucompressed bytes.
        """
        import lzma

        return lzma.decompress(data)


Compressor.FORMATS = {
    None: (Compressor.encode_none, Compressor.decode_none),
    "gz": (Compressor.encode_gz, Compressor.decode_gz),
    "bz2": (Compressor.encode_bz2, Compressor.decode_bz2),
    "xz": (Compressor.encode_xz, Compressor.decode_xz),
}
