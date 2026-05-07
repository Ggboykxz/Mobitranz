# ============================================================
# Modèle Points GPS Trajet MobiTranz
# Fichier : backend/models/trip_gps.py
# Description : Table des points GPS enregistrés pendant les trajets
# ============================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from backend.database import Base


class TripGpsPoint(Base):
    """Modèle des points GPS d'un trajet.
    
    Enregistre la position du véhicule à intervalles réguliers
    pendant un trajet pour le suivi et la détection de déviation.
    """
    
    __tablename__ = "trip_gps_points"
    
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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    speed_kmh = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    accuracy_meters = Column(Float, nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<TripGpsPoint {self.trip_id} ({self.latitude}, {self.longitude})>"