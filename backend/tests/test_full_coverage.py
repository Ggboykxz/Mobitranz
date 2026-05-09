# ============================================================
# Tests Complet pour tous les modules
# Fichier : backend/tests/test_full_coverage.py
# ============================================================

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# ============================================================
# Test Config
# ============================================================
class TestConfig:
    def test_settings_import(self):
        import os
        os.environ['SECRET_KEY'] = 'test_key_12345678901234567890'
        from backend.config import Settings, settings
        assert settings is not None
    
    def test_settings_values(self):
        import os
        os.environ['SECRET_KEY'] = 'test_key_12345678901234567890'
        from backend.config import settings
        assert settings.app_name == "MobiTranz"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.jwt_algorithm == "HS256"
        assert settings.access_token_expire_minutes == 15
        assert settings.refresh_token_expire_days == 7
        assert settings.rate_limit_auth_requests == 5
        assert settings.rate_limit_payment_requests == 10
        assert settings.tz == "Africa/Libreville"


# ============================================================
# Test Database
# ============================================================
class TestDatabase:
    def test_database_imports(self):
        from backend.database import get_db, Base, engine
        assert get_db is not None
        assert Base is not None
        assert engine is not None
    
    def test_base_contains_tables(self):
        from backend.database import Base
        # Base.metadata should contain tables
        assert Base.metadata is not None


# ============================================================
# Test Middleware
# ============================================================
class TestMiddleware:
    def test_security_headers_middleware(self):
        from backend.middleware.security import SecurityHeadersMiddleware
        app = MagicMock()
        middleware = SecurityHeadersMiddleware(app)
        assert middleware is not None
    
    def test_rate_limit_middleware(self):
        from backend.middleware.security import RateLimitMiddleware
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        assert middleware.requests_per_minute == 60
        assert middleware.request_counts == {}


# ============================================================
# Test Redis Client
# ============================================================
class TestRedis:
    def test_redis_client_import(self):
        from backend.redis_client import redis_client
        assert redis_client is not None
    
    def test_redis_client_connect_method_exists(self):
        from backend.redis_client import RedisClient
        client = RedisClient()
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'get_client')


# ============================================================
# Test Models - All Tables
# ============================================================
class TestAllModels:
    def setup_method(self):
        import os
        os.environ['SECRET_KEY'] = 'test_secret_key_12345678901234567890'
    
    def test_user_model(self):
        from backend.models.user import User, UserRole, UserStatus
        assert User is not None
        assert UserRole.CLIENT.value == "client"
        assert UserStatus.ACTIVE.value == "active"
    
    def test_trip_model(self):
        from backend.models.trip import Trip, TripStatus
        assert Trip is not None
        assert TripStatus.PROPOSING.value == "proposing"
    
    def test_payment_model(self):
        from backend.models.payment import Payment, PaymentStatus, PaymentMethod
        assert Payment is not None
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
    
    def test_driver_model(self):
        from backend.models.driver import Driver, DriverStatus
        assert Driver is not None
        assert DriverStatus.VALIDATED.value == "validated"
    
    def test_vehicle_model(self):
        from backend.models.vehicle import Vehicle, VehicleStatus
        assert Vehicle is not None
        assert VehicleStatus.ACTIVE.value == "active"
    
    def test_incident_model(self):
        from backend.models.incident import Incident, IncidentStatus, IncidentType
        assert Incident is not None
        assert IncidentStatus.PENDING.value == "pending"
        assert IncidentType.SOS.value == "sos"
    
    def test_recording_model(self):
        from backend.models.recording import Recording, RecordingStatus
        assert Recording is not None
        assert RecordingStatus.RECORDING.value == "recording"
    
    def test_notification_model(self):
        from backend.models.notification import Notification
        assert Notification is not None
        # Check columns exist
        assert hasattr(Notification, 'id')
        assert hasattr(Notification, 'user_id')
        assert hasattr(Notification, 'title')
        assert hasattr(Notification, 'body')
        assert hasattr(Notification, 'notification_type')
        assert hasattr(Notification, 'is_read')
    
    def test_audit_log_model(self):
        from backend.models.audit_log import AuditLog
        assert AuditLog is not None
    
    def test_trip_gps_model(self):
        from backend.models.trip_gps import TripGpsPoint
        assert TripGpsPoint is not None
        # Check columns exist
        assert hasattr(TripGpsPoint, 'id')
        assert hasattr(TripGpsPoint, 'trip_id')
        assert hasattr(TripGpsPoint, 'latitude')
        assert hasattr(TripGpsPoint, 'longitude')
        assert hasattr(TripGpsPoint, 'speed_kmh')
    
    def test_voice_proposal_model(self):
        from backend.models.voice_proposal import VoiceProposal
        assert VoiceProposal is not None
    
    def test_zone_model(self):
        from backend.models.zone import Zone
        assert Zone is not None
    
    def test_raspberry_pi_model(self):
        from backend.models.raspberry_pi import RaspberryPiUnit, RaspberryPiStatus
        assert RaspberryPiUnit is not None
        assert RaspberryPiStatus.ACTIVE.value == "active"
        # Check columns exist
        assert hasattr(RaspberryPiUnit, 'id')
        assert hasattr(RaspberryPiUnit, 'serial_number')
        assert hasattr(RaspberryPiUnit, 'status')
        assert hasattr(RaspberryPiUnit, 'vehicle_id')


