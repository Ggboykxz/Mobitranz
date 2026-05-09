# ============================================================
# Service Ministère MobiTranz
# Fichier : backend/services/ministry_service.py
# Description : Intégration avec les API ministérielles (Transport, Intérieur)
# ============================================================

import httpx
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

logger = structlog.get_logger()


class MinistryService:
    """Service d'intégration avec les ministères gabonais.

    Gère les échanges de données avec le Ministère du Transport
    et le Ministère de l'Intérieur.
    """

    async def send_transport_report(self, data: dict) -> bool:
        """Envoie un rapport au Ministère des Transports.

        Args:
            data: Données du rapport

        Returns:
            bool: True si l'envoi a réussi
        """
        if not settings.ministry_transport_webhook:
            logger.warning("Ministère Transport webhook non configuré")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.ministry_transport_webhook,
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": settings.ministry_api_key or "",
                    },
                    timeout=30.0,
                )

                response.raise_for_status()

                logger.info("Rapport envoyé au Ministère des Transports")
                return True

        except httpx.TimeoutException:
            logger.error("Timeout envoi rapport Ministère Transport")
            return False
        except Exception as e:
            logger.error("Erreur envoi rapport Ministère Transport", error=str(e))
            return False

    async def send_interior_report(self, data: dict) -> bool:
        """Envoie un rapport au Ministère de l'Intérieur.

        Args:
            data: Données du rapport

        Returns:
            bool: True si l'envoi a réussi
        """
        if not settings.ministry_interior_webhook:
            logger.warning("Ministère Intérieur webhook non configuré")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.ministry_interior_webhook,
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": settings.ministry_api_key or "",
                    },
                    timeout=30.0,
                )

                response.raise_for_status()

                logger.info("Rapport envoyé au Ministère de l'Intérieur")
                return True

        except httpx.TimeoutException:
            logger.error("Timeout envoi rapport Ministère Intérieur")
            return False
        except Exception as e:
            logger.error("Erreur envoi rapport Ministère Intérieur", error=str(e))
            return False

    async def send_sos_alert(
        self,
        incident_id: str,
        trip_id: str,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> bool:
        """Envoie une alerte SOS au Ministère de l'Intérieur.

        Args:
            incident_id: ID de l'incident
            trip_id: ID du trajet
            latitude: Latitude
            longitude: Longitude
            timestamp: Horodatage

        Returns:
            bool: True si l'envoi a réussi
        """
        alert_data = {
            "incident_type": "SOS",
            "incident_id": incident_id,
            "trip_id": trip_id,
            "location": {"latitude": latitude, "longitude": longitude},
            "timestamp": timestamp.isoformat(),
            "source": "MobiTranz",
        }

        return await self.send_interior_report(alert_data)

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
