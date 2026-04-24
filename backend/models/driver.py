# ============================================================
# Modèle Conducteur MobiTranz
# Fichier : backend/models/driver.py
# Description : Table des profils conducteur
# ============================================================

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
import enum
from backend.database import Base


class DriverStatus(enum.Enum):
    """Statuts possibles pour les conducteurs."""
    PENDING = "pending"
    VALIDATED = "validated"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Driver(Base):
    """Modèle des conducteiurs MobiTranz.
    
    Chaque conducteur a un profil vérifié avec documents KYC.
    Lié à un utilisateur et potentiellement à un véhicule.
    """
    
    __tablename__ = "drivers"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Statut et validation KYC
    status = Column(
        Enum(DriverStatus),
        default=DriverStatus.PENDING,
        nullable=False
    )
    kyc_verified = Column(Boolean, default=False)
    kyc_verified_at = Column(DateTime, nullable=True)
    
    # Documents KYC
    license_number = Column(String(50), nullable=True)
    license_expiry = Column(DateTime, nullable=True)
    permit_number = Column(String(50), nullable=True)
    permit_expiry = Column(DateTime, nullable=True)
    id_card_number = Column(String(50), nullable=True)
    
    # Véhicule attaché (optionnel)
    vehicle_id = Column(
        String(36),
        ForeignKey("vehicles.id"),
        nullable=True,
        index=True
    )
    
    # Géolocalisation temps réel
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    
    # Disponibilité
    is_available = Column(Boolean, default=False)
    is_on_trip = Column(Boolean, default=False)
    
    # Statistiques
    total_trips = Column(Integer, default=0)
    rating = Column(Float, default=5.0)
    total_earnings = Column(Integer, default=0)
    
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
    user = relationship("User", back_populates="driver_profile")
    vehicle = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")
    
    def __repr__(self):
        """Représentation textuelle du conducteur."""
        return f"<Driver {self.user_id} ({self.status.value})>"