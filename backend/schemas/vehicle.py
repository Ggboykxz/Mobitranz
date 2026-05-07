# ============================================================
# Schémas Véhicule
# Fichier : backend/schemas/vehicle.py
# Description : Schémas de validation pour les véhicules
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VehicleCreate(BaseModel):
    """Schéma pour créer un véhicule."""
    
    plate_number: str = Field(..., description="Numéro de plaque")
    brand: str = Field(..., description="Marque")
    model: str = Field(..., description="Modèle")
    year: Optional[int] = Field(None, description="Année", ge=1900, le=2100)
    color: Optional[str] = Field(None, description="Couleur")
    total_seats: int = Field(4, description="Nombre de places", ge=1, le=20)


class VehicleUpdate(BaseModel):
    """Schéma pour mettre à jour un véhicule."""
    
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    total_seats: Optional[int] = None
    status: Optional[str] = None


class VehicleResponse(BaseModel):
    """Schéma pour la réponse véhicule."""
    
    id: str
    plate_number: str
    brand: str
    model: str
    year: Optional[int]
    color: Optional[str]
    total_seats: int
    available_seats: int
    status: str
    driver_id: Optional[str]
    camera_enabled: bool
    
    class Config:
        from_attributes = True


class VehicleQRGenerate(BaseModel):
    """Schéma pour générer un QR code véhicule."""
    
    trip_id: str = Field(..., description="ID du trajet")