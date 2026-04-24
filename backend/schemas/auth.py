# ============================================================
# Schémas Pydantic MobiTranz
# Fichier : backend/schemas/auth.py
# Description : Schémas de validation pour l'authentification
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Schéma pour la connexion utilisateur."""
    
    phone: str = Field(
        ...,
        description="Numéro de téléphone au format +241XXXXXXXX",
        min_length=10,
        max_length=20
    )
    password: str = Field(
        ...,
        description="Mot de passe",
        min_length=8
    )


class UserRegister(BaseModel):
    """Schéma pour l'inscription utilisateur."""
    
    phone: str = Field(
        ...,
        description="Numéro de téléphone au format +241XXXXXXXX",
        min_length=10,
        max_length=20
    )
    email: Optional[str] = Field(
        None,
        description="Adresse email",
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    password: str = Field(
        ...,
        description="Mot de passe",
        min_length=8
    )
    first_name: Optional[str] = Field(
        None,
        description="Prénom",
        max_length=100
    )
    last_name: Optional[str] = Field(
        None,
        description="Nom",
        max_length=100
    )


class OTPRequest(BaseModel):
    """Schéma pour la demande OTP."""
    
    phone: str = Field(
        ...,
        description="Numéro de téléphone"
    )


class BiometricLogin(BaseModel):
    """Schéma pour la connexion biométrique."""
    
    user_id: str = Field(
        ...,
        description="Identifiant utilisateur"
    )
    biometric_hash: str = Field(
        ...,
        description="Hash des données biométriques"
    )


class TokenResponse(BaseModel):
    """Schéma pour la réponse de token."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schéma pour le rafraîchissement de token."""
    
    refresh_token: str


class TOTPEnable(BaseModel):
    """Schéma pour activer le 2FA TOTP."""
    
    secret: str
    code: str = Field(
        ...,
        description="Code TOTP à 6 chiffres"
    )


class TOTPDisable(BaseModel):
    """Schéma pour désactiver le 2FA TOTP."""
    
    code: str = Field(
        ...,
        description="Code TOTP à 6 chiffres"
    )