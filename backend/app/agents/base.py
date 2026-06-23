from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import AgentFindings


class DataSource(ABC):
    """Swap this to integrate real backends (Prometheus, Loki, GitHub API)."""

    @abstractmethod
    async def fetch(self, service_id: UUID, **kwargs) -> list[dict]:
        ...


class PostgresSource(DataSource):
    def __init__(self, db: AsyncSession, model: Any):
        self.db = db
        self.model = model

    async def fetch(self, service_id: UUID, **kwargs) -> list[dict]:
        limit = kwargs.get("limit", 50)
        order_col = self.model.timestamp if hasattr(self.model, "timestamp") else self.model.id
        stmt = (
            select(self.model)
            .where(self.model.service_id == service_id)
            .order_by(order_col.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            for r in rows
        ]


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def gather(self, service_id: UUID) -> AgentFindings:
        ...
