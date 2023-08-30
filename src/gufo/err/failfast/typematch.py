# ---------------------------------------------------------------------
# Gufo Err: TypeMatchFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""TypeMatchFailFast."""
# Python modules
from types import TracebackType
from typing import Dict, Optional, Type, Union

# Gufo Labs modules
from ..abc.failfast import BaseFailFast
from ..logger import logger


class TypeMatchFailFast(BaseFailFast):
    """
    Fail-fast on the given exception types and optional substrings.

    Args:
        exc:
            * Exception type.
            * string in form "module.name".
            * None to add matchers later.
        match: Optional substring matcher. Match all when set to None.
        msg: Optional message to show to log before failfast.
            `%s` will be expanded to the exception value.

    Examples:
        Single type:

        ``` py
        err.setup(fail_fast=[TypeMatchFailFast(RuntimeError)])
        ```

        Single type with match:

        ``` py
        err.setup(fail_fast=[TypeMatchFailFast(RuntimeError, match="stopped")])
        ```

        Single type with message:

        ``` py
        err.setup(fail_fast=[
            TypeMatchFailFast(RuntimeError, msg="Runtime Error: %s")
        ])
        ```

        Chaining:
        ``` py
        err.setup(
            fail_fast=[
                TypeMatchFailFast()
                .add_match(DivisionByZero)
                .add_match(ValueError, match="null value")
                .add_match(RuntimeError, msg="Runtime failure: %s")
            ]
        )
        ```
    """

    def __init__(
        self: "TypeMatchFailFast",
        exc: Optional[Union[str, Type[BaseException]]] = None,
        *,
        match: Optional[str] = None,
        msg: Optional[str] = None,
    ) -> None:
        super().__init__()
        # exc name -> match -> msg
        self.__map: Dict[str, Dict[Optional[str], Optional[str]]] = {}
        if exc:
            self.add_match(exc, match=match, msg=msg)

    def add_match(
        self: "TypeMatchFailFast",
        exc: Union[str, Type[BaseException]],
        *,
        match: Optional[str] = None,
        msg: Optional[str] = None,
    ) -> "TypeMatchFailFast":
        """
        Add new exception type for the fail-fast.

        Args:
            exc: Exception type or string in form "module.name".
            match: Optional substring matcher. Match all when set to None.
            msg: Optional message to show to log before failfast.
                `%s` will be expanded to the exception value.

        Returns:
            Self reference to allow chaining.

        Example:
            ``` py
            err.setup(
                fail_fast=[
                    TypeMatchFailFast()
                    .add_match(DivisionByZero)
                    .add_match(ValueError, match="null value")
                    .add_match(RuntimeError, msg="Runtime failure: %s")
                ]
            )
            ```
        """
        # Normalize to string
        xn = exc if isinstance(exc, str) else self.__exc_to_str(exc)
        # Fill mapping
        if xn not in self.__map:
            self.__map[xn] = {}
        self.__map[xn][match] = msg
        return self

    @staticmethod
    def __exc_to_str(t: Type[BaseException]) -> str:
        """
        Convert exception instance to string class name.

        Args:
            t: Exception type

        Returns:
            Class name in form `module.name`
        """
        return f"{t.__module__}.{t.__name__}"

    def must_die(
        self: "TypeMatchFailFast",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        """
        Check if the proceess must die quickly.

        Check if exception class matches given substrings.
        """

        def msg(s: Optional[str]) -> None:
            if not s:
                return
            if "%s" in s:
                logger.critical(s, v)
            else:
                logger.critical(s)

        xn = self.__exc_to_str(t)
        chain = self.__map.get(xn)
        if not chain:
            return False
        # Try to match
        xv = str(v)
        for match in chain:
            if match and match in xv:
                msg(chain[match])
                return True
        # Wildcard match
        if None in chain:
            msg(chain[None])
            return True
        # Not matched
        return False
