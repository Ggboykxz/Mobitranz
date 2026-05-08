import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestWalletModelsDirectly:

    def test_wallet_status_enum_import(self):
        import backend.services.wallet_service as ws_module

        assert hasattr(ws_module, "WalletStatus")

    def test_wallet_operation_type_enum_import(self):
        import backend.services.wallet_service as ws_module

        assert hasattr(ws_module, "WalletOperationType")

    def test_wallet_service_class_methods(self):
        from backend.services.wallet_service import WalletService

        service = WalletService()

        methods = [m for m in dir(service) if not m.startswith("_")]
        assert "create_wallet" in methods
        assert "get_wallet" in methods
        assert "deposit" in methods
        assert "withdraw" in methods
        assert "freeze_funds" in methods
        assert "release_funds" in methods
        assert "get_operations" in methods

    def test_wallet_status_values(self):
        from backend.services.wallet_service import WalletStatus

        assert WalletStatus.ACTIVE.value == "active"
        assert WalletStatus.FROZEN.value == "frozen"
        assert WalletStatus.SUSPENDED.value == "suspended"

    def test_wallet_operation_type_values(self):
        from backend.services.wallet_service import WalletOperationType

        ops = [o.value for o in WalletOperationType]
        assert "deposit" in ops
        assert "withdrawal" in ops
        assert "payment" in ops
        assert "refund" in ops
        assert "bonus" in ops
        assert "fee" in ops


class TestRedisClientMethods:

    def test_redis_client_class_methods(self):
        from backend.redis_client import RedisClient

        client = RedisClient()

        methods = [
            m
            for m in dir(client)
            if not m.startswith("_") and callable(getattr(client, m))
        ]
        assert "connect" in methods
        assert "disconnect" in methods
        assert "get_client" in methods
        assert "set_session" in methods
        assert "get_session" in methods
        assert "delete_session" in methods
        assert "set_cache" in methods
        assert "get_cache" in methods
        assert "get_cache" in methods
        assert "publish_event" in methods

    def test_redis_client_init_state(self):
        from backend.redis_client import RedisClient

        client = RedisClient()
        assert client._redis is None

    @pytest.mark.asyncio
    async def test_redis_get_client_raises_when_not_connected(self):
        from backend.redis_client import RedisClient

        client = RedisClient()

        with pytest.raises(RuntimeError) as exc_info:
            await client.get_client()

        assert "non connecté" in str(exc_info.value)


class TestQRServiceMethods:

    def test_qr_service_class_methods(self):
        from backend.services.qr_service import QRService

        service = QRService()

        assert hasattr(service, "generate_qr_signature")
        assert hasattr(service, "verify_qr_signature")
        assert hasattr(service, "generate_qr_code")
        assert hasattr(service, "verify_and_use_qr")

    def test_qr_service_constants(self):
        from backend.services.qr_service import QRService

        assert QRService.QR_EXPIRY_SECONDS == 300


class TestMatchingServiceMethods:

    def test_matching_service_class_methods(self):
        from backend.services.matching_service import MatchingService

        service = MatchingService()

        assert hasattr(service, "find_available_taxis")
        assert hasattr(service, "calculate_estimated_fare")
        assert hasattr(service, "create_proposal")
        assert hasattr(service, "get_matching_score")


class TestGeoServiceMethods:

    def test_geo_service_class_methods(self):
        from backend.services.geo_service import GeoService

        assert hasattr(GeoService, "calculate_distance")
        assert hasattr(GeoService, "calculate_eta")
        assert hasattr(GeoService, "is_within_radius")
        assert hasattr(GeoService, "detect_zone")
        assert hasattr(GeoService, "find_nearby_drivers")
        assert hasattr(GeoService, "calculate_trip_fare")
        assert hasattr(GeoService, "detect_route_deviation")

    def test_geo_service_constants(self):
        from backend.services.geo_service import GeoService

        assert GeoService.EARTH_RADIUS_KM == 6371.0


class TestMinistryServiceMethods:

    def test_ministry_service_class_methods(self):
        from backend.services.ministry_service import MinistryService

        service = MinistryService()

        assert hasattr(service, "send_transport_report")
        assert hasattr(service, "send_interior_report")
        assert hasattr(service, "send_sos_alert")
        assert hasattr(service, "generate_monthly_transport_report")
        assert hasattr(service, "generate_security_report")
        assert hasattr(service, "get_vehicle_registry")


class TestNotificationServiceMethods:

    def test_notification_service_class_methods(self):
        from backend.services.notification_service import NotificationService

        service = NotificationService()

        assert hasattr(service, "send_notification")
        assert hasattr(service, "send_proposal_notification")
        assert hasattr(service, "send_trip_started_notification")
        assert hasattr(service, "send_payment_notification")
        assert hasattr(service, "send_sos_notification")
        assert hasattr(service, "_initialize")


class TestEncryptionServiceMethods:

    def test_encryption_service_class_methods(self):
        from backend.services.encryption_service import EncryptionService

        service = EncryptionService()

        assert hasattr(service, "generate_aes_key")
        assert hasattr(service, "generate_nonce")
        assert hasattr(service, "encrypt_aesgcm")
        assert hasattr(service, "decrypt_aesgcm")
        assert hasattr(service, "hash_sha256")

    def test_encryption_service_constants(self):
        from backend.services.encryption_service import EncryptionService

        assert EncryptionService.AES_KEY_SIZE == 32
        assert EncryptionService.NONCE_SIZE == 12
