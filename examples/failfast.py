from types import TracebackType
from typing import Type

from gufo.err import BaseFailFast, err


class FailOnType(BaseFailFast):
    def __init__(self, exc_type) -> None:
        super().__init__()
        self.exc_type = exc_type

    def must_die(
        self, t: Type[BaseException], v: BaseException, tb: TracebackType
    ) -> bool:
        return t == self.exc_type


err.setup(fail_fast=[FailOnType(RuntimeError)], fail_fast_code=5)


def fail():
    msg = "failing"
    raise RuntimeError(msg)


try:
    fail()
except Exception:
    err.process()
print("Stopping")
