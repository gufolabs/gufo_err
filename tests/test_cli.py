# ---------------------------------------------------------------------
# Gufo Labs: CLI test
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# See LICENSE.md for details
# ---------------------------------------------------------------------

# Python modules
import os
import tempfile
from collections import defaultdict

# Third-party modules
import pytest

# Gufo Err modules
from gufo.err import Err, __version__
from gufo.err.cli import Cli, ExitCode

FAKE_UUID = "e5d2e3e0-d6b9-415f-ba09-5eadbe4b38ad"


def fn1():
    raise ValueError


def fn2():
    msg = "foobar"
    raise NameError(msg)


def fn3():
    raise TypeError


def fn4():
    raise NotImplementedError


@pytest.fixture(scope="module")
def crashinfo():
    """Create crashinfo directory and populate it with several crashes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for codec, fn in [
            (None, fn1),
            ("gz", fn2),
            ("bz2", fn3),
            ("xz", fn4),
        ]:
            err = Err().setup(
                name=f"fmt-{codec}",
                format=None,
                error_info_path=tmpdir,
                error_info_compress=codec,
            )
            try:
                fn()
            except Exception:
                err.process()
        yield tmpdir


def test_help_short() -> None:
    with pytest.raises(SystemExit):
        Cli().run(["-h"])


def test_help_long() -> None:
    with pytest.raises(SystemExit):
        Cli().run(["--help"])


def test_version(capsys) -> None:
    r = Cli().run(["version"])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    assert out == f"Gufo Err {__version__}\n"


def test_crashinfo_setup(crashinfo) -> None:
    assert os.path.exists(crashinfo)
    lst = os.listdir(crashinfo)
    # Check length
    assert len(lst) == 4
    # Check suffixes
    r = defaultdict(int)
    for fn in lst:
        r[fn.split(".", 1)[1]] += 1
    assert r.get("json") == 1
    assert r.get("json.gz") == 1
    assert r.get("json.bz2") == 1
    assert r.get("json.xz") == 1


def test_list_invalid(capsys) -> None:
    path = "/nonexistend/directory"
    r = Cli().run(["-p", path, "list"])
    assert r == ExitCode.NOT_EXISTS
    out = capsys.readouterr().out
    assert out == f"Error: {path} is not exists\n"


def test_list(capsys, crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "list"])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    assert "TypeError" in out
    assert "ValueError" in out
    assert "NameError: foobar" in out
    assert "NotImplementedError" in out
    assert "fmt-None" in out
    assert "fmt-gz" in out
    assert "fmt-bz2" in out
    assert "fmt-xz" in out
    assert "test_cli.py:57" in out
    # assert out == ""


def test_list_all(capsys, crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "list", "all"])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    assert "TypeError" in out
    assert "ValueError" in out
    assert "NameError: foobar" in out
    assert "NotImplementedError" in out
    assert "fmt-None" in out
    assert "fmt-gz" in out
    assert "fmt-bz2" in out
    assert "fmt-xz" in out
    assert "test_cli.py:57" in out
    # assert out == ""


def test_list_two(capsys, crashinfo) -> None:
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    include = all_fp[:2]
    exclude = all_fp[2:]
    r = Cli().run(["-p", crashinfo, "list", *include])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    for fp in include:
        assert fp in out
    for fp in exclude:
        assert fp not in out


def test_list_syntax_error(capsys, crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "list", "invalid"])
    assert r == ExitCode.SYNTAX


def test_view_invalid(capsys, crashinfo) -> None:
    path = "/nonexistend/directory"
    r = Cli().run(["-p", path, "view", FAKE_UUID])
    assert r == ExitCode.NOT_EXISTS
    out = capsys.readouterr().out
    assert out == f"Error: {path} is not exists\n"


def test_view_empty(crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "view"])
    assert r == ExitCode.OK


def test_view_cannot_read(crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "view", FAKE_UUID])
    assert r == ExitCode.CANNOT_READ


def test_view_invalid_args(crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "view", "-f", "custom", FAKE_UUID])
    assert r == ExitCode.INVALID_ARGS


def test_view(capsys, crashinfo) -> None:
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    r = Cli().run(["-p", crashinfo, "view", *all_fp])
    assert r == ExitCode.OK


def test_view_terse(capsys, crashinfo) -> None:
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    r = Cli().run(["-p", crashinfo, "view", "-f", "terse", *all_fp])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    assert "TypeError" in out
    assert "ValueError" in out
    assert "NameError: foobar" in out
    assert "NotImplementedError" in out
    for fp in all_fp:
        assert fp in out


def test_view_extend(capsys, crashinfo) -> None:
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    r = Cli().run(["-p", crashinfo, "view", "--format", "extend", *all_fp])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    assert "TypeError" in out
    assert "ValueError" in out
    assert "NameError: foobar" in out
    assert "NotImplementedError" in out
    for fp in all_fp:
        assert fp in out


def test_view_all(capsys, crashinfo):
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    r = Cli().run(["-p", crashinfo, "view", "all"])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    for fp in all_fp:
        assert fp in out


def test_view_all_star(capsys, crashinfo):
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    r = Cli().run(["-p", crashinfo, "view", "*"])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    for fp in all_fp:
        assert fp in out


def test_view_two(capsys, crashinfo) -> None:
    all_fp = [fn.split(".")[0] for fn in os.listdir(crashinfo)]
    include = all_fp[:2]
    exclude = all_fp[2:]
    r = Cli().run(["-p", crashinfo, "view", *include])
    assert r == ExitCode.OK
    out = capsys.readouterr().out
    for fp in include:
        assert fp in out
    for fp in exclude:
        assert fp not in out


def test_view_syntax_error(capsys, crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "view", "invalid"])
    assert r == ExitCode.SYNTAX


@pytest.mark.parametrize(
    ("t", "w", "exp"),
    [
        ("12345", 6, "12345 "),
        ("12345", 5, "12345"),
        ("123456", 5, "12..."),
    ],
)
def test_col(t: str, w: int, exp: str) -> None:
    r = Cli.col(t, w)
    assert r == exp


@pytest.mark.parametrize(
    ("t", "w", "exp"),
    [
        ("12345", 6, "12345 "),
        ("12345", 5, "12345"),
        ("123456", 5, "...56"),
    ],
)
def test_rcol(t: str, w: int, exp: str) -> None:
    r = Cli.rcol(t, w)
    assert r == exp


def test_clear_empty(crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "clear"])
    assert r == ExitCode.OK


def test_clear_syntax_error(capsys, crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "clear", "invalid"])
    assert r == ExitCode.SYNTAX


def test_clear_cannot_read(crashinfo) -> None:
    r = Cli().run(["-p", crashinfo, "clear", FAKE_UUID])
    assert r == ExitCode.CANNOT_READ


def test_clear_invalid(capsys, crashinfo) -> None:
    path = "/nonexistend/directory"
    r = Cli().run(["-p", path, "clear", FAKE_UUID])
    assert r == ExitCode.NOT_EXISTS
    out = capsys.readouterr().out
    assert out == f"Error: {path} is not exists\n"


# Keep this test as latest in the modules
def test_clear(crashinfo) -> None:
    def ls():
        return [fn.split(".")[0] for fn in os.listdir(crashinfo)]

    # Delete one
    all_fp = ls()
    assert len(all_fp) == 4
    to_delete = all_fp[0]
    r = Cli().run(["-p", crashinfo, "clear", to_delete])
    assert r == ExitCode.OK
    all_fp = ls()
    assert to_delete not in all_fp
    assert len(all_fp) == 3
    # Delete two
    to_delete = all_fp[:2]
    r = Cli().run(["-p", crashinfo, "clear", *to_delete])
    assert r == ExitCode.OK
    all_fp = ls()
    for fp in to_delete:
        assert fp not in all_fp
    assert len(all_fp) == 1
    # Delete all
    r = Cli().run(["-p", crashinfo, "clear", "all"])
    assert r == ExitCode.OK
    assert not ls()
