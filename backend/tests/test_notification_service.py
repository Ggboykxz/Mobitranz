import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import json


class TestNotificationService:

    def test_notification_service_init_no_config(self):
        with patch("backend.services.notification_service.settings") as mock_settings:
            mock_settings.firebase_credentials_path = None

            from backend.services.notification_service import NotificationService

            service = NotificationService()

            assert service._initialized is False

    def test_notification_service_init_with_file(self):
        mock_creds = {"project_id": "test-project", "api_key": "test-key"}

        with patch("backend.services.notification_service.settings") as mock_settings:
            mock_settings.firebase_credentials_path = "/path/to/creds.json"

            with patch("builtins.open", mock_open(read_data=json.dumps(mock_creds))):
                from backend.services.notification_service import NotificationService

                service = NotificationService()

                assert service._initialized is True
                assert service._project_id == "test-project"

    def test_notification_service_init_file_not_found(self):
        with patch("backend.services.notification_service.settings") as mock_settings:
            mock_settings.firebase_credentials_path = "/nonexistent/path.json"

            from backend.services.notification_service import NotificationService

            service = NotificationService()

            assert service._initialized is False

    @pytest.mark.asyncio
    async def test_send_notification_not_initialized(self):
        from backend.services.notification_service import NotificationService

        service = NotificationService()
        service._initialized = False

        result = await service.send_notification(
            token="test-token", title="Test", body="Test body"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_success(self):
        from backend.services.notification_service import NotificationService

        service = NotificationService()
        service._initialized = True
        service._project_id = "test-project"
        service._fcm_api_key = "test-key"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "message-id"}

        with patch(
            "backend.services.notification_service.httpx.AsyncClient"
        ) as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_instance

            result = await service.send_notification(
                token="test-token", title="Test", body="Test body"
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_send_notification_failure(self):
        from backend.services.notification_service import NotificationService

        service = NotificationService()
        service._initialized = True
        service._project_id = "test-project"
        service._fcm_api_key = "test-key"

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch(
            "backend.services.notification_service.httpx.AsyncClient"
        ) as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_instance

            result = await service.send_notification(
                token="test-token", title="Test", body="Test body"
            )

            assert result is False

    def test_notification_service_has_all_methods(self):
        from backend.services.notification_service import NotificationService

        service = NotificationService()

        assert hasattr(service, "send_notification")
        assert hasattr(service, "send_proposal_notification")
        assert hasattr(service, "send_trip_started_notification")
        assert hasattr(service, "send_payment_notification")
        assert hasattr(service, "send_sos_notification")
