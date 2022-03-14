# ---------------------------------------------------------------------
# Gufo Err: Err tests
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from uuid import UUID
from typing import List, Iterable, Type
import sys
import os

# Third-party modules
import pytest

# Gufo Labs modules
from gufo.err import Err, FrameInfo, SourceInfo
from gufo.err.types import ErrorInfo


def test_unitialized():
    err = Err()
    with pytest.raises(RuntimeError):
        try:
            raise Exception("test")
        except Exception:
            err.process()


def test_double_initialized():
    err = Err()
    err.setup()
    with pytest.raises(RuntimeError):
        err.setup()


def test_empty_process():
    err = Err()
    err.setup()
    err.process()


def test_invalid_hash():
    err = Err()
    with pytest.raises(RuntimeError):
        err.setup(hash="invalidhash")


@pytest.mark.parametrize(
    ["hash", "data", "expected"],
    [
        ("sha1", ["test"], "a94a8fe5-ccb1-5ba6-9c4c-0873d391e987"),
        ("sha1", ["test", "test2"], "7408bb49-1e0d-5dc3-bac8-e503353e7940"),
        ("sha256", ["test"], "9f86d081-884c-5d65-9a2f-eaa0c55ad015"),
        ("sha256", ["test", "test2"], "98316636-bec9-5dbd-a3b4-60a9d08b8b16"),
        ("md5", ["test"], "098f6bcd-4621-5373-8ade-4e832627b4f6"),
        ("md5", ["test", "test2"], "8f2ab979-2f93-569a-9898-855f12414208"),
    ],
)
def test_hash(hash, data, expected):
    class ZeroHashErr(Err):
        def iter_fingerprint_parts(
            self,
            t: Type[BaseException],
            v: BaseException,
            stack: List[FrameInfo],
        ) -> Iterable[str]:
            yield from data

    err = ZeroHashErr()
    err.setup(hash=hash)
    try:
        raise RuntimeError("test")
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        fp = err._Err__fingerprint(t, v, [])
        assert isinstance(fp, UUID)
        assert str(fp) == expected


@pytest.mark.parametrize(
    ["stack", "root_module", "expected"],
    [
        (
            [
                FrameInfo(
                    name="test_fn",
                    source=SourceInfo(
                        file_name="tests/test.py",
                        current_line=10,
                        first_line=3,
                        lines=[],
                    ),
                    locals={},
                )
            ],
            None,
            [
                "fp_test",
                "1.0.0",
                "RuntimeError",
                "tests/test.py",
                "test_fn",
                "10",
            ],
        ),
        (
            [
                FrameInfo(
                    name="lib_fn",
                    source=SourceInfo(
                        file_name="lib/final/test.py",
                        current_line=17,
                        first_line=10,
                        lines=[],
                    ),
                    locals={},
                ),
                FrameInfo(
                    name="proxt_fn",
                    source=SourceInfo(
                        file_name="lib/proxy/test.py",
                        current_line=20,
                        first_line=13,
                        lines=[],
                    ),
                    locals={},
                ),
                FrameInfo(
                    name="test_fn",
                    source=SourceInfo(
                        file_name="tests/test.py",
                        current_line=10,
                        first_line=3,
                        lines=[],
                    ),
                    locals={},
                ),
            ],
            None,
            [
                "fp_test",
                "1.0.0",
                "RuntimeError",
                "lib/final/test.py",
                "lib_fn",
                "17",
            ],
        ),
        (
            [
                FrameInfo(
                    name="lib_fn",
                    module="lib.final.test",
                    source=SourceInfo(
                        file_name="lib/final/test.py",
                        current_line=17,
                        first_line=10,
                        lines=[],
                    ),
                    locals={},
                ),
                FrameInfo(
                    name="proxt_fn",
                    module="lib.proxy.test",
                    source=SourceInfo(
                        file_name="lib/proxy/test.py",
                        current_line=20,
                        first_line=13,
                        lines=[],
                    ),
                    locals={},
                ),
                FrameInfo(
                    name="test_fn",
                    module="tests.test",
                    source=SourceInfo(
                        file_name="tests/test.py",
                        current_line=10,
                        first_line=3,
                        lines=[],
                    ),
                    locals={},
                ),
            ],
            "tests.test",
            [
                "fp_test",
                "1.0.0",
                "RuntimeError",
                "lib/final/test.py",
                "lib_fn",
                "17",
                "tests/test.py",
                "test_fn",
                "10",
            ],
        ),
    ],
)
def test_iter_fingerprint_parts(stack, root_module, expected):
    err = Err()
    err.setup(name="fp_test", version="1.0.0", root_module=root_module)
    try:
        raise RuntimeError("test")
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        parts = list(err.iter_fingerprint_parts(t, v, stack))
        assert parts == expected


