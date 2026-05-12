# ============================================================
# Modèle Véhicule MobiTranz
# Fichier : backend/models/vehicle.py
# Description : Table des véhicules (QR, caméra, places)
# ============================================================

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
import enum
from backend.database import Base


class VehicleStatus(enum.Enum):
    """Statuts possibles pour les véhicules."""

    PENDING = "pending"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class Vehicle(Base):
    """Modèle des véhicules MobiTranz.

    Chaque véhicule a un QR Code unique, une caméra embarquée
    et un nombre de places défini pour les passagers.
    """

    __tablename__ = "vehicles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identification
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=True)
    color = Column(String(30), nullable=True)

    # QR Code dynamique
    qr_code = Column(String(255), nullable=True)
    qr_code_expires_at = Column(DateTime, nullable=True)

    # Caméra
    camera_enabled = Column(Boolean, default=False)
    camera_device_id = Column(String(100), nullable=True)
    camera_encryption_key = Column(String(255), nullable=True)

    # Places disponibles
    total_seats = Column(Integer, default=4, nullable=False)
    available_seats = Column(Integer, default=4, nullable=False)

    # Statut
    status = Column(Enum(VehicleStatus), default=VehicleStatus.PENDING, nullable=False)

    # Association conducteur
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=True, index=True)

    # Localisation actuelle
    current_lat = Column(String(20), nullable=True)
    current_lon = Column(String(20), nullable=True)
    last_update = Column(DateTime, nullable=True)

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
    driver = relationship("Driver", back_populates="vehicle")
    trips = relationship("Trip", back_populates="vehicle")
    recordings = relationship("Recording", back_populates="vehicle")
    raspberry_pi = relationship("RaspberryPiUnit", back_populates="vehicle")

    def __repr__(self):
        """Représentation textuelle du véhicule."""
        return f"<Vehicle {self.plate_number}>"
