# ============================================================
# Modèle Trajet
# Fichier : backend/schemas/trip.py
# Description : Schémas de validation pour les trajets
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TripCreate(BaseModel):
    """Schéma pour créer un trajet."""

    driver_id: str = Field(..., description="ID du conducteur")
    vehicle_id: str = Field(..., description="ID du véhicule")
    origin_label: str = Field(..., description="Libellé du point de départ")
    dest_label: str = Field(..., description="Libellé de la destination")
    origin_lat: float = Field(..., description="Latitude départ")
    origin_lon: float = Field(..., description="Longitude départ")
    dest_lat: Optional[float] = Field(None, description="Latitude arrivée")
    dest_lon: Optional[float] = Field(None, description="Longitude'arrivée")
    amount: int = Field(..., description="Montant en XAF", ge=100)
    seats_count: int = Field(1, description="Nombre de places", ge=1, le=8)


class TripUpdate(BaseModel):
    """Schéma pour mettre à jour un trajet."""

    status: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None


class TripResponse(BaseModel):
    """Schéma pour la réponse trajet."""

    id: str
    driver_id: str
    vehicle_id: str
    client_ids: List[str]
    origin_label: str
    dest_label: str
    amount: int
    seats_count: int
    status: str
    proposed_at: datetime
    horn_at: Optional[datetime]
    payment_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class VoiceProposalSubmit(BaseModel):
    """Schéma pour soumettre une proposition vocale."""

    driver_id: str = Field(..., description="ID du conducteur")
    origin_label: str = Field(..., description="Zone de départ")
    dest_label: str = Field(..., description="Zone de destination")
    audio_data: str = Field(..., description="Audio encodé base64")


class HornValidation(BaseModel):
    """Schéma pour la validation klaxon."""

    trip_id: str = Field(..., description="ID du trajet")
    pattern: str = Field(..., description="Pattern détecté (accept/refuse)")


class TripLocationUpdate(BaseModel):
    """Schéma pour mettre à jour la localisation."""

    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
