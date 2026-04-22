from dataclasses import Field, dataclass, fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class DataclassMixin:
    """一个 Mini 版本的 Pydantic Model"""

    def to_dict(
        self,
        *,
        exclude_none: bool = False,
        exclude_empty: bool = False,
        datetime_format: str | None = None,
        datetime_timestamp: Literal["s", "ms"] = "s",
        enum_to_value: bool = True,
        by_alias: bool = False,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> dict[str, Any]:
        pass

    def to_payload(self) -> dict[str, Any]:
        pass


def _convert_dataclass(
    obj: Any,
    *,
    exclude_none: bool = True,
    by_alias: bool,
    includes: list[str] | None,
    excludes: list[str] | None,
):
    result: dict[str, Any] = {}

    includes = set(includes) if includes else None
    excludes = set(excludes) if excludes else None
    for field in fields(obj):
        if not _field_selected(field, includes=includes, excludes=excludes):
            continue
        origin_value = getattr(obj, field.name)
        # converted_value =


def _build_path_tree(paths: list[str] | None) -> dict[str, Any] | None:
    """构建包含/排除路径树, 如果父节点被包含/排除, 则所有子节点都被包含/排除

    Example:
        ```python
        # {'a': True, 'd': {'e': True, 'f': True}}
        # "a" 已经被包含/排除, 则 "a.b" 和 "a.c" 就无需单独处理
        _build_path_tree(["a.b", "a.c", "a", "d.e", "d.f"])

        # {'b': {'c': True, 'd': {'e': True}}, 'a': True}
        _build_path_tree(["a", "b.c", "b.d.e"])
        ```
    """
    path_set = set(paths) if paths else None
    if not path_set:
        return None
    path_tree = {}
    for path in path_set:
        if not path:
            continue
        path_parts = path.split(".")
        node = path_tree
        for i, path_part in enumerate(path_parts):
            if i == len(path_parts) - 1:  # 叶子节点
                node[path_part] = True
            else:
                current = node.get(path_part, {})
                if current is True:  # 当前节点已经被整体包含/排除, 无需处理子节点
                    break
                else:
                    node[path_part] = current
                    node = current
    return path_tree


def _field_selected(field: Field, *, include_tree: dict[str, Any] | None, exclude_tree: dict[str, Any] | None):
    """dataclass 对象中的 field 是否需要处理
    include ∩ (NOT exclude)

    Args:
        field: dataclass 对象中的 Field
        include_tree: 如果不为空，则只有在 `include_tree` 中存在的字段，才需要处理。判断优先级高于 `excludes`。
        excludes: 如果不为空，如果字段不在 `excludes` 中，则不需要处理。
    """
    name = field.name
    alias = field.metadata.get("alias", name)

    include_child = _get_child_tree(include_tree, field_name=name, field_alias=alias)
    exclude_child = _get_child_tree(exclude_tree, field_name=name, field_alias=alias)

    if include_tree is not None and include_child is None:
        # 字段不在包含的树中, 该字段完全过滤器掉
        return False, None, None
    if exclude_child is True:
        # 字段需要被过滤, 当前取到的 include_child 大概率是 None
        return False, include_child, exclude_child

    if includes:
        return field_name in includes or field_alias in includes
    if excludes:
        return field_name not in excludes and field_alias not in excludes
    return True


def _get_child_tree(tree: dict[str, Any] | None, *, field_name: str, field_alias: str):
    if tree is None:
        return None
    if field_name in tree:
        return tree[field_name]
    if field_alias in tree:
        return tree[field_alias]
    return None


def _should_exclude_value(value: Any, *, exclude_none: bool, exclude_empty: bool):
    """是否需要排除 value

    Args:
        value: dataclass 中的某个字段的值
        exclude_none: 为 True 则排除任何 None 值
        exclude_empty: 为 True 则排除空的容器值
    """
    if exclude_none:
        return value is None
    if exclude_empty:
        return value in ([], (), {}, set())
    return False


def _convert_value(
    value: Any,
    *,
    exclude_none: bool = True,
    exclude_empty: bool = True,
    datetime_format: str | None = None,
    datetime_timestamp: Literal["s", "ms"] = "s",
    enum_to_value: bool = True,
) -> Any:
    if is_dataclass(value):
        pass

    ######################### convert datetime #########################
    if isinstance(value, datetime):
        if datetime_format:
            return datetime.strftime(datetime_format)
        else:
            if datetime_timestamp == "s":
                return int(datetime.timestamp())
            elif datetime_timestamp == "ms":
                return int(datetime.timestamp() * 1000)
            else:
                raise ValueError(f"时间转时间戳的单位[{datetime_timestamp}]不合法")

    ######################### convert Enum #########################
    if isinstance(value, Enum):
        return value.value if enum_to_value else value

    ######################### convert list / tuple / set #########################
    if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
        result = []
        for item in value:
            converted = _convert_value(
                item,
                exclude_none=exclude_none,
                exclude_empty=exclude_empty,
                datetime_format=datetime_format,
                datetime_timestamp=datetime_timestamp,
                enum_to_value=enum_to_value,
            )
            if not _should_exclude_value(converted, exclude_none=exclude_none, exclude_empty=exclude_empty):
                result.append(converted)
        if isinstance(value, tuple):
            return tuple(result)
        elif isinstance(value, set):
            return set(result)
        else:
            return result

    ######################### convert dict #########################
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            converted = _convert_value(
                v,
                exclude_none=exclude_none,
                exclude_empty=exclude_empty,
                datetime_format=datetime_format,
                datetime_timestamp=datetime_timestamp,
                enum_to_value=enum_to_value,
            )
            if not _should_exclude_value(converted, exclude_none=exclude_none, exclude_empty=exclude_empty):
                result[k] = converted
        return result

    return value


if __name__ == "__main__":
    # @dataclass
    # class T:
    #     a: int
    #     b: str

    # print(fields(T(1, "a")))
    # for f in fields(T(1, "a")):
    #     print(type(f))

    print(_build_path_tree(["a.b", "a.c", "a", "d.e", "d.f"]))
    print(_build_path_tree(["a", "b.c", "b.d.e", "b.d.f"]))
