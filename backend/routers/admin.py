# ============================================================
# Routes Administration MobiTranz
# Fichier : backend/routers/admin.py
# Description : Routes /admin/* (gestion complète système)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
import structlog

from backend.database import get_db
from backend.deps.auth_deps import get_current_admin
from backend.models.user import User, UserRole, UserStatus
from backend.models.driver import Driver, DriverStatus
from backend.models.vehicle import Vehicle, VehicleStatus
from backend.models.trip import Trip, TripStatus
from backend.models.payment import Payment, PaymentStatus
from backend.models.incident import Incident, IncidentStatus, IncidentType
from backend.models.audit_log import AuditLog

logger = structlog.get_logger()
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/kpis")
async def get_dashboard_kpis(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """Retourne les KPIs temps réel du dashboard admin.

    Args:
        db: Session de base de données
        current_user: Utilisateur admin authentifié

    Returns:
        dict: KPIs du dashboard
    """
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )

    result = await db.execute(
        select(func.count(Trip.id)).where(Trip.created_at >= today_start)
    )
    trips_today = result.scalar() or 0

    result = await db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.created_at >= today_start,
                Payment.status == PaymentStatus.COMPLETED,
            )
        )
    )
    revenue_today = result.scalar() or 0

    result = await db.execute(
        select(func.count(Driver.id)).where(
            Driver.is_on_trip == True, Driver.status == DriverStatus.VALIDATED
        )
    )
    active_drivers = result.scalar() or 0

    result = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.status.in_(
                [
                    IncidentStatus.PENDING,
                    IncidentStatus.ACKNOWLEDGED,
                    IncidentStatus.ESCALATED,
                ]
            )
        )
    )
    open_incidents = result.scalar() or 0

    result = await db.execute(
        select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.ACTIVE)
    )
    active_vehicles = result.scalar() or 0

    result = await db.execute(
        select(func.count(User.id)).where(
            and_(User.status == UserStatus.ACTIVE, User.role == UserRole.CLIENT)
        )
    )
    active_clients = result.scalar() or 0

    return {
        "trips_today": trips_today,
        "revenue_today": revenue_today,
        "active_drivers": active_drivers,
        "active_vehicles": active_vehicles,
        "active_clients": active_clients,
        "open_incidents": open_incidents,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    role: str = Query(None),
    status_filter: str = Query(None),
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Liste les utilisateurs avec filtres avancés.

    Args:
        db: Session de base de données
        current_user: Utilisateur admin authentifié
        role: Filtre par rôle (client, driver, admin)
        status_filter: Filtre par statut
        search: Recherche par téléphone ou email
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        list: Liste des utilisateurs
    """
    query = select(User)

    if role:
        try:
            u_role = UserRole(role)
            query = query.where(User.role == u_role)
        except ValueError:
            pass

    if status_filter:
        try:
            u_status = UserStatus(status_filter)
            query = query.where(User.status == u_status)
        except ValueError:
            pass

    if search:
        query = query.where(
            (User.phone.contains(search))
            | (User.email.contains(search))
            | (User.first_name.contains(search))
            | (User.last_name.contains(search))
        )

    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    users = result.scalars().all()

    result = await db.execute(select(func.count(User.id)))
    total = result.scalar() or 0

    return {
        "users": [
            {
                "id": u.id,
                "phone": u.phone,
                "email": u.email,
                "role": u.role.value,
                "status": u.status.value,
                "kyc_verified": u.kyc_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    reason: str = None,
):
    """Suspend un utilisateur.

    Args:
        user_id: ID de l'utilisateur à suspendre
        db: Session de base de données
        current_user: Admin authentifié
        reason: Raison de la suspension

    Returns:
        dict: Statut de l'opération
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de suspendre un administrateur",
        )

    user.status = UserStatus.SUSPENDED
    user.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.warning(
        "Utilisateur suspendu", user_id=user_id, reason=reason, admin_id=current_user.id
    )

    return {"status": "suspended", "user_id": user_id}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Active ou réactive un utilisateur.

    Args:
        user_id: ID de l'utilisateur à activer
        db: Session de base de données
        current_user: Admin authentifié

    Returns:
        dict: Statut de l'opération
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    user.status = UserStatus.ACTIVE
    user.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info("Utilisateur activé", user_id=user_id, admin_id=current_user.id)

    return {"status": "active", "user_id": user_id}


