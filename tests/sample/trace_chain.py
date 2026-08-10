def oops1():
    msg = "oops"
    raise KeyError(msg)


def oops2():
    x = 1
    x += 1
    oops1()


def oops3():
    x = 1
    x += 1
    try:
        oops2()
    except KeyError as e:
        msg = "reraised"
        raise RuntimeError(msg) from e


def entry_chain():
    s = 2
    s += 1
    oops3()
