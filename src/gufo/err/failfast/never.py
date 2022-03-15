# ---------------------------------------------------------------------
# Gufo Err: NeverFailFast
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Type
from types import TracebackType

# Gufo Labs modules
from ..abc.failfast import BaseFailFast
from ..err import Err


class NeverFailFast(BaseFailFast):
    def must_die(
        self,
        err: "Err",
        t: Type[BaseException],
        v: BaseException,
        tb: TracebackType,
    ) -> bool:
        return False
