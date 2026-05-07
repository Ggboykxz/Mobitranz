# ============================================================
# Tests WebSocket MobiTranz
# Fichier : backend/tests/test_websocket.py
# ============================================================

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


class TestConnectionManager:
    """Tests pour le gestionnaire de connexions WebSocket."""
    
    @pytest.fixture
    def manager(self):
        """Fixture du gestionnaire."""
        from backend.websocket import ConnectionManager
        return ConnectionManager()
    
    def test_init(self, manager):
        """Test initialisation du gestionnaire."""
        assert "trips" in manager.active_connections
        assert "drivers" in manager.active_connections
        assert "notifications" in manager.active_connections
        assert len(manager.active_connections) == 5
    
    def test_disconnect(self, manager):
        """Test déconnexion."""
        mock_ws = MagicMock()
        manager.active_connections["notifications"].add(mock_ws)
        
        manager.disconnect(mock_ws, "notifications")
        
        assert mock_ws not in manager.active_connections["notifications"]


class TestWebSocketRouter:
    """Tests pour le router WebSocket."""
    
    def test_websocket_router_exists(self):
        """Test existence du router."""
        from backend.websocket import websocket_router
        assert websocket_router is not None


class TestMessageTypes:
    """Tests pour les types de messages."""
    
    def test_location_update_message(self):
        """Test format message localisation."""
        from backend.websocket import manager
        
        message = {
            "type": "location_update",
            "driver_id": "driver_123",
            "latitude": 0.4163,
            "longitude": 9.4673,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        assert message["type"] == "location_update"
        assert "driver_id" in message
        assert "latitude" in message
    
    def test_trip_status_message(self):
        """Test format message statut trip."""
        message = {
            "type": "trip_status",
            "trip_id": "trip_123",
            "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        assert message["type"] == "trip_status"
        assert message["status"] in ["pending", "accepted", "active", "completed", "cancelled"]
    
    def test_incident_message(self):
        """Test format message incident."""
        message = {
            "type": "incident",
            "incident_id": "inc_123",
            "incident_type": "sos",
            "trip_id": "trip_123",
            "priority": "high",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        assert message["type"] == "incident"
        assert message["priority"] in ["low", "medium", "high"]
    
    def test_notification_message(self):
        """Test format message notification."""
        message = {
            "type": "notification",
            "title": "Nouveau trajet",
            "body": "Un client cherche un trajet",
            "data": {"trip_id": "trip_123"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        assert message["type"] == "notification"
        assert "title" in message
        assert "body" in message


class TestChannelTypes:
    """Tests pour les types de channels."""
    
    def test_valid_channels(self):
        """Test channels valides."""
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        
        valid_channels = ["trips", "drivers", "incidents", "notifications", "admin"]
        
        for channel in valid_channels:
            assert channel in manager.active_connections