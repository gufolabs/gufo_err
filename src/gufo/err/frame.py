# ---------------------------------------------------------------------
# Gufo Err: Frame Extraction
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import sys
from itertools import islice
from types import TracebackType, CodeType
from typing import Optional, Iterable, cast
from importlib.abc import InspectLoader

# Gufo Labs modules
from .types import FrameInfo, SourceInfo, CodePosition


def exc_traceback() -> TracebackType:
    """
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
        src = __get_lines(
            file_name=frame.f_code.co_filename,
            line_no=current.tb_lineno,
            context_lines=context_lines,
            loader=frame.f_globals.get("__loader__"),
            module_name=frame.f_globals.get("__name__"),
            code_position=__get_code_position(frame.f_code, current.tb_lasti),
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


def __get_lines(
    line_no: int,
    context_lines: int,
    file_name: Optional[str] = None,
    loader: Optional[InspectLoader] = None,
    module_name: Optional[str] = None,
    code_position: Optional[CodePosition] = None,
) -> Optional[SourceInfo]:
    src = __get_source(
        file_name=file_name, loader=loader, module_name=module_name
    )
    if not src:
        return None  # Unable to get the source
    # @todo: maybe use linecachee
    lines = src.splitlines()  # @todo: Implement sliding line iterator
    if code_position:
        # Exact locations
        first_line = max(1, code_position.start_line - context_lines)
        last_line = code_position.end_line + context_lines
    else:
        first_line = max(1, line_no - context_lines)
        last_line = line_no + context_lines
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
        * True - if ????
        * False - otherwise
    """
    import os

    if sys.version_info.major < 3:
        return False  # No support for Python 2
    if sys.version_info.major > 3:
        return True  # Python 4? :)
    if sys.version_info.minor >= 11:
        return os.environ.get("PYTHONNODEBUGRANGES") is None
    return False


HAS_CODE_POSITION = __has_code_position()


def __get_code_position(
    code: CodeType, inst_index: int
) -> Optional[CodePosition]:
    """
    Extract code range for current instruction.

    Args:
        code: Code object
        inst_index: Current instruction index, usually from `tb_lasti`

    Returns:
        Optional CodePosition instance
    """
    if not HAS_CODE_POSITION or inst_index < 0:
        return None
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
    return CodePosition(
        start_line=start_line,
        end_line=end_line,
        start_col=start_col,
        end_col=end_col,
    )
