# ============================================================
# Modèle Proposition Vocale MobiTranz
# Fichier : backend/models/voice_proposal.py
# Description : Table des propositions vocales
# ============================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from backend.database import Base


class VoiceProposal(Base):
    __tablename__ = "voice_proposals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=True, index=True)
    client_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=True, index=True)

    audio_path = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)

    transcription = Column(String(2000), nullable=False)
    confidence_score = Column(Integer, nullable=True)

    extracted_destination = Column(String(200), nullable=True)
    extracted_amount = Column(Integer, nullable=True)
    extracted_seats = Column(Integer, nullable=True)

    pickup_lat = Column(Float, nullable=True)
    pickup_lon = Column(Float, nullable=True)
    dest_lat = Column(Float, nullable=True)
    dest_lon = Column(Float, nullable=True)
    dest_label = Column(String(200), nullable=True)
    amount = Column(Integer, nullable=True)
    seats_requested = Column(Integer, nullable=True)

    is_validated = Column(String(10), default="false")
    validated_at = Column(DateTime, nullable=True)
    validation_source = Column(String(50), nullable=True)

    detected_language = Column(String(10), default="fr")

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trip = relationship("Trip", back_populates="voice_proposal")
    client = relationship("User")

    def __repr__(self):
        return f"<VoiceProposal {self.id[:8]} -> {self.extracted_destination}>"
