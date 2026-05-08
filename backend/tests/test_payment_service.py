import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestPaymentService:

    @pytest.mark.asyncio
    async def test_initiate_moovmoney_no_config(self):
        from backend.services.payment_service import payment_service

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = None
            mock_settings.moovmoney_api_key = "test-key"

            result = await payment_service.initiate_moovmoney_payment(
                phone="+24101020304", amount=1000, reference="test-ref"
            )

            assert result["status"] == "error"
            assert "non disponible" in result["message"]

    @pytest.mark.asyncio
    async def test_initiate_moovmoney_success(self):
        from backend.services.payment_service import payment_service

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "pending",
            "transaction_id": "tx-123",
        }

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = "https://api.moovmoney.ga"
            mock_settings.moovmoney_api_key = "test-key"

            with patch(
                "backend.services.payment_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await payment_service.initiate_moovmoney_payment(
                    phone="+24101020304", amount=1000, reference="test-ref"
                )

                assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_check_moovmoney_status_no_config(self):
        from backend.services.payment_service import payment_service

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = None

            result = await payment_service.check_moovmoney_status("tx-123")

            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_check_moovmoney_status_success(self):
        from backend.services.payment_service import payment_service

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "amount": 1000}

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = "https://api.moovmoney.ga"
            mock_settings.moovmoney_api_key = "test-key"

            with patch(
                "backend.services.payment_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await payment_service.check_moovmoney_status("tx-123")

                assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_initiate_airtelmoney_no_config(self):
        from backend.services.payment_service import payment_service

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.airtelmoney_api_url = None

            result = await payment_service.initiate_airtelmoney_payment(
                phone="+24101020304", amount=1000, reference="test-ref"
            )

            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_initiate_airtelmoney_success(self):
        from backend.services.payment_service import payment_service

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "transaction_id": "at-456",
        }

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.airtelmoney_api_url = "https://api.airtelmoney.ga"
            mock_settings.airtelmoney_api_key = "test-key"

            with patch(
                "backend.services.payment_service.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await payment_service.initiate_airtelmoney_payment(
                    phone="+24101020304", amount=1000, reference="test-ref"
                )

                assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_payment_record_with_mock_payment(self):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentMethod, Payment

        mock_payment_instance = MagicMock(spec=Payment)
        mock_payment_instance.amount = 1000
        mock_payment_instance.method = PaymentMethod.MOOVMONEY

        with patch(
            "backend.services.payment_service.Payment",
            return_value=mock_payment_instance,
        ):
            mock_db = AsyncMock()
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock(return_value=mock_payment_instance)

            result = await payment_service.create_payment_record(
                db=mock_db,
                trip_id="trip-1",
                client_id="user-1",
                amount=1000,
                method=PaymentMethod.MOOVMONEY,
                phone_number="+24101020304",
            )

            assert result.amount == 1000

    @pytest.mark.asyncio
    async def test_mark_payment_completed(self):
        from backend.services.payment_service import payment_service
        from backend.models.payment import Payment, PaymentStatus

        mock_db = AsyncMock()
        mock_payment = MagicMock(spec=Payment)
        mock_payment.status = PaymentStatus.PENDING
        mock_payment.id = "pay-123"

        mock_db.commit = AsyncMock()

        await payment_service.mark_payment_completed(
            mock_db, mock_payment, "tx-123", "provider-ref"
        )

        assert mock_payment.status == PaymentStatus.COMPLETED
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_payment_failed(self):
        from backend.services.payment_service import payment_service
        from backend.models.payment import Payment, PaymentStatus

        mock_db = AsyncMock()
        mock_payment = MagicMock(spec=Payment)
        mock_payment.status = PaymentStatus.PENDING
        mock_payment.id = "pay-123"

        mock_db.commit = AsyncMock()

        await payment_service.mark_payment_failed(
            mock_db, mock_payment, "Network error"
        )

        assert mock_payment.status == PaymentStatus.FAILED
        assert mock_payment.failure_reason == "Network error"
        mock_db.commit.assert_called_once()
