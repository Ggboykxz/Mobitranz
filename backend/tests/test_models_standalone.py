# ============================================================
# Tests Modèles - Covering All Enum Values
# Fichier : backend/tests/test_models_standalone.py
# ============================================================

import pytest

# ============================================================
# Test UserRole Enum
# ============================================================
class TestUserRole:
    def test_all_values(self):
        from backend.models.user import UserRole
        assert UserRole.CLIENT.value == "client"
        assert UserRole.DRIVER.value == "driver"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MINISTRY.value == "ministry"


# ============================================================
# Test UserStatus Enum
# ============================================================
class TestUserStatus:
    def test_all_values(self):
        from backend.models.user import UserStatus
        assert UserStatus.PENDING.value == "pending"
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.DELETED.value == "deleted"


# ============================================================
# Test TripStatus Enum
# ============================================================
class TestTripStatus:
    def test_all_values(self):
        from backend.models.trip import TripStatus
        assert TripStatus.PROPOSING.value == "proposing"
        assert TripStatus.HORN_PENDING.value == "horn_pending"
        assert TripStatus.PAYMENT_PENDING.value == "payment_pending"
        assert TripStatus.ACTIVE.value == "active"
        assert TripStatus.COMPLETED.value == "completed"
        assert TripStatus.CANCELLED.value == "cancelled"
        assert TripStatus.INCIDENT.value == "incident"


# ============================================================
# Test PaymentStatus Enum
# ============================================================
class TestPaymentStatus:
    def test_all_values(self):
        from backend.models.payment import PaymentStatus
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"


# ============================================================
# Test PaymentMethod Enum
# ============================================================
class TestPaymentMethod:
    def test_all_values(self):
        from backend.models.payment import PaymentMethod
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
        assert PaymentMethod.AIRTELMONEY.value == "airtelmoney"
        assert PaymentMethod.CARD.value == "card"
        assert PaymentMethod.BIOMETRIC.value == "biometric"
        assert PaymentMethod.CASH.value == "cash"


# ============================================================
# Test DriverStatus Enum
# ============================================================
class TestDriverStatus:
    def test_all_values(self):
        from backend.models.driver import DriverStatus
        assert DriverStatus.PENDING.value == "pending"
        assert DriverStatus.VALIDATED.value == "validated"
        assert DriverStatus.INACTIVE.value == "inactive"
        assert DriverStatus.SUSPENDED.value == "suspended"


# ============================================================
# Test IncidentType Enum
# ============================================================
class TestIncidentType:
    def test_all_values(self):
        from backend.models.incident import IncidentType
        assert IncidentType.SOS.value == "sos"
        assert IncidentType.ACCIDENT.value == "accident"
        assert IncidentType.DISPUTE.value == "dispute"
        assert IncidentType.THEFT.value == "theft"
        assert IncidentType.HARASSMENT.value == "harassment"
        assert IncidentType.OTHER.value == "other"


# ============================================================
# Test IncidentStatus Enum
# ============================================================
class TestIncidentStatus:
    def test_all_values(self):
        from backend.models.incident import IncidentStatus
        assert IncidentStatus.PENDING.value == "pending"
        assert IncidentStatus.ACKNOWLEDGED.value == "acknowledged"
        assert IncidentStatus.ESCALATED.value == "escalated"
        assert IncidentStatus.RESOLVED.value == "resolved"
        assert IncidentStatus.CLOSED.value == "closed"


# ============================================================
# Test VehicleStatus Enum
# ============================================================
class TestVehicleStatus:
    def test_all_values(self):
        from backend.models.vehicle import VehicleStatus
        assert VehicleStatus.PENDING.value == "pending"
        assert VehicleStatus.ACTIVE.value == "active"
        assert VehicleStatus.MAINTENANCE.value == "maintenance"
        assert VehicleStatus.INACTIVE.value == "inactive"


# ============================================================
# Test RecordingStatus Enum
# ============================================================
class TestRecordingStatus:
    def test_all_values(self):
        from backend.models.recording import RecordingStatus
        assert RecordingStatus.RECORDING.value == "recording"
        assert RecordingStatus.PROCESSING.value == "processing"
        assert RecordingStatus.READY.value == "ready"
        assert RecordingStatus.ENCRYPTED.value == "encrypted"
        assert RecordingStatus.DELETED.value == "deleted"


# ============================================================
# Test RaspberryPiStatus Enum
# ============================================================
class TestRaspberryPiStatus:
    def test_all_values(self):
        from backend.models.raspberry_pi import RaspberryPiStatus
        assert RaspberryPiStatus.PENDING.value == "pending"
        assert RaspberryPiStatus.ACTIVE.value == "active"
        assert RaspberryPiStatus.OFFLINE.value == "offline"
        assert RaspberryPiStatus.ERROR.value == "error"
        assert RaspberryPiStatus.MAINTENANCE.value == "maintenance"


# ============================================================
# Test Enum Count Coverage
# ============================================================
class TestEnumCounts:
    def test_user_role_count(self):
        from backend.models.user import UserRole
        assert len(UserRole) == 4
    
    def test_user_status_count(self):
        from backend.models.user import UserStatus
        assert len(UserStatus) == 4
    
    def test_trip_status_count(self):
        from backend.models.trip import TripStatus
        assert len(TripStatus) == 7
    
    def test_payment_status_count(self):
        from backend.models.payment import PaymentStatus
        assert len(PaymentStatus) == 5
    
    def test_payment_method_count(self):
        from backend.models.payment import PaymentMethod
        assert len(PaymentMethod) == 5
    
    def test_driver_status_count(self):
        from backend.models.driver import DriverStatus
        assert len(DriverStatus) == 4
    
    def test_incident_type_count(self):
        from backend.models.incident import IncidentType
        assert len(IncidentType) == 6
    
    def test_incident_status_count(self):
        from backend.models.incident import IncidentStatus
        assert len(IncidentStatus) == 5
    
    def test_vehicle_status_count(self):
        from backend.models.vehicle import VehicleStatus
        assert len(VehicleStatus) == 4
    
    def test_recording_status_count(self):
        from backend.models.recording import RecordingStatus
        assert len(RecordingStatus) == 5
    
    def test_raspberry_pi_status_count(self):
        from backend.models.raspberry_pi import RaspberryPiStatus
        assert len(RaspberryPiStatus) == 5