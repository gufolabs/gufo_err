# ---------------------------------------------------------------------
# Gufo Err: iter_frames tests
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Optional

# Gufo Labs modules
from gufo.err import (
    HAS_CODE_POSITION,
    Anchor,
    CodePosition,
    FrameInfo,
    SourceInfo,
    exc_traceback,
    iter_frames,
)

from tests.sample.trace import entry

cwd = os.getcwd()


def MaybeCodePosition(
    *,
    start_line: int,
    end_line: int,
    start_col: int,
    end_col: int,
    anchor_left: Optional[int] = None,
    anchor_right: Optional[int] = None,
) -> Optional[CodePosition]:
    if HAS_CODE_POSITION:
        if anchor_left is None or anchor_right is None:
            anchor = None
        else:
            anchor = Anchor(left=anchor_left, right=anchor_right)
        return CodePosition(
            start_line=start_line,
            end_line=end_line,
            start_col=start_col,
            end_col=end_col,
            anchor=anchor,
        )
    return None


def to_full_path(*args) -> str:
    """Convert relative path to full path."""
    return os.path.join(cwd, *args)


SAMPLE_FRAMES = [
    FrameInfo(
        name="test_iter_frames",
        source=SourceInfo(
            file_name="/workspaces/gufo_err/tests/test_frames.py",
            first_line=169,
            current_line=176,
            lines=[
                "    ),",
                "]",
                "",
                "",
                "def test_iter_frames():",
                '    """Call the function which raises an exception."""',
                "    try:",
                "        entry()",
                '        msg = "No trace"',
                "        raise AssertionError(msg)",
                "    except RuntimeError:",
                "        frames = list(iter_frames(exc_traceback()))",
                "        assert frames == SAMPLE_FRAMES",
            ],
            pos=CodePosition(
                start_line=176,
                end_line=176,
                start_col=8,
                end_col=15,
                anchor=None,
            ),
        ),
        locals={},
        module="tests.test_frames",
    ),
    FrameInfo(
        name="entry",
        source=SourceInfo(
            file_name="/workspaces/gufo_err/tests/sample/trace.py",
            first_line=8,
            current_line=15,
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
            pos=CodePosition(
                start_line=15,
                end_line=15,
                start_col=4,
                end_col=13,
                anchor=None,
            ),
        ),
        locals={"s": 3},
        module="tests.sample.trace",
    ),
    FrameInfo(
        name="to_oops",
        source=SourceInfo(
            file_name="/workspaces/gufo_err/tests/sample/trace.py",
            first_line=2,
            current_line=9,
            lines=[
                '    msg = "oops"',
                "    raise RuntimeError(msg)",
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
            pos=CodePosition(
                start_line=9, end_line=9, start_col=4, end_col=10, anchor=None
            ),
        ),
        locals={"x": 2},
        module="tests.sample.trace",
    ),
    FrameInfo(
        name="oops",
        source=SourceInfo(
            file_name="/workspaces/gufo_err/tests/sample/trace.py",
            first_line=1,
            current_line=3,
            lines=[
                "def oops():",
                '    msg = "oops"',
                "    raise RuntimeError(msg)",
                "",
                "",
                "def to_oops():",
                "    x = 1",
                "    x += 1",
                "    oops()",
                "",
            ],
            pos=CodePosition(
                start_line=3, end_line=3, start_col=4, end_col=27, anchor=None
            ),
        ),
        locals={"msg": "oops"},
        module="tests.sample.trace",
    ),
]


def test_iter_frames():
    """Call the function which raises an exception."""
    try:
        entry()
        msg = "No trace"
        raise AssertionError(msg)
    except RuntimeError:
        frames = list(iter_frames(exc_traceback()))
        assert frames == SAMPLE_FRAMES
