from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, Any


class RiskLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AuthorizationRequest:
    skill: str
    risk: RiskLevel
    summary: str
    arguments: Mapping[str, Any]


class AuthorizationGate:
    def __init__(self, approver: Callable[[AuthorizationRequest], bool] | None = None) -> None:
        self._approver = approver or (lambda request: request.risk is RiskLevel.READ)

    def require(self, request: AuthorizationRequest) -> None:
        if not self._approver(request):
            raise PermissionError(f"authorization denied for skill: {request.skill}")
