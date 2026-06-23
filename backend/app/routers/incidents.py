from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Incident, Service, Report
from app.schemas import IncidentCreate, IncidentOut

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
async def list_incidents(service_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Incident).order_by(Incident.created_at.desc())
    if service_id:
        stmt = stmt.where(Incident.service_id == service_id)
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    out = []
    for inc in incidents:
        service = await db.get(Service, inc.service_id)
        report_exists = await db.scalar(select(func.count()).where(Report.incident_id == inc.id))
        out.append(IncidentOut(
            id=inc.id, service_id=inc.service_id, service_name=service.name,
            title=inc.title, severity=inc.severity, status=inc.status,
            created_at=inc.created_at, has_report=bool(report_exists),
        ))
    return out


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(service_id=body.service_id, title=body.title, severity=body.severity)
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    service = await db.get(Service, incident.service_id)
    return IncidentOut(
        id=incident.id, service_id=incident.service_id, service_name=service.name,
        title=incident.title, severity=incident.severity, status=incident.status,
        created_at=incident.created_at, has_report=False,
    )


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    incident = await db.get(Incident, incident_id)
    service = await db.get(Service, incident.service_id)
    report_exists = await db.scalar(select(func.count()).where(Report.incident_id == incident_id))
    return IncidentOut(
        id=incident.id, service_id=incident.service_id, service_name=service.name,
        title=incident.title, severity=incident.severity, status=incident.status,
        created_at=incident.created_at, has_report=bool(report_exists),
    )
