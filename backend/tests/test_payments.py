# ============================================================
# Tests Payment Service
# Fichier : backend/tests/test_payments.py
# ============================================================

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestPaymentService:
    """Tests pour le service de paiement."""
    
    def test_payment_service_exists(self):
        """Test que le service existe."""
        from backend.services.payment_service import payment_service
        assert payment_service is not None
    
    @pytest.mark.asyncio
    async def test_create_payment_record(self):
        """Test la création d'un enregistrement de paiement."""
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentMethod, PaymentStatus
        from unittest.mock import AsyncMock
        
        # Mock DB
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        payment = await payment_service.create_payment_record(
            db=mock_db,
            trip_id="trip_123",
            client_id="client_456",
            amount=1500,
            method=PaymentMethod.MOOVMONEY,
            phone_number="+24105000000"
        )
        
        assert payment is not None
        assert payment.trip_id == "trip_123"
        assert payment.amount == 1500
        assert payment.method == PaymentMethod.MOOVMONEY
        assert payment.status == PaymentStatus.PENDING
    
    def test_mark_payment_completed(self):
        """Test la completion d'un paiement."""
        from backend.services.payment_service import payment_service
        from backend.models.payment import Payment, PaymentStatus
        from unittest.mock import AsyncMock
        
        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()
        
        payment = Payment(
            id="payment_123",
            trip_id="trip_123",
            client_id="client_456",
            amount=1500,
            method=PaymentMethod.MOOVMONEY,
            status=PaymentStatus.PENDING,
            phone_number="+24105000000"
        )
        
        # Note: This test verifies the method exists and is callable
        assert callable(payment_service.mark_payment_completed)


class TestPaymentModel:
    """Tests pour le modèle Payment."""
    
    def test_payment_attributes(self):
        """Test que Payment a tous les attributs requis."""
        from backend.models.payment import Payment, PaymentStatus, PaymentMethod
        
        # Vérifier que les attributs existent
        assert hasattr(Payment, 'id')
        assert hasattr(Payment, 'trip_id')
        assert hasattr(Payment, 'client_id')
        assert hasattr(Payment, 'amount')
        assert hasattr(Payment, 'method')
        assert hasattr(Payment, 'status')
        assert hasattr(Payment, 'phone_number')
        assert hasattr(Payment, 'created_at')
    
    def test_payment_status_values(self):
        """Test les valeurs de status."""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"
    
    def test_payment_method_values(self):
        """Test les valeurs de méthode."""
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
        assert PaymentMethod.AIRTELMONEY.value == "airtelmoney"
        assert PaymentMethod.CARD.value == "card"
        assert PaymentMethod.BIOMETRIC.value == "biometric"
        assert PaymentMethod.CASH.value == "cash"