from collections import namedtuple

Coordinate = namedtuple("Coordinate", "lat lon")  # ["lan", "lon"]
print(issubclass(Coordinate, tuple))  # True
moscow = Coordinate(55.756, 37.617)
print(moscow)  # Coordinate(lat=55.756, lon=37.617)
lan, lon = moscow  # unpack
print(lan, lon)  # 55.756 37.617
print(moscow == Coordinate(lat=55.756, lon=37.617))
print(moscow.__doc__)  # Coordinate(lat, lon)
