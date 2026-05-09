# ============================================================
# Tests Schemas - Validation
# Fichier : backend/tests/test_schemas.py
# ============================================================

import pytest
from pydantic import ValidationError

# ============================================================
# Test Auth Schemas
# ============================================================
class TestAuthSchemas:
    """Tests pour les schémas d'authentification."""
    
    def test_user_login_valid(self):
        from backend.schemas.auth import UserLogin
        login = UserLogin(phone="+24106000000", password="password123")
        assert login.phone == "+24106000000"
        assert login.password == "password123"
    
    def test_user_login_invalid_phone(self):
        from backend.schemas.auth import UserLogin
        with pytest.raises(ValidationError):
            UserLogin(phone="invalid", password="password123")
    
    def test_user_register_valid(self):
        from backend.schemas.auth import UserRegister
        register = UserRegister(
            phone="+24106000000",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        assert register.phone == "+24106000000"
    
    def test_token_response(self):
        from backend.schemas.auth import TokenResponse
        token = TokenResponse(
            access_token="token123",
            refresh_token="refresh123",
            expires_in=3600
        )
        assert token.access_token == "token123"
        assert token.expires_in == 3600


# ============================================================
# Test User Schemas
# ============================================================
class TestUserSchemas:
    def test_user_response(self):
        from backend.schemas.user import UserResponse
        user = UserResponse(
            id="user123",
            phone="+24106000000",
            role="client",
            status="active"
        )
        assert user.id == "user123"
        assert user.role == "client"
    
    def test_user_update_valid(self):
        from backend.schemas.user import UserUpdate
        update = UserUpdate(first_name="John", last_name="Doe")
        assert update.first_name == "John"
        assert update.last_name == "Doe"


# ============================================================
# Test Trip Schemas
# ============================================================
class TestTripSchemas:
    def test_trip_create_valid(self):
        from backend.schemas.trip import TripCreate
        trip = TripCreate(
            pickup_location="Libreville",
            dropoff_location="Owendo",
            amount=1500,
            seats_count=2
        )
        assert trip.pickup_location == "Libreville"
        assert trip.amount == 1500
    
    def test_trip_response(self):
        from backend.schemas.trip import TripResponse
        trip = TripResponse(
            id="trip123",
            pickup_location="Libreville",
            dropoff_location="Owendo",
            amount=1500,
            status="pending"
        )
        assert trip.id == "trip123"
        assert trip.status == "pending"


# ============================================================
# Test Payment Schemas
# ============================================================
class TestPaymentSchemas:
    def test_payment_create_valid(self):
        from backend.schemas.payment import PaymentCreate
        payment = PaymentCreate(
            trip_id="trip123",
            method="moovmoney",
            phone_number="+24106000000"
        )
        assert payment.trip_id == "trip123"
        assert payment.method == "moovmoney"
    
    def test_payment_webhook_valid(self):
        from backend.schemas.payment import PaymentWebhook
        webhook = PaymentWebhook(
            transaction_id="txn123",
            status="success",
            amount=1500
        )
        assert webhook.transaction_id == "txn123"
        assert webhook.status == "success"


# ============================================================
# Test Driver Schemas
# ============================================================
class TestDriverSchemas:
    def test_driver_create_valid(self):
        from backend.schemas.driver import DriverCreate
        driver = DriverCreate(
            phone="+24107000000",
            name="John Doe",
            vehicle_plate="TA-001-GA"
        )
        assert driver.phone == "+24107000000"
        assert driver.vehicle_plate == "TA-001-GA"


# ============================================================
# Test Analytics Schemas
# ============================================================
class TestAnalyticsSchemas:
    def test_kpi_response(self):
        from backend.schemas.analytics import KPIResponse
        kpi = KPIResponse(
            trips_today=100,
            revenue_today=150000,
            active_drivers=50
        )
        assert kpi.trips_today == 100
        assert kpi.active_drivers == 50
    
    def test_daily_stats(self):
        from backend.schemas.analytics import DailyStats
        stats = DailyStats(
            date="2026-05-09",
            trips_count=100,
            revenue=150000
        )
        assert stats.date == "2026-05-09"
        assert stats.trips_count == 100


# ============================================================
# Test Incident Schemas
# ============================================================
class TestIncidentSchemas:
    def test_incident_create_valid(self):
        from backend.schemas.incident import IncidentCreate
        incident = IncidentCreate(
            trip_id="trip123",
            incident_type="sos",
            description="Emergency"
        )
        assert incident.incident_type == "sos"
    
    def test_incident_response(self):
        from backend.schemas.incident import IncidentResponse
        incident = IncidentResponse(
            id="inc123",
            trip_id="trip123",
            incident_type="sos",
            status="open"
        )
        assert incident.id == "inc123"


# ============================================================
# Test Validation - Phone Numbers
# ============================================================
class TestValidation:
    def test_phone_validation_valid(self):
        from backend.schemas.auth import UserLogin
        login = UserLogin(phone="+24106000000", password="test")
        assert login.phone is not None
    
    def test_phone_validation_gabon_format(self):
        from backend.schemas.auth import UserRegister
        # Test with various Gabon formats
        user = UserRegister(
            phone="+24161234567",
            password="password123"
        )
        assert user.phone.startswith("+241")
    
    def test_password_min_length(self):
        from backend.schemas.auth import UserRegister
        with pytest.raises(ValidationError):
            UserRegister(phone="+24106000000", password="123")