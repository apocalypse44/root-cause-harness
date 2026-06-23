import uuid
from datetime import datetime
import enum

from sqlalchemy import String, Float, ForeignKey, Enum as SAEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ServiceStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"


class DeploymentStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    rolled_back = "rolled_back"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"


class LogLevel(str, enum.Enum):
    info = "info"
    warn = "warn"
    error = "error"
    fatal = "fatal"


class MetricType(str, enum.Enum):
    cpu = "cpu"
    memory = "memory"
    latency = "latency"
    error_rate = "error_rate"


class Service(Base):
    __tablename__ = "services"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[ServiceStatus] = mapped_column(SAEnum(ServiceStatus), default=ServiceStatus.healthy)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deployments: Mapped[list["Deployment"]] = relationship(back_populates="service")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="service")


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    version: Mapped[str] = mapped_column(String(50))
    status: Mapped[DeploymentStatus] = mapped_column(SAEnum(DeploymentStatus))
    commit_sha: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    service: Mapped["Service"] = relationship(back_populates="deployments")


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    title: Mapped[str] = mapped_column(String(500))
    severity: Mapped[Severity] = mapped_column(SAEnum(Severity))
    status: Mapped[IncidentStatus] = mapped_column(SAEnum(IncidentStatus), default=IncidentStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped["Service"] = relationship(back_populates="incidents")
    report: Mapped["Report | None"] = relationship(back_populates="incident", uselist=False)


class Log(Base):
    __tablename__ = "logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    level: Mapped[LogLevel] = mapped_column(SAEnum(LogLevel))
    message: Mapped[str] = mapped_column(String)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Metric(Base):
    __tablename__ = "metrics"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    metric_type: Mapped[MetricType] = mapped_column(SAEnum(MetricType))
    value: Mapped[float] = mapped_column(Float)
    labels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class GitChange(Base):
    __tablename__ = "git_changes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    commit_sha: Mapped[str] = mapped_column(String(40))
    author: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String)
    files_changed: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id"), unique=True)
    root_cause: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident: Mapped["Incident"] = relationship(back_populates="report")
