from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from .orchestrator import Orchestrator, RunResult


@dataclass(frozen=True)
class ScheduledTask:
    name: str
    skill: str
    request: str
    run_at: datetime
    inputs: Mapping[str, Any]


class Scheduler:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator
        self._tasks: list[ScheduledTask] = []

    def add(self, task: ScheduledTask) -> None:
        self._tasks.append(task)

    def run_due(self, now: datetime) -> list[RunResult]:
        due = [task for task in self._tasks if task.run_at <= now]
        self._tasks = [task for task in self._tasks if task.run_at > now]
        return [
            self.orchestrator.run(task.skill, task.request, task.inputs)
            for task in sorted(due, key=lambda item: item.run_at)
        ]
