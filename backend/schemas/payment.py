# ============================================================
# Schémas Paiement
# Fichier : backend/schemas/payment.py
# Description : Schémas de validation pour les paiements
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    """Schéma pour créer un paiement."""

    trip_id: str = Field(..., description="ID du trajet")
    method: str = Field(..., description="Méthode de paiement")
    phone_number: str = Field(..., description="Numéro de téléphone")


class PaymentResponse(BaseModel):
    """Schéma pour la réponse paiement."""

    id: str
    trip_id: str
    client_id: str
    amount: int
    currency: str
    method: str
    status: str
    external_transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    """Schema pour le webhook de paiement (appels serveur->serveur)."""

    transaction_id: str = Field(..., description="ID de transaction")
    status: str = Field(..., description="Statut (success/failed)")
    amount: int = Field(0, description="Montant en FCFA")
    message: Optional[str] = Field(None, description="Message optionnel")
    external_reference: Optional[str] = Field(None, description="Reference provider")


class PaymentConfirmRequest(BaseModel):
    """Schéma pour confirmer un paiement."""

    transaction_id: str = Field(..., description="ID de transaction externe")
