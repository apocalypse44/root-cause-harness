from uuid import UUID
from collections import Counter

from app.agents.base import BaseAgent, DataSource
from app.schemas import AgentFindings


class LogsAgent(BaseAgent):
    name = "logs"

    def __init__(self, source: DataSource):
        self.source = source

    async def gather(self, service_id: UUID) -> AgentFindings:
        rows = await self.source.fetch(service_id, limit=100)
        errors = [r for r in rows if r.get("level") in ("error", "fatal")]
        patterns = Counter(r.get("message", "")[:80] for r in errors)
        top = patterns.most_common(3)

        summary = f"Found {len(errors)} error/fatal logs out of {len(rows)} total."
        if top:
            summary += f" Top pattern: '{top[0][0]}' ({top[0][1]}x)."

        return AgentFindings(agent_name=self.name, summary=summary, data=errors[:20])
