import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestMinistryServiceEnums:

    def test_ministry_service_import(self):
        from backend.services.ministry_service import MinistryService

        assert MinistryService is not None

    def test_ministry_service_has_send_transport_report(self):
        from backend.services.ministry_service import MinistryService

        assert hasattr(MinistryService, "send_transport_report")

    def test_ministry_service_has_send_interior_report(self):
        from backend.services.ministry_service import MinistryService

        assert hasattr(MinistryService, "send_interior_report")


class TestMinistryServiceTransport:

    @pytest.mark.asyncio
    async def test_send_transport_report_no_config(self):
        from backend.services.ministry_service import ministry_service

        with patch("backend.services.ministry_service.settings") as mock_settings:
            mock_settings.ministry_transport_webhook = None

            result = await ministry_service.send_transport_report({"data": "test"})

            assert result is False

    @pytest.mark.asyncio
    async def test_send_transport_report_success(self):
        from backend.services.ministry_service import MinistryService

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        service = MinistryService()

        with patch("backend.services.ministry_service.settings") as mock_settings:
            mock_settings.ministry_transport_webhook = "https://transport.gov.ga/api"
            mock_settings.ministry_api_key = "test-key"

            with patch(
                "backend.services.ministry_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await service.send_transport_report({"report": "data"})

                assert result is True

    @pytest.mark.asyncio
    async def test_send_transport_report_timeout(self):
        import httpx
        from backend.services.ministry_service import MinistryService

        service = MinistryService()

        with patch("backend.services.ministry_service.settings") as mock_settings:
            mock_settings.ministry_transport_webhook = "https://transport.gov.ga/api"
            mock_settings.ministry_api_key = "test-key"

            with patch(
                "backend.services.ministry_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(
                    side_effect=httpx.TimeoutException("Timeout")
                )
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await service.send_transport_report({"report": "data"})

                assert result is False

    @pytest.mark.asyncio
    async def test_send_interior_report_no_config(self):
        from backend.services.ministry_service import ministry_service

        with patch("backend.services.ministry_service.settings") as mock_settings:
            mock_settings.ministry_interior_webhook = None

            result = await ministry_service.send_interior_report({"data": "test"})

            assert result is False

    @pytest.mark.asyncio
    async def test_send_interior_report_success(self):
        from backend.services.ministry_service import MinistryService

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        service = MinistryService()

        with patch("backend.services.ministry_service.settings") as mock_settings:
            mock_settings.ministry_interior_webhook = "https://interieur.gov.ga/api"
            mock_settings.ministry_api_key = "test-key"

            with patch(
                "backend.services.ministry_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await service.send_interior_report({"report": "data"})

                assert result is True
