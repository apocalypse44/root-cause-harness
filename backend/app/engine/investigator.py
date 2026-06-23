from uuid import UUID
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import PostgresSource
from app.agents.deployment_agent import DeploymentAgent
from app.agents.logs_agent import LogsAgent
from app.agents.metrics_agent import MetricsAgent
from app.agents.git_agent import GitAgent
from app.agents.correlation_agent import CorrelationAgent
from app.models import Deployment, Log, Metric, GitChange
from app.schemas import AgentFindings


class Investigator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agents = [
            DeploymentAgent(PostgresSource(db, Deployment)),
            LogsAgent(PostgresSource(db, Log)),
            MetricsAgent(PostgresSource(db, Metric)),
            GitAgent(PostgresSource(db, GitChange)),
        ]
        self.correlation = CorrelationAgent()

    async def investigate(self, service_id: UUID) -> dict:
        all_findings: list[AgentFindings] = []
        for agent in self.agents:
            findings = await agent.gather(service_id)
            all_findings.append(findings)

        result = await self.correlation.correlate(all_findings)
        result["agent_findings"] = [f.model_dump() for f in all_findings]
        return result

    async def investigate_stream(self, service_id: UUID) -> AsyncGenerator[dict, None]:
        all_findings: list[AgentFindings] = []

        for agent in self.agents:
            yield {"event": "agent_start", "agent": agent.name}
            findings = await agent.gather(service_id)
            all_findings.append(findings)
            yield {"event": "agent_complete", "agent": agent.name, "summary": findings.summary}

        yield {"event": "agent_start", "agent": "correlation"}
        result = await self.correlation.correlate(all_findings)
        result["agent_findings"] = [f.model_dump() for f in all_findings]
        yield {"event": "complete", "report": result}
