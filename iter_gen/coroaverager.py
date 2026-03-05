from typing import Generator


def averager() -> Generator[float, float, None]:
    total = 0.0
    count = 0
    average = 0.0
    while True:
        term = yield average
        total += term
        count += 1
        average = total / count


if __name__ == "__main__":
    coro_avg = averager()
    print(next(coro_avg))  # 执行到 L10，返回 average
    print(coro_avg.send(10))  # 将 L10 的 `yield average` 表达式赋值为 10，然后继续执行直到再次循环到 L10，返回 average
    print(coro_avg.send(11))
    print(coro_avg.send(12))
