# def g():
#     i = next(me)
#     yield i


# me = g()
# next(me)


# # # def f1():
# # #     try:
# # #         return
# # #     except Exception:
# # #         yield 1


# # # def f2():
# # #     try:
# # #         raise StopIteration()
# # #     except Exception as e:
# # #         print(type(e))
# # #         yield 42


# # # # print(next(f1()))
# # # print(next(f2()))
# # # print(list(f1()))
# # # print(list(f2()))


# # # def g():
# # #     yield 1
# # #     raise StopIteration


# # # list(g())


# # # def gen():
# # #     try:
# # #         yield 1
# # #         yield 2
# # #     except GeneratorExit:
# # #         print("Clean up")
# # #         raise ValueError


# # # g = gen()
# # # print(next(g))  # 1
# # # g.close()


# # def gen():
# #     x = yield 42
# #     print("x is:", x)
# #     yield


# # g = gen()
# # next(g)  # prime，将执行推进到第一个 yield 表达式处
# # # next(g)  # 使用 next() 恢复，输出 `x is: None`
# # # g.send(9)  # 使用 send() 恢复，输出 `x is: 9`


# def fib():
#     a, b = 0, 1
#     while True:
#         yield a
#         a, b = b, a + b


# gen = fib()
# # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
# print([next(gen) for _ in range(10)])


def gen():
    yield 1
    raise StopIteration


g = gen()
print(next(g))
print(next(g))
