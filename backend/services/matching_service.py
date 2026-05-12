# ============================================================
# Service de Matching Client-Taxi MobiTranz
# Fichier : backend/services/matching_service.py
# Description : Algorithme de matching client avec taxis disponibles
# ============================================================

from typing import List, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.models.driver import Driver, DriverStatus
from backend.models.vehicle import Vehicle, VehicleStatus
from backend.services.geo_service import geo_service
from backend.services.voice_service import voice_proposal_service

logger = structlog.get_logger()


class MatchingService:
    """Service de matching client-taxi MobiTranz.

    Gère la recherche et la mise en relation des clients
    avec les taxis disponibles à proximité.
    """

    async def find_available_taxis(
        self,
        db: AsyncSession,
        client_lat: float,
        client_lon: float,
        radius_km: float = 5.0,
        max_results: int = 10,
    ) -> List[dict]:
        """Trouve les taxis disponibles à proximité du client.

        Args:
            db: Session de base de données
            client_lat: Latitude du client
            client_lon: Longitude du client
            radius_km: Rayon de recherche en km
            max_results: Nombre maximum de résultats

        Returns:
            list: Liste des taxis disponibles avec leurs infos
        """
        result = await db.execute(
            select(Driver).where(
                and_(
                    Driver.status == DriverStatus.VALIDATED,
                    Driver.is_available == True,
                    Driver.is_on_trip == False,
                )
            )
        )
        drivers = result.scalars().all()

        available_taxis = []

        for driver in drivers:
            if driver.current_lat and driver.current_lon:
                distance = geo_service.calculate_distance(
                    client_lat, client_lon, driver.current_lat, driver.current_lon
                )

                if distance <= radius_km:
                    vehicle = None
                    if driver.vehicle_id:
                        v_result = await db.execute(
                            select(Vehicle).where(Vehicle.id == driver.vehicle_id)
                        )
                        vehicle = v_result.scalar_one_or_none()

                    available_taxis.append(
                        {
                            "driver_id": driver.id,
                            "driver_name": (
                                f"{driver.user.first_name} {driver.user.last_name}"
                                if driver.user
                                else "Inconnu"
                            ),
                            "phone": driver.user.phone if driver.user else None,
                            "distance_km": round(distance, 2),
                            "eta_minutes": geo_service.calculate_eta(distance),
                            "rating": driver.rating,
                            "total_trips": driver.total_trips,
                            "vehicle_brand": vehicle.brand if vehicle else None,
                            "vehicle_model": vehicle.model if vehicle else None,
                            "vehicle_color": vehicle.color if vehicle else None,
                            "available_seats": (
                                vehicle.available_seats if vehicle else 4
                            ),
                            "latitude": driver.current_lat,
                            "longitude": driver.current_lon,
                        }
                    )

        available_taxis.sort(key=lambda x: (x["distance_km"], -x["rating"]))

        return available_taxis[:max_results]

    async def calculate_estimated_fare(
        self,
        db: AsyncSession,
        driver_id: str,
        destination_lat: float,
        destination_lon: float,
    ) -> dict:
        """Calcule le tarif estimé pour un trajet.

        Args:
            db: Session de base de données
            driver_id: ID du driver sélectionné
            destination_lat: Latitude de destination
            destination_lon: Longitude de destination

        Returns:
            dict: Détails du tarif estimé
        """
        result = await db.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()

        if not driver or not driver.current_lat or not driver.current_lon:
            return {"error": "Driver non trouvé ou position invalide"}

        distance = geo_service.calculate_distance(
            driver.current_lat, driver.current_lon, destination_lat, destination_lon
        )

        fare_info = await geo_service.calculate_trip_fare(db=db, distance_km=distance)

        fare_info["pickup_distance_km"] = distance

        return fare_info

    async def create_proposal(
        self,
        db: AsyncSession,
        driver_id: str,
        client_id: str,
        pickup_lat: float,
        pickup_lon: float,
        dest_lat: float,
        dest_lon: float,
        dest_label: str = None,
    ) -> dict:
        """Crée une proposition de trajet pour le driver.

        Args:
            db: Session de base de données
            driver_id: ID du driver
            client_id: ID du client
            pickup_lat: Latitude de départ
            pickup_lon: Longitude de départ
            dest_lat: Latitude de destination
            dest_lon: Longitude de destination
            dest_label: Nom de la destination

        Returns:
            dict: Proposition créée
        """
        distance = geo_service.calculate_distance(
            pickup_lat, pickup_lon, dest_lat, dest_lon
        )

        fare_info = await geo_service.calculate_trip_fare(db=db, distance_km=distance)

        from backend.models.voice_proposal import VoiceProposal

        proposal = VoiceProposal(
            driver_id=driver_id,
            client_id=client_id,
            pickup_lat=pickup_lat,
            pickup_lon=pickup_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            dest_label=dest_label,
            amount=fare_info["final_amount"],
            seats_requested=1,
            is_validated="false",
        )

        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)

        logger.info(
            "Proposition créée",
            proposal_id=proposal.id,
            driver_id=driver_id,
            client_id=client_id,
            amount=fare_info["final_amount"],
        )

        return {
            "proposal_id": proposal.id,
            "amount": fare_info["final_amount"],
            "distance_km": distance,
            "eta_minutes": geo_service.calculate_eta(distance),
        }

    async def get_matching_score(
        self,
        driver: Driver,
        client_lat: float,
        client_lon: float,
        vehicle: Vehicle = None,
    ) -> float:
        """Calcule un score de matching pour un driver.

        Args:
            driver: Driver à évaluer
            client_lat: Latitude du client
            client_lon: Longitude du client
            vehicle: Véhicule du driver

        Returns:
            float: Score de matching (0-100)
        """
        if not driver.current_lat or not driver.current_lon:
            return 0.0

        distance = geo_service.calculate_distance(
            client_lat, client_lon, driver.current_lat, driver.current_lon
        )

        distance_score = max(0, 100 - (distance * 20))

        rating_score = driver.rating * 20

        trips_score = min(driver.total_trips * 2, 40)

        seats_score = (vehicle.available_seats if vehicle else 4) * 10

        total_score = (
            (distance_score * 0.4)
            + (rating_score * 0.3)
            + (trips_score * 0.2)
            + (seats_score * 0.1)
        )

        return round(total_score, 2)


matching_service = MatchingService()
