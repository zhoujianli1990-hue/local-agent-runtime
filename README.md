# Local Agent Runtime

A small, local-first Python runtime for building assistants that coordinate skills and tools without coupling the orchestration layer to one business domain.

It extracts the reusable engineering pattern behind a tool-using assistant:

`User request → Skill → Connectors → Freshness check → Authorization → Result → Audit log`

## Why this exists

Many agent demos mix product prompts, private data, tool adapters and workflow code in one application. That makes them difficult to reuse and hard to audit. Local Agent Runtime keeps those responsibilities separate:

- **Skills** describe repeatable work methods.
- **Connectors** normalize data from MCP servers, APIs or local applications.
- **Orchestrator** assembles tool results and runs the selected skill.
- **Authorization gate** blocks write or critical operations until explicitly approved.
- **Scheduler** triggers the same skills at a defined time.
- **Audit log** records what ran, which sources were used and what was returned.

The repository contains no financial strategy, account data, private prompt, credential or product UI.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
python examples/cross_tool_analysis.py
```

Example output:

```text
{'conclusion': 'USD concentration deserves attention', 'facts': {...}}
```

## Minimal usage

```python
from local_agent_runtime import ConnectorRegistry, Orchestrator, Skill, SkillRegistry

connectors = ConnectorRegistry()
connectors.register(MyMCPConnector())

skills = SkillRegistry()
skills.register(
    Skill(
        name="daily-review",
        description="Review connected data and return one conclusion.",
        required_connectors=("my-mcp",),
        handler=review,
    )
)

result = Orchestrator(skills, connectors).run("daily-review", "What changed today?")
```

## Safety model

Read-only skills run by default. Skills marked `write` or `critical` require an explicit approver. Connector results marked stale are rejected before a skill runs. This keeps authorization and data freshness in the runtime instead of relying on prompt wording.

## Architecture

```text
Application
   │
   ├── Skill Registry ── reusable workflow definitions
   ├── Connector Registry ── MCP / API / local tool adapters
   ├── Authorization Gate ── read / write / critical policy
   ├── Scheduler ── time-based invocation
   └── Audit Log ── source and result trace
```

## Extension points

- Implement `Connector.invoke()` for an MCP server, HTTP API or desktop bridge.
- Register domain-specific `Skill` handlers outside this package.
- Replace `MemoryAuditLog` with SQLite or another local store.
- Supply an approver backed by an application confirmation dialog.
- Put an LLM call inside a skill handler when synthesis is needed.

## Status

Version `0.1.0` focuses on the smallest complete workflow: registration, multi-tool collection, freshness validation, authorization, scheduling and auditability.
