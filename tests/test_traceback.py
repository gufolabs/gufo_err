# ---------------------------------------------------------------------
# Gufo Err: test TracebackResponse
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Labs modules
from gufo.err import Err
from .sample.trace import entry


def test_default():
    err = Err().setup(format="extend")
    try:
        entry()
    except Exception:
        err.process()
        assert False
