import json
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.models import Incident, Report, IncidentStatus
from app.engine.investigator import Investigator
from app.schemas import ReportOut

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.post("/{incident_id}/investigate")
async def start_investigation(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    incident = await db.get(Incident, incident_id)
    incident.status = IncidentStatus.investigating
    await db.commit()

    investigator = Investigator(db)

    async def event_generator():
        async for event in investigator.investigate_stream(incident.service_id):
            if event["event"] == "complete":
                report_data = event["report"]
                report = Report(
                    incident_id=incident_id,
                    root_cause=report_data["root_cause"],
                    confidence=report_data["confidence"],
                    evidence={"timeline": report_data.get("timeline", []), "agent_findings": report_data.get("agent_findings", [])},
                    recommendations=report_data.get("recommendations", []),
                )
                db.add(report)
                incident.status = IncidentStatus.resolved
                await db.commit()
                await db.refresh(report)

            yield {"event": event["event"], "data": json.dumps(event, default=str)}

    return EventSourceResponse(event_generator())


@router.get("/{incident_id}/report", response_model=ReportOut)
async def get_report(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Report).where(Report.incident_id == incident_id)
    result = await db.execute(stmt)
    report = result.scalar_one()
    return report
