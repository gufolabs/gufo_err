# ---------------------------------------------------------------------
# Gufo Err: test TracebackResponse
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
import re
from typing import Any, Dict

# Third-party modules
import pytest

# Gufo Labs modules
from gufo.err import Err

from .sample.trace import entry
from .util import log_capture

RESAMPLE = False  # Change to True to rewrite sample files

rx_file = re.compile(r"^(\s*File:?\s*\"?)(.*/gufo_err)(/.*)$", re.MULTILINE)
rx_repr = re.compile("(= <.*? at 0x)([0-9a-f]+?)(>)", re.MULTILINE)
rx_caret = re.compile(r"\n +~*\^+~*$", re.MULTILINE)


def clean_config(src: str) -> str:
    src = rx_file.sub(r"\1\3", src)
    src = rx_repr.sub(r"\1aaaa\3", src)
    # Remove python 3.11+ caret
    return rx_caret.sub("", src)


def get_sample_path(fmt: str) -> str:
    return os.path.join("tests", "data", "trace", f"{fmt}.txt")


def get_sample(fmt: str) -> str:
    with open(get_sample_path(fmt)) as f:
        return f.read()


def set_sample(fmt: str, sample: str) -> None:
    with open(get_sample_path(fmt), "w") as f:
        f.write(sample)


def test_ci_resample() -> None:
    if RESAMPLE:
        assert "CI" not in os.environ, "RESAMPLE must not be set for CI"


@pytest.mark.parametrize(
    "cfg",
    [
        {},
        {"format": "terse"},
        {"format": "extend"},
    ],
)
def test_format(cfg: Dict[str, Any]) -> None:
    fmt = cfg.get("format", "terse")
    err = Err().setup(**cfg)
    cfg = {}  # Reset local vars
    try:
        entry()
    except Exception:
        with log_capture() as buffer:
            err.process()
            output = buffer.getvalue()
    if RESAMPLE:
        set_sample(fmt, output)
    assert clean_config(output) == clean_config(get_sample(fmt))
