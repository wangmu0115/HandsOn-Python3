class Averager:
    def __init__(self):
        self._series = []

    def __call__(self, new_value):
        self._series.append(new_value)
        total = sum(self._series)

        return total / len(self._series)


def make_averager():
    series = []

    def averager(new_value):
        series.append(new_value)
        return sum(series) / len(series)

    return averager


def make_averager2():
    count = 0
    total = 0

    def averager(new_value):
        nonlocal total, count
        total += new_value
        count += 1

        return total / count

    return averager


if __name__ == "__main__":
    avg_oo = Averager()
    print(avg_oo(10), avg_oo(11), avg_oo(12))

    avg1 = make_averager()
    print(avg1(10), avg1(11), avg1(12))

    avg2 = make_averager2()
    print(avg2(10), avg2(11), avg2(12))
