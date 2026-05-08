# ============================================================
# Tests Trips Service
# Fichier : backend/tests/test_trips.py
# ============================================================

import pytest
from datetime import datetime


class TestTripsFeature:
    """Tests fonctionnels pour les trips."""

    def test_trip_status_enum(self):
        """Test que les statuts de trip sont définis."""
        from backend.models.trip import TripStatus

        assert TripStatus.PROPOSING is not None
        assert TripStatus.HORN_PENDING is not None
        assert TripStatus.PAYMENT_PENDING is not None
        assert TripStatus.ACTIVE is not None
        assert TripStatus.COMPLETED is not None
        assert TripStatus.CANCELLED is not None

    def test_trip_status_values(self):
        """Test les valeurs des statuts."""
        from backend.models.trip import TripStatus

        assert TripStatus.PROPOSING.value == "proposing"
        assert TripStatus.COMPLETED.value == "completed"

    def test_payment_status_enum(self):
        """Test les statuts de paiement."""
        from backend.models.payment import PaymentStatus, PaymentMethod

        assert PaymentStatus.PENDING is not None
        assert PaymentStatus.PROCESSING is not None
        assert PaymentStatus.COMPLETED is not None
        assert PaymentStatus.FAILED is not None

        assert PaymentMethod.MOOVMONEY is not None
        assert PaymentMethod.AIRTELMONEY is not None
        assert PaymentMethod.CARD is not None

    def test_driver_status_enum(self):
        """Test les statuts de conducteur."""
        from backend.models.driver import DriverStatus

        assert DriverStatus.PENDING is not None
        assert DriverStatus.VALIDATED is not None
        assert DriverStatus.SUSPENDED is not None
        assert DriverStatus.INACTIVE is not None

    def test_vehicle_status_enum(self):
        """Test les statuts de véhicule."""
        from backend.models.vehicle import VehicleStatus

        assert VehicleStatus.PENDING is not None
        assert VehicleStatus.ACTIVE is not None
        assert VehicleStatus.MAINTENANCE is not None
        assert VehicleStatus.INACTIVE is not None

    def test_incident_status_enum(self):
        """Test les statuts d'incident."""
        from backend.models.incident import IncidentStatus

        assert IncidentStatus.PENDING is not None
        assert IncidentStatus.ACKNOWLEDGED is not None
        assert IncidentStatus.ESCALATED is not None
        assert IncidentStatus.RESOLVED is not None
        assert IncidentStatus.CLOSED is not None

    def test_incident_type_enum(self):
        """Test les types d'incident."""
        from backend.models.incident import IncidentType

        assert IncidentType.SOS is not None
        assert IncidentType.ACCIDENT is not None
        assert IncidentType.DISPUTE is not None
        assert IncidentType.THEFT is not None
        assert IncidentType.HARASSMENT is not None
        assert IncidentType.OTHER is not None
