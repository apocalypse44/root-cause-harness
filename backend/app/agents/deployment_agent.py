from uuid import UUID

from app.agents.base import BaseAgent, DataSource
from app.schemas import AgentFindings


class DeploymentAgent(BaseAgent):
    name = "deployment"

    def __init__(self, source: DataSource):
        self.source = source

    async def gather(self, service_id: UUID) -> AgentFindings:
        rows = await self.source.fetch(service_id, limit=10)
        versions = [r.get("version", "unknown") for r in rows]
        failed = [r for r in rows if r.get("status") in ("failed", "rolled_back")]

        summary = f"Found {len(rows)} recent deployments: {', '.join(versions)}."
        if failed:
            summary += f" {len(failed)} failed/rolled back."

        return AgentFindings(agent_name=self.name, summary=summary, data=rows)
