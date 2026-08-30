from datetime import datetime, timedelta, timezone
import unittest

from local_agent_runtime import (
    AuthorizationGate,
    ConnectorRegistry,
    Orchestrator,
    ScheduledTask,
    Scheduler,
    Skill,
    SkillRegistry,
    ToolResult,
)


class FakeConnector:
    name = "facts"

    def __init__(self, fresh=True):
        self.fresh = fresh

    def invoke(self, action, arguments):
        return ToolResult(source=self.name, data={"value": 7}, fresh=self.fresh)


def runtime(skill_risk="read", fresh=True, approver=None):
    connectors = ConnectorRegistry()
    connectors.register(FakeConnector(fresh=fresh))
    skills = SkillRegistry()
    skills.register(
        Skill(
            name="summarize",
            description="test",
            required_connectors=("facts",),
            risk=skill_risk,
            handler=lambda context: {"answer": context.tool_results[0].data["value"]},
        )
    )
    gate = AuthorizationGate(approver) if approver else None
    return Orchestrator(skills, connectors, authorization=gate)


class RuntimeTests(unittest.TestCase):
    def test_runs_skill_and_records_sources(self):
        agent = runtime()
        result = agent.run("summarize", "summarize")
        self.assertEqual(result.output, {"answer": 7})
        self.assertEqual(result.sources, ("facts",))
        self.assertEqual(agent.audit.events[-1].kind, "skill.completed")

    def test_rejects_stale_tool_data(self):
        with self.assertRaisesRegex(RuntimeError, "stale tool result"):
            runtime(fresh=False).run("summarize", "summarize")

    def test_write_skill_requires_explicit_approval(self):
        with self.assertRaises(PermissionError):
            runtime(skill_risk="write").run("summarize", "change something")
        result = runtime(skill_risk="write", approver=lambda request: True).run(
            "summarize", "change something"
        )
        self.assertEqual(result.output["answer"], 7)

    def test_scheduler_runs_due_tasks_only_once(self):
        agent = runtime()
        scheduler = Scheduler(agent)
        now = datetime.now(timezone.utc)
        scheduler.add(ScheduledTask("due", "summarize", "now", now, {}))
        scheduler.add(
            ScheduledTask("later", "summarize", "later", now + timedelta(hours=1), {})
        )
        self.assertEqual(len(scheduler.run_due(now)), 1)
        self.assertEqual(scheduler.run_due(now), [])


if __name__ == "__main__":
    unittest.main()
