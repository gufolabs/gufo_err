# ---------------------------------------------------------------------
# Gufo Err: err singleton
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import sys
import os
from typing import Optional, Type, List, Iterable, Callable
from types import TracebackType
from uuid import UUID
import hashlib

# Gufo Labs modules
from .types import ErrorInfo, FrameInfo
from .frame import iter_frames

DEFAULT_NAME = "unknown"
DEFAULT_VERSION = "unknown"
DEFAULT_HASH = "sha1"
DEFAULT_EXIT_CODE = 1


class Err(object):
    """
    Error handling singleton.

    Example:

        ```
        from gufo.err import err

        err.setup()
        ```
    """

    def __init__(self):
        self.__name = DEFAULT_NAME
        self.__version = DEFAULT_VERSION
        self.__hash_fn = hashlib.sha1
        self.__initialized = False
        self.__failfast_chain: List[
            Callable[[Type[BaseException], BaseException, TracebackType], bool]
        ] = []
        self.__response_chain = []
        self.__failfast_code = DEFAULT_EXIT_CODE
        self.__root_module: Optional[str] = None

    def process(self) -> None:
        """
        Process current exception context in the fenced code block.

        Example:

            ```
            from gufo.err import err

            ...
            try:
                my_function()
            except Exception:
                err.process()
            ```
        """
        t, v, tb = sys.exc_info()
        if not t or not v or not tb:
            return  # Not an exception context
        self.__process(t, v, tb)

    def __process(
        self,
        t: Type[BaseException],
        v: BaseException,
        tb: Optional[TracebackType] = None,
    ) -> None:
        """
        Process given exception context. Called either from .process()
        or as sys.excepthook for unhandled exceptions.

        Args:
            t: Exception type.
            v: Exception value.
            tb: Traceback frame.
        """
        if not self.__initialized:
            raise RuntimeError("setup() is not called")
        if not tb:
            return
        if t in (SystemExit, KeyboardInterrupt):
            raise  # Do not mess the exit sequence
        if self.__must_die(t, v, tb):
            os._exit(self.__failfast_code)  # Fatal error, die quickly
        # Collect stack frames
        # @todo: separate handling of endless recursion
        stack = list(iter_frames(tb))
        # Calculate error fingerprint
        fp = self.__fingerprint(t, v, stack)
        # Build stack info
        err_info = ErrorInfo(
            name=self.__name,
            version=self.__version,
            fingerprint=fp,
            stack=stack,
            exception=v,
        )
        # Process the response
        self.__do_response(err_info)

    def setup(
        self,
        catch_all: bool = False,
        root_module: Optional[str] = None,
        name: str = DEFAULT_NAME,
        version: str = DEFAULT_VERSION,
        hash: str = DEFAULT_HASH,
        fail_fast: Optional[
            Iterable[
                Callable[
                    [Type[BaseException], BaseException, TracebackType], bool
                ]
            ]
        ] = None,
        fail_fast_code: int = DEFAULT_EXIT_CODE,
        response: Optional[
            Iterable[Callable[["Err", ErrorInfo], None]]
        ] = None,
    ):
        """
        Setup error handling singleton. Must be called
        only once. Raises RuntimeError when called twice.

        Args:
            catch_all: Install global system exception hook.
            name: Application or service name.
            version: Application or service version.
            root_module: Top-level application module/namespace for
                split stack fingerprinting. Topmost frame from the root or
                the nested modules will be considered in the error
                fingerprint.
            hash: Fingerprint hashing function name. Available functions
                are: sha256, sha3_512, blake2s, sha3_224, md5, sha384,
                sha3_256, shake_256, blake2b, sha224, shake_128, sha3_384,
                sha1, sha512. Refer to the Python's hashlib for details.
            fail_fast: Iterable of callable for fail-fast detection.
                Process will terminate with `fail_fast_code` error code
                if any of callables in the chain will return True.
                Callables are evaluated in the order of appearance, accept
                sys.exc_info() result as positional arguments and return
                the boolean type.
            fail_fast_code: System exit code on fail-fast termination.
            response: Iterable of callable for error response.
                Callables are evaluated in the order of appearance
                and accept Err and ErrorInfo instance as arguments.
        """
        if self.__initialized:
            raise RuntimeError("Already initialized")
        # Install system-wide exception hook
        if catch_all:
            sys.excepthook = self.__process
        # Init parameters
        self.__name = name or DEFAULT_NAME
        self.__version = version or DEFAULT_VERSION
        self.__failfast_code = fail_fast_code
        self.__root_module = root_module
        try:
            self.__hash_fn = getattr(hashlib, hash)
        except AttributeError:
            raise RuntimeError(f"Unknown hash: {hash}")
        # Initialize fail fast chain
        if fail_fast:
            self.__failfast_chain = list(fail_fast)
        else:
            self.__failfast_chain = []
        # Initialize response chain
        if response:
            self.__response_chain = list(response)
        else:
            self.__response_chain = []
        # Mark as initialized
        self.__initialized = True

    def __must_die(
        self,
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Process fail-fast sequence and return True if the
        process must die quickly.
        """
        if not tb:
            return False
        return any(f(t, v, tb) for f in self.__failfast_chain)

    def __do_response(self, err_info: ErrorInfo) -> None:
        """
        Process all the error response.

        Args:
            err_info: Filled ErrorInfo structure
        """
        for resp in self.__response_chain:
            try:
                resp(self, err_info)
            except Exception:
                ...  # @todo: Report error

    def iter_fingerprint_parts(
        self,
        t: Type[BaseException],
        v: BaseException,
        stack: List[FrameInfo],
    ) -> Iterable[str]:
        """
        Iterable to yield all fingerprint parts.
        May be overriden in subclasses.

        Args:
            t: Exception type.
            v: Exception instance:
            stack: Current stack.
        Returns:
            Iterable of strings.
        """
        yield self.__name  # Service name
        yield self.__version  # Service version
        yield t.__name__  # Exception class
        # Top-level stack info
        if stack:
            top = stack[0]
            if top.source:
                yield top.source.file_name or "unknown"  # Top module
            yield top.name  # Top callable name
            if top.source:
                yield str(top.source.current_line)  # Top execution line
        # Application stack info
        if self.__root_module:
            app_top = None
            prefix = f"{self.__root_module}."
            for frame in stack:
                if frame.module and (
                    frame.module == self.__root_module
                    or frame.module.startswith(prefix)
                ):
                    app_top = frame
                    break
            if app_top:
                if app_top.source:
                    yield app_top.source.file_name or "unknown"  # Top module
                yield app_top.name  # Top callable name
                if app_top.source:
                    yield str(
                        app_top.source.current_line
                    )  # Top execution line

    def __fingerprint(
        self,
        t: Type[BaseException],
        v: BaseException,
        stack: List[FrameInfo],
    ) -> UUID:
        """
        Calculate error fingerprint for given exception
        and the stack. Fingerprint is stable for repeating
        conditions.

        Args:
            t: Exception type.
            v: Exception instance:
            stack: Current stack.

        Returns:
            Error fingerprint as UUID.
        """
        fp_hash = self.__hash_fn(
            b"\x00".join(
                x.encode("utf-8")
                for x in self.iter_fingerprint_parts(t, v, stack)
            )
        ).digest()
        return UUID(bytes=fp_hash[:16], version=5)

    def add_fail_fast(
        self,
        func: Callable[
            [Type[BaseException], BaseException, TracebackType], bool
        ],
    ) -> None:
        """
        Add fail-fast handler to the end of the chain.

        Args:
            func: Callable, accepting sys.exc_info() output and returning bool.
                True should be returned on unrecoverable error which leads to
                immediate process termination.
        """
        self.__failfast_chain.append(func)

    def add_response(self, func: Callable[["Err", ErrorInfo], None]) -> None:
        """
        Add response handler to the end of the chain.

        Args:
            func: Callable, accepting Err and Error info instances.
        """
        self.__response_chain.append(func)


# Define the singleton
err = Err()
