# ============================================================
# Modèle Zone
# Fichier : backend/models/zone.py
# Description : Zones tarifaires Libreville
# ============================================================

import uuid
from sqlalchemy import Column, String, Numeric, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from backend.database import Base


class Zone(Base):
    """Modèle Zone.

    Définit les zones tarifaires de Libreville avec prix de base.
    """

    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    base_price = Column(Numeric(10, 0), nullable=False)
    keywords = Column(String(500), nullable=False)
    lat_min = Column(Numeric(10, 7), nullable=True)
    lat_max = Column(Numeric(10, 7), nullable=True)
    lon_min = Column(Numeric(10, 7), nullable=True)
    lon_max = Column(Numeric(10, 7), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0)

    def contains_point(self, lat: float, lon: float) -> bool:
        if not all([self.lat_min, self.lat_max, self.lon_min, self.lon_max]):
            return False
        return float(self.lat_min) <= lat <= float(self.lat_max) and float(
            self.lon_min
        ) <= lon <= float(self.lon_max)

    def __repr__(self):
        return f"<Zone {self.name} [{self.display_name}]>"
