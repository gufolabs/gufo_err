from gufo.err import err

err.setup(format="extend")


def fail():
    x = 1
    x += 1
    msg = "failing"
    raise RuntimeError(msg)


try:
    fail()
except Exception:
    err.process()