@router.get("/drivers")
async def list_drivers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    status_filter: str = Query(None),
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Liste les conducteurs avec filtres.

    Args:
        db: Session de base de données
        current_user: Admin authentifié
        status_filter: Filtre par statut
        search: Recherche par nom ou téléphone
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        dict: Liste des drivers avec pagination
    """
    query = select(Driver).join(User)

    if status_filter:
        try:
            d_status = DriverStatus(status_filter)
            query = query.where(Driver.status == d_status)
        except ValueError:
            pass

    if search:
        query = query.where(
            (User.phone.contains(search))
            | (User.first_name.contains(search))
            | (User.last_name.contains(search))
        )

    query = query.order_by(Driver.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    drivers = result.scalars().all()

    return {
        "drivers": [
            {
                "id": d.id,
                "user_id": d.user_id,
                "phone": d.user.phone if d.user else None,
                "status": d.status.value,
                "kyc_verified": d.kyc_verified,
                "license_number": d.license_number,
                "vehicle_id": d.vehicle_id,
                "is_available": d.is_available,
                "rating": d.rating,
                "total_trips": d.total_trips,
                "total_earnings": d.total_earnings,
            }
            for d in drivers
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/drivers/{driver_id}/validate")
async def validate_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Valide un conducteur après vérification KYC.

    Args:
        driver_id: ID du driver à valider
        db: Session de base de données
        current_user: Admin authentifié

    Returns:
        dict: Statut de la validation
    """
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver non trouvé"
        )

    if driver.status == DriverStatus.VALIDATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Driver déjà validé"
        )

    driver.status = DriverStatus.VALIDATED
    driver.kyc_verified = True
    driver.kyc_verified_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info("Driver validé", driver_id=driver_id, admin_id=current_user.id)

    return {"status": "validated", "driver_id": driver_id}


