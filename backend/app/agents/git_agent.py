from uuid import UUID

from app.agents.base import BaseAgent, DataSource
from app.schemas import AgentFindings


class GitAgent(BaseAgent):
    name = "git"

    def __init__(self, source: DataSource):
        self.source = source

    async def gather(self, service_id: UUID) -> AgentFindings:
        rows = await self.source.fetch(service_id, limit=10)
        authors = set(r.get("author", "unknown") for r in rows)
        files = []
        for r in rows:
            files.extend(r.get("files_changed") or [])

        summary = f"Found {len(rows)} recent commits by {', '.join(authors)}. {len(files)} files changed."

        return AgentFindings(agent_name=self.name, summary=summary, data=rows)
