"""Typed API responses."""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    data: Optional[Mapping[str, Any]]
    body: str

    @property
    def successful(self) -> bool:
        return 200 <= self.status_code < 300
