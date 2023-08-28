# ---------------------------------------------------------------------
# Gufo Err: test ErrorInfoMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import re

import pytest

# Gufo Labs modules
from gufo.err import Err
from gufo.err.codec import from_json
from gufo.err.compressor import Compressor

from .util import log_capture

rx_log_path = re.compile(r"Writing error info into (\S+)")


def test_unwritable_path():
    with pytest.raises(ValueError):
        Err().setup(error_info_path="/a/b/c/d")


def test_invalid_compress(tmpdir):
    with pytest.raises(ValueError):
        Err().setup(
            error_info_path=tmpdir.mkdir("errinfo"), error_info_compress="rar"
        )


@pytest.mark.parametrize("compress", [None, "gz", "bz2", "xz"])
def test_compress(tmpdir, compress):
    err_info_path = tmpdir.mkdir("errinfo")
    # Setup
    err = Err().setup(
        format=None,
        error_info_path=err_info_path,
        error_info_compress=compress,
    )
    # Generate error
    try:
        msg = "oops"
        raise RuntimeError(msg)
    except RuntimeError:
        with log_capture() as buffer:
            err.process()
            output = buffer.getvalue()
    # Check error info
    match = rx_log_path.search(output)
    assert match
    ei_file = match.group(1)
    if compress is None:
        assert ei_file.endswith(".json")
    else:
        assert ei_file.endswith(f".json.{compress}")
    # Check crashinfo is written
    assert len(err_info_path.listdir()) == 1
    ei_path = err_info_path.listdir()[0]
    # Compare to logged
    assert ei_path == ei_file
    # Check compressor suffix
    compressor = Compressor(format=compress)
    assert ei_file.endswith(compressor.suffix)
    # Try to read file
    with open(ei_path, "rb") as f:
        data = compressor.decode(f.read()).decode("utf-8")
    ei = from_json(data)
    # Check error info
    fn = f"{ei.fingerprint}.json{compressor.suffix}"
    assert ei_file.endswith(fn)


@pytest.mark.parametrize("compress", [None, "gz", "bz2", "xz"])
def test_seen(tmpdir, compress):
    err_info_path = tmpdir.mkdir("errinfo")
    # Setup
    err = Err().setup(
        format=None,
        error_info_path=err_info_path,
        error_info_compress=compress,
    )
    # Generate error
    try:
        msg = "oops"
        raise RuntimeError(msg)
    except RuntimeError:
        with log_capture() as buffer:
            err.process()
            err.process()  # Must seen the error
            output = buffer.getvalue()
    # Check error info
    assert "is already registered" in output
