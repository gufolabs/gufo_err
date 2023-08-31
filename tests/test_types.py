# ---------------------------------------------------------------------
# Gufo Err: test types
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
import uuid

# Gufo Err modules
from gufo.err import ErrorInfo, FrameInfo, SourceInfo

SAMPLE_STACK = [
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
]


def test_app_top_empty_stack():
    info = ErrorInfo(
        name="unknown",
        version="unknown",
        fingerprint=uuid.uuid4(),
        stack=[],
        exception=ValueError(),
    )
    top = info.get_app_top_frame()
    assert top is None


def test_app_top_no_root_module():
    info = ErrorInfo(
        name="unknown",
        version="unknown",
        fingerprint=uuid.uuid4(),
        stack=SAMPLE_STACK,
        exception=ValueError(),
    )
    top = info.get_app_top_frame()
    assert top == info.stack[0]


def test_app_top_root_module():
    info = ErrorInfo(
        name="unknown",
        version="unknown",
        fingerprint=uuid.uuid4(),
        stack=SAMPLE_STACK,
        exception=ValueError(),
        root_module="tests.sample",
    )
    top = info.get_app_top_frame()
    assert top == info.stack[1]
