# ============================================================
# Schémas Conducteur
# Fichier : backend/schemas/driver.py
# Description : Schémas de validation pour les drivers
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DriverCreate(BaseModel):
    """Schéma pour créer un driver."""
    
    user_id: str = Field(..., description="ID de l'utilisateur")
    license_number: str = Field(..., description="Numéro de permis")
    license_expiry: Optional[datetime] = Field(None, description="Date expiry permis")


class DriverUpdate(BaseModel):
    """Schéma pour mettre à jour un driver."""
    
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    status: Optional[str] = None


class DriverResponse(BaseModel):
    """Schéma pour la réponse driver."""
    
    id: str
    user_id: str
    status: str
    kyc_verified: bool
    license_number: Optional[str]
    vehicle_id: Optional[str]
    current_lat: Optional[float]
    current_lon: Optional[float]
    is_available: bool
    is_on_trip: bool
    total_trips: int
    rating: float
    total_earnings: int
    
    class Config:
        from_attributes = True


class DriverLocationUpdate(BaseModel):
    """Schéma pour mettre à jour la localisation."""
    
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)


class DriverAvailabilityUpdate(BaseModel):
    """Schéma pour mettre à jour la disponibilité."""
    
    is_available: bool = Field(..., description="Disponibilité")