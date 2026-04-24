# ============================================================
# Modèle Incident MobiTranz
# Fichier : backend/models/incident.py
# Description : Table des alertes et incidents SOS
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class IncidentType(enum.Enum):
    """Types d'incidents possibles."""
    SOS = "sos"
    ACCIDENT = "accident"
    DISPUTE = "dispute"
    THEFT = "theft"
    HARASSMENT = "harassment"
    OTHER = "other"


class IncidentStatus(enum.Enum):
    """Statuts possibles pour un incident."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(Base):
    """Modèle des incidents MobiTranz.
    
    Gère les alertes SOS et autres incidents pendant les trajets.
    Chaque incident peut être catégorisé et escaladé aux autorités.
    """
    
    __tablename__ = "incidents"
    
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
    reporter_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Type et statut
    incident_type = Column(
        Enum(IncidentType),
        default=IncidentType.SOS,
        nullable=False
    )
    status = Column(
        Enum(IncidentStatus),
        default=IncidentStatus.PENDING,
        nullable=False
    )
    
    # Description
    description = Column(String(2000), nullable=True)
    location = Column(String(200), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Audio incident (optionnel)
    audio_path = Column(String(500), nullable=True)
    
    # Escalade
    escalated_to = Column(String(200), nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    escalation_reason = Column(String(500), nullable=True)
    
    # Résolution
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(String(1000), nullable=True)
    resolved_by = Column(String(36), nullable=True)
    
    # Métadonnées
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )
    
    # Relations
    trip = relationship("Trip", back_populates="incidents")
    reporter = relationship("User")
    
    def __repr__(self):
        """Représentation textuelle de l'incident."""
        return f"<Incident {self.id[:8]} ({self.incident_type.value})>"