# ---------------------------------------------------------------------
# Gufo Err: Frame Extraction
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import sys
from types import TracebackType
from typing import Optional, Iterable, cast
from importlib.abc import InspectLoader

# Gufo Labs modules
from .types import FrameInfo, SourceInfo


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
        )
        yield FrameInfo(
            name=frame.f_code.co_name,
            source=src,
            locals=current.tb_frame.f_locals,
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
    except (OSError, IOError):
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
) -> Optional[SourceInfo]:
    src = __get_source(
        file_name=file_name, loader=loader, module_name=module_name
    )
    if not src:
        return None  # Unable to get the source
    lines = src.splitlines()  # @todo: Implement sliding line iterator
    first_line = max(1, line_no - context_lines)
    return SourceInfo(
        file_name=file_name or module_name or "",
        first_line=first_line,
        current_line=line_no,
        lines=lines[first_line - 1 : line_no + context_lines],
    )
