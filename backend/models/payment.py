# ============================================================
# Modèle Paiement MobiTranz
# Fichier : backend/models/payment.py
# Description : Table des transactions de paiement
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class PaymentStatus(enum.Enum):
    """Statuts possibles pour un paiement."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    """Méthodes de paiement disponibles."""

    MOOVMONEY = "moovmoney"
    AIRTELMONEY = "airtelmoney"
    CARD = "card"
    BIOMETRIC = "biometric"
    CASH = "cash"


class Payment(Base):
    """Modèle des paiements MobiTranz.

    Gère toutes les transactions financières liées aux trajets.
    Supporte MoovMoney, Airtel Money, carte et biométrie.
    """

    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Montant et devise
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="XAF")

    # Méthode et statut
    method = Column(
        Enum(PaymentMethod), default=PaymentMethod.MOOVMONEY, nullable=False
    )
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Données externes
    external_transaction_id = Column(String(255), nullable=True)
    provider_reference = Column(String(255), nullable=True)
    provider_response = Column(String(1000), nullable=True)

    # Numéro de téléphone utilisé
    phone_number = Column(String(20), nullable=False)

    # Métadonnées
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String(500), nullable=True)

    # Relations
    trip = relationship("Trip", back_populates="payment")
    client = relationship("User")

    def __repr__(self):
        """Représentation textuelle du paiement."""
        return f"<Payment {self.id[:8]} {self.amount}XAF ({self.status.value})>"
