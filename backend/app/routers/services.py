from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Service, Deployment, Incident
from app.schemas import ServiceOut

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
async def list_services(db: AsyncSession = Depends(get_db)):
    stmt = select(Service).order_by(Service.name)
    result = await db.execute(stmt)
    services = result.scalars().all()

    out = []
    for s in services:
        dep_count = await db.scalar(select(func.count()).where(Deployment.service_id == s.id))
        inc_count = await db.scalar(select(func.count()).where(Incident.service_id == s.id))
        out.append(ServiceOut(
            id=s.id, name=s.name, status=s.status, created_at=s.created_at,
            deployment_count=dep_count or 0, incident_count=inc_count or 0,
        ))
    return out


@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(service_id: UUID, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, service_id)
    dep_count = await db.scalar(select(func.count()).where(Deployment.service_id == service_id))
    inc_count = await db.scalar(select(func.count()).where(Incident.service_id == service_id))
    return ServiceOut(
        id=service.id, name=service.name, status=service.status, created_at=service.created_at,
        deployment_count=dep_count or 0, incident_count=inc_count or 0,
    )
