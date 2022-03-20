from gufo.err import err

err.setup(catch_all=True, format="extend")


def fail():
    x = 1
    x += 1
    raise RuntimeError("failing")


fail()
