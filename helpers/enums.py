from enum import IntEnum
from typing import ClassVar, Self


class LabelIntEnum(IntEnum):
    """带 label / aliases 能力的 `IntEnum` 基类

    Example:
        ```python
        class Gender(LabelIntEnum):
            Male = (1, "Male", "Man", "Boy", "男", "男性")
            Female = (2, "Female", "Woman", "Girl", "女", "女性")

        # <Gender.Male: 1>
        print(repr(Gender.safe_from_label("man", case_sensitive=False)))
        # <Gender.Female: 2>
        print(repr(Gender.safe_from_value(2)))
        # {'name': 'Male', 'value': 1, 'label': 'Male', 'aliases': ('Man', 'Boy', '男', '男性')}
        print(Gender.Male.to_dict())
        ```
    """

    label: str
    aliases: tuple[str, ...]

    _label_map_cs: ClassVar[dict[str, Self]]  # case-sensitive
    _label_map_ci: ClassVar[dict[str, Self]]  # case-insensitive

    def __new__(cls, value: int, label: str, *aliases: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.aliases = tuple(aliases)
        return obj

    def __init_subclass__(cls):
        super().__init_subclass__()
        cs: dict[str, Self] = {}
        ci: dict[str, Self] = {}
        for item in cls:
            texts = (item.label, *item.aliases)
            for text in texts:
                # case-sensitive
                if text in cs and cs[text] is not item:
                    raise ValueError(f"重复的 label/alias: {text}")
                cs[text] = item
                # case-insensitive
                text_ci = text.casefold()
                if text_ci in ci and ci[text_ci] is not item:
                    raise ValueError(f"重复的 label/alias(case-insensitive): {text}")
                ci[text_ci] = item
        cls._label_map_cs = cs
        cls._label_map_ci = ci

    ############################## value / label / alias lookup ##############################

    @classmethod
    def safe_from_value(cls, value: int) -> Self | None:
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def from_value(cls, value: int) -> Self:
        return cls(value)

    @classmethod
    def safe_from_label(cls, label: str, *, case_sensitive: bool = True) -> Self | None:
        if case_sensitive:
            return cls._label_map_cs.get(label)
        else:
            return cls._label_map_ci.get(label.casefold())

    @classmethod
    def from_label(cls, label: str, *, case_sensitive: bool = True) -> Self:
        item = cls.safe_from_label(label, case_sensitive=case_sensitive)
        if not item:
            raise ValueError(f"{label!r} is not a valid label/alias for {cls.__name__}")
        return item

    ############################## serialization ##############################

    def to_dict(self) -> dict[str, int | str | tuple[str, ...]]:
        return {
            "name": self.name,
            "value": int(self),
            "label": self.label,
            "aliases": self.aliases,
        }
