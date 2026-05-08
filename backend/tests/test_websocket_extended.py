import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestConnectionManager:

    def test_connection_manager_init(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()

        assert "trips" in manager.active_connections
        assert "drivers" in manager.active_connections
        assert "notifications" in manager.active_connections

    @pytest.mark.asyncio
    async def test_connect(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await manager.connect(mock_websocket, "trips")

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections["trips"]

    @pytest.mark.asyncio
    async def test_connect_invalid_channel(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await manager.connect(mock_websocket, "invalid")

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections["notifications"]

    def test_disconnect(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_ws = MagicMock()

        manager.active_connections["trips"].add(mock_ws)
        manager.disconnect(mock_ws, "trips")

        assert mock_ws not in manager.active_connections["trips"]

    def test_disconnect_user(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_ws = MagicMock()

        manager.user_connections["user-123"] = mock_ws
        manager.disconnect(mock_ws, "trips")

        assert "user-123" not in manager.user_connections

    def test_register_user(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_ws = MagicMock()

        manager.register_user("user-123", mock_ws)

        assert manager.user_connections["user-123"] == mock_ws

    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()

        manager.user_connections["user-123"] = mock_ws

        await manager.send_personal_message({"msg": "test"}, "user-123")

        mock_ws.send_json.assert_called_once()


class TestWebSocketManager:

    def test_manager_exists(self):
        from backend.websocket import manager

        assert manager is not None

    def test_manager_has_connections(self):
        from backend.websocket import manager

        assert hasattr(manager, "active_connections")
        assert hasattr(manager, "user_connections")

    @pytest.mark.asyncio
    async def test_manager_connect(self):
        from backend.websocket import manager

        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        await manager.connect(mock_ws, "notifications")

        mock_ws.accept.assert_called_once()
