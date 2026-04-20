from collections import namedtuple
from typing import TYPE_CHECKING, NamedTuple, reveal_type

# Point1 = NamedTuple("Point1", [("x", float), ("y", float), ("units", str)])


# class Point2(NamedTuple):
#     x: float
#     y: float
#     units: str = "meters"


# class Point(NamedTuple):
#     x: float
#     y: float
#     units: str = "meters"


# class PointWithName(Point):
#     name: str


# pn = PointWithName(0.0, 0.0)
# pn.name = "Origin"
# x, y, _ = pn
# print(pn)
# print(x, y, pn.name)


# class Coordinate(NamedTuple):
#     lat: float
#     lon: float


# # Creating NamedTuple classes using keyword arguments is deprecated and will be disallowed in Python 3.15
# # Coordinate = NamedTuple("Coordinate", lat=float, lon=float)
# print(issubclass(Coordinate, tuple))
# moscow = Coordinate(55.756, 37.617)
# print(moscow)
# print(moscow == Coordinate(lat=55.756, lon=37.617))


# class Property[T](NamedTuple):
#     name: str
#     value: T


# # uv run mypy ...
# if TYPE_CHECKING:
#     # Revealed type is "tuple[str, float, fallback=typing_namedtuple.Property[float]]"
#     reveal_type(Property("height", 3.4))


class Point(NamedTuple):
    x: float
    y: float
    units: str = "meters"


Color = NamedTuple("Color", [("red", str), ("green", str), ("blue", str)])
print(Point.__annotations__)
print(Color.__annotations__)

Pixel = NamedTuple("Pixel", (Point.__annotations__ | Color.__annotations__).items())
print(Pixel(x=3.0, y=4.0, units="meters", red="255", green="255", blue="0"))