def test_must_die_no_tb():
    err = Err()
    err.setup()
    try:
        raise RuntimeError("test")
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        err._Err__must_die(t, v, None)


@pytest.mark.parametrize(
    ["chain", "expected"],
    [
        ([lambda _t, _v, _tb: False], False),
        ([lambda _t, _v, _tb: True], True),
        ([lambda _t, _v, _tb: False, lambda _t, _v, _tb: False], False),
        ([lambda _t, _v, _tb: False, lambda _t, _v, _tb: True], True),
    ],
)
def test_must_die(chain, expected):
    err = Err()
    err.setup(fail_fast=chain)
    try:
        raise RuntimeError("test")
    except Exception:
        t, v, tb = sys.exc_info()
        assert t and v and tb
        r = err._Err__must_die(t, v, tb)
        assert r is expected


def test_no_catch_all():
    prev_hook = sys.excepthook
    err = Err()
    err.setup()
    assert sys.excepthook == prev_hook


def test_catch_all():
    prev_hook = sys.excepthook
    err = Err()
    err.setup(catch_all=True)
    assert sys.excepthook == err._Err__process
    sys.excepthook = prev_hook


@pytest.mark.parametrize("exc_class", [SystemExit, KeyboardInterrupt])
def test_process_excluded_exc(exc_class: Type[BaseException]):
    err = Err()
    err.setup()
    try:
        try:
            raise exc_class("test")
        except BaseException:
            err.process()
    except exc_class as e:
        assert e.args[0] == "test"


def test_process_no_tb():
    err = Err()
    err.setup()
    try:
        raise RuntimeError("test")
    except Exception:
        t, v, _ = sys.exc_info()
        assert t and v
        err._Err__process(t, v, None)


@pytest.mark.parametrize("code", [1, 2, 3])
def test_failfast_exit(code):
    def _exit(c):
        nonlocal exit_code
        exit_code = c

    err = Err()
    err.setup(fail_fast_code=code, fail_fast=[lambda _t, _v, _tb: True])
    exit_code = 0
    prev_exit = os._exit
    os._exit = _exit
    try:
        raise RuntimeError("test")
    except Exception:
        err.process()
    os._exit = prev_exit
    assert exit_code == code


def test_add_fail_fast():
    def f1(t, v, tb) -> bool:
        return False

    def f2(t, v, tb) -> bool:
        return False

    def f3(t, v, tb) -> bool:
        return False

    def f4(t, v, tb) -> bool:
        return False

    err = Err()
    err.setup(fail_fast=[f1, f2])
    err.add_fail_fast(f3)
    err.add_fail_fast(f4)
    chain = [f.__name__ for f in err._Err__failfast_chain]
    assert chain == ["f1", "f2", "f3", "f4"]


def test_response():
    def r1(err: Err, error: ErrorInfo) -> None:
        nonlocal r1_passed
        assert not r1_passed
        r1_passed = True

    def r2(err: Err, error: ErrorInfo) -> None:
        nonlocal r2_passed
        assert not r2_passed
        r2_passed = True

    def r3(err: Err, error: ErrorInfo) -> None:
        nonlocal r3_passed
        assert not r3_passed
        r3_passed = True
        raise ValueError("test")

    def r4(err: Err, error: ErrorInfo) -> None:
        nonlocal r4_passed
        assert not r4_passed
        r4_passed = True

    r1_passed = False
    r2_passed = False
    r3_passed = False
    r4_passed = False
    err = Err()
    err.setup(response=[r1, r2])
    err.add_response(r3)
    err.add_response(r4)
    try:
        raise RuntimeError("test")
    except Exception:
        err.process()
    assert r1_passed
    assert r2_passed
    assert r3_passed
    assert r4_passed
