from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.models import ServiceStatus, Severity, IncidentStatus


class ServiceOut(BaseModel):
    id: UUID
    name: str
    status: ServiceStatus
    created_at: datetime
    deployment_count: int = 0
    incident_count: int = 0

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    service_id: UUID
    title: str
    severity: Severity


class IncidentOut(BaseModel):
    id: UUID
    service_id: UUID
    service_name: str = ""
    title: str
    severity: Severity
    status: IncidentStatus
    created_at: datetime
    has_report: bool = False

    class Config:
        from_attributes = True


class ReportOut(BaseModel):
    id: UUID
    incident_id: UUID
    root_cause: str
    confidence: float
    evidence: dict | None
    recommendations: list | None
    generated_at: datetime

    class Config:
        from_attributes = True


class InvestigationStatus(BaseModel):
    incident_id: UUID
    status: str
    current_agent: str | None = None
    findings: dict | None = None


class AgentFindings(BaseModel):
    agent_name: str
    summary: str
    data: list[dict]
