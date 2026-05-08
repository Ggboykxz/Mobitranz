# ============================================================
# Schémas Incidents
# Fichier : backend/schemas/incident.py
# Description : Schémas de validation pour les incidents
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IncidentCreate(BaseModel):
    """Schéma pour créer un incident."""

    trip_id: str = Field(..., description="ID du trajet")
    reporter_id: str = Field(..., description="ID du reporter")
    incident_type: str = Field(..., description="Type d'incident")
    description: Optional[str] = Field(None, description="Description")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    location: Optional[str] = Field(None, description="Nom du lieu")


class IncidentResponse(BaseModel):
    """Schéma pour la réponse incident."""

    id: str
    trip_id: str
    reporter_id: str
    incident_type: str
    status: str
    description: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    escalated_to: Optional[str]
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentEscalate(BaseModel):
    """Schéma pour escalader un incident."""

    escalate_to: str = Field(..., description="Destination de l'escalade")
    reason: Optional[str] = Field(None, description="Raison")


class IncidentResolve(BaseModel):
    """Schéma pour résoudre un incident."""

    resolution: str = Field(..., description="Résolution appliquée")
