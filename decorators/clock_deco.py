import time

from utils.timer import clock


@clock
def snooze(seconds):
    time.sleep(seconds)


@clock
def factorial(n):
    return 1 if n <= 1 else n * factorial(n - 1)


if __name__ == "__main__":
    print("*" * 30, "Calling snooze()", "*" * 30)
    snooze(1.0)
    print("*" * 30, "Calling factorial()", "*" * 30)
    print("10! =", factorial(10))

    print(factorial.__name__)
