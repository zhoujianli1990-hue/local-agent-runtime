from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .audit import MemoryAuditLog
from .authorization import AuthorizationGate, AuthorizationRequest, RiskLevel
from .contracts import SkillContext
from .registry import ConnectorRegistry, SkillRegistry


@dataclass(frozen=True)
class RunResult:
    skill: str
    output: Mapping[str, Any]
    sources: tuple[str, ...]


class Orchestrator:
    def __init__(
        self,
        skills: SkillRegistry,
        connectors: ConnectorRegistry,
        authorization: AuthorizationGate | None = None,
        audit: MemoryAuditLog | None = None,
    ) -> None:
        self.skills = skills
        self.connectors = connectors
        self.authorization = authorization or AuthorizationGate()
        self.audit = audit or MemoryAuditLog()

    def run(
        self,
        skill_name: str,
        request: str,
        inputs: Mapping[str, Any] | None = None,
    ) -> RunResult:
        skill = self.skills.get(skill_name)
        risk = RiskLevel(skill.risk)
        arguments = dict(inputs or {})
        self.authorization.require(
            AuthorizationRequest(
                skill=skill.name,
                risk=risk,
                summary=request,
                arguments=arguments,
            )
        )

        context = SkillContext(request=request, inputs=arguments)
        for connector_name in skill.required_connectors:
            connector = self.connectors.get(connector_name)
            result = connector.invoke("snapshot", arguments)
            if not result.fresh:
                raise RuntimeError(f"stale tool result: {result.source}")
            context.tool_results.append(result)

        output = dict(skill.handler(context))
        sources = tuple(result.source for result in context.tool_results)
        self.audit.append(
            "skill.completed",
            skill.name,
            {"request": request, "sources": sources, "output": output},
        )
        return RunResult(skill=skill.name, output=output, sources=sources)
