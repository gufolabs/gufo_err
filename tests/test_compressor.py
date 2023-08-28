# ---------------------------------------------------------------------
# Gufo Err: test Compressor
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Labs Modules
from gufo.err.compressor import Compressor


def test_invalid_format():
    with pytest.raises(ValueError):
        Compressor(format="rar")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/a/b/c/xxx.json", None),
        ("/a/b/c/xxx.json.gz", "gz"),
        ("/a/b/c/xxx.json.bz2", "bz2"),
        ("/a/b/c/xxx.json.xz", "xz"),
        ("/a/b/c/xxx.json.rar", None),
    ],
)
def test_get_format(path: str, expected: str) -> None:
    assert Compressor.get_format(path) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/a/b/c/xxx.json", None),
        ("/a/b/c/xxx.json.gz", "gz"),
        ("/a/b/c/xxx.json.bz2", "bz2"),
        ("/a/b/c/xxx.json.xz", "xz"),
        ("/a/b/c/xxx.json.rar", None),
    ],
)
def test_autodetect(path: str, expected: str) -> None:
    c = Compressor.autodetect(path)
    assert isinstance(c, Compressor)
    src = b"12345"
    cdata = c.encode(src)
    assert c.decode(cdata) == src


@pytest.mark.parametrize(
    ("fmt", "data"),
    [
        (None, b"12345"),
        (
            "gz",
            b"12345",
        ),
        (
            "bz2",
            b"12345",
        ),
        (
            "xz",
            b"12345",
        ),
    ],
)
def test_compressor(fmt: str, data: bytes):
    c = Compressor(format=fmt)
    c_data = c.encode(data)
    s_data = c.decode(c_data)
    assert s_data == data
