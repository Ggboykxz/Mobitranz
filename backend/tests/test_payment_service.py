from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPaymentRecord:
    async def test_create_payment_record(self, mock_db_session):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentMethod

        mock_payment = MagicMock()
        mock_payment.amount = 2500
        mock_payment.method = PaymentMethod.MOOVMONEY
        mock_payment.currency = "XAF"

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        with patch(
            "backend.services.payment_service.Payment", return_value=mock_payment
        ):
            result = await payment_service.create_payment_record(
                db=mock_db_session,
                trip_id="trip-1",
                client_id="client-1",
                amount=2500,
                method=PaymentMethod.MOOVMONEY,
                phone_number="+24106000001",
            )
            assert result.amount == 2500
            assert result.method == PaymentMethod.MOOVMONEY
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_awaited_once()

    async def test_create_payment_record_with_airtel(self, mock_db_session):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentMethod

        mock_payment = MagicMock()
        mock_payment.method = PaymentMethod.AIRTELMONEY

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        with patch(
            "backend.services.payment_service.Payment", return_value=mock_payment
        ):
            result = await payment_service.create_payment_record(
                db=mock_db_session,
                trip_id="trip-2",
                client_id="client-2",
                amount=3500,
                method=PaymentMethod.AIRTELMONEY,
                phone_number="+24106000002",
            )
            assert result.method == PaymentMethod.AIRTELMONEY

    async def test_mark_payment_completed(self, mock_db_session):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentStatus

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PENDING

        await payment_service.mark_payment_completed(
            mock_db_session, mock_payment, "ext-tx-123", "provider-ref-abc"
        )

        assert mock_payment.status == PaymentStatus.COMPLETED
        assert mock_payment.external_transaction_id == "ext-tx-123"
        assert mock_payment.provider_reference == "provider-ref-abc"
        assert mock_payment.completed_at is not None
        mock_db_session.commit.assert_awaited_once()

    async def test_mark_payment_failed(self, mock_db_session):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentStatus

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PENDING

        await payment_service.mark_payment_failed(
            mock_db_session, mock_payment, "Fonds insuffisants"
        )

        assert mock_payment.status == PaymentStatus.FAILED
        assert mock_payment.failure_reason == "Fonds insuffisants"
        mock_db_session.commit.assert_awaited_once()

    async def test_mark_completed_from_processing(self, mock_db_session):
        from backend.services.payment_service import payment_service
        from backend.models.payment import PaymentStatus

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PROCESSING

        await payment_service.mark_payment_completed(
            mock_db_session, mock_payment, "ext-tx-456"
        )
        assert mock_payment.status == PaymentStatus.COMPLETED


class TestPaymentProviders:
    async def test_initiate_moovmoney_submits_task(self):
        from backend.services.payment_service import payment_service

        mock_task = MagicMock()
        mock_task.id = "celery-task-1"

        with patch(
            "backend.services.payment_service.initiate_moovmoney_payment_task"
        ) as mock_task_cls:
            mock_task_cls.delay.return_value = mock_task

            result = await payment_service.initiate_moovmoney_payment(
                phone="+24101020304", amount=1000, reference="ref-1"
            )

            assert result["status"] == "submitted"
            assert result["task_id"] == "celery-task-1"
            mock_task_cls.delay.assert_called_once_with(
                "+24101020304", 1000, "ref-1"
            )

    async def test_initiate_airtelmoney_submits_task(self):
        from backend.services.payment_service import payment_service

        mock_task = MagicMock()
        mock_task.id = "celery-task-2"

        with patch(
            "backend.services.payment_service.initiate_airtelmoney_payment_task"
        ) as mock_task_cls:
            mock_task_cls.delay.return_value = mock_task

            result = await payment_service.initiate_airtelmoney_payment(
                phone="+24101020304", amount=1000, reference="ref-2"
            )

            assert result["status"] == "submitted"
            assert result["task_id"] == "celery-task-2"

    async def test_check_moovmoney_status_no_config(self):
        from backend.services.payment_service import payment_service

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = None
            result = await payment_service.check_moovmoney_status("tx-123")
            assert result["status"] == "error"

    async def test_check_moovmoney_status_http_error(self):
        from backend.services.payment_service import payment_service

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = "https://api.moovmoney.ga"
            mock_settings.moovmoney_api_key = "test-key"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(side_effect=Exception("Network error"))
                mock_client_cls.return_value.__aenter__.return_value = mock_instance

                result = await payment_service.check_moovmoney_status("tx-123")
                assert result["status"] == "error"

    async def test_check_moovmoney_status_success(self):
        from backend.services.payment_service import payment_service

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "amount": 1000}

        with patch("backend.services.payment_service.settings") as mock_settings:
            mock_settings.moovmoney_api_url = "https://api.moovmoney.ga"
            mock_settings.moovmoney_api_key = "test-key"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_client_cls.return_value.__aenter__.return_value = mock_instance

                result = await payment_service.check_moovmoney_status("tx-123")
                assert result["status"] == "success"


class TestPaymentPersistence:
    async def test_payment_enums(self):
        from backend.models.payment import PaymentStatus, PaymentMethod

        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"
        assert PaymentMethod.MOOVMONEY.value == "moovmoney"
        assert PaymentMethod.AIRTELMONEY.value == "airtelmoney"
        assert PaymentMethod.CASH.value == "cash"
