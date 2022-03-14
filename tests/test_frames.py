# ---------------------------------------------------------------------
# Gufo Err: iter_frames tests
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os

# Gufo Labs modules
from gufo.err import iter_frames, exc_traceback, SourceInfo, FrameInfo
from tests.sample.trace import entry


cwd = os.getcwd()


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
                "    raise RuntimeError",
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
            file_name=to_full_path("tests", "sample", "trace.py"),
            current_line=2,
            first_line=1,
            lines=[
                "def oops():",
                "    raise RuntimeError",
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
