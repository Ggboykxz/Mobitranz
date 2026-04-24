# ============================================================
# Routes Conducteurs MobiTranz
# Fichier : backend/routers/drivers.py
# Description : Routes /drivers/* (inscription, validation KYC, localisation)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import structlog

from backend.database import get_db
from backend.models.driver import Driver, DriverStatus
from backend.models.user import User, UserRole, UserStatus
from backend.schemas.user import UserCreate, DriverProfileResponse


logger = structlog.get_logger()
router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("/register", response_model=DriverProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Inscrit un nouveau conducteur.
    
    Crée un compte utilisateur avec rôle DRIVER et un profil conducteur.
    Le conducteur est en attente de validation KYC.
    """
    # Vérifier si le téléphone existe déjà
    result = await db.execute(
        select(User).where(User.phone == data.phone)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numéro de téléphone déjà enregistré"
        )
    
    # Créer l'utilisateur
    from backend.services.auth_service import auth_service
    user = User(
        phone=data.phone,
        email=data.email,
        password_hash=auth_service.hash_password(data.password),
        role=UserRole.DRIVER,
        status=UserStatus.ACTIVE,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    
    db.add(user)
    await db.flush()
    
    # Créer le profil conducteur
    driver = Driver(
        id=f"driver_{user.id[:8]}",
        user_id=user.id,
        status=DriverStatus.PENDING,
    )
    
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    
    logger.info("Conducteur inscrit", driver_id=driver.id, user_id=user.id)
    
    return driver


@router.get("/", response_model=list)
async def list_drivers(
    db: AsyncSession = Depends(get_db),
    status_filter: str = None,
    limit: int = 50,
    offset: int = 0
):
    """Liste les conducteurs avec filtres."""
    query = select(Driver)
    
    if status_filter:
        try:
            driver_status = DriverStatus(status_filter)
            query = query.where(Driver.status == driver_status)
        except ValueError:
            pass
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    drivers = result.scalars().all()
    
    return drivers


@router.get("/{driver_id}", response_model=DriverProfileResponse)
async def get_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère les détails d'un conducteur."""
    result = await db.execute(
        select(Driver).where(Driver.id == driver_id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conducteur non trouvé"
        )
    
    return driver


@router.post("/{driver_id}/validate")
async def validate_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Valide un conducteur après vérification KYC.
    
    Marque le conducteur comme validé et active son compte.
    """
    result = await db.execute(
        select(Driver).where(Driver.id == driver_id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conducteur non trouvé"
        )
    
    if driver.status == DriverStatus.VALIDATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conducteur déjà validé"
        )
    
    driver.status = DriverStatus.VALIDATED
    driver.kyc_verified = True
    driver.kyc_verified_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info("Conducteur validé", driver_id=driver_id)
    
    return {"status": "validated", "driver_id": driver_id}


@router.post("/{driver_id}/suspend")
async def suspend_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Suspend un conducteur."""
    result = await db.execute(
        select(Driver).where(Driver.id == driver_id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conducteur non trouvé"
        )
    
    driver.status = DriverStatus.SUSPENDED
    driver.is_available = False
    
    await db.commit()
    
    logger.warning("Conducteur suspendu", driver_id=driver_id)
    
    return {"status": "suspended", "driver_id": driver_id}


@router.post("/{driver_id}/location")
async def update_location(
    driver_id: str,
    lat: float,
    lon: float,
    db: AsyncSession = Depends(get_db)
):
    """Met à jour la localisation d'un conducteur."""
    result = await db.execute(
        select(Driver).where(Driver.id == driver_id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conducteur non trouvé"
        )
    
    driver.current_lat = lat
    driver.current_lon = lon
    driver.last_location_update = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "updated", "lat": lat, "lon": lon}


@router.get("/{driver_id}/available")
async def get_available_drivers(
    lat: float = None,
    lon: float = None,
    radius_km: float = 10.0,
    db: AsyncSession = Depends(get_db)
):
    """Retourne les conductores disponibles (optionnellement par proximité).
    
    Si lat/lon fournis, filtre par rayon sinon retourne tous.
    """
    query = select(Driver).where(
        Driver.status == DriverStatus.VALIDATED,
        Driver.is_available == True,
        Driver.is_on_trip == False
    )
    
    result = await db.execute(query)
    drivers = result.scalars().all()
    
    # Note: Pour une vraie implémentation PostGIS, utiliser ST_DWithin
    # Cela retourne simplement tous les disponibilités pour l'instant
    available = []
    for driver in drivers:
        available.append({
            "id": driver.id,
            "lat": driver.current_lat,
            "lon": driver.current_lon,
            "rating": driver.rating,
            "total_trips": driver.total_trips,
        })
    
    return available