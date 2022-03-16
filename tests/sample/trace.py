def oops():
    raise RuntimeError("oops")


def to_oops():
    x = 1
    x += 1
    oops()


def entry():
    s = 2
    s += 1
    to_oops()
