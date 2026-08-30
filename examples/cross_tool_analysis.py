from local_agent_runtime import (
    ConnectorRegistry,
    Orchestrator,
    Skill,
    SkillContext,
    SkillRegistry,
    ToolResult,
)


class PortfolioConnector:
    name = "portfolio"

    def invoke(self, action, arguments):
        return ToolResult(source=self.name, data={"usd_exposure": 0.72, "drawdown": 0.031})


class MarketConnector:
    name = "market"

    def invoke(self, action, arguments):
        return ToolResult(source=self.name, data={"dollar_index_change": 0.8, "gold_change": -1.2})


def analyze(context: SkillContext):
    facts = {result.source: dict(result.data) for result in context.tool_results}
    elevated = facts["portfolio"]["usd_exposure"] > 0.6
    return {
        "conclusion": "USD concentration deserves attention" if elevated else "Risk is balanced",
        "facts": facts,
    }


connectors = ConnectorRegistry()
connectors.register(PortfolioConnector())
connectors.register(MarketConnector())

skills = SkillRegistry()
skills.register(
    Skill(
        name="cross-tool-risk-check",
        description="Combine portfolio and market data into one conclusion.",
        required_connectors=("portfolio", "market"),
        handler=analyze,
    )
)

result = Orchestrator(skills, connectors).run(
    "cross-tool-risk-check",
    "How does today's market move affect my portfolio?",
)
print(result.output)
