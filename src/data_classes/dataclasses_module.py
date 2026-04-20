from dataclasses import dataclass


@dataclass
class InventoryItem:
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def __init__(
        self,
        name: str,
        unit_price: float,
        quantity_on_hand: int = 0,
    ):
        self.name = name
        self.unit_price = unit_price
        self.quantity_on_hand = quantity_on_hand


ii = InventoryItem()


@dataclass
class DataClass: ...


@dataclass()
class DataClass: ...


@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
class DataClass: ...
