import functools

from utils.timer import clock


@functools.lru_cache
@clock
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    print(fibonacci(6))
    print(fibonacci.cache_parameters())
    print(fibonacci.cache_info())
    print(fibonacci.cache_clear())
