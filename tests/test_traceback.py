# ---------------------------------------------------------------------
# Gufo Err: test TracebackMiddleware
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest
import re

# Gufo Labs modules
from gufo.err import Err
from .util import log_capture


def test_invalid_format():
    with pytest.raises(ValueError):
        Err().setup(format="unknownformat")


rx_long = re.compile(r"\|\n", re.MULTILINE)


def test_long_var():
    err = Err().setup(format="extend")
    longvar = {f"key{d}": "x" * 20 for d in range(10)}  # noqa
    try:
        raise RuntimeError("trigger exception")
    except RuntimeError:
        with log_capture() as buffer:
            err.process()
            output = buffer.getvalue()
    assert bool(rx_long.search(output))


def test_repr_failed():
    class FailedRepr(object):
        def __repr__(self):
            raise ValueError("Invalid repr")

    err = Err().setup(format="extend")
    instance = FailedRepr()  # noqa
    try:
        raise RuntimeError("trigger exception")
    except RuntimeError:
        with log_capture() as buffer:
            err.process()
            output = buffer.getvalue()
    assert "instance = repr() failed: Invalid repr" in output


@pytest.mark.parametrize(["fmt"], [("terse",), ("extend",)])
def test_stdin_module(fmt):
    def f():
        raise RuntimeError

    err = Err().setup(format=fmt)
    try:
        eval("f()")
    except Exception:
        with log_capture() as buffer:
            err.process()
            output = buffer.getvalue()
    assert "<stdin>" in output
