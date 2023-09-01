# ---------------------------------------------------------------------
# Gufo Err: Command-line utility
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""`err` utility."""

# Python module
import argparse
import datetime
import os
import re
import sys
import uuid
from dataclasses import dataclass
from enum import IntEnum
from operator import attrgetter
from typing import Callable, Dict, Iterable, List, Optional, Set

# Gufo Err modules
from . import __version__
from .codec import from_json
from .compressor import Compressor
from .formatter.loader import get_formatter
from .types import ErrorInfo


@dataclass
class ListItem(object):
    """
    Data structure for `err list`.

    Attributes:
        fingerprint: Stringified fingerprint.
        exception: Exception string.
        name: Application name.
        ts: Error timestamp.
        place: Error location.
    """

    fingerprint: str
    exception: str
    name: str
    ts: datetime.datetime
    place: str


class ExitCode(IntEnum):
    """
    Cli exit codes.

    Attributes:
        OK: Successful exit
        NOT_EXISTS: Error Info directory is not found
        EACCESS: Error Info directory is not readable
        CANNOT_READ: Cannot read Error Info file
        INVALID_ARGS: Invalid arguments
        SYNTAX: Invalid expression
    """

    OK = 0
    NOT_EXISTS = 1
    EACCESS = 2
    CANNOT_READ = 3
    INVALID_ARGS = 4
    SYNTAX = 5


class Cli(object):
    """`err` utility class."""

    rx_fn = re.compile(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.json"
        "(|.gz|.bz2|.xz)$"
    )

    def handle_version(self: "Cli", _ns: argparse.Namespace) -> ExitCode:
        """
        Print Gufo Err version.

        Args:
            _ns: Options namespace, ignored.

        Returns:
            Exit code.
        """
        print(f"Gufo Err {__version__}")
        return ExitCode.OK

    @staticmethod
    def col(t: str, width: int) -> str:
        """
        Format text to column.

        Enlarge with spaces, when necessary.
        Cut if too long.

        Args:
            t: Text
            width: Column width

        Returns:
            Aligned text.

        Examples:
            ``` py
            col("abcdef", 5)
            ```
            returns
            ``` py
            "ab..."
            ```
        """
        ln = len(t)
        if ln < width:
            return t + " " * (width - ln)
        if ln == width:
            return t
        return t[: width - 3] + "..."

    @staticmethod
    def rcol(t: str, width: int) -> str:
        """
        Format text to column aligned to the range.

        Enlarge with spaces, when necessary.
        Cut if too long.

        Args:
            t: Text
            width: Column width

        Returns:
            Aligned text.

        Examples:
            ``` py
            col("abcdef", 5)
            ```
            returns
            ``` py
            "...ef"
            ```
        """
        ln = len(t)
        if ln < width:
            return t + " " * (width - ln)
        if ln == width:
            return t
        return "..." + t[ln - width - 3 :]

    @staticmethod
    def __check_dir(path: str) -> ExitCode:
        """
        Check if directory exists and accessible.

        Args:
            path: Directory path

        Returns:
            * OK - on success
            * NOT_EXISTS - if the directory is not exists
            * EACCESS - if the directory is not accessible
        """
        # Check if the directory exists
        if not os.path.exists(path):
            print(f"Error: {path} is not exists")
            return ExitCode.NOT_EXISTS
        # Check if the directory is readable
        if not os.access(path, os.R_OK):
            print(f"Error: {path} is not accessible")
            return ExitCode.EACCESS
        return ExitCode.OK

    def handle_list(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """
        Show the list of the registered errors.

        Args:
            ns: argsparse.Namespace with fields:

                * `prefix` - directory of errorinfo files.
                * `fingerprints` - list of fingerprint expressions.

        Returns:
            Exit code.
        """
        prefix = ns.prefix
        # Check if the directory exists
        code = self.__check_dir(prefix)
        if code != ExitCode.OK:
            return code
        # Resolve expressions
        fp_expr = ns.fingerprints if ns.fingerprints else ["*"]
        try:
            fingerprints = list(self.iter_fingerprints(fp_expr, prefix))
        except SyntaxError as e:
            print(f"ERROR: Invalid expression {e!s}")
            return ExitCode.SYNTAX
        # Build index
        index = self.get_index(prefix)
        # Read files
        r: List[ListItem] = []
        faults = 0
        default_ts = datetime.datetime.now()
        for fp in fingerprints:
            fn = index.get(fp)
            if not fn:
                print(f"ERROR: {fp} is not found")
                faults += 1
                continue
            info = self.read_info(os.path.join(prefix, fn))
            if not info:
                faults += 1
                continue
            # Get place
            top = info.get_app_top_frame()
            if top and top.source:
                place = f"{top.source.file_name}:{top.source.current_line}"
            else:
                place = "unknown"
            #
            r.append(
                ListItem(
                    fingerprint=str(info.fingerprint),
                    exception=str(info.exception),
                    name=info.name,
                    ts=info.timestamp or default_ts,
                    place=place,
                )
            )
        # Get sort key
        # @todo: Make configurable
        sort_key = attrgetter("ts")
        # Print
        W_FINGER = 36
        W_EXCEPTION = 20
        W_SERVICE = 29
        W_TS = 30
        W_PLACE = 50
        print(
            " ".join(
                [
                    self.col("Fingreprint", W_FINGER),
                    self.col("Exception", W_EXCEPTION),
                    self.col("Service", W_SERVICE),
                    self.col("Time", W_TS),
                    self.col("Place", W_PLACE),
                ]
            )
        )
        print(
            " ".join(
                [
                    "-" * W_FINGER,
                    "-" * W_EXCEPTION,
                    "-" * W_SERVICE,
                    "-" * W_TS,
                    "-" * W_PLACE,
                ]
            )
        )
        for item in sorted(r, key=sort_key, reverse=False):
            print(
                " ".join(
                    [
                        self.col(str(item.fingerprint), W_FINGER),
                        self.col(item.exception, W_EXCEPTION),
                        self.col(item.name, W_SERVICE),
                        self.col(item.ts.isoformat(), W_TS),
                        self.rcol(item.place, W_PLACE),
                    ]
                )
            )
        return ExitCode.OK if not faults else ExitCode.CANNOT_READ

    @staticmethod
    def iter_fingerprints(items: List[str], prefix: str) -> Iterable[str]:
        """
        Resolve fingerprint expressions and iterate result.

        Fingerprint expressions is a list user-defined expressions
        passed via command line. Each item may be:

        * `<UUID>` - single fingerprint
        * `all` or `*` - all errors

        Args:
            items: List of expressions.
            prefix: Error info directory

        Returns:
            Yields all resolved fingerprints.
        """

        def is_uuid(fp: str) -> bool:
            """Check string is uuid."""
            try:
                uuid.UUID(fp)
                return True
            except ValueError:
                return False

        def resolve_all() -> Iterable[str]:
            """Resolve all fingerprints."""
            for n in os.listdir(prefix):
                fp = n.split(".")[0]
                if is_uuid(fp):
                    yield fp

        def iter_resolve(expr: str) -> Iterable[str]:
            """
            Resolve single expression.

            Args:
                expr: Expression

            Returns:
                Yield all resolved fingerprints.
            """
            if expr in ("all", "*"):
                yield from resolve_all()
            elif is_uuid(expr):
                # Single fingerprint
                yield expr
            else:
                # Invalid fingerprint
                raise SyntaxError(expr)

        seen: Set[str] = set()
        for expr in items:
            seen.update(iter_resolve(expr))
        yield from seen

    @staticmethod
    def get_index(prefix: str) -> Dict[str, str]:
        """
        Get fingerprint index.

        Args:
            prefix: Error Info directory prefix

        Returns:
            Dict of fingerprint -> file name
        """
        return {fn.split(".")[0]: fn for fn in os.listdir(prefix)}

    def handle_view(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """
        Show the details of the selected errors.

        Args:
            ns: argsparse.Namespace with fields:

                * `prefix` - directory of errorinfo files.
                * `format` - output format:

                    * `terse`
                    * `extend`

                * `fingerprints` - List of fingerprint expressions.

        Returns:
            Exit code.
        """
        # Get formatter
        try:
            formatter = get_formatter(ns.format)
        except ValueError:
            print(
                f"ERROR: Invalid format {ns.format}. "
                "Must be one of: terse, extend"
            )
            return ExitCode.INVALID_ARGS
        #
        prefix = ns.prefix
        # Check if the directory exists
        code = self.__check_dir(prefix)
        if code != ExitCode.OK:
            return code
        # Resolve expressions
        try:
            fingerprints = list(
                self.iter_fingerprints(ns.fingerprints, prefix)
            )
        except SyntaxError as e:
            print(f"ERROR: Invalid expression {e!s}")
            return ExitCode.SYNTAX
        # List all files
        index = self.get_index(prefix)
        #
        faults = 0
        for fp in fingerprints:
            path = index.get(fp)
            if not path:
                print(f"{fp} is not found")
                faults += 1
                continue
            info = self.read_info(os.path.join(prefix, path))
            if info is None:
                faults += 1
                continue
            # Format output through middleware
            print(formatter.format(info))
        return ExitCode.OK if not faults else ExitCode.CANNOT_READ

    def handle_clear(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """
        Clear selected errors.

        Args:
            ns: argsparse.Namespace with fields:

                * `prefix` - directory of errorinfo files.
                * `fingerprints` - List of fingerprint expressions.

        Returns:
            Exit code.
        """
        #
        prefix = ns.prefix
        # Check if the directory exists
        code = self.__check_dir(prefix)
        if code != ExitCode.OK:
            return code
        # Resolve expressions
        try:
            fingerprints = list(
                self.iter_fingerprints(ns.fingerprints, prefix)
            )
        except SyntaxError as e:
            print(f"ERROR: Invalid expression {e!s}")
            return ExitCode.SYNTAX
        # List all files
        index = self.get_index(prefix)
        #
        faults = 0
        for fp in fingerprints:
            path = index.get(fp)
            if not path:
                print(f"{fp} is not found")
                faults += 1
                continue
            full_path = os.path.join(prefix, path)
            try:
                os.unlink(full_path)
            except OSError as e:
                print(f"ERROR: Cannot remove file {full_path}: {e}")
                faults += 1
        return ExitCode.OK if not faults else ExitCode.CANNOT_READ

    @staticmethod
    def read_info(path: str) -> Optional[ErrorInfo]:
        """
        Read error info file.

        Args:
            path: JSON file path

        Returns:
          * [ErrorInfo][gufo.err.ErrorInfo] instance,
              if file has been read correctly.
          * `None` otherwise.
        """
        compressor = Compressor.autodetect(path)
        try:
            with open(path, "rb") as f:
                data = compressor.decode(f.read())
        except FileNotFoundError:
            print(f"ERROR: File {path} is not found")
            return None
        return from_json(data.decode())

    def get_handler(
        self: "Cli", name: str
    ) -> Callable[[argparse.Namespace], ExitCode]:
        """
        Get handler for command.

        Return the handler for furher command processing.

        Args:
            name: Command name

        Returns:
            Callable, accepting argparse.Namespace
            and returning ExitCode.
        """
        h: Callable[[argparse.Namespace], ExitCode] = getattr(
            self, f"handle_{name}"
        )
        return h

    def run(self: "Cli", args: List[str]) -> ExitCode:
        """
        Main dispatcher function.

        Args:
            args: List of command-line arguments.
        """
        parser = argparse.ArgumentParser(
            prog="err", description="Gufo Err reporting tool"
        )
        parser.add_argument(
            "-p",
            "--prefix",
            default=os.environ.get("GUFO_ERR_PREFIX"),
            help="JSON directory path",
        )
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # version
        subparsers.add_parser("version", help="Show Gufo Err version")
        # list
        list_parser = subparsers.add_parser(
            "list", help="Show the list of the registered errors"
        )
        list_parser.add_argument(
            "fingerprints",
            nargs=argparse.REMAINDER,
            help="Error Info fingerprint expressions",
        )
        # view
        view_parser = subparsers.add_parser("view", help="View error report")
        view_parser.add_argument(
            "-f",
            "--format",
            default="extend",
            help="Output format: terse, extend",
        )
        view_parser.add_argument(
            "fingerprints",
            nargs=argparse.REMAINDER,
            help="Error Info fingerprint expressions",
        )
        # clear
        clear_parser = subparsers.add_parser("clear", help="Remove error info")
        clear_parser.add_argument(
            "fingerprints",
            nargs=argparse.REMAINDER,
            help="Error Info fingerprint expressions",
        )
        ns = parser.parse_args(args)
        handler = self.get_handler(ns.cmd)
        return handler(ns)


def main() -> int:
    """Run err utility with command-line arguments."""
    return Cli().run(sys.argv[1:]).value
