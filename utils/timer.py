import functools
import time


def clock(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - t0
            arg_list = [repr(arg) for arg in args]
            arg_list.extend([f"{k}={v!r}" for k, v in kwargs])
            print(f"[{elapsed:0.8f}s] {func.__name__}({', '.join(arg_list)}) -> {result!r}")

    return wrapped
