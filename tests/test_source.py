# ---------------------------------------------------------------------
# Gufo Err: __source_from tests
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
from importlib.abc import InspectLoader

# Third-party modules
import pytest

# Gufo Labs modules
from gufo.err.frame import (
    __get_source,
    __source_from_file,
    __source_from_loader,
)

SAMPLE_STR = 'SAMPLE_LINE = "this is the sample"'
SAMPLE_PATH = os.path.join("tests", "sample", "sample.py")


@pytest.fixture(scope="module")
def loader() -> InspectLoader:
    m = __import__("tests.sample.sample", {}, {}, "*")
    return m.__loader__


def is_valid_sample(s: str) -> bool:
    """Check string is valid module sample."""
    lines = s.splitlines()
    print(lines)
    if len(lines) < 9:
        return False
    return lines[8] == SAMPLE_STR


def test_source_from_file_miss() -> None:
    """Missed file."""
    assert __source_from_file("/tmp/nosuchfileanyway") is None  # noqa: S108


def test_source_from_hit() -> None:
    """Existing file."""
    source = __source_from_file(SAMPLE_PATH)
    assert source is not None
    assert is_valid_sample(source) is True


def test_source_from_loader_miss(loader: InspectLoader) -> None:
    """Missed module from loader."""
    assert __source_from_loader(loader, "xxx.nosuchmodule") is None


def test_source_from_broken_loader() -> None:
    class BrokenLoader(object):
        ...

    assert __source_from_loader(BrokenLoader(), "invalidmodule") is None


def test_source_from_loader_hit(loader: InspectLoader) -> None:
    source = __source_from_loader(loader, "tests.sample.sample")
    assert source is not None
    assert is_valid_sample(source) is True


def test_get_source_from_loader(loader: InspectLoader) -> None:
    source = __get_source(loader=loader, module_name="tests.sample.sample")
    assert source is not None
    assert is_valid_sample(source) is True


def test_get_source_from_file() -> None:
    source = __get_source(file_name=SAMPLE_PATH)
    assert source is not None
    assert is_valid_sample(source) is True


def test_get_source_miss(loader: InspectLoader) -> None:
    source = __get_source(
        loader=loader,
        module_name="xxx.nosuchmodule",
    )
    assert source is None
