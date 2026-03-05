import sys


class LookingMirror:
    def __enter__(self):
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return "HelloWorld"

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print("DO NOT divide by zero!")
            return True
        # Any other exception raised in the with block will be propagated.

    def reverse_write(self, text):
        self.original_write(text[::-1])


if __name__ == "__main__":
    with LookingMirror() as lm:
        print(lm)
        print("Alice, Kitty and Snowdrop")
        # open("123.txt")
        12 / 0  # ZeroDivisionError

    print("Alice, Kitty and Snowdrop")
