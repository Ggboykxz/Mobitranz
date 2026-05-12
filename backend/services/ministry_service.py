# ============================================================
# Service Ministère MobiTranz
# Fichier : backend/services/ministry_service.py
# Description : Intégration avec les API ministérielles (Transport, Intérieur)
# ============================================================

import structlog
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.config import settings
from backend.models.trip import Trip, TripStatus
from backend.models.payment import Payment, PaymentStatus
from backend.models.incident import Incident, IncidentStatus
from backend.models.driver import Driver
from backend.tasks.ministry_tasks import (
    send_transport_report_task,
    send_interior_report_task,
    send_sos_alert_task,
)

logger = structlog.get_logger()


class MinistryService:
    """Service d'intégration avec les ministères gabonais.

    Gère les échanges de données avec le Ministère du Transport
    et le Ministère de l'Intérieur. Les appels HTTP sont délégués
    à Celery pour un traitement asynchrone.
    """

    async def send_transport_report(self, data: dict) -> bool:
        """Envoie un rapport au Ministère des Transports via Celery.

        Args:
            data: Données du rapport

        Returns:
            bool: True si la tâche a été soumise
        """
        if not settings.ministry_transport_webhook:
            logger.warning("Ministère Transport webhook non configuré")
            return False

        send_transport_report_task.delay(data)
        logger.info("Rapport Transport soumis à Celery")
        return True

    async def send_interior_report(self, data: dict) -> bool:
        """Envoie un rapport au Ministère de l'Intérieur via Celery.

        Args:
            data: Données du rapport

        Returns:
            bool: True si la tâche a été soumise
        """
        if not settings.ministry_interior_webhook:
            logger.warning("Ministère Intérieur webhook non configuré")
            return False

        send_interior_report_task.delay(data)
        logger.info("Rapport Intérieur soumis à Celery")
        return True

    async def send_sos_alert(
        self,
        incident_id: str,
        trip_id: str,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> bool:
        """Envoie une alerte SOS au Ministère de l'Intérieur via Celery.

        Args:
            incident_id: ID de l'incident
            trip_id: ID du trajet
            latitude: Latitude
            longitude: Longitude
            timestamp: Horodatage

        Returns:
            bool: True si la tâche a été soumise
        """
        send_sos_alert_task.delay(
            incident_id, trip_id, latitude, longitude, timestamp.isoformat()
        )
        logger.info("Alerte SOS soumise à Celery", incident_id=incident_id)
        return True

    async def generate_monthly_transport_report(
        self, db: AsyncSession, year: int, month: int
    ) -> dict:
        """Génère le rapport mensuel pour le Ministère des Transports.

        Args:
            db: Session de base de données
            year: Année
            month: Mois

        Returns:
            dict: Données du rapport
        """
        from datetime import timedelta

        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(
                seconds=1
            )
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(
                seconds=1
            )

        result = await db.execute(
            select(func.count(Trip.id)).where(
                Trip.created_at >= start_date,
                Trip.created_at <= end_date,
                Trip.status == TripStatus.COMPLETED,
            )
        )
        total_trips = result.scalar() or 0

        result = await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == PaymentStatus.COMPLETED,
            )
        )
        total_revenue = result.scalar() or 0

        result = await db.execute(
            select(func.count(Driver.id)).where(Driver.status == "validated")
        )
        active_drivers = result.scalar() or 0

        report = {
            "period": f"{year}-{month:02d}",
            "total_trips": total_trips,
            "total_revenue_xaf": total_revenue,
            "active_drivers": active_drivers,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_source": "MobiTranz Platform",
        }

        await self.send_transport_report(report)

        return report

    async def generate_security_report(self, db: AsyncSession, days: int = 30) -> dict:
        """Génère le rapport de sécurité pour le Ministère de l'Intérieur.

        Args:
            db: Session de base de données
            days: Nombre de jours à inclure

        Returns:
            dict: Données du rapport
        """
        from datetime import timedelta

        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(func.count(Incident.id)).where(Incident.created_at >= start_date)
        )
        total_incidents = result.scalar() or 0

        result = await db.execute(
            select(func.count(Incident.id)).where(
                Incident.created_at >= start_date,
                Incident.status == IncidentStatus.ESCALATED,
            )
        )
        escalated_incidents = result.scalar() or 0

        result = await db.execute(
            select(func.count(Incident.id)).where(
                Incident.created_at >= start_date,
                Incident.incident_type.in_(["sos", "accident"]),
            )
        )
        serious_incidents = result.scalar() or 0

        report = {
            "period_days": days,
            "total_incidents": total_incidents,
            "escalated_incidents": escalated_incidents,
            "serious_incidents": serious_incidents,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_source": "MobiTranz Platform",
        }

        await self.send_interior_report(report)

        return report

    async def get_vehicle_registry(self, db: AsyncSession) -> list:
        """Récupère le registre des véhicules pour les ministères.

        Args:
            db: Session de base de données

        Returns:
            list: Liste des véhicules
        """
        from backend.models.vehicle import Vehicle, VehicleStatus

        result = await db.execute(
            select(Vehicle).where(Vehicle.status == VehicleStatus.ACTIVE)
        )
        vehicles = result.scalars().all()

        return [
            {
                "id": v.id,
                "plate_number": v.plate_number,
                "brand": v.brand,
                "model": v.model,
                "total_seats": v.total_seats,
                "status": v.status.value,
            }
            for v in vehicles
        ]


ministry_service = MinistryService()
