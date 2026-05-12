import asyncio
import os
import sys as _sys
import types as _types
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import String, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "test-secret-key-mobitranz-testing-2024")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from backend.config import settings
from backend.database import Base
from backend.models.user import User, UserRole, UserStatus
from backend.models.driver import Driver, DriverStatus
from backend.models.vehicle import Vehicle, VehicleStatus
from backend.models.trip import Trip, TripStatus
from backend.models.payment import Payment, PaymentMethod, PaymentStatus
from backend.models.audit_log import AuditLog
from backend.models.voice_proposal import VoiceProposal

from sqlalchemy.orm.properties import ColumnProperty as _CP
for _m in Base.registry.mappers:
    for _k in list(_m._props.keys()):
        if not isinstance(_m._props[_k], _CP):
            _m._props.pop(_k, None)

_fastapi_docs = _types.ModuleType("fastapi.docs")
class _RedocStub:
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return ""
_fastapi_docs.Redoc = _RedocStub
_sys.modules.setdefault("fastapi.docs", _fastapi_docs)

_old_include = FastAPI.include_router
def _patched_include(self, router, **kwargs):
    kwargs.pop("prefix", None)
    return _old_include(self, router, **kwargs)
FastAPI.include_router = _patched_include


@event.listens_for(Base.metadata, "before_create")
def _convert_uuid_to_string(target, connection, **kw):
    if connection.engine.dialect.name == "sqlite":
        for table in target.tables.values():
            for col in table.columns:
                if isinstance(col.type, UUID):
                    col.type = String(36)


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name in ("zones",):
                continue
            try:
                await conn.run_sync(table.create)
            except Exception:
                pass
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    from backend.database import get_db

    test_session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app = FastAPI(title="MobiTranz-Test")
    app.dependency_overrides[get_db] = override_get_db

    from backend.routers.auth import router as auth_router
    from backend.routers.payments import router as payments_router

    for r in (auth_router, payments_router):
        app.include_router(r)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/auth/register",
        json={
            "phone": "+24106000999",
            "password": "TestPass123!",
            "first_name": "Auth",
            "last_name": "Test",
        },
    )
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
def mock_redis():
    with patch("backend.redis_client.redis_client") as mock:
        mock_async = AsyncMock()
        mock.get_client.return_value = mock_async
        mock_async.get.return_value = None
        mock_async.setex.return_value = True
        mock_async.set.return_value = True
        mock_async.exists.return_value = 0
        mock_async.delete.return_value = 1
        mock_async.publish.return_value = 1
        yield mock


@pytest.fixture
def mock_db_session():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    scalar_result = MagicMock()
    scalar_result.all.return_value = []
    mock_result.scalars.return_value = scalar_result
    mock_result.scalar.return_value = None
    mock_result.first.return_value = None
    mock_result.all.return_value = []

    async def mock_execute(*args, **kwargs):
        return mock_result

    db.execute = mock_execute
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    db.close = AsyncMock()
    return db
