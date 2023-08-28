def oops():
    msg = "oops"
    raise RuntimeError(msg)


def to_oops():
    x = 1
    x += 1
    oops()


def entry():
    s = 2
    s += 1
    to_oops()
