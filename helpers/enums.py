from enum import IntEnum, StrEnum
from typing import ClassVar, Generic, Self, TypeVar

ValueT = TypeVar("ValueT", int, str)


class LabelEnumMixin(Generic[ValueT]):
    label: str
    aliases: tuple[str, ...]

    _label_map_cs: ClassVar[dict[str, Self]]  # case-sensitive
    _label_map_ci: ClassVar[dict[str, Self]]  # case-insensitive

    def __init_subclass__(cls):
        super().__init_subclass__()

        cs: dict[str, Self] = {}
        ci: dict[str, Self] = {}

        for item in cls:
            texts = (item.label, *item.aliases)
            for text in texts:
                if text in cs and cs[text] is not item:
                    raise ValueError(f"重复的 label/alias: {text}")
                cs[text] = item

                text_ci = text.casefold()
                if text_ci in ci and ci[text_ci] is not item:
                    raise ValueError(f"重复的 label/alias(case-insensitive): {text}")
                ci[text_ci] = item

        cls._label_map_cs = cs
        cls._label_map_ci = ci

    @classmethod
    def safe_from_value(cls, value: ValueT) -> Self | None:
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def from_value(cls, value: ValueT) -> Self:
        return cls(value)

    @classmethod
    def safe_from_label(cls, label: str, *, case_sensitive: bool = True) -> Self | None:
        if case_sensitive:
            return cls._label_map_cs.get(label)
        return cls._label_map_ci.get(label.casefold())

    @classmethod
    def from_label(cls, label: str, *, case_sensitive: bool = True) -> Self:
        item = cls.safe_from_label(label, case_sensitive=case_sensitive)
        if item is None:
            raise ValueError(f"{label!r} is not a valid label/alias for {cls.__name__}")
        return item

    def to_dict(self) -> dict[str, int | str | tuple[str, ...]]:
        return {
            "name": self.name,
            "value": self.value,
            "label": self.label,
            "aliases": self.aliases,
        }


class LabelIntEnum(LabelEnumMixin[int], IntEnum):
    def __new__(cls, value: int, label: str, *aliases: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.aliases = tuple(aliases)
        return obj


class LabelStrEnum(LabelEnumMixin[str], StrEnum):
    def __new__(cls, value: str, label: str, *aliases: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.aliases = tuple(aliases)
        return obj


if __name__ == "__main__":

    class Gender1(LabelStrEnum):
        Male = ("male", "Male", "Man", "Boy", "男", "男性")
        Female = ("female", "Female", "Woman", "Girl", "女", "女性")

    print(repr(Gender1.safe_from_value("male")))
    print(repr(Gender1.safe_from_label("man", case_sensitive=False)))
    print(Gender1.Male.to_dict())

    class Gender2(LabelIntEnum):
        Male = (1, "Male", "Man", "Boy", "男", "男性")
        Female = (2, "Female", "Woman", "Girl", "女", "女性")

    print(repr(Gender2.safe_from_value(2)))
    print(repr(Gender2.safe_from_label("man", case_sensitive=False)))
    print(Gender2.Male.to_dict())
