from gufo.err import err

err.setup(format="extend")


def fail():
    x = 1
    x += 1
    raise RuntimeError("failing")


try:
    fail()
except Exception:
    err.process()
