from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


def compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


@dataclass(frozen=True)
class PaginationInput:
    page: int = 1
    page_size: int = 20

    def to_query(self) -> dict[str, int]:
        return {"page": self.page, "pageSize": self.page_size}


@dataclass(frozen=True)
class PaginatedResponse:
    items: list[dict[str, Any]]
    page: int
    page_size: int
    total: int | None = None
    next_page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": self.items,
            "page": self.page,
            "pageSize": self.page_size,
            "total": self.total,
            "nextPage": self.next_page,
        }


@dataclass(frozen=True)
class ProjectRef:
    id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EntityRef:
    id: str
    name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return compact_dict(asdict(self))


def paginated_from_upstream(
    items: list[dict[str, Any]],
    page: int,
    page_size: int,
    total: int | None = None,
) -> dict[str, Any]:
    next_page = None
    if total is not None and page * page_size < total:
        next_page = page + 1
    elif total is None and len(items) == page_size:
        next_page = page + 1
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        next_page=next_page,
    ).to_dict()
