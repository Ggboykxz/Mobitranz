# ============================================================
# Routes Analytics MobiTranz
# Fichier : backend/routers/analytics.py
# Description : Routes /analytics/* (KPIs, rapports ministères)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
import structlog

from backend.database import get_db
from backend.deps.auth_deps import get_current_admin, get_current_ministry
from backend.models.trip import Trip, TripStatus
from backend.models.payment import Payment, PaymentStatus
from backend.models.driver import Driver
from backend.models.incident import Incident, IncidentStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/kpis")
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Retourne les KPIs temps réel."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )

    # Trajets aujourd'hui
    trips_today = await db.execute(
        select(func.count(Trip.id)).where(Trip.created_at >= today_start)
    )
    trips_count = trips_today.scalar()

    # Revenus aujourd'hui
    result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.created_at >= today_start, Payment.status == PaymentStatus.COMPLETED
        )
    )
    revenue_today = result.scalar() or 0

    # Conducteurs actifs
    active_drivers = await db.execute(
        select(func.count(Driver.id)).where(Driver.is_on_trip == True)
    )
    drivers_count = active_drivers.scalar()

    # Incidents ouverts
    open_incidents = await db.execute(
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
    incidents_count = open_incidents.scalar()

    return {
        "trips_today": trips_count,
        "revenue_today": revenue_today,
        "active_drivers": drivers_count,
        "open_incidents": incidents_count,
    }


@router.get("/trips/by-day")
async def get_trips_by_day(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Retourne les trajets par jour sur N jours."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(select(Trip).where(Trip.created_at >= start_date))
    trips = result.scalars().all()

    # Grouper par jour
    by_day = {}
    for trip in trips:
        day = trip.created_at.date().isoformat()
        by_day[day] = by_day.get(day, 0) + 1

    return by_day


@router.get("/revenue/by-day")
async def get_revenue_by_day(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Retourne les revenus par jour."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    results = await db.execute(
        select(Payment).where(
            Payment.created_at >= start_date, Payment.status == PaymentStatus.COMPLETED
        )
    )
    payments = results.scalars().all()

    by_day = {}
    for payment in payments:
        day = payment.created_at.date().isoformat()
        by_day[day] = by_day.get(day, 0) + payment.amount

    return by_day


@router.get("/payment-methods")
async def get_payment_methods_breakdown(
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Répartition par méthode de paiement."""
    result = await db.execute(
        select(Payment.method, func.count(Payment.id)).group_by(Payment.method)
    )
    counts = result.all()

    return {method.value: count for method, count in counts}


@router.get("/drivers/top")
async def get_top_drivers(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Top conducteurs par revenus."""
    result = await db.execute(
        select(Driver).order_by(Driver.total_earnings.desc()).limit(limit)
    )
    drivers = result.scalars().all()

    return [
        {
            "id": d.id,
            "total_trips": d.total_trips,
            "total_earnings": d.total_earnings,
            "rating": d.rating,
        }
        for d in drivers
    ]


@router.get("/incidents/by-type")
async def get_incidents_by_type(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Répartition des incidents par type."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Incident.incident_type, func.count(Incident.id))
        .where(Incident.created_at >= start_date)
        .group_by(Incident.incident_type)
    )
    counts = result.all()

    return {inc_type.value: count for inc_type, count in counts}


@router.get("/export/csv")
async def export_trips_csv(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_admin),
):
    """Exporte les trajets en CSV (pour rapports ministère).

    Format: trip_id,driver_id,client_ids,origin,dest,amount,status,created_at
    """
    import csv
    import io

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    result = await db.execute(
        select(Trip).where(Trip.created_at >= start, Trip.created_at <= end)
    )
    trips = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "trip_id",
            "driver_id",
            "client_ids",
            "origin_label",
            "dest_label",
            "amount",
            "status",
            "created_at",
        ]
    )

    # Data
    for trip in trips:
        writer.writerow(
            [
                trip.id,
                trip.driver_id,
                ",".join(trip.client_ids),
                trip.origin_label,
                trip.dest_label,
                trip.amount,
                trip.status.value,
                trip.created_at.isoformat(),
            ]
        )

    return {
        "csv": output.getvalue(),
        "count": len(trips),
        "date_range": f"{start_date} to {end_date}",
    }


@router.get("/ministry-report")
async def generate_ministry_report(
    year: int = None,
    month: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_ministry),
):
    """Génère un rapport pour le Ministère des Transports."""
    if year is None:
        year = datetime.now(timezone.utc).year
    if month is None:
        month = datetime.now(timezone.utc).month

    from datetime import timedelta

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

    # Total trips
    trips_result = await db.execute(
        select(func.count(Trip.id)).where(
            Trip.created_at >= start_date,
            Trip.created_at <= end_date,
            Trip.status == TripStatus.COMPLETED,
        )
    )
    total_trips = trips_result.scalar()

    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.created_at >= start_date,
            Payment.created_at <= end_date,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    total_revenue = revenue_result.scalar() or 0

    # Incidents
    incidents_result = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.created_at >= start_date, Incident.created_at <= end_date
        )
    )
    total_incidents = incidents_result.scalar()

    return {
        "period": f"{year}-{month:02d}",
        "total_trips": total_trips,
        "total_revenue_xaf": total_revenue,
        "total_incidents": total_incidents,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
