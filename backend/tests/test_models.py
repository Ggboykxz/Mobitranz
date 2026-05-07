# ============================================================
# Tests Models MobiTranz
# Fichier : backend/tests/test_models.py
# ============================================================

import pytest
from datetime import datetime


class TestTripGPS:
    """Tests pour le modèle TripGpsPoint."""
    
    def test_trip_gps_import(self):
        """Test import du modèle."""
        from backend.models.trip_gps import TripGpsPoint
        assert TripGpsPoint is not None
    
    def test_trip_gps_tablename(self):
        """Test nom de table."""
        from backend.models.trip_gps import TripGpsPoint
        assert TripGpsPoint.__tablename__ == "trip_gps_points"


class TestRaspberryPi:
    """Tests pour le modèle RaspberryPiUnit."""
    
    def test_raspberry_pi_import(self):
        """Test import du modèle."""
        from backend.models.raspberry_pi import RaspberryPiUnit
        assert RaspberryPiUnit is not None
    
    def test_raspberry_pi_tablename(self):
        """Test nom de table."""
        from backend.models.raspberry_pi import RaspberryPiUnit
        assert RaspberryPiUnit.__tablename__ == "raspberry_pi_units"
    
    def test_raspberry_pi_status_values(self):
        """Test valeurs de statut."""
        from backend.models.raspberry_pi import RaspberryPiStatus
        
        assert RaspberryPiStatus.ACTIVE.value == "active"
        assert RaspberryPiStatus.OFFLINE.value == "offline"
        assert RaspberryPiStatus.MAINTENANCE.value == "maintenance"


class TestZone:
    """Tests pour le modèle Zone."""
    
    def test_zone_import(self):
        """Test import du modèle."""
        from backend.models.zone import Zone
        assert Zone is not None


class TestNotification:
    """Tests pour le modèle Notification."""
    
    def test_notification_import(self):
        """Test import du modèle."""
        from backend.models.notification import Notification
        assert Notification is not None
    
    def test_notification_tablename(self):
        """Test nom de table."""
        from backend.models.notification import Notification
        assert Notification.__tablename__ == "notifications"


class TestRedisClient:
    """Tests pour le client Redis."""
    
    def test_redis_client_import(self):
        """Test import du client."""
        from backend.redis_client import redis_client
        assert redis_client is not None


class TestConfig:
    """Tests pour la configuration."""
    
    def test_config_import(self):
        """Test import config."""
        from backend.config import settings
        assert settings is not None
    
    def test_settings_attributes(self):
        """Test attributs settings."""
        from backend.config import settings
        
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'app_version')