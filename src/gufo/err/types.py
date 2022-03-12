# ---------------------------------------------------------------------
# Gufo Err: Types
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class SourceInfo(object):
    """
    Source

    Args:
        file_name: xxxx
        first_line: xxxx
        current_line: xxxx
        lines: xxx
    """

    file_name: str
    first_line: int
    current_line: int
    lines: List[str]


@dataclass
class FrameInfo(object):
    """
    Frame

    Args:
        name: xxx
        source: xxx
        locals: xxx
    """

    name: str
    source: Optional[SourceInfo]
    locals: Dict[str, Any]
