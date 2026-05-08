import pytest
from unittest.mock import AsyncMock


class TestRedisClientBasics:

    def test_redis_client_init(self):
        from backend.redis_client import RedisClient

        client = RedisClient()
        assert client._redis is None

    @pytest.mark.asyncio
    async def test_disconnect(self):
        from backend.redis_client import RedisClient

        client = RedisClient()
        mock_redis = AsyncMock()
        client._redis = mock_redis

        await client.disconnect()

        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_not_connected(self):
        from backend.redis_client import RedisClient

        client = RedisClient()

        with pytest.raises(RuntimeError):
            await client.get_client()

    @pytest.mark.asyncio
    async def test_get_client(self):
        from backend.redis_client import RedisClient

        client = RedisClient()
        mock_redis = AsyncMock()
        client._redis = mock_redis

        result = await client.get_client()

        assert result == mock_redis

    @pytest.mark.asyncio
    async def test_delete_session_mock(self):
        from backend.redis_client import RedisClient

        client = RedisClient()
        mock_redis = AsyncMock()
        client._redis = mock_redis
        mock_redis.delete = AsyncMock()

        await client.delete_session("sess-1")

        mock_redis.delete.assert_called()


class TestConfigBasics:

    def test_config_import(self):
        from backend.config import settings

        assert settings is not None

    def test_config_has_required_fields(self):
        from backend.config import settings

        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")

    def test_config_debug_attribute(self):
        from backend.config import settings

        assert hasattr(settings, "debug")


class TestDatabaseBasics:

    def test_database_import(self):
        from backend.database import Base, engine, get_db

        assert Base is not None
        assert engine is not None
        assert get_db is not None

    def test_models_import(self):
        from backend.models import User, Driver, Vehicle, Trip

        assert User is not None
        assert Driver is not None
        assert Vehicle is not None
        assert Trip is not None
