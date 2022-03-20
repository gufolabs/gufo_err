from gufo.err import err

err.setup(catch_all=True)


def fail():
    raise RuntimeError("failing")


fail()
