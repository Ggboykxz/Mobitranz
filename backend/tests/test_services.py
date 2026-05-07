# ============================================================
# Tests Services MobiTranz
# Fichier : backend/tests/test_services.py
# ============================================================

import pytest


class TestPaymentService:
    """Tests pour le service de paiement."""
    
    def test_payment_service_import(self):
        """Test import du service."""
        from backend.services.payment_service import PaymentService
        assert PaymentService is not None


class TestQRService:
    """Tests pour le service QR."""
    
    def test_qr_service_import(self):
        """Test import du service."""
        from backend.services.qr_service import QRService
        assert QRService is not None


class TestGeoService:
    """Tests pour le service géolocaliation."""
    
    def test_geo_service_import(self):
        """Test import du service."""
        from backend.services.geo_service import GeoService
        assert GeoService is not None


class TestMatchingService:
    """Tests pour le service de matching."""
    
    def test_matching_service_import(self):
        """Test import du service."""
        from backend.services.matching_service import MatchingService
        assert MatchingService is not None


class TestAuditService:
    """Tests pour le service d'audit."""
    
    def test_audit_service_import(self):
        """Test import du service."""
        from backend.services.audit_service import AuditService
        assert AuditService is not None


class TestMinistryService:
    """Tests pour le service ministère."""
    
    def test_ministry_service_import(self):
        """Test import du service."""
        from backend.services.ministry_service import MinistryService
        assert MinistryService is not None


class TestWalletService:
    """Tests pour le service wallet."""
    
    def test_wallet_service_import(self):
        """Test import du service."""
        from backend.services.wallet_service import WalletService
        assert WalletService is not None


class TestVoiceService:
    """Tests pour le service vocal."""
    
    def test_voice_service_import(self):
        """Test import du service."""
        from backend.services.voice_service import VoiceProposalService
        assert VoiceProposalService is not None


class TestHornDetection:
    """Tests pour le service détection klaxon."""
    
    def test_horn_detection_import(self):
        """Test import du service."""
        from backend.services.horn_detection import HornDetectionService
        assert HornDetectionService is not None


class TestEncryptionService:
    """Tests pour le service chiffrement."""
    
    def test_encryption_service_import(self):
        """Test import du service."""
        from backend.services.encryption_service import EncryptionService
        assert EncryptionService is not None


class TestNotificationService:
    """Tests pour le service notification."""
    
    def test_notification_service_import(self):
        """Test import du service."""
        from backend.services.notification_service import NotificationService
        assert NotificationService is not None