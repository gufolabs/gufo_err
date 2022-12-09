# ----------------------------------------------------------------------
# Gufo Liftbridge: docs tests
# ----------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Set
import os
import re

# Third-party modules
import pytest

_doc_files: Optional[List[str]] = None

rx_link = re.compile(r"\[([^\]]+)\]\[([^\]]+)\]", re.MULTILINE)
rx_link_def = re.compile(r"^\[([^\]]+)\]:", re.MULTILINE)


def get_docs():
    global _doc_files

    if _doc_files is None:
        _doc_files = []
        for root, _, files in os.walk("docs"):
            for f in files:
                if f.endswith(".md") and not f.startswith("."):
                    _doc_files.append(os.path.join(root, f))
    return _doc_files


def get_file(path: str) -> str:
    with open(path) as f:
        return f.read()


@pytest.mark.parametrize("doc", get_docs())
def test_links(doc: str):
    data = get_file(doc)
    links: Set[str] = set()
    defs: Set[str] = set()
    for match in rx_link.finditer(data):
        links.add(match.group(2))
    for match in rx_link_def.finditer(data):
        d = match.group(1)
        assert d not in defs, f"Link already defined: {d}"
        assert d in links, f"Unused link definition: {d}"