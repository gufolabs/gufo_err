# ---------------------------------------------------------------------
# Gufo Err: Err tests
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
import sys
from typing import Iterable, List, Type
from uuid import UUID

# Third-party modules
import pytest

# Gufo Labs modules
from gufo.err import (
    BaseMiddleware,
    Err,
    ErrorInfo,
    FrameInfo,
    SourceInfo,
)
from gufo.err.failfast.always import AlwaysFailFast
from gufo.err.failfast.never import NeverFailFast
from gufo.err.failfast.typematch import TypeMatchFailFast
from gufo.err.failfast.types import TypesFailFast


def test_unitialized():
    def process():
        try:
            msg = "test"
            raise Exception(msg)
        except Exception:
            err.process()

    err = Err()
    with pytest.raises(RuntimeError):
        process()


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
    with pytest.raises(ValueError):
        err.setup(hash="invalidhash")


@pytest.mark.parametrize(
    ("hash", "data", "expected"),
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
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        fp = err._Err__fingerprint(t, v, [])
        assert isinstance(fp, UUID)
        assert str(fp) == expected


@pytest.mark.parametrize(
    ("stack", "root_module", "expected"),
    [
        (
            [
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
                )
            ],
            None,
            [
                "fp_test",
                "1.0.0",
                "RuntimeError",
                "tests.test",
                "test_fn",
                "10",
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
                "lib.final.test",
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
                "lib.final.test",
                "lib_fn",
                "17",
                "tests.test",
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
        msg = "test"
        raise RuntimeError(msg)
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
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        err._Err__must_die(t, v, None)


@pytest.mark.parametrize(
    ("chain", "expected"),
    [
        ([NeverFailFast()], False),
        ([AlwaysFailFast()], True),
        ([NeverFailFast(), NeverFailFast()], False),
        ([NeverFailFast(), AlwaysFailFast()], True),
        ([TypesFailFast([RuntimeError])], True),
        ([TypesFailFast([ValueError])], False),
        ([TypesFailFast([RuntimeError, ValueError])], True),
        ([TypeMatchFailFast(RuntimeError)], True),
        ([TypeMatchFailFast(ValueError)], False),
        ([TypeMatchFailFast("builtins.RuntimeError")], True),
        ([TypeMatchFailFast(RuntimeError, match="test")], True),
        ([TypeMatchFailFast(RuntimeError, match="est")], True),
        ([TypeMatchFailFast(RuntimeError, match="nest")], False),
        ([TypeMatchFailFast(RuntimeError, msg="stop")], True),
        ([TypeMatchFailFast(RuntimeError, msg="stop: %s")], True),
    ],
)
def test_must_die(chain, expected):
    err = Err()
    err.setup(fail_fast=chain)
    try:
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        t, v, tb = sys.exc_info()
        assert t
        assert v
        assert tb
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
            msg = "test"
            raise exc_class(msg)
        except BaseException:
            err.process()
    except exc_class as e:
        assert e.args[0] == "test"  # noqa: PT017


def test_process_no_tb():
    err = Err()
    err.setup()
    try:
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        t, v, _ = sys.exc_info()
        assert t
        assert v
        err._Err__process(t, v, None)


@pytest.mark.parametrize("code", [1, 2, 3])
def test_failfast_exit(code):
    def _exit(c):
        nonlocal exit_code
        exit_code = c

    err = Err()
    err.setup(fail_fast_code=code, fail_fast=[AlwaysFailFast()])
    exit_code = 0
    prev_exit = os._exit
    os._exit = _exit
    try:
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        err.process()
    os._exit = prev_exit
    assert exit_code == code


def test_add_fail_fast():
    class NamedFailFast(NeverFailFast):
        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name

    err = Err()
    err.setup(fail_fast=[NamedFailFast("f1"), NamedFailFast("f2")])
    err.add_fail_fast(NamedFailFast("f3"))
    err.add_fail_fast(NamedFailFast("f4"))
    chain = [f.name for f in err._Err__failfast_chain]
    assert chain == ["f1", "f2", "f3", "f4"]


def test_middlewre():
    class NamedMiddleware(BaseMiddleware):
        def __init__(self, name: str, fail: bool = False) -> None:
            super().__init__()
            self.name = name
            self.fail = fail

        def process(self, info: ErrorInfo) -> None:
            nonlocal passed
            passed[self.name] = True
            if self.fail:
                msg = "test"
                raise ValueError(msg)

    passed = {}

    err = Err()
    err.setup(middleware=[NamedMiddleware("r1"), NamedMiddleware("r2")])
    err.add_middleware(NamedMiddleware("r3", fail=True))
    err.add_middleware(NamedMiddleware("r4"))
    try:
        msg = "test"
        raise RuntimeError(msg)
    except Exception:
        err.process()
    for i in ("r1", "r2", "r3", "r4"):
        assert passed.get(i) is True


def test_failfast_type_setup():
    err = Err()
    with pytest.raises(ValueError):
        err.setup(fail_fast=[1])


def test_failfast_type_add():
    err = Err()
    err.setup()
    with pytest.raises(ValueError):
        err.add_fail_fast(1)


def test_middleware_type_setup():
    err = Err()
    with pytest.raises(ValueError):
        err.setup(middleware=[1])


def test_middleware_type_add():
    err = Err()
    err.setup()
    with pytest.raises(ValueError):
        err.add_middleware(1)
