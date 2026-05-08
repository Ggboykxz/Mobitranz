# ============================================================
# Routes Véhicules MobiTranz
# Fichier : backend/routers/vehicles.py
# Description : Routes /vehicles/* (enregistrement, QR, caméra)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import structlog

from backend.database import get_db
from backend.models.vehicle import Vehicle, VehicleStatus
from backend.services.qr_service import qr_service
from backend.services.camera_service import camera_service

logger = structlog.get_logger()
router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_vehicle(
    plate_number: str,
    brand: str,
    model: str,
    year: int = None,
    color: str = None,
    total_seats: int = 4,
    driver_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Enregistre un nouveau véhicule."""
    # Vérifier si la plaque existe déjà
    result = await db.execute(
        select(Vehicle).where(Vehicle.plate_number == plate_number)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Véhicule déjà enregistré"
        )

    vehicle = Vehicle(
        plate_number=plate_number,
        brand=brand,
        model=model,
        year=year,
        color=color,
        total_seats=total_seats,
        available_seats=total_seats,
        status=VehicleStatus.PENDING,
        driver_id=driver_id,
    )

    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    logger.info("Véhicule enregistré", vehicle_id=vehicle.id, plate=plate_number)

    return vehicle


@router.get("/{vehicle_id}")
async def get_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """Récupère les détails d'un véhicule."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    return {
        "id": vehicle.id,
        "plate_number": vehicle.plate_number,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "color": vehicle.color,
        "total_seats": vehicle.total_seats,
        "available_seats": vehicle.available_seats,
        "status": vehicle.status.value,
        "driver_id": vehicle.driver_id,
    }


@router.post("/{vehicle_id}/qr")
async def generate_vehicle_qr(
    vehicle_id: str, trip_id: str, db: AsyncSession = Depends(get_db)
):
    """Génère un QR Code dynamique pour un véhicule/trajet."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    # Générer le QR Code
    qr_image = await qr_service.generate_qr_code(vehicle_id, trip_id)

    # Mettre à jour la expire
    vehicle.qr_code = qr_image
    from datetime import timedelta

    vehicle.qr_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    await db.commit()

    logger.info("QR Code généré", vehicle_id=vehicle_id, trip_id=trip_id)

    return {"qr_code": qr_image, "expires_at": vehicle.qr_code_expires_at}


@router.post("/{vehicle_id}/camera/enable")
async def enable_camera(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """Active la caméra embarquée."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    vehicle.camera_enabled = True
    vehicle.camera_device_id = "/dev/video0"

    from backend.services.encryption_service import encryption_service

    vehicle.camera_encryption_key = encryption_service.encode_key_base64(
        encryption_service.generate_aes_key()
    )

    await db.commit()

    logger.info("Caméra activée", vehicle_id=vehicle_id)

    return {"status": "camera_enabled", "device": vehicle.camera_device_id}


@router.post("/{vehicle_id}/camera/disable")
async def disable_camera(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """Désactive la caméra."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    vehicle.camera_enabled = False
    await db.commit()

    logger.info("Caméra désactivée", vehicle_id=vehicle_id)

    return {"status": "camera_disabled"}


@router.post("/{vehicle_id}/location")
async def update_location(
    vehicle_id: str, lat: float, lon: float, db: AsyncSession = Depends(get_db)
):
    """Met à jour la localisation du véhicule."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    vehicle.current_lat = str(lat)
    vehicle.current_lon = str(lon)
    vehicle.last_update = datetime.now(timezone.utc)

    await db.commit()

    return {"status": "updated", "lat": lat, "lon": lon}


@router.get("/")
async def list_vehicles(db: AsyncSession = Depends(get_db), limit: int = 50):
    """Liste tous les véhicules."""
    result = await db.execute(select(Vehicle).limit(limit))
    vehicles = result.scalars().all()

    return [
        {
            "id": v.id,
            "plate_number": v.plate_number,
            "brand": v.brand,
            "model": v.model,
            "status": v.status.value,
            "available_seats": v.available_seats,
        }
        for v in vehicles
    ]
