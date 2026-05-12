from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestConnectionManager:
    @pytest.fixture
    def manager(self):
        from backend.websocket import ConnectionManager

        return ConnectionManager()

    def test_init_creates_channels(self, manager):
        expected = {"trips", "drivers", "incidents", "notifications", "admin"}
        assert set(manager.active_connections.keys()) == expected
        for channel in expected:
            assert len(manager.active_connections[channel]) == 0

    def test_init_has_user_connections(self, manager):
        assert manager.user_connections == {}

    def test_init_has_rooms(self, manager):
        assert manager.rooms == {}

    async def test_connect(self, manager):
        mock_ws = AsyncMock()
        await manager.connect(mock_ws, "trips")

        assert mock_ws in manager.active_connections["trips"]
        mock_ws.accept.assert_called_once()

    async def test_connect_invalid_channel_falls_back(self, manager):
        mock_ws = AsyncMock()
        await manager.connect(mock_ws, "nonexistent")

        assert mock_ws in manager.active_connections["notifications"]

    async def test_disconnect(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["notifications"].add(mock_ws)

        manager.disconnect(mock_ws, "notifications")
        assert mock_ws not in manager.active_connections["notifications"]

    async def test_disconnect_from_all_channels(self, manager):
        mock_ws = AsyncMock()
        for channel in manager.active_connections:
            manager.active_connections[channel].add(mock_ws)

        manager.disconnect(mock_ws, "trips")
        assert mock_ws not in manager.active_connections["trips"]
        assert mock_ws in manager.active_connections["drivers"]

    async def test_disconnect_removes_user_mapping(self, manager):
        mock_ws = AsyncMock()
        manager.register_user("user-1", mock_ws)
        manager.active_connections["notifications"].add(mock_ws)

        manager.disconnect(mock_ws, "notifications")
        assert "user-1" not in manager.user_connections

    async def test_register_user(self, manager):
        mock_ws = AsyncMock()
        manager.register_user("user-1", mock_ws)
        assert manager.user_connections["user-1"] == mock_ws


class TestBroadcast:
    @pytest.fixture
    def manager(self):
        from backend.websocket import ConnectionManager

        return ConnectionManager()

    async def test_broadcast_to_channel(self, manager):
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        manager.active_connections["notifications"].add(mock_ws1)
        manager.active_connections["notifications"].add(mock_ws2)

        message = {"type": "test", "content": "hello"}
        await manager.broadcast(message, "notifications")

        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)

    async def test_broadcast_unknown_channel(self, manager):
        message = {"type": "test"}
        await manager.broadcast(message, "unknown")
        for channel in manager.active_connections.values():
            assert len(channel) == 0

    async def test_broadcast_removes_disconnected(self, manager):
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=Exception("Disconnected"))

        manager.active_connections["trips"].add(mock_ws)
        await manager.broadcast({"type": "test"}, "trips")

        assert mock_ws not in manager.active_connections["trips"]

    async def test_broadcast_location_update(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["drivers"].add(mock_ws)

        await manager.broadcast_location_update(
            driver_id="driver-1", latitude=0.4163, longitude=9.4673
        )

        mock_ws.send_json.assert_called_once()
        sent = mock_ws.send_json.call_args[0][0]
        assert sent["type"] == "location_update"
        assert sent["driver_id"] == "driver-1"
        assert sent["latitude"] == 0.4163
        assert sent["longitude"] == 9.4673

    async def test_broadcast_trip_status(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["trips"].add(mock_ws)

        await manager.broadcast_trip_status(
            trip_id="trip-1", status="active"
        )

        mock_ws.send_json.assert_called_once()
        sent = mock_ws.send_json.call_args[0][0]
        assert sent["type"] == "trip_status"
        assert sent["trip_id"] == "trip-1"
        assert sent["status"] == "active"

    async def test_broadcast_incident(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["incidents"].add(mock_ws)
        manager.active_connections["admin"].add(mock_ws)

        await manager.broadcast_incident(
            incident_id="inc-1", incident_type="sos", trip_id="trip-1"
        )

        assert mock_ws.send_json.call_count >= 1
        sent = mock_ws.send_json.call_args[0][0]
        assert sent["type"] == "incident"
        assert sent["incident_id"] == "inc-1"
        assert sent["priority"] == "high"

    async def test_broadcast_notification(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["notifications"].add(mock_ws)

        await manager.broadcast_notification(
            title="New Trip", body="A client is waiting"
        )

        mock_ws.send_json.assert_called_once()
        sent = mock_ws.send_json.call_args[0][0]
        assert sent["type"] == "notification"
        assert sent["title"] == "New Trip"
        assert sent["body"] == "A client is waiting"

    async def test_send_personal_message(self, manager):
        mock_ws = AsyncMock()
        manager.register_user("user-1", mock_ws)

        await manager.send_personal_message(
            {"type": "private", "content": "secret"}, "user-1"
        )

        mock_ws.send_json.assert_called_once_with(
            {"type": "private", "content": "secret"}
        )

    async def test_send_personal_message_unknown_user(self, manager):
        await manager.send_personal_message(
            {"type": "test"}, "nonexistent"
        )

    async def test_broadcast_notification_to_specific_user(self, manager):
        mock_ws = AsyncMock()
        manager.register_user("user-1", mock_ws)

        await manager.broadcast_notification(
            title="Private", body="Just for you", user_id="user-1"
        )

        mock_ws.send_json.assert_called_once()

    async def test_broadcast_notification_to_all(self, manager):
        mock_ws = AsyncMock()
        manager.active_connections["notifications"].add(mock_ws)

        await manager.broadcast_notification(
            title="Public", body="For everyone"
        )

        mock_ws.send_json.assert_called_once()


class TestRooms:
    @pytest.fixture
    def manager(self):
        from backend.websocket import ConnectionManager

        return ConnectionManager()

    async def test_join_room(self, manager):
        mock_ws = AsyncMock()
        manager.join_room(mock_ws, "room-1")

        assert "room-1" in manager.rooms
        assert mock_ws in manager.rooms["room-1"]

    async def test_leave_room(self, manager):
        mock_ws = AsyncMock()
        manager.join_room(mock_ws, "room-1")
        manager.leave_room(mock_ws, "room-1")

        assert mock_ws not in manager.rooms["room-1"]

    async def test_leave_nonexistent_room(self, manager):
        mock_ws = AsyncMock()
        manager.leave_room(mock_ws, "no-such-room")

    async def test_send_to_room(self, manager):
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        manager.join_room(mock_ws1, "trip-42")
        manager.join_room(mock_ws2, "trip-42")

        message = {"type": "room_message", "room": "trip-42"}
        await manager.send_to_room(message, "trip-42")

        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)

    async def test_send_to_nonexistent_room(self, manager):
        await manager.send_to_room({"type": "test"}, "no-such-room")

    async def test_rooms_isolated(self, manager):
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        manager.join_room(mock_ws1, "room-a")
        manager.join_room(mock_ws2, "room-b")

        message_a = {"room": "a"}
        message_b = {"room": "b"}
        await manager.send_to_room(message_a, "room-a")
        await manager.send_to_room(message_b, "room-b")

        mock_ws1.send_json.assert_called_once_with(message_a)
        mock_ws2.send_json.assert_called_once_with(message_b)


class TestEventPropagation:
    async def test_trip_status_to_personal(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_client = AsyncMock()
        mock_driver = AsyncMock()
        manager.register_user("client-1", mock_client)
        manager.register_user("driver-1", mock_driver)

        mock_ws = AsyncMock()
        manager.active_connections["trips"].add(mock_ws)

        await manager.broadcast_trip_status(
            trip_id="trip-1",
            status="completed",
            client_id="client-1",
            driver_id="driver-1",
        )

        mock_client.send_json.assert_called_once()
        mock_driver.send_json.assert_called_once()
        mock_ws.send_json.assert_called_once()
        sent = mock_ws.send_json.call_args[0][0]
        assert sent["trip_id"] == "trip-1"
        assert sent["status"] == "completed"

    async def test_incident_broadcasts_to_admin_and_incidents(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        mock_inc = AsyncMock()
        mock_admin = AsyncMock()
        manager.active_connections["incidents"].add(mock_inc)
        manager.active_connections["admin"].add(mock_admin)

        await manager.broadcast_incident(
            incident_id="inc-1",
            incident_type="sos",
            trip_id="trip-1",
            latitude=0.4163,
            longitude=9.4673,
        )

        mock_inc.send_json.assert_called_once()
        mock_admin.send_json.assert_called_once()
        sent = mock_inc.send_json.call_args[0][0]
        assert sent["type"] == "incident"
        assert sent["incident_type"] == "sos"
        assert sent["latitude"] == 0.4163
        assert sent["priority"] == "high"


class TestWebsocketRouter:
    def test_router_exists(self):
        from backend.websocket import websocket_router

        assert websocket_router is not None
        assert len(websocket_router.routes) > 0
