from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol


@dataclass(frozen=True)
class ToolResult:
    source: str
    data: Mapping[str, Any]
    captured_at: str | None = None
    fresh: bool = True


class Connector(Protocol):
    name: str

    def invoke(self, action: str, arguments: Mapping[str, Any]) -> ToolResult:
        """Call a tool action and return normalized data."""


@dataclass
class SkillContext:
    request: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    tool_results: list[ToolResult] = field(default_factory=list)


SkillHandler = Callable[[SkillContext], Mapping[str, Any]]


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    handler: SkillHandler
    required_connectors: tuple[str, ...] = ()
    risk: str = "read"
