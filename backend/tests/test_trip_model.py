# ============================================================
# Tests Trip Model
# Fichier : backend/tests/test_trip_model.py
# ============================================================

import pytest
from backend.models.trip import Trip, TripStatus
from backend.models.payment import Payment, PaymentStatus, PaymentMethod
from backend.models.driver import Driver, DriverStatus


class TestTripModel:
    """Tests pour le modèle Trip."""

    def test_trip_creation(self):
        """Test création trajet."""
        trip = Trip(
            client_ids=["user123"],
            pickup_location="Libreville",
            dropoff_location="Owendo",
            amount=1500
        )
        
        assert trip.client_ids == ["user123"]
        assert trip.pickup_location == "Libreville"
        assert trip.dropoff_location == "Owendo"
        assert trip.amount == 1500

    def test_trip_status(self):
        """Test les statuts de trajet."""
        assert TripStatus.REQUESTED.value == "requested"
        assert TripStatus.HORN_PENDING.value == "horn_pending"
        assert TripStatus.HORN_ACCEPTED.value == "horn_accepted"
        assert TripStatus.PAYMENT_PENDING.value == "payment_pending"
        assert TripStatus.IN_PROGRESS.value == "in_progress"
        assert TripStatus.COMPLETED.value == "completed"
        assert TripStatus.CANCELLED.value == "cancelled"

    def test_trip_default_status(self):
        """Test statut par défaut."""
        trip = Trip(
            client_ids=["user123"],
            pickup_location="Libreville",
            dropoff_location="Owendo",
            amount=1500
        )
        
        assert trip.status == TripStatus.REQUESTED


class TestPaymentModel:
    """Tests pour le modèle Payment."""

    def test_payment_creation(self):
        """Test création paiement."""
        payment = Payment(
            trip_id="trip123",
            client_id="user123",
            amount=1500,
            method=PaymentMethod.MOOVMONEY,
            phone_number="+24106000000"
        )
        
        assert payment.trip_id == "trip123"
        assert payment.amount == 1500
        assert payment.method == PaymentMethod.MOOVMONEY

    def test_payment_status(self):
        """Test les statuts de paiement."""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"

    def test_payment_method(self):
        """Test les méthodes de paiement."""
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
        assert PaymentMethod.AIRTELMONEY.value == "airtelmoney"


class TestDriverModel:
    """Tests pour le modèle Driver."""

    def test_driver_creation(self):
        """Test création chauffeur."""
        driver = Driver(
            phone="+24107000000",
            name="Jean Dupont",
            vehicle_plate="TA-001-GA"
        )
        
        assert driver.phone == "+24107000000"
        assert driver.name == "Jean Dupont"
        assert driver.vehicle_plate == "TA-001-GA"

    def test_driver_status(self):
        """Test les statuts de chauffeur."""
        assert DriverStatus.PENDING.value == "pending"
        assert DriverStatus.VALIDATED.value == "validated"
        assert DriverStatus.ACTIVE.value == "active"
        assert DriverStatus.SUSPENDED.value == "suspended"