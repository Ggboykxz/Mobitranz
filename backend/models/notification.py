# ============================================================
# Modèle Notification
# Fichier : backend/models/notification.py
# Description : Historique des notifications push
# ============================================================

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Notification(Base):
    """Modèle Notification.
    
    Stocke l'historique des notifications push envoyées.
    """
    
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(Text, nullable=True)
    notification_type = Column(String(50), nullable=False)
    sent_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    fcm_message_id = Column(String(200), nullable=True)
    error = Column(Text, nullable=True)
    
    def mark_read(self):
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<Notification {self.id} [{self.notification_type}]>"