from typing import Generator, NamedTuple


class Result(NamedTuple):
    total: float
    count: int
    average: float


class Sentinel:
    def __repr__(self):
        return "<Sentinel>"


STOP = Sentinel()


def averager(verbose: bool = False) -> Generator[None, float | Sentinel, Result]:
    total = 0.0
    count = 0
    average = 0.0
    while True:
        term = yield
        if verbose:
            print("Received:", term)
        if isinstance(term, Sentinel):
            break
        total += term
        count += 1
        average = total / count
    return Result(total, count, average)


if __name__ == "__main__":
    coro_avg = averager()
    next(coro_avg)  # 启动执行生成器函数
    coro_avg.send(10)
    coro_avg.send(30)
    coro_avg.send(6.5)
    # print(coro_avg.close())
    coro_avg.send(STOP)

