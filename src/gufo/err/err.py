# ---------------------------------------------------------------------
# Gufo Err: err singleton
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import sys
import os
from typing import Optional, Type, List, Iterable
from types import TracebackType
from uuid import UUID
import hashlib

# Gufo Labs modules
from .types import ErrorInfo, FrameInfo
from .frame import iter_frames
from .abc.failfast import BaseFailFast
from .abc.middleware import BaseMiddleware
from .logger import logger


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

    def __init__(self) -> None:
        self.__name = DEFAULT_NAME
        self.__version = DEFAULT_VERSION
        self.__hash_fn = hashlib.sha1
        self.__initialized = False
        self.__failfast_chain: List[BaseFailFast] = []
        self.__middleware_chain: List[BaseMiddleware] = []
        self.__failfast_code = DEFAULT_EXIT_CODE
        self.__root_module: Optional[str] = None

    def process(self) -> None:
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
        self.__run_middleware(err_info)

    def setup(
        self,
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
    ) -> "Err":
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
        Returns:
            Err instance.
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
            self.__failfast_chain = []
            for ff in fail_fast:
                self.add_fail_fast(ff)
        else:
            self.__failfast_chain = []
        # Initialize response chain
        if middleware:
            self.__middleware_chain = self.__default_middleware(format=format)
            for resp in middleware:
                self.add_middleware(resp)
        else:
            self.__middleware_chain = self.__default_middleware(format=format)
        # Mark as initialized
        self.__initialized = True
        return self

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
        return any(ff.must_die(t, v, tb) for ff in self.__failfast_chain)

    def __run_middleware(self, err_info: ErrorInfo) -> None:
        """
        Process all the middleware.

        Args:
            err_info: Filled ErrorInfo structure
        """
        for resp in self.__middleware_chain:
            try:
                resp.process(err_info)
            except Exception as e:
                logger.error("%r middleware failed: %s", resp, e)

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

    def add_fail_fast(self, ff: BaseFailFast) -> None:
        """
        Add fail-fast handler to the end of the chain.

        Args:
            ff: BaseFailFast instance.
        """
        if not isinstance(ff, BaseFailFast):
            raise ValueError(
                "add_fail_fast() argument must be BaseFailFast instance"
            )
        self.__failfast_chain.append(ff)

    def add_middleware(self, mw: BaseMiddleware) -> None:
        """
        Add middleware to the end of the chain.

        Args:
            mw: BaseMiddleware instance
        """
        if not isinstance(mw, BaseMiddleware):
            raise ValueError(
                "add_response() argument must be BaseResponse instance"
            )
        self.__middleware_chain.append(mw)

    def __default_middleware(
        self, format: Optional[str] = None
    ) -> List[BaseMiddleware]:
        """
        Get default middleware chain.

        Args:
            format: traceback format. See TracebackMiddleware for details.
                Do not configure tracebacks if None.
        """
        r: List[BaseMiddleware] = []
        if format is not None:
            from .middleware.traceback import TracebackMiddleware

            r.append(TracebackMiddleware(format=format))
        return r


# Define the singleton
err = Err()
