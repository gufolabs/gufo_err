# ---------------------------------------------------------------------
# Gufo Err: test formatters
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import datetime
import os
import uuid

# Third-party modules
import pytest

# Gufo Err modules
from gufo.err import CodePosition, ErrorInfo, FrameInfo, SourceInfo
from gufo.err.formatter.extend import ExtendFormatter
from gufo.err.formatter.loader import get_formatter
from gufo.err.formatter.terse import TerseFormatter

SAMPLE_ERR = ErrorInfo(
    name="my-test",
    version="3.14",
    fingerprint=uuid.UUID("be8ccd86-3661-434c-8569-40dd65d9860a"),
    timestamp=datetime.datetime(2023, 9, 1, 6, 31, 16, 79222),
    exception=RuntimeError("oops"),
    stack=[
        FrameInfo(
            name="test_iter_frames",
            source=SourceInfo(
                file_name=os.path.join(
                    os.sep, "app", "tests", "test_frames.py"
                ),
                first_line=167,
                current_line=174,
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
                    start_line=174,
                    end_line=174,
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
                file_name=os.path.join(
                    os.sep, "app", "tests", "sample", "trace.py"
                ),
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
                file_name=os.path.join(
                    os.sep, "app", "tests", "sample", "trace.py"
                ),
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
                    start_line=9,
                    end_line=9,
                    start_col=4,
                    end_col=10,
                    anchor=None,
                ),
            ),
            locals={"x": 2},
            module="tests.sample.trace",
        ),
        FrameInfo(
            name="oops",
            source=SourceInfo(
                file_name=os.path.join(
                    os.sep, "app", "tests", "sample", "trace.py"
                ),
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
                    start_line=3,
                    end_line=3,
                    start_col=4,
                    end_col=27,
                    anchor=None,
                ),
            ),
            locals={"msg": "oops"},
            module="tests.sample.trace",
        ),
    ],
)

TERSE_RESULT = """Error: be8ccd86-3661-434c-8569-40dd65d9860a
Traceback (most resent call last):
  File "/app/tests/test_frames.py", line 174, in test_iter_frames
    entry()
    ^^^^^^^
  File "/app/tests/sample/trace.py", line 15, in entry
    to_oops()
    ^^^^^^^^^
  File "/app/tests/sample/trace.py", line 9, in to_oops
    oops()
    ^^^^^^
  File "/app/tests/sample/trace.py", line 3, in oops
    raise RuntimeError(msg)
    ^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: oops"""

EXTEND_RESULT = "\n".join(
    [
        "Error: be8ccd86-3661-434c-8569-40dd65d9860a",
        "RuntimeError: oops",
        "Traceback (most resent call last):",
        "-------------------------------------------------------------------------------",
        "File: /app/tests/test_frames.py (line 174)",
        "  167         ),",
        "  168     ]",
        "  169     ",
        "  170     ",
        "  171     def test_iter_frames():",
        '  172         """Call the function which raises an exception."""',
        "  173         try:",
        "  174 ==>         entry()",
        "                  ^^^^^^^",
        '  175             msg = "No trace"',
        "  176             raise AssertionError(msg)",
        "  177         except RuntimeError:",
        "  178             frames = list(iter_frames(exc_traceback()))",
        "  179             assert frames == SAMPLE_FRAMES",
        "-------------------------------------------------------------------------------",
        "File: /app/tests/sample/trace.py (line 15)",
        "    8         x += 1",
        "    9         oops()",
        "   10     ",
        "   11     ",
        "   12     def entry():",
        "   13         s = 2",
        "   14         s += 1",
        "   15 ==>     to_oops()",
        "              ^^^^^^^^^",
        "Locals:",
        "                   s = 3",
        "-------------------------------------------------------------------------------",
        "File: /app/tests/sample/trace.py (line 9)",
        '    2         msg = "oops"',
        "    3         raise RuntimeError(msg)",
        "    4     ",
        "    5     ",
        "    6     def to_oops():",
        "    7         x = 1",
        "    8         x += 1",
        "    9 ==>     oops()",
        "              ^^^^^^",
        "   10     ",
        "   11     ",
        "   12     def entry():",
        "   13         s = 2",
        "   14         s += 1",
        "   15         to_oops()",
        "Locals:",
        "                   x = 2",
        "-------------------------------------------------------------------------------",
        "File: /app/tests/sample/trace.py (line 3)",
        "    1     def oops():",
        '    2         msg = "oops"',
        "    3 ==>     raise RuntimeError(msg)",
        "              ^^^^^^^^^^^^^^^^^^^^^^^",
        "    4     ",
        "    5     ",
        "    6     def to_oops():",
        "    7         x = 1",
        "    8         x += 1",
        "    9         oops()",
        "   10     ",
        "Locals:",
        "                 msg = 'oops'",
        "-------------------------------------------------------------------------------",
    ]
)


def test_get_caret_error() -> None:
    pos = CodePosition(
        start_line=10, end_line=11, start_col=4, end_col=4, anchor=None
    )
    formatter = TerseFormatter()
    with pytest.raises(ValueError):
        formatter.get_caret("    test()", pos=pos, indent=0)


def test_loader_invalid() -> None:
    with pytest.raises(ValueError):
        get_formatter("invalid")


def test_loader_terse() -> None:
    formatter = get_formatter("terse")
    assert isinstance(formatter, TerseFormatter)


def test_loader_extend() -> None:
    formatter = get_formatter("extend")
    assert isinstance(formatter, ExtendFormatter)


def test_terse() -> None:
    formatter = get_formatter("terse")
    r = formatter.format(SAMPLE_ERR)
    assert r == TERSE_RESULT


def test_extend() -> None:
    formatter = get_formatter("extend")
    r = formatter.format(SAMPLE_ERR)
    assert r == EXTEND_RESULT
