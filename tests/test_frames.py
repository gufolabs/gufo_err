# ---------------------------------------------------------------------
# Gufo Err: iter_frames tests
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Optional

# Gufo Labs modules
from gufo.err import (
    iter_frames,
    exc_traceback,
    SourceInfo,
    FrameInfo,
    CodePosition,
    HAS_CODE_POSITION,
)
from tests.sample.trace import entry


cwd = os.getcwd()


def MaybeCodePosition(
    *,
    start_line: int,
    end_line: int,
    start_col: int,
    end_col: int,
) -> Optional[CodePosition]:
    if HAS_CODE_POSITION:
        return CodePosition(
            start_line=start_line,
            end_line=end_line,
            start_col=start_col,
            end_col=end_col,
        )
    return None


def to_full_path(*args) -> str:
    """
    Convert relative path to full path
    """
    return os.path.join(cwd, *args)


SAMPLE_FRAMES = [
    FrameInfo(
        name="test_iter_frames",
        module="tests.test_frames",
        source=SourceInfo(
            file_name=to_full_path("tests", "test_frames.py"),
            current_line=162,
            first_line=155,
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
            pos=MaybeCodePosition(
                start_line=162, end_line=162, start_col=8, end_col=15
            ),
        ),
        locals={},
    ),
    FrameInfo(
        name="entry",
        module="tests.sample.trace",
        source=SourceInfo(
            file_name=to_full_path("tests", "sample", "trace.py"),
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
            pos=MaybeCodePosition(
                start_line=14, end_line=14, start_col=4, end_col=13
            ),
        ),
        locals={"s": 3},
    ),
    FrameInfo(
        name="to_oops",
        module="tests.sample.trace",
        source=SourceInfo(
            file_name=to_full_path("tests", "sample", "trace.py"),
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
            pos=MaybeCodePosition(
                start_line=8, end_line=8, start_col=4, end_col=10
            ),
        ),
        locals={"x": 2},
    ),
    FrameInfo(
        name="oops",
        module="tests.sample.trace",
        source=SourceInfo(
            file_name=to_full_path("tests", "sample", "trace.py"),
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
            pos=MaybeCodePosition(
                start_line=2, end_line=2, start_col=4, end_col=30
            ),
        ),
        locals={},
    ),
]


def test_iter_frames():
    """
    Call the function which raises an exception
    """
    try:
        entry()
        assert False, "No trace"
    except RuntimeError:
        frames = list(iter_frames(exc_traceback()))
        assert frames == SAMPLE_FRAMES
