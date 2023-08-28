from gufo.err import err

err.setup(catch_all=True, format="extend")


def fail():
    x = 1
    x += 1
    msg = "failing"
    raise RuntimeError(msg)


fail()
