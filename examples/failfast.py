from typing import Type
from types import TracebackType
from gufo.err import err, BaseFailFast


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
    raise RuntimeError("failing")


try:
    fail()
except Exception:
    err.process()
print("Stopping")
