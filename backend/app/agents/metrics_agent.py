from uuid import UUID

from app.agents.base import BaseAgent, DataSource
from app.schemas import AgentFindings


class MetricsAgent(BaseAgent):
    name = "metrics"

    def __init__(self, source: DataSource):
        self.source = source

    async def gather(self, service_id: UUID) -> AgentFindings:
        rows = await self.source.fetch(service_id, limit=100)

        by_type: dict[str, list] = {}
        for r in rows:
            mt = str(r.get("metric_type", "unknown"))
            by_type.setdefault(mt, []).append(r)

        anomalies = []
        for mt, values in by_type.items():
            nums = [v.get("value", 0) for v in values]
            if len(nums) >= 2:
                latest, previous_avg = nums[0], sum(nums[1:]) / len(nums[1:])
                if previous_avg > 0 and latest / previous_avg > 2:
                    anomalies.append({"metric": mt, "latest": latest, "previous_avg": round(previous_avg, 2)})

        summary = f"Analyzed {len(rows)} metric points across {len(by_type)} types."
        if anomalies:
            summary += f" {len(anomalies)} anomalies detected."

        return AgentFindings(agent_name=self.name, summary=summary, data=rows[:20])
