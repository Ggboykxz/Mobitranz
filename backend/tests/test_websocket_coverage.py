import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestConnectionManagerBroadcast:

    @pytest.mark.asyncio
    async def test_broadcast_single_channel(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        manager.active_connections["trips"].add(ws)

        await manager.broadcast({"msg": "test"}, "trips")

        ws.send_json.assert_called_once_with({"msg": "test"})

    @pytest.mark.asyncio
    async def test_broadcast_multiple_clients(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()

        manager.active_connections["trips"].add(ws1)
        manager.active_connections["trips"].add(ws2)

        await manager.broadcast({"msg": "broadcast"}, "trips")

        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_empty_channel(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()

        await manager.broadcast({"msg": "test"}, "trips")

        assert True

    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock(side_effect=Exception("Disconnected"))

        manager.active_connections["trips"].add(ws)

        await manager.broadcast({"msg": "test"}, "trips")

        assert ws not in manager.active_connections["trips"]


class TestConnectionManagerRooms:

    def test_join_room(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = MagicMock()

        manager.join_room(ws, "room-1")

        assert ws in manager.rooms["room-1"]

    def test_join_room_creates_new(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = MagicMock()

        manager.join_room(ws, "new-room")

        assert "new-room" in manager.rooms

    def test_leave_room(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = MagicMock()

        manager.rooms["room-1"] = {ws}
        manager.leave_room(ws, "room-1")

        assert ws not in manager.rooms["room-1"]

    @pytest.mark.asyncio
    async def test_send_to_room(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        manager.rooms["room-1"] = {ws}

        await manager.send_to_room({"msg": "room-msg"}, "room-1")

        ws.send_json.assert_called_once_with({"msg": "room-msg"})


class TestConnectionManagerLocation:

    @pytest.mark.asyncio
    async def test_broadcast_location_update(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        manager.active_connections["drivers"].add(ws)

        await manager.broadcast_location_update("driver-1", 0.5, 0.5)

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "location_update"


class TestConnectionManagerTrip:

    @pytest.mark.asyncio
    async def test_broadcast_trip_status(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        manager.active_connections["trips"].add(ws)

        await manager.broadcast_trip_status("trip-1", "started")

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "trip_status"


class TestConnectionManagerIncident:

    @pytest.mark.asyncio
    async def test_broadcast_incident(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        manager.active_connections["incidents"].add(ws)
        manager.active_connections["admin"].add(ws)

        await manager.broadcast_incident(
            incident_id="inc-1", incident_type="accident", trip_id="trip-1"
        )

        ws.send_json.assert_called()


class TestConnectionManagerNotification:

    @pytest.mark.asyncio
    async def test_broadcast_notification(self):
        from backend.websocket import ConnectionManager

        manager = ConnectionManager()
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        manager.active_connections["notifications"].add(ws)

        await manager.broadcast_notification("Test", "Body")

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "notification"