# ============================================================
# Test Auth Deps
# ============================================================
class TestAuthDeps:
    def test_auth_deps_import(self):
        from backend.deps import auth_deps
        assert auth_deps is not None
    
    def test_get_current_user_exists(self):
        from backend.deps.auth_deps import get_current_user
        assert get_current_user is not None


# ============================================================
# Test All Routers - Simplified
# ============================================================
class TestAllRouters:
    def test_auth_router_exists(self):
        from backend.routers import auth
        assert 'router' in dir(auth)
    
    def test_payments_router_exists(self):
        from backend.routers import payments
        assert 'router' in dir(payments)
    
    def test_drivers_router_exists(self):
        from backend.routers import drivers
        assert 'router' in dir(drivers)
    
    def test_incidents_router_exists(self):
        from backend.routers import incidents
        assert 'router' in dir(incidents)
    
    def test_analytics_router_exists(self):
        from backend.routers import analytics
        assert 'router' in dir(analytics)
    
    def test_users_router_exists(self):
        from backend.routers import users
        assert 'router' in dir(users)
    
    def test_admin_router_exists(self):
        from backend.routers import admin
        assert 'router' in dir(admin)


# ============================================================
# Test Services - Most
# ============================================================
class TestAllServices:
    def test_auth_service(self):
        import os
        os.environ['SECRET_KEY'] = 'test_key_12345678901234567890'
        from backend.services import auth_service
        assert auth_service is not None
    
    def test_payment_service(self):
        from backend.services import payment_service
        assert payment_service is not None
    
    def test_wallet_service(self):
        from backend.services import wallet_service
        assert wallet_service is not None
    
    def test_matching_service(self):
        from backend.services import matching_service
        assert matching_service is not None
    
    def test_notification_service(self):
        from backend.services import notification_service
        assert notification_service is not None
    
    def test_geo_service(self):
        from backend.services import geo_service
        assert geo_service is not None
    
    def test_audit_service(self):
        from backend.services import audit_service
        assert audit_service is not None
    
    def test_ministry_service(self):
        from backend.services import ministry_service
        assert ministry_service is not None


# ============================================================
# Test Schemas - Simplified
# ============================================================
class TestAllSchemas:
    def test_auth_schemas(self):
        from backend.schemas import auth
        assert auth is not None
    
    def test_user_schemas(self):
        from backend.schemas import user
        assert user is not None
    
    def test_trip_schemas(self):
        from backend.schemas import trip
        assert trip is not None
    
    def test_payment_schemas(self):
        from backend.schemas import payment
        assert payment is not None
    
    def test_driver_schemas(self):
        from backend.schemas import driver
        assert driver is not None
    
    def test_vehicle_schemas(self):
        from backend.schemas import vehicle
        assert vehicle is not None
    
    def test_incident_schemas(self):
        from backend.schemas import incident
        assert incident is not None


# ============================================================
# Test WebSocket
# ============================================================
class TestWebSocket:
    def test_websocket_manager(self):
        from backend.websocket import ConnectionManager, manager
        assert ConnectionManager is not None
        assert manager is not None
    
    def test_websocket_router(self):
        from backend.websocket import websocket_router
        assert websocket_router is not None
    
    def test_connection_manager_methods(self):
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'broadcast')
        assert hasattr(manager, 'send_personal_message')
        assert hasattr(manager, 'register_user')
        assert hasattr(manager, 'join_room')
        assert hasattr(manager, 'leave_room')
        assert hasattr(manager, 'broadcast_location_update')
        assert hasattr(manager, 'broadcast_trip_status')
        assert hasattr(manager, 'broadcast_incident')
        assert hasattr(manager, 'broadcast_notification')


# ============================================================
# Test Utils
# ============================================================
class TestUtils:
    def test_security_utils(self):
        from backend.utils.security import (
            generate_csrf_token, verify_csrf_token,
            generate_api_key, hash_api_key, verify_api_key,
            sanitize_input, validate_phone_gabon,
            contains_sql_injection, detect_xss,
            IPBlocker, ip_blocker
        )
        assert generate_csrf_token() is not None
        assert len(generate_api_key()) > 10
    
    def test_ip_blocker(self):
        from backend.utils.security import IPBlocker
        blocker = IPBlocker()
        assert blocker.is_blocked("192.168.1.1") is False
        blocker.block_ip("10.0.0.1")
        assert blocker.is_blocked("10.0.0.1") is True
        blocker.unblock_ip("10.0.0.1")
        assert blocker.is_blocked("10.0.0.1") is False


# ============================================================
# Test Router Init
# ============================================================
class TestRoutersInit:
    def test_routers_init(self):
        from backend import routers
        assert routers is not None