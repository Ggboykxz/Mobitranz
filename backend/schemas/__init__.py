# ============================================================
# Schémas User Complets
# Fichier : backend/schemas/user.py
# Description : Schémas de validation pour user
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""

    phone: str = Field(..., description="Numéro de téléphone")
    email: Optional[str] = Field(None, description="Adresse email")
    first_name: Optional[str] = Field(None, description="Prénom")
    last_name: Optional[str] = Field(None, description="Nom")


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur."""

    password: str = Field(..., description="Mot de passe", min_length=8)


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur."""

    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(UserBase):
    """Schéma pour la réponse utilisateur."""

    id: str
    role: str
    status: str
    kyc_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DriverProfileResponse(BaseModel):
    """Schéma pour le profil conducteur."""

    id: str
    user_id: str
    status: str
    kyc_verified: bool
    license_number: Optional[str]
    is_available: bool
    is_on_trip: bool
    total_trips: int
    rating: float
    total_earnings: int

    class Config:
        from_attributes = True
