# ============================================================
# Tests Middleware et Utilities
# Fichier : backend/tests/test_middleware_utils.py
# ============================================================

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ============================================================
# Test Middleware Security Headers
# ============================================================
class TestSecurityHeadersMiddleware:
    def test_middleware_import(self):
        from backend.middleware.security import SecurityHeadersMiddleware
        assert SecurityHeadersMiddleware is not None
    
    def test_middleware_class_exists(self):
        from backend.middleware.security import SecurityHeadersMiddleware
        assert hasattr(SecurityHeadersMiddleware, 'dispatch')


# ============================================================
# Test Rate Limit Middleware
# ============================================================
class TestRateLimitMiddleware:
    def test_middleware_import(self):
        from backend.middleware.security import RateLimitMiddleware
        assert RateLimitMiddleware is not None
    
    def test_rate_limit_init(self):
        from backend.middleware.security import RateLimitMiddleware
        mock_app = MagicMock()
        middleware = RateLimitMiddleware(mock_app, requests_per_minute=60)
        assert middleware.requests_per_minute == 60
        assert middleware.request_counts == {}
    
    def test_rate_limit_get_client_ip(self):
        from backend.middleware.security import RateLimitMiddleware
        mock_app = MagicMock()
        middleware = RateLimitMiddleware(mock_app)
        
        # Test without X-Forwarded-For
        mock_request = MagicMock()
        mock_request.client.host = "192.168.1.1"
        mock_request.headers.get.return_value = None
        
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.1"
    
    def test_rate_limit_get_client_ip_with_forwarded(self):
        from backend.middleware.security import RateLimitMiddleware
        mock_app = MagicMock()
        middleware = RateLimitMiddleware(mock_app)
        
        # Test with X-Forwarded-For
        mock_request = MagicMock()
        mock_request.client.host = "192.168.1.1"
        mock_request.headers.get.return_value = "10.0.0.1, 192.168.1.1"
        
        ip = middleware._get_client_ip(mock_request)
        assert ip == "10.0.0.1"


# ============================================================
# Test Redis Client
# ============================================================
class TestRedisClient:
    def test_redis_client_import(self):
        from backend.redis_client import RedisClient
        assert RedisClient is not None
    
    def test_redis_client_init(self):
        from backend.redis_client import RedisClient
        client = RedisClient()
        assert client.redis is None
    
    def test_redis_client_methods(self):
        from backend.redis_client import RedisClient
        client = RedisClient()
        # Check methods exist
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'get_client')


# ============================================================
# Test Database
# ============================================================
class TestDatabase:
    def test_database_import(self):
        from backend.database import get_db
        assert get_db is not None
    
    def test_base_import(self):
        from backend.database import Base
        assert Base is not None


# ============================================================
# Test WebSocket Manager
# ============================================================
class TestWebSocket:
    def test_websocket_manager_import(self):
        from backend.websocket import ConnectionManager
        assert ConnectionManager is not None
    
    def test_connection_manager_init(self):
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        assert manager.active_connections is not None
        assert 'trips' in manager.active_connections
        assert 'drivers' in manager.active_connections
        assert 'notifications' in manager.active_connections
    
    def test_connection_manager_user_connections(self):
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        assert manager.user_connections == {}
    
    def test_connection_manager_rooms(self):
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        assert manager.rooms == {}


# ============================================================
# Test Logger
# ============================================================
class TestLogger:
    def test_logger_import(self):
        import structlog
        assert structlog is not None
    
    def test_logger_configuration(self):
        import structlog
        logger = structlog.get_logger()
        assert logger is not None


# ============================================================
# Test Config Imports
# ============================================================
class TestConfigImports:
    def test_settings_import(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings is not None
    
    def test_settings_singleton(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings as s1
            from backend.config import settings as s2
            # Same instance
            assert s1 is s2


# ============================================================
# Test All Router Imports
# ============================================================
class TestRouterImports:
    def test_auth_router(self):
        from backend.routers import auth
        assert auth is not None
    
    def test_trips_router(self):
        from backend.routers import trips
        assert trips is not None
    
    def test_payments_router(self):
        from backend.routers import payments
        assert payments is not None
    
    def test_drivers_router(self):
        from backend.routers import drivers
        assert drivers is not None
    
    def test_vehicles_router(self):
        from backend.routers import vehicles
        assert vehicles is not None
    
    def test_voice_router(self):
        from backend.routers import voice
        assert voice is not None
    
    def test_incidents_router(self):
        from backend.routers import incidents
        assert incidents is not None
    
    def test_analytics_router(self):
        from backend.routers import analytics
        assert analytics is not None
    
    def test_users_router(self):
        from backend.routers import users
        assert users is not None
    
    def test_admin_router(self):
        from backend.routers import admin
        assert admin is not None


# ============================================================
# Test All Service Imports
# ============================================================
class TestServiceImports:
    def test_auth_service_import(self):
        from backend.services import auth_service
        assert auth_service is not None
    
    def test_payment_service_import(self):
        from backend.services import payment_service
        assert payment_service is not None
    
    def test_matching_service_import(self):
        from backend.services import matching_service
        assert matching_service is not None
    
    def test_wallet_service_import(self):
        from backend.services import wallet_service
        assert wallet_service is not None
    
    def test_notification_service_import(self):
        from backend.services import notification_service
        assert notification_service is not None
    
    def test_geo_service_import(self):
        from backend.services import geo_service
        assert geo_service is not None
    
    def test_audit_service_import(self):
        from backend.services import audit_service
        assert audit_service is not None
    
    def test_ministry_service_import(self):
        from backend.services import ministry_service
        assert ministry_service is not None


# ============================================================
# Test All Model Imports
# ============================================================
class TestModelImports:
    def test_user_model(self):
        from backend.models import user
        assert user is not None
    
    def test_trip_model(self):
        from backend.models import trip
        assert trip is not None
    
    def test_payment_model(self):
        from backend.models import payment
        assert payment is not None
    
    def test_driver_model(self):
        from backend.models import driver
        assert driver is not None
    
    def test_vehicle_model(self):
        from backend.models import vehicle
        assert vehicle is not None
    
    def test_incident_model(self):
        from backend.models import incident
        assert incident is not None
    
    def test_recording_model(self):
        from backend.models import recording
        assert recording is not None
    
    def test_audit_log_model(self):
        from backend.models import audit_log
        assert audit_log is not None
    
    def test_notification_model(self):
        from backend.models import notification
        assert notification is not None
    
    def test_zone_model(self):
        from backend.models import zone
        assert zone is not None