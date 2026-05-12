# ============================================================
# Modèle Journal d'Audit MobiTranz
# Fichier : backend/models/audit_log.py
# Description : Table des journaux d'audit immuables
# ============================================================

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from backend.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=True)
    result = Column(String(20), default="success")
    details = Column(Text, nullable=True)
    data_hash = Column(String(64), nullable=True)
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.id[:8]} {self.action}>"
