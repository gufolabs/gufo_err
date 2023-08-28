from gufo.err import err

err.setup(catch_all=True)


def fail():
    msg = "failing"
    raise RuntimeError(msg)


fail()
