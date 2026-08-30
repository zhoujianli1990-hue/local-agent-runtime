from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AuditEvent:
    kind: str
    subject: str
    detail: Mapping[str, Any]
    created_at: str


class MemoryAuditLog:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, kind: str, subject: str, detail: Mapping[str, Any]) -> None:
        self.events.append(
            AuditEvent(
                kind=kind,
                subject=subject,
                detail=dict(detail),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )
