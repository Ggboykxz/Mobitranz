# ============================================================
# Modèle Enregistrement MobiTranz
# Fichier : backend/models/recording.py
# Description : Table des vidéos chiffrées (caméra embarquée)
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class RecordingStatus(enum.Enum):
    """Statuts possibles pour un enregistrement."""
    RECORDING = "recording"
    PROCESSING = "processing"
    READY = "ready"
    ENCRYPTED = "encrypted"
    DELETED = "deleted"


class Recording(Base):
    """Modèle des enregistrements vidéo MobiTranz.
    
    Gère les vidéos de caméra embarquée pendant les trajets.
    Chiffrement AES-256-GCM avec clé stockée séparément.
    Accès restreint : admin + forces de l'ordre.
    """
    
    __tablename__ = "recordings"
    
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
    vehicle_id = Column(
        String(36),
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )
    
    # Fichier vidéo
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Chiffrement
    encryption_key_id = Column(String(36), nullable=True)
    encryption_nonce = Column(String(50), nullable=True)
    is_encrypted = Column(String(10), default="false")
    
    # Statut et format
    status = Column(
        Enum(RecordingStatus),
        default=RecordingStatus.RECORDING,
        nullable=False
    )
    mime_type = Column(String(50), default="video/mp4")
    
    # Accès (pour audit)
    access_count = Column(Integer, default=0)
    last_access_by = Column(String(36), nullable=True)
    last_access_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    trip = relationship("Trip", back_populates="recording")
    vehicle = relationship("Vehicle", back_populates="recordings")
    
    def __repr__(self):
        """Représentation textuelle de l'enregistrement."""
        return f"<Recording {self.id[:8]} ({self.status.value})>"