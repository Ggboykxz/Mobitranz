# ============================================================
# Modèle Journal d'Audit MobiTranz
# Fichier : backend/models/audit_log.py
# Description : Table des journaux d'audit immuables
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class AuditAction(enum.Enum):
    """Actions critiques journalisées."""

    LOGIN = "login"
    LOGOUT = "logout"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    VIDEO_ACCESSED = "video_accessed"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_SUSPENDED = "user_suspended"
    DRIVER_VALIDATED = "driver_validated"
    DRIVER_SUSPENDED = "driver_suspended"
    TRIP_CREATED = "trip_created"
    TRIP_COMPLETED = "trip_completed"
    TRIP_CANCELLED = "trip_cancelled"
    INCIDENT_REPORTED = "incident_reported"
    INCIDENT_ESCALATED = "incident_escalated"


class AuditLog(Base):
    """Modèle du journal d'audit MobiTranz.

    Table append-only avec hash chain pour intégrité.
    Chaque action critique génère une entrée auditoría.
    """

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    # Action et hash chain
    action = Column(Enum(AuditAction), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)

    # Données de l'action (JSON)
    details = Column(Text, nullable=True)

    # Meta contexte
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Métadonnées
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relations
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        """Représentation textuelle de l'entrée d'audit."""
        return f"<AuditLog {self.id[:8]} {self.action.value}>"
