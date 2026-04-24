# ============================================================
# Tests Payment Service
# Fichier : backend/tests/test_payments.py
# ============================================================

import pytest


class TestPaymentModel:
    """Tests pour le modèle Payment."""
    
    def test_payment_status_enum(self):
        """Test les statuts de paiement."""
        from backend.models.payment import PaymentStatus
        assert PaymentStatus.PENDING is not None
        assert PaymentStatus.PROCESSING is not None
        assert PaymentStatus.COMPLETED is not None
        assert PaymentStatus.FAILED is not None
    
    def test_payment_status_values(self):
        """Test les valeurs de status."""
        from backend.models.payment import PaymentStatus
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"
    
    def test_payment_method_enum(self):
        """Test les méthodes de paiement."""
        from backend.models.payment import PaymentMethod
        assert PaymentMethod.MOOVMONEY is not None
        assert PaymentMethod.AIRTELMONEY is not None
        assert PaymentMethod.CARD is not None
    
    def test_payment_method_values(self):
        """Test les valeurs de méthode."""
        from backend.models.payment import PaymentMethod
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
        assert PaymentMethod.AIRTELMONEY.value == "airtelmoney"
        assert PaymentMethod.CARD.value == "card"
        assert PaymentMethod.BIOMETRIC.value == "biometric"
        assert PaymentMethod.CASH.value == "cash"


class TestPaymentService:
    """Tests pour le service de paiement."""
    
    def test_payment_service_import(self):
        """Test que le service peut être importé."""
        from backend.services.payment_service import payment_service
        assert payment_service is not None
    
    def test_payment_service_attributes(self):
        """Test les attributs du service."""
        from backend.services.payment_service import PaymentService
        assert hasattr(PaymentService, 'initiate_moovmoney_payment')
        assert hasattr(PaymentService, 'check_moovmoney_status')
        assert hasattr(PaymentService, 'initiate_airtelmoney_payment')
        assert hasattr(PaymentService, 'create_payment_record')
        assert hasattr(PaymentService, 'mark_payment_completed')
        assert hasattr(PaymentService, 'mark_payment_failed')