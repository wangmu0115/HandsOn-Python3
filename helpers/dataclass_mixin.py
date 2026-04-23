from dataclasses import Field, fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class DataclassMixin:
    """为 dataclass 提供轻量级序列化能力的混入类

    这是一个 Mini 版的 Pydantic Model，核心目标是为 dataclass 提供：
    1. 递归序列化为 `dict`
    2. `datetime`、`Enum` 等常见类型的转换
    3. 基于字段路径的 includes / excludes 过滤
    4. 空值、空容器值裁剪
    5. alias 输出支持

    与 Pydantic 不同的是：
    - 不做字段校验
    - 不做类型强制转换
    - 更偏向**可控的导出工具**而不是**声明式数据模型框架**
    """

    def to_dict(
        self,
        *,
        exclude_none: bool = False,
        exclude_empty: bool = False,
        keep_datetime: bool = True,
        datetime_format: str | None = None,
        datetime_timestamp: Literal["s", "ms"] | None = None,
        enum_to_value: bool = False,
        by_alias: bool = False,
        includes: list[str] | None = None,
        excludes: list[str] | None = None,
    ) -> dict[str, Any]:
        """将当前 dataclass 对象递归序列化为字典

        该方法是统一导出入口，负责：
        - 将 `includes` / `excludes` 路径列表构造成路径树
        - 将当前对象递归转换为 `dict[str, Any]`
        - 在转换过程中对 `datetime`、`Enum`、嵌套 dataclass、容器类型进行处理

        Args:
            exclude_none: 是否排除值为 `None` 的字段
                - `True` 表示值为 `None` 的字段不出现在输出结果中
                - `False` 表示保留 `None`
            exclude_empty: 是否排除空容器字段，空容器包括：`[]`, `()`, `{}` 和 `set()`
                - 该参数只裁剪空容器，不剪裁 `None`
                - 若同时希望移除 `None`，需配合 `exclude_none=True`
            keep_datetime: 是否保留 `datetime` 原始对象
                - `True` 表示输出中保留 `datetime` 实例
                - `False` 必须进一步通过 `datetime_format` 或 `datetime_timestamp` 指定导出方式
            datetime_format: `datetime` 导出为字符串时使用的格式：`"%Y-%m-%d %H:%M:%S"`, `"%Y-%m-%dT%H:%M:%S%z"`, ...
                - 仅在 `keep_datetime=False` 时生效
                - 若 `keep_datetime=False` 时，`datetime_format` 和 `datetime_timestamp` 都为 `None`，则会抛出 `ValueError`
            datetime_timestamp: `datetime` 导出为时间戳时的单位
                - 可选值：`"s"` 表示秒级时间戳；`"ms"` 表示毫秒级时间戳；`None` 表示不按时间戳导出
                - 仅在 `keep_datetime=False` 且 `datetime_format is None` 时使用
            enum_to_value: 是否将 `Enum` 导出为其 `.value`
                - `True`：例如 `Gender.Male` → `1`
                - `False`：保留原始枚举对象
            by_alias: 是否优先使用字段别名作为输出字段名，字段别名从 dataclass field 的 `metadata["alias"]` 中读取
            includes: 需要包含的字段路径列表，路径使用 `.` 分隔，例如：`["id", "profile.name", "profile.age"]`
                - 为 `None` 时，默认包含所有字段
                - 不为 `None` 时，仅导出命中的字段路径
            excludes: 需要排除的字段路径列表，路径使用 `.` 分隔，例如：`["password", "profile.email"]`
                - 为 `None` 时，不额外排除字段
                - 命中的字段路径会从最终输出中剪裁掉

        Returns:
            dict[str, Any]: 递归序列化后的字典对象
        """

        include_tree = _build_path_tree(includes)
        exclude_tree = _build_path_tree(excludes)

        return _convert_dataclass(
            self,
            exclude_none=exclude_none,
            exclude_empty=exclude_empty,
            keep_datetime=keep_datetime,
            datetime_format=datetime_format,
            datetime_timestamp=datetime_timestamp,
            enum_to_value=enum_to_value,
            by_alias=by_alias,
            include_tree=include_tree,
            exclude_tree=exclude_tree,
        )

    def to_payload(self) -> dict[str, Any]:
        """导出更适合接口传输的 payload 字典

        这是一个约定式快捷方法，相当于对 :meth:`to_dict` 预设了一组更适合 RPC / HTTP / MQ / JSON 序列化场景的默认参数：
        - 排除 `None`
        - 排除空容器
        - `datetime` 转换为秒级时间戳
        - `Enum` 转换为 `.value`
        - 字段名优先使用 alias

        Returns:
            适合作为接口入参 / 出参载荷的字典
        """
        return self.to_dict(
            exclude_none=True,
            exclude_empty=True,
            keep_datetime=False,
            datetime_format=None,
            datetime_timestamp="s",
            enum_to_value=True,
            by_alias=True,
        )


