# ============================================================
# Modèle Trajet MobiTranz
# Fichier : backend/models/trip.py
# Description : Table des trajets (trajet complet)
# ============================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class TripStatus(enum.Enum):
    """Statuts possibles d'un trajet MobiTranz."""

    PROPOSING = "proposing"
    HORN_PENDING = "horn_pending"
    PAYMENT_PENDING = "payment_pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INCIDENT = "incident"


class Trip(Base):
    """Modèle des trajets MobiTranz.

    Enregistre chaque trajet du début (proposition vocale) à la fin.
    Lié aux paiements, enregistrements vidéo et incidents.
    """

    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=False, index=True)
    vehicle_id = Column(
        String(36), ForeignKey("vehicles.id"), nullable=False, index=True
    )
    client_ids = Column(JSON, nullable=False, default=list)

    # Géolocalisation (PostGIS simplifié en string)
    origin_geo = Column(String(100), nullable=False)
    dest_geo = Column(String(100), nullable=True)
    origin_label = Column(String(200), nullable=False)
    dest_label = Column(String(200), nullable=False)

    # Tarification
    amount = Column(Integer, nullable=False)
    seats_count = Column(Integer, default=1)

    # Statut et timestamps
    status = Column(Enum(TripStatus), default=TripStatus.PROPOSING, nullable=False)
    proposed_at = Column(DateTime, nullable=False)
    horn_at = Column(DateTime, nullable=True)
    payment_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # QR Code utilisé
    qr_code_used = Column(String(255), nullable=True)

    # Métadonnées
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    # Relations
    driver = relationship("Driver", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
    payment = relationship("Payment", back_populates="trip", uselist=False)
    recording = relationship("Recording", back_populates="trip", uselist=False)
    voice_proposal = relationship("VoiceProposal", back_populates="trip", uselist=False)
    incidents = relationship("Incident", back_populates="trip")

    def __repr__(self):
        """Représentation textuelle du trajet."""
        return f"<Trip {self.id[:8]} ({self.status.value})>"
