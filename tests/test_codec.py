# ---------------------------------------------------------------------
# Gufo Err: serde tests
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import datetime
import os
import uuid
from typing import Any, Dict

# Third-party modules
import pytest
from gufo.err.codec import (
    ExceptionStub,
    from_dict,
    from_json,
    to_dict,
    to_json,
)

# Gufo Labs modules
from gufo.err.types import ErrorInfo, FrameInfo, SourceInfo

TZ = datetime.timezone(datetime.timedelta(hours=1), "CEST")

SAMPLE = ErrorInfo(
    name="oops",
    version="1.0",
    fingerprint=uuid.UUID("be8ccd86-3661-434c-8569-40dd65d9860a"),
    exception=RuntimeError("oops"),
    timestamp=datetime.datetime(2022, 3, 22, 7, 21, 29, 215827, tzinfo=TZ),
    root_module="tests",
    stack=[
        FrameInfo(
            name="test_iter_frames",
            module="tests.test_frames",
            source=SourceInfo(
                file_name=os.path.join("tests", "test_frames.py"),
                current_line=125,
                first_line=118,
                lines=[
                    "",
                    "",
                    "def test_iter_frames():",
                    '    """',
                    "    Call the function which raises an exception",
                    '    """',
                    "    try:",
                    "        entry()",
                    '        assert False, "No trace"',
                    "    except RuntimeError:",
                    "        frames = list(iter_frames(exc_traceback()))",
                    "        assert frames == SAMPLE_FRAMES",
                ],
            ),
            locals={},
        ),
        FrameInfo(
            name="entry",
            module="tests.sample.trace",
            source=SourceInfo(
                file_name=os.path.join("tests", "sample", "trace.py"),
                current_line=14,
                first_line=7,
                lines=[
                    "    x += 1",
                    "    oops()",
                    "",
                    "",
                    "def entry():",
                    "    s = 2",
                    "    s += 1",
                    "    to_oops()",
                ],
            ),
            locals={"s": 3},
        ),
        FrameInfo(
            name="to_oops",
            module="tests.sample.trace",
            source=SourceInfo(
                file_name=os.path.join("tests", "sample", "trace.py"),
                current_line=8,
                first_line=1,
                lines=[
                    "def oops():",
                    '    raise RuntimeError("oops")',
                    "",
                    "",
                    "def to_oops():",
                    "    x = 1",
                    "    x += 1",
                    "    oops()",
                    "",
                    "",
                    "def entry():",
                    "    s = 2",
                    "    s += 1",
                    "    to_oops()",
                ],
            ),
            locals={"x": 2},
        ),
        FrameInfo(
            name="oops",
            module="tests.sample.trace",
            source=SourceInfo(
                file_name=os.path.join("tests", "sample", "trace.py"),
                current_line=2,
                first_line=1,
                lines=[
                    "def oops():",
                    '    raise RuntimeError("oops")',
                    "",
                    "",
                    "def to_oops():",
                    "    x = 1",
                    "    x += 1",
                    "    oops()",
                    "",
                ],
            ),
            locals={},
        ),
    ],
)

SAMPLE_DICT: Dict[str, Any] = {
    "$type": "errorinfo",
    "$version": "1.0",
    "fingerprint": "be8ccd86-3661-434c-8569-40dd65d9860a",
    "name": "oops",
    "timestamp": "2022-03-22T07:21:29.215827+01:00",
    "version": "1.0",
    "root_module": "tests",
    "exception": {"class": "RuntimeError", "args": ["oops"]},
    "stack": [
        {
            "name": "test_iter_frames",
            "module": "tests.test_frames",
            "locals": {},
            "source": {
                "file_name": "tests/test_frames.py",
                "current_line": 125,
                "first_line": 118,
                "lines": [
                    "",
                    "",
                    "def test_iter_frames():",
                    '    """',
                    "    Call the function which raises an exception",
                    '    """',
                    "    try:",
                    "        entry()",
                    '        assert False, "No trace"',
                    "    except RuntimeError:",
                    "        frames = list(iter_frames(exc_traceback()))",
                    "        assert frames == SAMPLE_FRAMES",
                ],
            },
        },
        {
            "name": "entry",
            "module": "tests.sample.trace",
            "locals": {"s": 3},
            "source": {
                "file_name": "tests/sample/trace.py",
                "current_line": 14,
                "first_line": 7,
                "lines": [
                    "    x += 1",
                    "    oops()",
                    "",
                    "",
                    "def entry():",
                    "    s = 2",
                    "    s += 1",
                    "    to_oops()",
                ],
            },
        },
        {
            "name": "to_oops",
            "module": "tests.sample.trace",
            "locals": {"x": 2},
            "source": {
                "file_name": "tests/sample/trace.py",
                "current_line": 8,
                "first_line": 1,
                "lines": [
                    "def oops():",
                    '    raise RuntimeError("oops")',
                    "",
                    "",
                    "def to_oops():",
                    "    x = 1",
                    "    x += 1",
                    "    oops()",
                    "",
                    "",
                    "def entry():",
                    "    s = 2",
                    "    s += 1",
                    "    to_oops()",
                ],
            },
        },
        {
            "name": "oops",
            "module": "tests.sample.trace",
            "locals": {},
            "source": {
                "file_name": "tests/sample/trace.py",
                "current_line": 2,
                "first_line": 1,
                "lines": [
                    "def oops():",
                    '    raise RuntimeError("oops")',
                    "",
                    "",
                    "def to_oops():",
                    "    x = 1",
                    "    x += 1",
                    "    oops()",
                    "",
                ],
            },
        },
    ],
}


def test_to_dict():
    out = to_dict(SAMPLE)
    assert out == SAMPLE_DICT


def test_to_json():
    out = to_json(SAMPLE)
    isinstance(out, str)


def test_from_dict():
    out = from_dict(SAMPLE_DICT)
    assert isinstance(out.exception, ExceptionStub)
    assert out.exception.kls == "RuntimeError"
    assert out.exception.args == ("oops",)
    out.exception = SAMPLE.exception
    assert out == SAMPLE


def test_from_json():
    src = to_json(SAMPLE)
    out = from_json(src)
    assert isinstance(out.exception, ExceptionStub)
    assert out.exception.kls == "RuntimeError"
    assert out.exception.args == ("oops",)
    out.exception = SAMPLE.exception
    assert out == SAMPLE


def test_from_dict_no_dict():
    with pytest.raises(ValueError):
        from_dict(None)


def test_from_dict_invalid_type():
    with pytest.raises(ValueError):
        from_dict({"$type": "foobar"})


def test_from_dict_invalid_version():
    with pytest.raises(ValueError):
        from_dict({"$type": "errorinfo", "$version": "-1"})


def test_from_dict_no_exc():
    with pytest.raises(ValueError):
        from_dict({"$type": "errorinfo", "$version": "1.0"})