def _convert_dataclass(
    obj: Any,
    *,
    exclude_none: bool,
    exclude_empty: bool,
    keep_datetime: bool,
    datetime_format: str | None,
    datetime_timestamp: Literal["s", "ms"] | None,
    enum_to_value: bool,
    by_alias: bool,
    include_tree: dict[str, Any] | None,
    exclude_tree: dict[str, Any] | None,
) -> dict[str, Any]:
    """将 dataclass 实例递归转换为字典

    这是 dataclass 对象的核心转换函数，它会遍历对象的每个字段，并依次完成：
    1. 基于 `include_tree` / `exclude_tree` 判断字段是否应该保留
    2. 读取字段原始值
    3. 递归调用 :func:`_convert_value` 转换字段值
    4. 根据 `exclude_none` / `exclude_empty` 判断是否需要剔除该字段
    5. 根据 `by_alias` 决定输出字段名使用原名还是别名
    """
    result: dict[str, Any] = {}
    for field in fields(obj):
        selected, include_child, exclude_child = _field_selected(
            field,
            include_tree=include_tree,
            exclude_tree=exclude_tree,
        )
        if not selected:  # 字段被排除
            continue

        origin_value = getattr(obj, field.name)
        converted_value = _convert_value(
            origin_value,
            exclude_none=exclude_none,
            exclude_empty=exclude_empty,
            keep_datetime=keep_datetime,
            datetime_format=datetime_format,
            datetime_timestamp=datetime_timestamp,
            enum_to_value=enum_to_value,
            by_alias=by_alias,
            include_tree=include_child if isinstance(include_child, dict) else None,
            exclude_tree=exclude_child if isinstance(exclude_child, dict) else None,
        )
        # 是否需要排除空值
        if _should_exclude_value(converted_value, exclude_none=exclude_none, exclude_empty=exclude_empty):
            continue

        output_field_name = field.metadata.get("alias", field.name) if by_alias else field.name
        result[output_field_name] = converted_value
    return result


def _build_path_tree(field_paths: list[str] | None) -> dict[str, Any] | None:
    """将字段路径列表构造成树状字典

    该函数用于把 `includes` / `excludes` 中的路径表达式转换为便于递归处理的树结构

    Note:
        - 使用 `.` 表示嵌套字段，例如：`a.b.c`
        - 单节点路径如 `a` 表示整个 `a` 字段
        - 若父路径已经被完整选中，则其子路径无需重复展开

        示例：
        - `["a"]` -> `{"a": True}`
        - `["a.b", "a.c"]` -> `{"a": {"b": True, "c": True}}`
        - `["a", "a.b"]` -> `{"a": True}`

        `True` 的含义是：
        - 当前路径命中且“整个节点都生效”
        - 无需继续向下细分子节点

    Args:
        field_paths: 字段路径列表，为空列表、`None`、或仅包含空字符串时，返回 `None`

    Returns:
        构造后的路径树，若没有有效路径，则返回 `None`

    Example:
        ```python
        print(_build_path_tree(["a.b", "a.c", "a", "d.e", "d.f"]))
        # {'a': True, 'd': {'e': True, 'f': True}}

        print(_build_path_tree(["a", "b.c", "b.d.e"]))
        # {'a': True, 'b': {'c': True, 'd': {'e': True}}}

        print(_build_path_tree([]))
        # None

        print(_build_path_tree(None))
        # None

        print(_build_path_tree([""]))
        # None
        ```
    """
    if not field_paths:
        return None
    result_tree = {}
    for field_path in field_paths:
        if not field_path:
            continue
        field_path_items = field_path.split(".")  # ["a", "b"]
        node = result_tree
        for i, field_path_item in enumerate(field_path_items, start=1):
            if i == len(field_path_items):  # 叶子节点
                node[field_path_item] = True
            else:
                current = node.get(field_path_item, {})
                if current is True:  # 当前字段路径的父路径已经被全部包含/排除，子路径无需处理
                    break
                else:
                    node[field_path_item] = current
                    node = current
    return result_tree if result_tree else None


