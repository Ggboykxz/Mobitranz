# ============================================================
# Routes Incidents MobiTranz
# Fichier : backend/routers/incidents.py
# Description : Routes /incidents/* (signalement, escalation)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import structlog

from backend.database import get_db
from backend.models.incident import Incident, IncidentType, IncidentStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/report", status_code=status.HTTP_201_CREATED)
async def report_incident(
    trip_id: str,
    reporter_id: str,
    incident_type: str,
    description: str = None,
    latitude: float = None,
    longitude: float = None,
    location: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Signale un incident pendant un trajet."""
    try:
        inc_type = IncidentType(incident_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Type d'incident invalide"
        )

    incident = Incident(
        trip_id=trip_id,
        reporter_id=reporter_id,
        incident_type=inc_type,
        status=IncidentStatus.PENDING,
        description=description,
        latitude=str(latitude) if latitude else None,
        longitude=str(longitude) if longitude else None,
        location=location,
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    logger.warning(
        "Incident signalé", incident_id=incident.id, trip_id=trip_id, type=incident_type
    )

    return incident


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Récupère les détails d'un incident."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident non trouvé"
        )

    return incident


@router.post("/{incident_id}/acknowledge")
async def acknowledge_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Acquitte un incident."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident non trouvé"
        )

    incident.status = IncidentStatus.ACKNOWLEDGED
    await db.commit()

    logger.info("Incident acquitté", incident_id=incident_id)

    return {"status": "acknowledged"}


@router.post("/{incident_id}/escalate")
async def escalate_incident(
    incident_id: str,
    escalate_to: str,
    reason: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Escalade un incident aux autorités."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident non trouvé"
        )

    incident.status = IncidentStatus.ESCALATED
    incident.escalated_to = escalate_to
    incident.escalated_at = datetime.now(timezone.utc)
    incident.escalation_reason = reason

    await db.commit()

    logger.warning(
        "Incident escaladé", incident_id=incident_id, escalate_to=escalate_to
    )

    return {"status": "escalated", "escalated_to": escalate_to}


@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution: str,
    resolved_by: str,
    db: AsyncSession = Depends(get_db),
):
    """Résout un incident."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident non trouvé"
        )

    incident.status = IncidentStatus.RESOLVED
    incident.resolved_at = datetime.now(timezone.utc)
    incident.resolution = resolution
    incident.resolved_by = resolved_by

    await db.commit()

    logger.info("Incident résolu", incident_id=incident_id)

    return {"status": "resolved"}


@router.get("/")
async def list_incidents(
    db: AsyncSession = Depends(get_db),
    status_filter: str = None,
    type_filter: str = None,
    limit: int = 50,
):
    """Liste les incidents avec filtres."""
    query = select(Incident)

    if status_filter:
        try:
            s = IncidentStatus(status_filter)
            query = query.where(Incident.status == s)
        except ValueError:
            pass

    if type_filter:
        try:
            t = IncidentType(type_filter)
            query = query.where(Incident.incident_type == t)
        except ValueError:
            pass

    query = query.limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()

    return incidents


@router.get("/open")
async def get_open_incidents(db: AsyncSession = Depends(get_db)):
    """Retourne tous les incidents ouverts."""
    result = await db.execute(
        select(Incident).where(
            Incident.status.in_(
                [
                    IncidentStatus.PENDING,
                    IncidentStatus.ACKNOWLEDGED,
                    IncidentStatus.ESCALATED,
                ]
            )
        )
    )
    incidents = result.scalars().all()

    return [
        {
            "id": i.id,
            "type": i.incident_type.value,
            "status": i.status.value,
            "trip_id": i.trip_id,
            "created_at": i.created_at,
        }
        for i in incidents
    ]
