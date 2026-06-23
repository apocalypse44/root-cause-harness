"""Seed the database with the demo scenario: bad deployment causes checkout error spike."""
import asyncio
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.database import Base
from app.models import (
    Service, Deployment, Incident, Log, Metric, GitChange,
    ServiceStatus, DeploymentStatus, Severity, IncidentStatus,
    LogLevel, MetricType,
)

NOW = datetime.now(timezone.utc)
CHECKOUT_ID = uuid4()
AUTH_ID = uuid4()
PAYMENT_ID = uuid4()


def make_services():
    return [
        Service(id=CHECKOUT_ID, name="checkout-service", status=ServiceStatus.degraded),
        Service(id=AUTH_ID, name="auth-service", status=ServiceStatus.healthy),
        Service(id=PAYMENT_ID, name="payment-service", status=ServiceStatus.healthy),
    ]


def make_deployments():
    return [
        Deployment(service_id=CHECKOUT_ID, version="v2.3.0", status=DeploymentStatus.success,
                   commit_sha="prev789aaa", started_at=NOW - timedelta(hours=6), completed_at=NOW - timedelta(hours=6, minutes=-2)),
        Deployment(service_id=CHECKOUT_ID, version="v2.3.1", status=DeploymentStatus.success,
                   commit_sha="abc123def456", started_at=NOW - timedelta(minutes=15), completed_at=NOW - timedelta(minutes=14)),
        Deployment(service_id=AUTH_ID, version="v1.8.0", status=DeploymentStatus.success,
                   commit_sha="auth111", started_at=NOW - timedelta(hours=24), completed_at=NOW - timedelta(hours=24, minutes=-1)),
        Deployment(service_id=PAYMENT_ID, version="v3.1.0", status=DeploymentStatus.success,
                   commit_sha="pay222", started_at=NOW - timedelta(hours=48), completed_at=NOW - timedelta(hours=48, minutes=-1)),
    ]


def make_logs():
    logs = []
    for i in range(5):
        logs.append(Log(service_id=CHECKOUT_ID, level=LogLevel.info,
                        message="Request processed successfully", metadata_={"request_id": f"req-{i}"},
                        timestamp=NOW - timedelta(minutes=60 - i)))
    for i in range(8):
        logs.append(Log(service_id=CHECKOUT_ID, level=LogLevel.error,
                        message="NullPointerException in PaymentValidator.validate()",
                        metadata_={"stack_trace": "at PaymentValidator.validate(PaymentValidator.java:42)\nat CheckoutService.process(CheckoutService.java:118)",
                                   "request_id": f"req-err-{i}"},
                        timestamp=NOW - timedelta(minutes=10 - i)))
    logs.append(Log(service_id=CHECKOUT_ID, level=LogLevel.fatal,
                    message="Circuit breaker OPEN for payment-validation",
                    metadata_={"circuit": "payment-validation", "failure_count": 50},
                    timestamp=NOW - timedelta(minutes=3)))
    return logs


def make_metrics():
    metrics = []
    for i in range(6):
        t = NOW - timedelta(minutes=60 - i * 10)
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.error_rate, value=0.5, labels={"endpoint": "/checkout"}, timestamp=t))
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.latency, value=200.0, labels={"endpoint": "/checkout"}, timestamp=t))
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.cpu, value=35.0, labels={}, timestamp=t))
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.memory, value=512.0, labels={}, timestamp=t))
    for i in range(4):
        t = NOW - timedelta(minutes=10 - i * 2)
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.error_rate, value=12.5 + i, labels={"endpoint": "/checkout"}, timestamp=t))
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.latency, value=1500.0 + i * 200, labels={"endpoint": "/checkout"}, timestamp=t))
        metrics.append(Metric(service_id=CHECKOUT_ID, metric_type=MetricType.cpu, value=78.0 + i * 3, labels={}, timestamp=t))
    return metrics


def make_git_changes():
    return [
        GitChange(service_id=CHECKOUT_ID, commit_sha="abc123def456", author="dev@team.com",
                  message="refactor payment validation logic",
                  files_changed=["src/PaymentValidator.java", "src/CheckoutService.java"],
                  committed_at=NOW - timedelta(minutes=30)),
        GitChange(service_id=CHECKOUT_ID, commit_sha="prev789aaa", author="senior@team.com",
                  message="update checkout logging",
                  files_changed=["src/CheckoutService.java"],
                  committed_at=NOW - timedelta(hours=7)),
    ]


def make_incidents():
    return [
        Incident(service_id=CHECKOUT_ID, title="Checkout Service error rate spike — customers unable to complete purchases",
                 severity=Severity.critical, status=IncidentStatus.open),
    ]


async def seed():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        for obj in make_services():
            session.add(obj)
        await session.flush()

        for factory in [make_deployments, make_logs, make_metrics, make_git_changes, make_incidents]:
            for obj in factory():
                session.add(obj)
        await session.commit()

    print("Seeded successfully.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
