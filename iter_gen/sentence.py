import re
import reprlib


class SentenceV1:
    def __init__(self, text):
        self._text = text
        self._words = re.compile(r"\w+").findall(text)

    def __repr__(self):
        return f"{self.__class__.__name__}({reprlib.repr(self._text)})"

    def __getitem__(self, index):
        return self._words[index]


class SentenceV2:
    def __init__(self, text):
        self._text = text
        self._words = re.compile(r"\w+").findall(text)

    def __repr__(self):
        return f"{self.__class__.__name__}({reprlib.repr(self._text)})"

    def __iter__(self):
        return SentenceV2Iterator(self._words)


class SentenceV2Iterator:
    def __init__(self, words):
        self._words = words
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._words):
            raise StopIteration()
        else:
            word = self._words[self._index]
            self._index += 1
            return word


class SentenceV3:
    def __init__(self, text):
        self._text = text
        self._words = re.compile(r"\w+").findall(text)

    def __repr__(self):
        return f"{self.__class__.__name__}({reprlib.repr(self._text)})"

    def __iter__(self):
        # for word in self._words:
        #     yield word
        yield from self._words


if __name__ == "__main__":
    # print("*" * 40, "SentenceV1", "*" * 40)
    # s1 = SentenceV1('"The time has come," the Walrus said,')
    # print(s1)
    # for word in s1:
    #     print(word, end=", ")
    # print("\n", list(s1), sep="")

    # print("\n" + "*" * 40, "SentenceV2", "*" * 40)
    # s2 = SentenceV2('"The time has come," the Walrus said,')
    # print(s2)
    # it = iter(s2)
    # while True:
    #     try:
    #         value = next(it)
    #         print(value, end=", ")
    #     except StopIteration:
    #         del it
    #         break
    # print("\n", list(s2), sep="")

    print("\n" + "*" * 40, "SentenceV3", "*" * 40)
    s3 = SentenceV3('"The time has come," the Walrus said,')
    print(s3)
    for word in s3:
        print(word, end=", ")
    print("\n", list(s3), sep="")
