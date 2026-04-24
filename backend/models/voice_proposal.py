# ============================================================
# Modèle Proposition Vocale MobiTranz
# Fichier : backend/models/voice_proposal.py
# Description : Table des propositions vocales
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from backend.database import Base


class VoiceProposal(Base):
    """Modèle des propositions vocales MobiTranz.
    
    Enregistre les propositions vocales soumises par les clients.
    Contient la transcription et les informations extraites.
    """
    
    __tablename__ = "voice_proposals"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    trip_id = Column(
        String(36),
        ForeignKey("trips.id"),
        nullable=False,
        index=True
    )
    client_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Audio brut (optionnel, pour fallback)
    audio_path = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)
    
    # Transcription
    transcription = Column(String(2000), nullable=False)
    confidence_score = Column(Integer, nullable=True)
    
    # Informations extraites
    extracted_destination = Column(String(200), nullable=True)
    extracted_amount = Column(Integer, nullable=True)
    extracted_seats = Column(Integer, nullable=True)
    
    # Statut de validation
    is_validated = Column(String(10), default="false")
    validated_at = Column(DateTime, nullable=True)
    validation_source = Column(String(50), nullable=True)
    
    # Langue détectée
    detected_language = Column(String(10), default="fr")
    
    # Métadonnées
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relations
    trip = relationship("Trip", back_populates="voice_proposal")
    client = relationship("User")
    
    def __repr__(self):
        """Représentation textuelle de la proposition vocale."""
        return f"<VoiceProposal {self.id[:8]} -> {self.extracted_destination}>"