def gen():
    v1 = yield 1
    print(v1)
    v2 = yield 2
    print(v2)
    v3 = yield 3
    print(v3)


for v in gen():
    print("v =", v)
