from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from dataclass_mixin import DataclassMixin


class OrderStatus(Enum):
    PENDING = 1
    PAID = 2
    CANCELED = 3


@dataclass
class TimeRange:
    start: datetime = field(metadata={"alias": "startTime"})
    end: datetime = field(metadata={"alias": "endTime"})


@dataclass
class Address:
    city: str = field(metadata={"alias": "cityName"})
    zipcode: str | None = field(default=None, metadata={"alias": "zipCode"})


@dataclass
class UserProfile:
    nickname: str = field(metadata={"alias": "nickName"})
    address: Address
    tags: list[str] = field(default_factory=list)


@dataclass
class Order(DataclassMixin):
    order_id: int = field(metadata={"alias": "orderId"})
    status: OrderStatus
    amount: float
    created_at: datetime = field(metadata={"alias": "createdAt"})
    time_range: TimeRange = field(metadata={"alias": "timeRange"})
    profile: UserProfile
    remark: str | None = None
    extra: dict[str, object] = field(default_factory=dict)


def build_order() -> Order:
    return Order(
        order_id=10001,
        status=OrderStatus.PAID,
        amount=99.5,
        created_at=datetime(2026, 4, 23, 10, 0, 0),
        time_range=TimeRange(
            start=datetime(2026, 4, 23, 9, 0, 0),
            end=datetime(2026, 4, 23, 10, 0, 0),
        ),
        profile=UserProfile(
            nickname="alice",
            address=Address(city="Shanghai", zipcode="200000"),
            tags=["vip", "new"],
        ),
        remark=None,
        extra={"source": "app"},
    )


def test_by_alias() -> None:
    order = build_order()
    result = order.to_dict(by_alias=True)

    assert "orderId" in result
    assert "createdAt" in result
    assert "timeRange" in result
    assert "nickName" in result["profile"]
    assert "cityName" in result["profile"]["address"]


def test_enum_to_value() -> None:
    order = build_order()
    result = order.to_dict(enum_to_value=True)
    assert result["status"] == 2


def test_enum_keep_original() -> None:
    order = build_order()
    result = order.to_dict(enum_to_value=False)
    assert result["status"] is OrderStatus.PAID


def test_datetime_format() -> None:
    order = build_order()
    result = order.to_dict(
        keep_datetime=False,
        datetime_format="%Y-%m-%d %H:%M:%S",
    )

    assert result["created_at"] == "2026-04-23 10:00:00"
    assert result["time_range"]["start"] == "2026-04-23 09:00:00"
    assert result["time_range"]["end"] == "2026-04-23 10:00:00"


def test_datetime_timestamp_seconds() -> None:
    order = build_order()
    result = order.to_dict(
        keep_datetime=False,
        datetime_timestamp="s",
    )

    assert isinstance(result["created_at"], int)
    assert isinstance(result["time_range"]["start"], int)
    assert isinstance(result["time_range"]["end"], int)


def test_exclude_none() -> None:
    order = build_order()
    result = order.to_dict(exclude_none=True)
    assert "remark" not in result


def test_exclude_empty() -> None:
    order = build_order()
    order.extra = {}
    order.profile.tags = []

    result = order.to_dict(exclude_empty=True)
    assert "extra" not in result
    assert "tags" not in result["profile"]


def test_includes_simple_fields() -> None:
    order = build_order()
    result = order.to_dict(includes=["order_id", "amount"])

    assert result == {
        "order_id": 10001,
        "amount": 99.5,
    }


def test_includes_nested_fields() -> None:
    order = build_order()
    result = order.to_dict(
        includes=["profile.nickname", "profile.address.city"],
    )

    assert result == {
        "profile": {
            "nickname": "alice",
            "address": {
                "city": "Shanghai",
            },
        },
    }


def test_excludes_simple_fields() -> None:
    order = build_order()
    result = order.to_dict(excludes=["remark", "extra"])

    assert "remark" not in result
    assert "extra" not in result
    assert "order_id" in result


def test_excludes_nested_fields() -> None:
    order = build_order()
    result = order.to_dict(excludes=["profile.address.zipcode"])

    assert result["profile"]["address"]["city"] == "Shanghai"
    assert "zipcode" not in result["profile"]["address"]


def test_includes_and_excludes_together() -> None:
    order = build_order()
    result = order.to_dict(
        includes=["profile"],
        excludes=["profile.address.zipcode"],
    )

    assert "profile" in result
    assert result["profile"]["nickname"] == "alice"
    assert result["profile"]["address"]["city"] == "Shanghai"
    assert "zipcode" not in result["profile"]["address"]


def test_include_by_alias_path() -> None:
    order = build_order()
    result = order.to_dict(
        by_alias=True,
        includes=["timeRange.startTime", "orderId"],
        keep_datetime=False,
        datetime_format="%Y-%m-%d %H:%M:%S",
    )

    assert result == {
        "orderId": 10001,
        "timeRange": {
            "startTime": "2026-04-23 09:00:00",
        },
    }


def test_exclude_by_alias_path() -> None:
    order = build_order()
    result = order.to_dict(
        by_alias=True,
        excludes=["profile.address.zipCode"],
    )

    assert "zipCode" not in result["profile"]["address"]
    assert "cityName" in result["profile"]["address"]
