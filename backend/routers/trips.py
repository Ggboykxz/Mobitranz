# ============================================================
# Routeur Trajets MobiTranz
# Fichier : backend/routers/trips.py
# Description : Routes /trips/* (création, suivi, fin)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import structlog

from backend.database import get_db
from backend.schemas.trip import TripCreate, TripResponse, HornValidation
from backend.models.trip import Trip, TripStatus
from backend.models.driver import Driver
from backend.models.voice_proposal import VoiceProposal
from backend.redis_client import redis_client
from backend.services.horn_detection import horn_detection_service


logger = structlog.get_logger()
router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    data: TripCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crée un nouveau trajet.
    
    Crée un trajet après acceptation d'une proposition vocale
    et validation klaxon.
    """
    result = await db.execute(
        select(Driver).where(Driver.id == data.driver_id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conducteur non trouvé"
        )
    
    trip = Trip(
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        client_ids=[],
        origin_geo=f"{data.origin_lat},{data.origin_lon}",
        dest_geo=f"{data.dest_lat},{data.dest_lon}" if data.dest_lat else None,
        origin_label=data.origin_label,
        dest_label=data.dest_label,
        amount=data.amount,
        seats_count=data.seats_count,
        status=TripStatus.PROPOSING,
        proposed_at=datetime.now(timezone.utc),
    )
    
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    
    logger.info("Trajet créé", trip_id=trip.id, driver_id=data.driver_id)
    
    return trip


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère les détails d'un trajet."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    return trip


@router.post("/{trip_id}/Horn", status_code=status.HTTP_200_OK)
async def validate_horn(
    trip_id: str,
    data: HornValidation,
    db: AsyncSession = Depends(get_db)
):
    """Valide le pattern klaxon pour un trajet.
    
    Reçoit les données audio du microphone véhicule
    et détecte le pattern klaxon.
    """
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if data.pattern == "accept":
        trip.status = TripStatus.HORN_PENDING
        trip.horn_at = datetime.now(timezone.utc)
        
        # Activer la proposition dans Redis (fenêtre 30s)
        await redis_client.set_proposal_active(
            trip.id,
            trip.driver_id,
            {"destination": trip.dest_label, "amount": trip.amount},
            window_seconds=30
        )
        
        logger.info("Klaxon ACCEPTATION", trip_id=trip_id)
        
    elif data.pattern == "refuse":
        trip.status = TripStatus.CANCELLED
        
        logger.info("Klaxon REFUS", trip_id=trip_id)
    
    await db.commit()
    
    return {"status": "updated", "pattern": data.pattern}


@router.post("/{trip_id}/start", response_model=TripResponse)
async def start_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Démarre un trajet après paiement confirmé."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if trip.status != TripStatus.PAYMENT_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paiement non confirmé"
        )
    
    trip.status = TripStatus.ACTIVE
    trip.started_at = datetime.now(timezone.utc)
    await db.commit()
    
    logger.info("Trajet démarré", trip_id=trip_id)
    
    return trip


@router.post("/{trip_id}/complete", response_model=TripResponse)
async def complete_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Marque un trajet comme terminé."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    trip.status = TripStatus.COMPLETED
    trip.completed_at = datetime.now(timezone.utc)
    await db.commit()
    
    logger.info("Trajet terminé", trip_id=trip_id)
    
    return trip


@router.get("/driver/{driver_id}/active")
async def get_active_trip(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère le trajet actif d'un conducteur."""
    result = await db.execute(
        select(Trip).where(
            Trip.driver_id == driver_id,
            Trip.status == TripStatus.ACTIVE
        )
    )
    trip = result.scalar_one_or_none()
    
    if not trip:
        return None
    
    return trip


@router.post("/{trip_id}/join")
async def join_trip(
    trip_id: str,
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Permet à un client de rejoindre un trajet."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if trip.status not in [TripStatus.PROPOSING, TripStatus.HORN_PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajet non joignable"
        )
    
    if client_id in trip.client_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Déjà dans ce trajet"
        )
    
    if len(trip.client_ids) >= trip.seats_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajet complet"
        )
    
    trip.client_ids = trip.client_ids + [client_id]
    await db.commit()
    
    logger.info("Client a rejoint", trip_id=trip_id, client_id=client_id)
    
    return {"status": "joined", "client_count": len(trip.client_ids)}


@router.delete("/{trip_id}/clients/{client_id}")
async def leave_trip(
    trip_id: str,
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Permet à un client de quitter un trajet."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if trip.status == TripStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajet déjà commencé"
        )
    
    if client_id not in trip.client_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pas dans ce trajet"
        )
    
    trip.client_ids = [c for c in trip.client_ids if c != client_id]
    await db.commit()
    
    logger.info("Client a quitté", trip_id=trip_id, client_id=client_id)
    
    return {"status": "left", "client_count": len(trip.client_ids)}


@router.post("/{trip_id}/cancel")
async def cancel_trip(
    trip_id: str,
    reason: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Annule un trajet."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if trip.status == TripStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajet déjà terminé"
        )
    
    trip.status = TripStatus.CANCELLED
    trip.completed_at = datetime.now(timezone.utc)
    await db.commit()
    
    logger.info("Trajet annulé", trip_id=trip_id, reason=reason)
    
    return {"status": "cancelled"}