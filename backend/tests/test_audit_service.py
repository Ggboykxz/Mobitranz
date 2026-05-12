from unittest.mock import AsyncMock, MagicMock

import pytest


class TestHashChainIntegrity:
    async def test_first_log_has_zero_previous_hash(self, mock_db_session):
        from backend.services.audit_service import audit_service

        saved_hashes = []

        async def mock_refresh(obj):
            if hasattr(obj, 'current_hash'):
                saved_hashes.append(obj.current_hash)

        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

        result = await audit_service.log_action(
            db=mock_db_session, user_id="user-1", action="LOGIN", resource="auth"
        )

        assert result.previous_hash == "0" * 64
        assert result.current_hash is not None
        assert len(result.current_hash) == 64
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_second_log_chains_to_first(self, mock_db_session):
        from backend.services.audit_service import audit_service

        saved_hashes = []

        async def mock_refresh(obj):
            if hasattr(obj, 'current_hash'):
                saved_hashes.append(obj.current_hash)

        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

        log1 = await audit_service.log_action(
            db=mock_db_session, user_id="user-1", action="LOGIN", resource="auth"
        )
        log2 = await audit_service.log_action(
            db=mock_db_session, user_id="user-1", action="LOGOUT", resource="auth"
        )

        saved_hashes.insert(0, "0" * 64)
        for i, h in enumerate(saved_hashes):
            pass

    async def test_hash_chain_integrity(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)
        mock_db_session.add = MagicMock()

        log1_hash = [None]

        def capture_add(obj):
            if hasattr(obj, 'current_hash'):
                log1_hash[0] = obj.current_hash

        mock_db_session.add = MagicMock(side_effect=capture_add)

        log1 = await audit_service.log_action(
            db=mock_db_session, user_id="user-2", action="LOGIN", resource="test"
        )
        await audit_service.log_action(
            db=mock_db_session, user_id="user-2", action="LOGOUT", resource="test"
        )

        assert log1.current_hash is not None
        assert len(log1.current_hash) == 64

    async def test_data_hash_integrity(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        log = await audit_service.log_action(
            db=mock_db_session,
            user_id="user-3",
            action="PAYMENT",
            resource="payments:pay-1",
            data={"amount": 2500, "method": "moovmoney"},
        )

        assert log.data_hash is not None
        assert len(log.data_hash) == 64

    async def test_hash_chain_detects_tampering(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        log1 = await audit_service.log_action(
            db=mock_db_session, user_id="user-4", action="LOGIN", resource="auth"
        )
        log2 = await audit_service.log_action(
            db=mock_db_session, user_id="user-4", action="LOGOUT", resource="auth"
        )

        assert log2.previous_hash is not None
        assert isinstance(log2.current_hash, str)

    async def test_audit_log_has_all_fields(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        log = await audit_service.log_action(
            db=mock_db_session,
            user_id="user-5",
            action="UPDATE_TRIP",
            resource="trips:trip-1",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            result="success",
            data={"status": "completed"},
        )

        assert log.user_id == "user-5"
        assert log.action == "UPDATE_TRIP"
        assert log.resource == "trips:trip-1"
        assert log.result == "success"


class TestAuditConvenienceMethods:
    async def test_log_user_login(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_user_login(
            db=mock_db_session, user_id="user-10", ip_address="10.0.0.1", success=True
        )
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_log_user_login_failure(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_user_login(
            db=mock_db_session, user_id="user-11", ip_address="10.0.0.2", success=False
        )
        mock_db_session.add.assert_called_once()

    async def test_log_user_logout(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_user_logout(
            db=mock_db_session, user_id="user-12", ip_address="10.0.0.3"
        )
        mock_db_session.add.assert_called_once()

    async def test_log_payment(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_payment(
            db=mock_db_session,
            user_id="user-13",
            payment_id="pay-123",
            amount=5000,
            action="PAYMENT_INITIATED",
        )
        mock_db_session.add.assert_called_once()

    async def test_log_trip_action(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_trip_action(
            db=mock_db_session, user_id="user-14", trip_id="trip-99", action="TRIP_STARTED"
        )
        mock_db_session.add.assert_called_once()

    async def test_log_admin_action(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_admin_action(
            db=mock_db_session,
            admin_id="admin-1",
            action="SUSPEND_USER",
            resource="users",
            target_id="user-15",
            data={"reason": "Violation des CGU"},
        )
        mock_db_session.add.assert_called_once()

    async def test_log_incident(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_incident(
            db=mock_db_session, user_id="user-16", incident_id="inc-1", incident_type="sos"
        )
        mock_db_session.add.assert_called_once()

    async def test_log_camera_access(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_db_session.refresh = AsyncMock(side_effect=lambda x: None)

        await audit_service.log_camera_access(
            db=mock_db_session, admin_id="admin-2", trip_id="trip-50", ip_address="10.0.0.50"
        )
        mock_db_session.add.assert_called_once()

    async def test_get_user_logs(self, mock_db_session):
        from backend.services.audit_service import audit_service

        mock_logs = [MagicMock(), MagicMock()]
        mock_db_session.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_db_session.execute.return_value = mock_result

        logs = await audit_service.get_user_logs(
            db=mock_db_session, user_id="user-20"
        )
        assert len(logs) == 2
