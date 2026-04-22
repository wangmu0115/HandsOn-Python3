def inner():
    yield "inner"


def middle():
    # inner()
    for v in inner():
        yield v


def outer():
    # middle()
    for v in middle():
        yield v
    yield "outer"


print(next(outer()))
