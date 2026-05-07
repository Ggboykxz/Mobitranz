# ============================================================
# Modèle Raspberry Pi Véhicule MobiTranz
# Fichier : backend/models/raspberry_pi.py
# Description : Table des unités Raspberry Pi dans les véhicules
# ============================================================

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class RaspberryPiStatus(enum.Enum):
    """Statuts possibles pour les unités Raspberry Pi."""
    PENDING = "pending"
    ACTIVE = "active"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class RaspberryPiUnit(Base):
    """Modèle des unités Raspberry Pi MobiTranz.
    
    Chaque unité Raspberry Pi est associée à un véhicule
    et gère la caméra, le klaxon, le GPS et l'écran.
    """
    
    __tablename__ = "raspberry_pi_units"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    serial_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Association véhicule
    vehicle_id = Column(
        String(36),
        nullable=True,
        index=True
    )
    
    # Statut
    status = Column(
        Enum(RaspberryPiStatus),
        default=RaspberryPiStatus.PENDING,
        nullable=False
    )
    
    # Configuration
    firmware_version = Column(String(20), nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)
    
    # Configuration hardware
    camera_enabled = Column(Boolean, default=False)
    camera_device_id = Column(String(100), nullable=True)
    microphone_enabled = Column(Boolean, default=False)
    gps_enabled = Column(Boolean, default=False)
    
    # Clé de chiffrement AES pour les vidéos
    encryption_key_encrypted = Column(String(500), nullable=True)
    
    # Capteur anti-sabotage
    tamper_detected = Column(Boolean, default=False)
    tamper_detected_at = Column(DateTime, nullable=True)
    
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
    vehicle = relationship("Vehicle", back_populates="raspberry_pi")

    def __repr__(self):
        return f"<RaspberryPi {self.serial_number} ({self.status.value})>"