def _field_selected(
    field: Field,
    *,
    include_tree: dict[str, Any] | None,
    exclude_tree: dict[str, Any] | None,
) -> tuple[bool, dict[str, Any] | bool | None, dict[str, Any] | bool | None]:
    """判断 dataclass 字段是否应被导出，并返回其子树规则

    该函数同时支持，使用字段名和字段 alias 匹配，匹配规则可以概括为：include ∩ (NOT exclude)
    1. 若 `include_tree is None`，则表示默认全部可选
    2. 若 `include_tree is not None`，则字段必须命中 `include_tree` 才能继续
    3. 若字段被 `exclude_tree` 明确标记为 `True`，则字段最终被排除
    4. 若字段命中的是子树 dict，则继续将子规则向下传递给递归转换逻辑

    Note:
        - `include_tree` 决定候选范围
        - `exclude_tree` 决定二次剪裁
        - 如果某字段整体被 include，但其子字段被 exclude，则只排除对应子字段，不影响其他子字段

        示例：假设字段 `time` 下还有 `start` 和 `end`字段
        - `include_tree={"time": True}`, `exclude_tree=None` → 整个 `time` 字段保留
        - `include_tree={"time": True}`, `exclude_tree={"time": True}` → 整个 `time` 字段被排除
        - `include_tree={"time": True}`, `exclude_tree={"time": {"start": True}}` → 保留 `time.end`，排除 `time.start`

    Args:
        field: dataclass 中的字段对象
        include_tree: include 路径树
            - `None` 表示不过滤，默认允许所有字段参与导出
            - 非 `None` 表示仅允许命中的字段参与导出
        exclude_tree: exclude 路径树
            - `None` 表示不额外剪裁
            - 非 `None` 表示命中的字段会被排除

    Returns:
        一个三元组 `(selected, include_child, exclude_child)`：

        - `selected: bool`: 当前字段是否应该参与后续导出流程
        - `include_child: dict[str, Any] | bool | None`: 当前字段在 include_tree 中对应的子规则
            - `None`：无子规则
            - `True`：当前字段整体被命中
            - `dict[str, Any]`：子字段仍需进一步匹配
        - `exclude_child: dict[str, Any] | bool | None`: 当前字段在 exclude_tree 中对应的子规则
            - `None`：无子规则
            - `True`：当前字段整体被排除
            - `dict[str, Any]`：子字段仍需进一步剪裁
    """
    name = field.name
    alias = field.metadata.get("alias", name)

    def _get_child_tree(tree: dict[str, Any] | None):
        if tree and name in tree:
            return tree[name]
        if tree and alias in tree:
            return tree[alias]
        return None

    include_child = _get_child_tree(include_tree)
    exclude_child = _get_child_tree(exclude_tree)

    if include_tree is not None and include_child is None:
        return False, None, None
    if exclude_child is True:
        return False, include_child, exclude_child
    return True, include_child, exclude_child


def _should_exclude_value(value: Any, *, exclude_none: bool, exclude_empty: bool):
    """判断 `value` 在当前导出策略下是否应该被移除

    - 当 `exclude_none=True` 时，仅对 `None` 生效
    - 当 `exclude_empty=True` 时，仅对空容器生效

    Args:
        value: 待判断的值
        exclude_none: 是否移除 `None`
        exclude_empty: 是否移除空容器：`[]`, `()`, `{}`, `set()`

    Returns:
        `True` 表示移除该值；`False` 表示保留
    """
    if exclude_none and value is None:
        return True
    if exclude_empty and value in ([], (), {}, set()):
        return True
    return False