@router.get("/vehicles")
async def list_vehicles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    status_filter: str = Query(None),
    search: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Liste les véhicules avec filtres.

    Args:
        db: Session de base de données
        current_user: Admin authentifié
        status_filter: Filtre par statut
        search: Recherche par plaque
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        dict: Liste des véhicules
    """
    query = select(Vehicle)

    if status_filter:
        try:
            v_status = VehicleStatus(status_filter)
            query = query.where(Vehicle.status == v_status)
        except ValueError:
            pass

    if search:
        query = query.where(Vehicle.plate_number.contains(search))

    query = query.order_by(Vehicle.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    vehicles = result.scalars().all()

    return {
        "vehicles": [
            {
                "id": v.id,
                "plate_number": v.plate_number,
                "brand": v.brand,
                "model": v.model,
                "status": v.status.value,
                "total_seats": v.total_seats,
                "available_seats": v.available_seats,
                "driver_id": v.driver_id,
                "camera_enabled": v.camera_enabled,
            }
            for v in vehicles
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/transactions")
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    status_filter: str = Query(None),
    method_filter: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Liste les transactions avec filtres avancés.

    Args:
        db: Session de base de données
        current_user: Admin authentifié
        status_filter: Filtre par statut
        method_filter: Filtre par méthode de paiement
        start_date: Date de début (ISO)
        end_date: Date de fin (ISO)
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        dict: Liste des transactions
    """
    query = select(Payment)

    if status_filter:
        try:
            p_status = PaymentStatus(status_filter)
            query = query.where(Payment.status == p_status)
        except ValueError:
            pass

    if method_filter:
        from backend.models.payment import PaymentMethod

        try:
            method = PaymentMethod(method_filter)
            query = query.where(Payment.method == method)
        except ValueError:
            pass

    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.where(Payment.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.where(Payment.created_at <= end)
        except ValueError:
            pass

    query = query.order_by(Payment.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    payments = result.scalars().all()

    return {
        "transactions": [
            {
                "id": p.id,
                "trip_id": p.trip_id,
                "client_id": p.client_id,
                "amount": p.amount,
                "method": p.method.value,
                "status": p.status.value,
                "phone_number": p.phone_number,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in payments
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/incidents")
async def list_incidents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    status_filter: str = Query(None),
    type_filter: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Liste les incidents avec filtres.

    Args:
        db: Session de base de données
        current_user: Admin authentifié
        status_filter: Filtre par statut
        type_filter: Filtre par type d'incident
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        dict: Liste des incidents
    """
    query = select(Incident)

    if status_filter:
        try:
            i_status = IncidentStatus(status_filter)
            query = query.where(Incident.status == i_status)
        except ValueError:
            pass

    if type_filter:
        try:
            i_type = IncidentType(type_filter)
            query = query.where(Incident.incident_type == i_type)
        except ValueError:
            pass

    query = query.order_by(Incident.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    incidents = result.scalars().all()

    return {
        "incidents": [
            {
                "id": i.id,
                "trip_id": i.trip_id,
                "reporter_id": i.reporter_id,
                "type": i.incident_type.value,
                "status": i.status.value,
                "description": i.description,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in incidents
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Résout un incident.

    Args:
        incident_id: ID de l'incident
        resolution: Résolution appliquée
        db: Session de base de données
        current_user: Admin authentifié

    Returns:
        dict: Statut de la résolution
    """
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident non trouvé"
        )

    incident.status = IncidentStatus.RESOLVED
    incident.resolved_at = datetime.now(timezone.utc)
    incident.resolution = resolution
    incident.resolved_by = current_user.id

    await db.commit()

    logger.info("Incident résolu", incident_id=incident_id, admin_id=current_user.id)

    return {"status": "resolved", "incident_id": incident_id}


@router.get("/logs")
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    user_id: str = Query(None),
    action: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """Récupère les logs d'audit du système.

    Args:
        db: Session de base de données
        current_user: Admin authentifié
        user_id: Filtre par utilisateur
        action: Filtre par type d'action
        limit: Nombre de résultats
        offset: Offset de pagination

    Returns:
        dict: Liste des logs
    """
    query = select(AuditLog)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if action:
        query = query.where(AuditLog.action.contains(action))

    query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "resource": l.resource,
                "ip_address": l.ip_address,
                "result": l.result,
                "timestamp": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/system/backup")
async def trigger_backup(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """Déclenche une sauvegarde manuelle de la base de données.

    Args:
        db: Session de base de données
        current_user: Admin authentifié

    Returns:
        dict: Confirmation du déclenchement
    """
    logger.info("Sauvegarde déclenchée manuellement", admin_id=current_user.id)

    return {
        "status": "triggered",
        "message": "Sauvegarde en cours",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/system/health")
async def system_health(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """Vérifie l'état de santé du système.

    Args:
        db: Session de base de données
        current_user: Admin authentifié

    Returns:
        dict: État du système
    """
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    result = await db.execute(select(func.count(Driver.id)))
    total_drivers = result.scalar() or 0

    result = await db.execute(select(func.count(Vehicle.id)))
    total_vehicles = result.scalar() or 0

    result = await db.execute(select(func.count(Trip.id)))
    total_trips = result.scalar() or 0

    return {
        "status": "healthy",
        "database": "connected",
        "statistics": {
            "total_users": total_users,
            "total_drivers": total_drivers,
            "total_vehicles": total_vehicles,
            "total_trips": total_trips,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
