from typing import TypedDict


class BookDict(TypedDict):
    isbn: str
    title: str
    authors: list[str]
    pagecount: int


book1 = BookDict(isbn="0201657880", title="Programming Pearls", authors="Jon Bentley", pagecount=256)
print(book1)
print(type(book1))
print(book1["title"])
print(BookDict.__annotations__)