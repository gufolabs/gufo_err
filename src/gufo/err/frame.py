# ---------------------------------------------------------------------
# Gufo Err: Frame Extraction
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""FrameInfo structure."""
# Python modules
import ast
import sys
from importlib.abc import InspectLoader
from itertools import islice
from types import CodeType, TracebackType
from typing import Iterable, Optional, cast

# Gufo Labs modules
from .types import Anchor, CodePosition, FrameInfo, SourceInfo

PY_3 = 3
PY_3_11 = (3, 11)


def exc_traceback() -> TracebackType:
    """
    Cast type to `sys.exc_info()`.

    Extract and return top-level excecution frame
    from current exception context.

    Returns:
        Top-level exception frame.
    """
    return cast(TracebackType, sys.exc_info()[2])


def iter_frames(
    tb: TracebackType, context_lines: int = 7
) -> Iterable[FrameInfo]:
    """
    Iterate over traceback frames.

    Args:
        tb: current execution frame.
        context_lines: Source code context to extract.
            Current line, up to `context_lines` below
            the current line, and up to `context_lines`
            above the current line will be extracted.

    Returns:
        Iterable of FrameInfo, starting from top of the
        stack (current code position).
    """
    current: Optional[TracebackType] = tb
    while current is not None:
        frame = current.tb_frame
        src = __get_source_info(
            file_name=frame.f_code.co_filename,
            line_no=current.tb_lineno,
            context_lines=context_lines,
            loader=frame.f_globals.get("__loader__"),
            module_name=frame.f_globals.get("__name__"),
            code=frame.f_code,
            inst_index=current.tb_lasti,
        )
        yield FrameInfo(
            name=frame.f_code.co_name,
            module=frame.f_globals.get("__name__"),
            source=src,
            locals=frame.f_locals,
        )
        current = current.tb_next


def __source_from_loader(
    loader: InspectLoader, module_name: str
) -> Optional[str]:
    try:
        return loader.get_source(module_name)
    except AttributeError:
        return None  # .get_source() does not supported
    except ImportError:
        return None


def __source_from_file(file_name: str) -> Optional[str]:
    try:
        with open(file_name) as f:
            return f.read()
    except OSError:
        return None


def __get_source(
    file_name: Optional[str] = None,
    loader: Optional[InspectLoader] = None,
    module_name: Optional[str] = None,
) -> Optional[str]:
    src: Optional[str] = None
    if loader and module_name:
        src = __source_from_loader(loader, module_name)
    if not src and file_name:
        src = __source_from_file(file_name)
    return src


def __get_source_info(
    line_no: int,
    context_lines: int,
    code: CodeType,
    inst_index: int,
    file_name: Optional[str] = None,
    loader: Optional[InspectLoader] = None,
    module_name: Optional[str] = None,
) -> Optional[SourceInfo]:
    src = __get_source(
        file_name=file_name, loader=loader, module_name=module_name
    )
    if not src:
        return None  # Unable to get the source
    # @todo: maybe use linecache
    lines = src.splitlines()  # @todo: Implement sliding line iterator
    # Extract current code position
    code_position = __get_code_position(code, inst_index, lines[line_no - 1])
    #
    if code_position:
        # Exact locations
        first_line = max(1, code_position.start_line - context_lines)
        last_line = code_position.end_line + context_lines
    else:
        first_line = max(1, line_no - context_lines)
        last_line = line_no + context_lines
    #
    return SourceInfo(
        file_name=file_name or module_name or "",
        first_line=first_line,
        current_line=line_no,
        lines=lines[first_line - 1 : last_line],
        pos=code_position,
    )


def __has_code_position() -> bool:
    """
    Check if python supports exact code positions.

    Returns:
        * True - if python 3.11+ and PYTHONNODEBUGRANGES is not set.
        * False - otherwise
    """
    import os

    if sys.version_info.major < PY_3:
        return False  # No support for Python 2
    if sys.version_info.major > PY_3:
        return True  # Python 4? :)
    if sys.version_info >= PY_3_11:
        return os.environ.get("PYTHONNODEBUGRANGES") is None
    return False


HAS_CODE_POSITION = __has_code_position()


def __get_code_position(
    code: CodeType, inst_index: int, line: str
) -> Optional[CodePosition]:
    """
    Extract code range for current instruction.

    Args:
        code: Code object
        inst_index: Current instruction index, usually from `tb_lasti`
        line: Current code line

    Returns:
        Optional CodePosition instance
    """
    if not HAS_CODE_POSITION or inst_index < 0:
        return None
    # Warning! co_positions is not defineed prior the Python 3.11
    # so mypy will raise an error.
    positions_gen = code.co_positions()  # type:ignore[attr-defined]
    start_line, end_line, start_col, end_col = next(
        islice(positions_gen, inst_index // 2, None)
    )
    if (
        start_line is None
        or end_line is None
        or start_col is None
        or end_col is None
    ):
        return None
    if start_line == end_line:
        anchor = __get_anchor(line[start_col:end_col], start_col)
    else:
        anchor = None
    return CodePosition(
        start_line=start_line,
        end_line=end_line,
        start_col=start_col,
        end_col=end_col,
        anchor=anchor,
    )


def __get_anchor(segment: str, indent: int = 0) -> Optional[Anchor]:
    """
    Split code segment and try to get error anchors.

    Backport from Python 3.11
    `_extract_caret_anchors_from_line_segment`.

    Args:
        segment: Code segment with current op.
        indent: Position offset.

    Returns:
        * Anchor instance if code can be refined.
        * None otherwise
    """
    try:
        tree = ast.parse(segment)
    except SyntaxError:
        return None
    # Should be only current statement
    if len(tree.body) != 1:
        return None
    statement = tree.body[0]
    # Cannot use match as it raises SyntaxError
    # prior Python 3.10
    if not isinstance(statement, ast.Expr):
        return None
    expr = statement.value
    if isinstance(expr, ast.BinOp):
        # Binary operation, problem with operator
        operator_str = segment[
            expr.left.end_col_offset : expr.right.col_offset
        ]
        operator_offset = len(operator_str) - len(operator_str.lstrip())
        if expr.left.end_col_offset is None:
            return None
        left_anchor = expr.left.end_col_offset + operator_offset
        right_anchor = left_anchor + 1
        if (
            operator_offset + 1 < len(operator_str)
            and not operator_str[operator_offset + 1].isspace()
        ):
            right_anchor += 1
        return Anchor(left=left_anchor + indent, right=right_anchor + indent)
    if (
        isinstance(expr, ast.Subscript)
        and expr.value.end_col_offset is not None
        and expr.slice.end_col_offset is not None
    ):
        # Subscript operation, problem with value
        return Anchor(
            left=expr.value.end_col_offset + indent,
            right=expr.slice.end_col_offset + indent + 1,
        )
    return None