def _convert_value(
    value: Any,
    *,
    exclude_none: bool,
    exclude_empty: bool,
    keep_datetime: bool,
    datetime_format: str | None,
    datetime_timestamp: Literal["s", "ms"] | None,
    enum_to_value: bool,
    by_alias: bool,
    include_tree: dict[str, Any] | None,
    exclude_tree: dict[str, Any] | None,
) -> Any:
    """递归转换任意值为可导出结构

    支持处理的值类型包括：
    - dataclass
    - datetime
    - Enum
    - list / tuple / set
    - dict
    - 其他基础类型（原样返回）

    该函数是整个导出过程的递归核心：
    - dataclass 会进一步转成 dict
    - 容器类型会对每个元素递归调用自身
    - dict 会按 key 参与 include / exclude 过滤
    - datetime / Enum 根据参数决定如何转换

    Args:
        value: 待转换的值
        exclude_none: 是否排除 `None`
        exclude_empty: 是否排除空容器
        keep_datetime: 是否保留 `datetime` 原始对象
        datetime_format: `datetime` 转字符串时的格式
        datetime_timestamp: `datetime` 转时间戳时的单位
        enum_to_value: 是否将 `Enum` 转换为 `.value`
        by_alias: 对嵌套 dataclass 导出时，是否使用 alias 作为字段名
        include_tree: 当前值继承到的 include 子树规则
        exclude_tree: 当前值继承到的 exclude 子树规则

    Returns:
        转换后的值，返回类型取决于输入值类型以及导出参数配置
    """

    ######################### convert dataclass #########################
    if is_dataclass(value):
        return _convert_dataclass(
            value,
            exclude_none=exclude_none,
            exclude_empty=exclude_empty,
            keep_datetime=keep_datetime,
            datetime_format=datetime_format,
            datetime_timestamp=datetime_timestamp,
            enum_to_value=enum_to_value,
            by_alias=by_alias,
            include_tree=include_tree if isinstance(include_tree, dict) else None,
            exclude_tree=exclude_tree if isinstance(exclude_tree, dict) else None,
        )

    ######################### convert datetime #########################
    if isinstance(value, datetime):
        if keep_datetime:
            return value
        if datetime_format:
            return value.strftime(datetime_format)
        if datetime_timestamp:
            match datetime_timestamp:
                case "s":
                    return int(value.timestamp())
                case "ms":
                    return int(value.timestamp() * 1000)
                case _:
                    raise ValueError(f"时间转时间戳的单位[{datetime_timestamp}]不合法")
        raise ValueError(f"{value} 是 `datetime` 类型；当 `keep_datetime=False` 时，`datetime_format` 和 `datetime_timestamp` 不能同时为空")

    ######################### convert Enum #########################
    if isinstance(value, Enum):
        return value.value if enum_to_value else value

    ######################### convert list / tuple / set #########################
    if isinstance(value, (list, tuple, set)):
        result = []
        for item in value:
            converted = _convert_value(
                item,
                exclude_none=exclude_none,
                exclude_empty=exclude_empty,
                keep_datetime=keep_datetime,
                datetime_format=datetime_format,
                datetime_timestamp=datetime_timestamp,
                enum_to_value=enum_to_value,
                by_alias=by_alias,
                include_tree=include_tree if isinstance(include_tree, dict) else None,
                exclude_tree=exclude_tree if isinstance(exclude_tree, dict) else None,
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
            include_child = include_tree.get(k) if include_tree else None
            exclude_child = exclude_tree.get(k) if exclude_tree else None

            if include_tree and include_child is None:
                continue
            if exclude_child is True:
                continue

            converted = _convert_value(
                v,
                exclude_none=exclude_none,
                exclude_empty=exclude_empty,
                keep_datetime=keep_datetime,
                datetime_format=datetime_format,
                datetime_timestamp=datetime_timestamp,
                enum_to_value=enum_to_value,
                by_alias=by_alias,
                include_tree=include_child if isinstance(include_child, dict) else None,
                exclude_tree=exclude_child if isinstance(exclude_child, dict) else None,
            )
            # 是否需要排除空值
            if not _should_exclude_value(converted, exclude_none=exclude_none, exclude_empty=exclude_empty):
                result[k] = converted
        return result

    ######################### convert str / int / float /... #########################
    return value


if __name__ == "__main__":
    from dataclasses import dataclass, field
    from datetime import datetime
    from enum import Enum

    class Status(Enum):
        OK = 1
        FAIL = 2

    @dataclass
    class User(DataclassMixin):
        user_id: int = field(metadata={"alias": "userId"})
        created_at: datetime = field(metadata={"alias": "createdAt"})
        status: Status

    user = User(
        user_id=1,
        created_at=datetime(2026, 4, 23, 12, 0, 0),
        status=Status.OK,
    )

    print(user.to_dict(by_alias=True, enum_to_value=True, keep_datetime=False, datetime_format="%Y-%m-%d %H:%M:%S"))
    """
    {
        "userId": 1,
        "createdAt": "2026-04-23 12:00:00",
        "status": 1,
    }
    """
