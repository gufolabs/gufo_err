# ---------------------------------------------------------------------
# Gufo Err: err singleton
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""
Define `Err` class and `err` singleton.

Attributes:
    err: Err singletone.
"""
# Python modules
import hashlib
import os
import sys
from types import TracebackType
from typing import Iterable, List, Optional, Type
from uuid import UUID

from .abc.failfast import BaseFailFast
from .abc.middleware import BaseMiddleware
from .frame import iter_frames
from .logger import logger

# Gufo Labs modules
from .types import ErrorInfo, FrameInfo

DEFAULT_NAME = "unknown"
DEFAULT_VERSION = "unknown"
DEFAULT_HASH = "sha1"
DEFAULT_EXIT_CODE = 1


class Err(object):
    """
    Error handling singleton.

    Example:
        ``` py
        from gufo.err import err

        err.setup()
        ```
    """

    def __init__(self: "Err") -> None:
        self.__name = DEFAULT_NAME
        self.__version = DEFAULT_VERSION
        self.__hash_fn = hashlib.sha1
        self.__initialized = False
        self.__failfast_chain: List[BaseFailFast] = []
        self.__middleware_chain: List[BaseMiddleware] = []
        self.__failfast_code = DEFAULT_EXIT_CODE
        self.__root_module: Optional[str] = None

    def process(self: "Err") -> None:
        """
        Process current exception context in the fenced code block.

        Example:
            ``` py
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
        self: "Err",
        t: Type[BaseException],
        v: BaseException,
        tb: Optional[TracebackType] = None,
    ) -> None:
        """
        Process given exception context.

        Called either from .process()
        or as sys.excepthook for unhandled exceptions.

        Args:
            t: Exception type.
            v: Exception value.
            tb: Traceback frame.

        Raises:
            RuntimeError: If setup() is not called.
        """
        if not self.__initialized:
            msg = "setup() is not called"
            raise RuntimeError(msg)
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
            root_module=self.__root_module,
        )
        # Process the response
        self.__run_middleware(err_info)

    def setup(
        self: "Err",
        *,
        catch_all: bool = False,
        root_module: Optional[str] = None,
        name: str = DEFAULT_NAME,
        version: str = DEFAULT_VERSION,
        hash: str = DEFAULT_HASH,
        fail_fast: Optional[Iterable[BaseFailFast]] = None,
        fail_fast_code: int = DEFAULT_EXIT_CODE,
        middleware: Optional[Iterable[BaseMiddleware]] = None,
        format: Optional[str] = "terse",
        error_info_path: Optional[str] = None,
        error_info_compress: Optional[str] = None,
    ) -> "Err":
        """
        Setup error handling singleton.

        Must be called only once.

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
            fail_fast: Iterable of BaseFailFast instances for fail-fast
                detection.
                Process will terminate with `fail_fast_code` error code
                if any of instances in the chain will return True.
            fail_fast_code: System exit code on fail-fast termination.
            middleware: Iterable of BaseMiddleware instances
                for error processing middleware.
                Instances are evaluated in the order of appearance.
            format: If not None install TracebackMiddleware for given
                output format.
            error_info_path: If not None install ErrorInfoMiddleware.
                `error_info_path` should point to a writable directories,
                in which the error info files to be written.
            error_info_compress: Used only with `error_info_path`.
                Set error info compression method. One of:

                * `None` - do not compress
                * `gz` - GZip
                * `bz2` - BZip2
                * `xz` - LZMA/xz

        Returns:
            Err instance.

        Raises:
            RuntimeError: When called twice.
            ValueError: On configuration parameters error.
        """
        if self.__initialized:
            msg = "Already initialized"
            raise RuntimeError(msg)
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
        except AttributeError as e:
            msg = f"Unknown hash: {hash}"
            raise ValueError(msg) from e
        # Initialize fail fast chain
        if fail_fast:
            self.__failfast_chain = []
            for ff in fail_fast:
                self.add_fail_fast(ff)
        else:
            self.__failfast_chain = []
        # Initialize response chain
        if middleware:
            self.__middleware_chain = self.__default_middleware(
                format=format,
                error_info_path=error_info_path,
                error_info_compress=error_info_compress,
            )
            for resp in middleware:
                self.add_middleware(resp)
        else:
            self.__middleware_chain = self.__default_middleware(
                format=format,
                error_info_path=error_info_path,
                error_info_compress=error_info_compress,
            )
        # Mark as initialized
        self.__initialized = True
        return self

    def __must_die(
        self: "Err",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Check if the error is fatal and the process must die.

        Process fail-fast sequence and return True if the
        process must die quickly.
        """
        if not tb:
            return False
        return any(ff.must_die(t, v, tb) for ff in self.__failfast_chain)

    def __run_middleware(self: "Err", err_info: ErrorInfo) -> None:
        """
        Process all the middleware.

        Args:
            err_info: Filled ErrorInfo structure
        """
        for resp in self.__middleware_chain:
            try:
                resp.process(err_info)
            except Exception as e:  # noqa: BLE001
                logger.error("%r middleware failed: %s", resp, e)

    def iter_fingerprint_parts(
        self: "Err",
        t: Type[BaseException],
        v: BaseException,
        stack: List[FrameInfo],
    ) -> Iterable[str]:
        """
        Iterate over the fingerprint parts.

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
            yield top.module or "unknown"  # Top module
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
                yield app_top.module or "unknown"  # App module
                yield app_top.name  # App module Current callable name
                if app_top.source:
                    yield str(
                        app_top.source.current_line
                    )  # App execution line

    def __fingerprint(
        self: "Err",
        t: Type[BaseException],
        v: BaseException,
        stack: List[FrameInfo],
    ) -> UUID:
        """
        Calculate the error fingerprint.

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

    def add_fail_fast(self: "Err", ff: BaseFailFast) -> None:
        """
        Add fail-fast handler to the end of the chain.

        Args:
            ff: BaseFailFast instance.

        Raises:
            ValueError: If `ff` is not BaseFailFast instance.
        """
        if not isinstance(ff, BaseFailFast):
            msg = "add_fail_fast() argument must be BaseFailFast instance"
            raise ValueError(msg)
        self.__failfast_chain.append(ff)

    def add_middleware(self: "Err", mw: BaseMiddleware) -> None:
        """
        Add middleware to the end of the chain.

        Args:
            mw: BaseMiddleware instance

        Raises:
            ValueError: If `mw` is not BaseMiddleware instance.
        """
        if not isinstance(mw, BaseMiddleware):
            msg = "add_response() argument must be BaseMiddleware instance"
            raise ValueError(msg)
        self.__middleware_chain.append(mw)

    def __default_middleware(
        self: "Err",
        format: Optional[str] = None,
        error_info_path: Optional[str] = None,
        error_info_compress: Optional[str] = None,
    ) -> List[BaseMiddleware]:
        """
        Get default middleware chain.

        Args:
            format: traceback format. See TracebackMiddleware for details.
                Do not configure tracebacks if None.
            error_info_path: Directory path to write error info.
                See ErrorInfoMiddleware for details.
                Do not configure middleware if None.
            error_info_compress: Error info compression algorithm. Used along
                with `error_info_path`.
        """
        r: List[BaseMiddleware] = []
        if format is not None:
            from .middleware.traceback import TracebackMiddleware

            r.append(TracebackMiddleware(format=format))
        if error_info_path is not None:
            from .middleware.errorinfo import ErrorInfoMiddleware

            r.append(
                ErrorInfoMiddleware(
                    path=error_info_path, compress=error_info_compress
                )
            )
        return r


# Define the singleton
err = Err()
